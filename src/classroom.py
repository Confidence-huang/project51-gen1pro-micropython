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


def encode_snapshot(snapshot):
    """MQTT 发布 UTF-8 JSON；保持与网站消费者的字段名完全一致。"""
    return json.dumps(snapshot).encode("utf-8")
