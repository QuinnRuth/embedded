import snap7

PLC_IP = "192.168.0.1"  # 改成你的 PLC IP
DB_NUM = 200             # 我们期望的 DB 号

def main():
    client = snap7.client.Client()
    client.connect(PLC_IP, 0, 1)
    print("[OK] 已连接")

    # 读 DB200 前 16 个字节
    try:
        data = client.db_read(DB_NUM, 0, 16)
        print("DB200 前16字节:", data)
    except Exception as e:
        print("读 DB200 出错:", repr(e))

    client.disconnect()
    print("[OK] 已断开")

if __name__ == "__main__":
    main()