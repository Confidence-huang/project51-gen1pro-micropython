"""生成可重复的教室模拟快照；字段直接匹配现有网页和历史服务。"""

import json


def make_snapshot(seq, captured_at, device_id, room_id):
    """seq 为可信 UTC 秒数；captured_at 必须由已校准时钟生成。"""
    if not isinstance(seq, int) or seq < 0:
        raise ValueError("seq must be a nonnegative integer")
    if not captured_at or not captured_at.endswith("Z"):
        raise ValueError("captured_at must be UTC ISO 8601")

    # 默认每 10 秒发一条，以 10 秒槽位变化，避免整十秒采样让温度固定。
    sample_step = seq // 10
    # 数值按槽位变化，方便对照 LCD、MQTT 和网页；它们不是传感器读数。
    return {
        "schema_version": 1,
        "type": "telemetry",
        "source": "stm32_micropython_sim",
        "simulated": True,
        "device_id": device_id,
        "room_id": room_id,
        "seq": seq,
        "captured_at": captured_at,
        "people_count": 2 + sample_step % 3,
        "temperature_c": round(23.5 + (sample_step % 5) * 0.4, 1),
        "humidity_pct": 44 + sample_step % 7,
        "light_lux": 280 + (sample_step % 9) * 20,
    }


def make_environment_snapshot(seq, captured_at, device_id, room_id, readings):
    """板载实测值沿用同一 MQTT 主题；未接 K230 和未标定 lx 都明确留空。"""
    if not isinstance(seq, int) or seq < 0 or not captured_at.endswith("Z"):
        raise ValueError("sample time must be synchronized UTC")
    temperature, humidity, light_raw = readings
    return {
        "schema_version": 1,                 # 与现有网页的消息版本一致。
        "type": "telemetry",                 # 只有遥测消息会刷新看板。
        "source": "stm32_micropython_aht20_ldr",
        "simulated": False,                  # 数值从板载器件读取。
        "device_id": device_id,
        "room_id": room_id,
        "seq": seq,
        "captured_at": captured_at,
        "people_count": None,                # K230 尚未接入，不能填模拟人数。
        "temperature_c": temperature,
        "humidity_pct": humidity,
        "light_lux": None,                  # 缺少板级标定，不能把 ADC 当 lx。
        "light_raw_u16": light_raw,          # 0~65535 的原始 ADC 码值。
    }


def encode_snapshot(snapshot):
    """MQTT 发布 UTF-8 JSON；保持与网站消费者的字段名完全一致。"""
    return json.dumps(snapshot).encode("utf-8")
