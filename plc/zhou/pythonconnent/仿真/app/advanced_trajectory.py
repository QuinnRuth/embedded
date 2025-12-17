#!/usr/bin/env python3
"""
高端数学曲线轨迹生成器
适用于工业绘图机械臂 - 生成参数方程和分形艺术轨迹

限位范围：
- X: 0 ~ 1000 mm
- Y: -50 ~ 370 mm
- 建议工作区：X: 100-900, Y: 50-320 (留安全边界)
"""
import math
import logging
from typing import List, Tuple, Callable

from .models import Point2D, TrajectoryPoint
from .trajectory import TrajectoryGenerator

logger = logging.getLogger(__name__)


class AdvancedTrajectoryGenerator(TrajectoryGenerator):
    """高端数学曲线轨迹生成器"""

    # 推荐工作区中心和尺寸（考虑安全边界）
    WORK_CENTER_X = 500.0
    WORK_CENTER_Y = 160.0
    WORK_WIDTH = 700.0   # 100-800
    WORK_HEIGHT = 260.0  # 30-290

    @staticmethod
    def lissajous(
        num_points: int = 1000,
        velocity: float = 50.0,
        a: float = 3.0,
        b: float = 4.0,
        delta: float = math.pi / 2,
        amplitude: float = 200.0
    ) -> List[TrajectoryPoint]:
        """
        李萨如图形（Lissajous Curve）
        两个垂直方向简谐振动的合成，展现振动的相位关系

        参数方程：
            x(t) = A * sin(a*t + δ)
            y(t) = B * sin(b*t)

        参数:
            num_points: 点数（建议1000-2000）
            velocity: 速度 mm/s
            a: X方向频率（建议 1-5）
            b: Y方向频率（建议 1-5）
            delta: 相位差（弧度），0 为斜线，π/2 为椭圆
            amplitude: 振幅（mm），会自动缩放到工作区

        推荐组合（a:b:delta）：
            - 1:1:0 → 斜直线
            - 1:1:π/2 → 正圆
            - 3:2:π/2 → 经典8字形
            - 3:4:π/2 → 复杂花纹
            - 5:4:0 → 五角星变体

        返回:
            轨迹点列表
        """
        points = []
        center = Point2D(AdvancedTrajectoryGenerator.WORK_CENTER_X,
                        AdvancedTrajectoryGenerator.WORK_CENTER_Y)

        # 自动缩放到工作区
        scale_x = min(amplitude, AdvancedTrajectoryGenerator.WORK_WIDTH / 2.5)
        scale_y = min(amplitude, AdvancedTrajectoryGenerator.WORK_HEIGHT / 2.5)

        for i in range(num_points):
            t = (i / num_points) * 2 * math.pi * max(a, b)  # 确保至少完成一个周期

            x = center.x + scale_x * math.sin(a * t + delta)
            y = center.y + scale_y * math.sin(b * t)

            point = TrajectoryPoint(
                position=Point2D(x, y),
                velocity=velocity,
                index=i
            )
            points.append(point)

        logger.info(f"生成李萨如曲线: a={a}, b={b}, δ={delta:.2f}, {len(points)} 点")
        return AdvancedTrajectoryGenerator.validate_trajectory(points)

    @staticmethod
    def epitrochoid(
        num_points: int = 2000,
        velocity: float = 50.0,
        R: float = 150.0,
        r: float = 50.0,
        d: float = 30.0,
        cycles: int = 1
    ) -> List[TrajectoryPoint]:
        """
        外摆线（Epitrochoid）- 万花尺效果
        小圆沿大圆外侧滚动，笔尖轨迹

        参数方程：
            x(t) = (R + r) * cos(t) - d * cos((R + r) * t / r)
            y(t) = (R + r) * sin(t) - d * sin((R + r) * t / r)

        参数:
            num_points: 点数（建议1500-3000）
            velocity: 速度 mm/s
            R: 大圆半径（mm）
            r: 小圆半径（mm）
            d: 笔尖到小圆圆心的距离（mm）
            cycles: 循环圈数（1-3推荐）

        特殊情况：
            - d = r → 外摆线（Epicycloid）
            - d < r → 花瓣在内
            - d > r → 花瓣在外（更夸张）

        推荐组合：
            - R=150, r=50, d=30 → 五瓣花
            - R=120, r=40, d=60 → 外延花
            - R=100, r=30, d=20 → 精致花纹

        返回:
            轨迹点列表
        """
        points = []
        center = Point2D(AdvancedTrajectoryGenerator.WORK_CENTER_X,
                        AdvancedTrajectoryGenerator.WORK_CENTER_Y)

        # 自动缩放
        max_extent = R + r + d
        scale = min(
            AdvancedTrajectoryGenerator.WORK_WIDTH / (2.2 * max_extent),
            AdvancedTrajectoryGenerator.WORK_HEIGHT / (2.2 * max_extent)
        )
        R_scaled = R * scale
        r_scaled = r * scale
        d_scaled = d * scale

        t_max = cycles * 2 * math.pi

        for i in range(num_points):
            t = (i / num_points) * t_max

            x = center.x + (R_scaled + r_scaled) * math.cos(t) - d_scaled * math.cos((R_scaled + r_scaled) * t / r_scaled)
            y = center.y + (R_scaled + r_scaled) * math.sin(t) - d_scaled * math.sin((R_scaled + r_scaled) * t / r_scaled)

            point = TrajectoryPoint(
                position=Point2D(x, y),
                velocity=velocity,
                index=i
            )
            points.append(point)

        logger.info(f"生成外摆线: R={R}, r={r}, d={d}, {len(points)} 点")
        return AdvancedTrajectoryGenerator.validate_trajectory(points)

    @staticmethod
    def hypotrochoid(
        num_points: int = 2000,
        velocity: float = 50.0,
        R: float = 150.0,
        r: float = 50.0,
        d: float = 70.0,
        cycles: int = 1
    ) -> List[TrajectoryPoint]:
        """
        内摆线（Hypotrochoid）- 万花尺内圈效果
        小圆沿大圆内侧滚动，笔尖轨迹

        参数方程：
            x(t) = (R - r) * cos(t) + d * cos((R - r) * t / r)
            y(t) = (R - r) * sin(t) - d * sin((R - r) * t / r)

        参数:
            num_points: 点数（建议1500-3000）
            velocity: 速度 mm/s
            R: 大圆半径（mm）
            r: 小圆半径（mm）
            d: 笔尖到小圆圆心的距离（mm）
            cycles: 循环圈数

        特殊情况：
            - r = R/2, d = r → 直线
            - r = R/3, d = r → 三角形（Deltoid）
            - r = R/4, d = r → 四叶草（Astroid）

        推荐组合：
            - R=150, r=50, d=70 → 五角星
            - R=150, r=50, d=50 → 内花纹
            - R=120, r=30, d=40 → 精致齿轮纹

        返回:
            轨迹点列表
        """
        points = []
        center = Point2D(AdvancedTrajectoryGenerator.WORK_CENTER_X,
                        AdvancedTrajectoryGenerator.WORK_CENTER_Y)

        # 自动缩放
        max_extent = R + abs(d)  # 内摆线最大半径
        scale = min(
            AdvancedTrajectoryGenerator.WORK_WIDTH / (2.2 * max_extent),
            AdvancedTrajectoryGenerator.WORK_HEIGHT / (2.2 * max_extent)
        )
        R_scaled = R * scale
        r_scaled = r * scale
        d_scaled = d * scale

        t_max = cycles * 2 * math.pi

        for i in range(num_points):
            t = (i / num_points) * t_max

            x = center.x + (R_scaled - r_scaled) * math.cos(t) + d_scaled * math.cos((R_scaled - r_scaled) * t / r_scaled)
            y = center.y + (R_scaled - r_scaled) * math.sin(t) - d_scaled * math.sin((R_scaled - r_scaled) * t / r_scaled)

            point = TrajectoryPoint(
                position=Point2D(x, y),
                velocity=velocity,
                index=i
            )
            points.append(point)

        logger.info(f"生成内摆线: R={R}, r={r}, d={d}, {len(points)} 点")
        return AdvancedTrajectoryGenerator.validate_trajectory(points)

    @staticmethod
    def rose_curve(
        num_points: int = 1000,
        velocity: float = 50.0,
        k: float = 5.0,
        amplitude: float = 180.0
    ) -> List[TrajectoryPoint]:
        """
        玫瑰线（Rose Curve）
        极坐标方程：r = a * sin(k * θ)

        参数:
            num_points: 点数（建议800-1500）
            velocity: 速度 mm/s
            k: 花瓣参数
                - k 为整数 → k 个花瓣（k为奇数）或 2k 个花瓣（k为偶数）
                - k 为分数 → 复杂图案
            amplitude: 振幅（mm），自动缩放

        推荐参数：
            - k=3 → 三叶玫瑰
            - k=4 → 八瓣玫瑰
            - k=5 → 五瓣玫瑰
            - k=7 → 七瓣玫瑰
            - k=3.5 → 复杂花纹
            - k=5/3 → 三圈花纹

        返回:
            轨迹点列表
        """
        points = []
        center = Point2D(AdvancedTrajectoryGenerator.WORK_CENTER_X,
                        AdvancedTrajectoryGenerator.WORK_CENTER_Y)

        # 自动缩放
        scale = min(amplitude,
                   AdvancedTrajectoryGenerator.WORK_WIDTH / 2.5,
                   AdvancedTrajectoryGenerator.WORK_HEIGHT / 2.5)

        # 如果 k 是整数，决定周期数
        if k == int(k):
            periods = 1 if int(k) % 2 == 1 else 2
        else:
            periods = 3  # 分数 k 需要更多周期

        t_max = periods * 2 * math.pi

        for i in range(num_points):
            theta = (i / num_points) * t_max
            r = scale * abs(math.sin(k * theta))  # abs 避免负半径

            x = center.x + r * math.cos(theta)
            y = center.y + r * math.sin(theta)

            point = TrajectoryPoint(
                position=Point2D(x, y),
                velocity=velocity,
                index=i
            )
            points.append(point)

        logger.info(f"生成玫瑰线: k={k}, {len(points)} 点")
        return AdvancedTrajectoryGenerator.validate_trajectory(points)

    @staticmethod
    def butterfly_curve(
        num_points: int = 2000,
        velocity: float = 50.0,
        amplitude: float = 150.0
    ) -> List[TrajectoryPoint]:
        """
        蝴蝶曲线（Butterfly Curve）
        极坐标方程：r = e^(sin(θ)) - 2*cos(4θ) + sin^5(θ/12)

        这是一个复杂的极坐标曲线，形状像蝴蝶翅膀

        参数:
            num_points: 点数（建议1500-3000）
            velocity: 速度 mm/s
            amplitude: 振幅缩放因子

        返回:
            轨迹点列表
        """
        points = []
        center = Point2D(AdvancedTrajectoryGenerator.WORK_CENTER_X,
                        AdvancedTrajectoryGenerator.WORK_CENTER_Y)

        # 蝴蝶曲线的固有尺度约为 [-3, 3]
        scale = min(amplitude / 3.0,
                   AdvancedTrajectoryGenerator.WORK_WIDTH / 7.0,
                   AdvancedTrajectoryGenerator.WORK_HEIGHT / 7.0)

        for i in range(num_points):
            theta = (i / num_points) * 12 * math.pi  # 完整蝴蝶需要 12π

            # 蝴蝶曲线方程
            r = math.exp(math.sin(theta)) - 2 * math.cos(4 * theta) + math.sin(theta / 12) ** 5

            x = center.x + scale * r * math.cos(theta)
            y = center.y + scale * r * math.sin(theta)

            point = TrajectoryPoint(
                position=Point2D(x, y),
                velocity=velocity,
                index=i
            )
            points.append(point)

        logger.info(f"生成蝴蝶曲线: {len(points)} 点")
        return AdvancedTrajectoryGenerator.validate_trajectory(points)

    @staticmethod
    def cardioid(
        num_points: int = 800,
        velocity: float = 50.0,
        amplitude: float = 100.0
    ) -> List[TrajectoryPoint]:
        """
        心形线（Cardioid）
        极坐标方程：r = a * (1 + cos(θ))

        参数:
            num_points: 点数（建议600-1200）
            velocity: 速度 mm/s
            amplitude: 振幅（mm）

        返回:
            轨迹点列表
        """
        points = []
        center = Point2D(AdvancedTrajectoryGenerator.WORK_CENTER_X,
                        AdvancedTrajectoryGenerator.WORK_CENTER_Y)

        # 心形线最大半径为 2a
        scale = min(amplitude,
                   AdvancedTrajectoryGenerator.WORK_WIDTH / 5.0,
                   AdvancedTrajectoryGenerator.WORK_HEIGHT / 5.0)

        for i in range(num_points):
            theta = (i / num_points) * 2 * math.pi
            r = scale * (1 + math.cos(theta))

            x = center.x + r * math.cos(theta)
            y = center.y + r * math.sin(theta)

            point = TrajectoryPoint(
                position=Point2D(x, y),
                velocity=velocity,
                index=i
            )
            points.append(point)

        logger.info(f"生成心形线: {len(points)} 点")
        return AdvancedTrajectoryGenerator.validate_trajectory(points)

    @staticmethod
    def harmonic_oscillator(
        num_points: int = 1500,
        velocity: float = 50.0,
        frequencies: List[Tuple[float, float, float]] = None,
        duration: float = 10.0
    ) -> List[TrajectoryPoint]:
        """
        调和振子（Harmonic Oscillator）
        多个正弦波叠加形成复杂轨迹

        参数方程：
            x(t) = Σ A_i * sin(ω_i * t + φ_i)
            y(t) = Σ B_i * cos(ω_i * t + ψ_i)

        参数:
            num_points: 点数
            velocity: 速度 mm/s
            frequencies: 频率列表 [(A, ω, φ), ...]，如果为 None 使用默认值
            duration: 时间长度（秒）

        返回:
            轨迹点列表
        """
        points = []
        center = Point2D(AdvancedTrajectoryGenerator.WORK_CENTER_X,
                        AdvancedTrajectoryGenerator.WORK_CENTER_Y)

        if frequencies is None:
            # 默认：三个频率分量
            frequencies = [
                (100.0, 1.0, 0.0),      # (振幅, 频率, 相位)
                (60.0, 2.3, math.pi/4),
                (40.0, 3.7, math.pi/2),
            ]

        # 计算振幅总和以进行归一化
        total_amplitude = sum(f[0] for f in frequencies)
        scale = min(
            AdvancedTrajectoryGenerator.WORK_WIDTH / (2.5 * total_amplitude),
            AdvancedTrajectoryGenerator.WORK_HEIGHT / (2.5 * total_amplitude)
        )

        for i in range(num_points):
            t = (i / num_points) * duration

            x = center.x
            y = center.y

            for amp, freq, phase in frequencies:
                scaled_amp = amp * scale
                x += scaled_amp * math.sin(2 * math.pi * freq * t + phase)
                y += scaled_amp * math.cos(2 * math.pi * freq * t + phase + math.pi/3)

            point = TrajectoryPoint(
                position=Point2D(x, y),
                velocity=velocity,
                index=i
            )
            points.append(point)

        logger.info(f"生成调和振子: {len(frequencies)} 个频率分量, {len(points)} 点")
        return AdvancedTrajectoryGenerator.validate_trajectory(points)
