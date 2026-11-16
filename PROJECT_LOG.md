# Gen1 Pro MicroPython 项目日志

## 当前快照

- 项目：NUCLEO-F413ZH + UniKnect Gen1 Pro 的板端模拟四项遥测。
- 固件：官方 F413ZH MicroPython ELF 候选保存在上级项目 `work/`，本仓库不含固件。用户截图显示 STM32CubeProgrammer 下载验证成功，但所选文件名未完整显示；板端 REPL 仍未验收。
- 代码：`src/main.py` 调度 LCD、4G、NTP、TLS/MQTT；`src/classroom.py` 定义 JSON 契约。
- 验证：Python 3.12 环境的三项单元测试、本工程及官方 LCD 示例的主机语法检查通过；VS Code 专用配置文件中的 Python/Pylance 扩展安装成功。板端串口与例程运行尚未验证。
- Git：第 1 次 git `8abbe34b7071bbbd66109c9cebb713ad73f42161`，初始板端源码、模板、测试和说明。
- 安全：设备账号与根 CA 仅存本地忽略文件；不复制组长程序。
- 下一步：在 VS Code 专用工作区中确认 ST-LINK 虚拟串口、MicroPython 版本与 `/flash`，再逐段验 LCD、4G、NTP、TLS/MQTT、网页。

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

- 2026-11-16：为本工程建立 VS Code 专用工作区和配置文件，接入 Python 3.12、锁定 mpremote 1.29.0，配置语法检查、数据测试及板端串口任务。电脑端 3 项测试和两份脚本语法检查通过；Python/Pylance 在专用配置文件安装并列出。未执行实板串口任务或上传，REPL 状态待验。
- 2026-11-15：创建独立源码工程，记录第 1 次 git；电脑端三项载荷测试与语法编译通过。板端和云端验收尚未执行。
