## Langchain4j 常见错误

在开发过程中，可能会遇到各种问题。调试AI应用需要特殊的技巧，因为失败可能来自多个层面：网络连接、API配置、模型参数或代码逻辑。

### API调用失败

当遇到API调用失败时，首先检查API密钥是否正确设置，然后确认网络可以访问目标API服务。LangChain4j会记录详细的请求和响应信息，通过启用日志可以获取更多信息用于问题诊断。

```java
// 启用详细日志
System.setProperty("org.slf4j.simpleLogger.defaultLogLevel", "DEBUG");
```

如果遇到超时错误，可能是网络延迟或API服务繁忙导致的。您可以增加超时时间设置，或者实现重试机制来处理临时性的服务不可用情况。

```java
ChatLanguageModel model = OpenAiChatModel.builder()
        .apiKey(apiKey)
        .timeout(Duration.ofSeconds(120))  // 增加超时时间
        .build();
```

