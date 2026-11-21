# EcoVision 工程快照：2026-11-21

这是现有成果的工程快照，不是整机验收通过或最终发布。

## 对应目标

- board包：Confidence-huang/project51-gen1pro-micropython。
- web包：Confidence-huang/project51-classroom-dashboard。

两个包均只新增ecovision/子目录，保持原仓库的src、README、package.json、部署docs、板端入口及已工作方案。当前没有远端写入；连接账号yillnnn在核查时对两仓均为push=false。待取得写入权限后，分别在新分支上传，不直接修改main或自动部署，不合并PR。

板端包保存本机C/HAL、K230、算法、公共契约和相关检查。它与原仓库MicroPython镜像是不同运行版本，不会同时在一颗STM32运行。网页包保存本机独立cloud原型、沙盒、公共契约和软件检查，不覆盖线上Vite网页，不声称已经与现网接口适配。

## 已核实状态

- 本轮实际运行离线接口检查17项、视觉主机检查32项，均通过；仅为软件检查。
- 历史证据支持K230→STM32 UART及LCD环境显示；计数精度仍待独立验证。
- 干簧管有电平切换记录，窗户开关映射待标定；新增快照封装未烧录。
- BH1750软件已有构建及主机记录，尚未完成真实读数验收。
- 风扇F0有回执，机械起转停转待实物确认。
- 当前C固件的AUTO、EC200U 4G及下行ACK、30分钟联合和8小时综合测试尚未通过。
- 固件目录同时含源码和历史证据；历史HEX不代表与快照中最新源码一致，不自动烧录。

## 入口与复现

- 先读docs/PROJECT.md、INTERFACES.md、ACCEPTANCE.md、INTEGRATION.md及docs/daily/2026-11-21.md。
- STM32：firmware/stm32/EcoVision_F413ZH/EcoVision_F413ZH.ioc；Keil工程在MDK-ARM/EcoVision_F413ZH.uvprojx。工具链、资源及实测记录见模块目录文档。需在正确工具链另行构建，不据本快照宣称重新构建通过。
- K230：firmware/k230/figurine_uart.py；配套模块见UART-STM32.md。模型保留原相对路径figurine-pilot/multi-15-training/selected/figurine_multi.kmodel，部署到板上/sdcard/kmodel/。正式UART入口NMS为0.3，历史部署记录可能记0.5；以UART-STM32.md当前入口为准。
- 本包ecovision目录中运行：python -B -m unittest discover -s tests/integration -p "test_*.py" -v；board包另运行python -B -m unittest discover -s tests/vision -v。
- web包按cloud/README.md安装锁定依赖并运行本机原型；它不是外层Vite项目。沙盒按sandbox/README.md通过本机HTTP服务读取contracts。

## 收录与排除

保留源码、配置模板、依赖锁文件、原厂许可文件、公共样例及相关文本验证记录；每个源文件的SHA-256见UPLOAD-MANIFEST.json。

排除实际运行秘密与证书目录、node_modules、缓存、整片Flash备份、构建中间产物、训练过程权重与数据集、个人IDE设置、申报材料及与工程无关文件。日志和文档所指向的旧备份或图片可能未收录；完整原件仍在本机，不删除。敏感模式扫描只是辅助核查，不替代配置归属审阅。不能把缺失数据写成有效0，不能把模拟记录记为实物通过。

预算≤5000元；核心里程碑仍为24日4G与远控、25日冻结、27日8小时、29日交付。未付费、未部署、未写入凭据。
