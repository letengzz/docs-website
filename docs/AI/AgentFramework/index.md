# Agent 框架深入

<p style="text-align:center;"><img src="./assets/langgraph-logo.png" alt="LangGraph" style="zoom:75%;" /></p>

当 Agent 从「一次调用」变成「长流程」——中间要等人审批、进程崩了要从断点续跑、多个角色要协作——**编排框架**就从可选项变成了必选项。本专题深入两个当前主流框架的工程化核心：**LangGraph**（状态机式编排运行时，持久化与人机协同是一等公民）与 **CrewAI**（角色扮演式多智能体框架，Role/Goal/Task 的装配模型）。

![Agent 框架在技术栈中的位置](assets/afw-overview.svg)

## 本专题与相邻专题的分工

「Agent 编排」在库内有多个专题，边界如下——**先确认你要找的是哪一层，再进对应页面**：

| 专题 | 讲什么 | 不讲什么 |
| --- | --- | --- |
| [Agent 应用](../Agent/index.md) | Agent 的**通用原理**：工具调用循环、多智能体概念、记忆分层、安全边界（框架无关） | 具体框架的 API 与配置 |
| [LangChain · LangGraph 编排](../LangChain/LangGraph/index.md) | LangChain 生态内 LangGraph 的**入门**：最小图、reducer、`interrupt` 初识 | 持久化后端选型、子图、并行、生产化 |
| **本专题** | LangGraph / CrewAI 的**框架级工程化**：状态机设计、持久化与记忆、人工介入工程化、多智能体协作模式、部署与可观测 | Agent 概念本身为什么存在（去原理页） |
| [大模型应用开发](../LLMApp/index.md) | **不引入框架**直接调 SDK 的做法，成本与限流的工程口径 | 编排框架的用法 |
| [Agent 应用 · 工作流编排](../Agent/Workflow/index.md) | 编排层方法论：低代码平台（n8n / Coze / Dify）与代码编排的取舍 | LangGraph / CrewAI 的具体落地 |

::: tip 一条判断线
**「下一步做什么」由业务规则决定、流程要持久化 → LangGraph；「由一组角色分工协作完成一个目标」→ CrewAI；两者都不需要 → 直接调 SDK。** 它们不互斥：CrewAI 底层的 Flows 也是状态机思路，LangGraph 的节点内部也可以是一个 Crew。
:::

## 专题导航

- [框架选型与体系总览](Overview/index.md)：什么时候需要编排框架、两大框架的定位差异与选型判据
- [LangGraph 状态机深入](StateGraph/index.md)：State 与 reducer 体系、条件边与 `Command`、并行（Send）、子图、重试
- [持久化与记忆](Persistence/index.md)：checkpointer 后端选型、thread 与时间旅行、跨线程 Store、保留策略
- [人工介入工程化](HumanLoop/index.md)：`interrupt` / `Command(resume=...)`、审批类型、超时升级、不可逆动作判据
- [CrewAI 角色编排](CrewAI/index.md)：Role/Goal/Backstory、Task、Crew、Process、Flows、HITL
- [多智能体协作模式](Patterns/index.md)：supervisor、handoffs、hierarchical、map-reduce 在两个框架中的落地
- [生产化：部署与可观测](Production/index.md)：部署形态、流式、Trace 与评估、成本与安全
- [实战：内容审核发布流水线与研究小组](Practice/index.md)：LangGraph 审批流 + CrewAI 研究小组，完整可运行
- [常见问题与最佳实践](FAQ/index.md)：状态不更新、循环不终止、中断恢复失败等高频问题

## 版本速览（2026-10 核对）

| 包 | 当前线 | 说明 |
| --- | --- | --- |
| `langgraph` | **1.2.x**（1.2.12 / 2026-09-21） | 编排运行时；1.0 于 2025-10-22 与 LangChain 1.0 同步发布；要求 Python ≥ 3.10 |
| `langchain` | 1.4.x | 框架层；`langgraph.prebuilt` 已弃用，预置 Agent 迁入 `langchain.agents` |
| `langgraph-cli` / `langgraph-sdk` | 0.4.x / 0.4.x | 本地开发服务器与客户端 |
| `crewai` | **1.15.x**（1.15.23 / 2026-09-29） | 1.0 于 2025-10-21 发布；Flows 为结构化流程层；要求 Python ≥ 3.10 |
| `langgraph-supervisor` / `langgraph-swarm` | **已停维护** | supervisor / swarm 模式改用 [多智能体协作模式](Patterns/index.md) 中的自建方式 |

::: warning 版本以注册表为准
上表是写作时的核对结果，不要照抄。判断当前版本用 `pip index versions langgraph`、`pip index versions crewai`，或直接查 PyPI 发布页。
:::

::: danger 大版本口径
两个框架都跨过了 1.0：**1.0 之前（langgraph 0.x、crewai 0.x）的教程与代码大量失效**——搜索结果里的 `AgentExecutor`、`langgraph.prebuilt.create_react_agent`、crewai 0.x 的 `Tools` 写法都属于旧时代。本专题全部面向 1.x 主线；存量 0.x 项目建议锁版本运行，升级前先读官方迁移指南。
:::

## 学习路径建议

1. **先读分工表**：确认要解决的是「流程编排」还是「角色协作」，避免学错层。
2. **概念还没建立** → 先读 [Agent 应用 · Agent 原理](../Agent/AgentPrinciples/index.md)，本专题假设你已经懂工具调用循环。
3. **流程要持久化、要审批** → [状态机深入](StateGraph/index.md) → [持久化与记忆](Persistence/index.md) → [人工介入工程化](HumanLoop/index.md)，这是 LangGraph 的主线三篇。
4. **多角色协作** → [CrewAI 角色编排](CrewAI/index.md) 与 [多智能体协作模式](Patterns/index.md)。
5. **要上线** → [生产化](Production/index.md) 与 [实战](Practice/index.md)。

## 相关专题

- [Agent 应用](../Agent/index.md)：原理、工具调用、记忆与安全边界的框架无关讲法
- [LangChain](../LangChain/index.md)：装配层（模型、消息、工具的统一抽象）与本专题的运行时分工
- [RAG 检索增强](../RAG/index.md)：图节点的常见内容——检索链路本身怎么建
- [提示词工程](../PromptEngineering/index.md)：角色设定（CrewAI 的 Backstory）本质是提示词设计
- [大模型微调](../FineTuning/index.md)：框架解决流程，微调解决某个节点的输出质量
- [大模型应用开发](../LLMApp/index.md)：不引入框架时的直接调法与成本口径

## 参考资料

- LangGraph 官方文档：https://docs.langchain.com/oss/python/langgraph/overview
- LangGraph 持久化（官方）：https://docs.langchain.com/oss/python/langgraph/persistence
- LangGraph 中断与人工介入（官方）：https://docs.langchain.com/oss/python/langgraph/interrupts
- CrewAI 官方文档：https://docs.crewai.com/
- CrewAI 更新日志：https://docs.crewai.com/changelog
- 版本查询：`pip index versions langgraph`、`pip index versions crewai`
