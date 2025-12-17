# 项目协作指南

## 目录与角色
- `pythonconnent/仿真/`：Python + snap7 轨迹仿真与 PLC 同步控制（matplotlib 动画、多线程、YAML 配置，核心入口 `main.py`，通信封装 `plc_client.py`，轨迹生成 `trajectory.py`）。
- `pythonconnent/最简单的画圆通讯加测试/`：最小化 Python-S7 单文件示例（`run.py`）及 DB200/FB 导入文件，含架构与原理说明。
- `pythonconnent/素材/`：turtle 绘图集合与安全/架构清单，可复用图案或轨迹生成思路。
- `画圆扩展版/画圆/`：简化 MC 画圆流程 SCL（`FB_CircleSimple.scl`、`画圆简易版敲定版.scl`），附 TIA 配置指南。
- `钻孔单流程控制/`：MC 库版钻孔单流程（`最终版本_MC库版.scl`）和完整的 TIA Portal 操作流程。

## 开发与运行流程
- Python 仿真同步（推荐先在纯仿真验证）  
  - 进入 `pythonconnent/仿真/`（文档中路径示例为“py测试”，实际目录即本路径）。  
  - 安装依赖：`pip install -r requirements.txt`。  
  - 配置 `config.yaml`：设置 `plc.ip`、`db=200`、`simulation.fps/window_size/xlim/ylim`；需要 PUT/GET 访问与非优化 DB200。  
  - 运行模式：`python main.py`（默认同步）、`--mode sim_only`（纯仿真）、`--mode plc_only`（无 GUI）。  
  - 轨迹切换：在 `main.py` 中选用 `TrajectoryGenerator.circle/line/rectangle/spiral/...` 或自定义点集。  
  - 关键按键：`Q` 退出，`Space` 暂停/继续（若实现），`R` 复位；状态在窗口左上角显示。  
  - 性能与握手：`poll_interval` 建议 10–50 ms；DB200 Enable/NewPoint/Busy/Done 按握手顺序写读，发送新点前确保 Busy=0、Done=1、NewPoint=0（`wait_idle` → 清 Done → 写点 → 等待 Done）。

- Python 最小通讯示例  
  - 路径 `pythonconnent/最简单的画圆通讯加测试/`，依赖 `python-snap7`，运行 `python run.py`。  
  - 导入 `DB200_Traj.scl`（DB 号 200，`S7_Optimized_Access := FALSE`）、`FB_PythonFollow.scl` 到 TIA，OB1 中按文档连 MC_Power/MC_MoveAbsolute。  
  - 协议偏移：X/Y/Velocity/PointIndex 位于 DBD0/DBD4/DBD8/DBW12；NewPoint/Busy/Done/Error/Enable 位于 DBX14.0~14.4。  
  - 握手：Python 写 X/Y/Velocity + Enable=1 + NewPoint=1 → FB 置 Busy → MC 完成后置 Done/清 NewPoint → Python 读 Done/Busy 后发下一个点。

- 画圆简易版（SCL，6 个 MC 块）  
  - 导入 `画圆简易版敲定版.scl`/`FB_CircleSimple.scl`，OB1 按指南布置 Network 1~7，自动生成 `DB_CircleSimple`。  
  - 默认圆参数：圆心 (510, 176.3)，半径 80，速度 50，角度步进 5°。  
  - 状态流：10 使能 → 20 回原点 → 30 等待启动 → 100 初始化 → 110 移动起点 → 120 插补画圆 → 130 完成返回 30；启动/停止/复位输入需正确映射。  
  - 监控：关注 `当前状态`、`画圆进度`、MC_MoveAbsolute Done/Status 反馈。

- 钻孔 MC 库版  
  - 按 `钻孔单流程控制/TIA_Portal操作流程_MC库版.md`：创建项目与工艺对象（X/Y PTO），导入 `最终版本_MC库版.scl` 生成 `FB1 "钻孔控制_MC版"`。  
  - 创建 MC 实例 DB（Power/Reset/MoveJog 各双份）、主实例 `DB_钻孔控制`，OB1 按示例调用。  
  - IO 范围：输入 I4.0~I5.7，输出 Q10.0~Q11.7（Q10.0~Q10.3 由 MC 自动管理），执行器控制5~7 对应夹紧/钻下降/钻运行。  
  - 状态机与安全：急停/限位优先，定位超时与参数检查要保持；调试使用监控表观察状态与限位信号。

## 编码与命名规范
- SCL
  - 文件编码：UTF-8 with BOM。  
  - DB200 必须关闭优化访问；常量定义不加 `#`，局部变量使用时加 `#`；状态机单 CASE，先安全后流程。  
  - 轴命名需与工艺对象一致（"X轴"/"Y轴"）；MC 连线等价于实例 DB 读写，保持引脚/DB 名称一致。  
  - 轨迹/坐标写入后在 FB 内锁存为 `LReal`，避免执行期间被改写。
- Python
  - 使用类型提示/dataclass，线程安全共享状态；封装 snap7 读写时保持“等待-清除-发送-等待”节奏。  
  - 配置集中于 YAML，命令行参数优先于默认值；新增轨迹在 `trajectory.py` 添加静态方法。  
  - 日志/数据记录可在 `plc_client.py` 的 run/write_point 流程中追加（避免阻塞通信线程）。

## 测试与验收要点
- 仿真阶段：`python main.py --mode sim_only` 验证轨迹/参数；确认窗口 Status/Progress 与轨迹一致。  
- PLC 连线后：先在 TIA 在线监控 DB200/NewPoint/Busy/Done，手动写入一个点验证握手；再运行 Python 同步模式。  
- MC 监控：`MC_MoveAbsolute` 实例 DB 的 Execute/Done/Busy/Error 需与 FB 反馈一致。  
- 画圆/钻孔：执行前核对限位与急停，监控状态码卡点（10/20/110/120 等）并按文档排查。  
- 任何 IO/参数调整后，记录更新处（路径、参数表或映射表）并复测启停流程。

## 仿真界面操作（快捷键/按钮）
- Start 按钮：仅仿真模式启动/重置播放；PLC 模式切换暂停/继续。
- Gap Jump 按钮：开/关断点跳跃（大间隔不连线，阈值 80mm）。
- 轨迹切换：Tab / 方向键（左右/上下）循环切换右侧单选轨迹类型。
- 退出：`Q`。
- PLC 专用（仅连接 PLC 时有效）：`Space` 暂停/继续，`R` 复位，`S` 停止线程。

## 文档与变更要求
- 更新 PLC/通信相关改动时，同步修改对应目录下的 Markdown（配置指南/架构图/原理说明），保持偏移、状态位与代码一致。  
- 不随意删除或重命名 SCL 备份/实例 DB 文件；新增功能块请附简短使用说明和调用示例。  
- 提交信息建议说明影响范围（Python 仿真/PLC 画圆/钻孔），并备注已验证的模式（sim_only/同步/MC 调试）。

