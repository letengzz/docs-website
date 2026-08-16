# 常见问题与最佳实践

这一篇汇总 JVM 面试与实战最高频的 10 个问题和一套工程实践，覆盖内存、GC、类加载、调优与排查。

## 常见问题

### 1. 堆和栈有什么区别

| 维度 | 堆 | 虚拟机栈 |
| --- | --- | --- |
| 线程 | 共享 | 私有 |
| 内容 | 对象实例、数组 | 栈帧（局部变量、操作数栈） |
| 生命周期 | 随 GC 回收 | 方法调用结束即弹出 |
| 异常 | `OutOfMemoryError` | `StackOverflowError` |

### 2. 什么是 OOM，怎么处理

OOM 是 JVM 无法分配内存时抛出的 `OutOfMemoryError`。处理顺序：保留现场（HeapDump）→ 看异常类型（heap/metaspace/thread/direct）→ 分析转储或系统资源 → 修复并回归。

### 3. 对象一定分配在堆上吗

不一定。开启逃逸分析后，不逃逸的小对象可能被**标量替换**，直接在栈上分配，减少 GC 压力。

### 4. 什么是 GC Roots

可达性分析的起点：栈帧局部变量、静态变量、常量引用、JNI 引用、活跃线程等。从这些根出发不可达的对象会被回收。

### 5. 什么是双亲委派，为什么要打破

加载类时先委托父加载器，避免重复加载并保护核心类。SPI（JDBC）、Web 容器（Tomcat）、热部署场景需要打破，实现方式是自定义类加载器或线程上下文类加载器。

### 6. G1、ZGC、Shenandoah 怎么选

默认选 G1；超大堆且对延迟极其敏感选 ZGC；发行版支持且低延迟场景可选 Shenandoah。选择后必须压测验证。

### 7. 堆大小怎么设置

先估活跃数据量（full dump 或 GC 日志），`-Xms` 与 `-Xmx` 设为相同；再观察老年代水位，一般保留 1.5~2 倍余量。不要盲目 8G、16G。

### 8. Full GC 频繁怎么办

按顺序排查：`jstat` 看老年代水位 → dump 找大对象/泄漏 → 检查 `-Xmx` 是否过小 → 检查是否有大对象直接进老年代 → 修复后回归。

### 9. 类加载失败和初始化失败怎么区分

`ClassNotFoundException` 是“找不到”，检查依赖与 classpath；`NoClassDefFoundError` 常常是“加载到了但初始化失败”（静态块抛异常）或类加载后被卸载。

### 10. 元空间 OOM 是什么原因

元空间存类元信息。常见原因：动态代理/反射生成类过多、自定义类加载器泄漏（热部署）、`MaxMetaspaceSize` 设置过小。用 `jstat -class` 或 `jcmd VM.metaspace` 观察类加载数量。

## 最佳实践清单

::: tip 可直接落地的清单
1. 生产启动参数统一模板：`-Xms=-Xmx`、`-XX:MaxMetaspaceSize`、`-XX:+HeapDumpOnOutOfMemoryError`、`-Xlog:gc*`。
2. 容器部署时同时约束 JVM 堆与容器内存（如 `-XX:MaxRAMPercentage`），避免堆超过容器限制。
3. 上线前做压测，记录 GC 日志、P99 延迟、堆水位三条基线。
4. 一次只改一个参数，改完必须回归对比。
5. 报警指标至少包含：Full GC 次数、FGCT、老年代占用率、OOM 事件。
6. 定期用 MAT/Arthas 检查静态集合、ThreadLocal、连接池等常见泄漏点。
7. 大对象、长字符串、无界缓存是 OOM 高发区，代码评审重点看。
8. 多环境统一 JDK 版本（如 25 LTS），避免“本地没事、线上 GC 行为不同”。
9. 学习阶段用 `jcmd`、`jstat`、`jstack` 实操，不要只背参数。
:::

## 验证方式

1. 用一套生产参数模板启动压测程序，确认 GC 日志可滚动输出、OOM 会自动 dump。
2. 用 `jcmd <pid> VM.flags` 确认生效参数与预期一致。
3. 人为制造一次 Full GC 频繁场景，按 FAQ 流程走一遍完整排查。

## 参考资料

- Oracle GC 调优指南：https://docs.oracle.com/en/java/javase/25/gctuning/
- JDK 命令手册：https://docs.oracle.com/en/java/javase/25/docs/specs/man/index.html
- 《深入理解 Java 虚拟机（第 3 版）》（书籍）
