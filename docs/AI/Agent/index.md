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

- [大模型应用开发](../LLMApp/index.md)：从接口调用到上线指标的应用工程视角
- [大模型应用开发 · Agent 框架与应用集成](../LLMApp/AgentIntegration/index.md)：框架选型、集成清单与固定工作流 vs Agent 的判断
- [大模型应用开发 · 工具与函数调用](../LLMApp/FunctionCalling/index.md)：JSON Schema、strict 模式与并行调用的可运行示例
- [LangChain](../LangChain/index.md)：Agent 装配的框架侧落点——`create_agent` 与六个中间件钩子，以及 v1 与 `AgentExecutor` 时代的关系
- [多模态应用](../Multimodal/index.md)：把「看」与「听」交给专用模型再交回 Agent——多模态能力作为工具接入的做法
- [大模型微调](../FineTuning/index.md)：让模型稳定按你的格式发出工具调用——**工具调用习惯属于「行为」**，是微调的典型场景
