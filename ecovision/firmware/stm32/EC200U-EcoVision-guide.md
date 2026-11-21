# EC200U 在 EcoVision 中的接线与 4G 联调指南

2026-11-16。依据用户提供的 `D:\移远杯项目文档\ec200u资料`、移远公开 AT 文档及 EcoVision 统一接口 1.0.0。新资料对应 **UniKnect Gen1 Pro，QADP-EC200UCNAA-Arduino V1.1** 扩展板，板载 EC200U-CN，支持与 NUCLEO-F413ZH 直接叠插。下面的跳帽、丝印和接线以实物匹配这块 V1.1 载板为前提。此前记录的 C4-P01 是另一种载板，应按其对应资料接线。

## 1. 项目里的分工

```text
K230 <── 视觉 UART ──> STM32 ──> 5 V 风扇 / LED
                         │
                      AT 串口
                         │
                     EC200U ── LTE ── MQTT/TLS Broker ── 授权服务与看板
```

- STM32 汇总人数和温湿度、决定并驱动输出、校验远程命令并产生应用层 ACK。EC200U 处理 SIM、入网、数据连接和消息传输。手机通过授权看板下发命令。
- 断网时 STM32 继续执行本地控制。有效的远程租期按原定单调计时到期，再交回 AUTO。项目先完成 5 V 风扇与 LED，板上的 GNSS、音频、LCD、OTA、云平台 SDK 暂不进入核心链路。
- 建议沿用 STM32 C/HAL，从 EC200U 主串口发 AT。套件的 MicroPython 路线可用于对照测试：Thonny 与移远定制固件运行在 **NUCLEO 的 STM32 上**，示例调用 `quectel.Network`、`umqtt`。资料包的 `release/README.md` 指向在线下载，本地目录只见发布说明。保留现有固件，先读取版本。K230 的 CanMV 是独立环境。 [移远 UniKnect 官方仓库](https://github.com/quectel-develop/uniknect-micropython/)

## 2. 资料索引

文件路径以 `ec200u资料\uniknect-micropython\uniknect-micropython` 为起点。下列页码按 PDF 阅读器从 1 开始计数。

| 文件 | 项目中查什么 |
| --- | --- |
| `docs/Quectel_UniKnect_Gen1_Pro_硬件指导_V1.0_Preliminary_20260321.pdf` | 第 11–19 页找板上部件、供电、双 USB 口、开机、SIM 和天线。第 20–22 页找叠插、J308 UART 选择、J305 监听和 Arduino 控制脚。 |
| `docs/schematics/QADP-EC200UCNAA-Arduino Sch V1.1.pdf` 及同目录 `QADP-EC200UCNAA-Arduino V1.1 top Silkscreen.pdf` | 原理图第 2 页查电源与 PWRKEY/RESET，第 3 页查 Arduino 信号、UART 电平转换和 CP2105，第 5 页查 SIM、I²C 和 AHT20-F。丝印图定位实物。 |
| `docs/Quectel_UniKnect_Gen1_Pro_软件开发指导_V1.1_Preliminary_20260310.pdf` | 第 12–13 页查 Nucleo 叠插，第 14–17 页查驱动与 STM32 固件下载，后续章节查 Thonny/REPL。 |
| `docs/Quectel_UniKnect_Gen1_Pro_测试指导_V1.1_Preliminary_20260402.pdf` | 第 11–14 页查上电及电脑串口，第 18 页查温湿度，§3.10 查 TCP，§3.12（PDF 第 34–36 页）查 MQTTS 双向认证示例。根目录同名 PDF 的 SHA-256 与此文件一致。 |
| `modules/network/`、`modules/mqtt/`、`modules/socket/`、`modules/peripherals/温湿度/aht20.py` | 查套件 MicroPython 的拨号、普通 MQTT、单向与双向 TLS、Socket、板载温湿度。示例里的服务器、凭据、证书路径和主题是示例环境配置。 |
| 用户目录根部 `UM1974_Nucleo144_用户手册_中文版.pdf` 与英文 UM1974 | 查 NUCLEO 接口表。最终按英文 Rev 11 表 16 比对 F413ZH 的引脚。 [ST UM1974](https://www.st.com/resource/en/user_manual/um1974-stm32-nucleo144-boards-mb1137-stmicroelectronics.pdf#page=49) |

AT 路线配套阅读 [移远通用 AT 手册 V1.1](https://quectel.com/content/uploads/2024/02/Quectel_EC200UEG91xUEG915G_Series-AT-Commands-Manual_V1.1.pdf)、[TCP/IP 应用说明 V1.1](https://www.quectel.com/content/uploads/2024/02/Quectel_EC200UEG915U_Series_TCPIP_Application_Note_V1.1.pdf)、[MQTT 应用说明 V1.1](https://www.quectel.com/content/uploads/2024/02/Quectel_EC200UEG915U_Series_MQTT_Application_Note_V1.1.pdf) 和 [SSL 应用说明 V1.2](https://quectel.com/content/uploads/2024/02/Quectel_EC200UEG91xU_Series_SSL_Application_Note_V1.2.pdf)。实机版本拿到后，再向移远匹配对应修订。 [EC200U 产品与文档页](https://www.quectel.com/product/lte-ec200u-series/)

## 3. 台架上电与 USB 口

1. 断电识别载板丝印和模组完整型号。把 LTE 天线接到 **J101 MAIN_ANT**。使用已开通数据服务的 Nano SIM 时，插 `USIM1`，`S501` 拨印有 `USIM` 的一侧。若使用内置卡，拨到 `ESIM` 并确认该卡已经开通。切换后重新启动模组。
2. `S201` 拨到 **DC/USB**。载板有 **J201 DC 5 V、J401 Type-C、J403 Type-C** 三个供电入口。台架建议使用正规 5 V、带载能力至少 2 A 的电源，例如确认插头匹配后用 J201 供电，J401 用数据线连电脑做 AT。原理图上载板把输入降至约 3.8 V 模组 VBAT，另生成 3.3 V 板载电源。STM32 由自己的 CN1 供电，风扇使用独立 5 V 支路。
3. 先看 `POWER`。若 `J202` 自动开机跳帽未短接且模组未启动，按住 `S204 PWRKEY` 至少 2 秒后释放，再看 `STAT`。手册给出的典型 4G 外观是 `NET` 常亮、`MOD` 闪烁，入网仍以 `AT+CEREG?` 结果和数据连接验证为准。S202 是 BOOT 下载入口，日常联调使用 PWRKEY。

| PC 接哪一个 | 设备管理器找什么 | 用途 |
| --- | --- | --- |
| 扩展板 **J401** | **Quectel USB AT Port**，COM 编号因电脑而异 | 先做模组身份、SIM、注册、PDP 和 MQTT 验证 |
| 扩展板 **J403** | CP2105 Standard COM / Enhanced COM | Standard 按 J305 默认监听配置观察主串口，保留监听跳线并确认 3–4 未短接。Enhanced 默认用于模组 DEBUG 日志 |
| Nucleo **CN1** | STMicroelectronics STLink Virtual COM Port | STM32 烧录加 USART3 日志，套件 MicroPython 环境下也可作为 REPL |

J401 是扩展板的模组 USB。测试指导 PDF 第 14 页把 J401 写在 NUCLEO 名下，按扩展板原理图及丝印定位。J403 DEBUG 串口与 J401 AT 口功能不同，无需根据截图照抄 COM 号。核对依据为硬件指导 §3.2–3.8、§4.4 和测试指导 §2.2。

## 4. 与 NUCLEO-F413ZH 叠插后的串口分配

**QADP V1.1 叠插方案**建议把 EC200U 分给 USART6，把 K230 分给 USART2。断电对齐 Arduino 接口再叠插，J308 按 Nucleo-144 档短接 **1–3、2–4**。原理图第 3 页显示 STM32 侧信号经过相应电平转换接到 EC200U 主串口。

| 链路 | Nucleo 端 | 接法 |
| --- | --- | --- |
| STM32 → EC200U | USART6 TX `PG14`，`CN10-14 / D1` | 叠插经 D1 → J308 1–3 → 载板电平转换 → 模组 MAIN_RXD |
| EC200U → STM32 | USART6 RX `PG9`，`CN10-16 / D0` | 模组 MAIN_TXD → 载板电平转换 → J308 4–2 → D0 |
| STM32 → K230 | USART2 TX `PD5`，Morpho `CN11-41`，也引至 `CN9-6 / D53` | 接对端 RX，核对 K230 FPIOA 与逻辑电平，按需做电平转换 |
| K230 → STM32 | USART2 RX `PD6`，Morpho `CN11-43`，也引至 `CN9-4 / D52` | 接对端 TX，地可用 `CN11-49` 或 `CN9-12`。叠插后优先从外侧 Morpho 取线，按 UM1974 表 21 与丝印定位 |
| STM32 → PC | USART3 `PD8 / PD9` | Nucleo CN1 的板载 ST-LINK 虚拟串口 |

K230 使用项目既定的 `115200 / 8N1 / 无流控` 和 `EVQ → EVH → EV1`。模组 AT UART 的波特率、流控按实机确认；115200/8N1/无流控可作为双线叠插的试测起点。在 AT UART 能稳定回包前，先用 J401 确认模组状态。USB AT 通道验证后关闭测试命令会话，再由 STM32 独立接管主 UART；同时仍可用 J403 监听。

- 上一份 [Nucleo 指南](NUCLEO-F413ZH-guide.md) 的 K230＝USART6、EC200U＝USART2，适用于经跳线接独立 modem 串口的候选布局。QADP 默认叠插时，D0/D1 已用于 EC200U，不能同时接 K230。此处交换的是 STM32 外设实例与端子，公共报文和时序沿用统一接口。
- J307 的 `MAIN_RXD/MAIN_TXD` 是原理图上模组侧的信号。对外接线使用经确认的载板电平转换侧，不把 STM32 3.3 V TX 接到 J307 的原始模组信号。
- 选择风扇或 LED GPIO 时避开扩展板已接信号。原理图第 3 页包括 D4（DC_EN，驱动器贴装按实物核对）、D6（PWRKEY 控制）、D7（传感器中断）、D9（模组复位）。硬件指导 §4.5 列出 MCU 侧开机和复位控制。先验证手动开机，自动开机和复位控制单独测。
- **可复用板载 AHT20-F。** 叠插后将 `S502` 拨至 ARDU/MCU 一侧，按 D15/SCL＝`PB8`、D14/SDA＝`PB9` 配置 STM32 I²C1。原理图网名 `MCU_I2C2_*` 为载板命名，STM32 的外设实例按 UM1974 与套件示例核对。先确认地址 `0x38` 应答和温湿度采样，再接入 AUTO 温控。采样无效时按契约上报空值和有效性标记。出处为载板原理图第 3、5 页、测试指导 §3.3、`aht20.py` 和 UM1974 表 16。

## 5. 第一次用电脑验证 4G

串口助手打开 J401 对应的 AT Port，按 AT 手册发送命令，命令行以 CR 结束。此阶段先看原始返回，再写 STM32 状态机。日志里打码 SIM 标识、设备身份和认证数据。

| 顺序 | 操作 | 可以进入下一步的证据 |
| --- | --- | --- |
| 1. 识别 | `AT`、`ATI`、`AT+CGMR` | `OK`、实际模组型号与完整固件版本 |
| 2. SIM | `AT+CPIN?` | `+CPIN: READY`。否则先看卡槽方向、S501、卡 PIN 和卡是否开通 |
| 3. 注册 | `AT+CSQ`、`AT+CEREG?`、`AT+CGATT?` | EPS 注册状态通常为 1（本地）或 5（漫游），附着为 1。信号返回 99 表示未知，不能当良好信号 |
| 4. 数据 | 先查 `AT+QIACT?`。如需建上下文，用 `AT+QICSGP` 配运营商实际 APN 和认证参数，再 `AT+QIACT=1`，最后 `AT+QIACT?` | 所选 PDP 上下文有效且有 IP。已注册但无 IP 时先查 APN、卡的数据权限和上下文号 |
| 5. 校时 | 按实际固件核对 `AT+CCLK?`、`AT+QLTS`，验证其来源、时区、当前值和断电重启表现 | 模组 TLS 校时与 STM32 业务 UTC 分别确认。STM32 把可信时间换算为 UTC Unix 秒，命令租期仍用单调计时 |
| 6. 探测 MQTT/TLS | `AT+QMTCFG=?`、`AT+QMTOPEN=?`、`AT+QMTPUBEX=?`、`AT+QSSLCFG=?` | 留存能力输出，确定当前固件支持的配置项、上传方式、命令和长度限制 |

未获得可信业务 UTC 时，按项目合同让 `time_valid=false`、相应墙钟为 `null`，可用合法遥测检验连通性，对新远程动作返回 `TIME_UNTRUSTED`。一次 `CCLK?` 有值不能证明时钟已同步。TLS 证书校验也需要正确的模组时钟。

## 6. MQTT/TLS 怎么接入项目

先由云端负责人提供**已授权、EC200U 的 4G 能访问**的 Broker 域名、TLS 端口、CA、设备身份和设备 ID。当前项目的本机 demo 绑定 `127.0.0.1`，适合本机模拟验证。台架凭据从本地受控配置注入，串口抓包应遮盖认证行。 [云端说明](../../cloud/README.md)

### 建连和上报顺序

1. 用 `AT+QFUPL` 加载授权 CA，然后用 `AT+QSSLCFG` 配相同 SSL context 的 CA、服务端认证和兼容 TLS 版本；Broker 要求双向认证时才配设备证书和私钥。使用 Broker 域名，按固件配置 SNI，同时验证证书 SAN 与域名匹配。错误 CA、证书过期和同一可信 CA 签发但域名不符的证书都应失败。若测域名错误，测试端应能完成服务端握手准备，避免把 SNI 路由失败误判成客户端做了域名校验。
2. 参考 MQTT V1.1 中 `QMTCFG` 的 `version`（4 表示 MQTT 3.1.1）、`pdpcid`、`session`（1 表示 clean session）、`keepalive`（30 秒）、`ssl` 和接收配置。连接前用 `will/willex` 配本设备的离线遗嘱。每次 CONNECT 按合同预留 status 序号 n/n+1，online 用 n，遗嘱及正常 offline 用 n+1。
3. `QMTOPEN` 后等 `+QMTOPEN` 成功结果，再发 `QMTCONN`，等连接确认返回。连接成功后发布 online 状态，再订阅自己的 `cmd` 并确认 `+QMTSUB`。命令刚收到的 `OK` 只表明 AT 指令被接受。确定收到了各操作的最终结果，才能更新 STM32 内部的连接状态。
4. `QMTPUBEX` 按 UTF-8 字节数发送 JSON。等待提示符后送指定字节数，再等发送结果。先在授权测试设备下验证 [公共样例](../../contracts/examples/) 的形状，测试数据使用当前的设备身份、会话和时间，并与正式设备隔离。再由 STM32 填真实状态。收到 `+QMTRECV` 后，按实际固件的直推或缓冲模式读取完整主题与载荷，进入命令校验。JSON 中可能含引号、逗号或换行，按固件定义和长度处理。网络端状态与业务端动作分别记日志。

| 主题后缀（前缀 `ecovision/{device_id}/`） | 方向 | QoS / retain | 项目用途 |
| --- | --- | --- | --- |
| `telemetry` | STM32 → 云端 | 1 / false | 每 5 秒上报，必要时状态变化额外发送 |
| `status` | STM32 或 Broker 遗嘱 → 云端 | 1 / true | online/offline，会话状态 |
| `cmd` | 授权服务 → STM32 | 1 / false | 通过会话、设备、时间、优先级等校验才执行 |
| `ack` | STM32 → 云端 | 1 / false | 用 `cmd_id` 对应 `APPLIED` 或 `REJECTED`。成功 ACK 在写入输出后产生 |

### 优先验证的三项兼容性

| 项目要求 | 资料里的边界 | 台架验证 |
| --- | --- | --- |
| TLS 证书及域名验证 | SNI 配置描述的是客户端向服务器提供域名，样例 TLS 成功无法确认域名验证行为 | 有效域名成功、错 CA 失败、同 CA 错域名失败，使用正确 UTC，保留失败码 |
| 应拒绝下行 retained cmd | 公开 MQTT V1.1 手册的直推和缓冲返回未列出 RETAIN 字段；MicroPython 示例回调也只有 topic 与 payload | 在授权测试 Broker 上分别验证普通和预先保留的下行，尤其在重新订阅时确认 STM32 能区分并拒绝。在能区分前，远控能力待验收 |
| 业务载荷上限 2048 字节 | 公开 MQTT V1.1 的 `QMTPUBEX` 单次输入写明 1500 字节；公共正常遥测样例压缩后为 417 字节，样例连通不能覆盖边界 | 记录实际业务载荷字节数，并检查边界收发有无截断。若路径无法承载合同规定的有效载荷，记录为传输适配问题，提交总控 |

如果当前 QMT 固件确实缺 RETAIN 或主机名校验能力，先向移远确认同一 EC200U 可用的固件和接口版本。若仍无法满足，提交总控评估由 STM32 的 MQTT 客户端经 EC200U 提供的数据通道传输并读取 MQTT 报头，或其他满足原合同的实现路径。在授权兼容环境实测后再冻结。参考 [统一接口 §§3–6](../../docs/INTERFACES.md) 与 [移远 MQTT AT 接收及发布说明](https://www.quectel.com/content/uploads/2024/02/Quectel_EC200UEG915U_Series_MQTT_Application_Note_V1.1.pdf#page=24)。

## 7. STM32 集成与验收

- 通信状态顺序可按「识别 → SIM → 注册 → PDP → 校时与 TLS → MQTT 连接/订阅 → 在线 → 退避重连」组织。USART6 使用中断或 DMA 接收并交由主循环或任务解析。把 AT 行应答、发包提示符、异步状态和下行载荷分别处理。网络等待、证书上传和重连期间照常处理 K230 帧、温湿度、按键与本地输出。
- STM32 上电按合同生成新 `boot_id`，初始输出关闭。远程命令须验证当前会话、`control_epoch`、TTL 和幂等，LOCAL_OFF 优先。重复 QoS 1 消息只按原命令逻辑回 ACK，不重新动作或续租。断线重连后先恢复干净订阅并上报当前状态，设备保持本地控制，云端收到新鲜遥测后再开放操作。
- **台架验证顺序。** ① PC 经 J401 确认身份、SIM、注册并激活 PDP。② 仍由 PC 验证授权 Broker 的 TLS、上下行和兼容性。③ Nucleo 叠插后单独验证 USART6 AT 与 USART2 K230。④ 合入本地风扇和 LED，关掉电脑网络转发，验证真实 4G 遥测与页面远控、断网恢复及告警。每步保留时间、结果、接线照片和脱敏串口日志。
- **项目验收。** A06 连续 1 小时真 4G，5 秒周期样本完整率至少 95%。A07 手机发 20 条有效命令全部正确执行，至少 19 条在 10 秒内收到 ACK。A08 验证 retain、过期、重复和无可信时间等拒绝用例。11 月 24 日为远控关口，11 月 27 日完成 A15 八小时综合运行。 [项目验收表](../../docs/ACCEPTANCE.md)

## 本轮状态和下一步

- 文件：新增本指南，并在 Nucleo 指南补充叠插接线说明。原始资料与公共接口由原目录维护。
- 文档核对：已提取硬件、测试、软件、MQTT、网络、Socket 与外设手册的相关内容，目视复核 J308/J305 图、板卡丝印、供电与串口原理图及 USB AT 口截图。
- 代码、软件和硬件：本轮为资料整理，未实现或编译固件，未测试真实模组、SIM、Broker、4G 或控制负载。当前 STM32 模块只有文档和占位文件。
- 下一步：核对 EC200U 扩展板正反面丝印、J308 和 S201/S501 位置，先用 J401 读取 `AT`、`ATI`、`AT+CGMR`、`AT+CPIN?`、`AT+CEREG?`。有了这几条脱敏回显即可确认实际板型、固件和入网状态，随后补 APN 与授权 Broker。
