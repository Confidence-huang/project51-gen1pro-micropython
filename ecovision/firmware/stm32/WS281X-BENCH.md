# 16 灯 WS281x 灯环点亮测试

实物背面朝上、四针朝下时，照片中从左到右为 `DO / GND / 5V / DI`。接线时用 PCB 丝印复核。

| 灯环 | 台架接法 |
| --- | --- |
| 左起第 1 针 `DO` | 留空 |
| 左起第 2 针 `GND` | 接独立 5 V 电源负极、NUCLEO 的 CN12-20 和数据缓冲器 GND |
| 左起第 3 针 `5V` | 接独立稳压 +5 V，同时给缓冲器供电。NUCLEO 继续用 CN1 USB 供电 |
| 左起第 4 针 `DI` | NUCLEO PB11（CN12-18）→ 74AHCT125 → 330 Ω 串联电阻（靠近灯环）→ DI |

使用裸 SN74AHCT125 第 1 路时，脚 14 接 5 V，脚 7 和脚 1 接 GND，脚 2 接 PB11，脚 3 经串联电阻接 DI。芯片供电旁放 100 nF 去耦，剩余通道输入和使能脚接确定电平。全部断电接线后复查共地及供电极性。资料的 DI 高电平下限为 `0.7×VDD`，5 V 供电时为 3.5 V，因此选择 3.3 V→5 V 的缓冲方案。 [灯环资料](<E:/移远杯资料文档/模块资料/WS281x RGB灯/数据手册/WS2812 数据手册.pdf>) · [TI SN74AHCT125](https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf) · [ST UM1974 表 21](https://www.st.com/resource/en/user_manual/um1974-stm32-nucleo144-boards-mb1137-stmicroelectronics.pdf#page=70)

## 测试固件

台架副本加入 [ws281x_bench.c](tests/ws281x_bench.c)，使用 PB11 AF1、TIM2_CH4，定时器更新事件经 DMA1 Stream7 Channel 3 搬运 CCR4 计数值。时钟 96 MHz，位周期 1.25 µs，GRB 高位先发。启动先发全黑帧，随后周期刷新，只点第 1 颗，绿色值 8，其余 15 颗保持黑色。板载 LD2 继续提供心跳。

Keil AC6 6.16 全量构建为 **0 错误、378 告警**，链接检查通过。测试版本在独立副本构建，主工程未修改。 [HEX](ws281x-evidence/EcoVision_F413ZH-ws281x-bench-20261117.1.hex) · [构建日志](ws281x-evidence/keil-ws281x-bench.log) · [SHA-256](ws281x-evidence/sha256.txt)

用户用 CubeProgrammer 烧录并校验成功，现场反馈灯环仍未亮。SWD 读回 Flash 版本标记与该 HEX 一致，PB11 为 AF1，TIM2 已启动且 ARR=119，DMA 源地址指向灯环数据缓冲，DMA 目的地址指向 CCR4，采样时缓冲前六项为 `37,37,37,37,70,37`，剩余传输数为 0。该采样用于核对 MCU 的配置和数据，灯环端供电及 DI 电平、实际波形仍待测。 [SWD 寄存器记录](ws281x-evidence/led-dark-runtime.log)

复现构建时，在临时工程副本的 App 组加入测试 C 文件，并在 main.c 的 USER CODE 区加入 stdbool.h 和两个公开函数声明。在外设初始化后调用 `Ws281xBench_Init()` 和 `Ws281xBench_Show(false)`，在心跳循环翻转 PB7 后调用 `Ws281xBench_Show(true)`，用 [第一阶段的命令](PHASE1-RESULTS.md#构建与软件测试) 全量重建。
