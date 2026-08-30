# 快速开始

本指南将帮助你在 5 分钟内完成 LangChain4j 项目的搭建，并运行你的第一个 LLM 应用。

## 快速体验

只需几行代码，即可开始使用 LangChain4j：

```java
// 1. 添加依赖
// Maven: langchain4j, langchain4j-open-ai

// 2. 创建模型
ChatLanguageModel model = OpenAiChatModel.builder()
        .apiKey("your-api-key")
        .modelName("gpt-3.5-turbo")
        .build();

// 3. 生成内容
String response = model.generate("你好，LangChain4j！");
System.out.println(response);
```

## 环境要求

- Java 11 或更高版本
- Maven 3.6+ 或 Gradle 7+
- 有效的 LLM API Key（OpenAI、Anthropic 等）

## Maven 依赖配置

在 `pom.xml` 中添加以下依赖：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j</artifactId>
    <version>1.0.0-beta1</version>
</dependency>

<!-- OpenAI 支持 -->
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai</artifactId>
    <version>1.0.0-beta1</version>
</dependency>

<!-- 其他 LLM 提供商按需添加 -->
```

## Gradle 依赖配置

```groovy
implementation 'dev.langchain4j:langchain4j:1.0.0-beta1'
implementation 'dev.langchain4j:langchain4j-open-ai:1.0.0-beta1'
```

## 第一个程序

创建一个简单的 Java 类，体验 LangChain4j 的核心功能：

```java
import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.model.openai.OpenAiChatModel;

public class HelloWorld {

    public static void main(String[] args) {
        // 1. 创建模型实例
        ChatLanguageModel model = OpenAiChatModel.builder()
                .apiKey("your-api-key")
                .modelName("gpt-3.5-turbo")
                .build();

        // 2. 发送提示词
        String response = model.generate("你好，请介绍一下你自己");

        // 3. 输出结果
        System.out.println(response);
    }
}
```

:::tip
你可以通过环境变量设置 API Key，避免在代码中硬编码：

```java
String apiKey = System.getenv("OPENAI_API_KEY");
```
:::

## 流式响应示例

LangChain4j 支持流式响应，让用户体验更佳的交互效果：

```java
import dev.langchain4j.model.chat.StreamingChatLanguageModel;

StreamingChatLanguageModel model = StreamingChatModel.builder()
        .apiKey("your-api-key")
        .modelName("gpt-3.5-turbo")
        .build();

model.generate("讲一个关于程序员的笑话", response -> {
    System.out.print(response.token().text());
    System.out.flush();
});
System.out.println();
```

## 完整项目示例

创建一个更完整的对话应用，包含内存管理功能：

```java
import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.openai.OpenAiChatModel;

public class ChatBot {

    private final ChatLanguageModel model;
    private final MessageWindowChatMemory memory;

    public ChatBot(String apiKey) {
        this.model = OpenAiChatModel.builder()
                .apiKey(apiKey)
                .modelName("gpt-4")
                .temperature(0.7)
                .build();

        this.memory = MessageWindowChatMemory.builder()
                .maxMessages(10)
                .build();
    }

    public String chat(String userMessage) {
        memory.add(userMessage);

        String response = model.generate(memory.messages());

        memory.add(response);

        return response;
    }

    public static void main(String[] args) {
        ChatBot bot = new ChatBot(System.getenv("OPENAI_API_KEY"));

        System.out.println("Bot: 你好！我是你的 AI 助手，有什么可以帮助你的？");

        while (true) {
            System.out.print("You: ");
            String input = new Scanner(System.in).nextLine();

            if ("exit".equalsIgnoreCase(input)) {
                System.out.println("Bot: 再见！");
                break;
            }

            String response = bot.chat(input);
            System.out.println("Bot: " + response);
        }
    }
}
```

## 常见问题

### API Key 无效

确保你的 API Key 正确且有效，不同的 LLM 提供商需要不同的 API Key 格式。

### 模型不支持

检查你使用的模型名称是否正确，不同提供商对模型名称有不同的命名规范。

### 网络连接问题

如果遇到网络问题，请确认你的网络环境可以访问相应的 LLM 服务 API。

## 下一步

完成快速开始后，建议继续阅读以下内容：

- [核心概念](./Concepts/index.md) - 深入理解 LangChain4j 的设计理念
- [LLM 集成](./LlmIntegration/index.md) - 了解如何集成不同的 LLM
- [提示词模板](./PromptTemplate/index.md) - 学习构建复杂的提示词
