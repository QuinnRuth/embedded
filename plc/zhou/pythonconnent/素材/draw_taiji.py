#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太极图绘制程序
使用 Python turtle 库绘制经典的阴阳太极图
"""

from turtle import *


def draw_taiji(radius=150):
    """
    绘制标准太极图（黑左白右，阴阳互含）
    """
    pensize(2)
    speed(0)
    penup()
    goto(0, -radius)
    setheading(90)  # 朝上开始画大圆
    pendown()

    # 左黑右白外圈
    fillcolor('black')
    begin_fill()
    circle(radius, 180)
    circle(radius / 2, 180)
    end_fill()

    fillcolor('white')
    begin_fill()
    circle(radius / 2, 180)
    circle(radius, 180)
    end_fill()

    # 黑点（在白半区）
    penup()
    goto(0, radius / 2)
    setheading(0)
    pendown()
    fillcolor('black')
    begin_fill()
    circle(radius / 6)
    end_fill()

    # 白点（在黑半区）
    penup()
    goto(0, -radius / 2)
    pendown()
    fillcolor('white')
    begin_fill()
    circle(radius / 6)
    end_fill()

    hideturtle()


def main():
    """主函数"""
    setup(width=700, height=700)
    title("太极图 - Taiji (Yin Yang)")
    bgcolor("lightgray")
    draw_taiji(radius=180)
    done()


if __name__ == "__main__":
    main()
