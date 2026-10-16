# Agent 应用

<p style="text-align:center;"><img src="./assets/agent-logo.png" alt="Agent 应用" style="zoom:75%;" /></p>

AI Agent（智能体）是能**自主规划、调用工具、完成任务**的大模型应用形态，从“问答”升级为“做事”，是当前 AI 应用的核心方向。

- [Agent 原理](AgentPrinciples/index.md)
- [工具调用](ToolCalling/index.md)
- [工作流编排](Workflow/index.md)
- [多智能体](MultiAgent/index.md)
- [记忆与上下文](MemoryContext/index.md)
- [安全边界](Safety/index.md)
- [落地案例](Practice/index.md)
- [常见问题与最佳实践](FAQ/index.md)

## 相关专题

- [Agent 框架深入](../AgentFramework/index.md)：LangGraph / CrewAI 的框架级工程化——状态机、持久化、人工介入与角色编排；**本专题讲框架无关的概念与原理，具体框架用法在那边展开**
- [AI 编程助手 · Agent 模式](../AICodingAssistant/AgentMode/index.md)：Agent 原理在编码场景的产品化落点——权限四级、并行隔离、无人值守的护栏；本专题讲原理循环，那边讲怎么把它管起来
- [大模型应用开发](../LLMApp/index.md)：从接口调用到上线指标的应用工程视角
- [大模型应用开发 · Agent 框架与应用集成](../LLMApp/AgentIntegration/index.md)：框架选型、集成清单与固定工作流 vs Agent 的判断
- [大模型应用开发 · 工具与函数调用](../LLMApp/FunctionCalling/index.md)：JSON Schema、strict 模式与并行调用的可运行示例
- [LangChain](../LangChain/index.md)：Agent 装配的框架侧落点——`create_agent` 与六个中间件钩子，以及 v1 与 `AgentExecutor` 时代的关系
- [多模态应用](../Multimodal/index.md)：把「看」与「听」交给专用模型再交回 Agent——多模态能力作为工具接入的做法
- [大模型微调](../FineTuning/index.md)：让模型稳定按你的格式发出工具调用——**工具调用习惯属于「行为」**，是微调的典型场景
- [语音与音视频 AI](../SpeechAudioAI/index.md)：**语音 Agent 就是「文本 Agent + 一个必须在 700ms 内闭合的语音外圈」**。本专题的全部结论（工具调用、记忆、多智能体、安全边界）在语音场景**照常成立、不重复讲**；那边只补外圈工程——**任何超过 400ms 的计算都要被盖住**（填充语或异步执行）、打断状态机、以及四个实时专属指标（首包延迟 / 打断成功率 / 端点误判率 / 挂断率）。判断依据：**如果你的 Agent 需要「想 10 秒再回答」，它在语音场景里必须先学会说「我看一下」**
- [AI 安全与合规](../AISecurityCompliance/index.md)：Agent 落地时的**组织级治理**——数据脱敏、内容安全、[工具护栏与审批闸门](../AISecurityCompliance/Guardrails/index.md)、[审计链](../AISecurityCompliance/Audit/index.md)与[合规清单](../AISecurityCompliance/Compliance/index.md)。三页的分工是**设计 → 执行 → 举证**：本专题回答「**循环怎么写**」，[安全边界](Safety/index.md)回答「**边界怎么设计**」，那边回答「**这道边界真的被执行了吗**」——判据形态是「**把护栏关掉试一次，下游必须仍然拒绝**」，而不是「设计文档里写了」
