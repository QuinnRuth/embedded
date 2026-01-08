# STM32 烧录 Skill

## 用途
STM32F103C8T6 使用 OpenOCD 烧录固件

## 烧录命令

```bash
# 基本命令
echo "zxcvbnm" | sudo -S openocd \
  -f /path/to/openocd.cfg \
  -c "program /path/to/firmware.elf verify reset exit"
```

## 烧录成功标志

```
** Programming Started **
Info : device id = 0x20036410
Info : flash size = 64kbytes
** Programming Finished **
** Verify Started **
** Verified OK **
** Resetting Target **
shutdown command invoked
```

## 常见错误与解决

### 1. Error: Can't find openocd.cfg
```
错误: Error: Can't find boards/stm32f103c8t6/openocd.cfg
解决: 使用绝对路径
```

### 2. Error: open failed
```
错误: Error: open failed
in procedure 'program'

可能原因:
- ST-Link 未连接
- ST-Link USB 线松动
- WSL2 USBIPD 连接断开

解决:
1. 检查 ST-Link USB 连接
2. 重插 USB 线
3. WSL2 下执行: usbipd.exe list, usbipd.exe attach -w 2-3-7
```

### 3. device id 识别错误
```
正常: Info : device id = 0x20036410 (STM32F103x8)
异常: 可能是 ST-Link 版本问题或芯片损坏
```

## 硬件检查清单

- [ ] ST-Link 已插入电脑 USB 口
- [ ] ST-Link 的 4 线 (SWD) 正确连接：
  - SWDIO → SWDIO
  - SWCLK → SWCLK
  - GND → GND
  - 3.3V → 3.3V (可选)
- [ ] 开发板已上电
- [ ] BOOT0 跳线接 GND (正常模式)
- [ ] ST-Link 指示灯常亮或闪烁

## WSL2 USBIPD 连接步骤

```bash
# Windows PowerShell (管理员)
usbipd.exe list                      # 查看设备
usbipd.exe bind --busid 2-3-7       # ST-Link 绑定 (ID 要按实际修改)
usbipd.exe attach -w 2-3-7         # 附加到 WSL2

# WSL2 终端
lsusb                              # 验证能看到 ST-Link
```

## 项目 openocd.cfg 路径

```
/home/muqiao/dev/embedded/stm32/learning/lesson_N-N/boards/stm32f103c8t6/openocd.cfg
```

## 快速烧录脚本

可以创建 shell 脚本 `flash.sh`:

```bash
#!/bin/bash
PROJECT_DIR="/home/muqiao/dev/embedded/stm32/learning/$1"
CFG_FILE="$PROJECT_DIR/boards/stm32f103c8t6/openocd.cfg"
ELF_FILE="$PROJECT_DIR/build/firmware.elf"

echo "zxcvbnm" | sudo -S openocd -f "$CFG_FILE" -c "program $ELF_FILE verify reset exit"
```

使用: `./flash.sh lesson_6-4`
