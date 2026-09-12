// AI
export const AI_Agent = [
  {
    text: "Agent 应用",
    link: "/docs/AI/Agent/index.md",
    collapsed: true,
    items: [
      { text: "Agent 原理", link: "/docs/AI/Agent/AgentPrinciples/index.md" },
      { text: "工具调用", link: "/docs/AI/Agent/ToolCalling/index.md" },
      { text: "工作流编排", link: "/docs/AI/Agent/Workflow/index.md" },
      { text: "多智能体", link: "/docs/AI/Agent/MultiAgent/index.md" },
      { text: "记忆与上下文", link: "/docs/AI/Agent/MemoryContext/index.md" },
      { text: "安全边界", link: "/docs/AI/Agent/Safety/index.md" },
      { text: "落地案例", link: "/docs/AI/Agent/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/AI/Agent/FAQ/index.md" },
    ],
  },
];

export const AI_PromptEngineering = [
  {
    text: "提示词工程",
    link: "/docs/AI/PromptEngineering/index.md",
    collapsed: true,
    items: [
      { text: "原理与模型行为", link: "/docs/AI/PromptEngineering/Principles/index.md" },
      { text: "结构化提示词", link: "/docs/AI/PromptEngineering/StructuredPrompts/index.md" },
      { text: "角色与上下文", link: "/docs/AI/PromptEngineering/RoleContext/index.md" },
      { text: "few-shot 示例设计", link: "/docs/AI/PromptEngineering/FewShot/index.md" },
      { text: "思维链（Chain of Thought）", link: "/docs/AI/PromptEngineering/ChainOfThought/index.md" },
      { text: "提示词模板库", link: "/docs/AI/PromptEngineering/TemplateLibrary/index.md" },
      { text: "效果评估", link: "/docs/AI/PromptEngineering/Evaluation/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/AI/PromptEngineering/FAQ/index.md" },
    ],
  },
];

export const AI_OpenClaw = [
  {
    text: "OpenClaw",
    items: [
      { text: "概述", link: "/docs/AI/OpenClaw/Overview/index.md" },
      { text: "安装", link: "/docs/AI/OpenClaw/Install/index.md" },
      {
        text: "核心概念",
        link: "/docs/AI/OpenClaw/CoreConcepts/index.md",
        collapsed: true,
        items: [
          { text: "智能体（Agent）", link: "/docs/AI/OpenClaw/CoreConcepts/Agent/index.md" },
          { text: "系统架构", link: "/docs/AI/OpenClaw/CoreConcepts/Architecture/index.md" },
          { text: "记忆系统（Memory）", link: "/docs/AI/OpenClaw/CoreConcepts/Memory/index.md" },
          { text: "渠道（Channels）", link: "/docs/AI/OpenClaw/CoreConcepts/Channels/index.md" },
          { text: "技能（Skills）", link: "/docs/AI/OpenClaw/CoreConcepts/Skills/index.md" },
          { text: "工具（Tools）", link: "/docs/AI/OpenClaw/CoreConcepts/Tools/index.md" },
        ],
      },
    ],
  },
];

export const AI_LLMApp = [
  {
    text: "大模型应用开发",
    link: "/docs/AI/LLMApp/index.md",
    collapsed: true,
    items: [
      { text: "API 调用基础", link: "/docs/AI/LLMApp/ApiCall/index.md" },
      { text: "Chat Completions 兼容用法", link: "/docs/AI/LLMApp/ApiCall/ChatCompletions/index.md" },
      { text: "工具与函数调用", link: "/docs/AI/LLMApp/FunctionCalling/index.md" },
      { text: "上下文与记忆管理", link: "/docs/AI/LLMApp/ContextMemory/index.md" },
      { text: "RAG 检索增强接入", link: "/docs/AI/LLMApp/RagOverview/index.md" },
      { text: "Agent 框架与应用集成", link: "/docs/AI/LLMApp/AgentIntegration/index.md" },
      { text: "成本核算与限流降级", link: "/docs/AI/LLMApp/CostRateLimit/index.md" },
      { text: "实战：智能工单助手", link: "/docs/AI/LLMApp/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/AI/LLMApp/FAQ/index.md" },
    ],
  },
];

export const AI_RAG = [
  {
    text: "RAG 检索增强",
    link: "/docs/AI/RAG/index.md",
    collapsed: true,
    items: [
      { text: "嵌入与向量基础", link: "/docs/AI/RAG/Embedding/index.md" },
      { text: "文档解析与切分", link: "/docs/AI/RAG/Chunking/index.md" },
      { text: "向量库与索引", link: "/docs/AI/RAG/VectorStore/index.md" },
      { text: "检索优化", link: "/docs/AI/RAG/Retrieval/index.md" },
      { text: "评估体系", link: "/docs/AI/RAG/Evaluation/index.md" },
      { text: "生产工程化", link: "/docs/AI/RAG/Pipeline/index.md" },
      { text: "组件版本状态与升级", link: "/docs/AI/RAG/Version/index.md" },
      { text: "实战：企业知识库问答", link: "/docs/AI/RAG/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/AI/RAG/FAQ/index.md" },
    ],
  },
];
