#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
龙曲线（Dragon Curve）- 经典分形图案
这是一个超级酷炫的数学分形，笔迹会不断重叠形成复杂图案！
"""

import turtle

# 全局缩放因子，让图形更大更满屏
SCALE_FAST = 1.6
SCALE_LIMITED = 1.4

def turn(i):
    """
    通过位运算确定第 i 步是左转还是右转
    这是龙曲线的核心算法
    """
    left = (((i & -i) << 1) & i) != 0
    return 'L' if left else 'R'


def draw_dragon_curve_fast():
    """
    快速绘制龙曲线（无限循环，按 Ctrl+C 停止）
    """
    turtle.setup(900, 900)
    turtle.bgcolor('black')
    turtle.title("龙曲线 Dragon Curve - 按 Ctrl+C 停止")
    turtle.hideturtle()
    turtle.speed(0)  # 最快速度
    turtle.color('cyan')
    turtle.pensize(1)

    # 从中心开始
    turtle.penup()
    turtle.goto(0, 0)
    turtle.pendown()

    i = 1
    try:
        while True:
            step = 4 * SCALE_FAST
            if turn(i) == 'L':
                turtle.circle(-step, 90, 36)  # 左转圆弧
            else:
                turtle.circle(step, 90, 36)   # 右转圆弧
            i += 1

            # 每 1000 步改变一次颜色
            if i % 1000 == 0:
                colors = ['cyan', 'magenta', 'yellow', 'lime', 'orange', 'pink']
                turtle.color(colors[(i // 1000) % len(colors)])

    except KeyboardInterrupt:
        print("\n绘制已停止")


def draw_dragon_curve_limited(iterations=12):
    """
    绘制固定迭代次数的龙曲线

    参数:
        iterations: 迭代次数（建议 10-15，太大会非常慢）
    """
    turtle.setup(900, 900)
    turtle.bgcolor('black')
    turtle.title(f"龙曲线 - {iterations} 次迭代")
    turtle.hideturtle()
    turtle.speed(0)
    turtle.color('red')
    turtle.pensize(1)

    # 从偏左位置开始，给放大后的曲线留中心空间
    turtle.penup()
    turtle.goto(-260, 0)
    turtle.pendown()

    # 计算总步数
    total_steps = 2 ** iterations - 1

    for i in range(1, total_steps + 1):
        step = 3 * SCALE_LIMITED
        if turn(i) == 'L':
            turtle.circle(-step, 90, 36)
        else:
            turtle.circle(step, 90, 36)

        # 渐变颜色效果
        if i % 100 == 0:
            progress = i / total_steps
            r = int(255 * (1 - progress))
            g = int(255 * progress)
            b = 128
            turtle.color(f'#{r:02x}{g:02x}{b:02x}')

    turtle.done()


def main():
    """主函数 - 选择绘制模式"""
    print("=" * 50)
    print("龙曲线绘制程序")
    print("=" * 50)
    print("1. 快速无限模式（炫酷，按 Ctrl+C 停止）")
    print("2. 固定迭代模式（完整图案）")
    print("=" * 50)

    choice = input("请选择模式 (1/2，默认 2): ").strip()

    if choice == '1':
        print("\n开始绘制龙曲线（无限模式）...")
        print("按 Ctrl+C 停止绘制")
        draw_dragon_curve_fast()
    else:
        iterations = 12  # 默认迭代次数
        try:
            user_input = input(f"输入迭代次数 (10-15 推荐，默认 {iterations}): ").strip()
            if user_input:
                iterations = int(user_input)
                if iterations < 1:
                    iterations = 12
                elif iterations > 20:
                    print("⚠️  迭代次数太大会非常慢！已限制为 15")
                    iterations = 15
        except ValueError:
            print(f"输入无效，使用默认值 {iterations}")

        print(f"\n开始绘制龙曲线（{iterations} 次迭代）...")
        draw_dragon_curve_limited(iterations)


if __name__ == "__main__":
    main()
