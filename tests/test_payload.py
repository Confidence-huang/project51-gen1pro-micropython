"""在电脑上验证板端 JSON 契约；不需要实板、密码或云连接。"""

import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
import classroom


class ClassroomPayloadTests(unittest.TestCase):
    def test_four_simulated_readings_match_dashboard_contract(self):
        snapshot = classroom.make_snapshot(123, "2026-11-15T08:00:00Z",
                                           "f413zh-gen1pro-01", "room01")
        decoded = json.loads(classroom.encode_snapshot(snapshot))
        self.assertEqual(decoded["type"], "telemetry")
        self.assertEqual(decoded["source"], "stm32_micropython_sim")
        self.assertIs(decoded["simulated"], True)
        self.assertEqual(decoded["seq"], 123)
        self.assertEqual(decoded["captured_at"], "2026-11-15T08:00:00Z")
        for field in ("people_count", "temperature_c", "humidity_pct", "light_lux"):
            self.assertIsInstance(decoded[field], (int, float))
        self.assertNotIn("co2", decoded)

    def test_invalid_sequence_and_time_are_rejected(self):
        for seq, stamp in ((-1, "2026-11-15T08:00:00Z"),
                           (1, ""), (1, "2026-11-15T08:00:00+08:00")):
            with self.assertRaises(ValueError):
                classroom.make_snapshot(seq, stamp, "device", "room01")

    def test_default_interval_changes_each_simulated_reading(self):
        first = classroom.make_snapshot(120, "2026-11-15T08:00:00Z", "d", "room01")
        second = classroom.make_snapshot(130, "2026-11-15T08:00:10Z", "d", "room01")
        for field in ("people_count", "temperature_c", "humidity_pct", "light_lux"):
            self.assertNotEqual(first[field], second[field])

    def test_real_environment_keeps_uncalibrated_light_and_missing_people_explicit(self):
        snapshot = classroom.make_environment_snapshot(
            145, "2026-11-16T07:00:00Z", "f413zh-gen1pro-01", "room01", (25.2, 49.4, 22917))
        decoded = json.loads(classroom.encode_snapshot(snapshot))
        self.assertIs(decoded["simulated"], False)
        self.assertIsNone(decoded["people_count"])
        self.assertIsNone(decoded["light_lux"])
        self.assertEqual(decoded["light_raw_u16"], 22917)
        self.assertEqual(decoded["temperature_c"], 25.2)


if __name__ == "__main__":
    unittest.main()
