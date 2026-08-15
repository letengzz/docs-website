# 并发集合

普通集合（ArrayList、HashMap）在多线程下会出现数据错乱甚至死循环；并发集合（Concurrent Collections）是 `java.util.concurrent` 包为高并发场景提供的安全实现。这一篇讲清楚选型和原理。

## 线程安全集合总览

| 集合 | 线程安全策略 | 适用场景 |
| --- | --- | --- |
| `ConcurrentHashMap` | CAS + 局部 synchronized | 高并发读写的 Map |
| `CopyOnWriteArrayList` | 写时复制 | 读多写少的 List |
| `CopyOnWriteArraySet` | 基于 CopyOnWriteArrayList | 读多写少的 Set |
| `ConcurrentSkipListMap` | 跳表 | 有序且线程安全的 Map |
| `ConcurrentSkipListSet` | 跳表 | 有序且线程安全的 Set |
| `ArrayBlockingQueue` | 锁 + 数组 | 有界阻塞队列 |
| `LinkedBlockingQueue` | 锁 + 链表 | 无界/有界阻塞队列 |
| `SynchronousQueue` | 直接交接 | 生产者消费者直接配对 |
| `PriorityBlockingQueue` | 堆 + 锁 | 优先级阻塞队列 |
| `Collections.synchronizedXxx` | 全方法加锁 | 遗留代码兼容 |

::: warning 说明
`Hashtable`、`Vector` 虽然线程安全，但所有方法串行加锁，高并发下是性能瓶颈；新代码优先使用 `ConcurrentHashMap`、`CopyOnWriteArrayList`。
:::

## ConcurrentHashMap：并发 Map 首选

```java [Collection/Concurrent/ConcurrentMapDemo.java]
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class ConcurrentMapDemo {
    public static void main(String[] args) {
        Map<String, Integer> counter = new ConcurrentHashMap<>();

        // 高并发计数：merge 是原子的
        Runnable task = () -> {
            for (int i = 0; i < 1000; i++) {
                counter.merge("hits", 1, Integer::sum);
            }
        };

        Thread t1 = new Thread(task);
        Thread t2 = new Thread(task);
        t1.start();
        t2.start();
        try {
            t1.join();
            t2.join();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        System.out.println(counter.get("hits"));   // 2000
    }
}
```

输出：

```text
2000
```

如果把 `ConcurrentHashMap` 换成 `HashMap`，结果很可能小于 2000。

## CopyOnWriteArrayList：读多写少

写入时复制整个数组，读操作不加锁；适合“配置列表、监听器列表”这类读极多、写极少的场景。

```java [Collection/Concurrent/CopyOnWriteDemo.java]
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

public class CopyOnWriteDemo {
    public static void main(String[] args) {
        List<String> listeners = new CopyOnWriteArrayList<>();
        listeners.add("A");
        listeners.add("B");

        // 遍历时安全删除（快照迭代）
        for (String l : listeners) {
            if (l.equals("A")) {
                listeners.remove(l);
            }
        }
        System.out.println(listeners);   // [B]
    }
}
```

输出：

```text
[B]
```

## BlockingQueue：生产者-消费者

```java [Collection/Concurrent/BlockingQueueDemo.java]
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;

public class BlockingQueueDemo {
    public static void main(String[] args) throws InterruptedException {
        BlockingQueue<String> queue = new ArrayBlockingQueue<>(2);

        queue.put("任务1");       // 满时阻塞等待
        queue.put("任务2");
        System.out.println(queue.take());   // 空时阻塞等待
        System.out.println(queue.take());
    }
}
```

输出：

```text
任务1
任务2
```

常用方法分类：

| 操作 | 抛异常 | 返回特殊值 | 阻塞 |
| --- | --- | --- | --- |
| 入队 | `add` | `offer` | `put` |
| 出队 | `remove` | `poll` | `take` |
| 查看 | `element` | `peek` | - |

## 为什么不用 Hashtable / synchronizedMap

`Collections.synchronizedMap` 给每个方法加锁，但“检查再操作”的复合操作（如 `if (!map.containsKey(k)) map.put(k, v)`）仍然不是原子的，需要手动加锁；`ConcurrentHashMap` 的 `putIfAbsent`、`computeIfAbsent`、`merge` 原生原子，且读操作几乎无锁。

## 易错点

::: danger 常见错误
1. `ConcurrentHashMap` **不允许 null 键和 null 值**：从 HashMap 迁移时先排查。
2. `ConcurrentHashMap` 的迭代是**弱一致**的：遍历时其他线程的修改可能看不到，不要依赖“遍历结果等于最终状态”。
3. `CopyOnWriteArrayList` 每次写都复制数组：写多读少时性能很差，不要滥用。
4. 对 `Collections.synchronizedList` 的 `for-each` 不加锁：迭代期间其他线程修改会抛 `ConcurrentModificationException`，必须 synchronized 包裹整个迭代。
5. 复合操作（先查后写）在并发集合上也要用原子 API（`putIfAbsent` / `merge`），而不是“先 get 再 put”。
:::

## 验证方式

1. 运行 `ConcurrentMapDemo`，确认输出 2000；把 Map 换成 HashMap 多跑几次，观察小于 2000 的情况。
2. 运行 `BlockingQueueDemo`，确认 `put`/`take` 阻塞语义。
3. 用 `synchronizedList` 写一段不加锁的 for-each，配合另一个线程删除元素，观察异常。

## 参考资料

- java.util.concurrent 包文档：https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/package-summary.html
- ConcurrentHashMap 文档：https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html
- BlockingQueue 文档：https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/BlockingQueue.html
