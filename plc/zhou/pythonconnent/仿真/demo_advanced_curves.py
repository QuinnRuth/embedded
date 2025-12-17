#!/usr/bin/env python3
"""
高端数学曲线演示脚本
展示所有参数方程和分形艺术轨迹

运行方式：
    python demo_advanced_curves.py --all          # 显示所有曲线
    python demo_advanced_curves.py --parametric   # 只显示参数方程
    python demo_advanced_curves.py --fractal      # 只显示分形
    python demo_advanced_curves.py --curve lissajous  # 显示特定曲线
"""
import argparse
import logging
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from advanced_trajectory import AdvancedTrajectoryGenerator as ATG
from fractal_trajectory import FractalTrajectoryGenerator as FTG
from models import Point2D

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


# ============== 预设推荐参数 ==============

PARAMETRIC_CURVES = {
    "lissajous_classic": {
        "name": "李萨如 (3:4 经典)",
        "func": lambda: ATG.lissajous(num_points=1500, a=3, b=4, delta=1.57),
        "description": "频率比3:4，相位差π/2，经典花纹"
    },
    "lissajous_star": {
        "name": "李萨如 (5:4 五角星)",
        "func": lambda: ATG.lissajous(num_points=1500, a=5, b=4, delta=0),
        "description": "频率比5:4，相位差0，五角星变体"
    },
    "epitrochoid_flower": {
        "name": "外摆线 (五瓣花)",
        "func": lambda: ATG.epitrochoid(num_points=2000, R=150, r=50, d=30),
        "description": "万花尺效果，优雅的五瓣花纹"
    },
    "epitrochoid_fancy": {
        "name": "外摆线 (外延花)",
        "func": lambda: ATG.epitrochoid(num_points=2500, R=120, r=40, d=60),
        "description": "笔尖超出小圆，形成夸张花瓣"
    },
    "hypotrochoid_star": {
        "name": "内摆线 (五角星)",
        "func": lambda: ATG.hypotrochoid(num_points=2000, R=150, r=50, d=70),
        "description": "内侧滚动，锐利的五角星形"
    },
    "hypotrochoid_gear": {
        "name": "内摆线 (齿轮纹)",
        "func": lambda: ATG.hypotrochoid(num_points=2500, R=120, r=30, d=40),
        "description": "精致的齿轮形状"
    },
    "rose_5petal": {
        "name": "玫瑰线 (五瓣)",
        "func": lambda: ATG.rose_curve(num_points=1000, k=5),
        "description": "极坐标花瓣，k=5"
    },
    "rose_7petal": {
        "name": "玫瑰线 (七瓣)",
        "func": lambda: ATG.rose_curve(num_points=1200, k=7),
        "description": "更多花瓣，k=7"
    },
    "rose_complex": {
        "name": "玫瑰线 (复杂)",
        "func": lambda: ATG.rose_curve(num_points=1500, k=7/3),
        "description": "分数k=7/3，复杂花纹"
    },
    "butterfly": {
        "name": "蝴蝶曲线",
        "func": lambda: ATG.butterfly_curve(num_points=2500),
        "description": "复杂极坐标方程，蝴蝶翅膀形状"
    },
    "harmonic": {
        "name": "调和振子 (三频)",
        "func": lambda: ATG.harmonic_oscillator(num_points=1500, duration=10.0),
        "description": "三个正弦波叠加的复杂轨迹"
    }
}

FRACTAL_CURVES = {
    "koch_snowflake": {
        "name": "Koch 雪花 (4次)",
        "func": lambda: FTG.koch_snowflake(iterations=4),
        "description": "经典分形雪花，迭代4次"
    },
    "koch_snowflake_fine": {
        "name": "Koch 雪花 (5次)",
        "func": lambda: FTG.koch_snowflake(iterations=5),
        "description": "更精细的雪花，迭代5次（3072点）"
    },
    "koch_curve": {
        "name": "Koch 曲线",
        "func": lambda: FTG.koch_curve(iterations=5),
        "description": "单边Koch分形，不闭合"
    },
    "dragon_curve": {
        "name": "龙曲线 (12次)",
        "func": lambda: FTG.dragon_curve(iterations=12),
        "description": "经典龙曲线，4096点"
    },
    "dragon_curve_fine": {
        "name": "龙曲线 (13次)",
        "func": lambda: FTG.dragon_curve(iterations=13),
        "description": "更细致的龙曲线，8192点"
    },
    "hilbert_5": {
        "name": "Hilbert 曲线 (阶数5)",
        "func": lambda: FTG.hilbert_curve(order=5),
        "description": "空间填充曲线，1024点"
    },
    "hilbert_6": {
        "name": "Hilbert 曲线 (阶数6)",
        "func": lambda: FTG.hilbert_curve(order=6),
        "description": "更密集的Hilbert曲线，4096点"
    }
}


# ============== 可视化函数 ==============

def plot_single_curve(trajectory, title, ax=None):
    """绘制单个曲线"""
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))

    xs = [p.position.x for p in trajectory]
    ys = [p.position.y for p in trajectory]

    ax.plot(xs, ys, linewidth=1.0, color='#2E86AB')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1000)
    ax.set_ylim(-50, 370)
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')

    # 添加统计信息
    info_text = f"点数: {len(trajectory)}"
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))


def plot_all_parametric():
    """显示所有参数方程曲线"""
    n_curves = len(PARAMETRIC_CURVES)
    n_cols = 4
    n_rows = (n_curves + n_cols - 1) // n_cols

    fig = plt.figure(figsize=(18, 4 * n_rows))
    fig.suptitle('参数方程曲线集合 - 工业绘图素材', fontsize=16, fontweight='bold')

    for idx, (key, info) in enumerate(PARAMETRIC_CURVES.items(), 1):
        ax = fig.add_subplot(n_rows, n_cols, idx)
        logging.info(f"生成 {info['name']}...")
        trajectory = info['func']()
        plot_single_curve(trajectory, f"{info['name']}\n{info['description']}", ax)

    plt.tight_layout()
    plt.show()


def plot_all_fractals():
    """显示所有分形曲线"""
    n_curves = len(FRACTAL_CURVES)
    n_cols = 3
    n_rows = (n_curves + n_cols - 1) // n_cols

    fig = plt.figure(figsize=(15, 5 * n_rows))
    fig.suptitle('分形曲线集合 - 数学艺术', fontsize=16, fontweight='bold')

    for idx, (key, info) in enumerate(FRACTAL_CURVES.items(), 1):
        ax = fig.add_subplot(n_rows, n_cols, idx)
        logging.info(f"生成 {info['name']}...")
        trajectory = info['func']()
        plot_single_curve(trajectory, f"{info['name']}\n{info['description']}", ax)

    plt.tight_layout()
    plt.show()


def plot_all_curves():
    """显示所有曲线（参数方程 + 分形）"""
    all_curves = {**PARAMETRIC_CURVES, **FRACTAL_CURVES}
    n_curves = len(all_curves)
    n_cols = 4
    n_rows = (n_curves + n_cols - 1) // n_cols

    fig = plt.figure(figsize=(20, 5 * n_rows))
    fig.suptitle('高端数学曲线完整集合', fontsize=18, fontweight='bold')

    for idx, (key, info) in enumerate(all_curves.items(), 1):
        ax = fig.add_subplot(n_rows, n_cols, idx)
        logging.info(f"生成 {info['name']}...")
        trajectory = info['func']()
        plot_single_curve(trajectory, f"{info['name']}\n{info['description']}", ax)

    plt.tight_layout()
    plt.show()


def plot_specific_curve(curve_name):
    """显示特定曲线"""
    all_curves = {**PARAMETRIC_CURVES, **FRACTAL_CURVES}

    if curve_name not in all_curves:
        logging.error(f"未找到曲线: {curve_name}")
        logging.info(f"可用曲线: {', '.join(all_curves.keys())}")
        return

    info = all_curves[curve_name]
    logging.info(f"生成 {info['name']}...")
    trajectory = info['func']()

    fig, ax = plt.subplots(figsize=(12, 10))
    plot_single_curve(trajectory, f"{info['name']}\n{info['description']}", ax)
    plt.show()


# ============== 主程序 ==============

def main():
    parser = argparse.ArgumentParser(description='高端数学曲线演示')
    parser.add_argument('--all', action='store_true', help='显示所有曲线')
    parser.add_argument('--parametric', action='store_true', help='只显示参数方程曲线')
    parser.add_argument('--fractal', action='store_true', help='只显示分形曲线')
    parser.add_argument('--curve', type=str, help='显示特定曲线（名称）')
    parser.add_argument('--list', action='store_true', help='列出所有可用曲线')

    args = parser.parse_args()

    if args.list:
        print("\n=== 参数方程曲线 ===")
        for key, info in PARAMETRIC_CURVES.items():
            print(f"  {key:25} - {info['name']:30} : {info['description']}")

        print("\n=== 分形曲线 ===")
        for key, info in FRACTAL_CURVES.items():
            print(f"  {key:25} - {info['name']:30} : {info['description']}")

        return

    if args.curve:
        plot_specific_curve(args.curve)
    elif args.parametric:
        plot_all_parametric()
    elif args.fractal:
        plot_all_fractals()
    elif args.all:
        plot_all_curves()
    else:
        # 默认：显示精选曲线
        print("请使用以下选项之一：")
        print("  --all          显示所有曲线")
        print("  --parametric   只显示参数方程")
        print("  --fractal      只显示分形")
        print("  --curve NAME   显示特定曲线")
        print("  --list         列出所有曲线名称")
        print("\n示例：python demo_advanced_curves.py --fractal")


if __name__ == "__main__":
    main()
