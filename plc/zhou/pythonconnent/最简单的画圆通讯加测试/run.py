#!/usr/bin/env python3
"""
极简版 S7 轨迹通讯 - 单文件，无依赖配置
用法: python run.py
"""
import time
import snap7
from snap7.util import get_bool, set_bool, get_real, set_real, get_int, set_int

# ============ 配置（按实际修改）============
PLC_IP = "192.168.0.1"
DB = 200
VELOCITY = 3
POINTS = [
    (491.3, 233.9),   # 1 起点：上中
    (391.3, 233.9),   # 2 左上
    (591.3, 233.9),   # 3 右上
    (491.3, 233.9),   # 4 回上中

    (491.3, 133.9),   # 5 中中
    (391.3, 133.9),   # 6 中横右边 (注释里写的是右半段，但看坐标是往左)
    (491.3, 133.9),   # 7 回中中
    (491.3, 33.9),    # 8 中下
    (391.3, 33.9),    # 12 收笔：左下
    (591.3, 33.9),    # 10 右下
    
    (541.3, 33.9),    # 9 中下与右下之间
    (541.3, 100.9),   # 高度抬到"中中和上之间" 就这个 别改
]

# ============ 核心函数 ============
def run():
    plc = snap7.client.Client()
    plc.connect(PLC_IP, 0, 1)
    print(f"[OK] 连接 {PLC_IP}")

    def wait_idle(timeout=5.0):
        """
        等待 PLC 完全空闲（上一个点已执行完成并被消费）
        
        空闲条件：
        - Enable = TRUE（Python 模式开启）
        - Busy = FALSE（不在执行中）
        - Done = TRUE（上一个点已完成）
        - NewPoint = FALSE（上一个点已被消费）
        """
        t0 = time.time()
        while time.time() - t0 < timeout:
            try:
                data = plc.db_read(DB, 14, 1)
                new_point = get_bool(data, 0, 0)
                busy = get_bool(data, 0, 1)
                done = get_bool(data, 0, 2)
                enable = get_bool(data, 0, 4)

                # Python 模式未开启，返回 False
                if not enable:
                    print("  [警告] PLC Enable 未开启，无法发送新点")
                    return False

                # 理想的"上一个点确实跑完而且被消费掉"的状态
                if (not busy) and done and (not new_point):
                    return True

            except Exception as e:
                print(f"  [警告] 读取状态失败: {e}")
                time.sleep(0.01)
                continue

            time.sleep(0.01)

        # 超时
        print(f"  [警告] 等待 PLC 空闲超时 ({timeout}s)")
        return False

    def write_point(x, y, v, idx):
        # 步骤1：先清除 NewPoint 标志（制造脉冲下降沿）
        data = plc.db_read(DB, 14, 1)
        set_bool(data, 0, 0, False)  # NewPoint = False
        plc.db_write(DB, 14, data)
        time.sleep(0.05)  # 给 PLC 时间识别下降沿

        # 步骤2：写入新坐标和参数，并置位 NewPoint（制造脉冲上升沿）
        data = plc.db_read(DB, 0, 16)
        set_real(data, 0, x)
        set_real(data, 4, y)
        set_real(data, 8, v)
        set_int(data, 12, idx)
        
        # ★ 关键：写新点前先把 Done 清 0，防止残留 Done=1 导致误判
        set_bool(data, 14, 2, False)   # Done = False
        
        set_bool(data, 14, 4, True)   # Enable
        set_bool(data, 14, 0, True)   # NewPoint = True（上升沿触发）
        plc.db_write(DB, 0, data)

    def wait_done(timeout=30):
        t0 = time.time()
        while time.time() - t0 < timeout:
            data = plc.db_read(DB, 14, 1)
            if get_bool(data, 0, 3):  # Error
                return False
            if get_bool(data, 0, 2) and not get_bool(data, 0, 1):  # Done & !Busy
                return True
            time.sleep(0.05)
        return False

    print(f"[开始] {len(POINTS)} 点, 速度 {VELOCITY}")
    try:
        for i, (x, y) in enumerate(POINTS):
            # ★ 关键：发点前确认 PLC 真正"空闲"，避免丢点
            if not wait_idle(timeout=5.0):
                print(f"  [警告] PLC 未空闲就写入点 {i}，可能丢点")
            
            write_point(x, y, VELOCITY, i)
            print(f"  [{i+1}/{len(POINTS)}] X={x:.1f} Y={y:.1f}", end=" ")
            if wait_done():
                print("✓")
            else:
                print("✗ 失败")
                break
        print("[完成]")
    except KeyboardInterrupt:
        print("\n[中断]")
    finally:
        data = plc.db_read(DB, 14, 1)
        set_bool(data, 0, 4, False)  # Disable
        plc.db_write(DB, 14, data)
        plc.disconnect()
        print("[断开]")

if __name__ == "__main__":
    run()

