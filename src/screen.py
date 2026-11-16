"""按移远官方 SPI1/F12/D14 接法在 160×128 屏上显示同一快照。"""


def open_screen():
    """延迟导入板端模块，使载荷逻辑能在电脑单独测试。"""
    import machine
    from st7735 import LCD

    spi = machine.SPI(1, baudrate=10000000, polarity=0, phase=0)
    lcd = LCD(spi, dc_pin="F12", cs_pin="D14")
    lcd.set_rotation(1)
    return lcd


def show_snapshot(lcd, snapshot, link_status):
    """每次全屏重画；无 K230 时人数留空，光敏原码明确标 ADC。"""
    real_environment = snapshot.get("light_raw_u16") is not None
    people = "--" if snapshot["people_count"] is None else str(snapshot["people_count"])
    light = ("Light ADC: %d" % snapshot["light_raw_u16"] if real_environment
             else "Light: %d lx" % snapshot["light_lux"])
    lcd.fill_screen(lcd.BLACK)
    lcd.show_string(4, 2, "CLASSROOM  %s" % ("ENV" if real_environment else "SIM"), lcd.CYAN, lcd.BLACK, 16)
    lcd.show_string(4, 24, "People: %s" % people, lcd.WHITE, lcd.BLACK, 16)
    lcd.show_string(4, 46, "Temp: %.1f C" % snapshot["temperature_c"], lcd.WHITE, lcd.BLACK, 16)
    lcd.show_string(4, 68, "RH: %.1f %%" % snapshot["humidity_pct"], lcd.WHITE, lcd.BLACK, 16)
    lcd.show_string(4, 90, light, lcd.WHITE, lcd.BLACK, 16)
    lcd.show_string(4, 112, link_status[:19], lcd.YELLOW, lcd.BLACK, 12)
    lcd.flush()


if __name__ == "__main__":
    # 电脑通过 mpremote run 临时执行本文件时，只检查四项排版。
    # 固定模拟值便于与屏幕逐项对照；这里不读取传感器或连接网络。
    demo_snapshot = {
        "people_count": 3,
        "temperature_c": 24.3,
        "humidity_pct": 47,
        "light_lux": 320,
    }
    demo_lcd = open_screen()
    show_snapshot(demo_lcd, demo_snapshot, "DISPLAY TEST")
    print("SCREEN_DEMO_DRAWN people=3 temp=24.3 humidity=47 light=320")
