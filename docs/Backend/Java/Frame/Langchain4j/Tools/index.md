# 工具调用

工具调用（Tool Calling）是让大语言模型与外部世界交互的关键能力。通过工具调用，LLM 可以执行代码、查询数据库、调用 API 等操作，极大地扩展了其应用范围。

## 工具定义

### 基本工具接口

```java
import dev.langchain4j.agent.tool.Tool;

public class WeatherTool {

    @Tool("查询指定城市的天气信息")
    public String getWeather(String city) {
        // 调用天气 API
        return "北京天气：晴，25°C";
    }

    @Tool("计算两个数的和")
    public int calculate(int a, int b) {
        return a + b;
    }
}
```

### 带参数的工具

```java
import dev.langchain4j.agent.tool.Tool;
import dev.langchain4j.agent.tool.ToolSpecifications;

public class DatabaseTool {

    @Tool("执行 SQL 查询并返回结果")
    public List<Map<String, Object>> queryDatabase(
            @ToolParameters(description = "SQL 查询语句") String sql
    ) {
        // 执行数据库查询
        return jdbcTemplate.queryForList(sql);
    }

    @Tool("在指定表中插入数据")
    public boolean insertData(
            @ToolParameters(description = "表名") String table,
            @ToolParameters(description = "数据字段，JSON 格式") String data
    ) {
        // 插入数据
        return true;
    }
}
```

## 工具注册

### 使用 ToolExecutor

```java
import dev.langchain4j.agent.tool.ToolExecutor;
import dev.langchain4j.agent.tool.ToolMethod;

WeatherTool weatherTool = new WeatherTool();

ToolExecutor executor = new ToolExecutor(weatherTool);

// 获取工具方法
List<ToolMethod> methods = ToolSpecifications.from(weatherTool);
```

### 自定义工具执行器

```java
public class CustomToolExecutor implements ToolExecutor {

    private final Map<String, Object> tools;

    public CustomToolExecutor(Map<String, Object> tools) {
        this.tools = tools;
    }

    @Override
    public String execute(String toolName, String arguments) {
        Object tool = tools.get(toolName);
        if (tool == null) {
            throw new IllegalArgumentException("工具不存在: " + toolName);
        }

        try {
            Method method = findMethod(tool.getClass(), toolName);
            Object result = method.invoke(tool, parseArguments(arguments));
            return objectToJson(result);
        } catch (Exception e) {
            return "错误: " + e.getMessage();
        }
    }
}
```

## 与 LLM 集成

### OpenAI 工具调用

```java
import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.agent.tool.ToolSpecification;

List<ToolSpecification> toolSpecifications = List.of(
    ToolSpecification.builder()
        .name("get_weather")
        .description("获取指定城市的天气信息")
        .addParameterProperty("city", Type.STRING, "城市名称")
        .build(),
    ToolSpecification.builder()
        .name("calculate")
        .description("执行数学计算")
        .addParameterProperty("expression", Type.STRING, "数学表达式")
        .build()
);

ChatLanguageModel model = OpenAiChatModel.builder()
        .apiKey("your-api-key")
        .toolSpecifications(toolSpecifications)
        .build();
```

### 完整的工具调用流程

```java
public class ToolCallingAssistant {

    private final ChatLanguageModel model;
    private final Map<String, ToolExecutor> tools;

    public ToolCallingAssistant(ChatLanguageModel model) {
        this.model = model;
        this.tools = new HashMap<>();
        
        // 注册工具
        tools.put("get_weather", new ToolExecutor(new WeatherService()));
        tools.put("calculate", new ToolExecutor(new CalculatorService()));
    }

    public String chat(String userMessage) {
        List<ChatMessage> messages = new ArrayList<>();
        messages.add(UserMessage.from(userMessage));

        while (true) {
            GenerateResponse response = model.generate(messages);

            // 检查是否有工具调用
            Optional<ToolExecutionRequest> toolRequest = 
                response.toolExecutionRequests().stream().findFirst();

            if (toolRequest.isEmpty()) {
                // 没有工具调用，返回 AI 回复
                return response.content().text();
            }

            // 执行工具调用
            ToolExecutionRequest request = toolRequest.get();
            String toolResult = executeTool(request);

            // 添加工具执行结果到消息
            messages.add(ToolExecutionResultMessage.from(
                request.name(), 
                toolResult
            ));
        }
    }

    private String executeTool(ToolExecutionRequest request) {
        ToolExecutor executor = tools.get(request.name());
        if (executor == null) {
            return "错误: 未找到工具 '" + request.name() + "'";
        }

        return executor.execute(request.name(), request.arguments());
    }
}
```

## 实践示例

### 1. 数据库查询工具

```java
public class DatabaseTools {

    private final JdbcTemplate jdbcTemplate;

    public DatabaseTools(DataSource dataSource) {
        this.jdbcTemplate = new JdbcTemplate(dataSource);
    }

    @Tool("查询用户信息，需要提供用户 ID")
    public Map<String, Object> getUserById(
            @ToolParameters(description = "用户 ID") Long userId
    ) {
        String sql = "SELECT * FROM users WHERE id = ?";
        return jdbcTemplate.queryForMap(sql, userId);
    }

    @Tool("根据状态查询订单列表")
    public List<Map<String, Object>> getOrdersByStatus(
            @ToolParameters(description = "订单状态: PENDING, COMPLETED, CANCELLED") 
            String status
    ) {
        String sql = "SELECT * FROM orders WHERE status = ?";
        return jdbcTemplate.queryForList(sql, status);
    }

    @Tool("创建新用户，需要提供用户名和邮箱")
    public Long createUser(
            @ToolParameters(description = "用户名") String username,
            @ToolParameters(description = "邮箱地址") String email
    ) {
        String sql = "INSERT INTO users (username, email, created_at) VALUES (?, ?, NOW())";
        KeyHolder holder = new GeneratedKeyHolder();
        jdbcTemplate.update(sql, new Object[]{username, email}, holder);
        return holder.getKey().longValue();
    }
}
```

### 2. 文件操作工具

```java
import java.nio.file.*;

public class FileTools {

    @Tool("读取文件内容")
    public String readFile(
            @ToolParameters(description = "文件路径") String filePath
    ) throws IOException {
        Path path = Paths.get(filePath);
        return Files.readString(path);
    }

    @Tool("写入文件内容")
    public boolean writeFile(
            @ToolParameters(description = "文件路径") String filePath,
            @ToolParameters(description = "文件内容") String content
    ) throws IOException {
        Path path = Paths.get(filePath);
        Files.writeString(path, content);
        return true;
    }

    @Tool("列出目录中的文件")
    public List<String> listFiles(
            @ToolParameters(description = "目录路径") String dirPath
    ) throws IOException {
        try (Stream<Path> paths = Files.list(Paths.get(dirPath))) {
            return paths.map(p -> p.getFileName().toString())
                    .collect(Collectors.toList());
        }
    }

    @Tool("搜索文件")
    public List<String> searchFiles(
            @ToolParameters(description = "搜索目录") String directory,
            @ToolParameters(description = "文件名模式") String pattern
    ) throws IOException {
        Path dir = Paths.get(directory);
        String regex = pattern.replace("*", ".*").replace("?", ".");
        
        try (Stream<Path> paths = Files.walk(dir)) {
            return paths.filter(Files::isRegularFile)
                    .map(p -> p.toString())
                    .filter(s -> s.matches(regex))
                    .collect(Collectors.toList());
        }
    }
}
```

### 3. HTTP 请求工具

```java
import java.net.http.*;

public class HttpTools {

    private final HttpClient httpClient = HttpClient.newHttpClient();

    @Tool("发送 GET 请求")
    public String get(
            @ToolParameters(description = "请求 URL") String url
    ) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .GET()
                .build();

        HttpResponse<String> response = httpClient.send(request,
            HttpResponse.BodyHandlers.ofString());

        return response.body();
    }

    @Tool("发送 POST 请求")
    public String post(
            @ToolParameters(description = "请求 URL") String url,
            @ToolParameters(description = "请求体 JSON") String body
    ) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();

        HttpResponse<String> response = httpClient.send(request,
            HttpResponse.BodyHandlers.ofString());

        return response.body();
    }
}
```

## 工具调用的最佳实践

### 1. 工具描述要清晰

```java
// 不推荐 - 描述不清晰
@Tool("处理数据")
public String process(String data);

// 推荐 - 描述清晰完整
@Tool(
    description = """
        处理用户输入的数据，包括清洗、转换和验证。
        返回处理后的数据结果和任何发现的错误。
        """
)
public DataProcessResult processUserData(
    @ToolParameters(
        description = "用户输入的原始数据，JSON 格式",
        example = "{\"name\": \"张三\", \"age\": \"25\"}"
    ) String data
);
```

### 2. 错误处理

```java
@Tool("安全的数据库查询")
public QueryResult safeQuery(
        @ToolParameters(description = "SQL 查询语句") String sql
) {
    // 验证 SQL 安全性
    if (!isSafeSql(sql)) {
        return new QueryResult(false, null, "SQL 语句包含不安全内容");
    }

    try {
        var result = jdbcTemplate.queryForList(sql);
        return new QueryResult(true, result, null);
    } catch (Exception e) {
        return new QueryResult(false, null, "查询失败: " + e.getMessage());
    }
}
```

### 3. 权限控制

```java
public class SecureToolExecutor implements ToolExecutor {

    private final ToolExecutor delegate;
    private final PermissionService permissionService;

    @Override
    public String execute(String toolName, String arguments, ChatContext context) {
        String userId = context.userId();

        if (!permissionService.hasPermission(userId, toolName)) {
            return "错误: 用户没有权限执行工具 '" + toolName + "'";
        }

        return delegate.execute(toolName, arguments);
    }
}
```

## 工具调用与内存管理

```java
public class ToolCallingWithMemory {

    private final ChatLanguageModel model;
    private final ChatMemory memory;
    private final Map<String, ToolExecutor> tools;

    public String chat(String userMessage) {
        memory.add(UserMessage.from(userMessage));

        while (true) {
            List<ChatMessage> messages = new ArrayList<>(memory.messages());

            GenerateResponse response = model.generate(messages);

            Optional<ToolExecutionRequest> toolRequest = 
                response.toolExecutionRequests().stream().findFirst();

            if (toolRequest.isEmpty()) {
                String aiResponse = response.content().text();
                memory.add(AiMessage.from(aiResponse));
                return aiResponse;
            }

            // 执行工具调用
            ToolExecutionRequest request = toolRequest.get();
            String toolResult = executeTool(request);

            // 记录工具调用到内存
            memory.add(ToolExecutionResultMessage.from(request.name(), toolResult));
        }
    }
}
```

## 异步工具调用

```java
public class AsyncToolExecutor {

    private final ExecutorService executor = Executors.newCachedThreadPool();

    @Tool("异步执行耗时任务")
    public CompletableFuture<String> asyncTask(
            @ToolParameters(description = "任务描述") String taskDescription
    ) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                Thread.sleep(5000);  // 模拟耗时操作
                return "任务完成: " + taskDescription;
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return "任务被中断";
            }
        }, executor);
    }

    public String executeWithTimeout(String taskDescription, Duration timeout) {
        try {
            return asyncTask(taskDescription).get(timeout.toMillis(), 
                TimeUnit.MILLISECONDS);
        } catch (Exception e) {
            return "任务执行失败: " + e.getMessage();
        }
    }
}
```

## 下一步

- [核心概念](./Concepts/index.md) - 回顾 LangChain4j 的核心抽象
- [链式调用](./Chain/index.md) - 了解如何组合多个处理步骤
- [内存管理](./MemoryManagement/index.md) - 管理对话状态
