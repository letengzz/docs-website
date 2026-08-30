# Langchain4j 流式响应

## 流式响应处理

流式响应是提升用户体验的重要特性。通过流式API，模型可以边生成边返回结果，用户无需等待完整响应即可看到内容。这对于聊天机器人等交互式应用尤为重要，可以显著降低感知延迟。

### 同步流式响应

LangChain4j通过StreamingChatModel接口支持流式响应。您需要实现监听器接口来接收实时生成的内容片段。

```java
import dev.langchain4j.model.streaming.StreamingChatModel;
import dev.langchain4j.model.openai.OpenAiStreamingChatModel;
import dev.langchain4j.data.message.ChatMessage;
import dev.langchain4j.model streaming.StreamingChatResponseListener;

public class StreamingChatDemo {

    public static void main(String[] args) {
        StreamingChatModel model = OpenAiStreamingChatModel.builder()
                .apiKey(System.getenv("OPENAI_API_KEY"))
                .modelName("gpt-3.5-turbo")
                .build();

        String userMessage = "给我讲一个关于人工智能的笑话";

        model.generate(userMessage, new StreamingChatResponseListener() {
            @Override
            public void onPartialResponse(String partialResponse) {
                System.out.print(partialResponse);
            }

            @Override
            public void onCompleteResponse(ChatResponse completeResponse) {
                System.out.println("\n\n生成完成！Token使用量: " + 
                    completeResponse.tokenUsage().totalTokenCount());
            }

            @Override
            public void onError(Throwable error) {
                System.err.println("发生错误: " + error.getMessage());
            }
        });
    }
}
```

> com/example/streaming/StreamingChatDemo.java

流式响应的处理与同步响应有所不同。同步响应一次性返回完整结果，而流式响应会多次调用onPartialResponse方法，每次传递新生成的内容片段。您需要将这些片段拼接起来以获得完整的响应。

### 使用Flux处理流式响应

在响应式编程场景中，您可以使用Project Reactor的Flux来处理流式响应，这种方式与Spring WebFlux等框架集成更好。

```java
import dev.langchain4j.model.openai.OpenAiStreamingChatModel;
import reactor.core.publisher.Flux;

public class ReactiveStreamingDemo {

    public Flux<String> streamChat(String message) {
        StreamingChatModel model = OpenAiStreamingChatModel.builder()
                .apiKey(apiKey)
                .build();

        return model.stream(message)
                .map(chunk -> chunk.content().text());
    }
}
```

> com/example/streaming/ReactiveStreamingDemo.java