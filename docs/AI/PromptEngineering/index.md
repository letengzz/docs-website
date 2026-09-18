# 提示词工程

<p style="text-align:center;"><img src="./assets/prompt-logo.png" alt="提示词工程" style="zoom:75%;" /></p>

提示词工程（Prompt Engineering）是设计、优化与评估大模型输入指令的方法论，让 AI 输出更准确、稳定、可复用，是大模型应用开发的基础能力。

- [原理与模型行为](Principles/index.md)
- [结构化提示词](StructuredPrompts/index.md)
- [角色与上下文](RoleContext/index.md)
- [few-shot 示例设计](FewShot/index.md)
- [思维链（Chain of Thought）](ChainOfThought/index.md)
- [提示词模板库](TemplateLibrary/index.md)
- [效果评估](Evaluation/index.md)
- [常见问题与最佳实践](FAQ/index.md)

## 相关专题

- [大模型应用开发](../LLMApp/index.md)：提示词在真实系统里的落地（结构化输出、上下文预算、成本与限流）
- [大模型应用开发 · 上下文与记忆管理](../LLMApp/ContextMemory/index.md)：令牌预算与历史裁剪的工程做法
- [Agent 应用](../Agent/index.md)：提示词之上的自主规划与工具编排
- [LangChain · 记忆与上下文](../LangChain/Memory/index.md)：四层记忆与摘要压缩——把「上下文预算」这件事落到框架里的做法
- [多模态应用](../Multimodal/index.md)：多模态输入的提示组织方式——图文混排的顺序影响、语音转写后如何续接文本链路
- [大模型微调](../FineTuning/index.md)：当提示词榨不出效果、而需要改的又是**行为**而不是知识时，才轮到这一层
