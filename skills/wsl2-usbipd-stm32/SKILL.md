---
name: wsl2-usbipd-stm32
description: Use usbipd-win to pass through STM32 ST-Link (OpenOCD flashing/debug) and USB-UART dongles (CH340/CP210x/FTDI serial monitor) into WSL2; includes a copy/paste quick workflow for attaching both devices and detailed troubleshooting.
metadata:
  short-description: WSL2 usbipd + ST-Link + USB-UART quickflow
---

# WSL2：usbipd 转发 ST-Link + USB 转串口（CH340）一把梭

## 超级快捷（推荐）：ST-Link + CH340 一起 `--auto-attach`（写在最前面，照抄）

前提：你已经从 `usbipd list` 找到了两个设备的 BUSID，例如：

- ST-Link：`0483:xxxx` → `BUSID 2-1`
- CH340：`1a86:7523` → `BUSID 2-2`

### 1) Windows（管理员 PowerShell）：先共享（一次性 / 换口后重做）

```powershell
usbipd bind --busid 2-1
usbipd bind --busid 2-2
```

### 2) Windows（PowerShell）：分别自动重连（建议两个窗口/两个 tab）

窗口 A（ST-Link）：

```powershell
usbipd attach --wsl --busid 2-1 --auto-attach
```

窗口 B（CH340）：

```powershell
usbipd attach --wsl --busid 2-2 --auto-attach
```

> `--auto-attach` 会一直占用窗口（endless loop），属于正常现象；不要关掉窗口。

### 3) WSL：验证设备进来了

```bash
lsusb | egrep -i "0483|1a86"
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

常见结果：

- ST-Link：能看到 `0483:3748/374b/3752 ...`
- CH340：出现 `/dev/ttyUSB0`（大多数是这个）

### 4) WSL：串口监视（把 `9600` 换成你的波特率）

```bash
screen /dev/ttyUSB0 9600
```

退出 `screen`：按 `Ctrl+A` 再按 `K`，然后确认。

### 5) WSL：OpenOCD 烧录（把路径换成你的工程实际值）

```bash
sudo openocd -f boards/stm32f103c8t6/openocd.cfg -c "program build/firmware.elf verify reset exit"
```

---

## 快捷版（不需要自动重连）：一次 attach 两个设备

Windows PowerShell（管理员先 bind 一次）：

```powershell
usbipd bind --busid <STLINK_BUSID>
usbipd bind --busid <UART_BUSID>
```

Windows PowerShell（attach 可以同一窗口连续执行）：

```powershell
usbipd attach --wsl --busid <STLINK_BUSID>
usbipd attach --wsl --busid <UART_BUSID>
```

---

## 一次性准备清单（建议做完，后面少踩坑）

### A. Windows：usbipd-win

```powershell
usbipd --version
```

没有就安装（管理员 PowerShell）：

```powershell
winget install --id dorssel.usbipd-win -e
```

### B. WSL：常用工具

- `lsusb`（用于确认 USB 是否转发进来）：

```bash
sudo apt update
sudo apt install -y usbutils
```

- 串口工具（二选一即可）：
  - `screen`：`sudo apt install -y screen`
  - `minicom`：`sudo apt install -y minicom`

### C. WSL：串口权限（避免每次都 sudo）

```bash
sudo usermod -aG dialout $USER
```

然后重开一个 WSL 终端（或重新登录 WSL）生效。

---

## 查 BUSID 的正确姿势（最重要：别 attach 错设备）

Windows PowerShell：

```powershell
usbipd list
```

推荐用 VID 精确过滤：

```powershell
usbipd list | Select-String 0483             # ST-Link
usbipd list | Select-String 1A86             # CH340/CH341
usbipd list | Select-String "10C4|0403"      # CP210x / FTDI
```

如果你不确定是哪一行：用“拔插对比法”最稳。

---

## USB-TTL 接线要点（课程 9.1 常见）

以 `STM32F103` 的 `USART1` 为例（常见：PA9/PA10）：

- USB-TTL `TXD` → MCU `RX`（例如 PA10）
- USB-TTL `RXD` → MCU `TX`（例如 PA9）
- `GND` → `GND`（必须接）
- `VCC`：通常不需要接（板子自己供电就行）；要接也要确认 **3.3V/5V** 匹配

常见问题：

- 只接了 TX/RX 没接 GND → 100% 不通
- TX/RX 没有交叉 → 无输出
- TTL 电平不匹配（5V 打到 3.3V IO）→ 有风险，先确认模块电平

---

## 在 WSL 里怎么“看串口”（更完整的几种方式）

### 方式 1：screen（最省事）

```bash
screen /dev/ttyUSB0 9600
```

### 方式 2：minicom（更完整）

```bash
minicom -D /dev/ttyUSB0 -b 9600
```

### 方式 3：只看设备到底是哪个

```bash
dmesg | tail -n 80
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

---

## OpenOCD 烧录（WSL）

### 1) 推荐：直接用工程自带的 openocd.cfg（如果有）

```bash
sudo openocd -f boards/<board>/openocd.cfg -c "program <elf_or_hex> verify reset exit"
```

### 2) 通用：用 OpenOCD 自带脚本（适合快速验证）

```bash
sudo openocd -f interface/stlink-v2.cfg -f target/stm32f1x.cfg -c "program <elf_or_hex> verify reset exit"
```

如果 OpenOCD 提示找不到 `interface/...` / `target/...`：显式指定 scripts 目录（Ubuntu 常见路径）：

```bash
sudo openocd -s /usr/share/openocd/scripts -f interface/stlink-v2.cfg -f target/stm32f1x.cfg -c "program <elf_or_hex> verify reset exit"
```

---

## 断开/清理（Windows）

如果你在跑 `--auto-attach`：先在对应窗口按 `Ctrl+C` 停止 endless loop，再 detach。

```powershell
usbipd detach --busid <STLINK_BUSID>
usbipd detach --busid <UART_BUSID>
```

---

## 故障排查（把“其他调试方法”放后面）

### 1) `usbipd attach` 报：`Device is not shared`

原因：还没 `bind`（共享）。

解决（管理员 PowerShell）：

```powershell
usbipd bind --busid <BUSID>
```

### 2) Windows 能看到 COM4，但 WSL 没有 `/dev/ttyUSB0`

按顺序排查：

1. Windows：`usbipd list` 看该 BUSID 是否 `Attached`
2. WSL：`dmesg | tail -n 80` 看是否出现 `ttyUSB0`
3. 你是否 attach 了错误的 BUSID（比如把蓝牙适配器 attach 进来了）

### 3) OpenOCD 报 `open failed`

常见原因：

- USB 没转发进 WSL（先 `lsusb | grep -i 0483`）
- 权限问题（先用 `sudo openocd ...` 排除）
- Windows 上有软件占用 ST-Link（CubeProgrammer/CubeIDE/其他 OpenOCD）→ 关掉

### 4) `BUSID` 每次都变

BUSID 跟 USB 物理口强相关：尽量固定插同一个 USB 口；换口就重新 `usbipd list`。

### 5) attach 成功但设备不对（经典：attach 到蓝牙/摄像头了）

只用 VID 过滤确认：

```powershell
usbipd list | Select-String 0483
usbipd list | Select-String 1A86
```

---

## 使用提示（给 Codex 的“提问模板”）

当你要我定位问题或给你一键命令时，直接贴这 3 段就够：

1) Windows：`usbipd list` 的完整输出  
2) WSL：`lsusb` 输出（或 `lsusb | egrep -i "0483|1a86"`）  
3) WSL：`ls -l /dev/ttyUSB* /dev/ttyACM*` 输出

