#!/usr/bin/env python3
"""
考试项目 - 37点圆形轨迹
用法: python exam_trajectory.py
"""
import time
import snap7
from snap7.util import get_bool, set_bool, get_real, set_real, get_int, set_int

# ============ 配置（按实际修改）============
PLC_IP = "192.168.0.1"
DB = 200
VELOCITY = 50.0

# 考试项目轨迹点 (X, Y) - Point 0 到 Point 36
POINTS = [
    (591.3, 133.9),   # Point 0 (Start/End Point)
    (589.8, 151.3),   # Point 1
    (585.3, 168.1),   # Point 2
    (577.9, 183.9),   # Point 3
    (567.9, 198.2),   # Point 4
    (555.6, 210.5),   # Point 5
    (541.3, 220.5),   # Point 6
    (525.5, 227.9),   # Point 7
    (508.7, 232.4),   # Point 8
    (491.3, 233.9),   # Point 9
    (473.9, 232.4),   # Point 10
    (457.1, 227.9),   # Point 11
    (441.3, 220.5),   # Point 12
    (427.0, 210.5),   # Point 13
    (414.7, 198.2),   # Point 14
    (404.7, 183.9),   # Point 15
    (397.3, 168.1),   # Point 16
    (392.8, 151.3),   # Point 17
    (391.3, 133.9),   # Point 18
    (392.8, 116.5),   # Point 19
    (397.3, 99.7),    # Point 20
    (404.7, 83.9),    # Point 21
    (414.7, 69.6),    # Point 22
    (427.0, 57.3),    # Point 23
    (441.3, 47.3),    # Point 24
    (457.1, 39.9),    # Point 25
    (473.9, 35.4),    # Point 26
    (491.3, 33.9),    # Point 27
    (508.7, 35.4),    # Point 28
    (525.5, 39.9),    # Point 29
    (541.3, 47.3),    # Point 30
    (555.6, 57.3),    # Point 31
    (567.9, 69.6),    # Point 32
    (577.9, 83.9),    # Point 33
    (585.3, 99.7),    # Point 34
    (589.8, 116.5),   # Point 35
    (591.3, 133.9),   # Point 36 (same as Point 0 to complete the circle)
]

# ============ 核心函数 ============
def run():
    plc = snap7.client.Client()
    plc.connect(PLC_IP, 0, 1)
    print(f"[OK] 连接 {PLC_IP}")
    print(f"[考试项目] 共 {len(POINTS)} 个点")

    def write_point(x, y, v, idx):
        data = plc.db_read(DB, 0, 16)
        set_real(data, 0, x)
        set_real(data, 4, y)
        set_real(data, 8, v)
        set_int(data, 12, idx)
        set_bool(data, 14, 4, True)   # Enable
        set_bool(data, 14, 0, True)   # NewPoint
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

    print(f"[开始执行] 速度 {VELOCITY} mm/s")
    try:
        for i, (x, y) in enumerate(POINTS):
            write_point(x, y, VELOCITY, i)
            print(f"  [点 {i}/{len(POINTS)-1}] X={x:.1f} Y={y:.1f}", end=" ")
            if wait_done():
                print("✓")
            else:
                print("✗ 失败")
                break
        print("[考试项目完成]")
    except KeyboardInterrupt:
        print("\n[用户中断]")
    finally:
        data = plc.db_read(DB, 14, 1)
        set_bool(data, 0, 4, False)  # Disable
        plc.db_write(DB, 14, data)
        plc.disconnect()
        print("[已断开连接]")

if __name__ == "__main__":
    run()

