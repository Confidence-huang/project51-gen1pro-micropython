# NUCLEO-F413ZH FreeRTOS 接入记录

2026-11-17（北京时间）。固件 `rtos-20261117.1`，接口基线 1.0.0。

## 工程配置

- `EcoVision_F413ZH.ioc` 启用 FreeRTOS 10.3.1 / CMSIS-RTOS2，1 kHz tick，`heap_4` 4 KiB。SysTick 用于调度，TIM6 用于 HAL 的 1 ms 时基。既有硬件引脚分配继续使用。 [STM32CubeMX 时基说明](https://www.st.com/resource/en/user_manual/dm00104712-stm32cubemx-for-stm32-configuration-and-initialization-c-code-generation-stmicroelectronics.pdf)
- `Src/main.c` 在 USER CODE 中实现 `StartHeartbeatTask`。任务栈为 1 KiB、优先级 Normal。任务启动后调用 RTOS 延时，测得独立 HAL tick 在预期范围后才打印成功日志。随后用 RTOS 延时控制 PB7/LD2 每约 500 ms 翻转。本阶段没有启动舵机、风扇或其他外部输出。
- `Inc/FreeRTOSConfig.h`、`Src/stm32f4xx_hal_timebase_tim.c` 与 FreeRTOS 中间件来自本机 STM32Cube FW_F4 1.28.3。Keil 工作工程保留 AC6 和自定义 App 分组，使用同一固件包中的 Cortex-M4F GNU 语法 port。
- 首次上板时 CubeMX 生成的 TIM6 IRQ 没有调用 HAL。SWD 停核定位到空中断处理函数，此时 TIM6 更新标志置位，`uwTick` 与调度器启动状态为 0。已在 `stm32f4xx_it.c` 的 USER CODE 区加入 `HAL_TIM_IRQHandler(&htim6)`。复测使用修正后的 HEX。 [首次调试日志](rtos-evidence/startup-debug.log)

## 构建与实测

| 检查 | 结果 | 记录 |
|---|---|---|
| 工作工程 Keil AC6 6.16 全量构建 | 0 错误、363 告警，Code=15166，RO-data=694，RW-data=16，ZI-data=9448。告警主要为严格告警配置下的分号和填充诊断。链接确认 SVC、PendSV、SysTick、TIM6 回调及调度器入口 | [构建](rtos-evidence/keil-rtos.log)、[链接符号](rtos-evidence/linked-rtos-symbols.log) |
| CubeMX 临时副本重生成 | 保留心跳任务与恰好一处 TIM6 HAL 派发。用生成工程默认的 AC5 5.06u7 构建为 0 错误、0 告警。工作副本构建仍以 AC6 为准。采用 Keil AC6 时从工作工程合并生成差异，保留 App、DFP 和 GNU 语法 port 设置 | [保留检查](rtos-evidence/cubemx-regeneration.log)、[AC5 构建](rtos-evidence/keil-rtos-regenerated-fixed.log) |
| 公共离线回归 | 17 项通过 | [测试日志](rtos-evidence/contract-examples.log) |
| NUCLEO 单板烧录，CubeProgrammer 2.22.0 | SWD 烧录校验成功。复位后 COM4 记录版本和 `FreeRTOS heartbeat running; HAL TIM6 tick OK`，SWD 采到 PB7 高低电平。采样用于确认翻转，未精确测量周期 | [烧录](rtos-evidence/flash.log)、[串口](rtos-evidence/vcp.log)、[PB7](rtos-evidence/pb7.log) |

## 复现

Keil 全量构建和 CubeMX 临时副本重生成命令见 [第一阶段报告](PHASE1-RESULTS.md)。按该报告的方式保留 Keil 设置，CubeMX 生成差异经检查后再合并。已验证的 [RTOS HEX](rtos-evidence/EcoVision_F413ZH-rtos-20261117.1.hex) 和 [SHA-256](rtos-evidence/sha256.txt) 已归档。

```powershell
$cli = 'C:/Program Files/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin/STM32_Programmer_CLI.exe'
$hex = (Resolve-Path 'firmware/stm32/rtos-evidence/EcoVision_F413ZH-rtos-20261117.1.hex').Path
& $cli -c port=SWD mode=UR -w $hex -v -rst
& $cli -c port=SWD mode=HOTPLUG -r32 0x40020414 0x4
python -B -m unittest discover -s tests/integration -p 'test_*.py' -v
```

烧录前打开 USART3 VCP 监听，115200 / 8N1。下一步用单板确认 B1 极性与消抖，把 LD2 从心跳 GPIO 改成 TIM4_CH2 PWM 试验，再按驱动器实物接入低压风扇。
