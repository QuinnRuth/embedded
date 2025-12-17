#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钢铁侠（Iron Man）- 超级英雄头盔
使用坐标数组绘制钢铁侠的标志性头盔
"""

import turtle


# 钢铁侠头盔的三个部分的坐标数组
piece1 = [
    [(-40, 120), (-70, 260), (-130, 230), (-170, 200), (-170, 100),
     (-160, 40), (-170, 10), (-150, -10), (-140, 10), (-40, -20), (0, -20)],
    [(0, -20), (40, -20), (140, 10), (150, -10), (170, 10), (160, 40),
     (170, 100), (170, 200), (130, 230), (70, 260), (40, 120), (0, 120)]
]

piece2 = [
    [(-40, -30), (-50, -40), (-100, -46), (-130, -40), (-176, 0),
     (-186, -30), (-186, -40), (-120, -170), (-110, -210), (-80, -230),
     (-64, -210), (0, -210)],
    [(0, -210), (64, -210), (80, -230), (110, -210), (120, -170),
     (186, -40), (186, -30), (176, 0), (130, -40), (100, -46),
     (50, -40), (40, -30), (0, -30)]
]

piece3 = [
    [(-60, -220), (-80, -240), (-110, -220), (-120, -250),
     (-90, -280), (-60, -260), (-30, -260), (-20, -250), (0, -250)],
    [(0, -250), (20, -250), (30, -260), (60, -260), (90, -280),
     (120, -250), (110, -220), (80, -240), (60, -220), (0, -220)]
]


def draw_piece(piece, piece_goto, fill_color='red', outline_color='darkred'):
    """
    绘制钢铁侠头盔的一个部分

    参数:
        piece: 坐标数组（左右两部分）
        piece_goto: 起始点坐标
        fill_color: 填充颜色
        outline_color: 轮廓颜色
    """
    turtle.penup()
    turtle.goto(piece_goto)
    turtle.pendown()

    turtle.color(outline_color)
    turtle.fillcolor(fill_color)
    turtle.pensize(2)

    turtle.begin_fill()

    # 绘制左半部分
    for i in range(len(piece[0])):
        x, y = piece[0][i]
        turtle.goto(x, y)

    # 绘制右半部分
    for i in range(len(piece[1])):
        x, y = piece[1][i]
        turtle.goto(x, y)

    turtle.end_fill()


def draw_ironman_classic():
    """绘制经典红色钢铁侠头盔"""
    turtle.setup(600, 700)
    turtle.bgcolor('black')
    turtle.title("钢铁侠 Iron Man - 经典版")
    turtle.hideturtle()
    turtle.speed(5)

    # 绘制三个部分
    draw_piece(piece1, (0, 120), 'red', 'darkred')
    draw_piece(piece2, (0, -30), 'red', 'darkred')
    draw_piece(piece3, (0, -220), 'red', 'darkred')

    # 添加眼睛发光效果
    draw_eyes()

    turtle.done()


def draw_ironman_gold():
    """绘制金色钢铁侠头盔"""
    turtle.setup(600, 700)
    turtle.bgcolor('#1a1a2e')
    turtle.title("钢铁侠 Iron Man - 金色版")
    turtle.hideturtle()
    turtle.speed(5)

    # 绘制三个部分（金色）
    draw_piece(piece1, (0, 120), '#FFD700', '#B8860B')
    draw_piece(piece2, (0, -30), '#FFD700', '#B8860B')
    draw_piece(piece3, (0, -220), '#FFD700', '#B8860B')

    # 添加眼睛发光效果
    draw_eyes(color='cyan')

    turtle.done()


def draw_ironman_mark85():
    """绘制马克85（复仇者联盟4）配色"""
    turtle.setup(600, 700)
    turtle.bgcolor('#0f0f23')
    turtle.title("钢铁侠 Iron Man - Mark 85")
    turtle.hideturtle()
    turtle.speed(5)

    # 绘制三个部分（红金配色）
    draw_piece(piece1, (0, 120), '#C41E3A', '#8B0000')
    draw_piece(piece2, (0, -30), '#FFD700', '#DAA520')
    draw_piece(piece3, (0, -220), '#C41E3A', '#8B0000')

    # 添加眼睛发光效果
    draw_eyes(color='white')

    turtle.done()


def draw_eyes(color='yellow'):
    """
    绘制钢铁侠眼睛的发光效果

    参数:
        color: 眼睛颜色
    """
    turtle.penup()

    # 左眼
    turtle.goto(-60, 100)
    turtle.pendown()
    turtle.color(color)
    turtle.fillcolor(color)
    turtle.begin_fill()
    for _ in range(2):
        turtle.forward(50)
        turtle.right(90)
        turtle.forward(20)
        turtle.right(90)
    turtle.end_fill()

    # 右眼
    turtle.penup()
    turtle.goto(10, 100)
    turtle.pendown()
    turtle.begin_fill()
    for _ in range(2):
        turtle.forward(50)
        turtle.right(90)
        turtle.forward(20)
        turtle.right(90)
    turtle.end_fill()


def draw_arc_reactor():
    """绘制钢铁侠的方舟反应堆"""
    turtle.setup(600, 600)
    turtle.bgcolor('black')
    turtle.title("方舟反应堆 Arc Reactor")
    turtle.hideturtle()
    turtle.speed(6)

    # 外圈
    turtle.penup()
    turtle.goto(0, -150)
    turtle.pendown()
    turtle.color('cyan')
    turtle.pensize(5)
    turtle.circle(150)

    # 中圈
    turtle.penup()
    turtle.goto(0, -100)
    turtle.pendown()
    turtle.fillcolor('#00CED1')
    turtle.begin_fill()
    turtle.circle(100)
    turtle.end_fill()

    # 内核
    turtle.penup()
    turtle.goto(0, -50)
    turtle.pendown()
    turtle.fillcolor('white')
    turtle.begin_fill()
    turtle.circle(50)
    turtle.end_fill()

    # 辐射线
    turtle.pensize(3)
    turtle.color('cyan')
    for angle in range(0, 360, 30):
        turtle.penup()
        turtle.goto(0, 0)
        turtle.setheading(angle)
        turtle.pendown()
        turtle.forward(150)

    turtle.done()


def main():
    """主函数"""
    print("=" * 60)
    print("钢铁侠绘制程序")
    print("=" * 60)
    print("1. 经典红色头盔")
    print("2. 金色头盔（Mark 50）")
    print("3. 马克85头盔（红金配色）")
    print("4. 方舟反应堆")
    print("=" * 60)

    choice = input("请选择模式 (1/2/3/4，默认 1): ").strip()

    if choice == '2':
        print("\n绘制金色钢铁侠头盔...")
        draw_ironman_gold()
    elif choice == '3':
        print("\n绘制马克85头盔...")
        draw_ironman_mark85()
    elif choice == '4':
        print("\n绘制方舟反应堆...")
        draw_arc_reactor()
    else:
        print("\n绘制经典钢铁侠头盔...")
        draw_ironman_classic()


if __name__ == "__main__":
    main()
