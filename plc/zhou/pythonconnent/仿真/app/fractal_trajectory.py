#!/usr/bin/env python3
"""
分形艺术轨迹生成器
生成连续可绘制的分形曲线，适用于工业绘图机械臂

分形特点：
- 自相似性（不同尺度上重复相同模式）
- 递归生成
- 无限细节

限位范围：X: 0-1000mm, Y: -50-370mm
"""
import math
import logging
from typing import List, Tuple
from dataclasses import dataclass

from .models import Point2D, TrajectoryPoint
from .trajectory import TrajectoryGenerator

logger = logging.getLogger(__name__)


@dataclass
class LineSegment:
    """线段"""
    start: Point2D
    end: Point2D


class FractalTrajectoryGenerator(TrajectoryGenerator):
    """分形轨迹生成器"""

    WORK_CENTER_X = 500.0
    WORK_CENTER_Y = 160.0
    WORK_WIDTH = 700.0
    WORK_HEIGHT = 260.0

    @staticmethod
    def koch_snowflake(
        iterations: int = 4,
        velocity: float = 50.0,
        size: float = 300.0
    ) -> List[TrajectoryPoint]:
        """
        科赫雪花（Koch Snowflake）
        经典分形，从等边三角形开始，每条边递归替换为凸起

        迭代规则：
        每条线段 _____ 替换为 _/\\_
        (分成4段：1/3直线、60度转、1/3直线、-120度转、1/3直线)

        参数:
            iterations: 迭代次数（0-6推荐，每增加1次点数×4）
                - 0: 三角形 (4点)
                - 1: 12点
                - 2: 48点
                - 3: 192点
                - 4: 768点（推荐）
                - 5: 3072点
                - 6: 12288点（慢）
            velocity: 速度 mm/s
            size: 初始三角形边长（mm），自动缩放

        数学特性：
            - 周长：L_n = L_0 * (4/3)^n → ∞ （随迭代趋于无穷）
            - 面积：有限值
            - 分形维度：log(4)/log(3) ≈ 1.26

        返回:
            轨迹点列表
        """
        # 自动缩放到工作区
        scale = min(
            size,
            FractalTrajectoryGenerator.WORK_WIDTH * 0.8,
            FractalTrajectoryGenerator.WORK_HEIGHT * 1.2
        ) / size

        # 创建初始等边三角形（逆时针）
        center_x = FractalTrajectoryGenerator.WORK_CENTER_X
        center_y = FractalTrajectoryGenerator.WORK_CENTER_Y

        # 三角形顶点（正三角形，底边水平）
        h = size * math.sqrt(3) / 2  # 高度
        p1 = Point2D(center_x - size/2 * scale, center_y - h/3 * scale)
        p2 = Point2D(center_x + size/2 * scale, center_y - h/3 * scale)
        p3 = Point2D(center_x, center_y + 2*h/3 * scale)

        # 初始三条边
        segments = [
            LineSegment(p1, p2),
            LineSegment(p2, p3),
            LineSegment(p3, p1)
        ]

        # 递归迭代
        for iteration in range(iterations):
            new_segments = []
            for seg in segments:
                new_segments.extend(FractalTrajectoryGenerator._koch_subdivide(seg))
            segments = new_segments
            logger.info(f"Koch迭代 {iteration + 1}/{iterations}: {len(segments)} 条线段")

        # 转换为轨迹点
        points = FractalTrajectoryGenerator._segments_to_trajectory(segments, velocity)

        logger.info(f"生成Koch雪花: {iterations}次迭代, {len(points)} 点")
        return FractalTrajectoryGenerator.validate_trajectory(points)

    @staticmethod
    def _koch_subdivide(segment: LineSegment) -> List[LineSegment]:
        """
        Koch曲线细分：将一条线段分成4段

        _____ → _/\\_
        """
        p1 = segment.start
        p2 = segment.end

        # 计算三分点
        dx = (p2.x - p1.x) / 3
        dy = (p2.y - p1.y) / 3

        a = Point2D(p1.x + dx, p1.y + dy)
        b = Point2D(p1.x + 2*dx, p1.y + 2*dy)

        # 计算凸起顶点（等边三角形顶点）
        # 旋转60度
        angle = math.radians(60)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        # 以a为中心旋转向量(dx, dy)
        peak_x = a.x + dx * cos_a - dy * sin_a
        peak_y = a.y + dx * sin_a + dy * cos_a

        peak = Point2D(peak_x, peak_y)

        # 返回4条新线段
        return [
            LineSegment(p1, a),
            LineSegment(a, peak),
            LineSegment(peak, b),
            LineSegment(b, p2)
        ]

    @staticmethod
    def koch_curve(
        iterations: int = 5,
        velocity: float = 50.0,
        length: float = 600.0
    ) -> List[TrajectoryPoint]:
        """
        科赫曲线（Koch Curve）- 单条边
        只有一条边的Koch分形（不是闭合的雪花）

        参数:
            iterations: 迭代次数（推荐3-6）
            velocity: 速度 mm/s
            length: 初始线段长度（mm）

        返回:
            轨迹点列表
        """
        center_x = FractalTrajectoryGenerator.WORK_CENTER_X
        center_y = FractalTrajectoryGenerator.WORK_CENTER_Y

        # 水平线段
        scale = min(length, FractalTrajectoryGenerator.WORK_WIDTH * 0.9) / length
        p1 = Point2D(center_x - length/2 * scale, center_y)
        p2 = Point2D(center_x + length/2 * scale, center_y)

        segments = [LineSegment(p1, p2)]

        for iteration in range(iterations):
            new_segments = []
            for seg in segments:
                new_segments.extend(FractalTrajectoryGenerator._koch_subdivide(seg))
            segments = new_segments

        points = FractalTrajectoryGenerator._segments_to_trajectory(segments, velocity)

        logger.info(f"生成Koch曲线: {iterations}次迭代, {len(points)} 点")
        return FractalTrajectoryGenerator.validate_trajectory(points)

    @staticmethod
    def dragon_curve(
        iterations: int = 12,
        velocity: float = 50.0,
        step_size: float = 3.0
    ) -> List[TrajectoryPoint]:
        """
        龙曲线（Dragon Curve）
        通过左右转向序列生成的分形曲线

        算法：
        - 每一步前进固定距离
        - 使用位运算判断左转或右转：((i & -i) << 1) & i

        参数:
            iterations: 迭代次数（推荐10-14）
                - 10: 1024点
                - 12: 4096点（推荐）
                - 14: 16384点
            velocity: 速度 mm/s
            step_size: 每步长度（mm），会自动缩放

        数学特性：
            - 点数：2^iterations
            - 分形维度：2
            - 自相似性：每两次迭代自相似

        返回:
            轨迹点列表
        """
        num_points = 2 ** iterations

        # 起始位置（调整到工作区中心偏上，避免超出下限）
        x = FractalTrajectoryGenerator.WORK_CENTER_X - 250
        y = FractalTrajectoryGenerator.WORK_CENTER_Y + 50  # 向上偏移50mm
        heading = 0  # 初始方向（0度 = 向右）

        points = [TrajectoryPoint(
            position=Point2D(x, y),
            velocity=velocity,
            index=0
        )]

        # 自适应步长（避免超出工作区）
        # 使龙曲线占据大部分工作区空间（扩大6倍）
        scale = min(
            FractalTrajectoryGenerator.WORK_WIDTH / (num_points * 0.0083 * step_size),  # 0.05/6
            FractalTrajectoryGenerator.WORK_HEIGHT / (num_points * 0.0058 * step_size),  # 0.035/6
            1.0
        )
        actual_step = step_size * scale

        for i in range(1, num_points):
            # 位运算判断转向
            turn_left = (((i & -i) << 1) & i) != 0

            if turn_left:
                heading += 90
            else:
                heading -= 90

            # 前进
            rad = math.radians(heading)
            x += actual_step * math.cos(rad)
            y += actual_step * math.sin(rad)

            point = TrajectoryPoint(
                position=Point2D(x, y),
                velocity=velocity,
                index=i
            )
            points.append(point)

        logger.info(f"生成龙曲线: {iterations}次迭代, {len(points)} 点")
        return FractalTrajectoryGenerator.validate_trajectory(points)

    @staticmethod
    def hilbert_curve(
        order: int = 5,
        velocity: float = 50.0,
        size: float = 500.0
    ) -> List[TrajectoryPoint]:
        """
        希尔伯特曲线（Hilbert Curve）
        空间填充曲线，用一维线填满二维空间

        应用：
        - 图像处理（像素排序）
        - 数据库索引（空间查询）
        - 路径规划

        参数:
            order: 阶数（推荐3-7）
                - 3: 64点 (8×8网格)
                - 4: 256点 (16×16网格)
                - 5: 1024点 (32×32网格，推荐)
                - 6: 4096点 (64×64网格)
                - 7: 16384点 (128×128网格，慢)
            velocity: 速度 mm/s
            size: 正方形边长（mm）

        数学特性：
            - 点数：4^order
            - 分形维度：2（完全填充平面）
            - 连续曲线，不自相交

        返回:
            轨迹点列表
        """
        n = 2 ** order  # 网格大小
        num_points = n * n

        # 自动缩放
        scale = min(
            size,
            FractalTrajectoryGenerator.WORK_WIDTH * 0.9,
            FractalTrajectoryGenerator.WORK_HEIGHT * 0.9
        ) / size

        step = (size * scale) / n  # 网格步长

        # 起始位置（左下角）
        start_x = FractalTrajectoryGenerator.WORK_CENTER_X - (size * scale) / 2
        start_y = FractalTrajectoryGenerator.WORK_CENTER_Y - (size * scale) / 2

        points = []
        for i in range(num_points):
            # Hilbert索引转坐标
            hx, hy = FractalTrajectoryGenerator._hilbert_index_to_xy(i, order)

            x = start_x + hx * step
            y = start_y + hy * step

            point = TrajectoryPoint(
                position=Point2D(x, y),
                velocity=velocity,
                index=i
            )
            points.append(point)

        logger.info(f"生成Hilbert曲线: 阶数{order}, {len(points)} 点")
        return FractalTrajectoryGenerator.validate_trajectory(points)

    @staticmethod
    def _hilbert_index_to_xy(index: int, order: int) -> Tuple[int, int]:
        """
        将Hilbert曲线的一维索引转换为二维坐标
        使用递归算法
        """
        n = 2 ** order
        x, y = 0, 0

        for s in range(order):
            rx = 1 & (index >> 1)
            ry = 1 & (index ^ rx)

            # 旋转和翻转
            if ry == 0:
                if rx == 1:
                    x = n - 1 - x
                    y = n - 1 - y
                x, y = y, x

            x += (n >> 1) * rx
            y += (n >> 1) * ry
            index >>= 2

        return x, y

    @staticmethod
    def _segments_to_trajectory(
        segments: List[LineSegment],
        velocity: float,
        points_per_segment: int = 1
    ) -> List[TrajectoryPoint]:
        """
        将线段列表转换为轨迹点列表

        参数:
            segments: 线段列表
            velocity: 速度
            points_per_segment: 每条线段的点数（1=只要端点）
        """
        points = []
        index = 0

        for i, seg in enumerate(segments):
            if i == 0:
                # 第一个点：起点
                points.append(TrajectoryPoint(
                    position=seg.start,
                    velocity=velocity,
                    index=index
                ))
                index += 1

            # 添加终点
            points.append(TrajectoryPoint(
                position=seg.end,
                velocity=velocity,
                index=index
            ))
            index += 1

        return points


# ============== 示例和测试 ==============

def demo_all_fractals():
    """演示所有分形曲线"""
    import matplotlib.pyplot as plt

    fractals = [
        ("Koch雪花 (4次迭代)", FractalTrajectoryGenerator.koch_snowflake(iterations=4)),
        ("Koch曲线 (5次迭代)", FractalTrajectoryGenerator.koch_curve(iterations=5)),
        ("龙曲线 (12次迭代)", FractalTrajectoryGenerator.dragon_curve(iterations=12)),
        ("Hilbert曲线 (阶数5)", FractalTrajectoryGenerator.hilbert_curve(order=5)),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    for ax, (title, trajectory) in zip(axes, fractals):
        xs = [p.position.x for p in trajectory]
        ys = [p.position.y for p in trajectory]

        ax.plot(xs, ys, linewidth=0.5)
        ax.set_title(title)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 1000)
        ax.set_ylim(-50, 370)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    demo_all_fractals()
