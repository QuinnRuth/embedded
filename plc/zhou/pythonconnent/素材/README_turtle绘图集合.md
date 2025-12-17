# Python Turtle 绘图集合

这是一个超酷的 Python Turtle 绘图程序集合，包含分形、螺旋、超级英雄等各种稀奇古怪的图案！

所有图案都满足：
- ✅ **可以重叠** - 笔迹可以在同一个位置多次经过
- ✅ **单平面绘制** - 所有图案都在 2D 平面上

---

## 📂 文件列表

### 1. `draw_taiji.py` - 太极图
经典的阴阳太极图，黑白分明，简洁优雅。

**运行方式**：
```bash
python3 draw_taiji.py
```

**特点**：
- 经典太极图案
- 黑白配色，带阴阳鱼眼
- 适合初学者理解 turtle 绘图

---

### 2. `draw_dragon_curve.py` - 龙曲线 ⭐⭐⭐
超级炫酷的分形图案！笔迹会不断重叠形成复杂的龙形图案。

**运行方式**：
```bash
python3 draw_dragon_curve.py
```

**两种模式**：
1. **快速无限模式** - 无限绘制，颜色渐变，按 `Ctrl+C` 停止
2. **固定迭代模式** - 绘制完整图案（推荐 10-15 次迭代）

**推荐指数**：⭐⭐⭐⭐⭐（最炫酷！）

---

### 3. `draw_hilbert_curve.py` - 希尔伯特曲线 ⭐⭐⭐
空间填充曲线，像迷宫一样填满整个正方形！

**运行方式**：
```bash
python3 draw_hilbert_curve.py
```

**三种模式**：
1. **基础版** - 单色曲线
2. **彩色渐变版** - 颜色渐变效果（推荐）
3. **彩虹版** - 七彩颜色

**推荐指数**：⭐⭐⭐⭐（数学之美）

---

### 4. `draw_ironman.py` - 钢铁侠 ⭐⭐⭐⭐
漫威超级英雄钢铁侠的头盔和方舟反应堆！

**运行方式**：
```bash
python3 draw_ironman.py
```

**四种模式**：
1. **经典红色头盔**
2. **金色头盔**（Mark 50）
3. **马克85头盔**（红金配色，复仇者联盟4）
4. **方舟反应堆**（能量核心）

**推荐指数**：⭐⭐⭐⭐⭐（漫威粉丝必看！）

---

### 5. `draw_spiral_art.py` - 螺旋艺术 ⭐⭐⭐⭐⭐
迷幻的螺旋图案，笔迹大量重叠形成催眠般的效果！

**运行方式**：
```bash
python3 draw_spiral_art.py
```

**六种模式**：
1. **正方形螺旋** - 渐变收缩，重叠效果极强
2. **阿基米德螺线** - 经典螺旋
3. **多重螺旋花瓣** - 花朵般的图案（推荐 36 瓣）
4. **玫瑰曲线** - 数学玫瑰（推荐 7 瓣）
5. **催眠螺旋** - 黑白同心圆
6. **斐波那契螺旋** - 黄金螺旋

**推荐指数**：⭐⭐⭐⭐⭐（最迷幻！）

---

## 🎨 推荐运行顺序

### 初学者入门：
1. `draw_taiji.py` - 理解基本绘图
2. `draw_spiral_art.py` (模式 2 或 3) - 感受螺旋之美

### 进阶炫技：
1. `draw_dragon_curve.py` (无限模式) - 体验分形的魅力
2. `draw_hilbert_curve.py` (彩色渐变版) - 数学艺术
3. `draw_ironman.py` - 超级英雄登场

### 极致体验：
1. `draw_spiral_art.py` (模式 6) - 斐波那契黄金螺旋
2. `draw_dragon_curve.py` (15 次迭代) - 完整龙曲线
3. `draw_spiral_art.py` (模式 1, 角度 89°) - 催眠效果

---

## 🔥 最炫酷的组合

### 组合 1：分形三重奏
```bash
# 终端1
python3 draw_dragon_curve.py  # 选择模式 1（无限）

# 终端2
python3 draw_hilbert_curve.py  # 选择模式 2（彩色渐变），级别 6

# 终端3
python3 draw_spiral_art.py  # 选择模式 3（多重螺旋），36 瓣
```

### 组合 2：超级英雄主题
```bash
python3 draw_ironman.py  # 选择不同模式欣赏各种配色
```

---

## 📊 特性对比表

| 程序                    | 重叠程度 | 颜色丰富度 | 复杂度 | 炫酷指数 | 数学美感 |
|------------------------|---------|-----------|--------|---------|---------|
| draw_taiji.py          | ⭐      | ⭐⭐      | ⭐     | ⭐⭐    | ⭐⭐⭐  |
| draw_dragon_curve.py   | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐   | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| draw_hilbert_curve.py  | ⭐⭐⭐⭐  | ⭐⭐⭐⭐⭐  | ⭐⭐⭐⭐ | ⭐⭐⭐⭐  | ⭐⭐⭐⭐⭐ |
| draw_ironman.py        | ⭐      | ⭐⭐⭐    | ⭐⭐   | ⭐⭐⭐⭐⭐ | ⭐⭐    |
| draw_spiral_art.py     | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐  | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐  |

---

## 🎓 学习要点

### 1. 龙曲线（Dragon Curve）
- **原理**：L-System（林德梅尔系统）
- **特点**：自相似分形，通过递归生成
- **应用**：分形几何、混沌理论

### 2. 希尔伯特曲线（Hilbert Curve）
- **原理**：空间填充曲线
- **特点**：可以用一维线填满二维空间
- **应用**：图像处理、地理信息系统

### 3. 螺旋曲线
- **阿基米德螺线**：r = a + b*θ
- **玫瑰曲线**：r = a*sin(k*θ)
- **斐波那契螺旋**：基于黄金比例
- **应用**：自然界中的螺旋（贝壳、星系）

---

## 💡 自定义技巧

### 修改颜色
在代码中搜索 `color()` 或 `fillcolor()` 函数，替换为你喜欢的颜色：
```python
turtle.color('red')           # 基本颜色名
turtle.color('#FF5733')       # 十六进制颜色
turtle.color((255, 0, 0))     # RGB 值（需要 colormode(255)）
```

### 修改速度
```python
turtle.speed(0)    # 最快（瞬间完成）
turtle.speed(5)    # 中速（推荐观看绘制过程）
turtle.speed(1)    # 最慢（适合学习）
```

### 修改画布大小
```python
turtle.setup(800, 800)    # 宽度, 高度（像素）
```

---

## 🐛 常见问题

### 1. 程序运行后窗口立即关闭
**原因**：没有调用 `turtle.done()` 或 `turtle.mainloop()`

### 2. 绘制速度太慢
**解决方案**：
```python
turtle.speed(0)        # 设置最快速度
turtle.tracer(0)       # 关闭动画（需要手动 update()）
```

### 3. 图案不完整
**原因**：迭代次数太高或窗口太小
**解决方案**：降低迭代次数或增大窗口

### 4. 颜色显示异常
**解决方案**：
```python
turtle.colormode(255)  # 使用 0-255 RGB 模式
```

---

## 📚 参考资源

### 在线资源
- [Python Turtle 官方文档](https://docs.python.org/3/library/turtle.html)
- [GeeksforGeeks - Python Turtle](https://www.geeksforgeeks.org/python/turtle-programming-python/)
- [GitHub - Python Turtle 项目集合](https://github.com/saksham0626/Python-Turtle-Projects-Cartoon-Character)

### 分形艺术
- [Invent with Python - 分形艺术](https://inventwithpython.com/recursion/chapter13.html)
- [Python Turtle Academy - 龙曲线](https://pythonturtle.academy/dragon-curve/)
- [Medium - 希尔伯特曲线](https://medium.com/@nico727272/drawing-hilbert-curves-using-turtle-46f6d628732b)

### 超级英雄绘图
- [Pythondex - 钢铁侠教程](https://pythondex.com/draw-iron-man-in-python)
- [GitHub Gist - 钢铁侠代码](https://gist.github.com/gokulbhaveshjoshi/2dc649d6415a820435e2e102a5ae4c18)

---

## 🎉 更多创意

想要更多有趣的图案？试试这些关键词搜索：
- `python turtle pikachu` - 皮卡丘
- `python turtle doraemon` - 哆啦A梦
- `python turtle spiderman` - 蜘蛛侠
- `python turtle mandelbrot` - 曼德布洛特集
- `python turtle koch snowflake` - 科赫雪花
- `python turtle sierpinski` - 谢尔宾斯基三角形

---

**创建日期**：2024-12-05
**作者**：Claude Code + Python Turtle
**许可**：开源，随意使用和修改

祝你玩得开心！🎨🚀
