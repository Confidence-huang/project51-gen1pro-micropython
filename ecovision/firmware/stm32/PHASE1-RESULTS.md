# EcoVision STM32 第一阶段记录

日期 2026-11-17（北京时间）。固件 `phase1-20261117.1`，接口基线 `1.0.0`。原工程来自 `D:\移远杯项目文档\dsh work\stm32\EcoVision_F413ZH`。当前继续开发的工程为本目录的 [EcoVision_F413ZH](EcoVision_F413ZH/EcoVision_F413ZH.ioc)。

## 已修改文件

- 在工作区建原 CubeMX／Keil 工程副本。文件对比覆盖 1,464 个文件，其中仅 `Src/main.c` 的内容有变更。该文件在 USER CODE 中启动时输出固件版本，USART3 发送超时 25 ms。PB7/LD2 初始化为低电平，500 ms 后开始翻转作为板载心跳。停止调用原 AHT20、MQ-135 和舵机演示。镜像没有外接 LED、风扇和舵机的输出动作。
- 旧 `.ioc` 和 Keil 工程保留，阶段二引脚仅列在 [资源表](PHASE1-RESOURCES.md)。原生 AC6 产物与 [历史镜像](phase1-evidence/historical/Keil-2026-11-12.hex) 分开归档。

## 可复用代码

| 原工程内容 | 后续用途 |
|---|---|
| STM32Cube FW_F4 1.28.3 的 HAL、CMSIS、时钟、GPIO、SWD、USART3；Keil DFP 3.1.1 | 继续使用。原时钟依赖板载 8 MHz MCO 所在的 HSE bypass 路径 |
| `app_log.c` | USART3 调试格式化日志。高频联调前考虑发送队列或限速，旧实现的阻塞发送超时为 200 ms |
| `app_aht20.c` | 复用初始化命令和温湿度换算。旧采样有约 80 ms 等待和阻塞 I²C 调用，纳入控制循环前拆分触发与读取，校验有效性后更新样本 |
| `app_servo.c` | 参考 50 Hz、微秒脉宽计算。它直接写 TIM1，老 PE9/D6 与 UniKnect PWRKEY 冲突，阶段四重新选脚并通过 HAL 定时器、反馈和超时控制 |
| `app_mq135.c` | 留作分压、ADC 和趋势参考，核心原型未启用 |
| 组长 MicroPython 联调包 | 参考 AHT20、PC5 光敏、LCD、网络附着→NTP→TLS→MQTT QoS 1 流程。包内 `quectel.Network` 和 `umqtt` 使用套件固件，主题为 `classroom/room01/telemetry`，约 10–12 秒、retain=true。C/HAL 需用实际 AT 主串口实现，并按公共主题、5 秒周期及 retain=false 验证。实物记录属于组长版 |

## 构建与软件测试

| 检查 | 结果 | 日志 |
|---|---|---|
| 原样工程，沙箱内 Keil AC6 6.16 全量构建 | UV4 退出 2，1 错误、83 告警。Windows 启动 `D:\k51\ARM\ARMCLANG\Bin\armasm.exe` 返回 `0x26F`（无效的系统 DLL 重定位）。直接运行 `armasm.exe --vsn` 同样失败，ARM GCC 在该沙箱也遇到同类加载错误 | [沙箱内 Keil](phase1-evidence/keil-original.log)、[GCC 尝试](phase1-evidence/gcc-original.log) |
| 原样工程，沙箱外同一 Keil | UV4 退出 1，0 错误、83 告警，HEX 的 SHA-256 与历史 HEX 完全一致。直接查询 `armasm.exe --vsn` 成功 | [原样构建](phase1-evidence/keil-original-native.log) |
| 第一阶段，沙箱外 Keil AC6 6.16 | UV4 退出 1，0 错误、83 告警。Code=5692，RO-data=640，RW-data=12，ZI-data=1876。链接符号检查通过，旧传感器和舵机示例入口未链接 | [构建](phase1-evidence/keil-phase1-native.log)、[符号检查](phase1-evidence/phase1-image-check.log)、[第一阶段 HEX](phase1-evidence/EcoVision_F413ZH-phase1-20261117.1.hex)、[SHA-256](phase1-evidence/sha256.txt) |
| CubeMX 临时副本重生成 | 首次试验发现旧循环尾部位于 USER CODE 区之外，重生成后丢失循环闭合括号。修正后在临时副本再生成，保留版本打印和心跳。CubeMX 生成的 Keil 项目默认选 AC5 5.06u7，0 错误、0 告警。生成会省去原工程手加的 App 分组和包含路径，后续合并生成差异时从现有工程保留 AC6、DFP 和业务分组 | [重生成记录](phase1-evidence/cubemx-regeneration.log)、[失败记录](phase1-evidence/keil-regenerated-before-fix.log)、[重生成工程构建](phase1-evidence/keil-regenerated.log) |
| 公共离线用例 | 17 项通过，范围为公共契约、向量和既有实现 | [软件测试](phase1-evidence/contract-examples.log) |

从总控工作区用 PowerShell 运行以下命令。UV4 的退出码 1 表示有告警，需同时查看日志汇总。归档日志前去除本机许可证字段。

```powershell
$project = (Resolve-Path 'firmware/stm32/EcoVision_F413ZH/MDK-ARM/EcoVision_F413ZH.uvprojx').Path
$log = Join-Path $env:TEMP 'EcoVision-keil-rebuild.log'
$result = Start-Process -FilePath 'D:/k51/UV4/UV4.exe' -WindowStyle Hidden -Wait -PassThru `
    -WorkingDirectory (Split-Path $project) `
    -ArgumentList "-r `"$project`" -t EcoVision_F413ZH -j0 -o `"$log`""
$result.ExitCode
Select-String -LiteralPath $log -Pattern 'Using Compiler|Program Size|Error\(s\)|0x26F'
python -B -m unittest discover -s tests/integration -p 'test_*.py' -v
```

CubeMX 验证是在全新的临时副本复制 `.ioc`、`Src`、`Inc` 后执行。给 `D:/STM32CubeMX/STM32CubeMX.exe -q <脚本完整路径>` 提供以下三行，将首行路径换成临时副本的实际 ASCII 路径。生成后检查 `Src/main.c` 的版本行和用户代码区，再针对临时生成的 `.uvprojx` 重跑上述构建。

```text
config load C:/path/to/copy/EcoVision_F413ZH.ioc
project generate
exit
```

## 硬件实测

初次检查时，CubeProgrammer 2.22.0 通过 `-l` 枚举 ST-LINK V2J46M32、VCP COM4、Quectel USB AT COM10。使用 `-c port=SWD mode=HOTPLUG` 识别 Device ID 0x463、STM32F413/F423 Rev A、1.5 MB、3.24 V。当时 COM4 以 115200/8N1 被动读取 14 秒超时。详见 [初次 SWD 日志](phase1-evidence/swd-identify.log)、[枚举日志](phase1-evidence/cubeprogrammer-list-native.log)。

组长确认 MicroPython 镜像及配置已有备份，并确认只接 NUCLEO 后，重新用 SWD 确认目标并烧录 `phase1-20261117.1`。CubeProgrammer 校验成功并复位，COM4 收到固件版本和单板提示两行。通过 SWD 读取 GPIOB ODR，观测到 PB7 的高、低两种状态，PB0 与 PB14 在两次采样均为 0。该寄存器采样未测 LED 实际发光、精确翻转周期或复位瞬态。详见 [烧录与校验](phase1-evidence/standalone-flash.log)、[复位串口](phase1-evidence/standalone-vcp.log)、[PB7 采样](phase1-evidence/standalone-pb7.log)。

随后组长目视确认板载 LD2 闪烁。通过 SWD 只读采样 GPIOC IDR，记录到 PC13=1。该次采样按 B1 松开处理，按下与松开转换需在同步操作时再测。详见 [PC13 首次采样](phase1-evidence/standalone-b1-rest.log)。

```powershell
$cli = 'C:/Program Files/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin/STM32_Programmer_CLI.exe'
$hex = (Resolve-Path 'firmware/stm32/phase1-evidence/EcoVision_F413ZH-phase1-20261117.1.hex').Path
& $cli -c port=SWD mode=UR -w $hex -v -rst
& $cli -c port=SWD mode=HOTPLUG -r32 0x40020414 0x4
```

## 未完成项

第一阶段单板的下载校验、复位日志、PB7 寄存器采样和 LD2 目视观察已完成。外接驱动上电和复位期间保持关闭的验证需在驱动接入后进行。第二阶段 K230 会话、LED／风扇与实体按键、第三阶段 AT 主 UART 与 4G/MQTT/ACK、第四阶段窗户与红外均待实现和验证。

## 下一步

1. 在 NUCLEO 单板上测 B1 按下和松开电平，随后验证消抖和 PB7/TIM4_CH2 PWM。
2. 提供 LED／风扇驱动型号或端子照片、风扇线数。依据实物确定引脚和安全默认电平，接入台架驱动并实测。
3. 先用测试帧验证本地控制。接 K230 前确认载板版本、J308 和 K230 端 FPIOA/电平，再保存双向原始串口抓包和负载动作记录。按阶段三顺序验证 EC200U 主 UART。
