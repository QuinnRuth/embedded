"""
PLC 通信客户端 - 线程安全的 Snap7 封装
"""
import time
import threading
from queue import Queue, Empty
from typing import Optional, Callable, TYPE_CHECKING
import logging

# 延迟导入 snap7（仅在实际使用时导入）
if TYPE_CHECKING:
    import snap7

from .models import PLCConfig, TrajectoryPoint, RobotState, RobotStatus, Point2D


class PLCClient:
    """
    线程安全的 PLC 通信客户端

    职责：
    1. 维护与 PLC 的连接
    2. 发送轨迹点到 PLC
    3. 轮询 PLC 状态并更新共享状态
    4. 在独立线程中运行，不阻塞主线程
    """

    def __init__(self, config: PLCConfig, shared_state: RobotState):
        self.config = config
        self.shared_state = shared_state

        # 延迟导入 snap7（仅在实际连接时导入）
        try:
            import snap7
            from snap7.util import get_bool, set_bool, get_real, set_real, set_int
            self._snap7 = snap7
            self._snap7_util = (get_bool, set_bool, get_real, set_real, set_int)
            self.plc = snap7.client.Client()
        except ImportError:
            raise ImportError(
                "snap7 库未安装。请运行: pip install python-snap7\n"
                "或使用仅仿真模式: python main.py --mode sim_only"
            )

        self.connected = False

        # 线程控制
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        # 轨迹点队列
        self.point_queue: Queue[TrajectoryPoint] = Queue()

        # 日志
        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """连接到 PLC"""
        try:
            self.logger.info(f"正在连接 PLC {self.config.ip}...")
            self.shared_state.status = RobotStatus.CONNECTING

            self.plc.connect(self.config.ip, self.config.rack, self.config.slot)
            self.connected = True

            self.logger.info(f"✓ 已连接到 {self.config.ip}")
            self.shared_state.status = RobotStatus.READY
            return True

        except Exception as e:
            self.logger.error(f"✗ 连接失败: {e}")
            self.shared_state.status = RobotStatus.ERROR
            self.shared_state.error_message = str(e)
            self.connected = False
            return False

    def disconnect(self):
        """断开 PLC 连接"""
        if self.connected:
            try:
                # 清除 Enable 标志
                get_bool, set_bool, get_real, set_real, set_int = self._snap7_util
                data = self.plc.db_read(self.config.db, 14, 1)
                set_bool(data, 0, 4, False)
                self.plc.db_write(self.config.db, 14, data)

                self.plc.disconnect()
                self.logger.info("已断开 PLC 连接")
            except Exception as e:
                self.logger.warning(f"断开连接时出错: {e}")
            finally:
                self.connected = False

    def wait_idle(self, timeout: float = 5.0) -> bool:
        """
        等待 PLC 完全空闲（上一个点已执行完成并被消费）

        空闲条件：
        - Enable = TRUE（Python 模式开启）
        - Busy = FALSE（不在执行中）
        - Done = TRUE（上一个点已完成）
        - NewPoint = FALSE（上一个点已被消费）

        返回:
            True: PLC 已空闲，可以发送新点
            False: 超时或 Enable 未开启
        """
        get_bool, set_bool, get_real, set_real, set_int = self._snap7_util
        t0 = time.time()

        while time.time() - t0 < timeout:
            if self._stop_event.is_set():
                return False

            try:
                # 读取状态字节（Offset 14）
                data = self.plc.db_read(self.config.db, 14, 1)

                # 解析状态位
                new_point = get_bool(data, 0, 0)
                busy = get_bool(data, 0, 1)
                done = get_bool(data, 0, 2)
                enable = get_bool(data, 0, 4)

                # Python 模式未开启，返回 False
                if not enable:
                    self.logger.warning("PLC Enable 未开启，无法发送新点")
                    return False

                # 理想的"上一个点确实跑完而且被消费掉"的状态
                if (not busy) and done and (not new_point):
                    return True

            except Exception as e:
                self.logger.warning(f"读取状态失败: {e}")
                time.sleep(0.01)
                continue

            # 轮询间隔
            time.sleep(0.01)

        # 超时
        self.logger.warning(f"等待 PLC 空闲超时 ({timeout}s)")
        return False

    def write_point(self, point: TrajectoryPoint):
        """
        写入单个轨迹点到 PLC

        DB200 布局（16 字节）：
        - Offset 0:  X_Setpoint (Real)
        - Offset 4:  Y_Setpoint (Real)
        - Offset 8:  Velocity (Real)
        - Offset 12: PointIndex (Int)
        - Offset 14.0: NewPoint (Bool)
        - Offset 14.2: Done (Bool) - 写新点时主动清 0
        - Offset 14.4: Enable (Bool)
        """
        try:
            # 解包工具函数
            get_bool, set_bool, get_real, set_real, set_int = self._snap7_util

            # 读取前 16 字节
            data = self.plc.db_read(self.config.db, 0, 16)

            # 写入目标位置
            set_real(data, 0, point.position.x)
            set_real(data, 4, point.position.y)
            set_real(data, 8, point.velocity)
            set_int(data, 12, point.index)

            # ★ 关键：写新点前先把 Done 清 0，防止残留 Done=1 导致误判
            set_bool(data, 14, 2, False)   # Done = False

            # 设置握手信号
            set_bool(data, 14, 4, True)   # Enable
            set_bool(data, 14, 0, True)   # NewPoint = True

            # 一次性写回
            self.plc.db_write(self.config.db, 0, data)

            self.logger.debug(f"✓ 已写入点 {point}")

        except Exception as e:
            self.logger.error(f"写入点失败: {e}")
            raise

    def wait_for_done(self, timeout: float = 30.0) -> bool:
        """
        等待 PLC 完成当前点的运动

        返回:
            True: 成功完成
            False: 超时或错误
        """
        # 解包工具函数
        get_bool, set_bool, get_real, set_real, set_int = self._snap7_util

        t0 = time.time()

        while time.time() - t0 < timeout:
            if self._stop_event.is_set():
                return False

            try:
                # 读取状态字节（Offset 14）
                data = self.plc.db_read(self.config.db, 14, 1)

                # 解析状态位
                new_point = get_bool(data, 0, 0)
                busy = get_bool(data, 0, 1)
                done = get_bool(data, 0, 2)
                error = get_bool(data, 0, 3)

                # 更新共享状态
                self.shared_state.plc_busy = busy
                self.shared_state.plc_done = done
                self.shared_state.plc_error = error

                # 检查错误
                if error:
                    self.logger.error("PLC 报告错误")
                    self.shared_state.status = RobotStatus.ERROR
                    return False

                # 检查完成条件：Done=TRUE 且 Busy=FALSE
                if done and not busy:
                    self.logger.debug("✓ 点执行完成")
                    return True

            except Exception as e:
                self.logger.warning(f"读取状态失败: {e}")
                time.sleep(0.1)
                continue

            # 轮询间隔
            time.sleep(self.config.poll_interval)

        # 超时
        self.logger.warning(f"等待超时 ({timeout}s)")
        return False

    def run(self):
        """
        PLC 通信主循环（在独立线程中运行）

        流程：
        1. 从队列获取轨迹点
        2. 等待 PLC 空闲（上一个点已完成并被消费）
        3. 发送到 PLC
        4. 等待完成
        5. 更新共享状态
        6. 循环...
        """
        self.logger.info("PLC 通信线程已启动")

        while not self._stop_event.is_set():
            try:
                # 从队列获取点（阻塞 1 秒）
                point = self.point_queue.get(timeout=1.0)

                # 更新目标位置
                self.shared_state.target_position = point.position
                self.shared_state.point_index = point.index
                self.shared_state.velocity = point.velocity
                self.shared_state.status = RobotStatus.MOVING

                # ★ 关键：发点前确认 PLC 真正"空闲"，避免丢点
                if not self.wait_idle(timeout=5.0):
                    self.logger.warning(f"PLC 未空闲就写入点 {point.index}，可能丢点")

                # 发送到 PLC
                self.write_point(point)

                # 等待完成
                if self.wait_for_done(self.config.timeout):
                    # 更新当前位置（假设已到达目标）
                    self.shared_state.current_position = point.position

                    # 标记完成
                    self.point_queue.task_done()
                else:
                    # 失败，停止
                    self.logger.error("点执行失败，停止")
                    self.shared_state.status = RobotStatus.ERROR
                    break

            except Empty:
                # 队列为空，等待新点
                if self.shared_state.status == RobotStatus.MOVING:
                    self.shared_state.status = RobotStatus.READY
                continue

            except Exception as e:
                self.logger.error(f"PLC 线程异常: {e}")
                self.shared_state.status = RobotStatus.ERROR
                self.shared_state.error_message = str(e)
                break

        # 所有点完成
        if self.point_queue.empty() and self.shared_state.status != RobotStatus.ERROR:
            self.shared_state.status = RobotStatus.DONE
            self.logger.info("✓ 所有轨迹点已完成")

    def start(self):
        """启动 PLC 通信线程"""
        if self._thread and self._thread.is_alive():
            self.logger.warning("线程已在运行")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self.run, name="PLC-Thread", daemon=True)
        self._thread.start()
        self.logger.info("PLC 线程已启动")

    def stop(self):
        """停止 PLC 通信线程"""
        self.logger.info("正在停止 PLC 线程...")
        self._stop_event.set()

        if self._thread:
            self._thread.join(timeout=5.0)

        self.logger.info("PLC 线程已停止")

    def pause(self):
        """
        暂停 PLC 运动（设置 Enable=FALSE）
        
        PLC 侧逻辑：当 Enable 变为 FALSE 时，会停止发送 Execute 信号，轴立即停止
        """
        if not self.connected:
            self.logger.warning("未连接 PLC，无法暂停")
            return False
        
        try:
            get_bool, set_bool, get_real, set_real, set_int = self._snap7_util
            data = self.plc.db_read(self.config.db, 14, 1)
            set_bool(data, 0, 4, False)  # Enable = FALSE
            self.plc.db_write(self.config.db, 14, data)
            
            self.shared_state.status = RobotStatus.PAUSED
            self.logger.info("✓ PLC 已暂停 (Enable=FALSE)")
            return True
        except Exception as e:
            self.logger.error(f"暂停失败: {e}")
            return False

    def resume(self):
        """
        继续 PLC 运动（设置 Enable=TRUE）
        """
        if not self.connected:
            self.logger.warning("未连接 PLC，无法继续")
            return False
        
        try:
            get_bool, set_bool, get_real, set_real, set_int = self._snap7_util
            data = self.plc.db_read(self.config.db, 14, 1)
            set_bool(data, 0, 4, True)  # Enable = TRUE
            self.plc.db_write(self.config.db, 14, data)
            
            self.shared_state.status = RobotStatus.READY
            self.logger.info("✓ PLC 已继续 (Enable=TRUE)")
            return True
        except Exception as e:
            self.logger.error(f"继续失败: {e}")
            return False

    def reset(self):
        """
        复位 PLC 状态：
        1. 暂停运动 (Enable=FALSE)
        2. 清空轨迹队列
        3. 重置共享状态
        """
        self.logger.info("正在复位...")
        
        # 1. 暂停运动
        self.pause()
        
        # 2. 清空队列
        while not self.point_queue.empty():
            try:
                self.point_queue.get_nowait()
            except Empty:
                break
        
        # 3. 重置共享状态
        self.shared_state.point_index = 0
        self.shared_state.current_position = Point2D(0, 0)
        self.shared_state.status = RobotStatus.READY
        self.shared_state.plc_busy = False
        self.shared_state.plc_done = False
        self.shared_state.plc_error = False
        self.shared_state.error_message = ""
        
        self.logger.info("✓ PLC 已复位")
        return True

    def is_paused(self) -> bool:
        """检查是否处于暂停状态"""
        return self.shared_state.status == RobotStatus.PAUSED

    def add_trajectory(self, points: list[TrajectoryPoint]):
        """添加轨迹点到队列"""
        self.shared_state.total_points = len(points)

        for point in points:
            self.point_queue.put(point)

        self.logger.info(f"已添加 {len(points)} 个轨迹点到队列")

    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.stop()
        self.disconnect()
