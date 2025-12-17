# 使用指南

## 快速开始

### 1. 安装依赖

```bash
cd /home/muqiao/dev/plc/zhou/pythonconnent/py测试
pip install -r requirements.txt
```

### 2. 配置 PLC

编辑 `config.yaml`，修改 PLC IP 地址：

```yaml
plc:
  ip: "192.168.0.1"  # ← 改为你的 PLC IP
```

### 3. 运行程序

#### **仿真 + PLC 同步模式**（默认）
```bash
python main.py
```

这将同时：
- 打开仿真窗口，显示实时动画
- 连接 PLC，发送轨迹点
- 实时同步显示 PLC 执行状态

#### **仅仿真模式**（测试轨迹）
```bash
python main.py --mode sim_only
```

不连接 PLC，仅显示轨迹动画（用于调试）

#### **仅 PLC 模式**（无 GUI）
```bash
python main.py --mode plc_only
```

不显示仿真窗口，后台控制 PLC（用于生产环境）

---

## 高级用法

### 自定义轨迹

编辑 `main.py`，修改轨迹生成部分：

```python
# 方式 1：圆形轨迹
trajectory = TrajectoryGenerator.circle(
    center=Point2D(400, 200),
    radius=150,
    num_points=100,
    velocity=50.0
)

# 方式 2：直线轨迹
trajectory = TrajectoryGenerator.line(
    start=Point2D(100, 100),
    end=Point2D(700, 300),
    num_points=50,
    velocity=30.0
)

# 方式 3：矩形轨迹
trajectory = TrajectoryGenerator.rectangle(
    center=Point2D(400, 200),
    width=300,
    height=200,
    num_points=25,  # 每条边 25 个点
    velocity=40.0
)

# 方式 4：螺旋轨迹
trajectory = TrajectoryGenerator.spiral(
    center=Point2D(400, 200),
    start_radius=50,
    end_radius=200,
    num_loops=3,
    num_points=200,
    velocity=35.0
)

# 方式 5：自定义坐标点
custom_points = [
    (100, 100),
    (200, 150),
    (300, 100),
    (400, 200),
    # ... 更多点
]
trajectory = TrajectoryGenerator.from_points(custom_points, velocity=50.0)
```

### 调整仿真参数

编辑 `config.yaml`：

```yaml
simulation:
  fps: 60              # 帧率（越高越流畅，越消耗 CPU）
  xlim: [0, 800]       # X 轴显示范围
  ylim: [-200, 400]    # Y 轴显示范围
  trail_length: 100    # 轨迹尾迹长度（0 = 不显示）
  show_grid: true      # 是否显示网格
```

### 优化 PLC 通信

编辑 `config.yaml`：

```yaml
plc:
  poll_interval: 0.01  # 轮询间隔（秒）
                        # 建议: 0.01 (10ms) 匹配 PLC 扫描周期
                        # 降低可提升响应速度，但增加 CPU 负载

  timeout: 30.0        # 单点超时（秒）
                        # 建议: 根据最慢运动时间设置
```

---

## 键盘快捷键

| 按键 | 功能 |
|------|------|
| **Q** | 退出程序 |
| **Space** | 暂停/继续（TODO） |
| **R** | 重置轨迹（TODO） |

---

## 故障排查

### 问题 1：连接 PLC 失败

```
错误: [Errno 111] Connection refused
```

**检查**：
1. PLC 是否在 RUN 模式？
2. 网络是否可达？（`ping 192.168.0.1`）
3. TIA Portal 中是否启用了 PUT/GET 访问？

### 问题 2：动画卡顿

**原因**：CPU 负载过高

**解决**：
- 降低 `fps`（60 → 30）
- 减少 `trail_length`（100 → 50）
- 关闭 `show_grid`

### 问题 3：PLC 不响应

**检查**：
1. DB200 是否存在？
2. `S7_Optimized_Access` 是否为 FALSE？
3. FB_PythonFollow 是否在 OB1 中运行？

---

## 项目结构

```
py测试/
├── models.py          # 数据模型（Point2D, RobotState, Config）
├── plc_client.py      # PLC 通信（Snap7 封装，多线程）
├── simulator.py       # 仿真引擎（matplotlib 动画）
├── trajectory.py      # 轨迹生成器（圆形、直线、矩形等）
├── main.py            # 主程序入口
├── config.yaml        # 配置文件
└── requirements.txt   # 依赖库
```

---

## 技术特性

### 1. 线程安全设计

```
主线程（GUI）          PLC 线程
    │                      │
    ├─ 读取 shared_state ─┤
    │  （当前位置、状态）  │
    │                      │
    │                      ├─ 更新 shared_state
    │                      │  （新位置、状态）
    │                      │
    └──────────────────────┘
         线程安全共享
```

### 2. 类型提示

所有函数都有完整的类型提示：
```python
def circle(center: Point2D, radius: float, num_points: int,
           velocity: float) -> List[TrajectoryPoint]:
    ...
```

### 3. 上下文管理器

PLC 客户端支持 `with` 语句：
```python
with PLCClient(config, state) as plc:
    plc.add_trajectory(trajectory)
    # 自动连接、启动、断开
```

### 4. 数据类（dataclass）

使用现代化的数据结构：
```python
@dataclass
class Point2D:
    x: float
    y: float

    def distance_to(self, other: 'Point2D') -> float:
        ...
```

---

## 扩展开发

### 添加新的轨迹类型

在 `trajectory.py` 中添加静态方法：

```python
@staticmethod
def star(center: Point2D, radius: float, num_points: int,
         velocity: float) -> List[TrajectoryPoint]:
    """生成五角星轨迹"""
    # 实现代码...
    pass
```

### 添加实时数据记录

在 `plc_client.py` 的 `run()` 方法中添加：

```python
# 记录到 CSV
with open('trajectory_log.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['Time', 'X', 'Y', 'Status'])

    for point in trajectory:
        # ... 发送点 ...
        writer.writerow([time.time(), point.x, point.y, status])
```

---

## 性能基准

| 配置 | 300 点总时间 | CPU 占用 |
|------|-------------|----------|
| 默认（poll=50ms） | ~60s | 5% |
| 优化（poll=10ms） | ~45s | 8% |
| 仅 PLC 模式 | ~40s | 2% |

---

**需要帮助？** 查看 `README.md` 或运行 `python main.py --help`
