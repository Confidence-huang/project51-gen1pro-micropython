"""板端入口：LCD 显示模拟快照，4G 接入后按固定周期向 EMQX 发布。"""

import time

import classroom
import screen
import uplink


def run():
    """连接失败时保留屏幕提示并重试；Ctrl+C 可从 Thonny 安全中断。"""
    import settings

    lcd = screen.open_screen()
    network = None
    client = None
    while True:
        try:
            if network is None:
                network = uplink.attach_4g()
            if client is None:
                uplink.synchronize_utc(settings.NTP_HOST)
                client = uplink.connect_mqtt(settings)

            seq, captured_at = uplink.utc_sample_time()
            snapshot = classroom.make_snapshot(seq, captured_at,
                                               settings.DEVICE_ID, settings.ROOM_ID)
            screen.show_snapshot(lcd, snapshot, "4G MQTT: connected")
            uplink.publish_snapshot(client, settings.MQTT_TOPIC,
                                    classroom.encode_snapshot(snapshot))
            print("PUBLISHED device_id=%s seq=%d" % (settings.DEVICE_ID, seq))
            time.sleep(settings.PUBLISH_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            break
        except Exception as error:
            print("UPLINK_ERROR:", error)
            lcd.fill_screen(lcd.BLACK)
            lcd.show_string(4, 8, "SIM / uplink retry", lcd.YELLOW, lcd.BLACK, 16)
            lcd.flush()
            if client is not None:
                try:
                    client.disconnect()
                except Exception:
                    pass
                client = None
            time.sleep(10)

    if client is not None:
        client.disconnect()
    if network is not None:
        network.deinit()


if __name__ == "__main__":
    run()
