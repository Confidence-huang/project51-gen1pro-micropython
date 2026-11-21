# 移远载板 LCD 白屏修复

2026-11-20，NUCLEO-F413ZH + UniKnect ST7735 shield。

后续版本：已参考组员联调包恢复温湿度、光敏与人数同屏显示；当前固件和实测见 [ENVIRONMENT-DISPLAY-RESULTS.md](ENVIRONMENT-DISPLAY-RESULTS.md)。本文保留白屏修复版的历史证据。

## 原因

将原 MicroPython 固件替换为 C/HAL 串口固件时，串口工程没有包含 SPI1 和 ST7735 初始化/刷新代码。用户确认白屏的是 STM32/移远载板 LCD。不能把这次白屏归咎于 K230 UART 接线，也没有证据表明屏幕硬件损坏。

## 修改

- `EcoVision_F413ZH/App/Src/app_lcd.c`：SPI1，PA5 SCK/PA7 MOSI、PF12 DC、PD14 CS，6 MHz、mode 0、RGB565、160×128 横屏。LCD RESET 与板 NRST 相连，使用显示控制器软件复位，不驱动 NRST。
- `App/Src/lcd_view.c`：PEOPLE、人数、UART 状态和序号；有效无人显示 0，无效/未握手显示 --。
- `App/Src/app_vision.c`：初始化显示，每次接收新有效协议帧刷新，断流/重握手清除旧人数。LCD SPI 错误时记录错误并保持 UART 任务运行。
- 启用 HAL_SPI_MODULE_ENABLED，加入 HAL SPI 驱动及两个 LCD 源文件，固件版本 `uart-lcd-20261120.2`。
- 不改变 K230 模型、阈值、UART 帧格式或灯/风扇控制规则。本次恢复人数显示，不等于原 MicroPython 的全部传感器/云端页面恢复。

接线来源：本机原示例 `D:/移远杯项目文档/hjw works/移远杯_组长联调包_2026-11-16/移远杯_组长联调包_2026-11-16/02_移远官方示例历程_参考/03_LCD_ST7735/lcd1.py`，及 `D:/移远杯项目文档/ec200u资料/uniknect-micropython/uniknect-micropython/docs/schematics/Schematic_Arduino-1.8''-TFT-Shield_2026-01-26.pdf`。原理图渲染见 `lcd-evidence/lcd-schematic.png`。NUCLEO 引脚对照 [ST UM1974](https://www.st.com/resource/en/user_manual/dm00244518-stm32-nucleo-144-boards-mb1137-stmicroelectronics.pdf)。

## 验证

1. 渲染主机测试先失败于缺失新实现，再实现通过；覆盖缓冲区越界保护、0/12 人、无效占位、未握手、超范围和 0..20 人。
2. 既有 C UART 协议断言套件通过。
3. Keil AC6：0 错误，414 告警，含既有 HAL/RTOS 和结构对齐等告警；本驱动因 HAL SPI API 接受可写指针保留 const 强转告警。Code=39214，RO-data=2706，RW-data=16，ZI-data=71176。
4. CubeProgrammer 下载校验成功并复位。
5. 真机日志 `ST7735 ... init=OK`，连续 `[LCD] updated count=13/14 ...`，对应 UART 人数接收继续工作。启动采样 heap_free=6216 字节，task_stack_free=2584 字节，不代表最坏情况下的剩余栈。
6. **用户实物确认：已经显示 PEOPLE 和人数。**本次白屏症状恢复；不宣称颜色测量、长时间稳定性或识别精度已验收。

最终 HEX：`lcd-evidence/EcoVision-uart-lcd-20261120.2.hex`。

证据：`lcd-evidence/flash.log`、`flash-and-lcd-live.log`、`host-render-tests.log`、`keil-build.log`。修改前源码：`lcd-evidence/source-before/`；上一版串口固件：`uart-evidence/EcoVision-uart-20261120.1.hex`。
