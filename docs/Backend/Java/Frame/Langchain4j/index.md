# LangChain4j

![image-20251226091637928](assets/image-20251226091637928.png)

- [LangChain4j 概述](./Overview/index.md)

- [Langchain4j 大模型平台](./Platform/index.md)

- [Langchain4j 构建入门程序](./BasicProgram/index.md)
- [Langchain4j 大语言模型集成](./LlmIntegration/index.md)
- 
- [Langchain4j 流式响应](./Streaming/index.md)
- 
- [核心概念](./Concepts/index.md) - 深入理解 ChatLanguageModel、消息类型（UserMessage、AiMessage、SystemMessage）、提示词模板、RAG 组件以及 Service 类的抽象设计
- [LLM 集成](./LlmIntegration/index.md) - 详细配置 OpenAI、Anthropic Claude、Azure OpenAI、Google Vertex AI、Ollama 本地模型以及 HuggingFace 的方法与代码示例
- [提示词模板](./PromptTemplate/index.md) - 掌握 Mustache/花括号语法、ChatPromptTemplate 对话模板、条件逻辑、循环结构、数字日期格式化以及模板复用最佳实践
- [内存管理](./MemoryManagement/index.md) - 学习 MessageWindowChatMemory 基于消息数量的管理、TokenWindowChatMemory 基于 Token 的精确控制、分布式 Redis 内存实现以及会话生命周期管理
- [链式调用](./Chain/index.md) - 了解 Chain 接口设计、PromptTemplateChain/LLMChain/OutputParserChain 的组合使用、自定义链构建以及 ETL、聚合等设计模式
- [Langchain4j 检索增强生成RAG](./Rag/index.md)
- [工具调用](./Tools/index.md) - 掌握 @Tool 注解定义工具、ToolExecutor 工具注册、OpenAI 工具调用集成、数据库/文件/HTTP 实用工具实现以及异步工具调用和权限控制
- [Langchain4j 整合SpringBoot](SpringBoot/index.md)
- [Langchain4j 常见错误](Error/index.md)

## 模型比较与选择

在选择大语言模型时，需要综合考虑多个因素，包括任务需求、性能要求、成本预算、数据安全等。不同模型在这些方面各有优劣，理解它们的特点有助于做出最优选择。

### OpenAI GPT系列特点

OpenAI的GPT系列是目前最成熟的商业大模型服务，在各种基准测试中表现优异。GPT-4在复杂推理、长文本处理和多任务学习方面处于领先地位，适合对质量要求极高的应用。GPT-3.5 Turbo则提供了优秀的性价比，适合大多数通用场景。

### Claude系列特点

Anthropic的Claude系列以安全性和可控性著称，特别擅长遵循复杂指令和长文档分析。Claude在处理长上下文时表现稳定，适合需要分析长篇文档或进行复杂推理的任务。

### 开源模型特点

开源模型如Llama、Mistral等最大的优势是本地部署能力和数据隐私保护。虽然在绝对性能上可能不及顶级商业模型，但通过微调和优化可以在特定任务上达到很好的效果。开源模型还没有API调用成本，适合大规模使用。

```java
public class ModelSelector {

    public enum ModelType {
        HIGH_PERFORMANCE,
        BALANCED,
        COST_EFFECTIVE,
        LOCAL_DEPLOYMENT
    }

    public static ChatModel selectModel(ModelType type, String apiKey) {
        return switch (type) {
            case HIGH_PERFORMANCE -> OpenAiChatModel.builder()
                    .apiKey(apiKey)
                    .modelName("gpt-4-turbo")
                    .temperature(0.3)
                    .build();
            case BALANCED -> OpenAiChatModel.builder()
                    .apiKey(apiKey)
                    .modelName("gpt-3.5-turbo")
                    .temperature(0.7)
                    .build();
            case COST_EFFECTIVE -> AnthropicChatModel.builder()
                    .apiKey(apiKey)
                    .modelName(AnthropicChatModel.Model.CLAUDE_3_HAIKU)
                    .temperature(0.7)
                    .build();
            case LOCAL_DEPLOYMENT -> OllamaChatModel.builder()
                    .baseUrl("http://localhost:11434")
                    .modelName("llama3.2")
                    .build();
        };
    }
}
```

## 多模型统一接口

在实际项目中，可能需要支持多种模型或在不同模型之间切换。LangChain4j的统一接口使得这种需求变得简单。您可以通过配置文件或工厂模式来管理不同的模型实例。

### 模型工厂实现

```java
import dev.langchain4j.model.chat.ChatModel;
import java.util.Map;

public class ModelFactory {

    private final Map<String, ChatModel> models;

    public ModelFactory(Map<String, ChatModel> models) {
        this.models = models;
    }

    public ChatModel getModel(String modelName) {
        ChatModel model = models.get(modelName);
        if (model == null) {
            throw new IllegalArgumentException("未找到模型: " + modelName);
        }
        return model;
    }

    public String chatWithModel(String modelName, String message) {
        return getModel(modelName).generate(message);
    }
}
```

> com/example/factory/ModelFactory.java

```java
import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.model.anthropic.AnthropicChatModel;

public class FactoryConfig {

    public static ModelFactory createFactory() {
        Map<String, ChatModel> models = Map.of(
                "gpt-4", OpenAiChatModel.builder()
                        .apiKey(apiKey)
                        .modelName("gpt-4")
                        .build(),
                "gpt-3.5-turbo", OpenAiChatModel.builder()
                        .apiKey(apiKey)
                        .modelName("gpt-3.5-turbo")
                        .build(),
                "claude-sonnet", AnthropicChatModel.builder()
                        .apiKey(apiKey)
                        .modelName(AnthropicChatModel.Model.CLAUDE_3_SONNET)
                        .build()
        );

        return new ModelFactory(models);
    }
}
```

> com/example/factory/FactoryConfig.java

## 错误处理与重试机制

在实际生产环境中，API调用可能因为各种原因失败，包括网络问题、服务过载、认证过期等。实现健壮的错误处理和重试机制对于保证应用稳定性至关重要。

### 统一错误处理

```java
import dev.langchain4j.exception.*;

public class ModelErrorHandler {

    public String safeGenerate(ChatModel model, String message) {
        try {
            return model.generate(message);
        } catch (AuthenticationException e) {
            throw new RuntimeException("API认证失败，请检查密钥配置", e);
        } catch (RateLimitException e) {
            throw new RuntimeException("请求频率超限，请稍后重试", e);
        } catch (ContentFilterException e) {
            throw new RuntimeException("内容触发安全过滤", e);
        } catch (TimeoutException e) {
            throw new RuntimeException("请求超时", e);
        } catch (Exception e) {
            throw new RuntimeException("发生未知错误: " + e.getMessage(), e);
        }
    }
}
```

> com/example/error/ModelErrorHandler.java

### 重试策略配置

```java
import dev.langchain4j.model.RetryingChatModel;
import dev.langchain4j.model.chat.ChatModel;

public class RetryConfig {

    public static ChatModel createWithRetry(ChatModel delegate) {
        return RetryingChatModel.builder()
                .delegate(delegate)
                .maxRetries(3)
                .delay(Duration.ofSeconds(1))
                .retryOnRuntimeException(true)
                .retryOnApiException(true)
                .build();
    }
}
```

> com/example/retry/RetryConfig.java

## 模型性能优化

大语言模型的API调用通常涉及较高的延迟和成本。优化模型调用可以显著提升应用性能和降低成本。以下是一些常用的优化策略。

### 提示词优化

精简提示词可以减少输入token数量，降低API成本并提高响应速度。去除不必要的上下文和重复说明，只保留完成任务所必需的信息。同时，使用few-shot示例时选择最有代表性的样本，避免过多冗余示例。

```java
public class PromptOptimizer {

    public static String optimize(String originalPrompt) {
        String optimized = originalPrompt
                .replaceAll("\\s+", " ")  // 合并空白字符
                .replaceAll("请.*?：", ":")  // 简化指令前缀
                .trim();
        return optimized;
    }
}
```

### 缓存机制

对于相同或相似的请求，可以使用缓存来避免重复调用API。语义缓存可以根据请求的语义相似度来判断是否命中缓存，比精确匹配更加智能。

```java
import dev.langchain4j.service.AiServices;
import dev.langchain4j.memory.ChatMemory;
import dev.langchain4j.memory.MessageWindowChatMemory;

public class CachedChatService {

    private final ChatModel model;
    private final ChatMemory memory;

    public CachedChatService(ChatModel model) {
        this.model = model;
        this.memory = MessageWindowChatMemory.withMaxMessages(10);
    }

    public String chat(String userInput) {
        return model.generate(userInput, memory.messages());
    }
}
```

