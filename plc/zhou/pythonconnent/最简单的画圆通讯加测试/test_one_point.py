import time
import snap7
from snap7.util import set_real, set_int, set_bool, get_bool

PLC_IP = "192.168.0.1"  # 改你的 IP
DB = 200

def main():
    client = snap7.client.Client()
    client.connect(PLC_IP, 0, 1)
    print(f"[OK] 连接 {PLC_IP}")

    # 1. 写入目标数据：X=600.0, Y=100.0, V=50.0
    # -------------------------------------------------------
    data = client.db_read(DB, 0, 16)
    set_real(data, 0, 000)      # X_Setpoint
    set_real(data, 4, 50.0)       # Y_Setpoint
    set_real(data, 8, 50.0)       # Velocity
    set_int(data, 12, 1)          # PointIndex = 1
    set_bool(data, 14, 4, True)   # Enable = TRUE
    set_bool(data, 14, 0, True)   # NewPoint = TRUE
    
    client.db_write(DB, 0, data)
    print("[发送] 目标 X=100.0 Y=50.0 (Enable=1, NewPoint=1)")

    # 2. 循环监控 PLC 反馈 (Busy -> Done)
    # -------------------------------------------------------
    print("[监控] 等待 PLC 响应...")
    for _ in range(200):  # 最多等 10秒 (200 * 0.05s)
        try:
            # 只读第14字节状态位
            status_byte = client.db_read(DB, 14, 1)
            busy = get_bool(status_byte, 0, 1)  # bit 1
            done = get_bool(status_byte, 0, 2)  # bit 2
            error = get_bool(status_byte, 0, 3) # bit 3
            
            # 打印状态变化
            if error:
                print(" -> [ERROR] PLC 报错！停止。")
                break
            
            if busy:
                print(" -> [Busy] 正在运动...", end="\r", flush=True)
            
            if done and not busy:
                print("\n -> [Done] 到位完成！")
                
                # 清除 Enable 和 NewPoint，结束测试
                status_byte = client.db_read(DB, 14, 1)
                set_bool(status_byte, 0, 4, False) # Enable=0
                set_bool(status_byte, 0, 0, False) # NewPoint=0
                client.db_write(DB, 14, status_byte)
                print("[结束] 已复位 Enable=0")
                break
                
        except Exception as e:
            print(f"\n读失败: {e}")
            break
            
        time.sleep(0.05)
    
    client.disconnect()

if __name__ == "__main__":
    main()

