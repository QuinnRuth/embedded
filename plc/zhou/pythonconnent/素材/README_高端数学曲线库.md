# 高端数学曲线轨迹库

工业级参数方程和分形艺术，适用于机械臂/绘图机/CNC 绘图控制系统

---

## 📂 文件说明

```
仿真/
├── advanced_trajectory.py    # 参数方程曲线生成器
├── fractal_trajectory.py     # 分形艺术曲线生成器
└── demo_advanced_curves.py   # 演示脚本
```

---

## 🎨 一、参数方程曲线（Parametric Curves）

### 1.1 李萨如图形（Lissajous Curves）

**数学原理**：两个垂直方向简谐振动的合成

```
x(t) = A * sin(a*t + δ)
y(t) = B * sin(b*t)
```

**参数**：
- `a`, `b`：频率比（决定图形复杂度）
- `delta`：相位差（决定图形方向）
  - δ = 0 → 斜线
  - δ = π/2 → 椭圆/圆
  - δ = π/4 → 扭曲椭圆

**推荐组合**：

| a:b 比例 | 相位差 δ | 效果 | 点数 | 难度 |
|---------|---------|------|------|------|
| 1:1 | 0 | 斜直线 | 500 | ⭐ |
| 1:1 | π/2 | 正圆 | 800 | ⭐ |
| 3:2 | π/2 | 经典8字形 | 1200 | ⭐⭐⭐ |
| 3:4 | π/2 | 复杂花纹（**推荐**） | 1500 | ⭐⭐⭐⭐ |
| 5:4 | 0 | 五角星变体 | 1500 | ⭐⭐⭐⭐ |
| 7:5 | π/4 | 高密度纹理 | 2000 | ⭐⭐⭐⭐⭐ |

**代码示例**：
```python
from advanced_trajectory import AdvancedTrajectoryGenerator as ATG

# 经典3:4李萨如
trajectory = ATG.lissajous(
    num_points=1500,
    velocity=50.0,
    a=3.0,
    b=4.0,
    delta=math.pi/2,
    amplitude=200.0
)
```

---

### 1.2 外摆线/内摆线（Epitrochoid/Hypotrochoid）

**数学原理**：小圆沿大圆滚动，笔尖轨迹（万花尺效果）

**外摆线**（小圆在大圆外侧）：
```
x(t) = (R + r) * cos(t) - d * cos((R + r) * t / r)
y(t) = (R + r) * sin(t) - d * sin((R + r) * t / r)
```

**内摆线**（小圆在大圆内侧）：
```
x(t) = (R - r) * cos(t) + d * cos((R - r) * t / r)
y(t) = (R - r) * sin(t) - d * sin((R - r) * t / r)
```

**参数**：
- `R`：大圆半径
- `r`：小圆半径
- `d`：笔尖到小圆圆心的距离
  - d = r → 标准摆线
  - d < r → 花瓣在内
  - d > r → 花瓣外延

**推荐组合**：

| 类型 | R | r | d | 效果 | 点数 | 花瓣数 |
|------|---|---|---|------|------|--------|
| 外摆线 | 150 | 50 | 30 | 五瓣花（**推荐**） | 2000 | 5 |
| 外摆线 | 120 | 40 | 60 | 外延花 | 2500 | 5 |
| 外摆线 | 180 | 30 | 20 | 精致花纹 | 2500 | 7 |
| 内摆线 | 150 | 50 | 70 | 五角星（**推荐**） | 2000 | 5 |
| 内摆线 | 120 | 30 | 40 | 齿轮纹 | 2500 | 7 |
| 内摆线 | 150 | 37.5 | 37.5 | 四叶草 | 2000 | 4 |

**花瓣数公式**：
- 如果 R/r 是整数 n → n 个花瓣
- 如果 R/r 是分数 p/q（最简） → p 个花瓣

**代码示例**：
```python
# 外摆线 - 五瓣花
epitrochoid_traj = ATG.epitrochoid(
    num_points=2000,
    velocity=50.0,
    R=150.0,  # 大圆半径
    r=50.0,   # 小圆半径
    d=30.0,   # 笔距
    cycles=1
)

# 内摆线 - 五角星
hypotrochoid_traj = ATG.hypotrochoid(
    num_points=2000,
    velocity=50.0,
    R=150.0,
    r=50.0,
    d=70.0,   # d > r → 外延星形
    cycles=1
)
```

---

### 1.3 玫瑰线（Rose Curves）

**数学原理**：极坐标方程 `r = a * sin(k * θ)`

**花瓣规律**：
- k 为奇数 → k 个花瓣
- k 为偶数 → 2k 个花瓣
- k 为分数 p/q → p 个花瓣（但需要 q 圈才完整）

**推荐参数**：

| k 值 | 花瓣数 | 圈数 | 点数 | 效果 |
|------|--------|------|------|------|
| 3 | 3 | 1 | 800 | 三叶玫瑰（简洁） |
| 4 | 8 | 2 | 1200 | 八瓣玫瑰（对称美） |
| 5 | 5 | 1 | 1000 | 五瓣玫瑰（**推荐**） |
| 7 | 7 | 1 | 1200 | 七瓣玫瑰（精细） |
| 3.5 | 7 | 2 | 1500 | 复杂花纹 |
| 5/3 | 5 | 3 | 1800 | 三圈花纹 |

**代码示例**：
```python
# 五瓣玫瑰
rose_traj = ATG.rose_curve(
    num_points=1000,
    velocity=50.0,
    k=5.0,
    amplitude=180.0
)
```

---

### 1.4 蝴蝶曲线（Butterfly Curve）

**数学原理**：复杂极坐标方程
```
r = e^(sin(θ)) - 2*cos(4θ) + sin^5(θ/12)
```

**特点**：
- 形状像蝴蝶翅膀
- 需要 12π 弧度完整绘制
- 自然有机形态

**推荐参数**：
- 点数：2000-3000
- 速度：30-50 mm/s（较慢，精细绘制）

---

### 1.5 心形线（Cardioid）

**数学原理**：极坐标 `r = a * (1 + cos(θ))`

**特点**：
- 经典心形
- 简洁优雅
- 适合演示

**推荐参数**：
- 点数：600-1000
- 振幅：80-120 mm

---

### 1.6 调和振子（Harmonic Oscillator）

**数学原理**：多个正弦波叠加
```
x(t) = Σ A_i * sin(ω_i * t + φ_i)
y(t) = Σ B_i * cos(ω_i * t + ψ_i)
```

**推荐组合**：

```python
# 三频叠加（默认）
frequencies = [
    (100.0, 1.0, 0.0),           # (振幅, 频率, 相位)
    (60.0, 2.3, math.pi/4),
    (40.0, 3.7, math.pi/2),
]

# 五频叠加（复杂）
frequencies = [
    (80.0, 1.0, 0.0),
    (60.0, 1.7, math.pi/6),
    (50.0, 2.5, math.pi/4),
    (30.0, 3.2, math.pi/3),
    (20.0, 4.9, math.pi/2),
]
```

---

## 🔮 二、分形曲线（Fractal Curves）

### 2.1 Koch 雪花（Koch Snowflake）

**数学原理**：从等边三角形开始，每条边递归替换为凸起

**迭代规则**：
```
_____ → _/\_
(每条线段分成4段)
```

**推荐迭代次数**：

| 迭代 | 点数 | 效果 | 时间 | 推荐场景 |
|------|------|------|------|---------|
| 2 | 48 | 粗糙雪花 | 瞬间 | 快速演示 |
| 3 | 192 | 基本雪花 | <1s | 教学 |
| 4 | 768 | 精细雪花（**推荐**） | <1s | 工业绘图 |
| 5 | 3072 | 非常精细 | 1-2s | 高精度展示 |
| 6 | 12288 | 极致细节 | 5-10s | 艺术品 |

**数学特性**：
- 周长：L_n = L_0 * (4/3)^n → ∞
- 面积：有限值（约 1.6 倍原三角形）
- 分形维度：log(4)/log(3) ≈ 1.26

**代码示例**：
```python
from fractal_trajectory import FractalTrajectoryGenerator as FTG

# Koch 雪花（推荐4次迭代）
snowflake = FTG.koch_snowflake(
    iterations=4,
    velocity=50.0,
    size=300.0
)

# Koch 曲线（单边）
curve = FTG.koch_curve(
    iterations=5,
    velocity=50.0,
    length=600.0
)
```

---

### 2.2 龙曲线（Dragon Curve）

**数学原理**：通过左右转向序列生成，使用位运算判断
```python
turn_left = (((i & -i) << 1) & i) != 0
```

**推荐迭代次数**：

| 迭代 | 点数 | 效果 | 内存 | 时间 |
|------|------|------|------|------|
| 10 | 1024 | 基本龙形 | 微小 | 瞬间 |
| 11 | 2048 | 清晰龙形 | 微小 | <1s |
| 12 | 4096 | 完整龙形（**推荐**） | 小 | 1s |
| 13 | 8192 | 精细龙形 | 中 | 2-3s |
| 14 | 16384 | 极致细节 | 大 | 5-10s |

**数学特性**：
- 点数：2^n
- 分形维度：2（完全填充平面）
- 自相似性：每两次迭代

**代码示例**：
```python
# 龙曲线（推荐12次迭代）
dragon = FTG.dragon_curve(
    iterations=12,
    velocity=50.0,
    step_size=3.0
)
```

---

### 2.3 Hilbert 曲线（Hilbert Curve）

**数学原理**：空间填充曲线，用一维线填满二维空间

**推荐阶数**：

| 阶数 | 网格 | 点数 | 效果 | 应用 |
|------|------|------|------|------|
| 3 | 8×8 | 64 | 粗糙网格 | 演示 |
| 4 | 16×16 | 256 | 基本填充 | 路径规划 |
| 5 | 32×32 | 1024 | 精细填充（**推荐**） | 绘图 |
| 6 | 64×64 | 4096 | 高密度 | 图像处理 |
| 7 | 128×128 | 16384 | 极致密度 | 数据库索引 |

**应用场景**：
- 图像处理（像素排序）
- 数据库空间索引
- 路径规划（全覆盖）

**代码示例**：
```python
# Hilbert 曲线（推荐阶数5）
hilbert = FTG.hilbert_curve(
    order=5,
    velocity=50.0,
    size=500.0
)
```

---

## 🚀 三、快速开始

### 3.1 安装依赖

```bash
cd /home/muqiao/dev/plc/zhou/pythonconnent/仿真
pip install -r requirements.txt
```

### 3.2 运行演示

```bash
# 查看所有可用曲线
python demo_advanced_curves.py --list

# 显示所有参数方程曲线
python demo_advanced_curves.py --parametric

# 显示所有分形曲线
python demo_advanced_curves.py --fractal

# 显示所有曲线
python demo_advanced_curves.py --all

# 显示特定曲线
python demo_advanced_curves.py --curve lissajous_classic
python demo_advanced_curves.py --curve koch_snowflake
```

### 3.3 集成到主程序

```python
# 在 main.py 中集成
from advanced_trajectory import AdvancedTrajectoryGenerator as ATG
from fractal_trajectory import FractalTrajectoryGenerator as FTG

# 生成轨迹
trajectory = ATG.lissajous(num_points=1500, a=3, b=4, delta=math.pi/2)
# 或
trajectory = FTG.koch_snowflake(iterations=4)

# 运行仿真
python main.py --mode sim_only
```

---

## 📊 四、性能对比表

| 曲线类型 | 复杂度 | 点数范围 | 生成时间 | 视觉冲击 | 数学美感 | 适合场景 |
|---------|--------|---------|---------|---------|---------|---------|
| 李萨如 (3:4) | ⭐⭐⭐ | 1000-2000 | 瞬间 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 科技展示 |
| 外摆线 | ⭐⭐⭐⭐ | 2000-3000 | 瞬间 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 艺术绘图 |
| 内摆线 | ⭐⭐⭐⭐ | 2000-3000 | 瞬间 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 机械美学 |
| 玫瑰线 | ⭐⭐ | 800-1500 | 瞬间 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 简洁优雅 |
| 蝴蝶曲线 | ⭐⭐⭐⭐⭐ | 2000-3000 | <1s | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 有机形态 |
| 调和振子 | ⭐⭐⭐ | 1500-2500 | 瞬间 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 动态模拟 |
| Koch 雪花 | ⭐⭐⭐⭐ | 768-3072 | 1-5s | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 分形教学 |
| 龙曲线 | ⭐⭐⭐⭐⭐ | 4096-8192 | 2-10s | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 分形艺术 |
| Hilbert 曲线 | ⭐⭐⭐ | 1024-4096 | 1-3s | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 路径规划 |

---

## 🎯 五、推荐应用组合

### 5.1 工业展示套装（快速绘制）

```python
# 1. 外摆线 - 五瓣花（2000点，~40秒@50mm/s）
ATG.epitrochoid(num_points=2000, R=150, r=50, d=30)

# 2. 李萨如 3:4（1500点，~30秒）
ATG.lissajous(num_points=1500, a=3, b=4, delta=math.pi/2)

# 3. 玫瑰线 k=5（1000点，~20秒）
ATG.rose_curve(num_points=1000, k=5)
```

### 5.2 数学艺术套装（精细绘制）

```python
# 1. Koch 雪花 5次迭代（3072点，~60秒）
FTG.koch_snowflake(iterations=5)

# 2. 蝴蝶曲线（2500点，~50秒）
ATG.butterfly_curve(num_points=2500)

# 3. 龙曲线 12次迭代（4096点，~80秒）
FTG.dragon_curve(iterations=12)
```

### 5.3 极致展示套装（顶级效果）

```python
# 1. 内摆线 - 五角星（2000点）
ATG.hypotrochoid(num_points=2000, R=150, r=50, d=70)

# 2. Koch 雪花 6次迭代（12288点）
FTG.koch_snowflake(iterations=6)

# 3. Hilbert 曲线 阶数6（4096点）
FTG.hilbert_curve(order=6)
```

---

## 🔧 六、高级自定义

### 6.1 修改工作区范围

```python
# 在 advanced_trajectory.py 或 fractal_trajectory.py 中修改
class AdvancedTrajectoryGenerator(TrajectoryGenerator):
    WORK_CENTER_X = 500.0   # 工作区中心X
    WORK_CENTER_Y = 160.0   # 工作区中心Y
    WORK_WIDTH = 700.0      # 工作区宽度
    WORK_HEIGHT = 260.0     # 工作区高度
```

### 6.2 自定义速度曲线

```python
# 为不同段设置不同速度
trajectory = ATG.lissajous(...)
for i, point in enumerate(trajectory):
    if i < len(trajectory) // 2:
        point.velocity = 30.0  # 前半段慢
    else:
        point.velocity = 70.0  # 后半段快
```

### 6.3 组合多个曲线

```python
# 连续绘制多个曲线
from models import Point2D, TrajectoryPoint

traj1 = ATG.rose_curve(k=5)
traj2 = ATG.cardioid()

# 重新索引
combined = traj1 + traj2
for i, point in enumerate(combined):
    point.index = i
```

---

## 📚 七、数学参考

### 7.1 参数方程资源

- **李萨如图形**：[Wikipedia - Lissajous curve](https://en.wikipedia.org/wiki/Lissajous_curve)
- **摆线**：[MathWorld - Epitrochoid](https://mathworld.wolfram.com/Epitrochoid.html)
- **玫瑰线**：[MathWorld - Rose](https://mathworld.wolfram.com/Rose.html)

### 7.2 分形艺术资源

- **Koch 雪花**：[Wikipedia - Koch snowflake](https://en.wikipedia.org/wiki/Koch_snowflake)
- **龙曲线**：[Wikipedia - Dragon curve](https://en.wikipedia.org/wiki/Dragon_curve)
- **Hilbert 曲线**：[Wikipedia - Hilbert curve](https://en.wikipedia.org/wiki/Hilbert_curve)

---

## ⚠️ 八、注意事项

### 8.1 限位保护

- 所有轨迹自动缩放到工作区：X: 0-1000mm, Y: -50-370mm
- 超出限位的点会被裁剪并记录警告日志

### 8.2 性能优化

- 点数越多，PLC 通讯时间越长
- 推荐点数：1000-3000（平衡质量与速度）
- 高精度场景：3000-5000点
- 快速演示：500-1500点

### 8.3 速度建议

- 复杂曲线（分形）：30-50 mm/s
- 简单曲线（参数方程）：50-80 mm/s
- 直线段：80-100 mm/s

---

**创建日期**：2024-12-06
**适用系统**：S7-1200/1500 + Snap7 Python 通讯
**作者**：Claude Code + Advanced Trajectory Library
**许可**：开源，随意使用和修改

🎨 **让数学艺术在机械臂上绽放！**
