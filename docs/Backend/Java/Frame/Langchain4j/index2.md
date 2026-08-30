# LangChain4j

- [LangChain4j 概述](./Overview/index.md)

> LangChain4j 介绍、核心设计原则、支持的 LLM/向量数据库、典型应用场景以及与其他框架的对比

- [快速开始](./QuickStart/index.md) - Maven/Gradle 依赖配置、第一个 Hello World 程序、流式响应示例以及完整的多轮对话机器人实现
- [核心概念](./Concepts/index.md) - 深入理解 ChatLanguageModel、消息类型（UserMessage、AiMessage、SystemMessage）、提示词模板、RAG 组件以及 Service 类的抽象设计
- [LLM 集成](./LlmIntegration/index.md) - 详细配置 OpenAI、Anthropic Claude、Azure OpenAI、Google Vertex AI、Ollama 本地模型以及 HuggingFace 的方法与代码示例
- [提示词模板](./PromptTemplate/index.md) - 掌握 Mustache/花括号语法、ChatPromptTemplate 对话模板、条件逻辑、循环结构、数字日期格式化以及模板复用最佳实践
- [内存管理](./MemoryManagement/index.md) - 学习 MessageWindowChatMemory 基于消息数量的管理、TokenWindowChatMemory 基于 Token 的精确控制、分布式 Redis 内存实现以及会话生命周期管理
- [链式调用](./Chain/index.md) - 了解 Chain 接口设计、PromptTemplateChain/LLMChain/OutputParserChain 的组合使用、自定义链构建以及 ETL、聚合等设计模式
- [RAG 检索增强生成](./Rag/index.md) - 涵盖 Text/PDF/HTML/Markdown 文档加载、递归字符/标题分割器、OpenAI/本地嵌入模型、InMemory/Pinecone/Milvus/PostgreSQL 向量存储以及重排序、查询转换等优化策略
- [工具调用](./Tools/index.md) - 掌握 @Tool 注解定义工具、ToolExecutor 工具注册、OpenAI 工具调用集成、数据库/文件/HTTP 实用工具实现以及异步工具调用和权限控制
