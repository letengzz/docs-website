# 线程池

线程池（Thread Pool）是“复用线程、控制并发量”的线程管理机制。它避免频繁创建销毁线程，是高并发应用的标准做法。核心实现是 **ThreadPoolExecutor**。

## Executor 框架

```text
Executor（执行器）
├── ExecutorService    可提交任务、返回 Future、关闭
└── ScheduledExecutorService  延迟/周期执行
```

```java [Multithreading/ThreadPool/ExecutorDemo.java]
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class ExecutorDemo {
    public static void main(String[] args) throws InterruptedException {
        ExecutorService pool = Executors.newFixedThreadPool(3);
        for (int i = 1; i <= 5; i++) {
            int task = i;
            pool.execute(() -> System.out.println(
                "任务" + task + " 由 " + Thread.currentThread().getName() + " 执行"));
        }
        pool.shutdown();                      // 不再接受新任务
        pool.awaitTermination(10, TimeUnit.SECONDS);
    }
}
```

## ThreadPoolExecutor 七个核心参数

```java [Multithreading/ThreadPool/ThreadPoolExecutorDemo.java]
import java.util.concurrent.*;

public class ThreadPoolExecutorDemo {
    public static void main(String[] args) {
        ThreadPoolExecutor executor = new ThreadPoolExecutor(
            2,                                    // corePoolSize 核心线程数
            4,                                    // maximumPoolSize 最大线程数
            60L, TimeUnit.SECONDS,                // 空闲线程存活时间
            new LinkedBlockingQueue<>(3),         // 任务队列
            new ThreadFactoryBuilder(),           // 线程工厂（自定义命名）
            new ThreadPoolExecutor.CallerRunsPolicy()  // 拒绝策略
        );

        for (int i = 1; i <= 10; i++) {
            int task = i;
            executor.execute(() -> {
                System.out.println("任务" + task + " 执行，活跃线程: "
                    + executor.getActiveCount());
                try {
                    Thread.sleep(300);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            });
        }

        executor.shutdown();
    }
}

class ThreadFactoryBuilder implements ThreadFactory {
    private final java.util.concurrent.atomic.AtomicInteger seq =
        new java.util.concurrent.atomic.AtomicInteger();

    @Override
    public Thread newThread(Runnable r) {
        return new Thread(r, "biz-pool-" + seq.incrementAndGet());
    }
}
```

| 参数 | 含义 | 建议 |
| --- | --- | --- |
| `corePoolSize` | 常驻线程数 | 根据任务类型计算 |
| `maximumPoolSize` | 最大线程数 | 上限，防止资源耗尽 |
| `keepAliveTime` | 非核心线程空闲存活时间 | 默认 60s 常见 |
| `workQueue` | 等待队列 | 见下方队列选择 |
| `threadFactory` | 线程工厂 | 必须命名，便于排查 |
| `handler` | 拒绝策略 | 默认 AbortPolicy |

## 任务执行流程

```text
提交任务
  → 线程数 < corePoolSize？  创建核心线程执行
  → 队列未满？              入队等待
  → 线程数 < maximumPoolSize？ 创建非核心线程执行
  → 触发拒绝策略
```

## 队列与拒绝策略

| 队列 | 特点 |
| --- | --- |
| `LinkedBlockingQueue` | 无界（默认）或指定容量 |
| `ArrayBlockingQueue` | 有界，固定容量 |
| `SynchronousQueue` | 不缓存任务，直接交给线程 |
| `PriorityBlockingQueue` | 按优先级出队 |

| 拒绝策略 | 行为 |
| --- | --- |
| `AbortPolicy`（默认） | 抛 `RejectedExecutionException` |
| `CallerRunsPolicy` | 由提交任务的线程执行（降低提交速度） |
| `DiscardPolicy` | 静默丢弃 |
| `DiscardOldestPolicy` | 丢弃队列最老的任务 |

## Executors 工厂方法的坑

| 工厂方法 | 问题 |
| --- | --- |
| `newFixedThreadPool(n)` | 默认无界队列，任务积压会 OOM |
| `newCachedThreadPool()` | 最大线程数 `Integer.MAX_VALUE`，可能耗尽线程 |
| `newScheduledThreadPool(n)` | 无界延迟队列，同样有积压风险 |

::: warning 生产建议
生产环境**手动 new ThreadPoolExecutor**，设置有界队列和明确的拒绝策略，并用自定义 ThreadFactory 给线程命名；《阿里巴巴 Java 开发手册》也禁止使用 Executors 快捷方法创建线程池。
:::

## Callable 与 Future

```java [Multithreading/ThreadPool/FutureDemo.java]
import java.util.concurrent.*;

public class FutureDemo {
    public static void main(String[] args) throws Exception {
        ExecutorService pool = Executors.newFixedThreadPool(2);
        Future<Integer> future = pool.submit(() -> {
            Thread.sleep(500);
            return 42;
        });
        System.out.println("结果: " + future.get());   // 阻塞等待
        System.out.println("是否完成: " + future.isDone());
        pool.shutdown();
    }
}
```

输出：

```text
结果: 42
是否完成: true
```

## 关闭线程池

| 方法 | 行为 |
| --- | --- |
| `shutdown()` | 不再接收新任务，执行完已提交任务后关闭 |
| `shutdownNow()` | 中断所有任务，返回未执行任务列表 |
| `awaitTermination(timeout)` | 阻塞等待关闭完成 |

## 线程池监控

```java
executor.getPoolSize();              // 当前线程数
executor.getActiveCount();           // 活跃线程数
executor.getQueue().size();          // 队列积压数
executor.getCompletedTaskCount();    // 已完成任务数
```

## 易错点

::: danger 常见错误
1. 使用 Executors 的快捷方法：无界队列/无限线程，高并发下 OOM，生产禁止。
2. 忘记 `shutdown()`：进程不会退出，任务队列一直挂起。
3. `execute` 提交的任务抛 RuntimeException：不会被捕获，但线程会继续复用；需要日志兜底或使用 `submit` + Future 获取异常。
4. 不自定义线程工厂：排查问题时只能看到 `pool-1-thread-1`。
5. 核心线程数设置过小 + 无界队列：任务全排队，吞吐上不去；用有界队列触发拒绝策略更可控。
6. 在线程池任务里调用 `pool.shutdown()`：会造成混乱，统一由管理方关闭。
:::

## 验证方式

1. 运行 `ThreadPoolExecutorDemo`，观察任务 10 个、队列容量 3 时，第 6 个任务起由调用者线程执行（CallerRunsPolicy）。
2. 把拒绝策略换成 AbortPolicy，重新运行，观察 `RejectedExecutionException`。
3. 连续两次执行 `ExecutorDemo`，确认线程被复用（线程名重复出现）。

## 参考资料

- ThreadPoolExecutor 文档：https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html
- Executors 文档：https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/Executors.html
- Oracle 线程池教程：https://docs.oracle.com/javase/tutorial/essential/concurrency/pools.html
