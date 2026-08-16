# 垃圾收集器

垃圾收集器是 GC 算法的落地实现。从 Serial 到 G1、ZGC、Shenandoah，选择的核心权衡是：**吞吐量、停顿时间、内存占用**。

::: info 版本现状（2026-08 核对）
JDK 25 中 **G1 仍是默认收集器**；CMS 已在 JDK 14 移除；ZGC 从 JDK 23 起默认使用**分代模式**；Shenandoah 同样支持分代模式。
:::

## 收集器家族

```text
新生代：Serial、ParNew、Parallel Scavenge
老年代：Serial Old、Parallel Old、CMS（JDK 14 已移除）
整堆：G1（JDK 9+ 默认）、ZGC、Shenandoah、Epsilon
```

## 经典收集器

| 收集器 | 区域 | 特点 | 状态 |
| --- | --- | --- | --- |
| Serial | 新生代 | 单线程，Stop-The-World（STW） | 客户端、小内存 |
| Serial Old | 老年代 | 单线程标记-整理 | 备用组合 |
| ParNew | 新生代 | Serial 多线程版 | 曾配合 CMS |
| Parallel Scavenge | 新生代 | 多线程，关注吞吐量 | JDK 8 默认新生代 |
| Parallel Old | 老年代 | 多线程标记-整理 | JDK 8 默认老年代 |
| CMS | 老年代 | 并发标记清除，低停顿 | **JDK 14 已移除** |

## G1：JDK 9+ 默认收集器

G1（Garbage First）把堆划分为大小相等的 **Region**，跟踪每个 Region 的垃圾比例，优先回收垃圾最多的 Region：

```text
堆 → 多个 Region（1MB~32MB）
  → Young Region / Old Region / Humongous（大对象）
  → 并发标记 + 混合回收（Mixed GC）
  → 可预测停顿：-XX:MaxGCPauseMillis（默认 200ms）
```

优点：可控停顿、支持大堆、适合 Web/微服务。缺点：内存占用比 Parallel 高一些，小堆优势不明显。

```shell
java -XX:+UseG1GC -XX:MaxGCPauseMillis=100 -jar app.jar
```

## ZGC：亚毫秒停顿

ZGC 的目标是**停顿时间不随堆大小增长**（JDK 11 实验、JDK 15 生产，JDK 23+ 默认分代模式）：

- 使用染色指针（Colored Pointers）与读屏障，多数阶段并发执行。
- 适合超大堆（几十 GB~TB）、低延迟场景。
- 代价：CPU 占用较高、内存布局更复杂。

```shell
java -XX:+UseZGC -Xmx64g -jar app.jar
```

## Shenandoah：并发整理

Shenandoah（JDK 12+，Oracle JDK 15 起包含）同样是低停顿收集器，通过**并发移动对象**避免 STW 整理阶段，适合对停顿敏感且内存充足的服务。

```shell
java -XX:+UseShenandoahGC -jar app.jar
```

## 如何选择

| 场景 | 推荐 |
| --- | --- |
| 默认（大多数 Web/微服务） | G1 |
| 吞吐优先、内存较小 | Parallel（JDK 8 风格） |
| 超大堆、低延迟 | ZGC |
| 低延迟且使用 Shenandoah 发行版 | Shenandoah |
| 学习/诊断（不做回收） | Epsilon |

## 关键概念

| 概念 | 含义 |
| --- | --- |
| Stop-The-World（STW） | 暂停所有用户线程 |
| 并发（Concurrent） | 与用户线程并行执行 |
| 并行（Parallel） | 多条 GC 线程协作 |
| 吞吐量 | 用户代码运行时间 / 总时间 |
| 停顿时间 | GC 造成的应用暂停 |

## 查看当前使用的收集器

```shell
java -XX:+PrintCommandLineFlags -version
jcmd <pid> VM.flags | findstr GC
```

输出示例：

```text
-XX:InitialHeapSize=...
-XX:MaxHeapSize=...
-XX:+UseCompressedOops
-XX:+UseG1GC
```

## 易错点

::: danger 常见错误
1. 仍在配置 CMS：JDK 14 起已被移除，`-XX:+UseConcMarkSweepGC` 会启动失败，改用 G1 或 ZGC。
2. 盲目追求“低停顿”上 ZGC：它换取了更高 CPU 和内存开销，小堆场景收益不明显。
3. 只调收集器不调堆大小：收集器与堆配置是配合关系，先定堆再选收集器。
4. 认为 G1 停顿目标一定达到：`MaxGCPauseMillis` 是目标不是承诺，垃圾产生太快时仍会超时。
5. 生产环境直接用默认参数不监控：先跑压测看 GC 日志，再决定是否换收集器。
:::

## 验证方式

1. 用 `-XX:+PrintCommandLineFlags -version` 查看当前默认收集器（JDK 9+ 应为 G1）。
2. 分别用 G1、ZGC 启动同一压测程序，对比 `-Xlog:gc` 的停顿时间与吞吐。
3. 用 `jstat -gcutil <pid>` 观察各收集器下的堆占用曲线。

## 参考资料

- JEP 248（G1）：https://openjdk.org/jeps/248
- JEP 333（ZGC）：https://openjdk.org/jeps/333
- JEP 189（Shenandoah）：https://openjdk.org/jeps/189
- Oracle GC 调优指南：https://docs.oracle.com/en/java/javase/25/gctuning/
