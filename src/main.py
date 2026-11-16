"""板端入口：AHT20/光敏采样先同步显示到 LCD，再经 EC200U 周期上报。"""

import time

import classroom
import environment
import screen
import uplink


def run():
    """每轮先刷新实测屏幕；云端不可用时继续采样并在下轮重连。"""
    import settings

    lcd = screen.open_screen()
    thermometer, light = environment.open_sensors()  # 只初始化一次，失败时不发布。
    network = None
    client = None
    last_clock_sync_ms = None           # 厂商 RTC 运行时可能漂移，记录上次 NTP 校时的单调时刻。
    while True:
        display = None                     # 本轮采样失败时不沿用上一轮旧值。
        try:
            readings = environment.read(thermometer, light)  # 同一组值供 LCD 和 MQTT 使用。
            display = {"people_count": None, "temperature_c": readings[0],
                       "humidity_pct": readings[1], "light_raw_u16": readings[2]}
            screen.show_snapshot(lcd, display, "4G MQTT: waiting")

            if network is None:
                network = uplink.attach_4g()
            if (last_clock_sync_ms is None or
                    time.ticks_diff(time.ticks_ms(), last_clock_sync_ms) >= 60_000):
                uplink.synchronize_utc(settings.NTP_HOST)
                last_clock_sync_ms = time.ticks_ms()  # 每分钟重新校时，避免网页误判为过期数据。
            if client is None:
                client = uplink.connect_mqtt(settings)

            seq, captured_at = uplink.utc_sample_time()
            snapshot = classroom.make_environment_snapshot(
                seq, captured_at, settings.DEVICE_ID, settings.ROOM_ID, readings)
            uplink.publish_snapshot(client, settings.MQTT_TOPIC,
                                    classroom.encode_snapshot(snapshot))
            screen.show_snapshot(lcd, snapshot, "4G MQTT: sent")
            print("PUBLISHED device_id=%s seq=%d temp=%.1f rh=%.1f adc=%d" %
                  (settings.DEVICE_ID, seq, readings[0], readings[1], readings[2]))
        except KeyboardInterrupt:
            break
        except Exception as error:
            print("UPLINK_ERROR:", error)
            if display is not None:
                screen.show_snapshot(lcd, display, "4G MQTT: retry")
            if client is not None:
                try:
                    client.disconnect()
                except Exception:
                    pass
                client = None
        time.sleep(settings.PUBLISH_INTERVAL_SECONDS)

    if client is not None:
        client.disconnect()
    if network is not None:
        network.deinit()


if __name__ == "__main__":
    run()
