"""读取 Gen1 Pro 板载 AHT20 和光敏电阻；光敏值保留 ADC 原码，不冒充 lx。"""


def open_sensors():
    """S502 指向 MCU 时，I2C1 上的 0x38 应为 AHT20；PC5 接光敏分压。"""
    import machine
    from ahtx0 import AHT20

    bus = machine.I2C(1, freq=100000)       # 官方温湿度例程使用 I2C1。
    if 0x38 not in bus.scan():               # 未接通传感器时拒绝生成假读数。
        raise RuntimeError("AHT20 not found on I2C1")
    thermometer = AHT20(bus)                 # 传感器对象负责读温湿度。
    light = machine.ADC(machine.Pin("C5"))   # 官方光敏例程使用 PC5 的 ADC。
    return thermometer, light


def read(thermometer, light):
    """一次采样返回温度、湿度和光敏 ADC；原始值在各显示端保持一致。"""
    temperature = round(thermometer.temperature, 1)
    humidity = round(thermometer.relative_humidity, 1)
    light_raw = light.read_u16()
    if not (-40 <= temperature <= 85 and 0 <= humidity <= 100 and 0 <= light_raw <= 65535):
        raise RuntimeError("environment reading outside sensor range")
    return temperature, humidity, light_raw
