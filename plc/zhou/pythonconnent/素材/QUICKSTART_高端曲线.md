# 高端数学曲线 - 快速启动指南

## 🚀 一、立即体验（3分钟）

### 1.1 查看所有可用曲线

```bash
cd /home/muqiao/dev/plc/zhou/pythonconnent/仿真
python demo_advanced_curves.py --list
```

### 1.2 显示参数方程曲线（推荐先看这个！）

```bash
python demo_advanced_curves.py --parametric
```

**会显示 12 种参数方程曲线**：
- 李萨如图形（3种）
- 外摆线/内摆线（4种）
- 玫瑰线（3种）
- 蝴蝶曲线、心形线、调和振子

### 1.3 显示分形曲线

```bash
python demo_advanced_curves.py --fractal
```

**会显示 7 种分形曲线**：
- Koch 雪花（2种迭代）
- Koch 曲线
- 龙曲线（2种迭代）
- Hilbert 曲线（2种阶数）

### 1.4 显示特定曲线（大窗口）

```bash
# 外摆线 - 五瓣花（最推荐！）
python demo_advanced_curves.py --curve epitrochoid_flower

# 李萨如 3:4 经典花纹
python demo_advanced_curves.py --curve lissajous_classic

# Koch 雪花
python demo_advanced_curves.py --curve koch_snowflake

# 龙曲线
python demo_advanced_curves.py --curve dragon_curve
```

---

## 🎯 二、集成到主程序（在 main.py 中使用）

### 2.1 修改 main.py 使用新曲线

编辑 `/home/muqiao/dev/plc/zhou/pythonconnent/仿真/main.py`：

```python
# 在文件顶部添加导入
from advanced_trajectory import AdvancedTrajectoryGenerator as ATG
from fractal_trajectory import FractalTrajectoryGenerator as FTG
import math

# 在生成轨迹的部分（大约第 XX 行），替换为：

# === 选择你想要的轨迹 ===

# 方案1：外摆线 - 五瓣花（推荐）
trajectory_points = ATG.epitrochoid(
    num_points=2000,
    velocity=config.plc.velocity,
    R=150.0,
    r=50.0,
    d=30.0
)

# 方案2：李萨如 3:4
# trajectory_points = ATG.lissajous(
#     num_points=1500,
#     velocity=config.plc.velocity,
#     a=3.0,
#     b=4.0,
#     delta=math.pi/2
# )

# 方案3：Koch 雪花
# trajectory_points = FTG.koch_snowflake(
#     iterations=4,
#     velocity=config.plc.velocity
# )

# 方案4：龙曲线
# trajectory_points = FTG.dragon_curve(
#     iterations=12,
#     velocity=config.plc.velocity
# )
```

### 2.2 运行仿真

```bash
cd /home/muqiao/dev/plc/zhou/pythonconnent/仿真
python main.py --mode sim_only
```

---

## 💡 三、我的推荐（按优先级）

### 🥇 Top 1：外摆线 - 五瓣花
**为什么选它**：
- ✅ 视觉冲击力强（花瓣优雅）
- ✅ 点数适中（2000点，~40秒绘制）
- ✅ 数学原理清晰（万花尺效果）
- ✅ 工业展示效果极佳

```python
trajectory = ATG.epitrochoid(num_points=2000, R=150, r=50, d=30)
```

---

### 🥈 Top 2：李萨如 3:4
**为什么选它**：
- ✅ 经典科技美学
- ✅ 点数少（1500点，~30秒）
- ✅ 适合快速演示
- ✅ 观众认知度高（示波器图案）

```python
trajectory = ATG.lissajous(num_points=1500, a=3, b=4, delta=math.pi/2)
```

---

### 🥉 Top 3：Koch 雪花（4次迭代）
**为什么选它**：
- ✅ 分形艺术代表作
- ✅ 教育意义强（展示递归）
- ✅ 点数适中（768点，~15秒）
- ✅ 数学美感极强

```python
trajectory = FTG.koch_snowflake(iterations=4)
```

---

### 🎖️ Top 4：内摆线 - 五角星
**为什么选它**：
- ✅ 机械美学（齿轮/星形）
- ✅ 锐利的线条（视觉震撼）
- ✅ 适合技术展示

```python
trajectory = ATG.hypotrochoid(num_points=2000, R=150, r=50, d=70)
```

---

### 🌟 Top 5：龙曲线（12次迭代）
**为什么选它**：
- ✅ 分形艺术最炫酷
- ✅ 点数多（4096点，展示精度）
- ✅ 适合长时间演示
- ⚠️ 时间较长（~80秒）

```python
trajectory = FTG.dragon_curve(iterations=12)
```

---

## 📊 四、场景推荐

### 🏢 场景1：客户展示（30秒快速演示）

**目标**：快速展示系统精度和美感

```python
# 推荐：玫瑰线 k=5（20秒）
trajectory = ATG.rose_curve(num_points=1000, k=5)
```

---

### 🎓 场景2：技术培训（展示数学原理）

**目标**：讲解参数方程和分形

```python
# 1. 李萨如（讲解频率和相位）
trajectory1 = ATG.lissajous(num_points=1500, a=3, b=4, delta=math.pi/2)

# 2. Koch雪花（讲解递归和分形）
trajectory2 = FTG.koch_snowflake(iterations=4)
```

---

### 🏆 场景3：展会/比赛（震撼效果）

**目标**：最大视觉冲击，不惜时间

```python
# 1. 外摆线 - 外延花（夸张花瓣）
trajectory1 = ATG.epitrochoid(num_points=2500, R=120, r=40, d=60)

# 2. Koch雪花 5次迭代（超精细）
trajectory2 = FTG.koch_snowflake(iterations=5)

# 3. 龙曲线 13次迭代（极致细节）
trajectory3 = FTG.dragon_curve(iterations=13)
```

---

### 🔬 场景4：精度测试（评估系统性能）

**目标**：测试机械臂轨迹跟随精度

```python
# Hilbert曲线 - 全覆盖路径
trajectory = FTG.hilbert_curve(order=5)  # 1024个均匀点
```

---

## 🛠️ 五、高级技巧

### 5.1 调整速度

```python
# 不同段使用不同速度
trajectory = ATG.epitrochoid(num_points=2000, R=150, r=50, d=30)

for i, point in enumerate(trajectory):
    progress = i / len(trajectory)
    if progress < 0.2:
        point.velocity = 30.0  # 开始慢一点
    elif progress > 0.8:
        point.velocity = 30.0  # 结束慢一点
    else:
        point.velocity = 60.0  # 中间快一点
```

### 5.2 组合多个曲线

```python
# 连续绘制三个小图案
traj1 = ATG.rose_curve(num_points=500, k=5, amplitude=80)
traj2 = ATG.cardioid(num_points=400, amplitude=60)
traj3 = ATG.rose_curve(num_points=500, k=7, amplitude=80)

# 合并并重新索引
combined = traj1 + traj2 + traj3
for i, point in enumerate(combined):
    point.index = i
```

### 5.3 自定义工作区

编辑 `advanced_trajectory.py` 或 `fractal_trajectory.py`：

```python
class AdvancedTrajectoryGenerator(TrajectoryGenerator):
    # 修改这些值
    WORK_CENTER_X = 600.0   # 向右移动100mm
    WORK_CENTER_Y = 200.0   # 向上移动40mm
    WORK_WIDTH = 600.0      # 减小工作区宽度
    WORK_HEIGHT = 200.0     # 减小工作区高度
```

---

## ⚡ 六、性能优化

### 6.1 点数与时间对照表

假设速度 = 50 mm/s，轨迹周长约 800 mm：

| 点数 | 绘制时间 | 推荐场景 |
|------|---------|---------|
| 500 | ~10秒 | 快速演示 |
| 1000 | ~16秒 | 标准演示 |
| 1500 | ~24秒 | 精细演示 |
| 2000 | ~32秒 | 高质量展示 |
| 3000 | ~48秒 | 极致细节 |
| 4000+ | ~64秒+ | 艺术品级 |

### 6.2 速度建议

```python
# 快速演示
velocity = 80.0  # mm/s

# 标准展示
velocity = 50.0  # mm/s（推荐）

# 精细绘制
velocity = 30.0  # mm/s

# 极致细节（分形）
velocity = 20.0  # mm/s
```

---

## 🎬 七、完整示例

### 示例：运行外摆线到 PLC

```bash
cd /home/muqiao/dev/plc/zhou/pythonconnent/仿真

# 1. 先仿真预览
python -c "
from advanced_trajectory import AdvancedTrajectoryGenerator as ATG
import matplotlib.pyplot as plt

traj = ATG.epitrochoid(num_points=2000, R=150, r=50, d=30)
xs = [p.position.x for p in traj]
ys = [p.position.y for p in traj]

plt.figure(figsize=(10, 8))
plt.plot(xs, ys, linewidth=1)
plt.axis('equal')
plt.grid(True)
plt.title('外摆线 - 五瓣花')
plt.show()
"

# 2. 确认无误后，修改 main.py 使用该轨迹

# 3. 运行到 PLC
python main.py  # 同步模式（PLC + 仿真）
```

---

## 📚 八、参考资料

- **完整文档**：`README_高端数学曲线库.md`
- **源代码**：
  - `advanced_trajectory.py` - 参数方程
  - `fractal_trajectory.py` - 分形艺术
  - `demo_advanced_curves.py` - 演示脚本

---

## 🆘 九、常见问题

### Q1：曲线超出工作区怎么办？

**A**：所有曲线已自动缩放到工作区，并且有限位保护。如果仍然超出，检查：
```python
# 查看轨迹范围
xs = [p.position.x for p in trajectory]
ys = [p.position.y for p in trajectory]
print(f"X: [{min(xs)}, {max(xs)}]")
print(f"Y: [{min(ys)}, {max(ys)}]")
```

### Q2：点数太多，PLC 通讯太慢？

**A**：减少点数或提高速度：
```python
# 减少点数
trajectory = ATG.lissajous(num_points=800)  # 原来 1500

# 或提高速度
trajectory = ATG.lissajous(velocity=80.0)   # 原来 50.0
```

### Q3：想要更炫酷的效果？

**A**：尝试这些组合：
```python
# 外摆线 - 外延花（d > r）
ATG.epitrochoid(R=120, r=40, d=60)

# 李萨如 5:4（五角星）
ATG.lissajous(a=5, b=4, delta=0)

# 玫瑰线分数k（复杂花纹）
ATG.rose_curve(k=7/3)
```

---

**创建日期**：2024-12-06
**最后更新**：2024-12-06
**版本**：v1.0

🚀 **开始你的数学艺术之旅吧！**
