# volatile 与内存可见性

`volatile` 是 Java 中最轻量的同步关键字，解决**可见性**和**有序性**问题，但**不保证原子性**。理解它之前，先要理解 Java 内存模型（JMM）。

## JMM：主内存与工作内存

```text
线程 A 工作内存  ⇄  主内存  ⇄  线程 B 工作内存
```

线程操作共享变量时，会把变量拷贝到自己的工作内存（寄存器/缓存），操作完再写回主内存。没有同步时，写回时机不确定，其他线程可能一直读到旧值。

![JMM 主内存与工作内存](../assets/jmm.svg)

## volatile 的两个能力

1. **可见性**：写 volatile 变量立即刷新到主内存，读 volatile 变量强制从主内存读取。
2. **有序性**：禁止指令重排序（在 volatile 读写前后加内存屏障）。

它**不保证原子性**：`volatile int count; count++` 依然是“读-改-写”三步，多线程下照样丢更新。

## 经典错误：count++

```java [Multithreading/Volatile/VolatileNotAtomicDemo.java]
public class VolatileNotAtomicDemo {
    private static volatile int count = 0;

    public static void main(String[] args) throws InterruptedException {
        Thread t1 = new Thread(() -> {
            for (int i = 0; i < 10000; i++) count++;
        });
        Thread t2 = new Thread(() -> {
            for (int i = 0; i < 10000; i++) count++;
        });
        t1.start();
        t2.start();
        t1.join();
        t2.join();
        System.out.println(count);   // 小于 20000
    }
}
```

正确做法：`synchronized`、`AtomicInteger` 或 `LongAdder`。

## 正确场景一：状态标志

```java [Multithreading/Volatile/FlagDemo.java]
public class FlagDemo {
    private static volatile boolean running = true;

    public static void main(String[] args) throws InterruptedException {
        Thread worker = new Thread(() -> {
            while (running) {
                // 处理任务
            }
            System.out.println("已停止");
        });
        worker.start();
        Thread.sleep(500);
        running = false;   // 主线程修改，worker 能立即看到
    }
}
```

去掉 `volatile` 后，worker 可能永远看不到 `running = false`（取决于 JIT 优化）。

## 正确场景二：双重检查锁单例

```java [Multithreading/Volatile/Singleton.java]
public class Singleton {
    private static volatile Singleton instance;

    private Singleton() {
    }

    public static Singleton getInstance() {
        if (instance == null) {                        // 第一次检查
            synchronized (Singleton.class) {
                if (instance == null) {                // 第二次检查
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

`instance` 必须加 `volatile`：否则 `new Singleton()` 的“分配内存 → 初始化 → 赋值引用”可能重排序，其他线程拿到未初始化完成的对象。

## happens-before 规则

JMM 通过 happens-before（先行发生）关系保证有序性，常用规则：

1. 程序次序规则：代码书写顺序。
2. 锁规则：解锁 happens-before 后续加锁。
3. **volatile 规则**：volatile 写 happens-before 后续对该变量的读。
4. 传递性：A 先于 B，B 先于 C，则 A 先于 C。
5. 线程启动/终止规则：`start()` happens-before 线程内操作；线程内操作 happens-before `join()` 返回。

## volatile 与 synchronized 对比

| 维度 | volatile | synchronized |
| --- | --- | --- |
| 原子性 | 不保证 | 保证 |
| 可见性 | 保证 | 保证 |
| 有序性 | 禁止重排序 | 保证 |
| 互斥 | 无 | 有 |
| 性能 | 轻量 | 较重（但 JVM 已优化） |
| 适用 | 标志位、单例 | 复合操作、临界区 |

## 易错点

::: danger 常见错误
1. 用 volatile 修复合计/计数：`volatile int count++` 依然线程不安全，用 `AtomicInteger`。
2. 认为 volatile 能替代锁：多个变量联动（如“先检查后执行”）需要锁保证整体原子性。
3. 在 volatile 读写之外依赖其他共享变量：volatile 只保证自身可见性。
4. 把大对象整个加 volatile：可见性只针对引用，对象内部字段修改仍需同步。
5. 单例双重检查不加 volatile：可能拿到半初始化对象。
:::

## 验证方式

1. 运行 `VolatileNotAtomicDemo`，确认结果小于 20000；换成 `AtomicInteger` 后恢复 20000。
2. 运行 `FlagDemo`，确认 worker 正常退出；去掉 volatile 后在 `-server` 模式多跑几次观察差异。
3. 用 `jconsole` 或 JIT 参数观察可见性问题的复现。

## 参考资料

- Java 内存模型规范：https://docs.oracle.com/javase/specs/jls/se25/html/jls-17.html
- volatile 教程：https://docs.oracle.com/javase/tutorial/essential/concurrency/atomic.html
- JEP 188（Java 内存模型更新）：https://openjdk.org/jeps/188
