#!/usr/bin/env python3
"""
生成 300 个圆轨迹点的小工具程序

默认参数：
  - 圆心: (491.3, 133.9)
  - 半径: 182.4
  - 点数: 300

运行：
  python gen_circle_300.py
"""

import math


def generate_circle_points(
    cx: float = 491.3,   # 圆心 X
    cy: float = 133.9,   # 圆心 Y
    r: float = 182.4,    # 半径
    n: int = 300,        # 点数
):
    """返回 [(x1, y1), ...] 共 n 个点"""
    pts = []
    for i in range(n):
        theta = 2 * math.pi * i / n  # 0~2π 均匀分布
        x = cx + r * math.cos(theta)
        y = cy + r * math.sin(theta)
        pts.append((round(x, 3), round(y, 3)))
    return pts


def main():
    points = generate_circle_points()

    print(f"# 生成的圆轨迹点，总数: {len(points)}")
    print("# 格式: (X, Y)")
    print()

    # 直接打印为 Python 列表，可以复制到 run.py 里用
    print("POINTS_300 = [")
    for x, y in points:
        print(f"    ({x:.3f}, {y:.3f}),")
    print("]")


if __name__ == "__main__":
    main()


