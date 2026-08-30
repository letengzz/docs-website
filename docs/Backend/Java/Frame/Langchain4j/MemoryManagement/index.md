# 内存管理

在多轮对话场景中，内存管理是维护上下文连贯性的关键。LangChain4j 提供了灵活的内存抽象，支持多种存储策略。

## ChatMemory 接口

`ChatMemory` 接口定义了对话内存的基本操作：

```java
public interface ChatMemory {

    String getId();

    void add(ChatMessage message);

    void add(UserMessage userMessage);

    void add(AiMessage aiMessage);

    List<ChatMessage> messages();

    void clear();
}
```

## 消息窗口内存

`MessageWindowChatMemory` 维护固定数量的消息，适合短对话场景：

```java
import dev.langchain4j.memory.chat.MessageWindowChatMemory;

MessageWindowChatMemory memory = MessageWindowChatMemory.builder()
        .id("chat-session-1")
        .maxMessages(10)  // 保留最近 10 条消息
        .build();

memory.add(UserMessage.from("我叫李明"));
memory.add(AiMessage.from("你好李明，很高兴认识你！"));
memory.add(UserMessage.from("我是程序员"));
memory.add(AiMessage.from("程序员好啊！"));

List<ChatMessage> history = memory.messages();
// 只包含最近 10 条消息
```

## Token 窗口内存

`TokenWindowChatMemory` 基于 token 数量管理内存，更精确地控制上下文长度：

```java
import dev.langchain4j.memory.chat.TokenWindowChatMemory;
import dev.langchain4j.model.Tokenizer;
import dev.langchain4j.model.openai.OpenAiTokenizer;

TokenWindowChatMemory memory = TokenWindowChatMemory.builder()
        .id("chat-session-2")
        .maxTokens(4000)  // 最多 4000 tokens
        .tokenizer(new OpenAiTokenizer("gpt-3.5-turbo"))
        .build();
```

:::tip
使用 Token 窗口内存可以更好地控制 API 成本，因为大多数 LLM 按 token 计费。
:::

## 自定义内存存储

实现 `ChatMemory` 接口来创建自定义内存存储：

```java
import dev.langchain4j.memory.ChatMemory;
import dev.langchain4j.data.message.ChatMessage;

public class DatabaseChatMemory implements ChatMemory {

    private final String sessionId;
    private final MessageRepository repository;

    public DatabaseChatMemory(String sessionId, MessageRepository repository) {
        this.sessionId = sessionId;
        this.repository = repository;
    }

    @Override
    public String getId() {
        return sessionId;
    }

    @Override
    public void add(ChatMessage message) {
        repository.save(sessionId, message);
    }

    @Override
    public List<ChatMessage> messages() {
        return repository.findBySessionId(sessionId);
    }

    @Override
    public void clear() {
        repository.deleteBySessionId(sessionId);
    }
}
```

## 在对话中使用内存

### 基础对话

```java
public class MemoryChatBot {

    private final ChatLanguageModel model;
    private final ChatMemory memory;

    public MemoryChatBot(ChatLanguageModel model, ChatMemory memory) {
        this.model = model;
        this.memory = memory;
    }

    public String chat(String userInput) {
        // 添加用户消息
        memory.add(UserMessage.from(userInput));

        // 生成回复
        GenerateResponse response = model.generate(memory.messages());

        // 提取 AI 回复
        String aiResponse = response.content().text();
        memory.add(AiMessage.from(aiResponse));

        return aiResponse;
    }

    public void clearContext() {
        memory.clear();
    }
}
```

### 带系统提示的对话

```java
public class SystemPromptChatBot {

    private final ChatLanguageModel model;
    private final ChatMemory memory;
    private final String systemPrompt;

    public SystemPromptChatBot(ChatLanguageModel model, int maxMessages) {
        this.model = model;
        this.memory = MessageWindowChatMemory.builder()
                .maxMessages(maxMessages)
                .build();
        this.systemPrompt = """
            你是一个专业的技术顾问，擅长解答编程和架构相关问题。
            回答时应当：
            1. 先理解用户的问题
            2. 提供清晰、准确的答案
            3. 适当提供代码示例
            4. 如果有不明确的地方，主动询问
            """;
    }

    public String chat(String userInput) {
        // 确保系统消息始终存在
        if (memory.messages().isEmpty()) {
            memory.add(SystemMessage.from(systemPrompt));
        }

        memory.add(UserMessage.from(userInput));

        GenerateResponse response = model.generate(memory.messages());

        String aiResponse = response.content().text();
        memory.add(AiMessage.from(aiResponse));

        return aiResponse;
    }
}
```

## 分布式内存

在微服务架构中，需要共享内存状态：

### Redis 实现

```java
import redis.clients.jedis.Jedis;

public class RedisChatMemory implements ChatMemory {

    private final Jedis jedis;
    private final String keyPrefix;
    private final int maxMessages;

    public RedisChatMemory(String sessionId, Jedis jedis, int maxMessages) {
        this.keyPrefix = "chat:memory:" + sessionId;
        this.jedis = jedis;
        this.maxMessages = maxMessages;
    }

    @Override
    public void add(ChatMessage message) {
        jedis.rpush(keyPrefix, message.toJson());
        // 保持消息数量限制
        Long size = jedis.llen(keyPrefix);
        while (size > maxMessages) {
            jedis.lpop(keyPrefix);
            size--;
        }
    }

    @Override
    public List<ChatMessage> messages() {
        List<String> jsonMessages = jedis.lrange(keyPrefix, 0, -1);
        return jsonMessages.stream()
                .map(ChatMessage::fromJson)
                .collect(Collectors.toList());
    }

    @Override
    public void clear() {
        jedis.del(keyPrefix);
    }
}
```

## 内存管理策略

### 1. 基于消息数量的策略

```java
MessageWindowChatMemory memory = MessageWindowChatMemory.builder()
        .id(sessionId)
        .maxMessages(20)  // 保留最近 20 条消息
        .build();
```

### 2. 基于 Token 的策略

```java
TokenWindowChatMemory memory = TokenWindowChatMemory.builder()
        .id(sessionId)
        .maxTokens(8000)  // 保留最多 8000 tokens
        .tokenizer(new OpenAiTokenizer("gpt-4"))
        .build();
```

### 3. 基于时间的策略

```java
public class TimeBasedChatMemory implements ChatMemory {

    private final List<ChatMessage> messages = new ArrayList<>();
    private final Duration maxAge;
    private final Clock clock;

    @Override
    public void add(ChatMessage message) {
        messages.add(message);
        cleanupExpiredMessages();
    }

    private void cleanupExpiredMessages() {
        Instant cutoff = clock.instant().minus(maxAge);
        messages.removeIf(msg -> msg.timestamp().isBefore(cutoff));
    }
}
```

## 最佳实践

### 1. 合理的上下文大小

根据模型的最大上下文长度设置内存限制：

```java
// GPT-4 最大 8192 tokens
TokenWindowChatMemory memory = TokenWindowChatMemory.builder()
        .id(sessionId)
        .maxTokens(6000)  // 预留空间给系统提示和响应
        .tokenizer(new OpenAiTokenizer("gpt-4"))
        .build();
```

### 2. 清理过期会话

```java
public class SessionManager {

    private final Map<String, ChatMemory> sessions = new ConcurrentHashMap<>();
    private final ScheduledExecutorService cleaner = Executors.newScheduledThreadPool(1);

    public void startSession(String sessionId) {
        ChatMemory memory = MessageWindowChatMemory.builder()
                .id(sessionId)
                .maxMessages(50)
                .build();
        sessions.put(sessionId, memory);

        // 30 分钟后清理会话
        cleaner.schedule(() -> {
            memory.clear();
            sessions.remove(sessionId);
        }, 30, TimeUnit.MINUTES);
    }

    public void endSession(String sessionId) {
        ChatMemory memory = sessions.remove(sessionId);
        if (memory != null) {
            memory.clear();
        }
    }
}
```

### 3. 敏感信息处理

```java
public class SecureChatMemory implements ChatMemory {

    private final ChatMemory delegate;

    @Override
    public void add(ChatMessage message) {
        // 移除或脱敏敏感信息
        ChatMessage sanitized = sanitizeMessage(message);
        delegate.add(sanitized);
    }

    private ChatMessage sanitizeMessage(ChatMessage message) {
        String content = message.text();
        // 脱敏身份证号
        content = content.replaceAll("\\d{18}", "[身份证号]");
        // 脱敏手机号
        content = content.replaceAll("\\d{11}", "[手机号]");
        // 脱敏邮箱
        content = content.replaceAll("[\\w.-]+@[\\w.-]+", "[邮箱]");
        return UserMessage.from(content);
    }
}
```

## 下一步

- [链式调用](./Chain/index.md) - 学习如何组合多个处理步骤
- [RAG 检索增强生成](./Rag/index.md) - 构建基于知识库的问答系统
- [工具调用](./Tools/index.md) - 让 LLM 调用外部工具
