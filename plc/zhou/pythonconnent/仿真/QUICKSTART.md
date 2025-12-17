# 快速开始指南

## 🎯 5 分钟上手

### 1. 安装依赖（已完成✅）
```bash
cd /home/muqiao/dev/plc/zhou/pythonconnent/py测试
pip install -r requirements.txt
```

### 2. 运行仿真（无需 PLC）
```bash
python main.py --mode sim_only
```

**效果预览**：
- 🎨 打开动画窗口
- 🔴 红色圆点 = 当前位置
- 🔵 蓝色空心圆 = 目标位置
- 🟢 绿色轨迹 = 已走路径
- ⚪ 灰色虚线 = 完整轨迹（300 点圆形）

**控制**：
- 按 `Q` 键退出

### 3. 连接 PLC（实际运动）
```bash
# 1. 修改 config.yaml 中的 PLC IP
vim config.yaml  # 改 ip: "192.168.0.1"

# 2. 运行同步模式
python main.py
```

---

## 📊 显示信息

动画窗口左上角显示：
```
Status: idle / moving / done
Current: (当前 X, Y 坐标)
Target: (目标 X, Y 坐标)
Velocity: 速度 (mm/s)
Progress: 当前点 / 总点数 (百分比)
PLC: Busy=True/False, Done=True/False
```

---

## 🛠️ 自定义轨迹

编辑 `main.py` 第 45 行：

```python
# 圆形（默认）
trajectory = TrajectoryGenerator.circle(
    center=Point2D(491.3, 133.9),
    radius=182.4,
    num_points=300,
    velocity=50.0
)

# 直线
trajectory = TrajectoryGenerator.line(
    start=Point2D(100, 100),
    end=Point2D(700, 300),
    num_points=50,
    velocity=30.0
)

# 矩形
trajectory = TrajectoryGenerator.rectangle(
    center=Point2D(400, 200),
    width=300,
    height=200,
    num_points=25,
    velocity=40.0
)
```

---

## ⚡ 性能调优

编辑 `config.yaml`：

```yaml
plc:
  poll_interval: 0.01  # 降低延迟（10ms → 5ms）
  velocity: 100.0      # 提高速度（50 → 100）

simulation:
  fps: 30              # 降低帧率节省 CPU（60 → 30）
  trail_length: 50     # 减少尾迹长度
```

---

## 🐛 故障排查

| 问题 | 解决方案 |
|------|----------|
| `ImportError: No module named 'snap7'` | 运行 `pip install python-snap7` |
| 窗口无响应 | 按 `Q` 退出，重新运行 |
| PLC 连接失败 | 检查 IP、PUT/GET 访问、DB200 配置 |
| 动画卡顿 | 降低 FPS 或减少轨迹点数 |

---

## 🎓 进阶功能

### 批量测试轨迹
```bash
# 创建测试脚本
python -c "
from trajectory import TrajectoryGenerator
from models import Point2D
traj = TrajectoryGenerator.spiral(
    center=Point2D(400, 200),
    start_radius=50,
    end_radius=200,
    num_loops=3,
    num_points=200,
    velocity=60.0
)
print(f'Generated {len(traj)} points')
"
```

### 记录轨迹数据
修改 `plc_client.py`，在 `run()` 方法中添加：
```python
with open('trajectory_log.csv', 'w') as f:
    f.write('Time,X,Y,Status\n')
    for point in trajectory:
        f.write(f'{time.time()},{point.x},{point.y},{status}\n')
```

---

**需要帮助？** 查看 `USAGE.md` 或 `README.md`
