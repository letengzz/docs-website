# LLM 集成

LangChain4j 支持集成多种主流的大语言模型提供商。本章将详细介绍如何配置和使用不同的 LLM。

## OpenAI 集成

### Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai</artifactId>
    <version>1.0.0-beta1</version>
</dependency>
```

### Chat Model 配置

```java
import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.model.openai.OpenAiChatModel;

ChatLanguageModel model = OpenAiChatModel.builder()
        .apiKey("your-api-key")
        .modelName("gpt-4")
        .temperature(0.7)  // 控制随机性，0-2 之间
        .maxTokens(1000)   // 最大生成 token 数
        .topP(1.0)         // nucleus sampling 参数
        .presencePenalty(0.0) // 存在惩罚
        .frequencyPenalty(0.0) // 频率惩罚
        .build();
```

### Streaming Model 配置

```java
import dev.langchain4j.model.openai.OpenAiStreamingChatModel;

StreamingChatChatModel model = OpenAiStreamingChatModel.builder()
        .apiKey("your-api-key")
        .modelName("gpt-4")
        .temperature(0.7)
        .build();
```

### Embedding Model 配置

```java
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.openai.OpenAiEmbeddingModel;

EmbeddingModel embeddingModel = OpenAiEmbeddingModel.builder()
        .apiKey("your-api-key")
        .modelName("text-embedding-ada-002")
        .build();

List<Embedding> embeddings = embeddingModel.embedAll(
        TextSegment.from("Hello world"),
        TextSegment.from("LangChain4j is great")
);
```

## Anthropic 集成

### Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-anthropic</artifactId>
    <version>1.0.0-beta1</version>
</dependency>
```

### 配置示例

```java
import dev.langchain4j.model.anthropic.AnthropicChatModel;

AnthropicChatModel model = AnthropicChatModel.builder()
        .apiKey("your-api-key")
        .modelName("claude-3-opus-20240229")
        .temperature(0.7)
        .maxTokens(1024)
        .build();
```

:::tip
Anthropic 的 Claude 模型在长上下文处理和安全性方面表现出色，特别适合需要高可靠性的应用场景。
:::

## Azure OpenAI 集成

### Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-azure-open-ai</artifactId>
    <version>1.0.0-beta1</version>
</dependency>
```

### 配置示例

```java
import dev.langchain4j.model.azureopenai.AzureOpenAiChatModel;

AzureOpenAiChatModel model = AzureOpenAiChatModel.builder()
        .endpoint("https://your-resource.openai.azure.com/")
        .apiKey("your-api-key")
        .deploymentName("gpt-4")
        .apiVersion("2024-02-15-preview")
        .build();
```

:::danger
确保你的 Azure 资源已正确配置，并开启了相应的模型部署。
:::

## Google Vertex AI 集成

### Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-vertex-ai</artifactId>
    <version>1.0.0-beta1</version>
</dependency>
```

### 配置示例

```java
import dev.langchain4j.model.vertexai.VertexAiChatModel;

VertexAiChatModel model = VertexAiChatModel.builder()
        .project("your-project-id")
        .location("us-central1")
        .modelName("gemini-pro")
        .temperature(0.7)
        .build();
```

## Ollama 本地模型

### Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-ollama</artifactId>
    <version>1.0.0-beta1</version>
</dependency>
```

### 配置示例

```java
import dev.langchain4j.model.ollama.OllamaChatModel;

OllamaChatModel model = OllamaChatModel.builder()
        .baseUrl("http://localhost:11434")
        .modelName("llama2")
        .temperature(0.7)
        .build();
```

:::tip
Ollama 允许你在本地运行大语言模型，无需网络连接，适合开发测试和隐私敏感的场景。
:::

## HuggingFace 集成

### Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-huggingface</artifactId>
    <version>1.0.0-beta1</version>
</dependency>
```

### 配置示例

```java
import dev.langchain4j.model.huggingface.HuggingFaceChatModel;

HuggingFaceChatModel model = HuggingFaceChatModel.builder()
        .apiKey("your-api-key")
        .modelId("mistralai/Mistral-7B-Instruct-v0.2")
        .temperature(0.7)
        .maxNewTokens(512)
        .build();
```

## 模型对比

| 提供商 | 模型 | 特点 | 适用场景 |
|--------|------|------|----------|
| OpenAI | GPT-4/GPT-3.5 | 能力强，生态完善 | 通用场景 |
| Anthropic | Claude | 安全可靠，长上下文 | 对话、文档分析 |
| Azure | GPT-4/GPT-3.5 | 企业级服务 | 企业应用 |
| Google | Gemini | 多模态能力强 | 多模态应用 |
| Ollama | 本地模型 | 隐私保护，无网络依赖 | 本地开发 |
| HuggingFace | 开源模型 | 模型丰富 | 实验研究 |

## 统一接口

LangChain4j 提供了统一的接口，无论使用哪个提供商，代码结构保持一致：

```java
// 切换不同的 LLM 提供商，只需更改模型创建代码
ChatLanguageModel model;

// OpenAI
model = OpenAiChatModel.builder().apiKey("...").build();

// Anthropic
model = AnthropicChatModel.builder().apiKey("...").build();

// 业务代码无需更改
String response = model.generate("你好");
```

## 下一步

- [提示词模板](./PromptTemplate/index.md) - 学习构建高效的提示词
- [内存管理](./MemoryManagement/index.md) - 管理对话状态
- [RAG 检索增强生成](./Rag/index.md) - 构建知识库问答
