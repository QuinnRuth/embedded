"""
数据模型模块 - 使用 dataclass 定义所有数据结构
"""
from dataclasses import dataclass, field
from typing import Literal
from enum import Enum


class RobotStatus(Enum):
    """机器人状态枚举"""
    IDLE = "idle"           # 空闲
    CONNECTING = "connecting"  # 连接中
    READY = "ready"         # 就绪
    MOVING = "moving"       # 运动中
    PAUSED = "paused"       # 暂停
    ERROR = "error"         # 错误
    DONE = "done"           # 完成


@dataclass
class Point2D:
    """二维坐标点"""
    x: float
    y: float

    def __iter__(self):
        """允许元组解包：x, y = point"""
        return iter((self.x, self.y))

    def distance_to(self, other: 'Point2D') -> float:
        """计算到另一个点的距离"""
        import math
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def __repr__(self) -> str:
        return f"Point2D(x={self.x:.2f}, y={self.y:.2f})"


@dataclass
class TrajectoryPoint:
    """轨迹点（包含位置和速度）"""
    position: Point2D
    velocity: float
    index: int = 0

    def __repr__(self) -> str:
        return f"Traj[{self.index}]({self.position.x:.1f}, {self.position.y:.1f}, v={self.velocity})"


@dataclass
class RobotState:
    """机器人实时状态（线程安全共享）"""
    current_position: Point2D = field(default_factory=lambda: Point2D(0, 0))
    target_position: Point2D = field(default_factory=lambda: Point2D(0, 0))
    status: RobotStatus = RobotStatus.IDLE
    point_index: int = 0
    total_points: int = 0
    velocity: float = 0.0
    error_message: str = ""

    # PLC 反馈信号
    plc_busy: bool = False
    plc_done: bool = False
    plc_error: bool = False

    def progress_percent(self) -> float:
        """计算进度百分比"""
        if self.total_points == 0:
            return 0.0
        return (self.point_index / self.total_points) * 100

    def __repr__(self) -> str:
        return (f"RobotState(pos={self.current_position}, "
                f"status={self.status.value}, "
                f"progress={self.progress_percent():.1f}%)")


@dataclass
class PLCConfig:
    """PLC 配置"""
    ip: str = "192.168.0.1"
    rack: int = 0
    slot: int = 1
    db: int = 200
    velocity: float = 50.0
    timeout: float = 30.0
    poll_interval: float = 0.01  # 10ms 轮询周期


@dataclass
class SimulationConfig:
    """仿真配置"""
    fps: int = 60
    window_size: tuple[int, int] = (800, 600)
    xlim: tuple[float, float] = (0, 800)
    ylim: tuple[float, float] = (-200, 400)
    trail_length: int = 100  # 轨迹尾迹长度
    show_grid: bool = True


@dataclass
class AppConfig:
    """应用配置"""
    plc: PLCConfig = field(default_factory=PLCConfig)
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
    mode: Literal["sync", "sim_only", "plc_only"] = "sync"

    @classmethod
    def from_yaml(cls, filepath: str) -> 'AppConfig':
        """从 YAML 文件加载配置"""
        import yaml
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        plc_cfg = PLCConfig(**data.get('plc', {}))
        sim_cfg = SimulationConfig(**data.get('simulation', {}))
        mode = data.get('mode', 'sync')

        return cls(plc=plc_cfg, simulation=sim_cfg, mode=mode)
