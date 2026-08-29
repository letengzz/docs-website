# 常见问题与最佳实践

汇总 Java IO/NIO 开发中最常遇到的疑问与坑，按主题分类，方便快速查阅。

## 选型类

### 字节流、字符流、NIO 到底怎么选？

| 场景 | 推荐方案 |
| --- | --- |
| 小文本文件 | `Files.readString` / `writeString`（UTF-8） |
| 大文本逐行处理 | `Files.newBufferedReader` + `readLine` |
| 二进制文件（图片/压缩包） | `Files.newInputStream` + 8KB 缓冲循环 |
| 文件复制 | `Files.copy` 或 `FileChannel.transferTo` |
| 对象持久化 | 优先 JSON（Jackson/Gson），少用原生序列化 |
| 高并发网络服务 | Netty（NIO + Reactor） |
| 目录监听 | `WatchService` |

### 为什么 NIO 比传统 IO 快？

不是所有场景都快。NIO 的优势在于：

1. **非阻塞 + 多路复用**：一个线程管大量连接，省线程资源；
2. **零拷贝**：`transferTo` 减少用户态/内核态拷贝；
3. **直接缓冲区**：堆外内存减少一次拷贝。

但小文件、短连接场景下，NIO 的代码复杂度和 Buffer 管理开销可能不如传统 IO，**选型看场景，不迷信框架**。

### Java 21 虚拟线程出现后还要 NIO 吗？

虚拟线程（Virtual Threads）让「一请求一线程」的阻塞模型变得廉价，**BIO 风格代码可以重获新生**。但 NIO/Netty 的价值仍在：

- 虚拟线程不能减少**内核级系统调用次数**，大量并发下 NIO 的批量事件分发仍有优势；
- 现有 Netty 生态（网关、IM）不会立刻迁移；
- 虚拟线程适合 IO 密集业务代码，NIO 适合框架层。

## 性能类

### 为什么 `read()` 逐字节读那么慢？

每次 `read()` 都是一次系统调用，百万次调用开销巨大。批量读取（`read(byte[], off, len)`）或缓冲流把系统调用减少几个数量级。

```java
// 慢：逐字节
int data;
while ((data = is.read()) != -1) { ... }

// 快：批量 + 缓冲
byte[] buffer = new byte[8192];
int len;
while ((len = is.read(buffer)) != -1) { ... }
```

### `Files.readAllBytes` 会 OOM 吗？

会。文件远大于堆内存或单次分配过大时 OOM。**大文件必须流式处理**：

```java
// FAQ/LargeFileSafe.java
import java.io.BufferedReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

public class LargeFileSafe {
    public static void main(String[] args) throws Exception {
        // 逐行统计，内存稳定
        long lines = 0;
        try (BufferedReader reader = Files.newBufferedReader(
                Path.of("huge.log"), StandardCharsets.UTF_8)) {
            while (reader.readLine() != null) lines++;
        }
        System.out.println("总行数：" + lines);
    }
}
```

### 缓冲区设多大合适？

经验值：8KB～64KB。太小系统调用多，太大收益递减。网络读写还要考虑 MTU 与对端能力，Netty 默认 16KB～64KB 的池化缓冲区是合理参照。

## 编码类

### 中文乱码怎么排查？

排查三步：

1. 确认文件真实编码（`xxd` 看字节，或 VS Code 右下角编码提示）；
2. 确认读写代码显式指定同一 `Charset`（UTF-8）；
3. 确认传输链路每一跳（读 → 处理 → 写）都没有默认编码兜底。

```java
// 统一用 UTF-8
Files.readString(path, StandardCharsets.UTF_8);
Files.newBufferedReader(path, StandardCharsets.UTF_8);
```

### `FileReader` 为什么不可靠？

`FileReader` 使用平台默认编码：Windows 常见 GBK，Linux 是 UTF-8，同一代码在两个平台行为不同。显式指定编码可消除不确定性。

## 资源类

### 流不关闭有什么后果？

文件句柄、Socket 连接泄漏，最终 `Too many open files` 崩溃。**一律 try-with-resources**，自动调用 `close()`：

```java
try (BufferedReader reader = Files.newBufferedReader(path, StandardCharsets.UTF_8)) {
    // ...
}   // 自动关闭
```

::: danger 两个容易漏关的对象
1. `Files.list` / `Files.walk` 返回的 `Stream` 必须关闭（try-with-resources）；
2. 手动 `new Socket` / `new FileInputStream` 的裸对象要显式关闭。
:::

### `flush()` 与 `close()` 的区别？

- `flush()`：把缓冲区的数据强制写出，流仍可继续使用；
- `close()`：先 flush 再释放资源，流不可再用。

需要「写入立即可见」（如网络响应、日志）时手动 `flush()`；结束时只调用 `close()` 即可。

## 序列化类

### 反序列化报 `InvalidClassException` 怎么办？

类结构变化导致 `serialVersionUID` 不匹配。显式声明固定 UID，并保证新旧版本的字段兼容（新增字段给默认值、删除字段保留 `serialVersionUID`）。

### Java 原生序列化还有什么坑？

1. **安全**：反序列化不可信数据可能 RCE（如 Fastjson/原生序列化历史漏洞）；
2. **性能**：比 JSON 慢且体积大；
3. **兼容**：跨语言无法使用。

现代方案：JSON（Jackson/Gson）或二进制序列化（Protobuf、Kryo）。

## 网络 IO 类

### 什么是粘包/半包？怎么解决？

TCP 是字节流，没有消息边界：

- **粘包**：多条消息粘在一起到达；
- **半包**：一条消息被拆成多次到达。

解决方案：

| 方案 | 说明 |
| --- | --- |
| 固定长度 | 每条消息定长，不足补位，浪费空间 |
| 分隔符 | 用 `\n` 或特殊标记，消息内不能出现该字符 |
| 长度前缀 | 4 字节长度 + 内容（最常用，Netty `LengthFieldBasedFrameDecoder`） |

```java
// 长度前缀解码示意
// 先读 4 字节长度 n，再读 n 字节内容，循环直至完整
```

### NIO 为什么必须 `configureBlocking(false)`？

阻塞通道无法注册 Selector（抛 `IllegalBlockingModeException`），因为阻塞语义下线程会卡在读写上，Selector 无从调度。非阻塞是「多路复用」的前提。

### 生产环境为什么不直接手写 NIO？

手写 NIO 要处理：半包粘包、Buffer 扩容、异常恢复、连接生命周期、空闲检测、流量控制……全部是细节坑。Netty 把这些沉淀为成熟框架，**除非学习目的，否则直接上 Netty**。

## 最佳实践清单

::: tip 写 IO 代码前的检查清单
1. 是否显式指定了 `Charset`（UTF-8）？
2. 是否用 try-with-resources 管理所有流/通道？
3. 大文件是否流式处理（没有 `readAllBytes`）？
4. 缓冲区是否合理（8KB～64KB）？
5. 网络消息是否有边界协议（长度前缀/分隔符）？
6. 是否做了目录穿越、不可信数据校验？
7. 性能关键路径是否用了 `transferTo` / 缓冲流 / 直接缓冲区？
:::

## 参考资料

- [Oracle Java 教程：IO 与 NIO](https://docs.oracle.com/javase/tutorial/essential/io/index.html)
- [Netty 官方文档](https://netty.io/)
- [Java 25 发行说明](https://www.oracle.com/java/technologies/javase/25-relnote-issues.html)
