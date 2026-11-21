# 干簧管输入台架记录

## 2026-11-21 接口封装更新

用户要求直接封装进现有代码后，增加 `AppReed_GetSnapshot(AppReed_Snapshot *out)` 任务上下文接口，返回 `valid`、`do_high`、`sampled_at`。通过 RTOS 临界区复制快照；首次输入稳定 30 ms 前无效，距最近轮询采样达到 3000 ms 时对外无效，恢复采样后可恢复。调用方必须先判断 valid，不能把 do_high 直接当作窗户端点。快照测试覆盖初始无效、过期边界与恢复，并保留原消抖测试。此封装尚未烧录实测，不将旧版本电平变化记录转写为新版本验收。

## 2026-11-21 用户提供输入变化日志

用户在磁铁移动测试指导后贴出板端串口日志，其中 REED 事件依次为 0、1、0、1、0、1、0、1，共四组低→高转换。已按原顺序提取至 reed-evidence/2026-11-21/user-reed-events.log，文件明确标注为用户提供日志的事件摘录，不是完整抓包。可确认当前固件读取到双向稳定电平变化，GPIO 输入和消抖事件输出链路已实测有响应。日志未包含同步磁铁位置和时间戳，因此磁铁靠近／移开的具体对应及实际消抖时长不据此独立验收。

窗户尚未安装与标定，window=UNKNOWN / calibration=PENDING 为预期状态。只有验证闭窗位置、触发电平和重复到位后才映射“关闭到位”；高电平只能标“未确认关闭”，不表示全开。并行 ENV 日志 th_valid=0、err=-1 表示温湿度读数无效，本阶段未修复；VISION 重复 EVQ 只表明发送握手查询，不证明 K230 回应成功。

## 2026-11-21 烧录及初始输入实测更新

用户确认接线完成后，使用 ST-LINK 066BFF535153755087071921 将归档版本 reed-20261121.1 烧录到 0x08000000。SHA-256 核对一致，CubeProgrammer 2.22.0 返回 Download verified successfully，软件复位成功，退出码 0，目标电压 3.25 V。COM4 / 115200 / 8N1 捕获到版本行、FreeRTOS 心跳启动、LED/FAN 默认关闭初始化日志以及 `[REED] stable_do=1 window=UNKNOWN calibration=PENDING`。串口捕获结束后已关闭释放。见 reed-evidence/2026-11-21/flash.log 与 startup-serial.log。

该记录确认固件已运行并读到稳定高电平；磁铁当时位置未同步记录，不能据此独立确认“无磁为高”，也不能排除断线或接错位置。磁铁靠近／移开的低高转换仍待用户配合实测。下方“尚未烧录”为构建阶段历史记录，由本段更新。

2026-11-21。用户照片为三针模块，端子丝印 VCC、GND、DO，带电位器、PWR-LED、DO-LED。原始资料为用户指定 E 盘 Risym 模块目录中的《干簧管传感器模块.rar》，内含《干簧管传感器模块使用说明书.pdf》《干簧管传感器模块电路图.pdf》和 51 示例压缩包。已提取两份 PDF 文字；尚未逐线核验电路图与实物 PCB。

说明书写明工作电压 3.3～5 V，LM393 比较器、DO 数字输出；磁铁作用时低电平、无磁时高电平。该极性作为待实测的预期，磁铁距离和方向以实物为准。说明书尺寸为 3.2×1.4 cm，实物尺寸未测，板上电位器的实际作用及调节范围未确认，不预先改变其位置。

## 接线（全部使用内侧已焊排母）

| 模块端子（按丝印，不按照片左右顺序） | NUCLEO-F413ZH |
| --- | --- |
| VCC | CN8-7，3V3；本方案不使用 5 V 供电 |
| GND | CN10-27，GND，可与灯环和风扇共用地线分配点 |
| DO | PE13 / D3 / CN10-10，GPIO 输入、内部上拉 |

引脚依据 [UM1974 Rev11 表16，第51页](https://www.st.com/resource/en/user_manual/um1974-stm32-nucleo144-boards-mb1137-stmicroelectronics.pdf#page=51)。PE13 当前工程空闲，配置为普通输入，不启用 TIM1_CH3、EXTI 或 DMA；后续舵机不得再占用 PE13。模块使用 3.3 V 供电后与 MCU 同逻辑电源；上板前核对供电极性，若测 DO 电压异常则先断开 DO 查明原因。

## 固件

版本 reed-20261121.1。独立 app_reed.c/h，Keil App 组已引用。现有心跳任务约每 10 ms 采样，保持 500 ms 心跳翻转；稳定持续至少 30 ms 后产生首次有效值或变化事件。日志沿用 USART3 / COM4 / 115200 / 8N1。无等待磁铁的阻塞循环，不控制风扇或舵机，不改变 MQTT 字段和主题。

```text
[REED] stable_do=1 window=UNKNOWN calibration=PENDING
[REED] stable_do=0 window=UNKNOWN calibration=PENDING
```

预期磁铁远离为 1、靠近为 0，但必须通过实际移动磁铁验证。当前只输出电平，不把磁铁靠近自动等同于关闭到位。安装在闭窗端且验证极性后，才映射为“关闭到位”或“未确认关闭”。单传感器不提供全开反馈。内部上拉下断线可能读高，与磁铁远离无法区分，本版本不声称能够检测断线。

## 构建与验证

先备份 main.c、.ioc 和 .uvprojx 到 reed-evidence/2026-11-21/source-before，再修改；没有在原工程直接执行 CubeMX 再生成。

Keil AC6 6.16 全量构建：0 错误、427 告警。实际主机测试通过：初始未知、30 ms 门限、抖动重置、双向电平变化、无重复事件、uint32 毫秒回绕。源码与测试保存于当前工程及 tests/test_reed.c；日志、HEX 与哈希位于 reed-evidence/2026-11-21。

CubeMX 6.15.0 已在独立临时副本成功加载 .ioc 并完成代码生成（返回 OK）；检查生成结果，PE13 为 REED_DO 输入且启用 GPIO_PULLUP，用户区保留版本标识与 AppReed_Poll 调用。原工程未被生成器覆盖。当前 GPIO 用户区保底初始化与 CubeMX 后续生成的同配置重复执行时等效；重新生成合入时可统一到生成的初始化段。生成记录为 cubemx.log 与 cubemx-check.log。本次未对整个再生成副本另行构建，当前工程构建结果见 keil.log。

工作目录为总控工作区，复现：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File firmware/stm32/tests/build_fan.ps1 -EvidenceName reed-2026-11-21
powershell -NoProfile -ExecutionPolicy Bypass -File firmware/stm32/tests/test_reed.ps1
```

构建脚本沿用全工程构建入口，临时产物名含 fan-rebuild；本模块正式归档为 reed-evidence/2026-11-21/EcoVision_F413ZH-reed-20261121.1.hex。

硬件：本版本尚未烧录，模块供电与 DO 电平、磁铁靠近／移开、抖动、安装位置均待实测。不要将之前风扇固件的串口回执当作本模块验收。

下一步：断电按表接线，确认后烧录此版本；打开 COM4 并复位，记录初始值，磁铁靠近、移开各至少三次并保存原始日志；再讨论窗户端点与舵机联动。
