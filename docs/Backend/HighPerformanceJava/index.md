# 高性能 Java

<p style="text-align:center;"><img src="./assets/java-logo.png" alt="Java" style="zoom:75%;" /></p>

「高性能 Java」不是背一串 JVM 参数，而是一套**可以被证伪的工程流程**：先把「慢」变成一句有数字的话，再用剖析工具定位到具体的方法或对象，只改那一处，然后回到同一个口径上验证它真的变好了。本专题的前半部分讲**怎么测**（JMH、指标口径、剖析工具链），中间讲**为什么快**（JIT、对象布局、分配、锁），最后用一次完整的实战把两者串起来。

![性能优化四层模型与决策顺序](assets/hpj-overview.svg)

## 本专题与相邻专题的分工

「JVM / Java 性能」在库内有多个落点，边界如下——**先确认你要找的是哪一层，再进对应页面**：

| 专题 | 讲什么 | 不讲什么 |
| --- | --- | --- |
| **本专题** | **怎么测量、怎么定位、怎么优化**：指标口径、JMH、JIT 行为、对象布局与分配、锁与并发原语、剖析工具链、端到端实战 | JVM 内存区域的静态结构与 GC 算法的教科书式推导 |
| [JVM 基础](../Java/JavaSE/JVM/index.md) | **运行时是什么**：内存结构、类加载、GC 算法与收集器、调优参数、故障排查 | 怎么写出可信的基准测试、怎么用火焰图定位 |
| [Java 并发](../Java/JavaSE/Multithreading/index.md) | **并发怎么用对**：线程、线程池、`synchronized`/`Lock`、`volatile`、`CompletableFuture`、`ThreadLocal` | 并发原语在不同竞争强度下的**吞吐与延迟差异** |
| [网络编程 · 性能基准与压测](../NetworkProgramming/BenchmarkPractice/index.md) | 网络层的**指标定义与压测方法**（吞吐、延迟分布、连接数） | 单进程内热代码的微基准与 JIT 行为 |
| [数据库 · 索引与性能](../../DB/Relational/MySQL/IndexPerformance/index.md) | 慢在**存储层**时怎么治（执行计划、索引失效、分页） | 慢在应用进程内部时怎么治 |
| [前端性能优化](../../Frontend/Others/PerformanceOptimization/index.md) | 加载与渲染性能（浏览器侧） | 服务端进程内的性能 |

::: tip 一条判断线
**先把「慢」拆成「等」与「算」。** 等（IO、锁、下游、GC 停顿）优先去架构与容量层解决，本专题的工具只用来看清它；算（CPU 时间花在哪些方法上）才是 JIT、数据结构、分配与锁优化的战场。用错了方向，再精细的微优化也是在优化一条不在关键路径上的代码。
:::

## 专题导航

- [性能工程全景：指标口径与优化决策](Overview/index.md)：延迟分布与吞吐的关系、四层收益模型、基线三要素、什么时候不该优化
- [JMH 基准测试](JmhBenchmark/index.md)：为什么手写循环测不出真话、四种假结果、注解体系、`@State` 与死代码消除、结果怎么读
- [JIT 与分层编译](JitCompiler/index.md)：五层编译与三条去优化路径、内联阈值、逃逸分析、预热与 AOT cache（JDK 24/25）
- [对象布局：从对象头到紧凑对象头](MemoryLayout/index.md)：Mark Word 与类指针、字段重排与对齐、JOL 怎么读、JDK 25 的 64 位紧凑头
- [分配与内存效率](AllocationOptimize/index.md)：TLAB、逃逸分析的三个出路与六种失效写法、缓存行与伪共享、集合与字符串的真实开销
- [锁与并发原语的性能](LockOptimize/index.md)：现行 JDK 的三级锁状态、`AtomicLong` 与 `LongAdder`、`ReentrantLock`/`StampedLock`、锁粒度与无锁的边界
- [剖析工具链：JFR 与 async-profiler](Profiling/index.md)：按症状选工具、火焰图怎么读、JFR 事件与 `jcmd` 速查、生产环境采样的纪律
- [实战：把慢接口的 P99 打下来](Practice/index.md)：六步闭环，从基线到五处修复与前后对照表
- [常见问题与最佳实践](FAQ/index.md)：加了缓存更慢、本地快线上慢、改完没变好等高频问题

## 版本速览（2026-10 核对）

| 组件 | 当前状态 | 说明 |
| --- | --- | --- |
| **JDK** | **JDK 25 为当前 LTS**（2025-09-16 GA，支持至 2030-09） | JDK 26（2026-03-17）为非 LTS，JDK 27（2026-09-14）也是非 LTS；非 LTS 生命周期仅约 6 个月 |
| 紧凑对象头 | `-XX:+UseCompactObjectHeaders`（JDK 25 起为产品特性） | JDK 24 为实验性（JEP 450，还需 `UnlockExperimentalVMOptions`），JDK 25 转正（JEP 519）；**仍需显式开启**，未默认启用 |
| AOT cache | `-XX:AOTCacheOutput=` / `-XX:AOTCache=`（JDK 25 一步生成） | JDK 24 引入类加载与链接（JEP 483），JDK 25 加入方法 profile（JEP 515）与命令行简化（JEP 514） |
| 偏向锁 | **已不存在**（JDK 15 默认禁用，JDK 18 参数作废） | 见 [锁与并发原语的性能](LockOptimize/index.md) |
| JMH | `1.37` | 官方微基准测试框架，Maven 坐标 `org.openjdk.jmh:jmh-core` |
| JOL | Maven Central 上 `0.17`；仓库主线已到 `0.18-SNAPSHOT` | 0.18-SNAPSHOT 在 2026-01 加入 JDK 25 兼容修复；**用 0.17 读带紧凑对象头的布局会读错** |
| async-profiler | `4.5`（2026-07-13） | 4.x 主线；4.3 起支持原生锁剖析、延迟过滤与 Prometheus 指标导出；要求 JDK 11+ |
| k6（压测侧） | 2.x | 见 [工具 · 测试工具](../../Tools/TestingTools/index.md) |

::: warning 版本以官方发布页为准
上表是写作时（2026-10-02）的核对结果，不要照抄。核对当前 JDK 用 `java -version` 与 `java --list-modules`；核对 JMH / JOL 用 Maven Central 的版本页；核对 async-profiler 用其 GitHub Releases。**凡是「某参数在某个版本被移除」的说法，都要用 `-XX:+PrintFlagsFinal -version` 在目标 JDK 上现场确认。**
:::

::: danger 三条最容易踩的过期结论
1. **「synchronized 有四级锁升级，偏向锁最快」**：偏向锁自 JDK 15 默认关闭、JDK 18 参数作废；现行 JDK 是**无锁 → 轻量级锁 → 重量级锁**三级。
2. **「Graal JIT 比 C2 快，可以换上去」**：可选的实验性 Graal JIT 编译器**在 JDK 25 已被移除**；Graal 现在的可见形态是 GraalVM 的 native-image（AOT 编译），不是替换 JIT。
3. **「微基准用 `System.nanoTime()` 包个 for 循环就行」**：那样测出来的数字与真实性能可以差到几十倍，甚至量到的是「空循环」——见 [JMH 基准测试](JmhBenchmark/index.md)。
:::

## 学习路径建议

1. **只有现象没有数据** → 先读 [性能工程全景](Overview/index.md)，把指标口径定下来（P99 而不是均值），并确认自己的问题属于「等」还是「算」。
2. **要对比两种写法谁快** → 直接读 [JMH 基准测试](JmhBenchmark/index.md)，并接受一个前提：微基准只能回答「热代码在稳态下的差异」，回答不了端到端。
3. **线上毛刺、P99 抖动** → [剖析工具链](Profiling/index.md) → 若是 GC 侧结论则转 [JVM · 垃圾收集器](../Java/JavaSE/JVM/GcCollector/index.md)。
4. **要减少内存占用或对象数量** → [对象布局](MemoryLayout/index.md) → [分配与内存效率](AllocationOptimize/index.md)。
5. **并发下吞吐上不去** → [锁与并发原语的性能](LockOptimize/index.md)，先分清是「锁竞争」还是「缓存行乒乓」。
6. **想走一遍完整流程** → [实战](Practice/index.md)，那里有从基线到回归的每一步产物。

## 相关专题

- [JVM 基础](../Java/JavaSE/JVM/index.md)：运行时结构、GC 算法与收集器、调优参数与故障排查
- [Java 并发](../Java/JavaSE/Multithreading/index.md)：并发原语的正确用法（本专题只谈它的性能面）
- [Java 集合框架](../Java/JavaSE/Collection/index.md)：集合的复杂度与扩容行为
- [Java 函数式编程](../Java/JavaSE/FunctionalProgramming/index.md)：`Stream` 与 `Optional` 的开销来源
- [网络编程](../NetworkProgramming/index.md)：服务端 IO 模型与压测方法
- [工具 · 测试工具](../../Tools/TestingTools/index.md)：k6 / JMeter / Selenium 等工具的使用方式
- [CI/CD · 自动化测试与质量门禁](../../Tools/CICD/Testing/index.md)：把性能门禁接进流水线的位置

## 参考资料

- JMH（官方仓库，含样例）：https://github.com/openjdk/jmh
- JMH 样例集（官方，必读）：https://github.com/openjdk/jmh/tree/master/jmh-samples/src/main/java/org/openjdk/jmh/samples
- JOL：Java Object Layout（官方仓库）：https://github.com/openjdk/jol
- async-profiler（官方仓库与文档）：https://github.com/async-profiler/async-profiler
- JDK 25 重要变更（Oracle 官方迁移指南）：https://docs.oracle.com/en/java/javase/25/migrate/
- JEP 519: Compact Object Headers：https://openjdk.org/jeps/519
- JEP 515: Ahead-of-Time Method Profiling：https://openjdk.org/jeps/515
- JEP 374: Deprecate and Disable Biased Locking：https://openjdk.org/jeps/374
- JDK Flight Recorder（官方文档）：https://docs.oracle.com/en/java/javase/25/jfapi/
