#!/usr/bin/env python3
"""
轨迹生成器 - 生成各种类型的轨迹
"""
import math
import logging
from typing import List, Tuple

from .models import Point2D, TrajectoryPoint


class TrajectoryGenerator:
    """轨迹生成器"""
    
    # 限位范围（单位：mm）
    X_MIN = 0.0
    X_MAX = 1000.0
    Y_MIN = -50.0
    Y_MAX = 370.0
    
    @staticmethod
    def check_and_clamp_point(point: Point2D) -> Tuple[Point2D, bool]:
        """
        检查并裁剪点，确保在限位范围内
        
        参数:
            point: 原始点
            
        返回:
            (裁剪后的点, 是否被裁剪)
        """
        clamped = False
        x = point.x
        y = point.y
        
        # 检查并裁剪 X 轴
        if x < TrajectoryGenerator.X_MIN:
            x = TrajectoryGenerator.X_MIN
            clamped = True
        elif x > TrajectoryGenerator.X_MAX:
            x = TrajectoryGenerator.X_MAX
            clamped = True
        
        # 检查并裁剪 Y 轴
        if y < TrajectoryGenerator.Y_MIN:
            y = TrajectoryGenerator.Y_MIN
            clamped = True
        elif y > TrajectoryGenerator.Y_MAX:
            y = TrajectoryGenerator.Y_MAX
            clamped = True
        
        return Point2D(x, y), clamped
    
    @staticmethod
    def validate_trajectory(trajectory: List[TrajectoryPoint]) -> List[TrajectoryPoint]:
        """
        验证并裁剪轨迹中的所有点，确保都在限位范围内
        
        参数:
            trajectory: 原始轨迹
            
        返回:
            裁剪后的轨迹
        """
        logger = logging.getLogger(__name__)
        clamped_count = 0
        
        validated = []
        for point in trajectory:
            clamped_point, was_clamped = TrajectoryGenerator.check_and_clamp_point(point.position)
            if was_clamped:
                clamped_count += 1
                logger.warning(
                    f"点 {point.index} 超出限位: ({point.position.x:.1f}, {point.position.y:.1f}) "
                    f"-> ({clamped_point.x:.1f}, {clamped_point.y:.1f})"
                )
            
            validated.append(TrajectoryPoint(
                position=clamped_point,
                velocity=point.velocity,
                index=point.index
            ))
        
        if clamped_count > 0:
            logger.warning(f"轨迹验证完成: {clamped_count}/{len(trajectory)} 个点被裁剪到限位范围内")
        
        return validated

    @staticmethod
    def circle(
        center: Point2D,
        radius: float,
        num_points: int,
        velocity: float,
        start_angle_deg: float = 0.0,
        angle_step_deg: float = None
    ) -> List[TrajectoryPoint]:
        """
        生成圆形轨迹

        参数:
            center: 圆心坐标
            radius: 半径
            num_points: 点数
            velocity: 速度
            start_angle_deg: 起始角度（度），0度为X轴正方向，默认0
            angle_step_deg: 每个点之间的角度步进（度）
                          如果为 None，则自动计算为 360/num_points（均匀分布）
                          注意：如果 angle_step_deg * num_points > 360，会绘制多圈

        返回:
            轨迹点列表

        示例:
            # 标准圆（360度均匀分布）
            circle(center, 100, 300, 50.0)

            # 从90度开始的圆
            circle(center, 100, 300, 50.0, start_angle_deg=90)

            # 每5度一个点，共300个点（1500度，约4.17圈）
            circle(center, 100, 300, 50.0, angle_step_deg=5.0)
        """
        # 防御性检查：点数必须为正数
        if num_points <= 0:
            return []

        points = []

        # 将角度从度转换为弧度
        start_angle_rad = math.radians(start_angle_deg)

        # 计算角度步进（弧度）
        if angle_step_deg is None:
            # 自动均匀分布：360度 / 点数
            angle_step_rad = 2 * math.pi / num_points
        else:
            # 使用用户指定的角度步进
            angle_step_rad = math.radians(angle_step_deg)

        # 生成轨迹点
        for i in range(num_points):
            # 计算当前点的角度
            theta = start_angle_rad + i * angle_step_rad

            # 极坐标转笛卡尔坐标
            x = center.x + radius * math.cos(theta)
            y = center.y + radius * math.sin(theta)

            point = TrajectoryPoint(
                position=Point2D(x, y),
                velocity=velocity,
                index=i
            )
            points.append(point)

        # 验证并裁剪轨迹点，确保在限位范围内
        return TrajectoryGenerator.validate_trajectory(points)

    @staticmethod
    def line(start: Point2D, end: Point2D, num_points: int, velocity: float) -> List[TrajectoryPoint]:
        """
        生成直线轨迹

        参数:
            start: 起点
            end: 终点
            num_points: 点数
            velocity: 速度

        返回:
            轨迹点列表
        """
        points = []
        for i in range(num_points):
            t = i / (num_points - 1) if num_points > 1 else 0
            x = start.x + (end.x - start.x) * t
            y = start.y + (end.y - start.y) * t

            point = TrajectoryPoint(
                position=Point2D(x, y),
                velocity=velocity,
                index=i
            )
            points.append(point)

        # 验证并裁剪轨迹点，确保在限位范围内
        return TrajectoryGenerator.validate_trajectory(points)

    @staticmethod
    def rectangle(center: Point2D, width: float, height: float, num_points: int, velocity: float) -> List[TrajectoryPoint]:
        """
        生成矩形轨迹

        参数:
            center: 中心坐标
            width: 宽度
            height: 高度
            num_points: 点数（每条边的点数）
            velocity: 速度

        返回:
            轨迹点列表
        """
        half_w = width / 2
        half_h = height / 2

        # 四个角点
        p1 = Point2D(center.x - half_w, center.y - half_h)  # 左下
        p2 = Point2D(center.x + half_w, center.y - half_h)  # 右下
        p3 = Point2D(center.x + half_w, center.y + half_h)  # 右上
        p4 = Point2D(center.x - half_w, center.y + half_h)  # 左上

        # 生成四条边
        edge1 = TrajectoryGenerator.line(p1, p2, num_points, velocity)
        edge2 = TrajectoryGenerator.line(p2, p3, num_points, velocity)
        edge3 = TrajectoryGenerator.line(p3, p4, num_points, velocity)
        edge4 = TrajectoryGenerator.line(p4, p1, num_points, velocity)

        # 合并并重新编号
        all_points = edge1 + edge2 + edge3 + edge4
        for i, point in enumerate(all_points):
            point.index = i

        # 验证并裁剪轨迹点，确保在限位范围内
        return TrajectoryGenerator.validate_trajectory(all_points)

    @staticmethod
    def spiral(center: Point2D, start_radius: float, end_radius: float,
               num_loops: int, num_points: int, velocity: float) -> List[TrajectoryPoint]:
        """
        生成螺旋轨迹

        参数:
            center: 中心坐标
            start_radius: 起始半径
            end_radius: 结束半径
            num_loops: 圈数
            num_points: 点数
            velocity: 速度

        返回:
            轨迹点列表
        """
        points = []
        for i in range(num_points):
            t = i / (num_points - 1) if num_points > 1 else 0
            theta = 2 * math.pi * num_loops * t
            r = start_radius + (end_radius - start_radius) * t

            x = center.x + r * math.cos(theta)
            y = center.y + r * math.sin(theta)

            point = TrajectoryPoint(
                position=Point2D(x, y),
                velocity=velocity,
                index=i
            )
            points.append(point)

        # 验证并裁剪轨迹点，确保在限位范围内
        return TrajectoryGenerator.validate_trajectory(points)

    @staticmethod
    def from_points(points: List[tuple[float, float]], velocity: float) -> List[TrajectoryPoint]:
        """
        从坐标列表生成轨迹

        参数:
            points: 坐标列表 [(x1, y1), (x2, y2), ...]
            velocity: 速度

        返回:
            轨迹点列表
        """
        trajectory = []
        for i, (x, y) in enumerate(points):
            point = TrajectoryPoint(
                position=Point2D(x, y),
                velocity=velocity,
                index=i
            )
            trajectory.append(point)

        # 验证并裁剪轨迹点，确保在限位范围内
        return TrajectoryGenerator.validate_trajectory(trajectory)

    @staticmethod
    def star(
        center: Point2D,
        outer_radius: float,
        num_points: int,
        velocity: float,
        inner_radius_ratio: float = 0.4
    ) -> List[TrajectoryPoint]:
        """
        生成五角星轨迹（一笔画）

        参数:
            center: 中心坐标
            outer_radius: 外圆半径（星尖到中心的距离）
            num_points: 每条边的插值点数
            velocity: 速度
            inner_radius_ratio: 内圆半径与外圆的比例（默认0.4）

        返回:
            轨迹点列表

        说明:
            五角星的5个顶点按照 1→3→5→2→4→1 的顺序连接，形成标准五角星
        """
        points = []
        
        # 计算五角星的5个外顶点（从顶部开始，顺时针）
        # 起始角度为 -90 度（顶部）
        outer_points = []
        for i in range(5):
            theta = math.radians(-90 + i * 72)  # 72度 = 360/5
            x = center.x + outer_radius * math.cos(theta)
            y = center.y + outer_radius * math.sin(theta)
            outer_points.append(Point2D(x, y))
        
        # 五角星的绘制顺序：0→2→4→1→3→0（跳两个点连接）
        draw_order = [0, 2, 4, 1, 3, 0]
        
        # 生成轨迹点（在每条边上插值）
        for i in range(len(draw_order) - 1):
            start = outer_points[draw_order[i]]
            end = outer_points[draw_order[i + 1]]
            
            # 在这条边上插值
            for j in range(num_points):
                t = j / num_points
                x = start.x + (end.x - start.x) * t
                y = start.y + (end.y - start.y) * t
                points.append(Point2D(x, y))
        
        # 添加最后一个点（闭合）
        points.append(outer_points[0])
        
        # 转换为 TrajectoryPoint
        trajectory = []
        for i, pt in enumerate(points):
            trajectory.append(TrajectoryPoint(
                position=pt,
                velocity=velocity,
                index=i
            ))
        
        # 验证并裁剪轨迹点，确保在限位范围内
        return TrajectoryGenerator.validate_trajectory(trajectory)

    @staticmethod
    def taiji(
        center: Point2D,
        radius: float,
        num_points: int,
        velocity: float
    ) -> List[TrajectoryPoint]:
        """
        生成太极图轨迹（一笔画）- 参考 draw_taiji.py 的实现逻辑

        参数:
            center: 中心坐标
            radius: 外圆半径
            num_points: 总点数（会自动分配到各部分）
            velocity: 速度

        返回:
            轨迹点列表

        说明:
            参考 draw_taiji.py 的绘制逻辑，生成连续的一笔画路径：
            1. 外圆左半部分（180度，从顶部到左侧）
            2. S曲线上半部分（从左侧到中心，向下凸的半圆）
            3. 上鱼眼（完整圆）
            4. S曲线下半部分（从中心到右侧，向上凸的半圆）
            5. 下鱼眼（完整圆）
            6. 外圆右半部分（180度，从右侧回到顶部）
            
            注意：turtle 坐标系 y 轴向上，我们保持相同的坐标系
        """
        points = []
        
        # 分配点数到各部分
        outer_half_points = num_points // 6      # 外圆每半边
        s_curve_points = num_points // 6         # S曲线每半边
        eye_points = num_points // 6             # 每个鱼眼
        
        half_radius = radius / 2
        eye_radius = radius / 6  # 参考 draw_taiji.py 中的 dot_radius = radius / 6
        
        # 上鱼眼中心：参考 draw_taiji.py goto(0, half_radius + dot_radius)
        # 实际中心在 (center.x, center.y + half_radius)
        # 但 goto 的位置是绘制起点，圆心应该在 (center.x, center.y + half_radius)
        upper_eye_center = Point2D(center.x, center.y + half_radius)
        
        # 下鱼眼中心：参考 draw_taiji.py goto(0, 2 * (radius - dot_radius))
        # 这个位置计算可能有误，我们使用对称位置：center.y - half_radius
        # 与上鱼眼对称，下鱼眼中心在 (center.x, center.y - half_radius)
        lower_eye_center = Point2D(center.x, center.y - half_radius)
        
        # === 第1部分：外圆左半部分（180度，从顶部开始逆时针到左侧）===
        # 从顶部(90度)开始，逆时针到左侧(-90度)
        for i in range(outer_half_points):
            t = i / outer_half_points
            theta = math.radians(90 - t * 180)  # 90° 到 -90°（从顶部到左侧）
            x = center.x + radius * math.cos(theta)
            y = center.y + radius * math.sin(theta)
            points.append(Point2D(x, y))
        
        # === 第2部分：S曲线上半部分（从左侧到中心，向下凸的半圆）===
        # 参考 draw_taiji.py: 从 (0, radius) 开始，circle(half_radius, 180)
        # 这是一个以 (center.x, center.y + half_radius) 为圆心，半径为 half_radius 的上半圆
        # 从左侧(-90度)开始，顺时针到中心(90度)
        for i in range(s_curve_points):
            t = i / s_curve_points
            # 从左侧(-90度)到中心(90度)，顺时针
            theta = math.radians(-90 + t * 180)
            x = center.x + half_radius * math.cos(theta)
            y = center.y + half_radius + half_radius * math.sin(theta)
            points.append(Point2D(x, y))
        
        # === 第3部分：上鱼眼（完整圆）===
        # 参考 draw_taiji.py: goto(0, half_radius + dot_radius), circle(dot_radius)
        for i in range(eye_points):
            t = i / eye_points
            theta = 2 * math.pi * t
            x = upper_eye_center.x + eye_radius * math.cos(theta)
            y = upper_eye_center.y + eye_radius * math.sin(theta)
            points.append(Point2D(x, y))
        
        # 回到中心点
        points.append(Point2D(center.x, center.y))
        
        # === 第4部分：S曲线下半部分（从中心到右侧，向上凸的半圆）===
        # 参考 draw_taiji.py: 从 (0, radius) 开始，反向 circle(half_radius, 180)
        # 这是一个以 (center.x, center.y + half_radius) 为圆心，半径为 half_radius 的下半圆
        # 从中心(90度)开始，顺时针到右侧(270度或-90度)
        for i in range(s_curve_points):
            t = i / s_curve_points
            # 从中心(90度)到右侧(270度或-90度)，顺时针
            theta = math.radians(90 + t * 180)
            x = center.x + half_radius * math.cos(theta)
            y = center.y + half_radius + half_radius * math.sin(theta)
            points.append(Point2D(x, y))
        
        # === 第5部分：下鱼眼（完整圆）===
        # 参考 draw_taiji.py: goto(0, 2 * (radius - dot_radius)), circle(dot_radius)
        for i in range(eye_points):
            t = i / eye_points
            theta = 2 * math.pi * t
            x = lower_eye_center.x + eye_radius * math.cos(theta)
            y = lower_eye_center.y + eye_radius * math.sin(theta)
            points.append(Point2D(x, y))
        
        # 移动到外圆右侧
        points.append(Point2D(center.x + radius, center.y))
        
        # === 第6部分：外圆右半部分（180度，从右侧回到顶部）===
        # 从右侧(270度或-90度)开始，逆时针到顶部(90度)
        for i in range(outer_half_points):
            t = i / outer_half_points
            theta = math.radians(-90 - t * 180)  # -90° 到 -270°（从右侧到顶部，经过底部）
            x = center.x + radius * math.cos(theta)
            y = center.y + radius * math.sin(theta)
            points.append(Point2D(x, y))
        
        # 转换为 TrajectoryPoint
        trajectory = []
        for i, pt in enumerate(points):
            trajectory.append(TrajectoryPoint(
                position=pt,
                velocity=velocity,
                index=i
            ))
        
        # 验证并裁剪轨迹点，确保在限位范围内
        return TrajectoryGenerator.validate_trajectory(trajectory)

    @staticmethod
    def chinese_zheng(
        center: Point2D,
        size: float,
        num_points: int,
        velocity: float
    ) -> List[TrajectoryPoint]:
        """
        生成汉字"正"的轨迹（一笔画）- 使用用户验证过的精确坐标

        参数:
            center: 中心坐标（此参数保留以兼容接口，但实际使用固定坐标）
            size: 字体大小（此参数保留以兼容接口，但实际使用固定坐标）
            num_points: 每笔画的插值点数（此参数保留以兼容接口，但实际使用固定坐标）
            velocity: 速度

        返回:
            轨迹点列表

        说明:
            使用用户验证过的"正"字轨迹坐标（来自 正点位.md）
            注意：此轨迹在x盘留下的轨迹和绝对坐标构成的图像相反
        """
        # 用户验证过的"正"字轨迹坐标（来自 正点位.md）
        points_coords = [
            (491.3, 233.9),   # 1 起点：上中
            (391.3, 233.9),   # 2 左上
            (591.3, 233.9),   # 3 右上
            (491.3, 233.9),   # 4 回上中

            (491.3, 133.9),   # 5 中中
            (391.3, 133.9),   # 6 中横右边 (注释里写的是右半段，但看坐标是往左)
            (491.3, 133.9),   # 7 回中中
            (491.3, 33.9),    # 8 中下
            (391.3, 33.9),    # 12 收笔：左下
            (591.3, 33.9),    # 10 右下
            
            (541.3, 33.9),    # 9 中下与右下之间
            (541.3, 100.9),   # 高度抬到"中中和上之间" 就这个 别改
        ]
        
        # 转换为 TrajectoryPoint
        trajectory = []
        for i, (x, y) in enumerate(points_coords):
            trajectory.append(TrajectoryPoint(
                position=Point2D(x, y),
                velocity=velocity,
                index=i
            ))
        
        # 验证并裁剪轨迹点，确保在限位范围内
        return TrajectoryGenerator.validate_trajectory(trajectory)

    @staticmethod
    def dragon_curve(
        center: Point2D,
        iterations: int,
        step_size: float,
        velocity: float
    ) -> List[TrajectoryPoint]:
        """
        生成龙曲线轨迹（Dragon Curve）- 经典分形图案
        
        参数:
            center: 中心坐标
            iterations: 迭代次数（建议 10-15）
            step_size: 每步的长度（mm）
            velocity: 速度
            
        返回:
            轨迹点列表
        """
        def turn(i):
            """通过位运算确定第 i 步是左转还是右转"""
            left = (((i & -i) << 1) & i) != 0
            return 'L' if left else 'R'
        
        points = []
        x, y = center.x, center.y
        angle = 0.0  # 当前角度（度）
        
        # 计算总步数
        total_steps = 2 ** iterations - 1
        
        # 从中心开始
        points.append(TrajectoryPoint(
            position=Point2D(x, y),
            velocity=velocity,
            index=0
        ))
        
        # 生成轨迹点
        for i in range(1, total_steps + 1):
            # 确定转向
            direction = turn(i)
            
            # 根据转向更新角度（90度转向）
            if direction == 'L':
                angle += 90.0
            else:
                angle -= 90.0
            
            # 计算新位置（使用圆弧近似，每步走 step_size）
            angle_rad = math.radians(angle)
            x += step_size * math.cos(angle_rad)
            y += step_size * math.sin(angle_rad)
            
            points.append(TrajectoryPoint(
                position=Point2D(x, y),
                velocity=velocity,
                index=i
            ))
        
        return TrajectoryGenerator.validate_trajectory(points)

    @staticmethod
    def hilbert_curve(
        center: Point2D,
        level: int,
        size: float,
        velocity: float
    ) -> List[TrajectoryPoint]:
        """
        生成希尔伯特曲线轨迹（Hilbert Curve）- 空间填充曲线
        
        参数:
            center: 中心坐标
            level: 曲线级别（1-7 推荐）
            size: 曲线尺寸（mm）
            velocity: 速度
            
        返回:
            轨迹点列表
        """
        points = []
        
        # 递归生成希尔伯特曲线的坐标点
        def hilbert_points(lvl, x, y, xi, xj, yi, yj):
            """递归生成希尔伯特曲线点"""
            if lvl == 0:
                points.append(Point2D(x, y))
                return
            
            # 递归调用四个象限
            hilbert_points(lvl - 1, x, y, yi/2, yj/2, xi/2, xj/2)
            hilbert_points(lvl - 1, x + xi/2, y + xj/2, xi/2, xj/2, yi/2, yj/2)
            hilbert_points(lvl - 1, x + xi/2 + yi/2, y + xj/2 + yj/2, xi/2, xj/2, yi/2, yj/2)
            hilbert_points(lvl - 1, x + xi/2 + yi, y + xj/2 + yj, -yi/2, -yj/2, -xi/2, -xj/2)
        
        # 从左上角开始
        start_x = center.x - size / 2
        start_y = center.y + size / 2
        
        hilbert_points(level, start_x, start_y, size, 0, 0, size)
        
        # 转换为 TrajectoryPoint
        trajectory = []
        for i, pt in enumerate(points):
            trajectory.append(TrajectoryPoint(
                position=pt,
                velocity=velocity,
                index=i
            ))
        
        return TrajectoryGenerator.validate_trajectory(trajectory)

    @staticmethod
    def spiral_square(
        center: Point2D,
        initial_size: float,
        angle: float,
        num_iterations: int,
        velocity: float
    ) -> List[TrajectoryPoint]:
        """
        生成正方形螺旋轨迹
        
        参数:
            center: 中心坐标
            initial_size: 初始边长（mm）
            angle: 每次旋转的角度（度，89度会产生有趣效果）
            num_iterations: 迭代次数
            velocity: 速度
            
        返回:
            轨迹点列表
        """
        points = []
        x, y = center.x, center.y
        current_angle = 0.0
        size = initial_size
        
        for i in range(num_iterations):
            # 向前走当前边长
            angle_rad = math.radians(current_angle)
            x += size * math.cos(angle_rad)
            y += size * math.sin(angle_rad)
            
            points.append(TrajectoryPoint(
                position=Point2D(x, y),
                velocity=velocity,
                index=i
            ))
            
            # 转向并缩小
            current_angle += angle
            size -= initial_size / num_iterations * 0.1  # 逐渐缩小
        
        return TrajectoryGenerator.validate_trajectory(points)

    @staticmethod
    def spiral_archimedes(
        center: Point2D,
        start_radius: float,
        spacing: float,
        rotations: int,
        num_points: int,
        velocity: float
    ) -> List[TrajectoryPoint]:
        """
        生成阿基米德螺线轨迹
        
        参数:
            center: 中心坐标
            start_radius: 起始半径（mm）
            spacing: 螺旋间距（mm）
            rotations: 旋转圈数
            num_points: 点数
            velocity: 速度
            
        返回:
            轨迹点列表
        """
        points = []
        
        for i in range(num_points):
            t = i / num_points
            angle = 2 * math.pi * rotations * t
            r = start_radius + spacing * angle
            
            x = center.x + r * math.cos(angle)
            y = center.y + r * math.sin(angle)
            
            points.append(TrajectoryPoint(
                position=Point2D(x, y),
                velocity=velocity,
                index=i
            ))
        
        return TrajectoryGenerator.validate_trajectory(points)

    @staticmethod
    def spiral_rose(
        center: Point2D,
        petals: int,
        max_radius: float,
        num_points: int,
        velocity: float
    ) -> List[TrajectoryPoint]:
        """
        生成玫瑰曲线轨迹（数学玫瑰曲线）
        
        参数:
            center: 中心坐标
            petals: 花瓣数量
            max_radius: 最大半径（mm）
            num_points: 点数
            velocity: 速度
            
        返回:
            轨迹点列表
        """
        points = []
        
        for i in range(num_points):
            t = i / num_points
            theta = 2 * math.pi * petals * t
            r = max_radius * abs(math.sin(petals * theta))
            
            x = center.x + r * math.cos(theta)
            y = center.y + r * math.sin(theta)
            
            points.append(TrajectoryPoint(
                position=Point2D(x, y),
                velocity=velocity,
                index=i
            ))
        
        return TrajectoryGenerator.validate_trajectory(points)

    @staticmethod
    def ironman_helmet(
        center: Point2D,
        scale: float,
        velocity: float
    ) -> List[TrajectoryPoint]:
        """
        生成钢铁侠头盔轨迹
        
        参数:
            center: 中心坐标
            scale: 缩放比例
            velocity: 速度
            
        返回:
            轨迹点列表
        """
        # 钢铁侠头盔的坐标数组（从 draw_ironman.py 转换）
        piece1_left = [
            (-40, 120), (-70, 260), (-130, 230), (-170, 200), (-170, 100),
            (-160, 40), (-170, 10), (-150, -10), (-140, 10), (-40, -20), (0, -20)
        ]
        piece1_right = [
            (0, -20), (40, -20), (140, 10), (150, -10), (170, 10), (160, 40),
            (170, 100), (170, 200), (130, 230), (70, 260), (40, 120), (0, 120)
        ]
        
        piece2_left = [
            (-40, -30), (-50, -40), (-100, -46), (-130, -40), (-176, 0),
            (-186, -30), (-186, -40), (-120, -170), (-110, -210), (-80, -230),
            (-64, -210), (0, -210)
        ]
        piece2_right = [
            (0, -210), (64, -210), (80, -230), (110, -210), (120, -170),
            (186, -40), (186, -30), (176, 0), (130, -40), (100, -46),
            (50, -40), (40, -30), (0, -30)
        ]
        
        piece3_left = [
            (-60, -220), (-80, -240), (-110, -220), (-120, -250),
            (-90, -280), (-60, -260), (-30, -260), (-20, -250), (0, -250)
        ]
        piece3_right = [
            (0, -250), (20, -250), (30, -260), (60, -260), (90, -280),
            (120, -250), (110, -220), (80, -240), (60, -220), (0, -220)
        ]
        
        # 合并所有点（按绘制顺序）
        all_coords = piece1_left + piece1_right + piece2_left + piece2_right + piece3_left + piece3_right
        
        # 转换为轨迹点（应用缩放和平移）
        trajectory = []
        for i, (dx, dy) in enumerate(all_coords):
            x = center.x + dx * scale
            y = center.y + dy * scale
            
            trajectory.append(TrajectoryPoint(
                position=Point2D(x, y),
                velocity=velocity,
                index=i
            ))
        
        return TrajectoryGenerator.validate_trajectory(trajectory)

    @staticmethod
    def portrait_sketch(
        center: Point2D,
        scale: float,
        velocity: float
    ) -> List[TrajectoryPoint]:
        """
        生成人像轨迹（Portrait Sketch）- 高保真矢量人像
        
        参数:
            center: 中心坐标
            scale: 缩放比例
            velocity: 速度
            
        返回:
            轨迹点列表
            
        说明:
            包含脸部、眉毛、眼睛、鼻子、嘴唇、头发、耳环、项链、衣服等
            坐标范围约 (-300, -350) 到 (300, 350)
        """
        trajectory = []
        index = 0
        
        # 辅助函数：添加点到轨迹
        def add_point(x, y):
            nonlocal index
            trajectory.append(TrajectoryPoint(
                position=Point2D(center.x + x * scale, center.y + y * scale),
                velocity=velocity,
                index=index
            ))
            index += 1
        
        # 辅助函数：添加路径点
        def add_path(points):
            for x, y in points:
                add_point(x, y)
        
        # --- 1. 头发（底层）---
        hair_outer_left = [
            (-20, 160), (-60, 180), (-110, 150), (-140, 80), (-150, 0), 
            (-145, -80), (-130, -150), (-100, -200)
        ]
        hair_outer_right = [
            (40, 160), (80, 170), (120, 140), (140, 80), (145, 0), 
            (130, -100), (100, -180)
        ]
        add_path(hair_outer_left)
        add_path(hair_outer_right)
        
        # --- 2. 脸部轮廓 ---
        face_contour = [
            (-95, 100), (-98, 60), (-100, 20), (-95, -20), (-85, -60),
            (-70, -100), (-50, -130), (-30, -150), (0, -165),
            (15, -168), (40, -160), (65, -140), (85, -110),
            (95, -80), (100, -40), (102, 0), (98, 40), (90, 80)
        ]
        add_path(face_contour)
        
        # --- 3. 眉毛 ---
        left_eyebrow = [
            (-70, 45), (-60, 52), (-45, 55), (-30, 52), (-20, 48)
        ]
        right_eyebrow = [
            (20, 48), (35, 54), (55, 56), (70, 50), (80, 42)
        ]
        add_path(left_eyebrow)
        add_path(right_eyebrow)
        
        # --- 4. 眼睛 ---
        # 左眼
        left_eye_upper = [(-65, 30), (-55, 36), (-45, 36), (-35, 32)]
        left_eye_lower = [(-65, 30), (-55, 26), (-45, 26), (-35, 32)]
        left_pupil = [(-50, 31), (-48, 31)]
        add_path(left_eye_upper)
        add_path(left_eye_lower)
        add_path(left_pupil)
        
        # 右眼
        right_eye_upper = [(25, 32), (35, 38), (50, 38), (65, 34)]
        right_eye_lower = [(25, 32), (35, 28), (50, 28), (65, 34)]
        right_pupil = [(42, 33), (46, 33)]
        add_path(right_eye_upper)
        add_path(right_eye_lower)
        add_path(right_pupil)
        
        # --- 5. 鼻子 ---
        nose_bridge = [(-5, 45), (-8, 20), (-10, 0)]
        nose_bottom = [(-18, -10), (-10, -15), (0, -12), (10, -10)]
        nose_nostril = [(-12, -12), (-8, -10)]
        add_path(nose_bridge)
        add_path(nose_bottom)
        add_path(nose_nostril)
        
        # --- 6. 嘴唇 ---
        upper_lip_top = [(-20, -45), (-10, -40), (0, -42), (10, -40), (20, -45)]
        upper_lip_bottom = [(-20, -45), (0, -48), (20, -45)]
        mouth_line = [(-22, -45), (0, -46), (22, -45)]
        lower_lip = [(-18, -45), (0, -58), (18, -45)]
        add_path(upper_lip_top)
        add_path(upper_lip_bottom)
        add_path(mouth_line)
        add_path(lower_lip)
        
        # --- 7. 头发（顶层细节）---
        hairline = [
            (-95, 100), (-80, 130), (-40, 150), (0, 145), (40, 155), (80, 130), (90, 80)
        ]
        hair_strands = [
            [(-80, 130), (-90, 80), (-100, 40)],
            [(80, 130), (95, 90), (100, 50)],
            [(10, 145), (20, 100), (15, 60)],
            [(-140, 50), (-130, -50), (-110, -120)]
        ]
        add_path(hairline)
        for strand in hair_strands:
            add_path(strand)
        
        # --- 8. 耳环 ---
        earring_left_base = [(-98, 20), (-105, 15), (-100, 10)]
        earring_left_dangle = [
            (-102, 10), (-105, -10), (-102, -30), (-105, -50), (-100, -55),
            (-97, -50), (-100, -30), (-97, -10), (-102, 10)
        ]
        add_path(earring_left_base)
        add_path(earring_left_dangle)
        
        # --- 9. 颈部 ---
        neck_left = [(-60, -140), (-60, -200)]
        neck_right = [(60, -140), (65, -200)]
        add_path(neck_left)
        add_path(neck_right)
        
        # --- 10. 项链 ---
        necklace_chain = [
            (-55, -190), (-30, -210), (0, -215), (30, -210), (60, -190)
        ]
        necklace_gems = [
            [(-10, -215), (0, -225), (10, -215), (0, -205), (-10, -215)],
            [(-35, -210), (-30, -218), (-25, -210)],
            [(25, -210), (30, -218), (35, -210)]
        ]
        add_path(necklace_chain)
        for gem in necklace_gems:
            add_path(gem)
        
        # --- 11. 衣服 ---
        shoulder_left = [(-60, -200), (-120, -220), (-180, -230), (-180, -350)]
        shoulder_right = [(65, -200), (120, -210), (160, -230), (160, -350)]
        dress_neckline = [
            (-60, -200), (-30, -250), (0, -260), (40, -250), (65, -200)
        ]
        dress_folds = [
            [(-120, -220), (-100, -280), (-110, -350)],
            [(0, -260), (10, -300), (5, -350)]
        ]
        add_path(shoulder_left)
        add_path(shoulder_right)
        add_path(dress_neckline)
        for fold in dress_folds:
            add_path(fold)
        
        return TrajectoryGenerator.validate_trajectory(trajectory)
