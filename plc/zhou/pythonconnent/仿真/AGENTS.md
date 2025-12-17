# 仿真与 PLC 同步子项目协作说明

## 目录速览
- `main.py`：入口；解析参数（mode）、加载 YAML、启动仿真与 PLC 线程。
- `config.yaml`：PLC IP/DB 号、轮询间隔、仿真窗口/FPS/坐标范围等。
- `plc_client.py`：snap7 封装，多线程通信，含 `wait_idle`/`write_point`/`wait_for_done`。
- `trajectory.py`：轨迹生成（circle/line/rectangle/spiral/custom）。
- `models.py`：dataclass（Point2D、Config、SharedState）。
- `simulator.py`：matplotlib 动画渲染与状态展示。
- `README.md` / `QUICKSTART.md` / `USAGE.md`：操作指南与自定义示例。

## 快速运行（推荐顺序）
1) 安装依赖  
```bash
cd /home/muqiao/dev/plc/zhou/pythonconnent/仿真
pip install -r requirements.txt
```
2) 纯仿真验证轨迹（无 PLC）  
```bash
python main.py --mode sim_only
```
3) 同步 PLC（需 TIA 启用 PUT/GET，DB200 非优化访问）  
```bash
python main.py            # 默认同步模式
# 或无界面仅 PLC
python main.py --mode plc_only
```
4) 修改配置  
`config.yaml`：`plc.ip`、`plc.db=200`、`plc.poll_interval`(10–50ms)，`simulation.fps/window_size/xlim/ylim`。

## 关键握手（DB200）
- 偏移：X/Y/Velocity/PointIndex → DBD0/4/8/DBW12；NewPoint/Busy/Done/Error/Enable → DBX14.0~14.4。  
- 写点流程：`wait_idle` (Busy=0, Done=1, NewPoint=0, Enable=1) → 清 Done → 写 X/Y/Vel + NewPoint=1 → 等待 Busy→Done→Busy=0。  
- DB200 必须 `S7_Optimized_Access := FALSE`，CPU 需允许 PUT/GET。

## 轨迹与参数
- 在 `main.py` 选择 `TrajectoryGenerator.circle/line/rectangle/spiral/from_points`。  
- 圆轨迹默认 300 点，可通过命令行或 YAML 调整 `num_points`、`radius`、`velocity`、`angle_step`。

## 诊断与常见问题
- 无法连接：检查 IP、防火墙、PUT/GET、DB 号 200 是否存在。  
- Busy 一直为 1：确认 FB 在 OB1 运行且 MC 轴反馈正常。  
- Done 误判：确保发送新点前清 Done。  
- 动画卡顿：降低 `simulation.fps` 或轨迹点数。

## 编码约定
- Python：类型提示 + dataclass；线程共享状态需锁/安全结构；通信线程避免阻塞（日志/记录放异步或轻量）。  
- 日志与记录：可在 `plc_client.py` 中追加 CSV 记录，但勿阻塞循环。

## 提交与文档更新
- 变更握手/偏移/配置时，同步更新本文件及 `README.md`/`USAGE.md`。  
- 新增轨迹或模式：补充 `trajectory.py` 示例与命令示例。

