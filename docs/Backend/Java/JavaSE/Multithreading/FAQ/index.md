# 常见问题与最佳实践

这一篇汇总 Java 并发最高频的 10 个问题和一套工程实践，覆盖线程创建、线程池、锁、异步、上下文传递等日常场景。

## 常见问题

### 1. 创建线程用什么方式

优先实现 `Runnable` / `Callable`，批量任务交给线程池。直接 `new Thread` 只适合极少量一次性任务；每个请求一个线程的写法在高并发下会拖垮系统。

### 2. 线程池核心参数怎么定

- CPU 密集型：核心线程数 ≈ CPU 核数 + 1。
- IO 密集型：核心线程数 ≈ CPU 核数 × 2（或按等待比估算，如 `CPU核数 / (1 - 阻塞系数)`）。
- 队列必须有界，并配置拒绝策略；先压测再调整。

### 3. 为什么不推荐 Executors 快捷方法

`newFixedThreadPool` 默认无界队列、`newCachedThreadPool` 最大线程数无上限，任务积压或瞬间洪峰时可能 OOM 或耗尽线程。生产环境手动 `new ThreadPoolExecutor`。

### 4. volatile 和 synchronized 怎么选

只需要“一个线程写、其他线程读”的标志位用 volatile；涉及复合操作（`count++`、先查后写）必须 synchronized、Lock 或原子类。

### 5. count++ 为什么线程不安全

`count++` 是“读-改-写”三步，不是原子操作。两个线程可能同时读到同一个旧值再写回，导致丢更新。用 `AtomicInteger`、`LongAdder` 或加锁。

### 6. 怎么排查死锁

1. 现象：程序卡住、CPU 不高、日志停在某处。
2. 执行 `jps` 找进程 PID，`jstack <pid>` 看线程 dump。
3. 搜索 `Found one Java-level deadlock`，按提示定位两个线程各持有对方需要的锁。
4. 修复：统一锁顺序、缩小锁范围、用 `tryLock` 超时。

### 7. 线程中断怎么协作

`interrupt()` 只是设置中断标记，目标线程要主动检查 `isInterrupted()` 或捕获 `InterruptedException` 退出。捕获中断异常后应重新设置中断标记，让上层感知。

### 8. ThreadLocal 为什么会内存泄漏

线程池线程复用，ThreadLocalMap 的 value 被强引用且不自动清理。用完必须 `remove()`；跨线程池传递上下文用 TransmittableThreadLocal。

### 9. wait 和 sleep 有什么区别

| 维度 | wait | sleep |
| --- | --- | --- |
| 释放锁 | 释放 | 不释放 |
| 必须持有锁 | synchronized 内 | 不需要 |
| 唤醒 | notify/notifyAll | 时间到或中断 |
| 属于 | Object | Thread |

### 10. CompletableFuture 和 Future 有什么区别

Future 只能阻塞 `get()`；CompletableFuture 支持链式编排（thenApply、thenCombine、allOf）、异常处理和超时控制，是现代 Java 异步编程的主流。

## 最佳实践清单

::: tip 可直接落地的清单
1. 线程池统一由管理类创建，禁止散落 `new ThreadPoolExecutor`。
2. 自定义 ThreadFactory 给线程命名（如 `biz-pool-1`），故障排查事半功倍。
3. 锁必须 `try/finally` 释放；synchronized 优先于裸用 ReentrantLock。
4. 共享可变数据优先考虑不可变对象、并发集合和原子类。
5. ThreadLocal 用完即 `remove()`，最好用 try/finally。
6. 异步编排显式传业务线程池，避免占用 commonPool。
7. 高并发计数用 `LongAdder`，读多写少用 `CopyOnWriteArrayList`，Map 用 `ConcurrentHashMap`。
8. 定时任务用 `ScheduledExecutorService`，不要用 `Timer`（单线程、异常即终止）。
9. 上线前用压测验证线程池参数，并接入线程数、队列积压监控。
10. 学习阶段用 `jstack` / `jconsole` / `async-profiler` 验证并发行为，不要只背结论。
:::

## 验证方式

1. 用 `jps` + `jstack` 对死锁示例做一次完整排查。
2. 用 `jconsole` 观察线程池线程数与队列积压。
3. 用 `ThreadPoolExecutor` 压测 1000 个任务，观察拒绝策略触发与任务耗时。

## 相关专题

- [消息队列专题](../../../../../Backend/MessageQueue/index.md)：线程池与 MQ 消费端并发模型、积压与幂等的配合
- [Spring Boot 异步任务](../../../../../Backend/Java/Frame/SpringBoot/Common/FAQ/index.md)：`@Async` 线程池配置与消息驱动消费

## 参考资料

- Oracle 并发教程：https://docs.oracle.com/javase/tutorial/essential/concurrency/
- java.util.concurrent 包文档：https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/package-summary.html
- 《Java 并发编程的艺术》（书籍）
- 《阿里巴巴 Java 开发手册》：https://github.com/alibaba/p3c
