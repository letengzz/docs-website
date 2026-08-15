# 并发工具类

`java.util.concurrent` 提供了大量开箱即用的并发工具：倒计时门闩、栅栏、信号量、交换器、原子类等。用好它们，能避免手写 wait/notify 的细节错误。

## CountDownLatch：等 N 个事件

```java [Multithreading/ConcurrentUtils/CountDownLatchDemo.java]
import java.util.concurrent.CountDownLatch;

public class CountDownLatchDemo {
    public static void main(String[] args) throws InterruptedException {
        CountDownLatch latch = new CountDownLatch(3);

        for (int i = 1; i <= 3; i++) {
            int task = i;
            new Thread(() -> {
                System.out.println("任务" + task + " 完成");
                latch.countDown();
            }).start();
        }

        latch.await();   // 主线程等 3 个任务全部 countDown
        System.out.println("全部完成，继续");
    }
}
```

输出：

```text
任务1 完成
任务2 完成
任务3 完成
全部完成，继续
```

CountDownLatch **不可复用**，用一次就作废。

## CyclicBarrier：N 个线程互相等待

```java [Multithreading/ConcurrentUtils/CyclicBarrierDemo.java]
import java.util.concurrent.CyclicBarrier;

public class CyclicBarrierDemo {
    public static void main(String[] args) {
        CyclicBarrier barrier = new CyclicBarrier(3, () ->
            System.out.println("三人都到齐，一起出发"));

        for (int i = 1; i <= 3; i++) {
            int person = i;
            new Thread(() -> {
                System.out.println("人员" + person + " 到达");
                try {
                    barrier.await();
                } catch (Exception e) {
                    Thread.currentThread().interrupt();
                }
            }).start();
        }
    }
}
```

### 与 CountDownLatch 的区别

| 维度 | CountDownLatch | CyclicBarrier |
| --- | --- | --- |
| 语义 | 等计数归零 | 等固定数量线程到齐 |
| 等待方 | 可以是外部线程 | 参与的线程互相等待 |
| 复用 | 不可复用 | 可重置复用 |
| 计数方向 | 递减 | 固定数量 |

## Semaphore：限流

```java [Multithreading/ConcurrentUtils/SemaphoreDemo.java]
import java.util.concurrent.Semaphore;

public class SemaphoreDemo {
    public static void main(String[] args) {
        Semaphore semaphore = new Semaphore(2);   // 最多 2 个并发

        for (int i = 1; i <= 5; i++) {
            int task = i;
            new Thread(() -> {
                try {
                    semaphore.acquire();
                    System.out.println("任务" + task + " 开始");
                    Thread.sleep(500);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    semaphore.release();
                }
            }).start();
        }
    }
}
```

`acquire()` 与 `release()` 必须成对，release 放 finally。

## Exchanger：两线程交换数据

```java [Multithreading/ConcurrentUtils/ExchangerDemo.java]
import java.util.concurrent.Exchanger;

public class ExchangerDemo {
    public static void main(String[] args) {
        Exchanger<String> exchanger = new Exchanger<>();

        new Thread(() -> {
            try {
                String msg = exchanger.exchange("来自线程A");
                System.out.println("A 收到: " + msg);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }).start();

        new Thread(() -> {
            try {
                String msg = exchanger.exchange("来自线程B");
                System.out.println("B 收到: " + msg);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }).start();
    }
}
```

## 原子类：无锁计数

```java [Multithreading/ConcurrentUtils/AtomicDemo.java]
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.LongAdder;

public class AtomicDemo {
    public static void main(String[] args) throws InterruptedException {
        AtomicInteger count = new AtomicInteger();
        LongAdder adder = new LongAdder();

        Runnable task = () -> {
            for (int i = 0; i < 10000; i++) {
                count.incrementAndGet();
                adder.increment();
            }
        };

        Thread t1 = new Thread(task);
        Thread t2 = new Thread(task);
        t1.start();
        t2.start();
        t1.join();
        t2.join();

        System.out.println(count.get());   // 20000
        System.out.println(adder.sum());   // 20000
    }
}
```

原子类基于 **CAS（Compare And Swap）** 实现，无锁但并发高时自旋开销大；高竞争累加场景用 `LongAdder`（分段累加，性能更好）。

## 常用工具类总览

| 工具 | 用途 | 关键方法 |
| --- | --- | --- |
| CountDownLatch | 等 N 个任务完成 | `await()` / `countDown()` |
| CyclicBarrier | N 个线程到齐再继续 | `await()` |
| Semaphore | 控制并发数量 | `acquire()` / `release()` |
| Exchanger | 两线程交换数据 | `exchange(v)` |
| Phaser | 分阶段栅栏 | `arriveAndAwaitAdvance()` |
| AtomicInteger 等 | 无锁原子变量 | `incrementAndGet()` |
| LongAdder | 高竞争累加 | `increment()` / `sum()` |

## 易错点

::: danger 常见错误
1. CountDownLatch 的计数与任务数不一致：永远等不到归零，程序挂起；给 `await(timeout)` 加超时保护。
2. Semaphore 忘记 `release()`：许可证耗尽，后续任务全部阻塞。
3. 把 CyclicBarrier 当 CountDownLatch 用：语义相反，容易死等。
4. 原子类解决单变量原子性，解决不了“多个变量联动”的复合操作：仍需要锁。
5. 高竞争下无脑用 AtomicLong：改用 LongAdder 减少 CAS 自旋开销。
:::

## 验证方式

1. 运行 `CountDownLatchDemo`，确认“全部完成”在三个任务之后打印。
2. 运行 `SemaphoreDemo`，观察同一时刻最多 2 个任务执行。
3. 运行 `AtomicDemo`，确认两个线程各累加 10000 后结果为 20000。

## 参考资料

- java.util.concurrent 包文档：https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/package-summary.html
- CountDownLatch 文档：https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/CountDownLatch.html
- 原子类说明：https://docs.oracle.com/javase/tutorial/essential/concurrency/atomicvars.html
