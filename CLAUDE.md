# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

This is an **embedded development workspace** implementing a universal VS Code + CMake workflow for ARM Cortex-M microcontrollers (STM32/GD32/NRF etc).

**Key Principle**: Three-layer architecture - only swap toolchain/board configs when changing chips, keep everything else the same.

```
┌─────────────────────────────────────────────────────┐
│    Edit Layer (unchanged)                          │
│    VS Code + plugins: code completion, navigation        │
└─────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│    Build Layer (unified)                          │
│    CMake + Ninja, swap toolchain/board for chips   │
└─────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│    Debug Layer (pluggable)                        │
│    GDB + Cortex-Debug + OpenOCD/JLink          │
└─────────────────────────────────────────────────────┘
```

---

## Common Commands

### Build Commands

```bash
# From project root (e.g., ~/dev/embedded/stm32/my_project)

# Configure (first time or after CMake changes)
cmake -S . -B build \
    -DCMAKE_TOOLCHAIN_FILE=cmake/toolchains/arm-gcc.cmake \
    -DBOARD=stm32f103c8t6 \
    -G Ninja

# Build (incremental)
cmake --build build

# Clean build artifacts
rm -rf build
# or: cmake --build build --target clean
```

### Flash/Debug Commands

```bash
# Flash with OpenOCD (ST-Link)
openocd -f boards/stm32f103c8t6/openocd.cfg \
    -c "program build/firmware.elf verify reset exit"

# Or use CMake target (if defined)
cmake --build build --target flash

# Debug with GDB
arm-none-eabi-gdb build/firmware.elf
# Or use VS Code F5 (uses Cortex-Debug + OpenOCD)
```

### Environment Setup

```bash
# Enter embedded environment (loads ARM toolchain to PATH)
source ~/dev/embenv

# Quick verification
arm-none-eabi-gcc --version
cmake --version
openocd --version
```

---

## Architecture & Structure

### Three-Layer Separation

| Layer | Scope | What Changes Per Chip |
|--------|--------|---------------------|
| **Edit** | VS Code, plugins, settings.json | Nothing |
| **Build** | CMakeLists.txt, arm-gcc.cmake | Only board configs |
| **Debug** | launch.json, openocd.cfg | Only board configs |

### Directory Structure

```
template_root/
├── CMakeLists.txt              # Top-level build (unchanged per chip)
├── cmake/
│   ├── toolchains/
│   │   └── arm-gcc.cmake    # Universal toolchain (unchanged)
│   └── boards/
│       └── *.cmake             # Per-chip configs (ADD for new chips)
├── boards/
│   └── <board>/               # Per-board: linker, openocd.cfg
├── drivers/                   # STM32 HAL/StdPeriph libraries
├── include/                   # Project headers
├── src/                       # Application code
└── .vscode/
    ├── settings.json           # Editor config (mostly static)
    ├── tasks.json             # Build tasks
    └── launch.json            # Debug configs (per project)
```

### Key Design Decisions

1. **Toolchain is generic**: `cmake/toolchains/arm-gcc.cmake` works for any ARM Cortex-M chip
2. **Board configs isolate chip differences**: `cmake/boards/<board>.cmake` defines CPU, FPU, defines, library paths
3. **StdPeriph V3.5.0 compatibility**: Template excludes `core_cm3.c` from build due to GCC 10.x compatibility
4. **Linker script**: `_estack` must be defined (fixed in template for F103C8T6)

---

## Adding New Chip Support

To add a new STM32F1xx variant (e.g., F103RCT6 - High Density):

1. **Create board config**: `cmake/boards/stm32f103rct6.cmake`
   - Change `STM32F10X_MD` → `STM32F10X_HD`
   - Change startup to `startup_stm32f10x_hd.s`
   - Update RAM/FLASH sizes in linker script

2. **Create board resources**: `boards/stm32f103rct6/` directory
   - Copy/linker script, adjust MEMORY sizes
   - Create/open copy OpenOCD config

3. **No changes needed to**: `CMakeLists.txt`, `arm-gcc.cmake`, `vscode/settings.json`

---

## Important Constraints

### CMSIS Compatibility Issue

**Problem**: STM32 StdPeriph V3.5.0's `core_cm3.c` contains inline assembly incompatible with GCC 10.x.

**Solution**: Template excludes `core_cm3.c` from build - uses header-only inline functions from `core_cm3.h`.

**File affected**: `cmake/boards/stm32f103c8t6.cmake:62-64`

### Linker Script Requirements

Linker script must define `_estack` (stack pointer) for startup file:

```ld
_estack = 0x20005000;    /* End of RAM (20KB for F103C8T6) */
```

**File**: `boards/stm32f103c8t6/STM32F103C8Tx_FLASH.ld:5`

### Build Configuration

Must always specify:
1. Toolchain: `-DCMAKE_TOOLCHAIN_FILE=cmake/toolchains/arm-gcc.cmake`
2. Board: `-DBOARD=stm32f103c8t6` (or other board name)

If either is missing, CMake will fatal-error with helpful message.

---

## Testing Single Function

To test a single function change without full build:

```bash
# Build and flash in one command
cmake --build build && \
  openocd -f boards/stm32f103c8t6/openocd.cfg \
    -c "program build/firmware.elf verify reset exit"
```

---

## VS Code Integration

### Required Extensions

| Extension | ID | Purpose |
|-----------|-----|---------|
| C/C++ | ms-vscode.cpptools | IntelliSense, jump to definition |
| CMake Tools | ms-vscode.cmake-tools | Build config, CMake sidebar |
| Cortex-Debug | marus25.cortex-debug | ARM debugging via OpenOCD/JLink |

### Key Settings

- `"cmake.configureOnOpen": false` - Manual configure only
- `"C_Cpp.default.configurationProvider": "ms-vscode.cmake-tools"` - Use CMake for IntelliSense
- `"C_Cpp.default.compilerPath": "arm-none-eabi-gcc"` - Should be auto-detected by CMake Tools

---

## Known Issues & Workarounds

### WSL2 + ST-Link

OpenOCD in WSL2 cannot access USB directly. Use Windows `usbipd` to forward ST-Link.

```powershell
# Windows PowerShell (Admin)
winget install usbipd
usbipd bind --busid <BUSID>
usbipd attach --wsl --busid <BUSID>
```

### WSL2 USB Permissions

If ST-Link shows up but cannot connect:
1. Add user to plugdev group: `sudo usermod -aG plugdev $USER`
2. Re-login or: `newgrp plugdev`

---

## Reference Implementation

When adding new source files to `CMakeLists.txt`:

```cmake
add_executable(firmware.elf
    src/main.c
    src/your_new_file.c    # Add here
    ${STARTUP}
)
```

Include paths for new sources:
```cmake
target_include_directories(firmware.elf PRIVATE
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/src      # If .h and .c are together
)
```

---

## Project Scope

This template is designed for:

- **STM32F1xx** with StdPeriph Library V3.5.0 (currently configured)
- **STM32F4xx** with HAL/LL (planned)
- **GD32F1xx** clone with StdPeriph (planned)
- **NRF52xxx** with nRF5 SDK (planned)

**NOT recommended for**: Beginners first touching MCUs (use Keil/STM32CubeMX first)

---

## Course Notes (江科大STM32课程)

### Course Structure (课件目录)

```
课件/程序源码/STM32Project-有注释版/
├── 1-1 接线图/          # 每个实验的接线图片
├── 1-2 keilkill批处理/
├── 1-3 Delay函数模块/    # Delay.c, Delay.h
├── 1-4 OLED驱动函数模块/ # 4针脚I2C版本 / 7针脚SPI版本
├── 2-1 STM32工程模板/
├── 3-1 LED闪烁/
├── 3-2 LED流水灯/
├── 3-3 蜂鸣器/         # PB12 蜂鸣器
├── 3-4 按键控制LED/      # Hardware/LED.c, Hardware/Key.c
├── 3-5 光敏传感器控制蜂鸣器/
├── 4-1 OLED显示屏/
├── 5-1 对射式红外传感器计次/
├── 5-2 旋转编码器计次/
├── 6-1 定时器定时中断/
├── 6-2 定时器外部时钟/
├── 6-3 PWM驱动LED呼吸灯/
├── 6-4 PWM驱动舵机/
├── 6-5 PWM驱动直流电机/
├── 6-6 输入捕获模式测频率/
├── 6-7 PWMI模式测频率占空比/
├── 6-8 编码器接口测速/
├── 7-1 AD单通道/
├── 7-2 AD多通道/
├── 8-1 DMA数据转运/
├── 8-2 DMA+AD多通道/
├── 9-1 串口发送/
├── 9-2 串口发送+接收/
├── 9-3 串口收发HEX数据包/
├── 9-4 串口收发文本数据包/
├── 10-1 软件I2C读写MPU6050/
├── 10-2 硬件I2C读写MPU6050/
├── 11-1 软件SPI读写W25Q64/
├── 11-2 硬件SPI读写W25Q64/
├── 12-1 读写备份寄存器/
├── 12-2 实时时钟/
├── 13-1 修改主频/
├── 13-2 睡眠模式+串口发送+接收/
├── 13-3 停止模式+对射式红外传感器计次/
├── 13-4 待机模式+实时时钟/
├── 14-1 独立看门狗/
├── 14-2 窗口看门狗/
├── 15-1 读写内部FLASH/
└── 15-2 读取芯片ID/
```

### Keil Project Structure vs VS Code

| Keil | VS Code | Description |
|-------|---------|-------------|
| User/ | src/ | main.c, application code |
| Library/ | drivers/STM32F10x_StdPeriph_Driver/ | Standard Peripheral Library |
| Start/ | drivers/CMSIS/CM3/DeviceSupport/ST/STM32F10x/startup/ | Startup files (.s) |
| System/ | drivers/CMSIS/CM3/DeviceSupport/ST/STM32F10x/ | system_stm32f10x.c |
| Hardware/ | src/ (or include/) | Module drivers (LED.c, Key.c, OLED.c) |

### Reusable Modules (可复用模块)

**Delay Module (1-3)**
- Files: `Delay.c`, `Delay.h`
- Functions: `Delay_us()`, `Delay_ms()`, `Delay_s()`
- Usage: `#include "Delay.h"` then call delay functions
- Copy to: VS Code project `src/` and `include/`

**LED Module (3-4)**
- Files: `Hardware/LED.c`, `Hardware/LED.h`
- Pins: PA1 (LED1), PA2 (LED2)
- Functions: `LED_Init()`, `LED1_ON/OFF/Turn()`, `LED2_ON/OFF/Turn()`

**OLED Driver (1-4)**
- Files: `oled.c`, `oled.h` (choose 4-pin I2C or 7-pin SPI)
- Interface: I2C (SCL=PB10, SDA=PB11) or SPI

### Quick Operation Guide (操作指引)

**Step 1: 查看接线图**
```bash
# 查看对应实验的接线图
open "stm32/learning/课件/程序源码/STM32Project-有注释版/1-1 接线图/3-X 实验名.jpg"
```

**Step 2: 创建新项目**
```bash
# 复制模板
cp -r stm32/learning/vscode_cmake_template stm32/learning/lesson_3-3
cd stm32/learning/lesson_3-3
```

**Step 3: 复制课程模块**
```bash
# 复制Delay模块（如果需要）
cp stm32/learning/课件/程序源码/STM32Project-有注释版/1-3 Delay函数模块/Delay.c src/
cp stm32/learning/课件/程序源码/STM32Project-有注释版/1-3 Delay函数模块/Delay.h include/

# 复制LED模块（如果需要）
cp stm32/learning/课件/程序源码/STM32Project-有注释版/3-4 按键控制LED/Hardware/LED.c src/
cp stm32/learning/课件/程序源码/STM32Project-有注释版/3-4 按键控制LED/Hardware/LED.h include/
```

**Step 4: 编写main.c**
参考课程源码的main.c，适配VS Code项目结构

**Step 5: 更新CMakeLists.txt**
```cmake
add_executable(firmware.elf
    src/main.c
    src/Delay.c      # 添加新模块
    src/LED.c        # 添加新模块
    ${STARTUP}
)
```

**Step 6: 编译烧录**
```bash
cmake --build build
openocd -f boards/stm32f103c8t6/openocd.cfg -c "program build/firmware.elf verify reset exit"
```

### Common Pin Assignments

| Module | Pin | Function |
|--------|------|----------|
| LED | PA1, PA2 | LED1, LED2 (Active Low) |
| Buzzer | PB12 | Buzzer (Active Low) |
| Key | PB1, PB11 | Key1, Key2 |
| OLED I2C | PB10(SCL), PB11(SDA) | I2C1 |
| UART | PA9(TX), PA10(RX) | USART1 |

### STM32F103C8T6 Blue Pinout (引脚定义)

```
Blue Pill STM32F103C8T6
┌─────────────────────────────────────┐
│ 3.3V  ┃  C13  ┃  GND        │
│  C14   ┃  C15   ┃  B10        │
│  A0    ┃  A1    ┃  A2         │
│  A3    ┃  A4    ┃  A5         │
│  A6    ┃  A7    ┃  B0         │
│  B1    ┃  C0    ┃  C1         │
│  C2    ┃  C3    ┃  C4         │
│  C5    ┃  B12   ┃  B13        │
│  B14   ┃  B15   ┃  A8         │
│  A9    ┃  A10   ┃  A11        │
│  A12   ┃  GND   ┃  A15        │
│  B3    ┃  B4    ┃  B5         │
│  B6    ┃  B7    ┃  B8         │
│  B9    ┃  5V    ┃  GND        │
└─────────────────────────────────────┘
```
