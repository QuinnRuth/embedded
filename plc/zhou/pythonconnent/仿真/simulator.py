#!/usr/bin/env python3
"""
仿真引擎 - 使用 matplotlib 实时动画显示机器人运动
"""
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
from matplotlib.widgets import RadioButtons, Button  # 导入单选按钮和启动按钮
from collections import deque
import logging
import time
import math
import sys
import json
import ast
from collections import defaultdict
from pathlib import Path

# 配置中文字体（如果可用）
try:
    import matplotlib.font_manager as fm
    # 尝试使用系统中文字体
    font_path = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'  # WenQuanYi Zen Hei
    if fm.FontProperties(fname=font_path).get_name():
        plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']
except:
    # 如果没有中文字体，使用英文标题
    pass
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

BASE_DIR = Path(__file__).parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

PIXEL_NOIR_PATH = BASE_DIR.parent / "素材" / "pixelnoir_grid_1765041178878.py"

from models import SimulationConfig, RobotState, TrajectoryPoint, RobotStatus, Point2D
from advanced_trajectory import AdvancedTrajectoryGenerator as ATG  # type: ignore
from fractal_trajectory import FractalTrajectoryGenerator as FTG    # type: ignore
from trajectory import TrajectoryGenerator  # 导入轨迹生成器，用于动态重新生成轨迹


class RobotSimulator:
    """
    机器人仿真器

    职责：
    1. 显示实时动画（轨迹、当前位置、目标位置）
    2. 显示状态信息（位置、速度、进度）
    3. 响应键盘事件（暂停、重置、退出）
    4. 控制 PLC（暂停、继续、复位、停止）
    """

    def __init__(self, config: SimulationConfig, shared_state: RobotState,
                 trajectory: list[TrajectoryPoint], trajectory_params: dict = None,
                 plc_client=None):
        """
        初始化仿真器

        参数:
            config: 仿真配置
            shared_state: 共享状态（与 PLC 同步）
            trajectory: 初始轨迹点列表
            trajectory_params: 轨迹生成参数字典，包含：
                - center: Point2D，圆心坐标
                - radius: float，半径
                - velocity: float，速度
                - num_points: int，点数
                用于滑块动态重新生成轨迹
            plc_client: PLC 客户端实例（可选），用于暂停/继续/复位控制
        """
        # 日志（必须最先初始化，因为后续方法会使用）
        self.logger = logging.getLogger(__name__)

        self.config = config
        self.shared_state = shared_state
        self.trajectory = trajectory
        self.trajectory_params = trajectory_params or {}
        self.plc_client = plc_client  # PLC 客户端引用（用于控制）
        self.sim_only = plc_client is None  # 仅仿真模式
        self.sim_running = False             # 是否开始播放（仅仿真）
        self._sim_idx = 0
        self._sim_last_ts = time.time()
        self._portrait_cache = None  # 缓存人像轨迹
        self.gap_jump_enabled = False
        self.gap_threshold = 80.0  # mm，判定断点的距离阈值
        if self.sim_only:
            self.shared_state.status = RobotStatus.IDLE

        # 初始化共享状态的轨迹信息
        self.shared_state.total_points = len(self.trajectory)
        if self.trajectory:
            self.shared_state.target_position = self.trajectory[0].position

        # 历史轨迹（用于显示尾迹）
        self.position_history = deque(maxlen=config.trail_length)

        # matplotlib 图形对象 - 使用 gridspec 分割布局
        # 左侧 85% 给主绘图区域，右侧 15% 给轨迹类型选择
        self.fig = plt.figure(figsize=(12, 8))
        grid = self.fig.add_gridspec(nrows=1, ncols=2, 
                                      width_ratios=[0.85, 0.15], wspace=0.1)

        # 主绘图区域
        self.ax = self.fig.add_subplot(grid[0, 0])

        # 轨迹类型选择区域（右侧）
        self.radio_ax = self.fig.add_subplot(grid[0, 1])
        self.radio_ax.set_title('Trajectory Type', fontsize=10)

        # 启动按钮区域（放在右侧面板下方）
        self.start_ax = self.fig.add_axes([0.82, 0.08, 0.12, 0.05])
        self.start_button = Button(self.start_ax, 'Start', color='#e0f7fa', hovercolor='#b2ebf2')
        self.start_button.label.set_fontsize(11)
        self.start_button.on_clicked(self.on_start_clicked)

        # 断点跳跃按钮
        self.gap_ax = self.fig.add_axes([0.82, 0.02, 0.12, 0.05])
        self.gap_button = Button(self.gap_ax, 'Gap Jump:Off', color='#f0f0f0', hovercolor='#e0e0e0')
        self.gap_button.label.set_fontsize(10)
        self.gap_button.on_clicked(self.on_gap_clicked)
        
        # 轨迹类型选择器
        self.trajectory_type = 'lissajous'  # 默认轨迹类型
        self.radio_buttons = None
        
        # 轨迹类型列表（用于键盘切换）
        self.trajectory_types_list = [
            'lissajous', 'epitrochoid', 'hypotrochoid', 'rose',
            'butterfly', 'cardioid', 'harmonic',
            'koch_snowflake', 'dragon_fractal', 'hilbert_fractal',
            'star', 'taiji', 'zheng',
            'spiralsquare', 'spiralarchimedes', 'spiralrose',
            'ironman', 'portrait'
        ]
        self.trajectory_type_index = 0  # 当前轨迹类型索引（用于循环切换）

        # 设置绘图区域
        self.setup_plot()
        
        # 创建轨迹类型选择器
        self.create_trajectory_selector()

        # 动画对象（稍后初始化）
        self.anim = None

    def on_start_clicked(self, _event):
        """启动按钮回调"""
        if self.plc_client and getattr(self.plc_client, "connected", False):
            # PLC 模式：切换暂停/继续
            if self.plc_client.is_paused():
                self.plc_client.resume()
                self.logger.info("PLC 已继续运行")
            else:
                self.plc_client.pause()
                self.logger.info("PLC 已暂停")
        else:
            # 仅仿真：启动/重置播放
            self.sim_running = True
            self._sim_last_ts = time.time()
            self._sim_idx = 0
            if self.trajectory:
                first = self.trajectory[0]
                self.shared_state.current_position = first.position
                self.shared_state.target_position = first.position
                self.shared_state.point_index = 1
                self.shared_state.total_points = len(self.trajectory)
                self.shared_state.velocity = first.velocity
                self.shared_state.status = RobotStatus.MOVING
            self.logger.info("仅仿真模式已开始运行")

    def load_portrait_from_json(self, center, velocity):
        """
        从像素坐标 JSON 生成连续轨迹，采用蛇形行遍历以减少跳跃。
        """
        if self._portrait_cache is None:
            try:
                if PIXEL_NOIR_PATH.suffix.lower() == ".json":
                    with open(PIXEL_NOIR_PATH, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    coords = data.get("coordinates") or data.get("pixels") or []
                    img = data.get("image", {})
                    width = data.get("width", img.get("width", 0))
                    height = data.get("height", img.get("height", 0))
                    pixel = data.get("pixelSize", img.get("pixelSize", 1))
                else:
                    # 读取 Python 点集文件，遍历所有 Assign，提取 points/pixels 列表（含函数体内）
                    text = PIXEL_NOIR_PATH.read_text(encoding='utf-8')
                    module = ast.parse(text)
                    pts = []
                    width = height = pixel = 0
                    for node in ast.walk(module):
                        if isinstance(node, ast.Assign):
                            # 捕获 width/height/pixelSize 常量
                            for tgt in node.targets:
                                if isinstance(tgt, ast.Name):
                                    if tgt.id.lower() in ("width", "image_width"):
                                        try:
                                            width = int(ast.literal_eval(node.value))
                                        except Exception:
                                            pass
                                    if tgt.id.lower() in ("height", "image_height"):
                                        try:
                                            height = int(ast.literal_eval(node.value))
                                        except Exception:
                                            pass
                                    if tgt.id.lower() in ("pixelsize", "pixel_size"):
                                        try:
                                            pixel = int(ast.literal_eval(node.value))
                                        except Exception:
                                            pass
                            # 捕获坐标列表
                            for tgt in node.targets:
                                if isinstance(tgt, ast.Name) and tgt.id in ("points", "pixels"):
                                    if isinstance(node.value, ast.List):
                                        for elt in node.value.elts:
                                            if isinstance(elt, ast.Tuple) and len(elt.elts) == 2:
                                                try:
                                                    x = ast.literal_eval(elt.elts[0])
                                                    y = ast.literal_eval(elt.elts[1])
                                                    pts.append((x, y))
                                                except Exception:
                                                    pass
                    if not pts:
                        raise ValueError("未在 Python 文件中找到 points/pixels 坐标列表")
                    coords = [{"x": x, "y": y} for x, y in pts]
                    if width == 0:
                        width = max(x for x, _ in pts) + 1
                    if height == 0:
                        height = max(y for _, y in pts) + 1
                    if pixel == 0:
                        pixel = 1
                self._portrait_cache = {
                    "coords": coords,
                    "width": width,
                    "height": height,
                    "pixel": pixel
                }
                self.logger.info(f"已加载人像像素坐标: {len(coords)} 点 (文件: {PIXEL_NOIR_PATH.name})")
            except Exception as e:
                self.logger.error(f"加载人像坐标失败: {e}")
                return []

        raw = self._portrait_cache
        coords = raw["coords"]
        width = raw["width"]
        height = raw["height"]
        pixel = raw["pixel"]

        if not coords or width == 0 or height == 0:
            self.logger.error("人像坐标数据为空或尺寸非法")
            return []

        # 工作区缩放
        x_span_mm = (self.config.xlim[1] - self.config.xlim[0]) * 0.8
        y_span_mm = (self.config.ylim[1] - self.config.ylim[0]) * 0.8
        img_w = width * pixel
        img_h = height * pixel
        scale = min(x_span_mm / img_w, y_span_mm / img_h)

        # 蛇形遍历，减少行间跳跃
        rows = defaultdict(list)
        for pt in coords:
            rows[pt["y"]].append(pt["x"])

        points = []
        for idx, y in enumerate(sorted(rows.keys())):
            xs = sorted(rows[y])
            if idx % 2 == 1:
                xs = list(reversed(xs))
            for x in xs:
                x_local = (x * pixel) - img_w / 2.0
                y_local = (height - y) * pixel - img_h / 2.0  # 翻转Y使图像朝上
                world_x = center.x + x_local * scale
                world_y = center.y + y_local * scale
                points.append(
                    TrajectoryPoint(
                        position=Point2D(world_x, world_y),
                        velocity=velocity,
                        index=len(points)
                    )
                )

        return points

    def on_gap_clicked(self, _event):
        """断点跳跃开关"""
        self.gap_jump_enabled = not self.gap_jump_enabled
        label = "Gap Jump:On" if self.gap_jump_enabled else "Gap Jump:Off"
        self.gap_button.label.set_text(label)
        self.logger.info(f"断点跳跃: {'开启' if self.gap_jump_enabled else '关闭'} (阈值 {self.gap_threshold} mm)")

    def setup_plot(self):
        """初始化绘图区域"""
        self.ax.set_xlim(*self.config.xlim)
        self.ax.set_ylim(*self.config.ylim)
        self.ax.set_aspect('equal')
        self.ax.set_title('Robot Simulation - Python + PLC Sync', fontsize=16, fontweight='bold')
        self.ax.set_xlabel('X Position (mm)', fontsize=12)
        self.ax.set_ylabel('Y Position (mm)', fontsize=12)

        if self.config.show_grid:
            self.ax.grid(True, alpha=0.3)

        # 绘制完整轨迹（灰色虚线）- 保存为实例变量以便动态更新
        traj_x = [p.position.x for p in self.trajectory]
        traj_y = [p.position.y for p in self.trajectory]
        self.trajectory_line, = self.ax.plot(
            traj_x, traj_y, 'gray', linestyle='--', linewidth=1, alpha=0.5, label='Trajectory'
        )

        # 标记起点和终点 - 保存为实例变量以便动态更新
        if self.trajectory:
            start = self.trajectory[0].position
            end = self.trajectory[-1].position
            self.start_marker, = self.ax.plot(start.x, start.y, 'go', markersize=10, label='Start')
            self.end_marker, = self.ax.plot(end.x, end.y, 'ro', markersize=10, label='End')
        else:
            # 如果初始轨迹为空，创建空标记
            self.start_marker, = self.ax.plot([], [], 'go', markersize=10, label='Start')
            self.end_marker, = self.ax.plot([], [], 'ro', markersize=10, label='End')

        # 当前位置（红色圆圈）
        self.current_pos_marker = Circle((0, 0), radius=15, color='red', fill=True, alpha=0.8)
        self.ax.add_patch(self.current_pos_marker)

        # 目标位置（蓝色空心圆）
        self.target_pos_marker = Circle((0, 0), radius=15, color='blue', fill=False, linewidth=2)
        self.ax.add_patch(self.target_pos_marker)

        # 已走轨迹（绿色实线）
        self.trail_line, = self.ax.plot([], [], 'g-', linewidth=2, alpha=0.7, label='Trail')

        # 状态文本
        self.status_text = self.ax.text(
            0.02, 0.98, '', transform=self.ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        )

        self.ax.legend(loc='upper right', fontsize=10)


    def create_trajectory_selector(self):
        """
        创建轨迹类型选择器（单选按钮）
        
        支持的轨迹类型：
        
        """
        # 轨迹类型列表（添加新的有趣轨迹）
        trajectory_types = [
            'Lissajous', 'Epitrochoid', 'Hypotrochoid', 'Rose',
            'Butterfly', 'Cardioid', 'Harmonic',
            'KochSnowflake', 'DragonFractal', 'HilbertFractal',
            'Star', 'Taiji', 'Zheng',
            'SpiralSquare', 'SpiralArchimedes', 'SpiralRose',
            'Ironman', 'Portrait'
        ]
        
        # 设置单选按钮区域的背景
        self.radio_ax.set_facecolor('#f8f8f8')
        
        # 创建单选按钮
        self.radio_buttons = RadioButtons(
            self.radio_ax, 
            trajectory_types,
            active=0,  # 默认选中 Circle
            activecolor='steelblue'
        )
        
        # 增大单选按钮的点击区域和字体
        for label in self.radio_buttons.labels:
            label.set_fontsize(11)
        
        # 绑定选择事件 - 使用 lambda 确保回调正确绑定
        def on_click(label):
            print(f"[点击] 选择了: {label}")  # 调试输出
            # 将按钮标签映射到内部小写标识
            label_map = {
                'lissajous': 'lissajous',
                'epitrochoid': 'epitrochoid',
                'hypotrochoid': 'hypotrochoid',
                'rose': 'rose',
                'butterfly': 'butterfly',
                'cardioid': 'cardioid',
                'harmonic': 'harmonic',
                'kochsnowflake': 'koch_snowflake',
                'dragonfractal': 'dragon_fractal',
                'hilbertfractal': 'hilbert_fractal',
                'star': 'star',
                'taiji': 'taiji',
                'zheng': 'zheng',
                'spiralsquare': 'spiralsquare',
                'spiralarchimedes': 'spiralarchimedes',
                'spiralrose': 'spiralrose',
                'ironman': 'ironman',
                'portrait': 'portrait'
            }
            key = label.lower().replace(" ", "")
            self.trajectory_type = label_map.get(key, 'lissajous')
            self.update_trajectory()
            self.fig.canvas.draw()
        
        self.radio_buttons.on_clicked(on_click)
        
        self.logger.info("轨迹类型选择器已创建（包含 Circle/Star/Taiji/Zheng/Rectangle/Dragon/Hilbert/Spiral/Ironman）")
        
        # 初始化时触发一次更新
        self.update_trajectory()

    def on_trajectory_type_changed(self, label):
        """
        轨迹类型变化回调
        
        参数:
            label: 选中的轨迹类型名称
        """
        new_type = label.lower()
        print(f"[DEBUG] 轨迹类型切换: {self.trajectory_type} -> {new_type}")  # 调试输出
        self.trajectory_type = new_type
        self.logger.info(f"轨迹类型已切换为: {label}")
        
        # 强制更新轨迹
        self.update_trajectory()
        
        # 强制重绘整个画布
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def update_trajectory(self, _=None):
        """
        根据轨迹类型重新生成轨迹并更新绘图

        触发时机：
        - 轨迹类型变化时自动调用
        - create_trajectory_selector() 初始化时调用一次

        更新内容：
        1. 根据当前轨迹类型生成轨迹点
        2. 更新灰色轨迹线
        3. 更新起点/终点标记
        4. 更新共享状态中的轨迹信息
        5. 清空历史轨迹（避免显示旧轨迹残留）

        参数:
            _: 未使用（matplotlib 回调可能需要此参数）
        """
        # 检查是否有必要的参数（圆心和半径）
        if 'center' not in self.trajectory_params or 'radius' not in self.trajectory_params:
            self.logger.warning("缺少轨迹参数 'center' 或 'radius'，无法更新轨迹")
            return

        # 从参数字典中获取值（使用默认值）
        num_points = int(self.trajectory_params.get('num_points', len(self.trajectory) or 300))
        start_angle = float(self.trajectory_params.get('start_angle_deg', 0.0))
        angle_step = float(self.trajectory_params.get('angle_step_deg', 360.0 / num_points if num_points > 0 else 1.0))
        
        # 获取通用参数
        center = self.trajectory_params['center']
        radius = self.trajectory_params['radius']
        velocity = self.trajectory_params.get('velocity', 50.0)

        # 根据轨迹类型生成不同的轨迹
        ttype = self.trajectory_type

        if ttype == 'lissajous':
            self.trajectory = ATG.lissajous(
                num_points=max(num_points, 800),
                velocity=velocity,
                a=3,
                b=4,
                delta=math.pi / 2,
                amplitude=radius * 1.2
            )
        elif ttype == 'epitrochoid':
            self.trajectory = ATG.epitrochoid(
                num_points=max(num_points, 1500),
                velocity=velocity,
                R=180,
                r=60,
                d=40,
                cycles=1
            )
        elif ttype == 'hypotrochoid':
            self.trajectory = ATG.hypotrochoid(
                num_points=max(num_points, 1500),
                velocity=velocity,
                R=180,
                r=60,
                d=80,
                cycles=1
            )
        elif ttype == 'rose':
            self.trajectory = ATG.rose_curve(
                num_points=max(num_points, 900),
                velocity=velocity,
                k=5
            )
        elif ttype == 'butterfly':
            self.trajectory = ATG.butterfly_curve(
                num_points=max(num_points, 2000),
                velocity=velocity
            )
        elif ttype == 'cardioid':
            self.trajectory = ATG.cardioid(
                num_points=max(num_points, 800),
                velocity=velocity,
                radius=radius
            )
        elif ttype == 'harmonic':
            self.trajectory = ATG.harmonic_oscillator(
                num_points=max(num_points, 1500),
                velocity=velocity,
                duration=10.0
            )
        elif ttype == 'koch_snowflake':
            self.trajectory = FTG.koch_snowflake(
                iterations=4,
                velocity=velocity,
                size=radius * 3.0
            )
        elif ttype == 'dragon_fractal':
            traj = FTG.dragon_curve(
                iterations=12,
                velocity=velocity,
                step_size=6.0  # 间距放大一倍
            )
            # 平移到指定偏移（右移200，下移100）
            self.trajectory = [
                TrajectoryPoint(
                    position=Point2D(p.position.x + 200, p.position.y - 100),
                    velocity=p.velocity,
                    index=p.index
                )
                for p in traj
            ]
        elif ttype == 'hilbert_fractal':
            self.trajectory = FTG.hilbert_curve(
                order=5,
                velocity=velocity
            )
        elif ttype == 'star':
            # 五角星轨迹
            self.trajectory = TrajectoryGenerator.star(
                center=center,
                outer_radius=radius,
                num_points=max(10, num_points // 5),  # 每条边的点数
                velocity=velocity
            )
        elif ttype == 'taiji':
            # 太极图轨迹
            self.trajectory = TrajectoryGenerator.taiji(
                center=center,
                radius=radius,
                num_points=num_points,
                velocity=velocity
            )
        elif ttype == 'zheng':
            # 汉字"正"轨迹（使用固定坐标，忽略参数）
            self.trajectory = TrajectoryGenerator.chinese_zheng(
                center=center,
                size=radius * 2,  # 字体大小等于直径（实际不使用）
                num_points=max(5, num_points // 10),  # 每笔画的点数（实际不使用）
                velocity=velocity
            )
        elif ttype == 'spiralsquare':
            # 正方形螺旋轨迹
            initial_size = radius * 1.5
            angle = 89.0  # 89度产生有趣效果
            num_iterations = min(200, num_points)
            self.trajectory = TrajectoryGenerator.spiral_square(
                center=center,
                initial_size=initial_size,
                angle=angle,
                num_iterations=num_iterations,
                velocity=velocity
            )
        elif ttype == 'spiralarchimedes':
            # 阿基米德螺线轨迹
            start_radius = radius * 0.1
            spacing = radius / 20.0
            rotations = 5
            self.trajectory = TrajectoryGenerator.spiral_archimedes(
                center=center,
                start_radius=start_radius,
                spacing=spacing,
                rotations=rotations,
                num_points=num_points,
                velocity=velocity
            )
        elif ttype == 'spiralrose':
            # 玫瑰曲线轨迹
            petals = 7
            max_radius = radius
            self.trajectory = TrajectoryGenerator.spiral_rose(
                center=center,
                petals=petals,
                max_radius=max_radius,
                num_points=num_points,
                velocity=velocity
            )
        elif ttype == 'ironman':
            # 钢铁侠头盔轨迹
            scale = radius / 200.0  # 根据半径调整缩放
            self.trajectory = TrajectoryGenerator.ironman_helmet(
                center=center,
                scale=scale,
                velocity=velocity
            )
        elif ttype == 'portrait':
            # 人像轨迹：使用像素坐标文件生成，蛇形遍历减少跳点
            # 每次切换 portrait 时刷新缓存（防止上一个文件的缓存残留）
            self._portrait_cache = None
            self.trajectory = self.load_portrait_from_json(
                center=center,
                velocity=velocity
            )
        else:
            # 默认退回李萨如
            self.trajectory = ATG.lissajous(
                num_points=max(num_points, 800),
                velocity=velocity,
                a=3,
                b=4,
                delta=math.pi / 2,
                amplitude=radius * 1.2
            )

        # 更新轨迹线的数据
        traj_x = [p.position.x for p in self.trajectory]
        traj_y = [p.position.y for p in self.trajectory]
        self.trajectory_line.set_data(traj_x, traj_y)

        # 更新起点和终点标记
        if self.trajectory:
            start = self.trajectory[0].position
            end = self.trajectory[-1].position
            self.start_marker.set_data([start.x], [start.y])
            self.end_marker.set_data([end.x], [end.y])

            # 更新共享状态
            self.shared_state.target_position = start
            self.shared_state.total_points = len(self.trajectory)

            # 重置进度（Codex review 建议：避免中途改轨迹导致进度不一致）
            # 注意：在 sim_only 模式下，这是安全的；在 sync 模式下需谨慎
            self.shared_state.point_index = 0

        # 清空历史轨迹（避免显示旧轨迹）
        self.position_history.clear()
        
        # ★ 同步新轨迹到 PLC 客户端 ★
        if self.plc_client and self.plc_client.connected:
            # 1. 暂停当前运动
            self.plc_client.pause()
            
            # 2. 清空旧的轨迹队列
            while not self.plc_client.point_queue.empty():
                try:
                    self.plc_client.point_queue.get_nowait()
                except:
                    break
            
            # 3. 添加新轨迹到队列
            self.plc_client.add_trajectory(self.trajectory)
            
            # 4. 继续运动
            self.plc_client.resume()
            
            self.logger.info(f"★ 新轨迹已同步到 PLC ({len(self.trajectory)} 点)")

        # 请求重绘画布（使用 draw_idle 避免阻塞）
        self.fig.canvas.draw_idle()

        self.logger.info(
            f"轨迹已更新: 类型={self.trajectory_type}, 点数={len(self.trajectory)}"
        )

    def update_animation(self, frame):
        """
        动画更新函数（每帧调用）

        参数:
            frame: 帧编号（matplotlib 自动传入）
        """
        # 仅仿真模式：在未连接 PLC 的情况下按 FPS 推进轨迹
        if self.sim_only and self.sim_running and self.trajectory:
            now = time.time()
            step_time = 1.0 / max(1, self.config.fps)
            if now - self._sim_last_ts >= step_time:
                self._sim_last_ts = now
                self._sim_idx = (self._sim_idx + 1) % len(self.trajectory)
                point = self.trajectory[self._sim_idx]
                self.shared_state.current_position = point.position
                self.shared_state.target_position = point.position
                self.shared_state.point_index = self._sim_idx + 1
                self.shared_state.total_points = len(self.trajectory)
                self.shared_state.velocity = point.velocity
                if self._sim_idx < len(self.trajectory) - 1:
                    self.shared_state.status = RobotStatus.MOVING
                else:
                    self.shared_state.status = RobotStatus.DONE

        # 更新当前位置
        current = self.shared_state.current_position
        self.current_pos_marker.set_center((current.x, current.y))

        # 更新目标位置
        target = self.shared_state.target_position
        self.target_pos_marker.set_center((target.x, target.y))

        # 更新轨迹尾迹
        if self.position_history:
            last_x, last_y = self.position_history[-1]
            gap = ((current.x - last_x) ** 2 + (current.y - last_y) ** 2) ** 0.5
            if self.gap_jump_enabled and gap > self.gap_threshold:
                # 大跳跃时断开尾迹，避免连线
                self.position_history.clear()
        self.position_history.append((current.x, current.y))
        if len(self.position_history) > 1:
            trail_x, trail_y = zip(*self.position_history)
            self.trail_line.set_data(trail_x, trail_y)

        # 更新状态文本
        status_str = (
            f"Status: {self.shared_state.status.value}\n"
            f"Current: ({current.x:.1f}, {current.y:.1f})\n"
            f"Target: ({target.x:.1f}, {target.y:.1f})\n"
            f"Velocity: {self.shared_state.velocity:.1f} mm/s\n"
            f"Progress: {self.shared_state.point_index}/{self.shared_state.total_points} "
            f"({self.shared_state.progress_percent():.1f}%)\n"
            f"PLC: Busy={self.shared_state.plc_busy}, Done={self.shared_state.plc_done}\n"
            f"轨迹: {self.trajectory_type.capitalize()}\n"
            f"切换: Tab/→/↓ 或 1-9/0/-/="
        )

        if self.shared_state.error_message:
            status_str += f"\nError: {self.shared_state.error_message}"

        self.status_text.set_text(status_str)

        # 返回需要更新的对象（包括轨迹线，以便在切换时能看到变化）
        return self.current_pos_marker, self.target_pos_marker, self.trail_line, self.status_text, self.trajectory_line, self.start_marker, self.end_marker

    def switch_trajectory_type(self, new_type: str):
        """
        切换轨迹类型（内部方法）
        
        参数:
            new_type: 新的轨迹类型名称（小写）
        """
        if new_type in self.trajectory_types_list:
            self.trajectory_type = new_type
            self.trajectory_type_index = self.trajectory_types_list.index(new_type)
            
            # 更新单选按钮选中状态
            if self.radio_buttons:
                try:
                    # 找到对应的标签（首字母大写）
                    labels = [label.get_text() for label in self.radio_buttons.labels]
                    for i, label in enumerate(labels):
                        if label.lower() == new_type:
                            self.radio_buttons.set_active(i)
                            break
                except:
                    pass
            
            # 更新轨迹
            self.update_trajectory()
            self.fig.canvas.draw()
            
            # 显示提示信息
            type_name = new_type.capitalize()
            self.logger.info(f"[切换] 轨迹类型: {type_name}")

    def on_key(self, event):
        """
        键盘事件处理
        
        快捷键：
        - Q: 退出程序
        - Space: 暂停/继续 PLC 运动
        - R: 复位（清空队列，重置状态）
        - S: 停止 PLC 线程
        - Tab / →: 切换到下一个轨迹类型
        - Shift+Tab / ←: 切换到上一个轨迹类型
        - 1-9, 0, -, =: 直接选择轨迹类型
          1=Circle, 2=Star, 3=Taiji, 4=Zheng, 5=Rectangle,
          6=Dragon, 7=Hilbert, 8=SpiralSquare, 9=SpiralArchimedes,
          0=SpiralRose, -=Ironman, ==Portrait
        """
        if event.key == 'q':
            self.logger.info("User pressed Q, exiting...")
            if self.plc_client:
                self.plc_client.stop()
                self.plc_client.disconnect()
            plt.close(self.fig)

        elif event.key == ' ':
            # 暂停/继续
            if not self.plc_client:
                return  # 仅仿真模式，直接忽略（使用 Start 按钮）
            if self.plc_client.is_paused():
                self.plc_client.resume()
                self.logger.info("[Space] PLC 继续运动")
            else:
                self.plc_client.pause()
                self.logger.info("[Space] PLC 暂停运动")

        elif event.key == 'r':
            # 复位
            if not self.plc_client:
                return  # 仅仿真模式，直接忽略（使用 Start 重置起点）
            self.plc_client.reset()
            self.logger.info("[R] PLC 已复位")
            # 清空显示的历史轨迹
            self.position_history.clear()

        elif event.key == 's':
            # 停止 PLC 线程
            if not self.plc_client:
                return  # 仅仿真模式，直接忽略
            self.plc_client.pause()  # 先暂停运动
            self.plc_client.stop()   # 再停止线程
            self.logger.info("[S] PLC 已停止")
        
        elif event.key == 'tab':
            # Tab 键：切换到下一个轨迹类型（如果按住 Shift，则反向）
            # 检查是否有 Shift 修饰键
            if hasattr(event, 'key') and hasattr(event, 'modifiers'):
                # 某些 matplotlib 版本可能支持 modifiers
                if hasattr(event.modifiers, '__contains__') and 'shift' in str(event.modifiers).lower():
                    # Shift+Tab：上一个
                    self.trajectory_type_index = (self.trajectory_type_index - 1) % len(self.trajectory_types_list)
                else:
                    # Tab：下一个
                    self.trajectory_type_index = (self.trajectory_type_index + 1) % len(self.trajectory_types_list)
            else:
                # 默认：下一个
                self.trajectory_type_index = (self.trajectory_type_index + 1) % len(self.trajectory_types_list)
            new_type = self.trajectory_types_list[self.trajectory_type_index]
            self.switch_trajectory_type(new_type)
        
        elif event.key in ['right', 'rightarrow', 'down', 'downarrow']:
            # 右/下方向键：切换到下一个轨迹类型
            self.trajectory_type_index = (self.trajectory_type_index + 1) % len(self.trajectory_types_list)
            new_type = self.trajectory_types_list[self.trajectory_type_index]
            self.switch_trajectory_type(new_type)
        
        elif event.key in ['left', 'leftarrow', 'up', 'uparrow']:
            # 左/上方向键：切换到上一个轨迹类型
            self.trajectory_type_index = (self.trajectory_type_index - 1) % len(self.trajectory_types_list)
            new_type = self.trajectory_types_list[self.trajectory_type_index]
            self.switch_trajectory_type(new_type)
        
        elif event.key in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=']:
            # 数字键直接选择轨迹类型
            key_map = {
                '1': 'circle',
                '2': 'star',
                '3': 'taiji',
                '4': 'zheng',
                '5': 'rectangle',
                '6': 'dragon',
                '7': 'hilbert',
                '8': 'spiralsquare',
                '9': 'spiralarchimedes',
                '0': 'spiralrose',
                '-': 'ironman',
                '=': 'portrait'
            }
            if event.key in key_map:
                new_type = key_map[event.key]
                self.switch_trajectory_type(new_type)

    def run(self):
        """启动动画"""
        # 绑定键盘事件
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

        # 创建动画（interval = 1000/fps ms）
        # 注意：blit=False 以确保轨迹切换时能正确更新显示
        interval_ms = 1000 / self.config.fps
        self.anim = animation.FuncAnimation(
            self.fig,
            self.update_animation,
            interval=interval_ms,
            blit=False,  # 禁用 blit 以支持轨迹切换
            cache_frame_data=False
        )

        self.logger.info(f"Simulation started (FPS={self.config.fps})")
        self.logger.info("快捷键: Q=退出, Space=暂停/继续, R=复位, S=停止")
        self.logger.info("轨迹切换: Tab/→/↓=下一个, ←/↑=上一个, 1-9/0/-/==直接选择")

        # 显示窗口（阻塞主线程）
        plt.show()

    def close(self):
        """关闭动画窗口"""
        if self.anim:
            self.anim.event_source.stop()
        plt.close(self.fig)
        self.logger.info("Simulation window closed")
