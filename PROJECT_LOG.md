# Gen1 Pro MicroPython 项目日志

## 当前快照

- 项目：NUCLEO-F413ZH + UniKnect Gen1 Pro 的板端模拟四项遥测。
- 固件：官方 F413ZH MicroPython ELF 候选保存在上级项目 `work/`，本仓库不含固件。板端 COM15 已返回 `micropython` 1.27.0 preview，机器标识 `NUCLEO-F413ZH with STM32F413`；所选 ELF 文件名在原烧录截图中未完整显示。
- 代码：`src/main.py` 调度 LCD、4G、NTP、TLS/MQTT；`src/classroom.py` 定义 JSON 契约。
- 验证：Python 3.12 环境的三项单元测试、本工程及官方 LCD 示例的主机语法检查通过；VS Code 专用配置文件中的 Python/Pylance 扩展安装成功。实板 `mpremote` 可进入 raw REPL，`/flash` 中有 `boot.py`、`main.py`，LCD/Network/MQTT/TLS 模块导入通过；LCD 图像、联网与上报尚未验收。
- Git：第 3 次 git `e06e70c00f5c366085353caaf7747db48c5dfb49`，VS Code 工作区配置；本次板端检查的日志提交编号以 Git 现查为准。
- 安全：设备账号与根 CA 仅存本地忽略文件；不复制组长程序。
- 下一步：先临时运行官方 `modules/lcd/lcd1/lcd1.py` 验证屏幕显示，再逐段验本工程四项布局、4G、NTP、TLS/MQTT、网页。不要运行带示例 MQTT 凭据的 `examples/application.py`。

## 关键文件索引

- `README.md`：环境、配置和实板验证顺序。
- `src/settings.example.py`：无秘密配置模板。
- `src/classroom.py`：模拟载荷及编码。
- `src/screen.py`：LCD 四项布局。
- `src/uplink.py`：4G、NTP、TLS 和 MQTT。
- `src/main.py`：板端运行入口。
- `tests/test_payload.py`：电脑端契约测试。
- `移远杯-MicroPython.code-workspace`：VS Code 双根工作区与语法、测试、串口、REPL 任务。
- `check_syntax.py`：不运行板端代码的主机语法检查。

## 近期任务记录

- 2026-11-16：用户 VS Code 截图证实 `mpremote` 经 COM15 返回 MicroPython 1.27.0 preview 与 NUCLEO-F413ZH 机器标识；本机只读 `fs ls` 及 `os.listdir('/flash')` 见 `boot.py`、`main.py`，`st7735.LCD`、`quectel.Network`、`umqtt.robust.MQTTClient`、`tls` 导入均成功。EC200U AT COM18 当前也已枚举。未运行 LCD 例程、上传文件或联网发布，下一步屏幕最小验收。
- 2026-11-16：为本工程建立 VS Code 专用工作区和配置文件，接入 Python 3.12、锁定 mpremote 1.29.0，配置语法检查、数据测试及板端串口任务。电脑端 3 项测试和两份脚本语法检查通过；Python/Pylance 在专用配置文件安装并列出。未执行实板串口任务或上传，REPL 状态待验。
- 2026-11-15：创建独立源码工程，记录第 1 次 git；电脑端三项载荷测试与语法编译通过。板端和云端验收尚未执行。
