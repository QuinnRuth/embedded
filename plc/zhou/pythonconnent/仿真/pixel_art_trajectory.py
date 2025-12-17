#!/usr/bin/env python3
"""
像素艺术轨迹生成器
从JSON坐标文件加载像素点位图并转换为连续轨迹
"""
import json
import logging
from typing import List
from pathlib import Path

from models import Point2D, TrajectoryPoint
from trajectory import TrajectoryGenerator

logger = logging.getLogger(__name__)


class PixelArtTrajectoryGenerator(TrajectoryGenerator):
    """像素艺术轨迹生成器"""

    WORK_CENTER_X = 500.0
    WORK_CENTER_Y = 160.0
    WORK_WIDTH = 700.0
    WORK_HEIGHT = 260.0

    @staticmethod
    def from_json_file(
        json_path: str,
        velocity: float = 50.0,
        scale: float = None,
        center: Point2D = None
    ) -> List[TrajectoryPoint]:
        """
        从JSON坐标文件加载像素艺术轨迹

        JSON格式：
        {
            "width": 98,
            "height": 171,
            "pixelSize": 3,
            "totalPixels": 8870,
            "coordinates": [
                {"x": 31, "y": 0},
                {"x": 32, "y": 0},
                ...
            ]
        }

        参数:
            json_path: JSON文件路径
            velocity: 速度 mm/s
            scale: 缩放因子（如果为None，自动缩放到工作区）
            center: 图形中心位置（如果为None，使用工作区中心）

        返回:
            轨迹点列表
        """
        # 加载JSON文件
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        width = data['width']
        height = data['height']
        coordinates = data['coordinates']

        logger.info(f"加载像素艺术: {len(coordinates)} 点, 尺寸 {width}x{height}")

        # 自动计算缩放比例（保持纵横比）
        if scale is None:
            scale_x = PixelArtTrajectoryGenerator.WORK_WIDTH * 0.8 / width
            scale_y = PixelArtTrajectoryGenerator.WORK_HEIGHT * 0.8 / height
            scale = min(scale_x, scale_y)

        # 使用工作区中心
        if center is None:
            center = Point2D(
                PixelArtTrajectoryGenerator.WORK_CENTER_X,
                PixelArtTrajectoryGenerator.WORK_CENTER_Y
            )

        # 转换坐标到轨迹点
        points = []
        for i, coord in enumerate(coordinates):
            # 原始坐标（左上角为原点）
            px = coord['x']
            py = coord['y']

            # 转换到中心对齐坐标系
            # 1. 平移到中心（原点从左上角移到中心）
            x_centered = px - width / 2
            y_centered = py - height / 2

            # 2. Y轴翻转（JSON通常是Y向下，我们需要Y向上）
            y_centered = -y_centered

            # 3. 缩放
            x_scaled = x_centered * scale
            y_scaled = y_centered * scale

            # 4. 平移到指定中心位置
            x_final = center.x + x_scaled
            y_final = center.y + y_scaled

            point = TrajectoryPoint(
                position=Point2D(x_final, y_final),
                velocity=velocity,
                index=i
            )
            points.append(point)

        logger.info(f"像素艺术转换完成: 缩放={scale:.2f}, 中心=({center.x}, {center.y})")

        # 验证并裁剪到限位范围
        return PixelArtTrajectoryGenerator.validate_trajectory(points)

    @staticmethod
    def optimize_path(points: List[TrajectoryPoint]) -> List[TrajectoryPoint]:
        """
        优化像素点路径（减少笔抬起次数）
        使用贪心算法连接最近的点

        参数:
            points: 原始像素点列表

        返回:
            优化后的轨迹点列表
        """
        if not points:
            return []

        # 创建未访问点集合
        unvisited = set(range(len(points)))
        optimized = []

        # 从第一个点开始
        current_idx = 0
        optimized.append(points[current_idx])
        unvisited.remove(current_idx)

        # 贪心算法：每次选择最近的未访问点
        while unvisited:
            current_pos = points[current_idx].position
            min_dist = float('inf')
            nearest_idx = None

            for idx in unvisited:
                dist = current_pos.distance_to(points[idx].position)
                if dist < min_dist:
                    min_dist = dist
                    nearest_idx = idx

            if nearest_idx is not None:
                optimized.append(points[nearest_idx])
                unvisited.remove(nearest_idx)
                current_idx = nearest_idx

        # 重新索引
        for i, point in enumerate(optimized):
            point.index = i

        logger.info(f"路径优化完成: {len(points)} -> {len(optimized)} 点")
        return optimized


# ============== 测试和演示 ==============

def demo_pixel_art():
    """演示像素艺术加载"""
    import matplotlib.pyplot as plt

    # 加载像素艺术
    json_path = "/home/muqiao/dev/plc/zhou/pythonconnent/素材/pixelnoir-coords-1764953381340.json"

    try:
        # 原始顺序
        trajectory_original = PixelArtTrajectoryGenerator.from_json_file(
            json_path,
            velocity=50.0
        )

        # 优化路径
        trajectory_optimized = PixelArtTrajectoryGenerator.optimize_path(
            trajectory_original.copy()
        )

        # 绘制对比
        fig, axes = plt.subplots(1, 2, figsize=(14, 8))

        # 原始顺序
        xs = [p.position.x for p in trajectory_original]
        ys = [p.position.y for p in trajectory_original]
        axes[0].scatter(xs, ys, s=1, c='blue', alpha=0.6)
        axes[0].set_title(f'原始顺序 ({len(trajectory_original)} 点)')
        axes[0].set_aspect('equal')
        axes[0].grid(True, alpha=0.3)
        axes[0].set_xlim(0, 1000)
        axes[0].set_ylim(-50, 370)

        # 优化路径
        xs_opt = [p.position.x for p in trajectory_optimized]
        ys_opt = [p.position.y for p in trajectory_optimized]
        axes[1].plot(xs_opt, ys_opt, linewidth=0.5, c='red', alpha=0.6)
        axes[1].set_title(f'优化路径 ({len(trajectory_optimized)} 点)')
        axes[1].set_aspect('equal')
        axes[1].grid(True, alpha=0.3)
        axes[1].set_xlim(0, 1000)
        axes[1].set_ylim(-50, 370)

        plt.tight_layout()
        plt.show()

    except Exception as e:
        logger.error(f"加载失败: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    demo_pixel_art()
