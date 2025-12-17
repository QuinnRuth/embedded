#!/usr/bin/env python3
"""
主程序 - 集成仿真与 PLC 通信

使用方法:
    python main.py                    # 默认使用 config.yaml
    python main.py --mode sim_only    # 仅仿真模式
    python main.py --config my.yaml   # 指定配置文件
"""
import argparse
import logging
import sys
from pathlib import Path

from models import AppConfig, RobotState, Point2D
from plc_client import PLCClient
from simulator import RobotSimulator
from trajectory import TrajectoryGenerator


def setup_logging(level=logging.INFO):
    """配置日志"""
    logging.basicConfig(
        level=level,
        format='[%(asctime)s] [%(name)s] %(levelname)s: %(message)s',
        datefmt='%H:%M:%S'
    )


def main():
    # 命令行参数
    parser = argparse.ArgumentParser(description='Python 仿真 + PLC 同步控制系统')
    parser.add_argument('--config', type=str, default='config.yaml', help='配置文件路径')
    parser.add_argument('--mode', type=str, choices=['sync', 'sim_only', 'plc_only'],
                        help='运行模式（覆盖配置文件）')
    parser.add_argument('--debug', action='store_true', help='启用调试日志')
    parser.add_argument('--auto-start', action='store_true', help='跳过启动确认直接运行')
    args = parser.parse_args()

    # 配置日志
    setup_logging(logging.DEBUG if args.debug else logging.INFO)
    logger = logging.getLogger(__name__)

    # 加载配置
    config_path = Path(__file__).parent / args.config
    if not config_path.exists():
        logger.error(f"配置文件不存在: {config_path}")
        sys.exit(1)

    config = AppConfig.from_yaml(str(config_path))

    # 规范化运行模式（命令行优先，其次配置；统一为小写）
    mode_raw = args.mode or config.mode
    mode = (mode_raw or "sync").strip().lower()
    if mode not in ["sync", "sim_only", "plc_only"]:
        logger.warning(f"不支持的模式 '{mode_raw}'，已回退为 sim_only")
        mode = "sim_only"
    config.mode = mode

    logger.info(f"运行模式: {config.mode}")
    logger.info(f"PLC: {config.plc.ip}:{config.plc.db}")
    logger.info(f"速度: {config.plc.velocity} mm/s")

    # 创建共享状态
    shared_state = RobotState()

    # 生成轨迹（圆形轨迹）
    logger.info("生成轨迹...")

    # 轨迹参数字典（传递给 simulator 用于滑块动态调整）
    trajectory_params = {
        "center": Point2D(491.3, 133.9),  # 圆心坐标（固定）
        "radius": 182.4,                   # 半径（固定）
        "velocity": config.plc.velocity,   # 速度（mm/s）
        "num_points": 300,                 # 初始点数
        "start_angle_deg": 0.0,            # 初始起始角度（度）
    }

    # 使用参数生成初始轨迹
    trajectory = TrajectoryGenerator.circle(
        center=trajectory_params["center"],
        radius=trajectory_params["radius"],
        num_points=trajectory_params["num_points"],
        velocity=trajectory_params["velocity"],
        start_angle_deg=trajectory_params["start_angle_deg"]
    )
    logger.info(f"✓ 生成 {len(trajectory)} 个轨迹点")

    # 启动 PLC 通信（如果需要）
    plc_client = None
    if config.mode in ["sync", "plc_only"]:
        try:
            logger.info("启动 PLC 通信...")
            plc_client = PLCClient(config.plc, shared_state)

            # 使用上下文管理器（自动连接、启动、断开）
            plc_client.connect()
            if not plc_client.connected:
                logger.error("PLC 连接失败，切换到仅仿真模式")
                config.mode = "sim_only"
                plc_client = None
            else:
                plc_client.add_trajectory(trajectory)
                plc_client.start()

        except Exception as e:
            logger.error(f"PLC 初始化失败: {e}")
            if config.mode == "plc_only":
                sys.exit(1)
            config.mode = "sim_only"
            plc_client = None

    # 启动仿真（如果需要）
    if config.mode in ["sync", "sim_only"]:
        try:
            logger.info("启动仿真...")
            # 传递轨迹参数和 PLC 客户端给 simulator（用于滑块控件和控制功能）
            simulator = RobotSimulator(
                config.simulation, 
                shared_state, 
                trajectory, 
                trajectory_params,
                plc_client=plc_client  # 传递 PLC 客户端以支持暂停/复位/停止
            )
            simulator.run()  # 阻塞主线程，直到窗口关闭

        except KeyboardInterrupt:
            logger.info("用户中断")

        except Exception as e:
            logger.error(f"仿真异常: {e}", exc_info=True)

        finally:
            # 清理资源
            if plc_client:
                plc_client.stop()
                plc_client.disconnect()

    elif config.mode == "plc_only":
        # 纯 PLC 模式（无仿真窗口）
        try:
            logger.info("PLC 模式运行中，按 Ctrl+C 退出...")
            plc_client._thread.join()  # 等待 PLC 线程完成

        except KeyboardInterrupt:
            logger.info("用户中断")

        finally:
            plc_client.stop()
            plc_client.disconnect()

    logger.info("程序已退出")


if __name__ == "__main__":
    main()
