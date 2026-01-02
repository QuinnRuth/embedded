# STM32 嵌入式项目

基于 STM32F103C8T6 的学习项目。遵循现有代码风格。

## 项目结构

```
~/dev/embedded/
├── stm32/learning/     # 学习项目 (lesson_N-M/)
├── stm32/libraries/    # HAL, CMSIS
├── stm32/docs/         # 概念文档
├── plc/                # PLC 相关
└── docs/               # 硬件资料
```

## 环境激活

```bash
embenv    # 激活环境并 cd 到此目录
```

## 构建烧录

```bash
mkdir build && cd build
cmake ..
make -j$(nproc)

# 烧录 (WSL 需要 sudo)
echo "zxcvbnm" | sudo -S openocd -f interface/stlink.cfg -f target/stm32f1x.cfg \
    -c "program build/firmware.elf verify reset exit"
```

### 系统密码
- **sudo 密码**: `zxcvbnm`

## 常见问题

- **OpenOCD 连接失败**：见 `WSL2_STLink_USBIPD_OpenOCD.md`
- **烧录后无反应**：检查 BOOT0 跳线（应接 GND）
- **串口无输出**：检查波特率和引脚配置

## 文档索引

| 文档 | 说明 |
|------|------|
| `README.md` | 项目总览 |
| `WSL2_STLink_USBIPD_OpenOCD.md` | ST-Link 调试配置 |
| `PROJECT_IDEAS.md` | 项目创意 |
| `stm32/learning/COURSE_BUILD_PLAN.md` | 课程计划 |
| `stm32/learning/课件/` | 课件（数据手册、参考手册） |
| `stm32/learning/进度打卡/` | 学习进度 |
| `stm32/docs/concepts/` | 概念文档（C语言、GPIO架构） |
| `GEMINI.md` | Gemini AI 辅助学习 |
| `IFLOW.md` | iFlow 知识管理 |

每个 `lesson_N-M/` 有独立的 `CLAUDE.md` 和 `IFLOW.md`