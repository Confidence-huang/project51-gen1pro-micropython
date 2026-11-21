# 参考组员联调包恢复板载模块显示

2026-11-20，当前固件 `uart-env-lcd-20261120.3`。

只读参考用户指定联调包 `01_STM32板端工程_已验证/src/screen.py`、`environment.py`、`main.py` 及 README。原包未修改，未读取 MQTT 密码。保留其人数、温度、湿度、光敏 ADC 和链路状态的布局与语义；原包人数为 None，本版接入真实 K230 UART。

| 页面项目 | 当前数据来源 |
|---|---|
| PEOPLE | K230 UART 的新鲜计数；异常/未握手显示 -- |
| TEMP / RH | I2C1 地址 0x38 的真实 AHT20，同一数据帧；失败/过期显示 -- |
| ADC16 | PC5 ADC1_IN15 的 12 位原码，按位扩展到 16 位表示，同时保留 ADC12 日志；不是 lux |
| UART / SEQ | 当前实际握手状态和接收序号 |
| NET:NOTINIT | C 固件尚未恢复 4G/MQTT，不伪装原 MicroPython 固件的在线状态 |

新增独立低优先级环境任务（2048 字节栈），约每秒采样一次，避免 AHT20 的等待阻塞人数接收任务。LCD 每秒消费受保护的快照，3 秒过期使环境数据无效。AHT20 C 驱动新增 CRC8、忙/校准状态与范围检查；温湿度故障与光敏故障独立处理。

主要代码：`EcoVision_F413ZH/App/Src/app_environment.c`、`environment_codec.c`、`lcd_view.c`、`app_lcd.c`、`app_vision.c`、`app_aht20.c`，及对应头文件、main.c 和 Keil 工程。

## 验证

- 主机测试覆盖 AHT20 CRC8 标准向量、已知原码换算、坏帧/忙/未校准拒绝、ADC12→16 端点；显示空值、有效零、负温、满量程和缓冲区边界。
- Keil 0 错误、427 告警（含既有 HAL/RTOS 与结构对齐等告警），Code=44438、RO-data=2838、RW-data=16、ZI-data=71208；烧录校验成功。
- 实际日志样例：temp_x100=2610、rh_x100=1811、ADC12=1531、ADC16=24501、th_valid=1、adc_valid=1、err=0；同时 K230 count=14、序号继续递增。仅是一次实测，不代表传感器校准准确度或人数识别精度通过。
- 启动采样 heap_free=4064 字节、视觉任务 stack_free=2520 字节；不代表全部任务的最坏资源验收。
- **用户实物确认：PEOPLE、TEMP、RH、ADC16 四项显示正常，没有文字重叠。**

最终 HEX：`environment-evidence/EcoVision-uart-env-lcd-20261120.3.hex`。

证据：`live-environment-display.log`、`flash.log`、`keil-build.log`。修改前的 LCD 人数版源码在 `environment-evidence/source-before/`，旧 HEX 仍保留在 `lcd-evidence/`。

`dashboard-preview.png` 是 C 渲染器生成的模拟排版预览（12 人、25.1°C、50.3%RH、ADC16=23029），不是实物照片或实测证据。

组员 4G/MQTT 实现继续作为后续适配来源；本次未恢复其全部传感/云端链路，也没有修改公共协议、网络主题、账号或凭据。自动控制、长测、CubeMX 整体重新生成兼容性均未在本轮验收。
