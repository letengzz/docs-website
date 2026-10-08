# Langchain4j 流式响应

## 流式响应处理

流式响应是提升用户体验的重要特性。通过流式API，模型可以边生成边返回结果，用户无需等待完整响应即可看到内容。这对于聊天机器人等交互式应用尤为重要，可以显著降低感知延迟。

### 同步流式响应

LangChain4j通过StreamingChatModel接口支持流式响应。您需要实现监听器接口来接收实时生成的内容片段。

```java
import dev.langchain4j.model.streaming.StreamingChatModel;
import dev.langchain4j.model.openai.OpenAiStreamingChatModel;
import dev.langchain4j.data.message.ChatMessage;
import dev.langchain4j.model.streaming.StreamingChatResponseListener;

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

## 与响应式编程专题的分工

本页讲的是**怎么把模型的流式输出接出来**（`StreamingChatModel` / `Flux<chunk>` / SSE 返回给前端）；[响应式编程](../../../../ReactiveProgramming/index.md) 讲的是**这条流接入之后怎么被非阻塞链路正确承载**：

| 问题 | 看哪一页 |
| --- | --- |
| 流式输出怎么写、回调与 `Flux` 两种形态怎么选 | **本页** |
| 返回 `Flux` 后怎么用 SSE 推给浏览器、客户端断开怎么释放订阅 | 响应式编程 · [WebFlux 落地](../../../../ReactiveProgramming/WebFlux/index.md) |
| 模型产得快、下游写得慢时怎么不把内存撑爆 | 响应式编程 · [背压](../../../../ReactiveProgramming/Backpressure/index.md) |
| 流式链路上的超时、降级与「半截结果」怎么处理 | 响应式编程 · [实战：一次聚合查询的改造](../../../../ReactiveProgramming/Practice/index.md) |

::: danger 流式输出最容易被忽略的两件事
1. **客户端断开必须终止上游**：用户关掉页面后，模型调用仍在继续并持续计费。接口返回 `Flux` 时要绑定取消信号（`doOnCancel` / `doFinally`），让取消一路传到模型客户端的 HTTP 连接。
2. **流式响应没有真背压**：模型侧已开始生成，服务端只能缓冲。必须给流设上限（总时长 / 最大 token），并监控待发队列，否则「几百个用户同时开着对话框」会把服务端内存吃光。
:::

::: info 版本适用性提示
上面的 `StreamingChatResponseListener` 与 `generate(...)` 属于**旧版回调式写法**；Langchain4j 1.x 起流式接口已演进（`StreamingChatModel` + 响应式形态的处理器/`Flux`）。**升级前请以所用版本的官方文档为准核对包名与类名**，本页保留旧写法仅供存量项目参考，不覆盖其内容。
:::