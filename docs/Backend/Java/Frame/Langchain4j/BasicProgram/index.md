# Langchain4j 构建入门程序

## 环境准备

在开始使用LangChain4j之前，需要确保开发环境满足必要的要求。LangChain4j对Java版本有一定的要求，根据不同的功能模块可能需要不同的JDK版本。了解这些要求将帮助您避免常见的兼容性问题，确保项目能够顺利搭建和运行。

### Java版本要求

LangChain4j需要Java 17或更高版本才能运行。虽然Java 8曾经是企业应用的主流选择，但随着AI框架对现代语言特性的依赖增加，建议使用Java 17或Java 21来获得最佳性能和最新的语言特性支持。Java 21引入了虚拟线程（Virtual Threads）等革命性特性，对于构建高并发的AI应用非常有帮助。可以通过以下命令检查当前Java版本：

```bash
java -version
```

如果Java版本不符合要求，建议使用SDKMAN、Jabba或直接下载安装JDK 17/21来管理多个Java版本。对于生产环境部署，请确保目标服务器的Java版本与开发环境一致，以避免运行时兼容性问题。

### 构建工具配置

LangChain4j支持Maven和Gradle两种主流的Java构建工具。可以根据项目现有技术栈或个人偏好选择合适的方式。Maven作为Java生态中最成熟的构建工具，拥有完善的依赖管理和插件系统；Gradle则以其灵活的构建脚本和高效的增量编译著称。

:::tip

由于LangChain4j采用模块化设计，不同功能模块是独立发布的，因此可以根据实际需求选择添加相应的依赖。

:::

对于 Maven 在 `pom.xml` 中：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai</artifactId>
    <version>1.10.0</version>
</dependency>
```

如果希望使用高级 [AI 服务](https://docs.langchain4j.info/tutorials/ai-services) API，还需要添加以下依赖项：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j</artifactId>
    <version>1.10.0</version>
</dependency>
```

对于 Gradle 在 `build.gradle` 中：

```groovy
implementation 'dev.langchain4j:langchain4j-open-ai:1.10.0'
implementation 'dev.langchain4j:langchain4j:1.10.0'
```

### 依赖管理清单

Maven的BOM（Bill of Materials）机制可以统一管理所有LangChain4j模块的版本，避免版本冲突。建议在生产项目中使用BOM来管理依赖。

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
```

### API密钥配置

在使用任何大语言模型API之前，都需要获取相应的API密钥。对于OpenAI API，需要访问OpenAI官方网站注册账号并创建API密钥。请务必妥善保管API密钥，不要将其提交到版本控制系统或泄露给他人。以下是安全配置API密钥的几种推荐方式。

在开发阶段，可以使用环境变量来存储API密钥，这是最安全且便携的方式。通过环境变量配置可以在不修改代码的情况下切换不同的密钥，也便于在不同环境（开发、测试、生产）使用不同的配置。

:::danger

在生产环境中，请务必妥善处理API密钥，不要将其硬编码在源代码中。建议使用专业的密钥管理服务或环境变量来存储敏感信息。

:::

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

在Windows系统中，可以使用以下命令设置环境变量：

```powershell
$env:OPENAI_API_KEY="sk-your-api-key-here"
```

也可以在 application.properties 或 application.yml 文件中配置，但需要确保此类配置文件被添加到 .gitignore 中：

```properties
# application.properties
langchain4j.open-ai.api-key=${OPENAI_API_KEY}
langchain4j.open-ai.model-name=gpt-3.5-turbo
```

## 创建聊天模型实例

LangChain4j提供了统一的接口来访问不同的大语言模型。无论使用哪种模型，核心API都是一致的，这使得切换模型提供商变得非常简单。以下代码展示了如何创建OpenAI聊天模型实例并发送第一条消息。

```java
package com.hjc;

import dev.langchain4j.model.openai.OpenAiChatModel;

public class HelloWorld {

    public static void main(String[] args) {
        OpenAiChatModel model = OpenAiChatModel.builder()
                .baseUrl("https://dashscope.aliyuncs.com/compatible-mode/v1")
                .apiKey(System.getenv("ALIBL_API_KEY")) //从大模型平台中获取
                .modelName("qwen3-max") //指定模型名
                .temperature(0.7)
                .maxTokens(1000)
                .build();

        String response = model.chat("你好，请介绍一下你自己");
        System.out.println(response);
    }
}
```

交互式做法：

```java
package com.hjc;

import dev.langchain4j.model.openai.OpenAiChatModel;

import java.util.Scanner;

public class ChatBot {

    private final OpenAiChatModel model;

    public ChatBot() {
        this.model = OpenAiChatModel.builder()
                .baseUrl("https://dashscope.aliyuncs.com/compatible-mode/v1")
                .apiKey(System.getenv("ALIBL_API_KEY"))
                .modelName("qwen3-max")
                .temperature(0.3)
                .build();
    }

    public String chat(String userInput) {
        return model.chat(userInput);
    }

    public static void main(String[] args) {
        ChatBot bot = new ChatBot();
        Scanner scanner = new Scanner(System.in);

        System.out.println("欢迎使用ChatBot！输入'退出'结束对话。");

        while (true) {
            System.out.print("你: ");
            String input = scanner.nextLine();

            if ("退出".equals(input.trim())) {
                System.out.println("再见！");
                break;
            }

            String response = bot.chat(input);
            System.out.println("AI: " + response);
        }

        scanner.close();
    }
}
```

## 运行应用

在运行应用之前，请确保已经正确设置了API密钥环境变量，并且网络可以正常访问OpenAI的API服务。首次运行可能需要较长时间来下载必要的依赖包，请耐心等待。

使用Maven运行应用：

```bash
mvn compile exec:java -Dexec.mainClass="com.hjc.HelloWorld"
```

使用Gradle运行应用：

```bash
gradle run
```

如果一切配置正确，应该能够看到AI的响应输出。

## 高级配置

在实际项目中，可能需要对模型进行更精细的配置，以满足特定的业务需求。LangChain4j提供了丰富的配置选项，允许控制模型的各个方面，从生成内容的确定性到请求的超时时间。

ChatLanguageModel的builder提供了多种配置参数，以下是常用参数的详细说明。理解这些参数对于调优模型输出至关重要。temperature参数控制输出的随机性，较低的值（如0.2）会产生更确定性的回复，适合需要精确性的场景；较高的值（如0.8）会产生更有创意的回复，适合内容创作场景。maxTokens参数限制模型生成的最大token数量，防止产生过长的输出并帮助控制成本。

```java
OpenAiChatModel model = OpenAiChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-4")  // 指定模型名称
        .temperature(0.7)    // 控制随机性，范围0-2
        .topP(1.0)           // 核采样参数
        .maxTokens(2000)     // 最大输出token数
        .presencePenalty(0.0) // 存在惩罚，减少重复
        .frequencyPenalty(0.0) // 频率惩罚，控制词频
        .logRequests(true)   // 日志记录请求
        .logResponses(true)  // 日志记录响应
        .timeout(Duration.ofSeconds(60))  // 超时设置
        .build();
```

