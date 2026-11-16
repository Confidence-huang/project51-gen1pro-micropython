# Gen1 Pro MicroPython 项目日志

## 当前快照

- 项目：NUCLEO-F413ZH + UniKnect Gen1 Pro 的板端模拟四项遥测。
- 固件：官方 F413ZH MicroPython ELF 候选保存在上级项目 `work/`，本仓库不含固件。板端 COM15 已返回 `micropython` 1.27.0 preview，机器标识 `NUCLEO-F413ZH with STM32F413`；所选 ELF 文件名在原烧录截图中未完整显示。
- 代码：`src/main.py` 调度 LCD、4G、NTP、TLS/MQTT；`src/classroom.py` 定义 JSON 契约。
- 验证：Python 3.12 环境的三项单元测试和本工程语法检查通过；实板 `mpremote` 可进入 raw REPL，LCD/Network/MQTT/TLS 模块导入通过。用户确认官方 LCD 例程正常；本工程 `src/screen.py` 四项布局目视通过。`src/cellular_check.py` 临时运行返回 `CELLULAR_ATTACH_OK` 和 `CELLULAR_DNS_OK`，证明 STM32→EC200U 附着及 DNS 解析通过；NTP、MQTT、网站自主上报尚未验收。
- Git：第 3 次 git `e06e70c00f5c366085353caaf7747db48c5dfb49`，VS Code 工作区配置；本次板端检查的日志提交编号以 Git 现查为准。
- 安全：设备账号与根 CA 仅存本地忽略文件；不复制组长程序。
- 下一步：单独验证板端 UTC/NTP，再逐段验 TLS/MQTT、网页。不要运行带示例 MQTT 凭据的 `examples/application.py`。

## 关键文件索引

- `README.md`：环境、配置和实板验证顺序。
- `src/settings.example.py`：无秘密配置模板。
- `src/classroom.py`：模拟载荷及编码。
- `src/screen.py`：LCD 四项布局。
- `src/uplink.py`：4G、NTP、TLS 和 MQTT。
- `src/main.py`：板端运行入口。
- `src/cellular_check.py`：不使用账号的 4G 附着与 DNS 最小测试。
- `tests/test_payload.py`：电脑端契约测试。
- `移远杯-MicroPython.code-workspace`：VS Code 双根工作区与语法、测试、串口、REPL 任务。
- `check_syntax.py`：不运行板端代码的主机语法检查。

## 近期任务记录

- 2026-11-16：增加 `src/cellular_check.py`，依照官方 Network 示例对 EC200U 执行初始化、USIM 检查、4G 附着及 `example.com` DNS 查询。首次发现固件不提供标准名 `socket`，按官方 `modules/socket/udp.py` 用 `usocket as socket` 修正检查脚本及 `src/uplink.py`；实板重试返回 `CELLULAR_ATTACH_OK`、`CELLULAR_DNS_OK`，模组底层有 IPv6 `inet_pton` 报错但 IPv4 DNS 查询完成。未验证 NTP、TLS/MQTT 或网页。
- 2026-11-16：用户确认官方 LCD 最小例程运行正常。发现该无限循环任务仍占用 COM15，精确停止其 `uv/mpremote/python` 进程后，本工程 `src/screen.py` 增加单次模拟布局入口；主机语法检查、3 项既有单测通过，`mpremote run src/screen.py` 返回 `SCREEN_DEMO_DRAWN people=3 temp=24.3 humidity=47 light=320`，用户目视确认四项清晰且无重叠。没有上传脚本、写入固件或连接网络。
- 2026-11-16：用户 VS Code 截图证实 `mpremote` 经 COM15 返回 MicroPython 1.27.0 preview 与 NUCLEO-F413ZH 机器标识；本机只读 `fs ls` 及 `os.listdir('/flash')` 见 `boot.py`、`main.py`，`st7735.LCD`、`quectel.Network`、`umqtt.robust.MQTTClient`、`tls` 导入均成功。EC200U AT COM18 当前也已枚举。未运行 LCD 例程、上传文件或联网发布，下一步屏幕最小验收。
- 2026-11-16：为本工程建立 VS Code 专用工作区和配置文件，接入 Python 3.12、锁定 mpremote 1.29.0，配置语法检查、数据测试及板端串口任务。电脑端 3 项测试和两份脚本语法检查通过；Python/Pylance 在专用配置文件安装并列出。未执行实板串口任务或上传，REPL 状态待验。
- 2026-11-15：创建独立源码工程，记录第 1 次 git；电脑端三项载荷测试与语法编译通过。板端和云端验收尚未执行。
