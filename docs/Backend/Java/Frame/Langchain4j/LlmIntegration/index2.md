# Langchain4j 大语言模型集成

大语言模型集成是LangChain4j最核心的功能之一，它提供了与各类模型提供商交互的统一接口。可以根据项目需求灵活选择最适合的模型方案。

官方文档：https://docs.langchain4j.dev/integrations/language-models

## 模型集成概述

LangChain4j采用**适配器模式**来实现对多种大语言模型的支持。每种模型提供商都有一个对应的模块，包含该模型的特定实现。所有这些实现都遵循统一的ChatModel接口，这意味着无论使用哪种模型，上层代码都可以保持一致。这种设计使得切换模型提供商变得非常简单，只需更改依赖和配置即可，无需修改业务逻辑代码。

模型集成的配置通常包括API密钥、模型名称、生成参数等必要信息。不同的模型提供商有不同的认证方式和端点，LangChain4j已经封装了这些差异，开发者只需要提供相应的配置即可。框架还支持环境变量配置，使得在不同环境（开发、测试、生产）之间切换配置变得非常便捷。

## OpenAI集成

OpenAI是目前最知名的大语言模型提供商，其GPT系列模型在各类AI应用中广泛使用。LangChain4j提供了完整的OpenAI集成支持，包括ChatGPT和GPT-4等模型。通过OpenAiChatModel类，可以轻松调用OpenAI的API来生成自然语言响应。

### OpenAI 添加依赖

在开始使用OpenAI之前，需要将相应的依赖添加到项目中。LangChain4j将OpenAI支持独立为一个模块，可以根据需要选择不同的依赖配置方式。使用BOM可以自动管理版本，确保所有LangChain4j模块的版本兼容性。

```xml
<dependencies>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-open-ai</artifactId>
    </dependency>
    
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j</artifactId>
    </dependency>
</dependencies>
```

对于Maven项目，使用BOM来管理版本是最佳实践，可以避免版本冲突并简化依赖管理：

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>dev.langchain4j</groupId>
            <artifactId>langchain4j-bom</artifactId>
            <version>1.10.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-open-ai</artifactId>
    </dependency>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j</artifactId>
    </dependency>
</dependencies>
```

### OpenAI 创建模型实例

创建OpenAI模型实例是使用OpenAI API的第一步。您需要提供API密钥来认证请求，并指定要使用的模型名称。OpenAI提供了多种模型，每种模型在能力、价格和速度方面都有所不同，选择合适的模型对于应用的性能和成本控制至关重要。

```java
public class OpenAiConfig {

    public static ChatModel createGpt4Model(String apiKey) {
        return OpenAiChatModel.builder()
                .apiKey(apiKey)
                .modelName("gpt-4")
                .temperature(0.7)
                .maxTokens(2000)
                .build();
    }

    public static ChatModel createGpt35TurboModel(String apiKey) {
        return OpenAiChatModel.builder()
                .apiKey(apiKey)
                .modelName("gpt-3.5-turbo")
                .temperature(0.7)
                .maxTokens(2000)
                .build();
    }
}
```

### 模型参数配置详解

OpenAiChatModel提供了丰富的配置参数，允许您精细控制模型的行为。这些参数直接影响生成结果的质量和特性，因此理解每个参数的含义和适用场景非常重要。

temperature参数控制生成结果的随机性。较低的值（如0.2）会产生更加确定性的输出，适合需要精确性的任务；较高的值（如0.8）会产生更有创意和多样性的输出，适合内容创作场景。topP参数与temperature类似，控制核采样的范围，两者通常只设置其中一个。maxTokens参数限制生成的最大token数量，防止输出过长并有助于控制API成本。

```java
OpenAiChatModel model = OpenAiChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-4-turbo")
        .temperature(0.3)          // 较低温度，适合精确任务
        .topP(1.0)
        .presencePenalty(0.0)      // 降低重复内容的可能性
        .frequencyPenalty(0.0)     // 降低高频词的使用频率
        .logProbs(false)           // 不返回对数概率
        .topLogProbs(null)
        .maxTokens(4096)           // 限制最大输出长度
        .seed(42)                  // 设置随机种子以获得可重复的结果
        .stop(null)                // 自定义停止词
        .build();
```

### Azure OpenAI集成

对于企业用户，Azure OpenAI提供了在Azure云平台上部署OpenAI模型的能力，具有更好的合规性和数据安全保障。LangChain4j同样支持Azure OpenAI，与标准OpenAI API的使用方式类似，但需要提供Azure特有的认证信息。

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-azure-open-ai</artifactId>
    <version>1.10.0</version>
</dependency>
```

```java
import dev.langchain4j.model.azure.OpenAiChatModel;

public class AzureOpenAiConfig {

    public static OpenAiChatModel createAzureModel() {
        return OpenAiChatModel.builder()
                .apiKey(System.getenv("AZURE_OPENAI_API_KEY"))
                .endpoint("https://your-resource.openai.azure.com/")
                .deploymentName("gpt-4")
                .temperature(0.7)
                .build();
    }
}
```

Azure OpenAI需要额外的配置，包括资源端点和部署名称。您可以在Azure门户中创建OpenAI资源并部署所需的模型。与标准OpenAI API相比，Azure版本提供了企业级的安全性和合规性保障，适合对数据安全有严格要求的应用场景。

## Anthropic集成

Anthropic是由前OpenAI研究人员创立的AI公司，其Claude系列模型以安全性和可控性著称。Claude在长文本理解、复杂推理和遵守指令方面表现出色，是构建专业AI应用的优秀选择。LangChain4j通过langchain4j-anthropic模块提供了对Claude模型的支持。

### Anthropic 添加依赖

```xml
<dependencies>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-anthropic</artifactId>
    </dependency>
</dependencies>
```

### 创建Claude模型实例

Anthropic提供了多个Claude模型版本，包括Claude 3 Haiku（快速轻量）、Claude 3 Sonnet（平衡性能）和Claude 3 Opus（最高性能）。可以根据任务复杂度和响应时间要求选择合适的模型。Claude模型特别擅长长文档分析、代码编写和遵循复杂的指令集。

```java
import dev.langchain4j.model.anthropic.AnthropicChatModel;
import dev.langchain4j.model.anthropic.AnthropicChatModelName;

public class AnthropicConfig {

    public static AnthropicChatModel createClaudeModel(String apiKey) {
        return AnthropicChatModel.builder()
                .apiKey(apiKey)
                .modelName(AnthropicChatModelName.CLAUDE_3_5_HAIKU_20241022)
                .temperature(0.7)
                .maxTokens(2000)
                .build();
    }
}
```

## Ollama本地模型集成

Ollama是一个允许在本地运行大语言模型的平台。通过Ollama，可以部署如Llama、Mistral等开源模型，无需依赖外部API服务，既保护了数据隐私，又可以降低成本。LangChain4j支持与Ollama的集成，使本地模型的使用体验与调用云端API一样简单。

### Ollama 安装与配置

首先需要在机器上安装Ollama。Ollama支持Windows、macOS和Linux系统，提供了一键安装包。安装完成后，您可以通过命令行拉取和运行各种开源模型。

```bash
# 安装Ollama后，拉取模型
ollama pull llama3.2
ollama pull mistral
ollama pull qwen2

# 运行模型服务
ollama serve
```

Ollama默认在本地11434端口启动API服务。可以通过简单的HTTP请求来测试服务是否正常运行。LangChain4j通过与这个API服务通信来调用本地模型，提供与云端API相同的接口体验。

### Ollama 添加依赖

```xml
<dependencies>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-ollama</artifactId>
    </dependency>
</dependencies>
```

### Ollama 创建模型实例

Ollama支持多种参数配置来调整模型行为。temperature控制随机性，topK和topP控制采样策略，repeatPenalty减少重复输出。这些参数与云端API的参数类似，便于在云端和本地模型之间迁移代码。

```java
import dev.langchain4j.model.ollama.OllamaChatModel;
import dev.langchain4j.model.chat.ChatModel;

public class OllamaConfig {

    public static ChatModel createLlamaModel() {
        return OllamaChatModel.builder()
                .baseUrl("http://localhost:11434")
                .modelName("llama3.2")
                .temperature(0.7)
                .build();
    }

    public static ChatModel createMistralModel() {
        return OllamaChatModel.builder()
                .baseUrl("http://localhost:11434")
                .modelName("mistral")
                .temperature(0.7)
                .topK(50)
                .topP(0.9)
                .build();
    }
}
```

```java
import dev.langchain4j.model.ollama.OllamaChatModel;

public class LocalModelDemo {

    public static void main(String[] args) {
        ChatModel model = OllamaChatModel.builder()
                .baseUrl("http://localhost:11434")
                .modelName("llama3.2")
                .build();

        String response = model.chat("用一句话介绍你自己");
        System.out.println(response);
    }
}
```

## 国产大模型集成

随着国内AI技术的快速发展，越来越多的国产大语言模型可供选择。目前LangChain4j官方对国产大模型的支持主要体现在对OpenAI兼容API的支持上，大部分国产模型都提供了与OpenAI API格式兼容的接口，可以直接使用OpenAI集成方式或通过配置端点来调用。此外，LangChain4j官方还提供了对智谱AI的原生支持。

::: tip
大部分国产大模型（如通义千问、文心一言、讯飞星火、DeepSeek等）都提供了与OpenAI兼容的API接口。可以使用OpenAI客户端或配置自定义端点来调用这些模型。
:::

### 智谱ChatGLM集成

智谱AI的ChatGLM系列模型是国内开源大模型的代表之一，在学术界和工业界都有广泛应用。LangChain4j通过langchain4j-zhipu模块提供了对智谱AI的原生支持。

#### 智谱AI 添加依赖

:::code-group

```xml [1.0.0-alpha1之前]
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-zhipu-ai</artifactId>
    <version>${previous version here}</version>
</dependency>
```

```xml [1.0.0-alpha1及之后]
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-zhipu-ai</artifactId>
    <version>${previous version here}</version>
</dependency>
```

:::

可以使用 BOM 来一致地管理依赖项：

```xml
<dependencyManagement>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-community-bom</artifactId>
        <version>1.10.0-beta18</version>
        <type>pom</type>
        <scope>import</scope>
    </dependency>
</dependencyManagement>
```

#### 智谱AI 创建模型实例

智谱AI提供了多个模型版本，包括GLM-4、GLM-3-Turbo等。您可以根据需求选择合适的模型。

:::tip

智谱AI的API认证只需要API Key，无需额外的Secret Key。需要在智谱AI开放平台申请API Key后才能使用服务。

:::

```java
import dev.langchain4j.community.model.zhipu.ZhipuAiChatModel;
import dev.langchain4j.model.chat.ChatModel;

public class ZhipuConfig {

    public static ChatModel createChatGlmModel() {
        return ZhipuAiChatModel.builder()
                .apiKey(System.getenv("ZHIPU_API_KEY"))
                .model("glm-4")
                .temperature(0.7)
                .maxToken(2000)
                .build();
    }

    public static ChatModel createChatGlmTurboModel() {
        return ZhipuAiChatModel.builder()
                .apiKey(System.getenv("ZHIPU_API_KEY"))
                .model("glm-3-turbo")
                .temperature(0.7)
                .maxToken(2000)
                .build();
    }
}
```

### DashScope(通义千问)集成

DashScope是阿里巴巴云原生数据智能服务团队推出的大模型服务平台，通义千问（Qwen）系列大语言模型便是基于该平台提供服务。通义千问模型在中文理解、多轮对话、逻辑推理等方面表现优异，广泛应用于电商、智能客服、内容创作等场景。DashScope平台提供了完善的API接口，支持通过OpenAI兼容模式进行调用，使得现有基于OpenAI的开发代码可以轻松迁移。

DashScope平台的核心理念是为开发者提供稳定、可靠、高性能的大模型服务。平台采用按调用量计费模式，提供免费额度供开发者测试使用。与其他国产大模型平台相比，DashScope的API接口设计更加规范化，与OpenAI API的兼容度最高，这使得开发者可以以最小的代码改动将应用切换到通义千问模型。此外，平台还提供了丰富的模型选择，从轻量级的Qwen-Turbo到高性能的Qwen-Max，能够满足不同业务场景的需求。

#### DashScope 平台模型详解

DashScope平台提供了多个版本的通义千问模型，每个版本在性能、响应速度和价格方面各有特点，开发者可以根据实际需求选择最适合的模型版本。

| 模型名称 | 模型ID | 上下文长度 | 特点说明 | 适用场景 |
|---------|--------|-----------|---------|---------|
| Qwen-Max | qwen-max | 16K | 通义千问旗舰模型，综合能力最强 | 复杂推理、专业写作、高质量内容生成 |
| Qwen-Plus | qwen-plus | 32K | 平衡型模型，性价比高 | 日常对话、知识问答、内容摘要 |
| Qwen-Turbo | qwen-turbo | 16K | 轻量级模型，响应速度快 | 实时交互、高并发场景、简单问答 |
| Qwen1.5-110B | qwen1.5-110b | 32K | 开源大模型，灵活可控 | 企业定制、长文本处理、多语言任务 |
| Qwen-VL | qwen-vl | 16K | 视觉语言模型，支持图像理解 | 图文理解、多模态任务、视觉问答 |

Qwen-Max作为旗舰模型，在各项基准测试中表现最为出色，特别适合需要深度推理和专业知识的场景。该模型支持超长上下文理解，可以处理复杂的对话历史和长篇文档。Qwen-Plus则在性能和成本之间取得了良好平衡，是大多数应用场景的首选。Qwen-Turbo专为对响应速度有高要求的场景设计，虽然在复杂任务上略逊于前两者，但其快速响应特性使其成为实时交互系统的理想选择。

#### DashScope 添加依赖

:::code-group

```xml [1.0.0-alpha1之前]

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-dashscope</artifactId>
    <version>${previous version here}</version>
</dependency>
```

```xml [1.0.0-alpha1及之后]
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-dashscope</artifactId>
    <version>${latest version here}</version>
</dependency>
```

:::

可以使用 BOM 来一致地管理依赖项：

```xml
<dependencyManagement>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-community-bom</artifactId>
        <version>1.10.0-beta18</version>
        <type>pom</type>
        <scope>import</scope>
    </dependency>
</dependencyManagement>
```

#### DashScope API认证配置

DashScope采用API Key进行身份认证，开发者需要在阿里云控制台创建DashScope服务并获取API Key。整个认证流程非常简单，只需在请求头中携带API Key即可完成身份验证。为了保护API Key的安全，建议通过环境变量或安全的配置中心进行管理，避免将密钥硬编码在源代码中。

获取API Key的步骤如下：首先登录阿里云控制台，搜索并开通DashScope服务；然后在访问凭证管理页面创建新的API Key；最后将API Key妥善保存并配置到应用环境中。API Key具有完全访问您账户下DashScope服务的权限，因此必须像保护密码一样保护它，不要在客户端代码、版本控制系统或公开渠道中暴露API Key。

```java
public class DashScopeConfig {

    public static ChatModel createQwenMaxModel() {
        return QwenChatModel.builder()
                .apiKey(System.getenv("DASHSCOPE_API_KEY"))
                .modelName("qwen-max")
                .temperature(0.7F)
                .maxTokens(4096)
                .build();
    }

    public static ChatModel createQwenPlusModel() {
        return QwenChatModel.builder()
                .apiKey(System.getenv("DASHSCOPE_API_KEY"))
                .modelName("qwen-plus")
                .temperature(0.7F)
                .maxTokens(4096)
                .build();
    }

    public static ChatModel createQwenTurboModel() {
        return QwenChatModel.builder()
                .apiKey(System.getenv("DASHSCOPE_API_KEY"))
                .modelName("qwen-turbo")
                .temperature(0.7F)
                .maxTokens(4096)
                .build();
    }
}
```

#### DashScope 高级参数配置

通义千问模型支持丰富的生成参数配置，开发者可以通过这些参数精细控制模型输出的行为。以下是一些常用参数的详细说明及其适用场景。

temperature参数控制输出的随机性，取值范围通常在0到1之间。当temperature接近0时，模型输出更加确定和保守，适合需要精确答案的场景；当temperature接近1时，模型输出更加多样化和有创意，适合内容创作场景。topP参数控制核采样的范围，与temperature类似但机制不同，通常建议只设置其中一个参数。maxTokens参数限制模型生成内容的最大长度，以token为单位计算，合理设置可以控制响应长度和API成本。

搜索增强是通义千问特有的功能之一，通过在extraParameters中设置enable_search为true，可以让模型在生成回答前先进行互联网搜索，从而获取最新、最准确的信息。这个功能特别适合回答时效性问题或需要引用最新数据查询结果的场景。启用搜索增强后，模型会在回答中标注信息来源，增强了回答的可信度和可追溯性。

```java
public class DashScopeAdvancedConfig {

    public static ChatModel createPreciseModel() {
        return QwenChatModel.builder()
                .apiKey(System.getenv("DASHSCOPE_API_KEY"))
                .modelName("qwen-max")
                .baseUrl("https://dashscope.aliyuncs.com/compatible-mode/v1")
                .temperature(0.1F)
                .topP(0.5)
                .maxTokens(2000)
                .build();
    }

    public static ChatModel createCreativeModel() {
        return QwenChatModel.builder()
                .apiKey(System.getenv("DASHSCOPE_API_KEY"))
                .modelName("qwen-max")
                .baseUrl("https://dashscope.aliyuncs.com/compatible-mode/v1")
                .temperature(0.9F)
                .topP(0.95)
                .maxTokens(4096)
                .build();
    }

    public static ChatModel createSearchEnhancedModel() {
        return QwenChatModel.builder()
                .apiKey(System.getenv("DASHSCOPE_API_KEY"))
                .modelName("qwen-turbo")
                .baseUrl("https://dashscope.aliyuncs.com/compatible-mode/v1")
                .temperature(0.7F)
                .maxTokens(2048)
                .enableSearch(true)
                .build();
    }
}
```

#### DashScope 注意事项

在使用DashScope平台时，开发者需要注意以下几个关键点，以确保应用的稳定性和成本控制。

::: danger
1. **API调用限制**：DashScope对API调用频率有严格限制，不同模型的QPS限制不同。超过限制会触发限流错误，建议在生产环境中实现指数退避重试机制。

2. **成本控制**：虽然DashScope提供免费额度，但生产环境使用会产生费用。请在阿里云控制台设置费用预警，并定期检查API调用账单。

3. **内容安全**：通义千问内置了内容安全过滤机制，对于涉及敏感话题的请求可能会拒绝处理或返回安全提示。开发者需要根据业务需求做好相应的错误处理。

4. **版本兼容性**：DashScope平台的API接口会定期更新，建议定期查阅官方文档，确保代码与最新API版本兼容。


:::

### DeepSeek集成

DeepSeek是近年来快速崛起的国产大模型提供商，其DeepSeek-V2和DeepSeek-Coder等模型在性能和性价比方面表现出色，备受开发者关注。

DeepSeek同样提供与OpenAI兼容的API接口，无需额外的依赖。

```java
// LangChain4j/DeepSeekConfig.java

import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.model.chat.ChatModel;

public class DeepSeekConfig {

    public static ChatModel createDeepSeekChatModel() {
        return OpenAiChatModel.builder()
                .apiKey(System.getenv("DEEPSEEK_API_KEY"))
                .modelName("deepseek-chat")
                .baseUrl("https://api.deepseek.com/v1")
                .temperature(0.7)
                .maxTokens(4000)
                .build();
    }

    public static ChatModel createDeepSeekCoderModel() {
        return OpenAiChatModel.builder()
                .apiKey(System.getenv("DEEPSEEK_API_KEY"))
                .modelName("deepseek-coder")
                .baseUrl("https://api.deepseek.com/v1")
                .temperature(0.7)
                .maxTokens(4000)
                .build();
    }
}
```

### 讯飞星火集成

讯飞星火是科大讯飞推出的大语言模型，在语音交互、自然语言处理等方面有独特优势。

使用OpenAI协议协议兼容方式集成：

```java
// LangChain4j/SparkConfig.java

import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.model.chat.ChatModel;

public class SparkConfig {

    public static ChatModel createSparkV3Model() {
        return OpenAiChatModel.builder()
                .apiKey(System.getenv("SPARK_API_KEY"))
                .modelName("spark-v3.5")
                .baseUrl("https://spark-api.xf-yun.com/v3.5/chat")
                .temperature(0.7)
                .build();
    }

    public static ChatModel createSparkV2Model() {
        return OpenAiChatModel.builder()
                .apiKey(System.getenv("SPARK_API_KEY"))
                .modelName("spark-v2.0")
                .baseUrl("https://spark-api.xf-yun.com/v2.1/chat")
                .temperature(0.7)
                .build();
    }
}
```

### MiniMax集成

MiniMax是专注于大模型技术的公司，其Abab系列模型在对话场景中表现优秀。

```java
// LangChain4j/MiniMaxConfig.java

import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.model.chat.ChatModel;

public class MiniMaxConfig {

    public static ChatModel createAbab65ChatModel() {
        return OpenAiChatModel.builder()
                .apiKey(System.getenv("MINIMAX_API_KEY"))
                .modelName("abab6.5-chat")
                .baseUrl("https://api.minimax.chat/v1/text/chatcompletion_v2")
                .temperature(0.7)
                .build();
    }
}
```

### Moonshot Kimi集成

Moonshot AI的Kimi系列模型以其长文本处理能力著称，是国产大模型中的新锐力量。

```java
// LangChain4j/MoonshotConfig.java

import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.model.chat.ChatModel;

public class MoonshotConfig {

    public static ChatModel createKimiChatModel() {
        return OpenAiChatModel.builder()
                .apiKey(System.getenv("MOONSHOT_API_KEY"))
                .modelName("moonshot-v1-128k")
                .baseUrl("https://api.moonshot.cn/v1")
                .temperature(0.7)
                .build();
    }

    public static ChatModel createKimiChat8kModel() {
        return OpenAiChatModel.builder()
                .apiKey(System.getenv("MOONSHOT_API_KEY"))
                .modelName("moonshot-v1-8k")
                .baseUrl("https://api.moonshot.cn/v1")
                .temperature(0.7)
                .build();
    }
}
```

### 百度千帆集成

百度千帆平台是百度智能云提供的大模型服务平台，整合了文心一言等多种大语言模型，并提供统一的API调用接口。千帆平台的优势在于提供了一站式的大模型服务，包括模型管理、API调用、监控计费等完整功能。通过千帆平台，开发者可以方便地调用多种文心一言系列模型，以及其他第三方大模型。

#### 千帆平台模型列表

千帆平台提供了丰富的模型选择，包括以下主要模型：

| 模型名称 | 模型ID | 适用场景 | 特点 |
|---------|--------|---------|------|
| ERNIE-Bot-4 | ernie-bot-4 | 复杂对话、写作、编程 | 百度最强文心模型，支持超长文本 |
| ERNIE-Bot-Turbo | ernie-bot-turbo | 快速响应场景 | 响应速度快，适合实时对话 |
| ERNIE-Bot | ernie-bot | 通用对话场景 | 经典文心模型，稳定可靠 |
| ERNIE-Speed-8K | ernie-speed-8k | 高并发场景 | 性价比高，适合大规模调用 |
| ERNIE-Speed-128K | ernie-speed-128k | 长文本理解场景 | 支持超长上下文，理解能力强 |
| BLOOMZ-7B | bloomz-7b1 | 开源模型应用 | 开源可商用，灵活可控 |

#### 千帆 添加依赖

:::code-group

```xml [1.0.0-alpha1之前]
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-qianfan</artifactId>
    <version>${previous version here}</version>
</dependency>
```

```xml [1.0.0-alpha1及之后]
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-qianfan</artifactId>
    <version>${latest version here}</version>
</dependency>
```

:::

可以使用 BOM 来一致地管理依赖项：

```xml
<dependencyManagement>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-community-bom</artifactId>
        <version>1.10.0-beta18</version>
        <type>pom</type>
        <scope>import</scope>
    </dependency>
</dependencyManagement>
```

#### 千帆ERNIE-Bot集成

千帆平台的API认证采用Access Token机制，需要先通过API Key和Secret Key获取访问令牌，然后再使用访问令牌调用模型API。这种认证方式比直接在请求中传递API Key更加安全，可以有效保护Secret Key的安全。建议在应用启动时预先获取Access Token并设置合理的过期时间，在Token过期前自动刷新，避免因Token过期导致请求失败。

```java
public class QianfanConfig {

    public static ChatModel createQianfanModel() {
        return QianfanChatModel.builder()
                .apiKey(System.getenv("ERNIE_API_KEY"))
                .secretKey("secretKey")
                .modelName("Yi-34B-Chat")
                .temperature(0.7)
                .build();
    }
}
```

#### 千帆平台注意事项

::: danger

1. **Access Token有效期**：Access Token的默认有效期为30天（2592000秒），需要在Token过期前及时刷新。建议设置过期前5分钟自动刷新机制。

2. **API调用频率限制**：千帆平台对API调用有频率限制，不同模型的QPS限制不同。ERNIE-Bot-4的QPS限制为2，ERNIE-Bot-Turbo的QPS限制为10。超过限制会返回错误。

3. **费用控制**：千帆平台采用按调用次数计费模式，请务必在百度智能云控制台设置费用预警，避免产生意外费用。

4. **敏感内容过滤**：百度文心一言内置了敏感内容过滤机制，如果输入或输出包含敏感内容，API会返回错误并提示过滤原因。
:::

### 国产大模型统一工厂

为了便于管理多个国产大模型，可以创建一个统一的工厂类来管理不同提供商的模型实例。

```java
// LangChain4j/DomesticModelFactory.java

import dev.langchain4j.model.chat.ChatModel;
import java.util.Map;
import java.util.HashMap;
import java.util.function.Supplier;

public class DomesticModelFactory {

    private final Map<String, Supplier<ChatModel>> modelSuppliers;

    public DomesticModelFactory() {
        this.modelSuppliers = new HashMap<>();
    }

    public void registerModel(String provider, Supplier<ChatModel> supplier) {
        modelSuppliers.put(provider, supplier);
    }

    public ChatModel getModel(String provider) {
        Supplier<ChatModel> supplier = modelSuppliers.get(provider);
        if (supplier == null) {
            throw new IllegalArgumentException("未注册的模型提供商: " + provider);
        }
        return supplier.get();
    }

    public static DomesticModelFactory createDefaultFactory() {
        DomesticModelFactory factory = new DomesticModelFactory();

        factory.registerModel("qwen-turbo", () ->
                OpenAiChatModel.builder()
                        .apiKey(System.getenv("TONGYI_API_KEY"))
                        .modelName("qwen-turbo")
                        .baseUrl("https://dashscope.aliyuncs.com/compatible-mode/v1")
                        .temperature(0.7)
                        .build());

        factory.registerModel("ernie-bot-4", () ->
                OpenAiChatModel.builder()
                        .apiKey(System.getenv("BAIDU_API_KEY"))
                        .modelName("ernie-bot-4")
                        .baseUrl("https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat")
                        .temperature(0.7)
                        .build());

        factory.registerModel("glm-4", () ->
                ZhipuAiChatModel.builder()
                        .apiKey(System.getenv("ZHIPU_API_KEY"))
                        .model("glm-4")
                        .temperature(0.7)
                        .build());

        factory.registerModel("deepseek-chat", () ->
                OpenAiChatModel.builder()
                        .apiKey(System.getenv("DEEPSEEK_API_KEY"))
                        .modelName("deepseek-chat")
                        .baseUrl("https://api.deepseek.com/v1")
                        .temperature(0.7)
                        .build());

        return factory;
    }
}
```

### 国产大模型对比

在选择国产大语言模型时，需要综合考虑模型性能、API价格、响应速度、功能特性等因素。

::: tip
建议根据具体业务场景进行模型对比测试，选择最适合的模型。不同模型在不同任务上的表现可能有较大差异。
:::

| 模型提供商 | 模型名称 | 主要特点 | 适用场景 |
|-----------|---------|---------|---------|
| 智谱AI | GLM-4 | 原生支持，中文能力强 | 通用对话、代码生成 |
| 阿里 | 通义千问 | 电商场景优化，价格实惠 | 电商、客服、业务咨询 |
| 百度 | 文心一言 | 搜索增强，知识图谱 | 知识问答、搜索增强 |
| DeepSeek | DeepSeek-V2 | 高性价比，代码能力强 | 编程、技术文档 |
| 讯飞 | 星火 | 语音交互优化 | 语音助手、多模态 |
| MiniMax | Abab6.5 | 对话体验好 | 社交对话、陪伴 |
| Moonshot | Kimi | 超长文本支持 | 长文档分析、研究 |

## HuggingFace集成

HuggingFace是机器学习社区的重要平台，托管了数以万计的开源模型。LangChain4j支持与HuggingFace的集成，可以使用HuggingFace上托管的各类模型，包括专门针对特定任务微调的模型。

### 添加HuggingFace依赖

```xml
<dependencies>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-huggingface</artifactId>
    </dependency>
</dependencies>
```

### 使用HuggingFace模型

HuggingFace集成支持两种使用方式：调用HuggingFace Inference API云端服务，或者使用HuggingFace Transformers库在本地运行模型。两种方式有不同的适用场景，可以根据需求选择。

对于本地运行模型，需要设置适当的硬件配置（GPU、内存等），并处理模型加载和推理的优化。HuggingFace本地推理适合对延迟敏感或需要保护数据隐私的场景。

```java
import dev.langchain4j.model.huggingface.HuggingFaceChatModel;
import dev.langchain4j.model.chat.ChatModel;

public class HuggingFaceConfig {

    // 使用云端Inference API
    public static ChatModel createCloudModel() {
        return HuggingFaceChatModel.builder()
                .apiKey(System.getenv("HUGGINGFACE_API_KEY"))
                .modelId("meta-llama/Llama-3.2-1B")
                .temperature(0.7)
                .build();
    }
}
```



