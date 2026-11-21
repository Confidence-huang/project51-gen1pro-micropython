# EcoVision 绿智微视

执行周期：2026-11-14 晚—2026-11-29（北京时间）。公共接口基线为1.0.0；本机已有 K230→STM32 人数通信和板载环境/LCD 实测，4G、云端和整机集成按各模块最新证据分别验收。

先读 [项目与每日计划](docs/PROJECT.md)、[统一接口](docs/INTERFACES.md)、[验收方法](docs/ACCEPTANCE.md)、[联调指南](docs/INTEGRATION.md)。检查发现及来源见[现状记录](docs/STATUS.md)。公共结构与正常/故障样例在[contracts](contracts/README.md)。

## 2026-11-20 交接与协作入口

[队长接手与双仓库协作](docs/collaboration/README.md) 已汇总用户提供的网页/板端 Git 协作方案，含原文、适用于当前代码的接手清单和 Issue/PR 模板。当前目录是本机集成工作区，不是方案中 Vite 网页仓库或 MicroPython 仓库的完整克隆；构建与发布应在各自实际 Git 根进行。

本机最新硬件证据见 [K230→STM32 串口](firmware/k230/UART-STM32.md) 和 [板载环境同屏显示](firmware/stm32/ENVIRONMENT-DISPLAY-RESULTS.md)：人数通信与温湿度/光敏/LCD 已有实测，当前 C 固件尚未恢复 EC200U 4G/MQTT。外部 Pages/API 的文档快照不能直接作为本机端到端验收。

## 公共接口检查

```powershell
python -B -m unittest discover -s tests/integration -p "test_*.py" -v
```

这是离线合同检查。真实视觉、STM32控制、EC200U真实4G、云端运行和8小时硬件验收均需模块实际交付与证据，不能由此命令推断通过。旧20天方案与12个月策划书保留为参考，不覆盖当前每日计划。
