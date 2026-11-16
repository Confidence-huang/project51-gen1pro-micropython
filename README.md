# Gen1 Pro 智慧教室板端 MicroPython

本仓库只保存新写的板端模拟遥测程序。目标硬件为 NUCLEO-F413ZH、UniKnect Gen1 Pro EC200U 扩展板及官方 160×128 ST7735S LCD。未接 K230 和环境传感器时，人数、温度、湿度、照度均为**模拟值**。程序不会上报 CO₂。组长的 C 工程、固件和相关文件均未复制到本仓库。

## 文件与数据流

`src/main.py` 触发周期采样；`src/classroom.py` 生成四项模拟数据与 JSON；`src/screen.py` 在 LCD 同屏显示；`src/uplink.py` 经 EC200U/4G、NTP、TLS 与 MQTT 发布。`src/settings.example.py` 是不含秘密的配置模板。设备 `/flash` 中的 `settings.py` 和根 CA 必须独立放置，且不得提交 Git。

发布到 `classroom/room01/telemetry`，MQTT 3.1.1 over TLS，端口 8883，QoS 1。载荷示例：

```json
{"schema_version":1,"type":"telemetry","source":"stm32_micropython_sim","simulated":true,"device_id":"f413zh-gen1pro-01","room_id":"room01","seq":1794729600,"captured_at":"2026-11-15T08:00:00Z","people_count":2,"temperature_c":23.5,"humidity_pct":44,"light_lux":280}
```

`seq` 为已校准 UTC 时钟的秒数。刷新间隔至少 2 秒，以免重复。程序从 NTP 同步 RTC；若同步失败、CA 缺失或证书校验失败，不发布带假时间的消息。屏幕会显示重试提示，串口打印 `UPLINK_ERROR`，不会打印密码。

## 电脑环境与静态验证

- VS Code 1.146.0 可作为日常主 IDE。打开本仓库的 `移远杯-MicroPython.code-workspace`，选择专用配置文件“移远杯-MicroPython”。左侧同时显示本工程和官方仓库；官方例程只作参考，不需要另装仓库中推荐的 Thonny 才能编辑本工程。
- 本工程用 `uv` 固定 Python 3.12 环境，`uv.lock` 当前锁定 `mpremote` 1.29.0。首次打开先在本目录运行 `uv sync`。VS Code 安装 Python 与 Pylance 扩展后，解释器选本目录 `.venv/Scripts/python.exe`。
- 在 VS Code 中打开一个 `.py`，按 **Ctrl+Shift+B** 执行“MicroPython：检查当前文件语法”；也可在“终端 → 运行任务”中执行“电脑：运行数据契约测试”。这些任务检查脚本，不会连接或改写开发板。官方例程同样可以用语法检查任务检查。
- 需要实板时，先退出 STM32CubeProgrammer 的连接、按 NUCLEO 的 RESET，并确认设备管理器中的 ST-LINK 虚拟串口号。在“终端 → 运行任务”依次执行“板端：列出串口”“板端：读取 MicroPython 版本”“板端：列出文件”。只有得到版本和文件列表后才运行当前脚本或上传；默认 COM15 只是上次发现值，每次以当前枚举为准。
- “板端：运行当前脚本（不上传）”通过串口临时运行打开的文件；“板端：上传当前脚本（写入设备）”会提示设备目标路径，须先确认 `/flash` 存在和目标文件名，避免覆盖板上自启 `main.py`。REPL 任务可代替 Thonny 的 Shell。VS Code 终端若报端口被占用，先关闭 CubeProgrammer、Thonny 或其他串口终端。
- 官方 `.py` 例程由板上 MicroPython 解释器执行，电脑上的语法检查不是 STM32 固件编译，也不能验证厂商模块是否存在。STM32CubeProgrammer 仍负责官方 ELF 固件的烧录与校验。暂不生成 `.mpy`，需先读取板端固件的 `sys.implementation._mpy` 并确认交叉编译器版本。
- Windows 11 x64；Thonny 4.1.7（自带 Python 3.10），Thonny 解释器选 **MicroPython (generic)**，端口选择现场实际枚举的 **STMicroelectronics STLink Virtual COM Port**。
- STM32CubeProgrammer 2.23.0 Windows x64 用于将官方 F413ZH ELF 烧录并 Verify。固件候选在项目的 `work/UniKnect_官方固件候选_v1.2.0/`，SHA256 见上级项目实施方案。烧录须先在 GUI 确认目标芯片确为 F413ZH；本仓库不含固件副本。
- 在本目录运行 `pwsh -NoProfile -Command "& '$env:LOCALAPPDATA\Programs\Thonny\python.exe' -m unittest discover -s tests -v"`。这仅验证 JSON 契约，不代表板端联网通过。

## 板端分阶段操作

1. 接好 ST-LINK USB、EC200U 扩展板电源、MAIN 蜂窝天线并打开 S201；S501 选已开通的 eSIM。电脑端分别确认 ST-LINK VCP 与 EC200U 端口，不能依赖旧 COM 编号。
2. 用户已提供 STM32CubeProgrammer 显示“下载验证成功”的截图；所选文件名在截图中未完整显示，故仍须用 VS Code 的版本任务或 Thonny Shell 确认 MicroPython 提示符和 `/flash`。不要执行全片擦除、解锁、Option Bytes 更改或 ST-LINK 固件升级。
3. 在 REPL 先单独验证 `from st7735 import LCD`、`from quectel import Network`、`from umqtt.robust import MQTTClient`、`import tls`。先运行官方 LCD 最小示例，确认 SPI1、F12、D14 与屏幕实际连线一致。再验证 `Network.init()`/`attach()` 可以联网。
4. 复制 `src/settings.example.py` 到电脑本地 `src/settings.py`，填写 EMQX **设备专用发布账号**、实例公网域名和端口 8883；勿用网页只读账号。把与 EMQX 服务器证书链匹配的**根 CA PEM**保存为本地 `src/mqtt_ca.pem`。CA 必须与当前实例实际证书核对，不能直接拿上游示例证书冒充。
5. 用 VS Code 的上传任务逐个将 `classroom.py`、`screen.py`、`uplink.py`、`settings.py`、`mqtt_ca.pem` 复制到设备 `/flash`；先从电脑打开 `main.py`，执行“板端：运行当前脚本（不上传）”，核对屏幕四行和 REPL `PUBLISHED device_id=... seq=...`。确认后才把 `main.py` 复制到 `/flash` 实现自启。若厂商固件不支持 mpremote 的 raw REPL，可用 Thonny 作为兼容备用入口。
6. 在 EMQX 在线调试订阅同一主题，核对 JSON、`simulated:true`、`device_id+seq` 和 UTC 时间；在网页设置中连接同一 EMQX 实例，核对相同序号与四项数值。断网重连、断电重启分别复验。电脑测试脚本或 EMQX 控制台手动发布，不算板端通过。

## 当前验收边界

源码与电脑单元测试只能确认 JSON 字段、数值和屏幕布局逻辑。固件、屏幕引脚、NTP/RTC、TLS 库参数、CA 链、4G 注册、MQTT QoS 1 回执与网页实收均需在实板上逐段核验。固件 API 若与仓库例程有差异，先以 REPL 输出定位具体环节，再修改该层。

上游参考：移远官方 `https://github.com/quectel-develop/uniknect-micropython` 的 LCD、Network、`umqtt.robust`、`tls.SSLContext` 示例；源码未复制其测试账号或固定密码。
