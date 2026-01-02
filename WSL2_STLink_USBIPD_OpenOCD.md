# WSL2 使用 ST-Link：usbipd 转发 + OpenOCD 烧录（新手复用版）

WSL2 里默认**不能直接访问 USB 设备**（包括 ST-Link）。需要在 Windows 侧用 `usbipd-win` 将 USB 设备转发进 WSL2，然后在 WSL 里用 OpenOCD 烧录。

## 0. 前提

- Windows 已安装 `usbipd-win`（本机示例：`usbipd-win 5.3.0`）
- WSL2 发行版已安装 OpenOCD（并有可用的 `.cfg`）
- ST-Link 已插入电脑 USB 口（建议固定插同一个口，BUSID 更稳定）

## 0.1 严格使用规则（避免走弯路）

- Windows 命令只在 **Windows PowerShell** 执行（`usbipd ...`）；WSL 命令只在 **WSL 终端** 执行（`lsusb/openocd/...`）
- 烧录/调试前先关闭 Windows 上可能占用 ST-Link 的软件（CubeProgrammer/CubeIDE/其他 OpenOCD）
- 你看到的 `BUSID`（如 `2-1`）跟“USB 物理口”强相关：尽量固定同一个 USB 口；换口就重新 `usbipd list`
- `attach --auto-attach` 会启动“无尽循环”，必须保持该 PowerShell 窗口/进程在运行；关窗口或重启后需要重新执行 `attach`

## 0.2 最短复用流程（每次插入后照抄）

> 前提：已做过第 1/2 节的一次性准备（usbipd 已安装且设备已 bind/shared）。

1) Windows PowerShell（让设备进入 WSL）：

```powershell
usbipd attach --wsl --busid 2-1 --auto-attach
```

2) WSL（确认设备已进来）：

```bash
lsusb | grep -i 0483
```

3) WSL（烧录）：

```bash
cd /path/to/your/project
sudo openocd -f boards/stm32f103c8t6/openocd.cfg -c "program build/firmware.elf verify reset exit"
```

> 把 `2-1`、`/path/to/your/project`、`build/firmware.elf` 改成你的实际值。

## 1. 一次性准备：安装/验证 usbipd-win（Windows）

在 Windows PowerShell 里确认 `usbipd` 可用：

```powershell
usbipd --version
```

如果提示找不到命令，安装（管理员 PowerShell）：

```powershell
winget install --id dorssel.usbipd-win -e
```

安装后重新打开 PowerShell 再执行 `usbipd --version` 验证。

## 2. 一次性准备：绑定设备（Windows，管理员）

> `bind` 通常需要管理员权限；`attach` 视环境可能不需要，但建议按此流程操作。

1) 查看 USB 设备列表，找到 ST-Link 的 `BUSID`（形如 `2-1`）：

```powershell
usbipd list
```

严格定位 ST-Link（推荐二选一）：

- 直接按 ST 的 VID 过滤（通常是 `0483`）：

```powershell
usbipd list | Select-String 0483
```

- 如果列表里有多个相似设备：用“拔插对比法”  
  先 `usbipd list` 记下可疑行 → 拔掉 ST-Link 再 `usbipd list` → 消失的那一行就是它

2) 绑定（把 `2-1` 换成你的实际 `BUSID`）：

```powershell
usbipd bind --busid 2-1
```

验证点：

- 输出包含 `was already shared` 或 `successfully shared` 都算成功
- `usbipd list` 里该设备状态应变为 `Shared`（或后续 `Attached`）

## 3. 日常使用：转发到 WSL2（Windows）

把设备附加到 WSL（默认发行版）：

```powershell
usbipd attach --wsl --busid 2-1
```

推荐开启自动重连（设备拔插/断开后自动重新附加）：

```powershell
usbipd attach --wsl --busid 2-1 --auto-attach
```

> 说明：
> - `--auto-attach` 会在设备被拔掉/重新插上时自动重连（前提是 BUSID 对应的口不变）。
> - `--auto-attach` 会一直运行并占用当前 PowerShell（会显示 “Starting endless attach loop”）：建议单独开一个 PowerShell 窗口专门跑它。
> - 如果你换了 USB 口，`BUSID` 会变，需要重新 `usbipd list` 后按新 BUSID 执行。
>
> 可选：指定发行版（把 `Ubuntu-22.04` 换成你的发行版名）：
>
> ```powershell
> usbipd attach --wsl Ubuntu-22.04 --busid 2-1 --auto-attach
> ```

验证点（Windows 侧）：

```powershell
usbipd list
```

应看到该 `BUSID` 的状态为 `Attached`（或类似 Attached/WSL Attached 的描述）。

## 4. WSL2 内确认 ST-Link 是否进来了

在 WSL 里查看 USB 列表（通常 ST 的 VID 是 `0483`）：

```bash
lsusb | grep -i 0483
```

如果 WSL 提示 `lsusb: command not found`，先安装：

```bash
sudo apt update
sudo apt install -y usbutils
```

如果你不想手动切到 WSL 窗口，也可以在 Windows PowerShell 里直接调用 WSL 执行验证命令：

```powershell
wsl -e bash -lc "lsusb | grep -i 0483"
```

如果还是看不到，先回到 Windows 检查 `usbipd list` 是否显示已 Attached，然后再看 WSL 的 `dmesg`：

```bash
dmesg | tail -n 80
```

## 5. 在 WSL2 里用 OpenOCD 烧录

示例（按你的工程路径调整）：

```bash
sudo openocd -f boards/stm32f103c8t6/openocd.cfg \
  -c "program build/firmware.elf verify reset exit"
```

如果 OpenOCD 报找不到脚本（例如 `interface/stlink.cfg` / `target/stm32f1x.cfg`），为 OpenOCD 显式指定 scripts 目录：

```bash
sudo openocd -s /usr/share/openocd/scripts \
  -f boards/stm32f103c8t6/openocd.cfg \
  -c "program build/firmware.elf verify reset exit"
```

## 6. 断开转发（Windows）

如果你在跑 `attach --auto-attach`，要先在那个 PowerShell 窗口按 `Ctrl+C` 停止“无尽循环”，否则你 `detach` 之后会立刻被自动重新附加。

```powershell
usbipd detach --busid 2-1
```

## 7. 常见问题速查

### 7.1 OpenOCD 报 `open failed`

常见原因与排查顺序：

1) **USB 没转发进 WSL2**：先按第 3/4 节确认 `usbipd list` 显示已 Attached，且 WSL 内 `lsusb` 能看到 ST（`0483:xxxx`）。
2) **权限问题**：先用 `sudo openocd ...` 排除权限。
3) **设备被占用**：关闭 Windows 上可能占用 ST-Link 的软件（如 STM32CubeProgrammer、CubeIDE、其他 OpenOCD 实例）。

### 7.2 `BUSID` 每次都变

`BUSID` 与 USB 物理口有关。尽量固定插同一个 USB 口；换口就需要重新 `usbipd list` 并用新的 `BUSID` 执行 `bind/attach`。

### 7.3 我已经 `bind` 了，但 WSL 里还是没有设备

严格按顺序检查：

1) Windows：`usbipd list` 是否显示该设备为 `Attached`（不是 `Shared`/`Not shared`）
2) Windows：是否把 `lsusb` 误在 PowerShell 里运行了（`lsusb` 是 WSL 命令）
3) WSL：`dmesg | tail -n 80` 是否有 USB attach 的日志

### 7.4 Attach 成功但 WSL 里看到的是错误设备（真实案例！）

**问题现象**：

Windows PowerShell 显示 attach 成功：
```
WSL 2025-12-30 12:09:28 Device 2-3 is available. Attempting to attach...
WSL 2025-12-30 12:09:35 Device 2-3 is now attached.
```

但 WSL 里 `lsusb` 看不到 ST-Link（`0483:xxxx`），反而看到蓝牙适配器：
```bash
$ lsusb
Bus 001 Device 002: ID 13d3:3585 IMC Networks Wireless_Device  # 这是蓝牙！
```

**原因**：

BUSID 记错了！你 attach 的 `2-3` 其实是蓝牙适配器，不是 ST-Link。

**诊断方法**：

1) Windows PowerShell 查看完整列表：

```powershell
usbipd list
```

示例输出：
```
BUSID  VID:PID    DEVICE                                STATE
1-3    2b7e:b680  HD Webcam                             Not shared
1-4    1ea7:0066  USB 输入设备                          Not shared
2-1    0483:3748  STM32 STLink                          Shared      ← 这才是 ST-Link!
2-2    0000:3825  USB 输入设备                          Not shared
2-3    13d3:3585  MediaTek Bluetooth Adapter            Attached    ← 你错误 attach 了这个
```

2) 精确过滤 ST-Link（VID=0483）：

```powershell
usbipd list | Select-String 0483
```

**解决步骤**：

1) 停止错误的 attach（在运行 `--auto-attach` 的 PowerShell 窗口按 `Ctrl+C`）

2) 用正确的 BUSID 重新 attach：

```powershell
usbipd attach --wsl --busid 2-1 --auto-attach
```

3) WSL 验证：

```bash
lsusb | grep -i 0483
# 应该看到: Bus 001 Device 003: ID 0483:3748 STMicroelectronics ST-LINK/V2
```

**教训**：

- **永远用 VID 过滤确认 ST-Link 的 BUSID**，不要凭记忆
- ST-Link 的 VID 固定是 `0483`，常见 PID：`3748`(V2), `374b`(V2-1), `3752`(V3)
- 多个 USB 设备时，BUSID 容易混淆

---

## 8. 完整诊断流程图

当 ST-Link 烧录失败时，按此顺序排查：

```
[开始] ST-Link 烧录失败
    │
    ▼
[Step 1] Windows: usbipd list
    │
    ├─ ST-Link 不在列表中 → 检查 USB 线/换口/重插
    │
    ├─ ST-Link 状态是 "Not shared" → 执行 usbipd bind --busid <X>
    │
    ├─ ST-Link 状态是 "Shared" → 执行 usbipd attach --wsl --busid <X>
    │
    └─ ST-Link 状态是 "Attached" → 继续 Step 2
    │
    ▼
[Step 2] WSL: lsusb | grep -i 0483
    │
    ├─ 没有输出 → 检查 attach 的 BUSID 是否正确（见 7.4）
    │            → 检查 dmesg | tail -30 是否有 USB 日志
    │
    └─ 看到 0483:3748 → 继续 Step 3
    │
    ▼
[Step 3] WSL: openocd -f ... -c "program ..."
    │
    ├─ "open failed" → 关闭 Windows 上占用 ST-Link 的软件
    │                → 尝试 sudo openocd ...
    │
    └─ "Programming Finished" → 成功！
```

---

## 9. 本机实际 BUSID 记录

> 记录你的设备 BUSID，避免每次都要查

| 设备 | VID:PID | BUSID | USB口位置 |
|------|---------|-------|----------|
| ST-Link V2 | 0483:3748 | 2-1 | 右侧 USB-A |
| 蓝牙适配器 | 13d3:3585 | 2-3 | 内置 |

**注意**：换 USB 口后 BUSID 会变，需要重新 `usbipd list` 确认。
