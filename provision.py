"""经 ST-LINK 串口把设备运行配置写入 /flash，不在电脑磁盘保存 MQTT 密码。

调用示例：uv run python provision.py --port COM15 --user classroom_test
程序只接受交互输入；已有 settings.py 时拒绝覆盖，避免误改别的设备配置。
"""

import argparse
import getpass
import hashlib

from mpremote.transport_serial import SerialTransport


def main():
    """确认 F413ZH 身份后写入配置，并在板端比对内容散列。"""
    parser = argparse.ArgumentParser(description="Provision Gen1 Pro MQTT settings on the board")
    parser.add_argument("--port", required=True, help="ST-LINK VCP port from Device Manager")
    parser.add_argument("--user", required=True, help="EMQX device publisher username")
    parser.add_argument("--host", default="i1103de1.ala.cn-hangzhou.emqxsl.cn")
    args = parser.parse_args()

    board = SerialTransport(args.port)           # 密码只经当前串口送往板端。
    try:
        board.enter_raw_repl()                   # 不改写 STM32 固件。
        machine = board.eval("__import__('os').uname().machine")
        if "NUCLEO-F413ZH" not in machine:
            raise RuntimeError("connected board is not NUCLEO-F413ZH")
        if board.eval("'settings.py' in __import__('os').listdir('/flash')"):
            raise RuntimeError("board settings.py already exists; no overwrite")
        print("BOARD_ID_OK")                    # 不打印设备序列号或账号密码。

        password = getpass.getpass("MQTT password (hidden): ")
        if not password:
            raise RuntimeError("empty MQTT password")
        lines = [
            '"""Local board-only MQTT configuration. Do not copy into Git."""',
            f"MQTT_HOST = {args.host!r}",
            "MQTT_PORT = 8883",
            f"MQTT_USER = {args.user!r}",
            f"MQTT_PASSWORD = {password!r}",
            "MQTT_CA_PATH = '/flash/mqtt_ca.pem'",
            "MQTT_TOPIC = 'classroom/room01/telemetry'",
            "ROOM_ID = 'room01'",
            "DEVICE_ID = 'f413zh-gen1pro-01'",
            "NTP_HOST = 'pool.ntp.org'",
            "PUBLISH_INTERVAL_SECONDS = 10",
        ]
        payload = ("\n".join(lines) + "\n").encode("utf-8")
        password = None                         # 后续只保留待写入的配置字节。
        board.fs_writefile("/flash/settings.py", payload)
        matched = board.fs_hashfile("/flash/settings.py", "sha256") == hashlib.sha256(payload).digest()
        if not matched:
            board.fs_rmfile("/flash/settings.py")
            raise RuntimeError("board settings verification failed")
        print("BOARD_SETTINGS_WRITTEN")
    finally:
        board.exit_raw_repl()                   # 恢复友好 REPL，交还 VS Code 串口。
        board.close()


if __name__ == "__main__":
    main()
