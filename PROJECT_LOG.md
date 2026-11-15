# Gen1 Pro MicroPython 项目日志

## 当前快照

- 项目：NUCLEO-F413ZH + UniKnect Gen1 Pro 的板端模拟四项遥测。
- 固件：官方 F413ZH MicroPython ELF 候选保存在上级项目 `work/`，本仓库不含固件；尚未烧录。
- 代码：`src/main.py` 调度 LCD、4G、NTP、TLS/MQTT；`src/classroom.py` 定义 JSON 契约。
- 验证：电脑端 `python -m unittest discover -s tests -v` 三项通过；实板各环节尚未验证。
- 安全：设备账号与根 CA 仅存本地忽略文件；不复制组长程序。
- 下一步：确认 ST-LINK 和目标芯片后由用户烧录官方 ELF；用 Thonny 逐段验 REPL、LCD、4G、NTP、TLS/MQTT、网页。

## 关键文件索引

- `README.md`：环境、配置和实板验证顺序。
- `src/settings.example.py`：无秘密配置模板。
- `src/classroom.py`：模拟载荷及编码。
- `src/screen.py`：LCD 四项布局。
- `src/uplink.py`：4G、NTP、TLS 和 MQTT。
- `src/main.py`：板端运行入口。
- `tests/test_payload.py`：电脑端契约测试。

## 近期任务记录

- 2026-11-15：创建独立源码工程；电脑端三项载荷测试与语法编译通过。板端和云端验收尚未执行。
