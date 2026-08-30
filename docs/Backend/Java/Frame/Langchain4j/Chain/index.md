# 链式调用

链式调用是 LangChain4j 的核心特性之一，它允许你将多个处理步骤组合成一个复杂的处理流程。本章将详细介绍如何使用 Chain API 构建强大的 LLM 应用流水线。

## Chain 接口

`Chain` 接口是 LangChain4j 中处理流程的基本抽象：

```java
public interface Chain<I, O> {

    O execute(I input);

    // 组合多个链
    <V> Chain<I, V> andThen(Chain<O, V> next);
}
```

## 内置 Chain

### 1. PromptTemplateChain

将提示词模板作为链的一个步骤：

```java
import dev.langchain4j.chain.PromptTemplateChain;
import dev.langchain4j.prompt.PromptTemplate;

PromptTemplate template = PromptTemplate.from(
    "请用{{style}}风格，写一段关于{{topic}}的{{length}}文字。"
);

Chain<Map<String, Object>, Prompt> promptChain = 
    PromptTemplateChain.from(template);
```

### 2. LLMChain

将 LLM 模型作为链的步骤：

```java
import dev.langchain4j.chain.LlmChain;
import dev.langchain4j.model.chat.ChatLanguageModel;

LLMChain<Prompt, GenerateResponse> llmChain = LLMChain.builder()
        .llm(model)
        .build();
```

### 3. OutputParserChain

将输出解析器作为链的步骤：

```java
import dev.langchain4j.chain.OutputParserChain;
import dev.langchain4j.output.OutputParser;

OutputParserChain<GenerateResponse, ParsedResult> parserChain = 
    OutputParserChain.from(new JsonOutputParser<>(ParsedResult.class));
```

## 链的组合

### 使用 andThen 组合

```java
Chain<Map<String, Object>, String> chain = promptChain
        .andThen(llmChain)
        .andThen(parserChain)
        .andThen(responseChain);

String result = chain.execute(input);
```

### 使用 SequentialChain 组合多个并行输入

```java
SequentialChain chain = SequentialChain.builder()
        .add(promptTemplate1)
        .add(promptTemplate2)
        .build();

Map<String, Object> inputs = Map.of(
    "input1", "值1",
    "input2", "值2"
);
```

### 使用 RouterChain 进行条件路由

```java
public class CategoryRouterChain implements Chain<String, Chain<String, String>> {

    private final Map<String, Chain<String, String>> routes;

    public CategoryRouterChain(Map<String, Chain<String, String>> routes) {
        this.routes = routes;
    }

    @Override
    public Chain<String, String> execute(String category) {
        return routes.getOrDefault(category, defaultChain);
    }
}
```

## 完整示例

### 构建一个问答系统链

```java
public class QASystemChain {

    private final Chain<QuestionAndDocuments, String> chain;

    public QASystemChain(ChatLanguageModel model, int maxRetries) {
        // 步骤 1: 检索相关文档
        Chain<QuestionAndDocuments, List<Document>> retrieveChain = 
            RetrieverChain.from(retriever);

        // 步骤 2: 构建提示词
        Chain<QuestionAndDocuments, Prompt> promptChain = 
            PromptTemplateChain.from(QA_PROMPT_TEMPLATE);

        // 步骤 3: 调用 LLM
        Chain<Prompt, GenerateResponse> llmChain = LLMChain.builder()
                .llm(model)
                .build();

        // 步骤 4: 解析输出
        Chain<GenerateResponse, String> outputChain = 
            OutputParserChain.from(new StringOutputParser());

        // 组合完整链
        this.chain = retrieveChain
                .andThen(context -> {
                    // 将检索结果注入到提示词变量中
                    List<String> contexts = context.documents().stream()
                            .map(Document::text)
                            .collect(Collectors.toList());
                    return new QuestionAndDocuments(
                        context.question(), 
                        contexts
                    );
                })
                .andThen(promptChain)
                .andThen(llmChain)
                .andThen(outputChain);
    }

    public String execute(String question) {
        return chain.execute(new QuestionAndDocuments(question, List.of()));
    }
}
```

### 构建内容生成链

```java
public class ContentGenerationChain {

    private final Chain<ContentRequest, ContentResult> chain;

    public ContentGenerationChain(ChatLanguageModel model) {
        // 1. 创意生成
        Chain<ContentRequest, List<String>> ideasChain = 
            PromptTemplateChain.from(IDEAS_TEMPLATE)
                .andThen(llmChain)
                .andThen(new LineSplitParser());

        // 2. 内容扩展
        Chain<String, GenerateResponse> expandChain = 
            PromptTemplateChain.from(EXPAND_TEMPLATE)
                .andThen(llmChain);

        // 3. 质量检查
        Chain<String, QualityCheckResult> qualityChain = 
            PromptTemplateChain.from(QUALITY_TEMPLATE)
                .andThen(llmChain)
                .andThen(outputParser);

        // 组合
        this.chain = ideasChain.andThen(ideas -> {
            // 对每个创意进行扩展
            List<String> expanded = new ArrayList<>();
            for (String idea : ideas) {
                GenerateResponse response = expandChain.execute(
                    new ContentRequest(idea)
                );
                expanded.add(response.content().text());
            }
            return expanded;
        });
    }
}
```

## 自定义 Chain

### 简单的转换链

```java
public class UpperCaseChain implements Chain<String, String> {

    @Override
    public String execute(String input) {
        return input.toUpperCase();
    }
}
```

### 带条件的处理链

```java
public class ConditionalChain<I, O> implements Chain<I, O> {

    private final Predicate<I> condition;
    private final Chain<I, O> ifTrue;
    private final Chain<I, O> ifFalse;

    public ConditionalChain(
            Predicate<I> condition,
            Chain<I, O> ifTrue,
            Chain<I, O> ifFalse) {
        this.condition = condition;
        this.ifTrue = ifTrue;
        this.ifFalse = ifFalse;
    }

    @Override
    public O execute(I input) {
        return condition.test(input) 
            ? ifTrue.execute(input) 
            : ifFalse.execute(input);
    }
}
```

### 带重试的链

```java
public class RetryChain<I, O> implements Chain<I, O> {

    private final Chain<I, O> delegate;
    private final int maxRetries;
    private final Predicate<O> successCondition;

    @Override
    public O execute(I input) {
        int attempts = 0;
        O result = null;

        while (attempts < maxRetries) {
            result = delegate.execute(input);
            if (successCondition.test(result)) {
                return result;
            }
            attempts++;
        }

        throw new RuntimeException("重试次数耗尽");
    }
}
```

## 链式调用最佳实践

### 1. 单一职责原则

每个链应该只负责一个明确的处理步骤：

```java
// 不推荐 - 一个链做了太多事情
Chain<String, String> everything = input -> {
    // 检索、转换、生成、解析
    // ...
};

// 推荐 - 每个链专注一件事
Chain<String, List<Document>> retrieve = RetrieverChain.from(retriever);
Chain<List<Document>, String> summarize = SummarizeChain.from(model);
Chain<String, ParsedResult> parse = OutputParserChain.from(parser);
```

### 2. 错误处理

```java
public class ErrorHandlingChain<I, O> implements Chain<I, O> {

    private final Chain<I, O> delegate;
    private final Function<Exception, O> errorHandler;

    @Override
    public O execute(I input) {
        try {
            return delegate.execute(input);
        } catch (Exception e) {
            return errorHandler.apply(e);
        }
    }
}
```

### 3. 监控和日志

```java
public class LoggingChain<I, O> implements Chain<I, O> {

    private final Chain<I, O> delegate;
    private final String name;
    private final Logger logger;

    @Override
    public O execute(I input) {
        logger.info("[{}] 开始处理, 输入: {}", name, input);
        long start = System.currentTimeMillis();
        
        O result = delegate.execute(input);
        
        long duration = System.currentTimeMillis() - start;
        logger.info("[{}] 处理完成, 耗时: {}ms, 输出: {}", 
            name, duration, result);
        
        return result;
    }
}
```

## 常见链模式

### 1. ETL 模式

```java
public class ETLChain<I, T, O> implements Chain<List<I>, List<O>> {

    private final Chain<I, T> extract;
    private final Chain<T, T> transform;
    private final Chain<T, O> load;

    @Override
    public List<O> execute(List<I> inputs) {
        return inputs.stream()
                .map(extract)
                .map(transform)
                .map(load)
                .collect(Collectors.toList());
    }
}
```

### 2. 聚合模式

```java
public class AggregationChain<I, O> implements Chain<List<I>, O {

    private final Chain<List<I>, O> aggregator;

    @Override
    public O execute(List<I> inputs) {
        return aggregator.execute(inputs);
    }
}
```

## 下一步

- [RAG 检索增强生成](./Rag/index.md) - 构建知识库问答系统
- [工具调用](./Tools/index.md) - 让 LLM 调用外部工具
- [内存管理](./MemoryManagement/index.md) - 管理对话状态
