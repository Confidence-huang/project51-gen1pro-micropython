# EcoVision STM32 / EC200U 模块检查记录

## 2026-11-17 复核组长联调包

来源：`D:\移远杯项目文档\hjw works\移远杯_组长联调包_2026-11-16\移远杯_组长联调包_2026-11-16`。已查阅包内 `README_先看.md`、板端 `README.md`、`src/main.py` 和 `src/uplink.py` 的发布路径，并查看 `04_模拟与验收/验收截图/` 的两张照片。

- **已有板端验证记录。** 官方 UniKnect MicroPython 在 NUCLEO-F413ZH 上读取板载 AHT20 和 PC5 光敏 ADC，ST7735S LCD 显示实测值。包内记录 STM32 经 EC200U 真实 4G 访问 EMQX，完成 NTP、CA 校验 TLS 和 MQTT QoS 1 发布。网页截图有 `simulated:false` 的板端遥测，LCD 和网页截图拍摄时刻不同。包内未见原始串口或 Broker 日志，本轮未在实板重新执行这些步骤。USB AT 口回显与 LTE 注册另有本模块当日直接查询记录。
- **本轮软件验证。** 对联调包 `01_STM32板端工程_已验证/tests` 运行 `python -B -m unittest discover -s <测试目录> -v`，4 项通过。测试覆盖联调包的载荷约定。
- **与公共接口对接。** 联调包使用 `classroom/room01/telemetry`、独立 JSON 字段、约 10–12 秒发布及 retain=true；EcoVision 1.0.0 要求 `ecovision/{device_id}/telemetry`、正式字段、5 秒周期、retain=false。组长版是现成的实测联网基线，旧 C/HAL 工程的构建验收单独记录。须由总控确定合入路线，外部联调包和公共接口均未修改。
- **下一步补链路。** K230 人数握手、5V 风扇与 LED 控制、授权下行和 ACK、断网恢复及断电自启仍待验证。优先复用已有 4G 和 LCD 记录，用正式契约验证新增闭环。

## 2026-11-17 实物与 USB 枚举

- 用户照片可读到模组丝印 `EC200U-CN`。载板的 Arduino 排针、J401、J201、J308 与 UniKnect Gen1 Pro 布局相符。载板完整版本和 J308 对应针号未从照片独立确认。照片中 USB 线接在 J401，天线接在 MAIN_ANT。
- 第三张照片显示 NUCLEO、EC200U 载板与 LCD 已叠插，LCD 显示 `25.2 C`、`52.9 %`、`Light ADC: 15203`、`People: --` 和 `4G MQTT: waiting`。已观察到屏幕亮起并显示界面。温湿度来源、人数串口、注册及 MQTT 状态仍需通过日志确认。
- CubeProgrammer v2.22.0 枚举到 `STMicroelectronics STLink Virtual COM Port (COM4)`，调试器枚举仍报告 `No ST-Link detected`。Windows PnP 的 `ST-Link Debug` 状态为 Started。VCP 与 SWD 单独验收。
- `pnputil /enum-devices /connected /ids` 检测到 Quectel USB 复合设备 `VID_2C7C&PID_0901`。多个 `Mobile Generic Serial` 子接口报 Code 28，当前无 Quectel USB AT COM 口。参赛资料的 `03_官方入口/开发资料/01_驱动与串口` 内找到 `EC200U模组驱动_Quectel_Windows_USB_DriverU_V1.0.19-1.zip`，包内列出 `setup.exe`，尚未安装或验证兼容性。
- 后续已执行移远 U 系列驱动安装。安装程序返回 0，SetupAPI 记录 `qcser.inf` 注册为 `oem126.inf`，其中 `USB\VID_2C7C&PID_0901&MI_02` 映射到 `Quectel USB AT Port`。
- 用户拔插后重新核对。Windows 只在断开设备清单中保留移远 USB 记录。管理员 `pnputil /scan-devices` 退出 0，仍只有 COM4、COM7、COM8。下一步核对 EC200U 供电和 J401 数据链路，待设备重新枚举后读取 `AT`、`ATI`、`AT+CGMR`、`AT+CPIN?`、`AT+CEREG?`。AT 和 4G 待实测。
- 换 USB 口后复现 Windows 兼容性提示。SetupAPI 确认旧过滤驱动 `qew_usbenumfilter.sys`（`oem123.inf`）导致 EC200U USB 复合设备 Code 39。卸载该过滤包并扫描后，`oem126.inf` 保留，`Quectel USB AT Port (COM10)` 出现。未更改 Windows 安全设置。
- 本轮使用 COM10 以 115200、8N1 完成只读查询。`AT` 返回 `OK`，`ATI` 与 `AT+CGMR` 确认固件 `EC200UCNAAR03A17M08`，`AT+CPIN?` 返回 `READY`，`AT+CEREG?` 返回 `0,1`，确认 LTE 归属网注册。下一步验证数据连接、MQTT TLS 与 STM32 主 UART。

## 2026-11-16 联调基线

本节更新下方 11 月 12 日的工程和载板盘点。已在 `D:\移远杯项目文档\dsh work\stm32\EcoVision_F413ZH` 找到现有 CubeMX / Keil HAL 工程。`.uvprojx` 的目标为 STM32F413ZHTx，已有 AHT20、USART3 日志、MQ-135 和舵机代码。`.ioc` 目前仅配置 USART3，K230 和 EC200U 串口均待接入。原工程的 AHT20 读取约阻塞 80 ms，接入并发串口后需将采样等待从控制循环中分离。

本机运行 `D:\k51\ARM\ARMCLANG\Bin\armclang.exe --version` 返回 MDK Plus 5.36、ARM Compiler 6.16。原工程留有 HEX 和同版本构建日志，历史结果为 0 错误、83 警告。用工程临时副本执行两次 Keil `UV4.exe -r`，均退出 2，结果为 1 错误、83 警告、`Target not created`。日志定位到 `armclang` 启动 `armasm.exe` 时 Windows 返回 `0x26F`（无效的系统 DLL 重定位）。本轮构建未通过，历史 HEX 不能当作本次产物。平衡车工程目标为 STM32F103C8，只作为旧工具链的历史证据。

`D:\移远杯项目文档\stm32资料` 提供 UM1974。`D:\移远杯项目文档\ec200u资料` 提供 UniKnect Gen1 Pro 的硬件、软件和测试指南，以及 QADP-EC200UCNAA-Arduino V1.1 原理图、丝印图、MQTT 与 AHT20 示例。该载板的接线索引见 [EC200U 联调指南](../../firmware/stm32/EC200U-EcoVision-guide.md)。MicroPython 示例运行于配套 STM32 固件，可用于单独验证套件能力。本项目沿用现有 C/HAL 工程，通过主 AT UART 控制 EC200U。

| 链路 | UniKnect V1.1 叠插候选 |
|---|---|
| STM32 ↔ EC200U | USART6，PG14/PG9（D1/D0），J308 采用 Nucleo-144 档（1–3、2–4） |
| STM32 ↔ K230 | USART2，PD5/PD6。叠插挡住内侧 CN9 时可从 Morpho CN11-41/43 取线，K230 端引脚及电平待查 |
| STM32 ↔ PC | USART3，PD8/PD9，经 NUCLEO 板载 ST-LINK 虚拟串口 |
| STM32 ↔ 载板 AHT20-F | I²C1，PB8/PB9（D15/D14），S502 选择 MCU 侧后检查 0x38 和采样 |

以下旧的 USART2 → EC200U 和 C4-P01 条目只适用于独立接线方案。实际载板先按丝印识别，再选相应配置。公共接口 1.0.0 的帧格式、MQTT 主题和控制优先级沿用原定义。

本轮 CubeProgrammer 只读枚举未发现 ST-LINK、J-Link 或 DFU，串口仅 COM7/COM8。板上最小运行、AT 回显与 4G 均待实测。优先连接 NUCLEO 的 CN1 以识别 ST-LINK，确认 UniKnect 实物丝印后从载板 J401 识别 USB AT 口，并读取 `AT`、`ATI`、`AT+CGMR`。随后在现有 HAL 工程上接入 USART2 和 USART6。

检查日期：2026-11-12（北京时间）。本轮范围：现有工程、工具链、最小运行条件和两路 UART 资源核对。

## 当前结论

环境盘点已执行；STM32 最小运行和两路串口实物核对尚未完成。未生成或覆盖 STM32 工程，未烧录、复位或向未知串口发送数据。

| 项目 | 本轮证据 | 状态 |
|---|---|---|
| 项目说明 | 已读《EcoVision二十天原型机完整实施方案.md》及 V4.1 的资源、通信章节 | 可作背景；本轮用户给定范围和日期优先 |
| 统一接口 | 后续复查已出现并已读 `docs/PROJECT.md`、`docs/INTERFACES.md` 1.0.0、`contracts/policy.json` 及 UART 样例 | 业务实现按冻结契约执行，不采用旧参考帧 |
| STM32 工程 | 工作区未发现 `.ioc`、`.uvprojx`、`.cproject`、C/H 源码、链接脚本或固件 | 无现有工程可编译或复用 |
| STM32 / K230 / EC200U 型号 | 用户确认 NUCLEO-F413ZH（板载调试器）；K230 为 LCKFB-LSPI-K230-1G；EC200U 子型号未知 | STM32/K230 板型已明确；PCB 版本、电平及 EC200U 待核 |
| ARM 工具链 | PATH 未找到 `arm-none-eabi-gcc`、`UV4`、`IarBuild`、`STM32CubeIDE`、`cmake`、`ninja` | 未确认可编译环境；不等于全盘未安装 |
| Keil | 存在 `C:\Keil_v5\UV4\UV4.exe`；安装根目录仅枚举到 `C51`、`UV4` | μVision 存在；尚无 ARM 编译器证据 |
| 烧录工具 | 绝对路径运行 STM32CubeProgrammer CLI `-l`，版本 2.22.0，退出码 0 | 枚举命令执行成功；不代表烧录成功 |
| 调试器 / DFU | CLI 报告无 ST-Link、无 J-Link、无 DFU 设备 | 当前未检测到可用目标 |
| COM 口 | .NET 和 CLI 均枚举 COM7、COM8；注册表分别映射 `BthModem0`、`BthModem1` | 蓝牙串口，未识别出目标板 UART |

补充：`Get-CimInstance Win32_SerialPort` 返回“无法从客户端中访问 CIM 资源”；不能用该失败推断没有硬件。上述串口结论来自 .NET、注册表和 CubeProgrammer 三项结果。

### 用户补充的硬件基线（2026-11-12）

- STM32：NUCLEO-F413ZH，自带调试器；无需另购独立调试器。已有工程和编译器仍未提供，板卡 revision、焊桥和外接占用未核实。
- K230：立创·庐山派标准版、1GB，型号 LCKFB-LSPI-K230-1G；摄像头 GC2093。用户提供历史 640×480 采集成功记录路径 `captures/camera_test.jpg`，本模块未重新采集验证。
- K230 固件：用户提供 CanMV MicroPython `v1.8-66-g2d060be`（LCKFB）、nncase 2.11.0、MicroPython 1.21.0、构建配置 `k230_canmv_01studio_defconfig`；镜像名 `CanMV_K230_LCKFB_micropython_v1.8-66-g2d060be_nncase_v2.11.0.img`。用户依据扩展 stubs 判断实机 commit，本模块将其作为用户提供的版本线索，不作为本轮实机查询证据。
- K230 开发环境：用户提供 VS Code 1.142.0、CanMV 扩展 0.9.10；PCB revision 待背面丝印。视觉模块当前配置的 UART 仍禁用，端口/引脚为空、电平未确认，本模块不修改视觉目录。

### NUCLEO-F413ZH 文档核对后的资源候选

依据 [ST UM1974 Rev 11](https://www.st.com/resource/en/user_manual/dm00244518-stm32-nucleo-144-boards-mb1137-stmicroelectronics.pdf) 第 7.9 节及表 16：

| 用途候选 | 外设 | MCU TX / RX | 板上位置 | 限制 |
|---|---|---|---|---|
| K230 双向握手与人数帧 | USART6 | PG14 / PG9 | CN10-14（D1）/ CN10-16（D0） | 对端引脚、电平及工程占用待核 |
| EC200U AT | USART2 | PD5 / PD6 | CN9-6（D53）/ CN9-4（D52） | 对端电平、供电及固件待核；如需要流控，再核对 PD4/PD3 |
| 调试日志 | USART3 | PD8 / PD9 | 板载 ST-LINK 虚拟串口路径 | 检查 SB5/SB6/SB4/SB7；保留用于日志，避免外部 TX 共驱动 |

这是模块内候选分配，不是实测接线许可，不改变任何公共协议。USART6 与 USART2 的引脚在文档层面可分开使用；AF、DMA stream/channel、IRQ、时钟及现有工程冲突需在拿到工程后核实。K230 UART 按正式契约为双向：STM32 发送 EVQ、接收 EVH/EV1，115200 8N1、无流控。电平确认前不连接 EC200U。

## 两路 UART 核对表（待实物确认）

此表是资源核对表，尚不是实际接线表。旧方案的 USART1/PA9/PA10、USART2/PA2/PA3 是 F411 示例，本轮不采用为正式分配。

| 核对项 | K230 视觉链路 | EC200U 主 AT 链路 |
|---|---|---|
| STM32 外设实例 / TX、RX 引脚 / AF | USART6 PG14/PG9 候选；AF/占用待工程核对 | USART2 PD5/PD6 候选；AF/占用待工程核对 |
| 对端实际引脚 | 待查 K230 板卡及 FPIOA 配置 | 待查 EC200U 载板主 AT 口，区别调试口 |
| 信号方向 | K230 TX → STM32 RX；STM32 TX → K230 RX（握手必需） | EC200U TX → STM32 RX；STM32 TX → EC200U RX |
| UART 逻辑电平 / 电平转换 | 待查两板原理图及测量 | 原始模组和载板外露接口分别核对，尚不能判定可直连 |
| 波特率 / 数据格式 / 流控 | 契约固定 115200、8N1、无流控；工程配置待核 | 待实际固件、载板及 AT 配置确认；核对 RTS/CTS 是否需要 |
| IRQ / DMA / 缓冲资源 | 待查已有 HAL/RTOS 工程及 DMA 映射 | 待查已有工程；与视觉链路避免资源冲突 |
| 板载占用与调试输出 | 核对 USB 虚拟串口、下载口及其他外设 | 核对 USB 转串口是否共接，避免多个 TX 同驱动 |
| 验证结果 | 未实测 | 未实测 |

需要两路独立可用的硬件串口；调试日志优先复用现有 SWD/SWO、USB 或其他可用资源，不能默认还存在第三路 UART。UART IDLE 事件不能直接视作完整业务帧。

## 电源与负载核对

### EC200U 本地开发资料核对（2026-11-12）

用户提供目录：`E:\移远杯资料文档\E200U开发资料`。原文件只读，未移动或修改。目录名虽写 E200U，四份文件实际标题均涉及 EC200U；开发板资料为兼容 EC200U/EC200A 的 C4-P01 系列，不能由文件名认定实物模组是 EC200U 或确认具体子型号。

| 本地来源 | 已核实信息 | 边界 |
|---|---|---|
| `Quectel_QuecPython_EC200UA_C4_P01系列_开发板产品规格及用户指导.pdf`，PDF 第13页/印刷第12页，第30页/印刷第29页 | USB 输入 5.0–5.1V；外部输入 5–6V；外部 5V 时电源至少 2A；板载 DCDC 转为 3.8V 供模块 | 仅适用于资料对应 EVB 的指定输入，不可将 5V 接模组 VBAT 或 JP5 的 VBAT 端 |
| 同指南 PDF 第18页/印刷第17页，表3 | 40-pin 第8脚 TXD=UART2_TXD，第10脚 RXD=UART2_RXD；第6/9/14等为 GND；第2/4脚标为 5V 输出 | 排针方向需实物定位；不能把输出脚直接当供电输入 |
| 同指南 PDF 第15页/印刷第14页，表2 | DTX/DRX 测试点为 DBG_TXD/DBG_RXD，1.8V | 是调试测试点，不能误作 3.3V AT 口 |
| 同指南 PDF 第30页/印刷第29页，表7；`Quectel_QuecPython_EC200UA_C4_P01系列_开发板原理图.pdf`，第1页 40PIN 与 Level Translation 区 | 外设 I/O 典型 3.3V；原理图 UART2_TX/RX 经 TXS0104E 转换至 UART2_TX/RX_3V3 并引出排针 | 文档层面支持 3.3V 排针链路；需确认实物型号、转换供电和有效状态，不代表已经实测 |
| 同指南 PDF 第21页/印刷第20页，表4 | JP5 的1–2自动开机、3–4外围供电、5–6模块供电，7–8 SD、9–10 GNSS | 用户实际跳帽状态未知；不在未知供电情况下调整跳帽 |
| `Quectel_EC200U系列_LTE_Standard_模块产品规格书_V1.9.pdf`，PDF 第2页 | 模组供电范围 3.3–4.3V，典型 3.8V | 这是模组电源，与开发板 USB/外部电源入口不同；仍需硬件设计手册确认峰值供电设计 |
| `Quectel_EC200U系列EG912U-GL_GNSS_应用指导_V1.2.pdf` | GNSS 应用资料 | 不能替代通用 AT、MQTT、TLS 应用说明；本期核心不需要 GNSS |

如确认实物为此 C4-P01 EC200U 开发板、转换器正常且排针为 3.3V，可采用候选连接：NUCLEO CN9-6/PD5 TX → EVB 40-pin 第10脚 RXD；EVB 第8脚 TXD → NUCLEO CN9-4/PD6 RX；两板 GND 相连。暂不连接两板 5V/3V3 电源输出。此表仍是待核候选，不是实际接线验收记录。

**固件待核：** QuecPython 开发板资料说明硬件平台，不证明当前固件能直接接受标准 AT，更不证明支持项目需要的 MQTT TLS、域名/证书验证及下行 retain 标志。先获取当前固件身份、实际 USB 端口和已跑通示例；在确认 AT 通道后保存 `AT`、`ATI`、`AT+CGMR` 的真实响应。不据此自动刷写或更换固件，不擅自改变 STM32 + EC200U 架构。

当前目录没有通用 AT 指令手册、MQTT 应用说明、SSL/TLS 应用说明或可确认的固件包。待取得实机子型号/版本后匹配相应官方资料，不从 GNSS 命令推断联网命令支持。

验证方式：pypdf 提取文字；pypdfium2 渲染并人工检查指南供电页、排针表、电气表以及原理图排针/电平转换区。检查图保存在 `tests/embedded/artifacts/ec200u_docs/`，仅为资料截图，不是硬件测试证据。

- STM32：记录完整芯片丝印、板卡型号、供电入口和允许输入、I/O 电压、BOOT 配置、SWD 接口及 LED 有效电平。
- EC200U 原始模组：按实际区域子型号对应的移远硬件设计文档核对 VBAT 范围、发射峰值供电能力、UART 电压、上电时序和主 AT 引脚；本轮未核实数值，不授权直连。
- EC200U 开发板：另外核对板卡输入端允许电压、稳压能力、电平转换及外露 UART 电压，不能把模组参数套在开发板电源口上。保留原理图依据和注册/发射时的供电测量记录。
- K230：核对具体板卡供电、引脚映射及 UART 电压。连接前确认两端电平兼容、共地、TX/RX 交叉及无电源反灌。
- 风扇/LED：先断开负载完成 MCU 最小运行；之后核对驱动输入有效电平、复位默认关闭和独立 5V 负载供电。GPIO 读回只记录输出状态；没有转速或电流反馈时，风扇运行反馈应标记“未知/无反馈”。

## 收到工程与硬件后的最小运行验收

沿用现有 HAL 或 RTOS，不迁移系统、不重新生成覆盖整个工程。

| 步骤 | 操作 | 必须保留的证据 | 当前结果 |
|---|---|---|---|
| B01 | 核对芯片丝印、工程目标、启动文件、链接脚本、时钟和编译器版本 | 型号记录、工程路径、工具版本 | 未执行 |
| B02 | 原样编译已有工程，确认 Flash/RAM 使用 | 完整构建日志、退出码、产物路径 | 未执行 |
| B03 | 接调试器只读识别目标，核对目标与工程一致后烧录 | 设备识别、烧录及校验日志 | 未执行 |
| B04 | 负载断开，验证复位、节拍/心跳、日志及输出默认关闭 | 板上串口日志或调试记录、GPIO 测量 | 未执行 |
| B05 | 两个 UART 各自与已确认电平的适配器做收发/回环 | 每路实例、实际针脚、波特率、发送/接收计数及错误计数 | 未执行 |
| B06 | 两路同时持续收发，检查丢字节、溢出和控制节拍 | 流量、持续时间、错误计数、节拍间隔记录 | 未执行 |
| B07 | EC200U 单板 AT 应答及版本查询，再进入注册与 TLS 联调 | 脱敏原始串口日志及实际固件版本 | 未执行 |

B05/B06 是传输层验证，不代表人数协议、命令处理或真实 4G 已通过。网络等待不得阻塞本地控制，后续必须独立验证超时/断网期间的控制节拍。

## 提交总控的接口待办

已取得并读取正式 `docs/INTERFACES.md` 1.0.0、policy 和 UART 样例。采用 EVQ/EVH/EV1 显式会话，不接收旧五字段帧。其余公共规则直接遵守正式文档；本轮没有公共接口修改建议。

## 最少必要补充信息

1. 现有 STM32 工程的实际路径或完整工程副本，以及以往使用的 IDE/编译器版本；如确无工程，明确说明。
2. NUCLEO-F413ZH 板卡版本/焊桥及现有外接占用；用支持数据的 USB 线连接板载 ST-LINK 端后重新枚举。型号和自带调试器已明确，无需重复提供。
3. 庐山派 PCB revision、计划使用的实际 UART 排针和 FPIOA；EC200U 实物模组完整丝印、开发板型号/版本、是否与 C4-P01 资料一致、当前固件和跳帽/供电状态。已有 C4-P01 原理图与指南，无需重复提供；电压实测记录可随后补充。

本轮不需要 Broker 密钥；SIM、APN、Broker 地址、证书和设备凭据在真实联网阶段再按安全配置方式提供，禁止写入代码。

## 本轮交付状态与下一步

- 修改文件：`docs/modules/embedded.md`；新增 `tests/embedded/artifacts/ec200u_docs/` 下6张 PDF 核对图。
- 代码完成：未实现固件；正式接口已取得，尚无现有 STM32 工程。
- 软件测试通过：仅完成本机环境/设备枚举；未执行固件构建或业务测试。
- 硬件实测通过：无。最小运行、两路 UART、供电电平、真实 4G 均待验证。
- 下一步：取得上述最少信息后先完成 B01–B06，再按实际 EC200U 固件推进 B07、注册和 MQTT TLS。保存真实日志，不以模拟日志替代。

排期采用当前共同背景：2026-11-14 晚启动；11-20 前视觉到本地控制；11-24 前真实 4G 上报与远控；11-25 核心冻结；11-27 完成 8 小时综合测试；11-29 交付。总预算不超过 5000 元，优先复用已有硬件。
