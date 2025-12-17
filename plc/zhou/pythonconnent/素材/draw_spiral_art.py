#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
螺旋艺术（Spiral Art）- 迷幻的重叠图案
使用多重螺旋和旋转创造出催眠般的图案，笔迹大量重叠！
"""

import turtle
import math


def draw_spiral_square(size=420, angle=89):
    """
    绘制正方形螺旋（会逐渐收缩）

    参数:
        size: 初始边长
        angle: 每次旋转的角度（89度会产生有趣效果）
    """
    turtle.setup(900, 900)
    turtle.bgcolor('black')
    turtle.title(f"正方形螺旋 - 旋转角度 {angle}°")
    turtle.speed(0)
    turtle.hideturtle()
    turtle.pensize(1)

    colors = ['red', 'orange', 'yellow', 'lime', 'cyan', 'blue', 'magenta']

    # 将起点移到左上，让螺旋整体居中
    turtle.penup()
    turtle.goto(-size / 2, size / 2)
    turtle.setheading(0)
    turtle.pendown()

    for i in range(240):
        turtle.color(colors[i % len(colors)])
        turtle.forward(size)
        turtle.right(angle)
        size -= 1.2  # 逐渐缩小，放大初始尺寸整体更饱满

    turtle.done()


def draw_spiral_circle(radius=5, spacing=3, rotations=50):
    """
    绘制圆形螺旋（阿基米德螺线）

    参数:
        radius: 起始半径
        spacing: 螺旋间距
        rotations: 旋转圈数
    """
    turtle.setup(800, 800)
    turtle.bgcolor('black')
    turtle.title("阿基米德螺线")
    turtle.speed(0)
    turtle.hideturtle()
    turtle.pensize(2)

    # 彩虹渐变
    for i in range(360 * rotations):
        angle = math.radians(i)
        r = radius + spacing * angle

        x = r * math.cos(angle)
        y = r * math.sin(angle)

        # 颜色渐变
        hue = (i / (360 * rotations)) * 255
        turtle.color(f'#{int(hue):02x}{int(255-hue):02x}80')

        if i == 0:
            turtle.penup()
            turtle.goto(x, y)
            turtle.pendown()
        else:
            turtle.goto(x, y)

    turtle.done()


def draw_multi_spiral(num_spirals=36, length=200):
    """
    绘制多重螺旋花瓣图案

    参数:
        num_spirals: 螺旋数量（建议 12, 18, 36）
        length: 螺旋长度
    """
    turtle.setup(800, 800)
    turtle.bgcolor('black')
    turtle.title(f"多重螺旋 - {num_spirals} 瓣")
    turtle.speed(0)
    turtle.hideturtle()
    turtle.pensize(1)

    angle_step = 360 / num_spirals

    for i in range(num_spirals):
        # 每条螺旋使用不同颜色
        hue = int((i / num_spirals) * 255)
        turtle.color(f'#{hue:02x}{int(255-hue):02x}80')

        turtle.penup()
        turtle.home()
        turtle.setheading(i * angle_step)
        turtle.pendown()

        # 绘制一条螺旋
        for j in range(100):
            turtle.forward(length / 100 * j)
            turtle.right(59)

    turtle.done()


def draw_rose_spiral(petals=7, length=300):
    """
    绘制玫瑰螺旋（数学玫瑰曲线）

    参数:
        petals: 花瓣数量
        length: 最大半径
    """
    turtle.setup(800, 800)
    turtle.bgcolor('black')
    turtle.title(f"玫瑰曲线 - {petals} 瓣")
    turtle.speed(0)
    turtle.hideturtle()
    turtle.pensize(2)

    # 使用参数方程绘制玫瑰曲线
    # r = a * sin(k * θ)
    for theta in range(0, 360 * petals, 1):
        angle = math.radians(theta)
        r = length * math.sin(petals * angle)

        x = r * math.cos(angle)
        y = r * math.sin(angle)

        # 颜色渐变
        progress = theta / (360 * petals)
        turtle.color(f'#{int(255*progress):02x}{int(255*(1-progress)):02x}ff')

        if theta == 0:
            turtle.penup()
            turtle.goto(x, y)
            turtle.pendown()
        else:
            turtle.goto(x, y)

    turtle.done()


def draw_hypnotic_spiral():
    """
    绘制催眠螺旋（旋转的同心圆）
    """
    turtle.setup(800, 800)
    turtle.bgcolor('white')
    turtle.title("催眠螺旋")
    turtle.speed(0)
    turtle.hideturtle()
    turtle.pensize(3)

    num_circles = 50
    max_radius = 300

    for i in range(num_circles):
        radius = max_radius * (1 - i / num_circles)

        # 黑白相间
        if i % 2 == 0:
            turtle.color('black')
        else:
            turtle.color('white')

        turtle.penup()
        turtle.goto(0, -radius)
        turtle.pendown()
        turtle.fillcolor(turtle.pencolor())
        turtle.begin_fill()
        turtle.circle(radius)
        turtle.end_fill()

    turtle.done()


def draw_fibonacci_spiral():
    """
    绘制斐波那契螺旋（黄金螺旋）
    """
    turtle.setup(800, 800)
    turtle.bgcolor('black')
    turtle.title("斐波那契螺旋")
    turtle.speed(6)
    turtle.hideturtle()
    turtle.pensize(2)
    turtle.color('gold')

    # 斐波那契数列
    fib = [1, 1]
    for i in range(2, 15):
        fib.append(fib[i-1] + fib[i-2])

    # 绘制斐波那契方格和圆弧
    turtle.penup()
    turtle.goto(0, 0)
    turtle.pendown()
    turtle.setheading(0)

    square_size = 10  # 基础单位

    for i in range(len(fib)):
        size = fib[i] * square_size

        # 绘制方格
        turtle.color('cyan')
        for _ in range(4):
            turtle.forward(size)
            turtle.right(90)

        # 绘制圆弧
        turtle.color('gold')
        turtle.pensize(3)
        turtle.circle(-size, 90)
        turtle.pensize(2)

    turtle.done()


def main():
    """主函数"""
    print("=" * 60)
    print("螺旋艺术绘制程序")
    print("=" * 60)
    print("1. 正方形螺旋（重叠效果）")
    print("2. 阿基米德螺线")
    print("3. 多重螺旋花瓣")
    print("4. 玫瑰曲线")
    print("5. 催眠螺旋")
    print("6. 斐波那契螺旋（黄金螺旋）")
    print("=" * 60)

    choice = input("请选择模式 (1-6，默认 3): ").strip()

    if choice == '1':
        angle = 89  # 默认角度
        try:
            angle_input = input("输入旋转角度 (85-95 推荐，默认 89): ").strip()
            if angle_input:
                angle = int(angle_input)
        except ValueError:
            pass
        print(f"\n绘制正方形螺旋（角度 {angle}°）...")
        draw_spiral_square(angle=angle)

    elif choice == '2':
        print("\n绘制阿基米德螺线...")
        draw_spiral_circle()

    elif choice == '4':
        petals = 7
        try:
            petals_input = input("输入花瓣数量 (3-11 推荐，默认 7): ").strip()
            if petals_input:
                petals = int(petals_input)
        except ValueError:
            pass
        print(f"\n绘制玫瑰曲线（{petals} 瓣）...")
        draw_rose_spiral(petals=petals)

    elif choice == '5':
        print("\n绘制催眠螺旋...")
        draw_hypnotic_spiral()

    elif choice == '6':
        print("\n绘制斐波那契螺旋...")
        draw_fibonacci_spiral()

    else:
        num_spirals = 36
        try:
            spirals_input = input("输入螺旋数量 (12/18/36 推荐，默认 36): ").strip()
            if spirals_input:
                num_spirals = int(spirals_input)
        except ValueError:
            pass
        print(f"\n绘制多重螺旋（{num_spirals} 瓣）...")
        draw_multi_spiral(num_spirals=num_spirals)


if __name__ == "__main__":
    main()
