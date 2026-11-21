# EcoVision K230 视觉模块

更新：2026-11-12。仅维护 `firmware/k230/`、`tests/vision/`、本文。
执行基线：`docs/PROJECT.md`；UART契约：`docs/INTERFACES.md` 1.0.0。

## 交付状态

| 层次 | 当前结论 | 证据/限制 |
|---|---|---|
| 代码 | 最小采集检查、官方检测类适配、有效性、心跳、UART代码已实现 | 不代表板端兼容性已通过 |
| 软件测试 | 主机26项测试通过；语法和3个提取文件的哈希已检查；公共UART样例逐字节比对通过 | CPython 3.13.13；没有运行KPU、摄像头、FPIOA |
| 硬件实测 | **本次尚未进行** | 当前仅有蓝牙COM7/COM8，无CanMV设备；不得填写“视觉通路已跑通” |
| 历史证据 | 用户报告640×480采集成功、11-10运行过YOLOv8n | 旧工程笔记可读；不替代本次人体模型与串口验收 |

本次先检查现有资料和工具链，再从匹配固件提取原样官方资产，完成主机异常与协议测试。下一步严格按“官方原摄像头例程 → 官方原人体检测例程 → 本模块摄像头检查 → 计数与串口”推进。无自训练、穿衣识别、跟踪、占用去抖、无人关断或云端图像功能。

## 环境及最少待确认项

| 项目 | 已有依据 | 尚需确认 |
|---|---|---|
| 板卡 | 用户提供庐山派标准1GB，LCKFB-LSPI-K230-1G | 看实物正背面型号及PCB revision；01Studio机械图不能证明实物是01Studio |
| 摄像头 | 用户提供GC2093；旧脚本使用`Sensor(id=2)`/`pl.create(sensor_id=2)` | 模组丝印、排线方向、当前连接与实际成像 |
| 固件 | 本地镜像名v1.8-66-g2d060be、nncase 2.11.0；镜像revision核实如下 | 板端`os.uname()`、`/sdcard/revision.txt`和nncase输出复验 |
| 工具链 | VS Code/CanMV扩展版本由用户及旧项目记录提供；旧venv内pyserial可实际执行 | 重新连板后确认CanMV扩展选择正确端口 |
| 模型 | **匹配镜像中确有专用人体模型**，已提取，2,375,584字节 | 当前板上是否存在、哈希是否匹配、能否实际加载 |
| UART | 契约固定115200/8N1、CRC和握手 | UART实例、FPIOA编号与物理排针对照、电平、与其他外设占用；本次没有填任何针脚 |

最少需要现场补：①板卡/摄像头丝印；②连接CanMV后保存preflight输出；③原样官方人体检测的运行日志与0/1人观察；④启用UART前确认实际实例、TX/RX、电平及对端。无需云凭据。

只读参考旧工程：`D:\codex richang\k230-learning\canmv\04_yolov8n_detect.py`及`docs\LESSON_03_YOLO.md`。
检查发现：当前旧脚本默认`MODEL_PROFILE="320"`，笔记记录224模型；其`preprocess()`直接`nn.from_numpy()`，不能假定配置过的ai2d总会执行；当前RGB与模型尺寸相同，但不宜直接改大采集尺寸。旧`DET`帧为XOR校验、100ms发送、8位序号，只报一个目标，**不能用于本项目EV1契约**。没有复制旧脚本中的候选针脚，也没有修改旧工程。

## 模型和官方资产版本

本期选择同一镜像中的单类人体YOLOv5n作为待板测候选：它的模型与脚本已实际找到，比按名称猜测网上模型更可复现。旧YOLOv8n保留为故障排查对照，不新增第二套生产适配器；如专用模型不通过，先提交实际错误、现有v8脚本/模型哈希和切换建议。

来源为用户本地镜像：
`D:\codex richang\k230-learning\CanMV_K230_LCKFB_micropython_v1.8-66-g2d060be_nncase_v2.11.0.img`。

镜像SHA-256：`b78e04e4020b8b3ab0c925638e8635ae0cfc4a407ca313fd9a160ad2eff88952`。

| 文件 | 镜像内原路径 | SHA-256 |
|---|---|---|
| `official/person_detection.py` | `/examples/05-AI-Demo/person_detection.py` | `7117eeff7fd2cb81d98fabe1bcc9e4b0e292adf4eb71034c6602f159eff28063` |
| `official/person_detect_yolov5n.kmodel` | `/examples/kmodel/person_detect_yolov5n.kmodel` | `512325f2b5924bf4502c8b88006c50fb801a2bc93101148df92b30fbc4c8682a` |

`official/firmware_revision.txt`保留镜像原始版本信息：CanMV `2d060bef54b161c3ac65a1c4c1e2789d4ea8a544`；模型资源`nncase_kmodels_v2_11=0843f558a9cd9b9da1ddf45b214bd570ac628fc5`；构建时间2026-10-17。完整哈希、尺寸、路径见`official/manifest.json`。这是固件资源版本，不虚构训练权重版本或训练数据证明。原文件字节未修改，仅供本项目本地复现；公开再分发前需单独核对上游模型许可。

默认完全沿用该脚本主程序的模型输入640×640、采集1280×720、`labels=["person"]`、anchors/strides、置信度0.2和NMS 0.6。类构造器的默认NMS是0.5，但原脚本实际主程序传0.6，以实际调用为准。

复现提取（PC；只读镜像，不刷板）：

```powershell
python -B firmware/k230/extract_firmware_assets.py 'D:\codex richang\k230-learning\CanMV_K230_LCKFB_micropython_v1.8-66-g2d060be_nncase_v2.11.0.img'
```

参考[官方人体检测源码](https://github.com/kendryte/canmv_k230/blob/canmv_k230/resources/examples/05-AI-Demo/person_detection.py)、[PipeLine API](https://www.kendryte.com/k230_canmv/en/main/api/aidemo/pipeline_module_api_manual.html)、[UART API](https://www.kendryte.com/k230_canmv/en/main/api/machine/k230_canmv_uart_api_manual.html)。网页main分支只作API参考，不能替代本地镜像版本。

## 从断电开始的板端复验

1. 确认实物型号后连接开发板；用原有CanMV扩展，不安装训练依赖、不更换固件。当前枚举COM7/COM8是蓝牙，不能作为板卡端口使用。
2. 将本模块运行文件及`official/`拷至板上`/sdcard/ecovision/`，保持子目录结构。仅PC使用的`extract_firmware_assets.py`无需上传。不要覆盖原有`boot.py`、其他模块或启动脚本。CanMV运行当前文件需要先确保模块已真正存到板上，不能只打开电脑文件。
3. 在CanMV执行`/sdcard/ecovision/preflight.py`，保存完整终端输出。它不打开摄像头或UART；打印固件和候选资产的实际哈希。板端实际版本不同则先停止模型适配并核对来源。
4. 先原样运行当前固件配套的摄像头官方例程，观察连续成像并记录；再原样运行`/sdcard/examples/05-AI-Demo/person_detection.py`。如果模型缺失，从本模块`official/`恢复到原脚本指定的`/sdcard/examples/kmodel/person_detect_yolov5n.kmodel`，不修改脚本去匹配别的模型。若文件存在但哈希不同，保留原文件并核对，不直接覆盖。记录原例程SHA、模型SHA、画面/0人/1人/FPS/异常。原例程中断后可能未释放媒体资源，复位后再跑下个程序。
5. 原样程序不成功时先保留错误日志，不设置已通过标志。如仅默认摄像头选择失败，在原文件保持不变的前提下，用另存副本验证`sensor_id=2`，分别记录“原样失败”和“仅摄像头选择改动后的结果”，由模块负责人确认匹配后继续，不能称原样通过。
6. 运行`camera_smoke.py`，它依据旧工程已知的`sensor_id=2`采30帧640×480并本地显示、检查格式和全黑/饱和帧；任一失败即抛错并释放资源。它不做推理，成功不能替代人体检测测试。
7. 将`config.example.json`复制为板上`/sdcard/ecovision/config.json`。补入此次实际核对的板卡/摄像头/固件及`official_test_record`日志路径；只有原例程真实通过后才设`official_example_passed=true`。默认false故意阻止未验证组合输出可信人数；不自动生成“通过”记录。保留UART关闭。
8. 执行`main.py`，观察本地`EV_DIAG`每秒状态，分别测0—5人及遮挡镜头、模型不存在/损坏、异常恢复。异常必须`valid=false,count=null`；有效无人必须`valid=true,count=0`。初始化失败保持无效心跳，修复后重启程序；运行中的可返回异常可下一帧立即恢复。不做人数去抖。
9. 实物接线确认后再填`uart.id/tx_pin/rx_pin`及两项确认标志，设`enabled=true`。原理图中的FPIOA号不一定等于排针序号。先做官方UART单板收发验证，再由STM32发送带正确CRC的新EVQ；看到EVH后才有EV1。记录真实抓包、序号、时间间隔、掉线重握手与两端复位结果。

UART入口仅允许配置已确认的1/2/4实例（按已查API手册），不推测可用针脚。若实际固件资源分配不同，应先核对其API和板卡手册。初始化失败不会自动改用其他实例。

## 数据、异常和调度

`vision.py`消费官方后处理的NMS检测框。只接受该单类模型的person类；0—5人直接输出，不限幅、不做控制规则。超过5人视为本场景超容量，无效输出；UART定义0—20为通用传输范围，本模块的验收能力仍为0—5。`None`/不合法框/缺帧/全黑与全白帧/模型或采集异常均无效，不能保留上一帧的可信人数。

显示端绘制与计数相同的NMS框；未沿用原例程`draw_result`中的小框/边缘隐藏条件，避免“计到了但画面没有框”的歧义。官方推理、预处理和后处理类未更改。这个显示差异须在板测时观察。

`main.py`在主循环中推理，1秒节流心跳；没有补发旧人数。初始化错误不反复重建资源，持续输出无效状态。可返回的逐帧错误下次立即重试。若底层采集/KPU卡死或单帧耗时过长，同线程无法保证1秒心跳；由STM32按契约5秒超时判失效。本次未加入未经板测的线程/中断推理或复位规则。正式联调需测实际帧率、发送间隔和200ms半帧超时兼容性。

串口严格使用EVQ/EVH/EV1、CRC-16/CCITT-FALSE、CRLF。接收支持半包、粘包、新`$`重同步、超长/非ASCII/错CRC丢弃及200ms超时；应用接收区512字节、单帧上限128。**固件底层UART环缓冲实际容量仍须核实**，应用512字节不等于驱动环缓冲已满足契约；发现不满足则提交总控，不自行虚构`read_buf_len`之类未验证参数。写串口支持短写，写停滞报错退出，不伪记已发送成功。

`vision_boot_id`通过`boot_identity.py`预留持久递增64位ID：首次OS随机种子，此后先落盘预留下一个值、同步后才使用本次ID。保持板上`.vision_boot_id`文件，不复制到另一活动设备；文件损坏、同步API缺失、计数耗尽均拒绝启用UART，不静默归零。SD卡掉电持久性、固件`os.sync/rename`覆盖行为仍需硬件测试。seq跨重复EVQ及链路切换保持递增，uint32回绕；每次程序新运行分配新boot ID。

本地诊断JSON不是公共协议，内部无效人数null。UART按统一契约把无效值转为`count=0,valid=0`占位，STM32必须忽略这个0。原始图像仅在本地显示；脚本不导入网络库、不上传图像、不存视频。

## 软件验证与串口样例

在项目根目录运行：

```powershell
python -B -m unittest discover -s tests/vision -v
```

26项主机测试覆盖0—5人、6人超容量、空结果与None差异、异常后不沿用旧人数、下一帧恢复、初始化失败心跳、1秒节流、序号回绕、黑/白/格式异常、未确认配置、资源关闭、CRC标准向量、握手前禁发、重复握手、新link、坏帧/半包/粘包/超长/非ASCII/200ms过期、短写/停滞、UART未配置禁用、持久boot ID递增和损坏拒绝；另通过注入后端/时钟/UART验证`main.run()`确实输出握手→有人→异常无效→有效0人，并在退出时释放资源。这仍是主机模拟，不是串口硬件实测。

输出记录：`tests/vision/host-unittest-2026-11-12.txt`。
`tests/vision/uart_samples.json`为**主机生成的软件样例，不是真实串口抓包**，包括EVQ、EVH、有效0/1人和无效占位。收尾时总控已补入`contracts/examples/uart.json`与`policy.json`；现已对公共query、hello、normal、invalid_detection四个发送向量逐字节比对通过，未修改公共文件。公共stream_cases是STM32接收EV1用例，不把K230的EVQ接收测试当作STM32验收。

## 安装视场与验收记录

固定相机和镜头，在小场景一侧斜看人员，使站立/坐姿躯干可见；先确认0—5人均能在画面中分开。实际高度、角度、距离由现场画面确定，不把未测建议数值当作安装规格。避开逆光窗、过暗和强遮挡，不用延长无人延时掩盖漏检。记录安装位置/高度/俯角/视场边界/最近最远距离/照明/画面截图，仅保留授权的本地测试材料。

| 测项 | 方法 | 本次硬件结果 |
|---|---|---|
| 官方原样例 | 原程序、原参数、配套模型；0/1人及FPS/日志 | 待连接后进行 |
| 摄像头检查 | 30帧640×480连续画面、形状/黑白异常 | 待进行 |
| 小场景0—5人 | 每人数10个独立片段，各取1个稳定结果，共60样本，分人数报告MAE；目标≤0.5人不是已达到 | 待进行 |
| 视觉故障 | 遮镜头、缺模型、模型哈希不符、采集错误；有效性必须为无效 | 待进行 |
| UART | 官方收发、握手、真实0/1人及无效帧、拔线、双方分别重启 | 待进行 |
| 稳定性 | 先30分钟视觉闭环，再配合总控11-27完成8小时测试 | 待进行 |

记录每段的时间、固件/脚本/模型SHA、环境、真实人数、检测人数、有效性、FPS、UART间隔、错误与日志路径。不要拿主机样例或历史截图替代本轮实测。

## 已知限制和下一步

无活体、无精确跟踪、无法识别完全遮挡/出视场人员；坐姿、小目标、背光和重叠可能漏检。极暗/饱和守卫仅检查像素范围，无法可靠识别普通遮挡或冻结画面，不能声称所有摄像头故障都会被主动发现。原模型精度及采样成本未知，需板测；没有发布FPS或精度承诺。

下一步依次补：连板preflight → 原摄像头与人体检测例程 → 适配后0/1人验证 → 0—5人场景记录 → 已确认接线UART单板与STM32联调。11-19前争取完成视觉到本地控制预验收、11-20为关口；11-25冻结模型/参数；11-27配合8小时测试。本模块没有修改总控接口、其他固件、云端、沙盒或旧工程。
