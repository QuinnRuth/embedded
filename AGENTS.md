# AGENTS.md（Embedded 工作区）

本文件为所有 AI Agent 提供该仓库的长期上下文入口，帮助你快速理解项目目标、目录结构与默认工作流。本文自包含核心配置与命令，不依赖其他文件。

## 项目概览

这是一个通用嵌入式开发工作区，核心理念是：编辑层 + 构建层 + 调试层保持稳定，只切换 toolchain 与 board 配置来支持不同芯片。主要用于 STM32 学习、课程代码迁移与跨平台（Linux/WSL2/macOS）开发。

## 关键目录与入口

```
embedded/
├── stm32/                     # STM32 项目区（主力）
├── esp32/                     # ESP32 项目区（待扩展）
├── nrf52/                     # NRF52 项目区（待扩展）
├── plc/                       # PLC 相关项目
├── README.md                  # 工作区完整说明
├── CLAUDE.md                  # 具体构建/烧录/常见问题
└── WSL2_STLink_USBIPD_OpenOCD.md  # WSL2 + ST-Link 调试指南
```

STM32 的核心模板在 `stm32/learning/vscode_cmake_template/`，其中包含 CMake 通用配置、板卡配置、驱动库与 VS Code 调试设置。

## STM32 默认板卡与外设（从课程代码推断）

- 默认板卡：stm32f103c8t6（BluePill / StdPeriph / CMake 工程体系）
- 课程里已有可复用的外设与典型接线（从 lesson 代码/文档推断）：
  - OLED：PB8(SCL) / PB9(SDA)（软件 I2C 4-pin OLED）
  - USART1：PA9(TX) / PA10(RX)（常用 9600）
  - MPU6050：PB10/PB11（I2C2 硬件；软件 I2C 也常用这对）
  - W25Q64：SPI1 常见引脚 PA5/PA6/PA7 + PA4(CS)（课程里是软件 SPI）
  - 蜂鸣器：PB12（低电平响）
  - 对射红外计次：PB14（EXTI）
  - 编码器：课程里有两种实现：PB0/PB1（EXTI 软解码）或 PA6/PA7（TIM3 编码器接口）

## 目录导航建议

- 想改主逻辑：优先从 `stm32/.../src/` 入手。
- 想改板卡：看 `stm32/.../cmake/boards/` 与 `stm32/.../boards/<board>/`。
- 想查调试与烧录：参考本文的“构建与调试”与“常见问题”。
- 想了解整体设计理念：参阅 `README.md`（可选）。

## 标准工作流（默认）

1. 先确认目标（芯片/板卡/课程/移植/调试场景）。
2. 快速定位模板与板卡配置位置。
3. 小步修改，优先遵循现有代码风格与目录结构。
4. 变更后做最小验证（构建/烧录/串口输出等，视任务而定）。
5. 如果是架构级改动，先提出澄清问题再动手。

## 构建与调试（入口）

### 环境激活

```bash
embenv    # 激活环境并 cd 到此目录
```

### 构建

```bash
mkdir build && cd build
cmake ..
make -j$(nproc)
```

### 烧录（OpenOCD）

```bash
openocd -f interface/stlink-v2.cfg -f target/stm32f1x.cfg \
    -c "program build/project.hex verify reset exit"
```

### 默认工具链

- 编译器：ARM GCC (arm-none-eabi-gcc) 10.3.1
- 构建系统：CMake 3.22+ / Ninja 1.10+
- 调试器：GDB (gdb-multiarch) 12.1
- 烧录工具：OpenOCD 0.11.0
- 编辑器：VS Code + C/C++ + CMake Tools + Cortex-Debug

## 变更原则

- 优先保持工程结构稳定，避免无关目录重构。
- 代码改动以可读性与可追溯性为先。
- 工具链与板卡配置尽量复用模板，不轻易自创新套路。
- 如果需要新增芯片/板卡，遵循 README 的“添加新芯片支持”流程。

## 质量与验证

- 常规改动：至少能成功构建目标项目。
- 驱动/板卡相关变更：建议包含烧录或调试验证步骤。
- 无法验证时，明确说明原因与风险点。

## 常见问题

- OpenOCD 连接失败：在 WSL2 场景下通常与 USBIPD 绑定/权限有关，可查 `WSL2_STLink_USBIPD_OpenOCD.md`（可选）。
- 烧录后无反应：检查 BOOT0 跳线（应接 GND）。
- 串口无输出：确认波特率与引脚配置匹配。

## 课程实现约定（实践经验）

- OLED 自动恢复：为应对“供电切换/电机舵机干扰导致 OLED 黑屏”，应用层可每约 5 秒尝试重新 `OLED_Init()` 一次，实现无需重启的自恢复（示例：`stm32/learning/lesson_6-4`）。
- WSL2 USB 分工（推荐）：CH340 串口模块留在 Windows（Serial Studio/串口助手直接用 `COMx`），只把 ST-Link 通过 `usbipd attach --wsl` 转发进 WSL2 用于 OpenOCD 烧录；避免把 CH340 attach 进 WSL 导致 Windows 侧 COM 口不可用/混乱。
- 视频录制建议：最好每隔五秒重启一次（因为会有断电插充电宝的操作）。
## 参考文档（可选）

- `README.md`：完整工作流、工具链与目录结构
- `WSL2_STLink_USBIPD_OpenOCD.md`：WSL2 + ST-Link 调试指南
- `PROJECT_IDEAS.md`：项目创意与方向
- `IFLOW.MD` / `GEMINI.md`：知识管理与 AI 辅助说明

## 使用提示

- 你可以把任务拆分为“定位模板/修改代码/验证/记录”四步。
- 若任务涉及 PLC 项目或 SCL/LAD 工作流，请先查看 `plc/` 下的 AGENTS/CLAUDE 指引。
