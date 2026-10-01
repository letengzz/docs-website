# API 设计与治理

<p style="text-align:center;"><img src="./assets/apidesign-logo.png" style="zoom:75%;" /></p>

接口调试、接口自动化、契约测试这些词都有人讲，但**「接口长什么样、谁说了算、改了怎么通知别人」**这一层常常没人负责——于是同一套系统里出现 `GET /getUserById`、`POST /user/query`、`DELETE /removeUser` 三种风格，文档与实现各说各话，前端靠口口相传。

本专题补的就是这一层：**把接口从「代码里长出来的副产品」变成「先定、评审、可校验、可演进」的产品**。主线是**契约优先（Contract-First）**——先写 OpenAPI 契约，再由契约驱动 Mock、文档、客户端、门禁与网关配置；与之配套的是**治理机制**：规范怎么定、Lint 怎么卡、破坏性变更怎么拦、废弃怎么通知。

## 专题导航

- [体系概述：契约优先与治理四道关](Overview/index.md)
- [REST 设计规范：资源、方法、状态码与错误结构](RestDesign/index.md)
- [OpenAPI 契约工程化：从 3.0 到 3.2](OpenAPI/index.md)
- [版本策略与兼容性演进](Versioning/index.md)
- [治理机制：Lint 门禁与破坏性变更拦截](Governance/index.md)
- [Mock、文档站与沙箱](MockAndDocs/index.md)
- [网关对接：路由、鉴权、限流与契约的一致性](Gateway/index.md)
- [实战：给博客平台做一套 API 设计与治理](Practice/index.md)
- [常见问题与最佳实践](FAQ/index.md)

## 一句话定位

**本专题回答三个问题：接口该长什么样（设计）、怎么把它写死成机器可读的契约（OpenAPI）、怎么保证半年后它还没走样（治理）。**

## 本专题与相邻专题的分工

接口是一个被反复讲述的话题——调试工具讲一遍、测试工具讲一遍、框架文档再讲一遍。本专题**只讲「设计与治理」这一段**，相邻环节各自归位：

| 你想要的 | 去哪里 |
| --- | --- |
| **接口该长什么样、怎么定规范、怎么写契约、怎么卡门禁** | 本专题 |
| **手工构造请求、调试响应、分享集合** | [接口调试工具](../APITools/index.md) |
| **把调好的请求沉淀成可回归脚本、进 CI 跑** | [测试工具 · 接口自动化](../TestingTools/APIAutomation/index.md) |
| **测试怎么分层、覆盖率与质量门禁阈值怎么定** | [CI/CD · 自动化测试与质量门禁](../CICD/Testing/index.md) |
| **框架侧怎么实现 REST（Spring MVC / FastAPI 注解与绑定）** | [Spring Boot REST API](../../Backend/Java/Frame/SpringBoot/Common/RestAPI/index.md)、[Python Web 框架 · FastAPI](../../Backend/PythonWeb/FastAPI/index.md) |
| **从 Java 注解反向导出契约（代码优先）** | [SpringBoot · Swagger / springdoc](../../Backend/Java/Frame/SpringBoot/v3/Integration/Swagger/index.md) |
| **从契约反向生成前端 TS 类型与请求函数** | [前端 · 接口自动生成](../../Frontend/Others/AutoGenInterface/index.md) |
| **项目里「契约先行」怎么排进流程、验收怎么写** | [完整项目交付 · 接口契约先行](../../Others/ProjectDelivery/Contract/index.md) |
| **网关本身怎么部署、插件怎么写**（如 Kong/APISIX） | [微服务 · 网关](../../Backend/Microservices/index.md) |

::: tip 一句话理解
**代码优先产出的是「能跑的接口」，契约优先产出的是「可以被别人依赖的接口」。** 差别不在格式，在于**谁是事实来源**：契约优先时，实现与契约不一致，错的是实现。
:::

## 版本口径

接口设计这一层的「版本」有两类：**规范版本**（OpenAPI 等）与**工具版本**（Lint、文档、差异检测）。本专题统一按 **2026-10 官方渠道**核对，落在各页的 `:::info` 中；工具迭代快，落地前请以官方发布页为准。

| 对象 | 当前主线 | 状态说明 |
| --- | --- | --- |
| **OpenAPI Specification** | **3.2.1**（2026-09-10 补丁版，承接 2025-09-19 发布的 3.2.0） | 3.2 相对 3.1 **完全向后兼容**，无既有文档失效；`openapi: 3.2.0` 与 `3.2.1` 都是 3.2 特性集 |
| OpenAPI 3.1.x / 3.0.x | 仍在维护 | **3.1 是 JSON Schema 2020-12 对齐的分水岭**；3.0 工具链最成熟，存量项目多数仍在此 |
| OpenAPI 4.0（Moonwalk） | 设计中，无发布日期 | 3.2 已提前吸收部分来自 4.0 探索的**向后兼容**特性（如 `$self`、标签嵌套） |
| **Arazzo Specification** | **1.1.0**（2026-05-17） | 描述「一串接口调用」的工作流；1.1 新增 AsyncAPI 支持、`Selector` 对象、链式工作流调用 |
| **Overlay Specification** | **1.1.0** | 用一份独立文档**确定性地改写** OpenAPI 描述，适合治理元数据与多受众视图 |
| Redocly CLI | v2.46.x 线（2026-08-07） | 一个工具覆盖 lint / bundle / 预览 / 破坏性变更；`generate-client` 仍为实验特性 |
| Spectral（`@stoplight/spectral-cli`） | 持续迭代，Apache-2.0 | **规则集可完全自定义**，是「把团队规范写成可执行检查」的标准答案 |
| oasdiff | Go 单二进制，Apache-2.0 | 专做**两份 OpenAPI 的差异与破坏性变更判定**，Lint 工具替代不了它 |

::: info 为什么把版本口径放在首页
「治理」这件事最怕的是**判据漂移**：团队按 3.1 写的规则去卡 3.2 的文档，会漏掉新增结构；用只认 3.0 的解析器去读 3.1 的 `webhooks`，会直接报错。所以本专题每页都会明确「这一页的判据基于哪个版本」，而不是笼统说一句「OpenAPI 3.x」。
:::

## 阅读建议

1. **第一次系统性整理接口**：按顺序读「体系概述 → REST 设计规范 → OpenAPI 契约工程化」，先把「该长什么样」和「怎么写下来」立住。
2. **接口已经上线、要给它们立规矩**：直接读「治理机制」，重点是**先把规范写成 Lint 规则集**，再谈破坏性变更拦截——没有规则集的门禁只是摆设。
3. **正在做版本升级（v1 → v2）**：读「版本策略与兼容性演进」，`Deprecation` / `Sunset` 两个响应头（RFC 9745 / RFC 8594）是这个页面最实用的部分。
4. **前端在等接口**：读「Mock、文档站与沙箱」，契约一旦定稿，Mock 与文档就是附带产物而不是额外工作。
5. **接口要出网、要限流、要鉴权**：读「网关对接」，重点是**网关配置与契约同源**这件事怎么落地。
6. **想要一份能照抄的完整方案**：读「实战：给博客平台做一套 API 设计与治理」，它把前面所有页面的结论串成一条可验证的流水线。

## 参考资料

- [OpenAPI Specification 3.2.0](https://spec.openapis.org/oas/v3.2.0.html)：本专题所有规范类结论的第一来源
- [OpenAPI Initiative 官方博客](https://www.openapis.org/blog)：3.2 / Arazzo 1.1 的发布说明与升级指引
- [Arazzo Specification](https://spec.openapis.org/arazzo/latest.html)：工作流描述规范
- [RFC 9110 · HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)：方法、状态码、幂等性的权威定义
- [RFC 9457 · Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457.html)：结构化错误响应
- [RFC 9745 · The Deprecation HTTP Response Header Field](https://www.rfc-editor.org/rfc/rfc9745.html) 与 [RFC 8594 · The Sunset HTTP Header Field](https://www.rfc-editor.org/rfc/rfc8594.html)：接口废弃的机器可读信号
- [OWASP API Security Top 10](https://owasp.org/API-Security/)：设计阶段就该规避的风险类别
