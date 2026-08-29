# 实战：Netty 聊天服务器

本实战用 Netty 实现一个完整的**群聊服务器**：客户端连接、登录、广播消息、上下线通知，并用自定义协议 + 粘包拆包解码器保证消息边界。按步骤做完，你就掌握了 Netty 服务端的完整套路。

![Netty 核心架构](../assets/netty-arch.svg)

## 功能需求

```text
1. 客户端连接后发送【登录：昵称】
2. 服务器广播：xxx 上线 / xxx 下线
3. 客户端发送聊天消息，广播给所有在线用户
4. 支持心跳，超时自动断开
```

## 协议设计

```text
魔数(4B) + 版本(1B) + 类型(1B) + 长度(4B) + 消息体(N)
类型：1=登录，2=聊天，3=心跳，4=下线
```

## 第一步：消息类

```java [ChatMessage.java]
public class ChatMessage {
    private byte type;          // 1 登录 2 聊天 3 心跳 4 下线
    private String from;        // 昵称
    private String content;     // 内容

    public ChatMessage(byte type, String from, String content) {
        this.type = type;
        this.from = from;
        this.content = content;
    }
    // getter / setter...
}
```

## 第二步：编解码器（复用协议设计）

```java [ChatCodec.java]
public class ChatCodec {
    public static final int MAGIC = 0x12345678;
    public static final int HEADER_LEN = 10;
}
```

### 编码器

```java [ChatEncoder.java]
public class ChatEncoder extends MessageToByteEncoder<ChatMessage> {
    @Override
    protected void encode(ChannelHandlerContext ctx, ChatMessage msg, ByteBuf out) {
        byte[] name = msg.getFrom().getBytes(StandardCharsets.UTF_8);
        byte[] content = msg.getContent().getBytes(StandardCharsets.UTF_8);
        out.writeInt(ChatCodec.MAGIC);
        out.writeByte(1);                       // 版本
        out.writeByte(msg.getType());
        out.writeInt(4 + name.length + 4 + content.length);
        out.writeInt(name.length);
        out.writeBytes(name);
        out.writeInt(content.length);
        out.writeBytes(content);
    }
}
```

### 解码器

```java [ChatDecoder.java]
public class ChatDecoder extends ByteToMessageDecoder {
    @Override
    protected void decode(ChannelHandlerContext ctx, ByteBuf in, List<Object> out) {
        if (in.readableBytes() < ChatCodec.HEADER_LEN) return;
        in.markReaderIndex();
        int magic = in.readInt();
        if (magic != ChatCodec.MAGIC) { ctx.close(); return; }
        in.readByte();                          // 版本
        byte type = in.readByte();
        int total = in.readInt();
        if (in.readableBytes() < total) {       // 数据未到齐
            in.resetReaderIndex();
            return;
        }
        int nameLen = in.readInt();
        byte[] name = new byte[nameLen];
        in.readBytes(name);
        int contentLen = in.readInt();
        byte[] content = new byte[contentLen];
        in.readBytes(content);
        out.add(new ChatMessage(type,
            new String(name, StandardCharsets.UTF_8),
            new String(content, StandardCharsets.UTF_8)));
    }
}
```

## 第三步：服务端

```java [ChatServer.java]
public class ChatServer {
    // 在线用户：channel → 昵称
    private static final ConcurrentHashMap<Channel, String> USERS = new ConcurrentHashMap<>();

    public static void main(String[] args) throws Exception {
        EventLoopGroup boss = new NioEventLoopGroup(1);
        EventLoopGroup worker = new NioEventLoopGroup();
        try {
            ServerBootstrap b = new ServerBootstrap();
            b.group(boss, worker)
                .channel(NioServerSocketChannel.class)
                .childHandler(new ChannelInitializer<SocketChannel>() {
                    @Override
                    protected void initChannel(SocketChannel ch) {
                        ch.pipeline()
                            .addLast(new LengthFieldBasedFrameDecoder(8192, 7, 4, 0, 0))
                            .addLast(new ChatDecoder())
                            .addLast(new ChatEncoder())
                            .addLast(new ChatHandler());
                    }
                });
            b.bind(9090).sync();
            System.out.println("chat server on 9090");
            b.channel().closeFuture().sync();
        } finally {
            boss.shutdownGracefully();
            worker.shutdownGracefully();
        }
    }

    static void broadcast(ChatMessage msg) {
        USERS.keySet().forEach(ch -> ch.writeAndFlush(msg));
    }

    static void join(Channel ch, String name) {
        USERS.put(ch, name);
        broadcast(new ChatMessage((byte) 2, "系统", name + " 上线了"));
    }

    static void leave(Channel ch) {
        String name = USERS.remove(ch);
        if (name != null) {
            broadcast(new ChatMessage((byte) 2, "系统", name + " 下线了"));
        }
    }
}
```

## 第四步：业务 Handler

```java [ChatHandler.java]
public class ChatHandler extends SimpleChannelInboundHandler<ChatMessage> {
    @Override
    protected void channelRead0(ChannelHandlerContext ctx, ChatMessage msg) {
        switch (msg.getType()) {
            case 1 -> ChatServer.join(ctx.channel(), msg.getFrom());
            case 2 -> ChatServer.broadcast(msg);
            case 3 -> ctx.writeAndFlush(new ChatMessage((byte) 3, "心跳", "pong"));
            case 4 -> ctx.close();
            default -> ctx.close();
        }
    }

    @Override
    public void channelInactive(ChannelHandlerContext ctx) {
        ChatServer.leave(ctx.channel());
    }

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
        cause.printStackTrace();
        ctx.close();
    }
}
```

## 第五步：客户端

```java [ChatClient.java]
public class ChatClient {
    public static void main(String[] args) throws Exception {
        EventLoopGroup group = new NioEventLoopGroup();
        try {
            Bootstrap b = new Bootstrap();
            b.group(group)
                .channel(NioSocketChannel.class)
                .handler(new ChannelInitializer<SocketChannel>() {
                    @Override
                    protected void initChannel(SocketChannel ch) {
                        ch.pipeline()
                            .addLast(new LengthFieldBasedFrameDecoder(8192, 7, 4, 0, 0))
                            .addLast(new ChatDecoder())
                            .addLast(new ChatEncoder())
                            .addLast(new SimpleChannelInboundHandler<ChatMessage>() {
                                @Override
                                protected void channelRead0(ChannelHandlerContext c, ChatMessage m) {
                                    System.out.println(m.getFrom() + ": " + m.getContent());
                                }
                            });
                    }
                });
            Channel ch = b.connect("localhost", 9090).sync().channel();

            // 登录
            ch.writeAndFlush(new ChatMessage((byte) 1, args[0], "login"));
            // 读键盘输入发消息
            BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
            String line;
            while ((line = reader.readLine()) != null) {
                ch.writeAndFlush(new ChatMessage((byte) 2, args[0], line));
            }
        } finally {
            group.shutdownGracefully();
        }
    }
}
```

## 验证流程

```shell
# 启动两个客户端
java ChatClient 张三
java ChatClient 李四

# 张三发消息
大家好
# 张三窗口显示：李四 上线了 / 系统: 李四 上线了
# 两个窗口都显示：张三: 大家好
# 关闭李四，张三窗口显示：系统: 李四 下线了
```

## 进阶收尾

1. **心跳超时**：用 `IdleStateHandler` 读空闲 30s 触发断连。
2. **私聊**：消息体加目标昵称，服务器按 channel 定向发送。
3. **鉴权**：登录消息校验 Token。
4. **业务线程池**：消息落库等耗时操作放独立线程池。
5. **扩展 WebSocket**：`WebSocketServerProtocolHandler` 与浏览器互通。

## 易错点与最佳实践

::: danger 实战易错
1. **编解码器位置顺序**：拆帧解码器 → 业务解码器 → 业务 Handler；编码器在出站侧。
2. **LengthField 参数**：长度字段偏移/长度不匹配，粘包拆包失效；对照协议字段精确配置。
3. **广播写慢客户端**：写入慢的连接会积压内存；设置水位或剔除。
4. **并发修改 USERS**：用 ConcurrentHashMap 并只在 EventLoop 线程操作 channel。
5. **登录未鉴权就加入**：先校验身份再入群。
:::

::: tip 最佳实践
1. 一个连接一个 Channel，同一个连接的处理都在一个 EventLoop，天然线程安全。
2. 广播操作注意背压：`isWritable()` 判断再写。
3. 协议先文档后编码，编解码器单元测试覆盖粘包拆包。
4. 压测后调 EventLoop 数量与业务线程池大小。
:::

## 参考资料

- 本专题章节：[Netty 入门](../Netty/index.md)、[粘包拆包与编解码](../StickyHalf/index.md)
- Netty 示例源码：https://github.com/netty/netty/tree/4.1/example
- Netty 官方文档：https://netty.io/wiki/
