### Spring Boot集成

对于企业级应用，将LangChain4j与Spring Boot集成是最常见的选择。Spring Boot提供了依赖注入、配置管理、健康检查等企业级功能，可以显著简化LangChain4j应用的管理。以下是一个完整的Spring Boot集成示例。

首先，添加必要的依赖到pom.xml：

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-spring-boot-starter</artifactId>
    </dependency>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-open-ai-spring-boot-starter</artifactId>
    </dependency>
</dependencies>
```

配置application.yml：

```yaml
langchain4j:
  open-ai:
    api-key: ${OPENAI_API_KEY}
    chat-model:
      gpt-4:
        temperature: 0.7
        max-tokens: 2000
```

创建服务类：

```java
package com.example.service;

import dev.langchain4j.model.chat.ChatLanguageModel;
import org.springframework.stereotype.Service;

@Service
public class AiChatService {

    private final ChatLanguageModel chatModel;

    public AiChatService(ChatLanguageModel chatModel) {
        this.chatModel = chatModel;
    }

    public String chat(String message) {
        return chatModel.generate(message);
    }
}
```

创建控制器：

```java
package com.example.controller;

import com.example.service.AiChatService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/chat")
public class ChatController {

    private final AiChatService chatService;

    public ChatController(AiChatService chatService) {
        this.chatService = chatService;
    }

    @PostMapping
    public String chat(@RequestBody String message) {
        return chatService.chat(message);
    }
}
```

> com/example/ChatApplication.java

#### DashScope Spring Boot集成

对于Spring Boot应用，DashScope提供了便捷的集成方式。通过自定义配置类和属性绑定，可以将DashScope模型配置纳入Spring的依赖注入体系，实现与其他Spring组件的无缝集成。

```properties
# application.yml

dashscope:
  enabled: true
  api-key: ${DASHSCOPE_API_KEY}
  model-name: qwen-plus
  temperature: 0.7
  max-tokens: 4096
  base-url: https://dashscope.aliyuncs.com/compatible-mode/v1
```

```java
// LangChain4j/DashScopeProperties.java

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Component
@ConfigurationProperties(prefix = "dashscope")
public class DashScopeProperties {

    private boolean enabled = false;
    private String apiKey;
    private String modelName = "qwen-plus";
    private double temperature = 0.7;
    private int maxTokens = 4096;
    private String baseUrl = "https://dashscope.aliyuncs.com/compatible-mode/v1";

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public String getApiKey() {
        return apiKey;
    }

    public void setApiKey(String apiKey) {
        this.apiKey = apiKey;
    }

    public String getModelName() {
        return modelName;
    }

    public void setModelName(String modelName) {
        this.modelName = modelName;
    }

    public double getTemperature() {
        return temperature;
    }

    public void setTemperature(double temperature) {
        this.temperature = temperature;
    }

    public int getMaxTokens() {
        return maxTokens;
    }

    public void setMaxTokens(int maxTokens) {
        this.maxTokens = maxTokens;
    }

    public String getBaseUrl() {
        return baseUrl;
    }

    public void setBaseUrl(String baseUrl) {
        this.baseUrl = baseUrl;
    }
}
```

```java
// LangChain4j/DashScopeAutoConfig.java

import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.model.chat.ChatLanguageModel;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConditionalOnProperty(name = "dashscope.enabled", havingValue = "true", matchIfMissing = false)
public class DashScopeAutoConfig {

    private final DashScopeProperties properties;

    public DashScopeAutoConfig(DashScopeProperties properties) {
        this.properties = properties;
    }

    @Bean
    public ChatLanguageModel dashscopeChatModel() {
        return OpenAiChatModel.builder()
                .apiKey(properties.getApiKey())
                .modelName(properties.getModelName())
                .baseUrl(properties.getBaseUrl())
                .temperature(properties.getTemperature())
                .maxTokens(properties.getMaxTokens())
                .build();
    }
}
```

```java
// LangChain4j/DashScopeChatService.java

import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.data.message.AiMessage;
import org.springframework.stereotype.Service;

@Service
public class DashScopeChatService {

    private final ChatLanguageModel chatModel;

    public DashScopeChatService(ChatLanguageModel chatModel) {
        this.chatModel = chatModel;
    }

    public String chat(String userInput) {
        UserMessage userMessage = UserMessage.from(userInput);
        AiMessage response = chatModel.generate(userMessage);
        return response.text();
    }

    public String chatWithSystemPrompt(String userInput, String systemPrompt) {
        return chatModel.generate(
            dev.langchain4j.data.message.SystemMessage.from(systemPrompt),
            UserMessage.from(userInput)
        ).text();
    }
}
```

#### 

#### 千帆Spring Boot Starter配置

对于Spring Boot项目，可以使用以下配置方式集成千帆：

```properties
# application.properties

# 百度千帆配置
qianfan.api-key=${QIANFAN_API_KEY}
qianfan.secret-key=${QIANFAN_SECRET_KEY}
qianfan.access-token=${QIANFAN_ACCESS_TOKEN}
```

```java
// LangChain4j/QianfanAutoConfig.java

import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.model.chat.ChatModel;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableConfigurationProperties(QianfanProperties.class)
public class QianfanAutoConfig {

    private final QianfanProperties properties;

    public QianfanAutoConfig(QianfanProperties properties) {
        this.properties = properties;
    }

    @Bean
    @ConditionalOnProperty(name = "qianfan.enabled", havingValue = "true", matchIfMissing = false)
    public ChatModel qianfanChatModel() throws Exception {
        QianfanAuth auth = new QianfanAuth(properties.getApiKey(), properties.getSecretKey());
        String accessToken = auth.getAccessToken();

        return OpenAiChatModel.builder()
                .apiKey(accessToken)
                .modelName(properties.getModelName())
                .baseUrl("https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat")
                .temperature(properties.getTemperature())
                .maxTokens(properties.getMaxTokens())
                .build();
    }
}
```

```java
// LangChain4j/QianfanProperties.java

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "qianfan")
public class QianfanProperties {

    private boolean enabled = false;
    private String apiKey;
    private String secretKey;
    private String accessToken;
    private String modelName = "ernie-bot-4";
    private double temperature = 0.7;
    private int maxTokens = 2048;

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public String getApiKey() {
        return apiKey;
    }

    public void setApiKey(String apiKey) {
        this.apiKey = apiKey;
    }

    public String getSecretKey() {
        return secretKey;
    }

    public void setSecretKey(String secretKey) {
        this.secretKey = secretKey;
    }

    public String getAccessToken() {
        return accessToken;
    }

    public void setAccessToken(String accessToken) {
        this.accessToken = accessToken;
    }

    public String getModelName() {
        return modelName;
    }

    public void setModelName(String modelName) {
        this.modelName = modelName;
    }

    public double getTemperature() {
        return temperature;
    }

    public void setTemperature(double temperature) {
        this.temperature = temperature;
    }

    public int getMaxTokens() {
        return maxTokens;
    }

    public void setMaxTokens(int maxTokens) {
        this.maxTokens = maxTokens;
    }
}
```

#### 