# PLC 配置指南

## 1. 导入程序块

### DB200_Traj
程序块 → 右键 → 从外部源生成块 → 选择 `DB200_Traj.scl`

> 确保 DB 编号为 200，且 `S7_Optimized_Access := 'FALSE'`

### FB_PythonFollow
程序块 → 右键 → 从外部源生成块 → 选择 `FB_PythonFollow.scl`

## 2. OB1 配置（LAD）

### Network 1: 调用 FB
拖入 `Python跟随控制` → 自动生成 `DB_PythonFollow`

### Network 2: MC_Power X轴
```
Axis := "X轴"
Enable := "DB_PythonFollow".X轴使能请求
```

### Network : MC_Power Y轴
```
Axis := "Y轴"
Enable := "DB_PythonFollow".Y轴使能请求
```

### Network : MC_MoveAbsolute X轴
```
Axis := "X轴"
Execute := "DB_PythonFollow".X轴定位启动
Position := "DB_PythonFollow".X轴目标位置
Velocity := "DB_PythonFollow".定位速度
```

### Network : MC_MoveAbsolute Y轴
```
Axis := "Y轴"
Execute := "DB_PythonFollow".Y轴定位启动
Position := "DB_PythonFollow".Y轴目标位置
Velocity := "DB_PythonFollow".定位速度
```

### 回填 FB 输入

输入：
X轴定位完成 ← MC_MoveAbs_DB_X.Done
Y轴定位完成 ← MC_MoveAbs_DB_Y.Done
输出：
X轴目标位置 → MC_MoveAbsolute_X.Position
Y轴目标位置 → MC_MoveAbsolute_Y.Position
X轴定位启动 → MC_MoveAbsolute_X.Execute
Y轴定位启动 → MC_MoveAbsolute_Y.Execute
|
## 3. 启用 S7 通讯

CPU 属性 → 防护与安全 → 勾选 **允许 PUT/GET 通讯访问**

## 4. 手动测试

1. 下载程序
2. 在线打开 DB200_Traj
3. 设置：
   - `Enable := TRUE`
   - `X_Setpoint := 100.0`
   - `Y_Setpoint := 50.0`
   - `NewPoint := TRUE`
4. 观察 Busy→Done 变化

# Python-S7 轨迹通讯

Python 通过 S7 协议向 PLC 发送轨迹点，控制两轴运动。

## 文件

```
├── run.py              # Python 主程序（单文件）
├── requirements.txt    # 依赖：python-snap7
├── DB200_Traj.scl      # PLC 数据块（导入 TIA）
├── FB_PythonFollow.scl # PLC 跟随控制 FB（导入 TIA）
└── PLC配置指南.md      # TIA Portal 配置
```

## 使用

### 1. PLC 配置

见 `PLC配置指南.md`

### 2. Python 运行

```bash
pip install python-snap7
# 修改 run.py 中的 PLC_IP
python run.py
```

## 通讯协议

| 偏移 | 类型 | 变量 | 说明 |
|------|------|------|------|
| 0 | Real | X_Setpoint | X目标 |
| 4 | Real | Y_Setpoint | Y目标 |
| 8 | Real | Velocity | 速度 |
| 12 | Int | PointIndex | 索引 |
| 14.0 | Bool | NewPoint | 新点 |
| 14.1 | Bool | Busy | 执行中 |
| 14.2 | Bool | Done | 完成 |
| 14.3 | Bool | Error | 错误 |
| 14.4 | Bool | Enable | 使能 |

## 握手流程

```
Python              PLC
  │ X/Y + NewPoint   │
  │ ───────────────> │ Busy=TRUE
  │                  │ 执行运动
  │ <─────────────── │ Done=TRUE
  │ 发送下一个点...  │
```

## 注意

- PLC 需启用 PUT/GET 访问
- DB200 需设为非优化访问
