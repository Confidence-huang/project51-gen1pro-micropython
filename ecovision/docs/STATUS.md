# 现状检查记录

检查日期：2026-11-12；范围：当前工作目录的文件清单、Markdown正文和文档生成脚本。没有连接实物、云账户或其他聊天。

| 材料 | 检查结论 |
|---|---|
| EcoVision项目策划书V4.1优化稿.md | 12个月长期计划；明确EC200U及≤5000元边界；不用于本次排期 |
| EcoVision二十天原型机完整实施方案.md | 提供低压负载、AUTO/REMOTE/LOCAL_OFF、EV1帧与MQTT候选；D1无日期，20天表不是本次日历 |
| EcoVision可行性评估与修订说明.md | 研究目标与实测成果需区分；硬件/计量/节能结论有条件 |
| V4优化稿、source_full.txt、已有DOCX和渲染图片 | 历史来源；本次不修改，未重新逐页审查DOCX排版 |
| review_work/*.py、*.ps1 | 文档/图片生成与渲染脚本，不是K230、STM32或云端运行代码 |
| delete-lenovo.ps1 | 非本项目实现，不运行、不修改 |

检查时不存在 docs/、firmware/、cloud/、sandbox/、contracts/、tests/integration/，未找到 AGENTS.md、独立最新每日计划或模块工程。`git status --short`报告当前目录不是Git仓库，不能引用提交号证明来源。本次未初始化Git、未执行历史脚本。

初始方案缺口：UART重启握手未定、字段与ACK未完整定义、时效边界/幂等容量/本地接管后旧消息规则未定。由总控在1.0.0中补齐；旧文档的EV1五字段候选不是已交付的协议实现。当前版增加会话字段，具体差异见contracts/CHANGELOG.md。

收尾复查时共享目录出现firmware/k230/代码、官方模型资产、tests/vision/与docs/modules/vision.md、embedded.md。它们不属于本次总控新增文件，未覆盖或修改。已读取K230协议实现、模块记录及现有主机日志，并另行重跑主机测试与公共字节向量交叉验证，结果见tests/integration/RESULTS.md。模块记录中的型号/历史板测来源尚未独立核实，不升级为总控硬件结论。embedded.md所写“统一接口缺少”为其较早快照，现已落盘1.0.0。

总控新增文件的验证结果写入tests/integration/RESULTS.md。合同样例检查通过仅表示离线样例与结构一致，不表示真实串口、4G、TLS、负载或8小时测试通过。初始未发现代码是盘点时点结论，不代表共享目录之后不会继续出现模块交付。
