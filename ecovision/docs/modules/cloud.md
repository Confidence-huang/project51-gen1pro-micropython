# 云端模块交付记录

## 2026-11-16 · 网页和微信小程序

- 新增 `cloud/miniprogram/` 原生微信小程序，前台每约 2 秒读取环境信息、设备模式、输出和故障。显示云端最后接收时间、模拟标记及数据过期状态。
- `cloud/src/server.cjs` 新增只读 `GET /api/monitor/{device_id}/latest`，只认绑定单设备的独立令牌，拒绝写入。网页继续共用同一个已校验的设备快照和原有操作员权限。新增 `public_origin` 配置支持目标 HTTPS 来源。
- `cloud/config/` 新增 ECS 的 systemd、Nginx WebSocket 和 API 反代模板。 `cloud/scripts/publish-sample.cjs` 提供独立 TLS MQTT 样例上报。导入、部署与接板步骤见 `cloud/miniprogram/README.md` 和 `cloud/DEPLOY-ECS.md`。
- 11-16 总控进度表记录的集成超时对应运行日志 `EACCES`（回环连接失败）。允许本机回环通信后，原测试可通过。此轮追加单设备只读权限、HTTPS Origin、样例上报和小程序 JS 生命周期验证。
- 当前只有 ECS 公网 IP。目标 Nginx、Mosquitto、微信开发者工具编译、真机小程序及 EC200U 4G 仍待联调。正式小程序需要实际 AppID 和 HTTPS 合法域名。公共 MQTT 契约未修改。

日期：2026-11-12（Asia/Shanghai）。接口基线：1.0.0；未修改公共字段/主题/优先级。仅修改cloud/、tests/cloud/及本文件。

## 当前交付

- `cloud/src/core.cjs`：直接读取公共schema/policy、严格JSON/大小/跨字段校验、按boot_id与uint32模序去重；独立telemetry/status水位；云端单调时间判STALE；命令会话/epoch/唯一ID/UTC/TTL与租期；PENDING/10秒TIMEOUT/迟到ACK历史，不用ACK覆盖实时遥测。
- `cloud/src/bridge.cjs`：TLS MQTT3.1.1、精确设备白名单主题、QoS1/非保留命令、断连禁止控制与干净重连，不恢复旧动作；PUBACK不表示执行。
- `cloud/src/server.cjs`、`cloud/dashboard.vue`、`cloud/flows.json`及生成脚本：Node-RED + FlowFuse Dashboard，人数/温湿度/模式/两路输出/故障/更新时间/过期提示；自动与手动请求；页面和WebSocket认证；编辑器与Admin API禁用；轮换事件日志。
- `cloud/scripts/demo.cjs`、`src/test-broker.cjs`、`src/sim-device.cjs`：127.0.0.1 TLS测试Broker与明确标注的sim001，自动生成不同角色独立随机口令。模拟量取自公共正常样例并更新当前时间/会话，不能冒充实测。
- `cloud/config/`：无秘密的运行样例、Mosquitto TLS/ACL和仅本机端口Compose模板。`cloud/package-lock.json`锁依赖；`cloud/README.md`含启动、权限、日志、依赖、部署配置与费用边界；`cloud/PLAN.md`记录范围。
- `tests/cloud/`：状态/消息/鉴权集成测试、浏览器PENDING快照与APPLIED截图；证据均属模拟软件测试。

## 验证与限制

代码完成：本次最小模拟上报→看板→请求→ACK通路完成。软件测试：10项状态单测与1项实际TLS MQTT/Node-RED/HTTP/WebSocket集成测试通过；公共契约17项回归通过。Chrome检查见tests/cloud/evidence，观察到PENDING→APPLIED及随后REMOTE遥测，检查时控制台0错误。最终原始日志及额外前端过期验证以证据说明为准。

集成测试涵盖独立身份、错误口令、跨设备订阅/发布拒绝、未信任TLS证书拒绝、匿名页面/API/WebSocket拒绝、认证页面/socket可用、编辑器路径404、事件记录不含口令。状态单测涵盖15秒边界/重复不续鲜、10秒超时/迟到ACK、未知字段/重复键/超长/retain与感知有效性、序号回绕、旧boot/遗嘱与状态水位、LOCAL_OFF/无可信时间/断线禁控制、多次拒绝记录与成功不回退。最终浏览器额外验证15秒ACK延迟及网页断网：本地倒计时仍显示TIMEOUT/结果未知、按钮禁用，重连后显示同一命令迟到ACK。故意断网产生的网络错误已保留在证据中。`ack_remaining_ms`只是云端到看板的内部显示元数据，没有增加到MQTT公共报文。

硬件实测：**NOT_RUN**。没有验证K230→STM32→EC200U链路、真实4G、手机远控真实负载、1小时上报完整率、20次真实远控或8小时稳定运行。Mosquitto容器/目标主机部署：**NOT_RUN**（当前无Docker）；不把Aedes测试等同于Mosquitto通过。未公开部署、未购买服务。

## 下一步与最少信息

1. 总控确认已授权Broker域名/端口/CA、真实device_id、独立云服务与设备身份（秘密仅本机私密配置），然后使用cloud/README的已有Broker流程替换模拟入口，核查目标Broker ACL。
2. 嵌入式模块提供EC200U完整型号、AT固件/TLS能力、可信UTC策略和当前上行；核对telemetry/status序号、boot_id、control_epoch后跑A06/A07/A08/A13。通信模组仍明确使用移远EC200U。
3. 若无已有服务，先审阅Mosquitto模板、目标主机/网络/域名/TLS/认证代理与实际费用，取得公开部署授权后才部署；不得开放未认证编辑器。预算仍由总控维护。
4. 11-24前完成真实4G上报/远控关口，11-25冻结；11-27前用真实系统完成8小时记录。当前软件证据只能支持本地模拟通路。

接口建议：目前无需要总控修改契约的阻断项。本模块未变更公共接口。
