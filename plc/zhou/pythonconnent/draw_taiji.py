#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太极图绘制程序
使用 Python turtle 库绘制经典的阴阳太极图
"""

from turtle import *

def draw_taiji(radius=100):
    """
    绘制太极图

    参数:
        radius: 太极图的半径（默认 100）

    原理:
        1. 绘制一个大圆，左半部分填充黑色，右半部分保持白色
        2. 在上半部分绘制白色半圆（阳中阴）
        3. 在下半部分绘制黑色半圆（阴中阳）
        4. 在白色区域绘制黑点
        5. 在黑色区域绘制白点
    """

    # 设置画笔速度和线宽
    speed(5)  # 1-10，10 最快，0 为瞬间完成
    pensize(2)

    # 计算辅助半径
    half_radius = radius / 2    # 小半圆的半径
    dot_radius = radius / 6     # 小圆点的半径

    # 使用角度制（而非弧度制）
    degrees()

    # ========== 步骤1：绘制大圆的左半部分（黑色） ==========
    fillcolor('black')
    begin_fill()
    circle(radius, 180)  # 绘制半圆（180度）
    end_fill()

    # ========== 步骤2：绘制大圆的右半部分（白色） ==========
    circle(radius, 180)  # 只绘制轮廓，不填充

    # ========== 步骤3：绘制上半部分的白色半圆（阳中阴） ==========
    left(180)  # 调整方向
    penup()
    goto(0, radius)  # 移动到上半部分的起始位置
    pendown()

    fillcolor('white')
    begin_fill()
    circle(half_radius, 180)  # 绘制小半圆
    end_fill()

    # ========== 步骤4：绘制下半部分的黑色半圆（阴中阳） ==========
    penup()
    goto(0, radius)
    pendown()

    fillcolor('black')
    begin_fill()
    circle(half_radius, 180)  # 反向绘制另一个小半圆
    end_fill()

    # ========== 步骤5：绘制白色区域的黑点 ==========
    penup()
    goto(0, half_radius + dot_radius)
    pendown()

    fillcolor('black')
    begin_fill()
    circle(dot_radius)  # 绘制完整圆
    end_fill()

    # ========== 步骤6：绘制黑色区域的白点 ==========
    penup()
    goto(0, 2 * (radius - dot_radius))
    pendown()

    fillcolor('white')
    begin_fill()
    circle(dot_radius)
    end_fill()

    # 隐藏画笔
    hideturtle()


def main():
    """主函数"""
    # 设置画布
    setup(width=600, height=600)
    title("太极图 - Taiji (Yin Yang)")
    bgcolor("lightgray")

    # 绘制太极图
    draw_taiji(radius=150)

    # 等待用户关闭窗口
    done()


if __name__ == "__main__":
    main()
