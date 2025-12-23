# S7-1200 + 触摸屏：ABB 机器人 6 轴角度实时显示（操作步骤 + ABB端完整程序）

目标：

- 运行页面实时显示 ABB 机器人当前 6 个轴角度（保留小数点后两位）
- 可选择机器人垛形；行/列/层最小为 1；行/列最大为 3；层数不限制（输入错误不允许写入）
- 参数不合理不可启动；仅当机器人在安全位置 `(0, 0, 0, 0, 90, 0)` 才能启动
- 显示机器人状态与当前处理的物料数量
- 机器人状态包含：正在运行中、机器人初始姿态、急停安全位置、空闲安全位置、停止

> 通讯参考：`abbk考/ABB机器人发送当前位置坐标给PLC-林木森Lmsa-微信公众号-2025-12-19.markdown`  
> 本文将其简化为“只发 6 轴角度”。

---

## 1. 通讯与数据约定（先定死，最省事）

- 拓扑：ABB 机器人 = TCP Client；S7-1200 = TCP Server（被动监听）
- 端口：PLC 监听 `2000`
- 周期：ABB 每 `0.2s` 发送一次（建议 0.1~0.3s）
- 数据帧：仅 6 轴角度
  - `6 × REAL(IEEE754 Float4)` = `24 bytes`
  - ABB 端按参考实现进行字节反序（大端网络序）；PLC 端按相同字节序还原为 REAL
- 显示：触摸屏对每轴显示格式设为 `0.00`
- 安全位容差：每轴 `±1.00°`（建议起步用这个，稳定后再收紧）

---

## 2. ABB 机器人端：完整 RAPID 程序（只发 6 轴，24 字节）

使用方式：

1. 将下方代码保存为一个 RAPID 模块文件（例如 `PLC_Axis6_Stream.mod`）
2. 只需要修改 `gPlcIp / gPlcPort / gSendPeriod`
3. 下载到控制器，运行 `main()`

> 注：本仓库已生成对应模块文件：`abbk考/PLC_Axis6_Stream.mod`。  
> 导入建议用“加载模块/合并”方式，只新增该模块，不要用会覆盖整套程序的“还原备份/系统包下载”（详见本文末尾“导入与不覆盖”）。

```rapid
MODULE PLC_Axis6_Stream

    ! === 参数：按你的PLC改这里 ===
    PERS string gPlcIp := "192.168.0.1";
    PERS num    gPlcPort := 2000;
    PERS num    gSendPeriod := 0.2;   ! 秒：0.1~0.3 都可以

    VAR socketdev gSock;
    VAR bool gSockOpen := FALSE;

    VAR intnum gIntNo;

    VAR num gAxis{6};
    VAR rawbytes gRaw;
    VAR byte gTmp{4};
    VAR byte gFrame{24};

    PROC BuildFrame()
        VAR jointtarget jt;
        VAR num i;
        VAR num p;

        jt := CJointT();

        gAxis{1} := jt.robax.rax_1;
        gAxis{2} := jt.robax.rax_2;
        gAxis{3} := jt.robax.rax_3;
        gAxis{4} := jt.robax.rax_4;
        gAxis{5} := jt.robax.rax_5;
        gAxis{6} := jt.robax.rax_6;

        ClearRawBytes gRaw;
        p := 1;

        FOR i FROM 1 TO 6 DO
            PackRawBytes gAxis{i}, gRaw, 1\Float4;

            UnpackRawBytes gRaw, 1, gTmp{1}\Hex1;
            UnpackRawBytes gRaw, 2, gTmp{2}\Hex1;
            UnpackRawBytes gRaw, 3, gTmp{3}\Hex1;
            UnpackRawBytes gRaw, 4, gTmp{4}\Hex1;

            ! 按参考做反序（大端网络序）
            gFrame{p} := gTmp{4}; p := p + 1;
            gFrame{p} := gTmp{3}; p := p + 1;
            gFrame{p} := gTmp{2}; p := p + 1;
            gFrame{p} := gTmp{1}; p := p + 1;
        ENDFOR
    ENDPROC

    PROC EnsureConnected()
        IF gSockOpen THEN
            RETURN;
        ENDIF

        SocketClose gSock;
        SocketCreate gSock;
        SocketConnect gSock, gPlcIp, gPlcPort;
        gSockOpen := TRUE;

    ERROR
        gSockOpen := FALSE;
        TRYNEXT;
    ENDPROC

    PROC SendFrame()
        EnsureConnected;

        IF NOT gSockOpen THEN
            RETURN;
        ENDIF

        SocketSend gSock\data:=gFrame;

    ERROR
        gSockOpen := FALSE;
        SocketClose gSock;
        TRYNEXT;
    ENDPROC

    PROC main()
        WHILE TRUE DO
            BuildFrame;
            SendFrame;
            WaitTime gSendPeriod;
        ENDWHILE
    ENDPROC

ENDMODULE
```

---

## 3. S7-1200（TIA Portal）PLC 侧：最简操作步骤（只说做什么）

### 3.1 建 TCP Server 接收 24 字节

1. 在 TIA Portal 打开项目，确认 S7-1200 CPU 已配置以太网 IP（与 ABB 同网段）
2. 新建全局 DB：`DB_机器人通讯`
3. 在 `DB_机器人通讯` 建变量（示例）：
   - `接收Bytes : ARRAY[0..23] OF BYTE`
   - `轴角度 : ARRAY[1..6] OF REAL`
   - `通讯OK : BOOL`
   - `接收超时 : BOOL`
4. 新建一个 `FB_机器人TCP`（或放到现有 FB 中），使用 S7-1200 的开放式 TCP 通讯指令：
   - `TCON`：建立 TCP Server，监听端口 `2000`
   - `TRCV`：循环接收固定长度 `24` 字节，写到 `DB_机器人通讯.接收Bytes`
   - 收到后：把 `接收Bytes` 每 4 个字节还原为 1 个 REAL，依次写入 `轴角度[1..6]`
   - 维护 `通讯OK` 与“接收超时”（例如 1 秒内未收到则超时）
5. 在 `OB1` 周期调用 `FB_机器人TCP`

> 若 PLC 端解析出来的 REAL 明显异常（极大值/NaN），优先检查字节序：ABB 端已经按参考做了反序；PLC 端应按同样字节序还原。

---

## 4. 触摸屏（HMI）运行页面：最简操作步骤

### 4.1 6 轴角度实时显示（两位小数）

1. 新建“运行页面”
2. 放 6 个“数值显示”，分别绑定：
   - `DB_机器人通讯.轴角度[1]` … `DB_机器人通讯.轴角度[6]`
3. 每个显示的格式设为 `0.00`（两位小数）

### 4.2 垛形选择 + 行列层输入限制（输入错就不允许写入）

1. 放一个“垛形选择”（下拉框/按钮组选一种），绑定 `垛形类型`（PLC 变量，INT/USINT 均可）
2. 放 3 个“数值输入”，绑定 PLC 变量：`行 / 列 / 层`
3. 对输入框设置范围：
   - 行：最小 `1`，最大 `3`（越界不允许输入，需重新输入）
   - 列：最小 `1`，最大 `3`（越界不允许输入，需重新输入）
   - 层：最小 `1`，最大不限制（由 PLC “合理性检查”决定能否启动）

### 4.3 启动按钮联锁（不合理/不安全不得启动）

1. 放“启动”按钮，写入 PLC 变量 `启动请求`（BOOL）
2. 把按钮“使能条件”绑定 PLC 变量 `允许启动`（为 1 才可按）
3. 页面增加一条“禁止原因”文本显示（推荐用状态码映射），当 `允许启动=0` 时提示：
   - 参数无效/不合理
   - 机器人不在安全位置
   - 通讯断开
   - 急停等

### 4.4 状态与物料数量显示

1. 放“文本显示”绑定 PLC 变量 `机器人状态码`，做文本列表映射：
   - 正在运行中
   - 机器人初始姿态
   - 急停安全位置
   - 空闲安全位置
   - 停止
2. 放“数值显示”绑定 PLC 变量 `当前处理物料数量`

---

## 5. PLC 侧逻辑（你需要实现的最少判定）

### 5.1 安全位置判定（必须在 `(0,0,0,0,90,0)` 才能启动）

- 设 `tol := 1.0`（单位：度）
- `安全位OK := AND(ABS(A1-0)<=tol, ABS(A2-0)<=tol, ABS(A3-0)<=tol, ABS(A4-0)<=tol, ABS(A5-90)<=tol, ABS(A6-0)<=tol)`

### 5.2 参数有效/合理

- 参数有效（输入范围）：
  - 行/列：`1..3`
  - 层：`>=1`
- 参数合理（不合理不允许启动）：
  - 建议至少做：`总数量 := 行 * 列 * 层`
  - 结合现场工艺设一个上限（例如最大堆高/最大总数量），超过即判“合理=FALSE”

### 5.3 允许启动（建议）

- `允许启动 := 通讯OK AND NOT 急停 AND 安全位OK AND 参数有效 AND 参数合理`

### 5.4 机器人状态（建议优先级，从高到低）

1. `急停=1 AND 安全位OK=1` → 急停安全位置
2. `运行中=1` → 正在运行中
3. `初始姿态OK=1` → 机器人初始姿态
4. `运行中=0 AND 安全位OK=1 AND 通讯OK=1` → 空闲安全位置
5. 其他 → 停止（包含通讯断开、未在安全位、参数不满足等）

---

## 6. 现场核对清单（一次性排坑）

- ABB → PLC 的 IP/端口一致，PLC 正在监听 `2000`
- PLC 收到的字节长度固定为 `24`；轴角度数值正常变化
- HMI 显示 `0.00` 格式生效
- 行/列越界确实“无法写入”，必须重新输入
- 不在安全位时，启动按钮不可按（或按下后 PLC 拒绝并提示原因）

---

## 7. 导入到虚拟示教器（RobotStudio）与“不覆盖”注意事项

### 7.1 导入（推荐：RobotStudio 里加载模块）

1. 让 RobotStudio 连接到虚拟控制器（Virtual Controller）
2. 在 `RAPID` 里选择对应任务（通常是 `T_ROB1`）
3. 执行 “Load Module/加载模块”，选择 `PLC_Axis6_Stream.mod`，并选择“合并/追加（Merge/Add）”到现有程序
4. 如已有自己的主程序，建议不要改动现有 `main()`：改为在你自己的主循环里调用 `PLC_Axis6_Stream\main;` 或把本模块的 `main()` 改名后再调用

### 7.2 不覆盖（关键点）

- 不要用会“整包覆盖”的操作：例如“还原备份（Restore）/加载系统（System Pack）”去导入单个 `.mod`
- 模块名/过程名尽量避免冲突：如果你系统里已经有 `main()`，请改名（例如 `Axis6StreamMain()`）后再加载
- 导入前先做一次备份：RobotStudio 的 “Backup/备份控制器” 或复制虚拟控制器目录（至少能回滚）
