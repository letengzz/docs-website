# JVM 基础

JVM（Java Virtual Machine）是 Java 跨平台与自动内存管理的基石。本专题从内存结构、类加载、GC 到调优与故障排查，建立完整的 JVM 认知体系。

- [内存结构](MemoryStructure/index.md)
- [对象创建与内存布局](ObjectLayout/index.md)
- [类加载机制](ClassLoading/index.md)
- [GC 算法](GcAlgorithm/index.md)
- [垃圾收集器](GcCollector/index.md)
- [JVM 调优参数](Tuning/index.md)
- [故障排查](Troubleshoot/index.md)
- [常见问题与最佳实践](FAQ/index.md)

## 相关专题

- [高性能 Java](../../../HighPerformanceJava/index.md)：回答「**慢在哪儿、怎么改、怎么证明改好了**」——指标口径、JMH 基准测试、JIT 与去优化、对象布局与分配、锁开销、火焰图与生产采样纪律。本专题讲**运行时是什么**（内存结构、GC 算法与收集器、参数与故障），那里讲**怎么测量与优化**；两边的「对象布局」页分工是：本页看结构，那边看它怎么影响占用与缓存
