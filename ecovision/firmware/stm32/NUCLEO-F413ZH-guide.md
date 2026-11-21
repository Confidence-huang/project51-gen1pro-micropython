# NUCLEO-F413ZH 资料索引与上板指南

适用项目为 EcoVision 绿智微视。资料核对日期为 2026-11-15。开发板型号已记录为 NUCLEO-F413ZH，实际 PCB 版本和跳帽、焊桥状态待实物核对。

## 官方资料

| 资料 | 查什么 |
| --- | --- |
| [UM1974 开发板手册 Rev 11](https://www.st.com/resource/en/user_manual/um1974-stm32-nucleo144-boards-mb1137-stmicroelectronics.pdf) | 首先看图 4（第 13 页）和图 13（第 35 页）找接口。第 7.3–7.6 节查烧录、供电、LED、按键，第 7.9 节和表 12 查 USART3 与焊桥，第 49–52 页表 16 查 F413ZH 的 Zio 排针，第 70–71 页表 21 查 Morpho 排针。 |
| [DS11581 芯片数据手册](https://www.st.com/resource/en/datasheet/stm32f413zh.pdf) | 查 STM32F413ZHT6 的引脚复用（AF）、输入输出电气指标、供电和封装。芯片为 Cortex-M4F，最高 100 MHz，配有 1.5 MB Flash、320 KB SRAM。 |
| [RM0430 芯片参考手册](https://www.st.com/resource/en/reference_manual/dm00305666-stm32f413-423-advanced-arm-based-32-bit-mcus-stmicroelectronics.pdf) | 查 RCC 时钟、GPIO、USART、定时器及 DMA 的工作方式和寄存器。 |
| [MB1137 官方原理图包](https://www.st.com/resource/en/schematic_pack/nucleo_144pins_sch.zip) | 根据板背面丝印匹配 PCB 版本，查供电、排针和焊桥的实际走线。下载入口也在 [ST 产品页](https://www.st.com/en/evaluation-tools/nucleo-f413zh.html)的 Schematic Pack 一栏。 |
| [STM32CubeF4 官方代码与示例](https://github.com/STMicroelectronics/STM32CubeF4) | 查 F4 HAL，按 `Projects/STM32F413ZH-Nucleo` 找同板型示例。 |

## 第一次上板

1. 先单独接 Nucleo。用可传数据的 **Micro-USB（Micro-B）** 线接标有 **USB ST-LINK** 的 `CN1`。保留 `CN4` 上连接板载目标的两只跳帽，确认 `JP5` 已短接，USB 供电时核对 `JP3` 在 `U5V`（3–4）位置。查看 `LD6` 电源灯。板载 ST-LINK/V2-1 可同时提供 SWD 调试和虚拟 COM 口，用户 USB `CN13` 是 MCU 的 USB OTG 接口。[UM1974 §7.3–7.7](https://www.st.com/resource/en/user_manual/um1974-stm32-nucleo144-boards-mb1137-stmicroelectronics.pdf#page=17)
2. 用 STM32CubeMX 的 Board Selector 选择 `NUCLEO-F413ZH`，配置 `PB7` 为推挽输出，初始为低电平。最小测试可采用内部 HSI 时钟。在 `while (1)` 的用户代码区调用 `HAL_GPIO_TogglePin(GPIOB, GPIO_PIN_7)`，再调用 `HAL_Delay(500)`。用 STM32CubeIDE 编译，通过板载 ST-LINK 下载和运行。CubeIDE 2.x 的配置和代码生成在独立 CubeMX 中完成。[STM32CubeMX](https://www.st.com/en/development-tools/stm32cubemx.html) · [STM32CubeIDE 2.0 发布说明](https://community.st.com/stm32-software-tools-165/what-s-new-in-stm32cubeide-2-0-0-159478)
3. 用 [STM32CubeProgrammer](https://www.st.com/en/development-tools/stm32cubeprog.html) 也可以通过 `ST-LINK / SWD` 识别目标、烧录 `.elf` 或 `.hex` 并校验。若 Windows 无法识别 ST-LINK，先检查 `CN1`、数据线和设备管理器，再检查 [STSW-LINK009 驱动](https://www.st.com/en/development-tools/stsw-link009.html)。
4. 看到蓝色 `LD2` 每 500 ms 翻转并能在按 `B2 RESET` 后恢复闪烁，即可记录最小程序运行结果。三颗用户 LED 均为高电平点亮。绿灯 `LD1` 由 `PB0` 或 `PA5` 驱动，取决于焊桥，蓝灯 `LD2 = PB7`，红灯 `LD3 = PB14`。用户按键 `B1` 默认接 `PC13`，可用于后续本地控制验证。[UM1974 §7.5–7.6](https://www.st.com/resource/en/user_manual/um1974-stm32-nucleo144-boards-mb1137-stmicroelectronics.pdf#page=25)

## EcoVision 串口候选

如果实物是 **UniKnect Gen1 Pro QADP V1.1** 且按 Nucleo-144 档叠插，扩展板会占用 `D0/D1`（USART6）。该装配方式建议 EC200U 用 USART6、K230 用 USART2、日志用 USART3。见 [EC200U 叠插接线与联调指南](EC200U-EcoVision-guide.md#4-与-nucleo-f413zh-叠插后的串口分配)。

下表用于独立载板通过跳线接入 UART 的候选布局。

表中的 TX / RX 均以 STM32 为视角。排针编号依据 UM1974 表 16，选型沿用[嵌入式模块检查记录](../../docs/modules/embedded.md)。

| 用途 | STM32 外设 | TX | RX | GND 或连接方式 |
| --- | --- | --- | --- | --- |
| K230 视觉链路 | USART6 | `PG14` → `CN10-14 (D1)` | `PG9` → `CN10-16 (D0)` | `CN10-22 (GND)` |
| EC200U 主 AT 口 | USART2 | `PD5` → `CN9-6 (D53)` | `PD6` → `CN9-4 (D52)` | `CN9-12 (GND)` |
| PC 调试日志 | USART3 | `PD8` | `PD9` | 经板载 ST-LINK 虚拟 COM 口接 PC |

- K230 按[统一接口 1.0.0](../../docs/INTERFACES.md#2-k230-uartascii--crc--显式会话)使用 `115200, 8N1, 无流控`。STM32 发 `EVQ`，K230 回 `EVH` 后发送 `EV1`，因此两根数据线都需要。确认对端排针及 UART 电平后，TX 接对端 RX、RX 接对端 TX，双方共地。
- EC200U 先核对载板型号、实际主 AT 口及其逻辑电平，再确定直连或电平转换。USART2 硬件流控候选为 `PD4 / CN9-8 (RTS)`、`PD3 / CN9-10 (CTS)`，按模组固件和接线状态配置。给模组载板按其规定单独供电，Nucleo 与对端只接已核对的信号和 GND。
- USART3 优先保留给 PC 日志，台架可用 `115200, 8N1, 无流控`。`PD8/PD9` 还涉及 Morpho 排针。用作外部 UART 时需按实物和手册核对 `SB5/SB6`、`SB7/SB4`，避免外部 TX 与板载 ST-LINK TX 同时驱动 `PD9`。[UM1974 §7.9 及表 12](https://www.st.com/resource/en/user_manual/um1974-stm32-nucleo144-boards-mb1137-stmicroelectronics.pdf#page=27)

## 本地控制验证顺序

1. **板载 LED 和日志。** 点亮 `LD2`，再让 USART3 周期打印日志。记录 CubeProgrammer 目标识别、下载校验和 LED 实际表现。
2. **两路串口。** 外设暂断开，用确认是 3.3 V 逻辑的 USB 转 TTL 模块逐路验证 USART6 和 USART2 双向收发。之后接 K230 验证握手，接 EC200U 验证 AT 响应。EC200U 的波特率、流控和供电参数以实际载板与固件为准。
3. **实际负载。** 先用板载 LED 验证状态变化，再接 5 V 风扇。采用可由 3.3 V GPIO 控制的 MOSFET 驱动或驱动模块，风扇由独立 5 V 电源供电并与 MCU 共地。确认驱动输入有效电平，给驱动输入适当偏置以维持复位期间关闭，并实测上电、复位和关断时的风扇状态。

本轮完成官方文档与项目接口核对。工作区的 STM32 模块原有内容仅为占位文件，固件构建、烧录、串口和负载实测均待执行。第一次台架验证只需 Nucleo 实物、板背面版本丝印以及一根可传数据的 Micro-USB 线。
