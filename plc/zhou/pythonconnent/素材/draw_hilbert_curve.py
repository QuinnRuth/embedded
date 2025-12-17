#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
希尔伯特曲线（Hilbert Curve）- 空间填充曲线
这条曲线可以填满整个正方形，是数学中的经典分形！
笔迹会在正方形内部不断重叠形成迷宫般的图案。
"""

from turtle import *


def hilbert(level, angle, step):
    """
    递归绘制希尔伯特曲线

    参数:
        level: 递归深度（1-7 推荐）
        angle: 转向角度（通常为 90 度）
        step: 每步的长度
    """
    if level == 0:
        return

    right(angle)
    hilbert(level - 1, -angle, step)
    forward(step)
    left(angle)
    hilbert(level - 1, angle, step)
    forward(step)
    hilbert(level - 1, angle, step)
    left(angle)
    forward(step)
    hilbert(level - 1, -angle, step)
    right(angle)


def draw_hilbert_basic(level=4):
    """
    绘制基础希尔伯特曲线（单色）

    参数:
        level: 曲线级别（1-7）
    """
    setup(900, 900)
    bgcolor('black')
    title(f"希尔伯特曲线 - 级别 {level}")
    speed(0)
    color('cyan')
    pensize(2)

    size = 700
    penup()
    step = size / (2 ** level - 1)
    total = step * (2 ** level - 1)
    goto(-total / 2.0, total / 2.0)
    setheading(0)
    pendown()

    hilbert(level, 90, step)

    hideturtle()
    done()


def draw_hilbert_colorful(level=5):
    """
    绘制彩色希尔伯特曲线（渐变色效果）

    参数:
        level: 曲线级别（1-7）
    """
    setup(900, 900)
    bgcolor('black')
    title(f"彩色希尔伯特曲线 - 级别 {level}")
    speed(0)
    pensize(2)
    tracer(0)  # 关闭动画，加速绘制

    size = 700
    penup()
    step_size = size / (2 ** level - 1)
    total = step_size * (2 ** level - 1)
    goto(-total / 2.0, total / 2.0)
    setheading(0)
    pendown()

    # 使用栈来模拟递归，以便添加颜色渐变
    total_steps = 4 ** level  # 总步数
    current_step = [0]  # 使用列表以便在内部函数中修改

    def hilbert_colored(lvl, angle, step):
        if lvl == 0:
            return

        right(angle)
        hilbert_colored(lvl - 1, -angle, step)

        # 渐变颜色
        progress = current_step[0] / total_steps
        r = int(255 * (1 - progress))
        g = int(100 + 155 * progress)
        b = int(155 + 100 * (1 - progress))
        color(f'#{r:02x}{g:02x}{b:02x}')

        forward(step)
        current_step[0] += 1

        left(angle)
        hilbert_colored(lvl - 1, angle, step)
        forward(step)
        current_step[0] += 1

        hilbert_colored(lvl - 1, angle, step)
        left(angle)
        forward(step)
        current_step[0] += 1

        hilbert_colored(lvl - 1, -angle, step)
        right(angle)

    hilbert_colored(level, 90, step_size)

    hideturtle()
    update()  # 显示最终结果
    done()


def draw_hilbert_rainbow(level=5):
    """
    绘制彩虹色希尔伯特曲线

    参数:
        level: 曲线级别（1-7）
    """
    setup(900, 900)
    bgcolor('#1a1a1a')
    title(f"彩虹希尔伯特曲线 - 级别 {level}")
    speed(0)
    pensize(3)

    size = 720
    penup()
    step = size / (2 ** level - 1)
    total = step * (2 ** level - 1)
    goto(-total / 2.0, total / 2.0)
    setheading(0)
    pendown()

    # 彩虹颜色列表
    colors = ['red', 'orange', 'yellow', 'lime', 'cyan', 'blue', 'magenta']
    color_idx = [0]
    steps_per_color = (2 ** level - 1) // len(colors) + 1

    def hilbert_rainbow(lvl, angle, step, step_count):
        if lvl == 0:
            return step_count

        right(angle)
        step_count = hilbert_rainbow(lvl - 1, -angle, step, step_count)

        if step_count % steps_per_color == 0:
            color_idx[0] = (color_idx[0] + 1) % len(colors)
        color(colors[color_idx[0]])

        forward(step)
        step_count += 1
        left(angle)

        step_count = hilbert_rainbow(lvl - 1, angle, step, step_count)
        forward(step)
        step_count += 1

        step_count = hilbert_rainbow(lvl - 1, angle, step, step_count)
        left(angle)
        forward(step)
        step_count += 1

        step_count = hilbert_rainbow(lvl - 1, -angle, step, step_count)
        right(angle)

        return step_count

    hilbert_rainbow(level, 90, step, 0)

    hideturtle()
    done()


def main():
    """主函数"""
    print("=" * 60)
    print("希尔伯特曲线绘制程序")
    print("=" * 60)
    print("1. 基础版（单色）")
    print("2. 彩色渐变版")
    print("3. 彩虹版")
    print("=" * 60)

    choice = input("请选择模式 (1/2/3，默认 2): ").strip()

    default_level = 5
    try:
        level_input = input(f"输入曲线级别 (1-7 推荐，默认 {default_level}): ").strip()
        if level_input:
            level = int(level_input)
            if level < 1:
                level = default_level
            elif level > 8:
                print("⚠️  级别太高会非常慢！已限制为 7")
                level = 7
        else:
            level = default_level
    except ValueError:
        print(f"输入无效，使用默认值 {default_level}")
        level = default_level

    print(f"\n开始绘制希尔伯特曲线（级别 {level}）...")

    if choice == '1':
        draw_hilbert_basic(level)
    elif choice == '3':
        draw_hilbert_rainbow(level)
    else:
        draw_hilbert_colorful(level)


if __name__ == "__main__":
    main()
