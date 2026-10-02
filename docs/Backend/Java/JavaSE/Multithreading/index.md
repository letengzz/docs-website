# Java 并发

Java 并发是编写多线程程序的基础能力，覆盖线程创建、同步、线程池、异步编排与线程安全等核心主题，是后端高并发开发的必修内容。

- [线程基础](ThreadBasic/index.md)
- [线程池](ThreadPool/index.md)
- [synchronized 与 Lock](SynchronizedLock/index.md)
- [volatile 与内存可见性](Volatile/index.md)
- [并发工具类](ConcurrentUtils/index.md)
- [CompletableFuture 异步编排](CompletableFuture/index.md)
- [ThreadLocal 详解](ThreadLocal/index.md)
- [常见问题与最佳实践](FAQ/index.md)

## 相关专题

- [高性能 Java](../../../HighPerformanceJava/index.md)：同一批并发原语在**不同竞争强度下的吞吐与延迟差异**——三级锁状态、`AtomicLong` 与 `LongAdder` 的选型分界、`StampedLock` 乐观读、伪共享与锁粒度。本专题讲**怎么用对**（内存语义、可见性、正确性），那里讲**为什么快、慢在哪**；`synchronized` 的锁状态表在两页都出现，本页看语义、那边看开销
