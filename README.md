# Embedded Development Workspace

> **"VS Code 打天下"** - 通用嵌入式开发工作流
>
> 核心理念：编辑层 + 构建层 + 调试界面 **不变**，只换 **"toolchain 文件 + board 配置"**

---

## 目录

- [完整技术栈](#完整技术栈)
- [适用范围](#适用范围)
- [核心设计：三层架构](#核心设计三层架构)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [日常开发流程](#日常开发流程)
- [从课程代码迁移指南](#从课程代码迁移指南)
- [VS Code 操作手册](#vs-code-操作手册)
- [配置文件详解](#配置文件详解)
- [添加新芯片支持](#添加新芯片支持)
- [常见问题](#常见问题)
- [与 Keil 对比](#与-keil-对比)

---

## 完整技术栈

### 核心工具链

| 组件 | 工具 | 版本 | 用途 |
|------|------|------|------|
| **编译器** | ARM GCC (arm-none-eabi-gcc) | 10.3.1 | C/C++/ASM 编译 |
| **构建系统** | CMake + Ninja | 3.22 / 1.10 | 跨平台构建管理 |
| **调试器** | GDB (gdb-multiarch) | 12.1 | 源码级调试 |
| **烧录工具** | OpenOCD | 0.11.0 | 支持 ST-Link/J-Link/CMSIS-DAP |
| **编辑器** | VS Code | Latest | 统一开发环境 |

### VS Code 插件栈

| 插件 | ID | 功能 | 必装 |
|------|----|------|------|
| C/C++ | `ms-vscode.cpptools` | IntelliSense/跳转/补全 | ✅ |
| CMake Tools | `ms-vscode.cmake-tools` | CMake 集成 | ✅ |
| Cortex-Debug | `marus25.cortex-debug` | ARM Cortex 调试 | ✅ |
| CMake | `twxs.cmake` | CMake 语法高亮 | 推荐 |
| ARM Assembly | `dan-c-underwood.arm` | 汇编高亮 | 推荐 |
| LinkerScript | `zixuanwang.linkerscript` | 链接脚本高亮 | 推荐 |
| Error Lens | `usernamehw.errorlens` | 行内错误显示 | 推荐 |
| GitLens | `eamodio.gitlens` | Git 增强 | 推荐 |

### 固件库支持

| 芯片系列 | 库类型 | 版本 | 状态 |
|----------|--------|------|------|
| STM32F1xx | StdPeriph (标准外设库) | V3.5.0 | ✅ 已配置 |
| STM32F1xx | HAL/LL | 待添加 | 📋 计划中 |
| STM32F4xx | HAL/LL | 待添加 | 📋 计划中 |
| GD32F1xx | 标准外设库 | 待添加 | 📋 计划中 |
| NRF52xxx | nRF5 SDK | 待添加 | 📋 计划中 |

---

## 适用范围

### ✅ 适合使用本工作流的场景

| 场景 | 说明 |
|------|------|
| **学习 STM32/ARM** | 配合江科大、正点原子、野火等课程 |
| **课程代码移植** | 将 Keil 工程迁移到 VS Code |
| **Linux/Mac 开发** | 不依赖 Windows 专有工具 |
| **多芯片项目** | 统一工作流，换芯片只改配置 |
| **版本控制友好** | 纯文本配置，适合 Git |
| **团队协作** | 跨平台，配置可共享 |
| **自动化构建** | CI/CD 友好 |

### ⚠️ 可能不太适合的场景

| 场景 | 原因 | 替代方案 |
|------|------|----------|
| **初学者第一次接触单片机** | 配置门槛稍高 | 先用 Keil 入门，熟悉后迁移 |
| **需要图形化配置引脚/时钟** | 本方案是纯代码 | 配合 STM32CubeMX 生成初始代码 |
| **公司强制要求 Keil** | 商业授权问题 | 遵循公司规范 |
| **特殊芯片无 GCC 支持** | 部分小众芯片只有专用编译器 | 使用厂商工具 |

### 🎯 最佳实践场景

```
推荐路径：
1. Keil 入门 → 理解基本概念
2. 学习 CMake 基础 → 理解构建系统
3. 迁移到本工作流 → 享受现代开发体验
4. 一套配置打天下 → STM32/GD32/NRF 通用
```

---

## 核心设计：三层架构

```
┌─────────────────────────────────────────────────────────────┐
│                    编辑层 (永不改变)                          │
│  VS Code + 通用插件: 补全、跳转、格式化、代码风格               │
│  ✅ 一次配置，所有项目通用                                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    构建层 (高度统一)                          │
│  CMake + Ninja                                              │
│  ✅ CMakeLists.txt 通用                                      │
│  ✅ cmake/toolchains/arm-gcc.cmake 通用                      │
│  ⚙️ cmake/boards/<board>.cmake 按芯片配置                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    调试层 (可插拔)                            │
│  GDB + Cortex-Debug                                         │
│  ⚙️ boards/<board>/openocd.cfg 按调试器配置                   │
│  ⚙️ .vscode/launch.json 按项目配置                           │
└─────────────────────────────────────────────────────────────┘
```

### 换芯片/项目时的改动量

| 场景 | 需要改的文件 | 工作量 |
|------|-------------|--------|
| **同芯片新项目** | 复制模板，改 `src/main.c` | 极小 |
| **同系列换型号** (F103C8→F103RB) | 改链接脚本内存大小 | 很小 |
| **换芯片系列** (F1→F4) | 新增 board 配置 + 驱动库 | 中等 |
| **换芯片厂商** (STM32→GD32) | 新增 board + 驱动库 | 中等 |

---

## 项目结构

```
~/dev/embedded/                    # 嵌入式工作区根目录
├── .embedded_env                  # 环境变量脚本
├── README.md                      # 本文档
│
├── stm32/                         # STM32 项目区
│   └── learning/
│       ├── vscode_cmake_template/ # ★ 通用 CMake 模板 (核心)
│       │   ├── CMakeLists.txt     # 顶层构建配置
│       │   ├── .gitignore         # Git 忽略规则
│       │   │
│       │   ├── cmake/             # CMake 配置目录
│       │   │   ├── toolchains/
│       │   │   │   └── arm-gcc.cmake    # ARM GCC 工具链 (通用)
│       │   │   └── boards/
│       │   │       └── stm32f103c8t6.cmake  # 板卡配置
│       │   │
│       │   ├── boards/            # 板卡资源目录
│       │   │   └── stm32f103c8t6/
│       │   │       ├── openocd.cfg          # OpenOCD 配置
│       │   │       ├── STM32F103C8Tx_FLASH.ld  # 链接脚本
│       │   │       └── (启动文件在 drivers 中)
│       │   │
│       │   ├── drivers/           # 外设库
│       │   │   ├── CMSIS/         # ARM CMSIS 核心
│       │   │   └── STM32F10x_StdPeriph_Driver/  # 标准外设库
│       │   │
│       │   ├── include/           # 项目头文件
│       │   │   └── stm32f10x_conf.h  # 外设库配置
│       │   │
│       │   ├── src/               # 源代码
│       │   │   └── main.c
│       │   │
│       │   └── .vscode/           # VS Code 配置
│       │       ├── settings.json  # 编辑器设置
│       │       ├── tasks.json     # 构建任务
│       │       └── launch.json    # 调试配置
│       │
│       ├── 课件/                  # 课程资料
│       │   └── 固件库/            # STM32 官方库
│       │
│       └── learning/              # 其他学习项目...
│
├── esp32/                         # ESP32 项目区 (待扩展)
├── nrf52/                         # NRF52 项目区 (待扩展)
└── plc/                           # PLC 相关项目
```

---

## 快速开始

### 1. 环境安装 (Ubuntu/WSL2)

```bash
# 安装全部工具
sudo apt update
sudo apt install -y gcc-arm-none-eabi gdb-multiarch cmake ninja-build openocd

# 验证安装
arm-none-eabi-gcc --version   # 应显示 10.3.1
cmake --version               # 应显示 3.22+
ninja --version               # 应显示 1.10+
openocd --version             # 应显示 0.11+
```

### 2. VS Code 插件安装

```bash
# 一键安装核心插件
code --install-extension ms-vscode.cpptools
code --install-extension ms-vscode.cmake-tools
code --install-extension marus25.cortex-debug

# 推荐插件
code --install-extension twxs.cmake
code --install-extension dan-c-underwood.arm
code --install-extension usernamehw.errorlens
```

### 3. 创建新项目

```bash
# 进入嵌入式环境
source ~/dev/embenv

# 复制模板
cp -r ~/dev/embedded/stm32/learning/vscode_cmake_template ~/dev/embedded/stm32/my_project

# 用 VS Code 打开
code ~/dev/embedded/stm32/my_project
```

### 4. 编译和烧录

```bash
cd ~/dev/embedded/stm32/my_project

# 配置 (首次或改了 CMake 配置后)
cmake -S . -B build \
    -DCMAKE_TOOLCHAIN_FILE=cmake/toolchains/arm-gcc.cmake \
    -DBOARD=stm32f103c8t6 \
    -G Ninja

# 编译
cmake --build build

# 烧录 (WSL 需要 sudo)
echo "zxcvbnm" | sudo -S openocd -f boards/stm32f103c8t6/openocd.cfg \
    -c "program build/firmware.elf verify reset exit"
```

### 系统密码
- **sudo 密码**: `zxcvbnm`

---

## 日常开发流程

### 命令行流程

```bash
# 1. 进入环境
source ~/dev/embenv
cd ~/dev/embedded/stm32/my_project

# 2. 编辑代码
code .   # 或 vim src/main.c

# 3. 编译
cmake --build build

# 4. 烧录
cmake --build build --target flash
# 或手动 (WSL 需要 sudo):
echo "zxcvbnm" | sudo -S openocd -f boards/stm32f103c8t6/openocd.cfg \
    -c "program build/firmware.elf verify reset exit"

# 5. 调试 (在 VS Code 中按 F5)
```

### VS Code 快捷操作

| 操作 | 快捷键 | 说明 |
|------|--------|------|
| 编译 | `Ctrl+Shift+B` | 运行默认构建任务 |
| 调试 | `F5` | 启动调试会话 |
| CMake 配置 | `Ctrl+Shift+P` → "CMake: Configure" | 重新配置 |
| 清理 | `Ctrl+Shift+P` → "CMake: Clean" | 清理构建 |
| 终端 | `` Ctrl+` `` | 打开集成终端 |

---

## 从课程代码迁移指南

### 从 Keil 工程迁移

以江科大 STM32 入门教程为例，将 Keil 工程迁移到本工作流：

#### 步骤 1: 复制模板

```bash
cp -r ~/dev/embedded/stm32/learning/vscode_cmake_template \
      ~/dev/embedded/stm32/learning/3-1_LED闪烁
```

#### 步骤 2: 复制源文件

从 Keil 工程复制这些文件到 `src/` 目录：
- `main.c`
- 其他 `.c` 文件 (如 `led.c`, `delay.c`)
- 对应的 `.h` 文件放到 `include/`

#### 步骤 3: 修改 CMakeLists.txt

```cmake
# 在 add_executable 中添加你的源文件
add_executable(firmware.elf
    src/main.c
    src/led.c           # 添加
    src/delay.c         # 添加
    ${STARTUP}
)

# 添加头文件目录
target_include_directories(firmware.elf PRIVATE
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/src      # 如果 .h 和 .c 在一起
)
```

#### 步骤 4: 编译测试

```bash
cd ~/dev/embedded/stm32/learning/3-1_LED闪烁
rm -rf build
cmake -S . -B build \
    -DCMAKE_TOOLCHAIN_FILE=cmake/toolchains/arm-gcc.cmake \
    -DBOARD=stm32f103c8t6 \
    -G Ninja
cmake --build build
```

### Keil vs VS Code 对照表

| Keil 操作 | VS Code 等价操作 |
|-----------|------------------|
| 新建工程 | 复制模板目录 |
| 添加源文件 | 编辑 `CMakeLists.txt` |
| 选择芯片 | 修改 `-DBOARD=xxx` |
| 设置编译选项 | 编辑 `cmake/boards/xxx.cmake` |
| 编译 (F7) | `Ctrl+Shift+B` 或 `cmake --build build` |
| 调试 (Ctrl+F5) | `F5` |
| 下载 | `cmake --build build --target flash` |

---

## VS Code 操作手册

### 首次打开项目

1. **打开文件夹**: `File` → `Open Folder` → 选择项目目录
2. **等待 CMake 配置**: 右下角会显示 CMake 正在配置
3. **选择工具链**: 如果提示选择 Kit，选择 `arm-none-eabi-gcc`

### 编译项目

**方法 1: 快捷键**
- `Ctrl+Shift+B` → 选择 "build-firmware"

**方法 2: CMake 面板**
- 左侧边栏点击 CMake 图标
- 点击 "Build" 按钮

**方法 3: 命令面板**
- `Ctrl+Shift+P` → 输入 "CMake: Build"

### 调试项目

1. **连接硬件**: 将 ST-Link 连接到电脑和开发板
2. **按 F5**: 自动编译并启动调试
3. **调试控制**:
   - `F5` - 继续运行
   - `F10` - 单步跳过
   - `F11` - 单步进入
   - `Shift+F11` - 单步跳出
   - `Shift+F5` - 停止调试

### 设置断点

- 点击代码行号左侧空白处
- 或光标在行上按 `F9`

### 查看变量

- **监视窗口**: 调试时左侧 "WATCH" 面板，添加变量名
- **悬停查看**: 调试时鼠标悬停在变量上
- **寄存器查看**: "CORTEX PERIPHERALS" 面板查看外设寄存器

### 常用命令面板操作

按 `Ctrl+Shift+P` 打开命令面板，常用命令：

| 命令 | 功能 |
|------|------|
| `CMake: Configure` | 重新配置 CMake |
| `CMake: Build` | 编译项目 |
| `CMake: Clean` | 清理构建 |
| `CMake: Delete Cache and Reconfigure` | 完全重新配置 |
| `C/C++: Edit Configurations` | 编辑 IntelliSense 配置 |
| `Tasks: Run Task` | 运行自定义任务 |

---

## 配置文件详解

### CMakeLists.txt (顶层)

```cmake
cmake_minimum_required(VERSION 3.20)
project(embedded_firmware C CXX ASM)

# 必须指定工具链和板卡
# cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=... -DBOARD=...

# 加载板卡配置
include(cmake/boards/${BOARD}.cmake)

# 编译目标
add_executable(firmware.elf
    src/main.c
    # 添加更多源文件...
    ${STARTUP}
)

# 链接库
target_link_libraries(firmware.elf PRIVATE cmsis hal)

# 生成 bin/hex
add_custom_command(TARGET firmware.elf POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O binary ... firmware.bin
    COMMAND ${CMAKE_OBJCOPY} -O ihex ... firmware.hex
)
```

### arm-gcc.cmake (工具链)

定义编译器和通用编译选项，适用于所有 ARM Cortex-M 芯片。

**关键配置**:
- 编译器路径
- CPU 架构参数 (`-mcpu`, `-mthumb`)
- 优化和调试选项
- 链接选项 (`--specs=nano.specs`)

### stm32f103c8t6.cmake (板卡配置)

定义特定芯片的参数：
- CPU 核心 (`cortex-m3`)
- 宏定义 (`STM32F10X_MD`, `HSE_VALUE`)
- 链接脚本路径
- 启动文件路径
- CMSIS/HAL 库配置

### launch.json (调试配置)

```json
{
    "name": "Debug Firmware (OpenOCD)",
    "type": "cortex-debug",
    "request": "launch",
    "servertype": "openocd",
    "executable": "${workspaceFolder}/build/firmware.elf",
    "configFiles": ["${workspaceFolder}/boards/stm32f103c8t6/openocd.cfg"],
    "runToMain": true
}
```

---

## 添加新芯片支持

### 示例: 添加 STM32F103RCT6 (大容量)

STM32F103RC 与 STM32F103C8 的区别：
- Flash: 256KB (vs 64KB)
- RAM: 48KB (vs 20KB)
- 属于 High Density (HD) 而非 Medium Density (MD)

#### 1. 创建板卡配置

**文件**: `cmake/boards/stm32f103rct6.cmake`

```cmake
# STM32F103RCT6 (High Density, 256KB Flash, 48KB RAM)

set(ARM_CPU "cortex-m3" CACHE STRING "" FORCE)
set(ARM_FPU "" CACHE STRING "" FORCE)
set(ARM_FLOAT_ABI "soft" CACHE STRING "" FORCE)

set(BOARD_DEFINES
    STM32F10X_HD            # High Density (改这里!)
    USE_STDPERIPH_DRIVER
    HSE_VALUE=8000000
)

set(LINKER_SCRIPT ${CMAKE_SOURCE_DIR}/boards/stm32f103rct6/STM32F103RCTx_FLASH.ld)
set(STARTUP ${CMAKE_SOURCE_DIR}/drivers/CMSIS/CM3/DeviceSupport/ST/STM32F10x/startup/gcc_ride7/startup_stm32f10x_hd.s)  # 改这里!

# ... 其余配置与 stm32f103c8t6.cmake 相同
```

#### 2. 创建链接脚本

**文件**: `boards/stm32f103rct6/STM32F103RCTx_FLASH.ld`

```ld
_estack = 0x2000C000;    /* 48KB RAM */

MEMORY
{
  FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 256K  /* 改这里 */
  RAM   (rwx) : ORIGIN = 0x20000000, LENGTH = 48K   /* 改这里 */
}
/* 其余与 F103C8 相同 */
```

#### 3. 创建 OpenOCD 配置

**文件**: `boards/stm32f103rct6/openocd.cfg`

```
interface stlink
transport select hla_swd
source [find target/stm32f1x.cfg]
# F103RC 与 F103C8 使用相同的配置
```

#### 4. 使用新板卡

```bash
cmake -S . -B build \
    -DCMAKE_TOOLCHAIN_FILE=cmake/toolchains/arm-gcc.cmake \
    -DBOARD=stm32f103rct6 \
    -G Ninja
```

---

## 常见问题

### 编译问题

**Q: `arm-none-eabi-gcc: command not found`**
```bash
sudo apt install gcc-arm-none-eabi
# 或检查 PATH
which arm-none-eabi-gcc
```

**Q: `undefined reference to '_sbrk'`**
```bash
# 确保链接选项包含:
--specs=nosys.specs --specs=nano.specs
```

**Q: `core_cm3.c` 编译错误 (strexb/strexh)**
```
这是 CMSIS V3.5.0 与新版 GCC 的兼容性问题。
解决方案：不编译 core_cm3.c，只用头文件中的内联函数。
本模板已修复此问题。
```

### 调试问题

**Q: OpenOCD 无法连接**
```bash
# 检查 USB 权限
sudo usermod -aG plugdev $USER
# 重新登录

# 安装 udev 规则
sudo cp /usr/share/openocd/contrib/60-openocd.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
```

**Q: WSL2 无法识别 ST-Link**
```powershell
# Windows PowerShell (管理员)
winget install usbipd
usbipd list                    # 找到 ST-Link 的 BUSID
usbipd bind --busid <BUSID>
usbipd attach --wsl --busid <BUSID>
```

### VS Code 问题

**Q: IntelliSense 报错但编译正常**
```
Ctrl+Shift+P → "C/C++: Edit Configurations"
确保 compilerPath 指向 arm-none-eabi-gcc
或让 CMake Tools 提供配置:
"C_Cpp.default.configurationProvider": "ms-vscode.cmake-tools"
```

**Q: 调试时变量显示 `<optimized out>`**
```
在 CMake 配置时使用 Debug 模式:
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug ...
这会使用 -Og 优化级别，保留调试信息。
```

---

## 与 Keil 对比

| 方面 | Keil | VS Code + CMake |
|------|------|-----------------|
| **平台** | Windows 专有 | 跨平台 (Win/Linux/Mac) |
| **授权** | 商业授权 (免费版 32KB 限制) | 完全免费开源 |
| **配置方式** | GUI 图形界面 | 文本配置文件 |
| **版本控制** | 二进制工程文件 | 纯文本，Git 友好 |
| **编译器** | ARMCC/ARM Compiler | GCC (业界标准) |
| **调试器** | 内置 | OpenOCD/J-Link GDB Server |
| **代码补全** | 一般 | 优秀 (clangd/IntelliSense) |
| **扩展性** | 有限 | 无限 (VS Code 插件生态) |
| **学习曲线** | 较平缓 | 稍陡峭 (需理解 CMake) |
| **多芯片支持** | 需要分别配置 | 统一工作流 |
| **CI/CD** | 不友好 | 完美支持 |

### 什么时候用 Keil？

- 初学者第一次接触单片机
- 公司已有成熟的 Keil 工程
- 需要使用 ARMCC 特有功能
- 追求最简单的上手体验

### 什么时候用 VS Code + CMake？

- 追求现代化开发体验
- 需要跨平台开发
- 多人协作项目
- 需要 CI/CD 自动化
- 同时开发多个芯片平台
- 已经熟悉 VS Code

---

## 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2025-12-07 | v0.1 | 初始三层架构设计 |
| 2025-12-24 | v1.0 | 完整工具链配置，驱动库集成，编译测试通过 |

---

## 参考资源

- [ARM GCC 下载](https://developer.arm.com/downloads/-/gnu-rm)
- [OpenOCD 文档](https://openocd.org/doc/html/index.html)
- [Cortex-Debug 插件](https://marketplace.visualstudio.com/items?itemName=marus25.cortex-debug)
- [STM32 标准外设库](https://www.st.com/en/embedded-software/stm32-standard-peripheral-libraries.html)
- [江科大 STM32 入门教程](https://www.bilibili.com/video/BV1th411z7sn)

---

*Last Updated: 2025-12-24*
*Author: muqiao*
