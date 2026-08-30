# 提示词模板

提示词模板是构建高效 LLM 应用的关键。LangChain4j 提供了灵活强大的提示词模板系统，支持变量替换、条件逻辑和动态生成。

## 基础模板

### 使用 Mustache 语法

```java
import dev.langchain4j.prompt.PromptTemplate;
import dev.langchain4j.data.message.UserMessage;

PromptTemplate template = PromptTemplate.from(
    "请为 {{product}} 写一段营销文案，目标用户是 {{audience}}，" +
    "卖点包括：{{features}}"
);

Map<String, Object> variables = Map.of(
    "product", "智能手表",
    "audience", "年轻的运动爱好者",
    "features", "心率监测、GPS追踪、50米防水"
);

UserMessage prompt = template.apply(variables);
```

### 使用花括号语法

```java
PromptTemplate template = PromptTemplate.from(
    "分析以下数据：\n" +
    "收入：${revenue}\n" +
    "支出：${expenses}\n" +
    "请计算利润率并给出建议。"
);

Map<String, Object> variables = Map.of(
    "revenue", "1000000",
    "expenses", "600000"
);

Prompt prompt = template.apply(variables);
```

## ChatPromptTemplate

对于对话场景，使用 `ChatPromptTemplate` 更加合适：

```java
import dev.langchain4j.prompt.ChatPromptTemplate;
import dev.langchain4j.data.message.*;

ChatPromptTemplate template = ChatPromptTemplate.from(
    List.of(
        SystemMessage.from(
            "你是一个专业的{{role}}，具有{{years}}年的从业经验。"
        ),
        HumanMessage.from(
            "请{{task}}，要求：\n" +
            "1. 详细说明\n" +
            "2. 提供代码示例\n" +
            "3. 注意事项"
        )
    )
);

Map<String, Object> variables = Map.of(
    "role", "Java架构师",
    "years", "10",
    "task", "解释依赖注入的原理"
);

Prompt prompt = template.apply(variables);
```

## 模板组合

可以将多个模板组合使用，构建复杂的提示词：

```java
PromptTemplate systemTemplate = PromptTemplate.from(
    "你是一个{{personality}}助手。"
);

PromptTemplate userTemplate = PromptTemplate.from(
    "用户的问题是：{{question}}"
);

Map<String, Object> vars = Map.of(
    "personality", "友好",
    "question", "如何学习编程？"
);

Prompt prompt = systemTemplate.and(userTemplate).apply(vars);
```

## 条件逻辑

在模板中使用条件逻辑，根据变量值生成不同的内容：

```java
PromptTemplate template = PromptTemplate.from(
    "用户{{username}}的订单信息：\n" +
    "订单号：{{orderId}}\n" +
    "{{#if isVip}}" +
    "会员等级：{{vipLevel}}\n" +
    "享受折扣：{{discount}}%\n" +
    "{{/if}}" +
    "订单金额：{{amount}}元"
);

Map<String, Object> variables = Map.of(
    "username", "张三",
    "orderId", "ORDER123456",
    "isVip", true,
    "vipLevel", "黄金会员",
    "discount", "15",
    "amount", "2999"
);

Prompt prompt = template.apply(variables);
```

## 循环结构

在模板中使用循环处理列表数据：

```java
PromptTemplate template = PromptTemplate.from(
    "请分析以下商品并给出推荐：\n" +
    "{{#each products}}" +
    "{{@index}}. {{name}} - 价格：{{price}}元 - 评分：{{rating}}\n" +
    "{{/each}}"
);

Map<String, Object> variables = Map.of(
    "products", List.of(
        Map.of("name", "商品A", "price", "99", "rating", "4.5"),
        Map.of("name", "商品B", "price", "199", "rating", "4.8"),
        Map.of("name", "商品C", "price", "299", "rating", "4.2")
    )
);

Prompt prompt = template.apply(variables);
```

## 格式化数字和日期

```java
PromptTemplate template = PromptTemplate.from(
    "报告生成时间：{{timestamp}}\n" +
    "用户数量：{{userCount, number}}人\n" +
    "收入总额：{{revenue, currency}}元"
);

Map<String, Object> variables = Map.of(
    "timestamp", ZonedDateTime.now(),
    "userCount", 1234567,
    "revenue", 9876543.21
);

Prompt prompt = template.apply(variables);
```

## 模板最佳实践

### 1. 明确的指令

```java
// 不推荐 - 模糊的指令
PromptTemplate.from("写一些关于 Java 的内容")

// 推荐 - 明确的指令
PromptTemplate.from(
    "请作为一位有10年经验的Java架构师，撰写一篇关于" +
    "微服务架构设计的文章，要求：\n" +
    "1. 介绍微服务的核心概念\n" +
    "2. 分析优缺点\n" +
    "3. 提供实践建议"
)
```

### 2. 使用分隔符

```java
PromptTemplate.from(
    "请分析以下代码并找出潜在问题：\n" +
    "```java\n" +
    "{{code}}\n" +
    "```\n" +
    "问题分析："
)
```

### 3. 提供示例

```java
PromptTemplate.from(
    "将以下自然语言转换为 SQL 查询。\n\n" +
    "示例：\n" +
    "输入：查找所有年龄大于30的用户\n" +
    "输出：SELECT * FROM users WHERE age > 30\n\n" +
    "现在请转换：\n" +
    "输入：{{userInput}}\n" +
    "输出："
)
```

### 4. 结构化输出

```java
PromptTemplate.from(
    "请按照以下 JSON 格式输出分析结果：\n" +
    "```json\n" +
    "{\n" +
    "  \"sentiment\": \"positive|neutral|negative\",\n" +
    "  \"confidence\": 0.0-1.0,\n" +
    "  \"keywords\": [\"keyword1\", \"keyword2\"],\n" +
    "  \"summary\": \"一句话总结\"\n" +
    "}\n" +
    "```\n\n" +
    "分析文本：{{text}}"
)
```

## 模板复用

将常用的模板定义为常量：

```java
public class PromptTemplates {

    public static final PromptTemplate SUMMARIZATION = 
        PromptTemplate.from(
            "请用{{length}}个字数总结以下内容：\n" +
            "{{content}}"
        );

    public static final PromptTemplate TRANSLATION = 
        PromptTemplate.from(
            "将以下文字翻译成{{targetLanguage}}：\n" +
            "{{content}}"
        );

    public static final PromptTemplate CODE_REVIEW = 
        PromptTemplate.from(
            "请审查以下代码，找出潜在问题并给出改进建议：\n" +
            "```{{language}}\n" +
            "{{code}}\n" +
            "```"
        );
}

// 使用
Map<String, Object> vars = Map.of(
    "length", "200",
    "content", longText
);
Prompt prompt = PromptTemplates.SUMMARIZATION.apply(vars);
```

## 下一步

- [内存管理](./MemoryManagement/index.md) - 学习如何在多轮对话中维护上下文
- [链式调用](./Chain/index.md) - 了解如何组合多个处理步骤
- [RAG 检索增强生成](./Rag/index.md) - 构建基于知识库的问答系统
