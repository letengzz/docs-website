# 多线程

多线程是 Java 的核心特性之一，允许程序同时执行多个任务。Java 提供了丰富的多线程支持，包括线程创建、同步机制、线程池等。

## 线程基础

### 线程的创建

```java
// Multithreading/ThreadCreationDemo.java

public class ThreadCreationDemo {
    public static void main(String[] args) {
        System.out.println("=== 线程创建方式 ===");
        
        // 方式1：继承 Thread 类
        System.out.println("\n方式1：继承 Thread 类");
        MyThread thread1 = new MyThread("线程1");
        thread1.start();  // 启动线程
        
        // 方式2：实现 Runnable 接口
        System.out.println("\n方式2：实现 Runnable 接口");
        Thread thread2 = new Thread(new MyRunnable(), "线程2");
        thread2.start();
        
        // 方式3：实现 Callable 接口（可以有返回值）
        System.out.println("\n方式3：实现 Callable 接口");
        java.util.concurrent.FutureTask<String> futureTask = 
            new java.util.concurrent.FutureTask<>(new MyCallable());
        Thread thread3 = new Thread(futureTask, "线程3");
        thread3.start();
        
        try {
            System.out.println("Callable 返回值: " + futureTask.get());
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        // 方式4：使用 Lambda 表达式（Runnable 接口）
        System.out.println("\n方式4：Lambda 表达式");
        Thread thread4 = new Thread(() -> {
            for (int i = 0; i < 5; i++) {
                System.out.println(Thread.currentThread().getName() + ": " + i);
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }, "线程4");
        thread4.start();
        
        // 等待线程结束
        try {
            thread1.join();
            thread2.join();
            thread3.join();
            thread4.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        
        System.out.println("\n所有线程执行完毕");
    }
}

// 方式1：继承 Thread
class MyThread extends Thread {
    public MyThread(String name) {
        super(name);
    }
    
    @Override
    public void run() {
        for (int i = 0; i < 5; i++) {
            System.out.println(getName() + ": " + i);
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

// 方式2：实现 Runnable
class MyRunnable implements Runnable {
    @Override
    public void run() {
        for (int i = 0; i < 5; i++) {
            System.out.println(Thread.currentThread().getName() + ": " + i);
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

// 方式3：实现 Callable
class MyCallable implements java.util.concurrent.Callable<String> {
    @Override
    public String call() throws Exception {
        for (int i = 0; i < 5; i++) {
            System.out.println(Thread.currentThread().getName() + ": " + i);
            Thread.sleep(100);
        }
        return "Callable 执行完成";
    }
}
```

### Thread 常用方法

```java
// Multithreading/ThreadMethodsDemo.java

public class ThreadMethodsDemo {
    public static void main(String[] args) {
        // 获取当前线程
        Thread currentThread = Thread.currentThread();
        System.out.println("当前线程: " + currentThread.getName());
        System.out.println("线程优先级: " + currentThread.getPriority());
        System.out.println("是否存活: " + currentThread.isAlive());
        System.out.println("线程状态: " + currentThread.getState());
        
        // 创建新线程演示方法
        Thread demoThread = new Thread(() -> {
            System.out.println("子线程启动");
            
            try {
                // sleep - 线程休眠
                Thread.sleep(1000);
                System.out.println("子线程休眠结束");
                
                // yield - 放弃 CPU 执行权
                Thread.yield();
                System.out.println("子线程放弃了 CPU");
                
            } catch (InterruptedException e) {
                System.out.println("子线程被中断");
            }
            
            System.out.println("子线程结束");
        }, "DemoThread");
        
        // 设置线程优先级（1-10，默认5）
        demoThread.setPriority(Thread.MAX_PRIORITY);
        demoThread.start();
        
        // 等待线程结束
        try {
            demoThread.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        
        System.out.println("主线程继续执行");
        
        // 中断线程演示
        System.out.println("\n=== 线程中断 ===");
        Thread interruptThread = new Thread(() -> {
            try {
                while (!Thread.currentThread().isInterrupted()) {
                    System.out.println("线程运行中...");
                    Thread.sleep(500);
                }
            } catch (InterruptedException e) {
                // 捕获中断异常后，中断状态会被清除
                System.out.println("检测到中断，退出循环");
            }
        }, "InterruptThread");
        
        interruptThread.start();
        
        // 主线程 2 秒后中断子线程
        try {
            Thread.sleep(2000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        interruptThread.interrupt();
        
        try {
            interruptThread.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}
```

## 线程同步

### synchronized 关键字

```java
// Multithreading/SynchronizedDemo.java

class SynchronizedCounter {
    private int count = 0;
    
    // 同步方法 - 锁住当前对象
    public synchronized void increment() {
        count++;
    }
    
    public synchronized int getCount() {
        return count;
    }
    
    // 同步代码块
    public void incrementWithBlock() {
        synchronized (this) {
            count++;
        }
    }
    
    // 锁住类对象
    public static synchronized void staticMethod() {
        // 锁住当前类的 Class 对象
    }
}

class BankAccount {
    private final String accountId;
    private double balance;
    
    public BankAccount(String accountId, double balance) {
        this.accountId = accountId;
        this.balance = balance;
    }
    
    // 同步方法保证线程安全
    public synchronized void deposit(double amount) {
        if (amount > 0) {
            balance += amount;
            System.out.println(Thread.currentThread().getName() + 
                " 存入 " + amount + "，余额: " + balance);
        }
    }
    
    public synchronized void withdraw(double amount) {
        if (amount > 0 && balance >= amount) {
            balance -= amount;
            System.out.println(Thread.currentThread().getName() + 
                " 取出 " + amount + "，余额: " + balance);
        } else {
            System.out.println(Thread.currentThread().getName() + 
                " 取款失败，余额不足");
        }
    }
    
    public synchronized double getBalance() {
        return balance;
    }
}

public class SynchronizedDemo {
    public static void main(String[] args) throws InterruptedException {
        BankAccount account = new BankAccount("123456", 1000);
        
        // 创建多个线程同时操作账户
        Thread[] threads = new Thread[10];
        for (int i = 0; i < 10; i++) {
            final int num = i;
            threads[i] = new Thread(() -> {
                account.deposit(100);
                account.withdraw(50);
            }, "线程-" + (i + 1));
            threads[i].start();
        }
        
        // 等待所有线程完成
        for (Thread thread : threads) {
            thread.join();
        }
        
        System.out.println("最终余额: " + account.getBalance());
        
        // 死锁演示
        System.out.println("\n=== 死锁示例 ===");
        DeadlockDemo deadlockDemo = new DeadlockDemo();
        deadlockDemo.demonstrateDeadlock();
    }
}

class DeadlockDemo {
    private final Object lock1 = new Object();
    private final Object lock2 = new Object();
    
    public void demonstrateDeadlock() {
        Thread thread1 = new Thread(() -> {
            synchronized (lock1) {
                System.out.println("线程1 获取了锁1");
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {}
                synchronized (lock2) {
                    System.out.println("线程1 获取了锁2");
                }
            }
        }, "死锁线程1");
        
        Thread thread2 = new Thread(() -> {
            synchronized (lock2) {
                System.out.println("线程2 获取了锁2");
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {}
                synchronized (lock1) {
                    System.out.println("线程2 获取了锁1");
                }
            }
        }, "死锁线程2");
        
        thread1.start();
        thread2.start();
        
        // 注意：这段代码会造成死锁，实际运行请谨慎
    }
}
```

### ReentrantLock

```java
// Multithreading/ReentrantLockDemo.java
import java.util.concurrent.locks.ReentrantLock;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.TimeUnit;

class ReentrantCounter {
    private int count = 0;
    private final Lock lock = new ReentrantLock(true);  // 公平锁
    
    public void increment() {
        lock.lock();
        try {
            count++;
        } finally {
            lock.unlock();  // 必须在 finally 中释放锁
        }
    }
    
    public int getCount() {
        lock.lock();
        try {
            return count;
        } finally {
            lock.unlock();
        }
    }
    
    // 尝试获取锁
    public boolean tryIncrement() {
        if (lock.tryLock()) {
            try {
                count++;
                return true;
            } finally {
                lock.unlock();
            }
        }
        return false;
    }
    
    // 带超时的锁获取
    public boolean tryIncrementWithTimeout(long timeout, TimeUnit unit) {
        try {
            if (lock.tryLock(timeout, unit)) {
                try {
                    count++;
                    return true;
                } finally {
                    lock.unlock();
                }
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return false;
    }
}

class ReadWriteLockDemo {
    private int data = 0;
    private final java.util.concurrent.locks.ReadWriteLock rwLock = 
        new java.util.concurrent.locks.ReentrantReadWriteLock();
    
    public void write(int value) {
        rwLock.writeLock().lock();
        try {
            System.out.println(Thread.currentThread().getName() + 
                " 写入数据: " + value);
            data = value;
            Thread.sleep(500);
        } catch (InterruptedException e) {
            e.printStackTrace();
        } finally {
            rwLock.writeLock().unlock();
        }
    }
    
    public int read() {
        rwLock.readLock().lock();
        try {
            System.out.println(Thread.currentThread().getName() + 
                " 读取数据: " + data);
            return data;
        } finally {
            rwLock.readLock().unlock();
        }
    }
}

public class ReentrantLockDemo {
    public static void main(String[] args) throws InterruptedException {
        ReentrantCounter counter = new ReentrantCounter();
        
        // 多线程并发增加计数
        Thread[] threads = new Thread[100];
        for (int i = 0; i < 100; i++) {
            threads[i] = new Thread(() -> {
                counter.increment();
            }, "计数线程-" + i);
            threads[i].start();
        }
        
        for (Thread thread : threads) {
            thread.join();
        }
        
        System.out.println("最终计数: " + counter.getCount());
        
        // 读写锁演示
        System.out.println("\n=== 读写锁演示 ===");
        ReadWriteLockDemo rwDemo = new ReadWriteLockDemo();
        
        // 多个读线程
        for (int i = 0; i < 5; i++) {
            final int num = i;
            new Thread(() -> rwDemo.read(), "读线程-" + num).start();
        }
        
        // 写线程
        new Thread(() -> rwDemo.write(100), "写线程").start();
        
        Thread.sleep(2000);
    }
}
```

## 线程间通信

### wait/notify

```java
// Multithreading/ThreadCommunicationDemo.java

class ProducerConsumer {
    private final java.util.List<Integer> buffer = new java.util.ArrayList<>();
    private final int MAX_SIZE = 5;
    
    // 生产者
    public synchronized void produce(int item) throws InterruptedException {
        while (buffer.size() >= MAX_SIZE) {
            System.out.println("缓冲区满，生产者等待");
            wait();  // 等待消费者消费
        }
        
        buffer.add(item);
        System.out.println("生产: " + item);
        notifyAll();  // 通知消费者
    }
    
    // 消费者
    public synchronized int consume() throws InterruptedException {
        while (buffer.isEmpty()) {
            System.out.println("缓冲区空，消费者等待");
            wait();  // 等待生产者生产
        }
        
        int item = buffer.remove(0);
        System.out.println("消费: " + item);
        notifyAll();  // 通知生产者
        return item;
    }
}

class ThreadCommunicationDemo {
    public static void main(String[] args) {
        ProducerConsumer pc = new ProducerConsumer();
        
        // 生产者线程
        Thread producer = new Thread(() -> {
            for (int i = 1; i <= 10; i++) {
                try {
                    pc.produce(i);
                    Thread.sleep(200);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }, "生产者");
        
        // 消费者线程
        Thread consumer = new Thread(() -> {
            for (int i = 1; i <= 10; i++) {
                try {
                    pc.consume();
                    Thread.sleep(500);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }, "消费者");
        
        producer.start();
        consumer.start();
        
        try {
            producer.join();
            consumer.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}
```

### Condition

```java
// Multithreading/ConditionDemo.java
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.ReentrantLock;

class BoundedBuffer {
    private final Object[] items = new Object[5];
    private int count = 0;
    private int takeIndex = 0;
    private int putIndex = 0;
    
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition notEmpty = lock.newCondition();
    private final Condition notFull = lock.newCondition();
    
    public void put(Object item) throws InterruptedException {
        lock.lock();
        try {
            while (count == items.length) {
                notFull.await();
            }
            items[putIndex] = item;
            putIndex = (putIndex + 1) % items.length;
            count++;
            System.out.println("生产: " + item + "，当前数量: " + count);
            notEmpty.signal();
        } finally {
            lock.unlock();
        }
    }
    
    public Object take() throws InterruptedException {
        lock.lock();
        try {
            while (count == 0) {
                notEmpty.await();
            }
            Object item = items[takeIndex];
            takeIndex = (takeIndex + 1) % items.length;
            count--;
            System.out.println("消费: " + item + "，当前数量: " + count);
            notFull.signal();
            return item;
        } finally {
            lock.unlock();
        }
    }
}

public class ConditionDemo {
    public static void main(String[] args) {
        BoundedBuffer buffer = new BoundedBuffer();
        
        Thread producer = new Thread(() -> {
            for (int i = 1; i <= 10; i++) {
                try {
                    buffer.put(i);
                    Thread.sleep(300);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }, "生产者");
        
        Thread consumer = new Thread(() -> {
            for (int i = 1; i <= 10; i++) {
                try {
                    buffer.take();
                    Thread.sleep(500);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }, "消费者");
        
        producer.start();
        consumer.start();
        
        try {
            producer.join();
            consumer.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}
```

## 线程池

### Executors 工厂方法

```java
// Multithreading/ThreadPoolDemo.java
import java.util.concurrent.*;

public class ThreadPoolDemo {
    public static void main(String[] args) {
        System.out.println("=== 线程池演示 ===");
        
        // 1. 创建固定大小线程池
        System.out.println("\n固定大小线程池 (3个线程):");
        ExecutorService fixedPool = Executors.newFixedThreadPool(3);
        for (int i = 1; i <= 5; i++) {
            final int taskNum = i;
            fixedPool.execute(() -> {
                System.out.println("任务 " + taskNum + " 由 " + 
                    Thread.currentThread().getName() + " 执行");
                try {
                    Thread.sleep(500);
                } catch (InterruptedException e) {}
            });
        }
        fixedPool.shutdown();
        
        // 2. 创建单线程线程池
        System.out.println("\n单线程线程池:");
        ExecutorService singlePool = Executors.newSingleThreadExecutor();
        for (int i = 1; i <= 3; i++) {
            final int taskNum = i;
            singlePool.execute(() -> {
                System.out.println("任务 " + taskNum + " 由 " + 
                    Thread.currentThread().getName() + " 执行");
            });
        }
        singlePool.shutdown();
        
        // 3. 创建缓存线程池
        System.out.println("\n缓存线程池:");
        ExecutorService cachedPool = Executors.newCachedThreadPool();
        for (int i = 1; i <= 5; i++) {
            final int taskNum = i;
            cachedPool.execute(() -> {
                System.out.println("任务 " + taskNum + " 由 " + 
                    Thread.currentThread().getName() + " 执行");
            });
        }
        cachedPool.shutdown();
        
        // 4. 创建调度线程池
        System.out.println("\n调度线程池:");
        ScheduledExecutorService scheduledPool = 
            Executors.newScheduledThreadPool(2);
        
        // 延迟执行
        scheduledPool.schedule(() -> {
            System.out.println("延迟 2 秒执行");
        }, 2, TimeUnit.SECONDS);
        
        // 固定频率执行
        scheduledPool.scheduleAtFixedRate(() -> {
            System.out.println("每 1 秒执行一次");
        }, 0, 1, TimeUnit.SECONDS);
        
        // 5. 创建工作窃取线程池
        System.out.println("\n工作窃取线程池:");
        ExecutorService workStealingPool = Executors.newWorkStealingPool();
        for (int i = 1; i <= 8; i++) {
            final int taskNum = i;
            ((ForkJoinPool) workStealingPool).submit(() -> {
                System.out.println("任务 " + taskNum + " 由 " + 
                    Thread.currentThread().getName() + " 执行");
            });
        }
        
        try {
            Thread.sleep(3000);
            workStealingPool.shutdown();
            scheduledPool.shutdown();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}
```

### ThreadPoolExecutor

```java
// Multithreading/ThreadPoolExecutorDemo.java
import java.util.concurrent.*;

public class ThreadPoolExecutorDemo {
    public static void main(String[] args) {
        // 自定义线程池
        ThreadPoolExecutor executor = new ThreadPoolExecutor(
            2,                          // 核心池大小
            4,                          // 最大池大小
            60L, TimeUnit.SECONDS,      // 空闲线程存活时间
            new LinkedBlockingQueue<>(3), // 任务队列
            Executors.defaultThreadFactory(),  // 线程工厂
            new ThreadPoolExecutor.CallerRunsPolicy()  // 拒绝策略
        );
        
        System.out.println("=== 自定义线程池 ===");
        
        // 提交任务
        for (int i = 1; i <= 10; i++) {
            final int taskNum = i;
            executor.execute(() -> {
                System.out.println("任务 " + taskNum + " 执行中，活跃线程数: " + 
                    executor.getActiveCount());
                try {
                    Thread.sleep(500);
                } catch (InterruptedException e) {}
            });
        }
        
        // 监控线程池状态
        System.out.println("\n线程池状态:");
        System.out.println("核心线程数: " + executor.getCorePoolSize());
        System.out.println("最大线程数: " + executor.getMaximumPoolSize());
        System.out.println("当前线程数: " + executor.getPoolSize());
        System.out.println("活跃线程数: " + executor.getActiveCount());
        System.out.println("已完成任务数: " + executor.getCompletedTaskCount());
        System.out.println("队列任务数: " + executor.getQueue().size());
        
        executor.shutdown();
        
        try {
            executor.awaitTermination(10, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}
```

### Callable 与 Future

```java
// Multithreading/FutureDemo.java
import java.util.concurrent.*;

public class FutureDemo {
    public static void main(String[] args) throws Exception {
        System.out.println("=== Future 演示 ===");
        
        ExecutorService executor = Executors.newFixedThreadPool(3);
        
        // 提交 Callable 任务
        Future<Integer> future1 = executor.submit(() -> {
            System.out.println("计算任务执行中...");
            Thread.sleep(1000);
            return 42;
        });
        
        // 提交 Runnable 任务
        Future<?> future2 = executor.submit(() -> {
            System.out.println("无返回值任务执行中");
            Thread.sleep(500);
        });
        
        // 提交有返回值的 Runnable
        Future<String> future3 = executor.submit(() -> {
            Thread.sleep(800);
            return "任务完成";
        }, "返回结果");
        
        // 获取结果
        System.out.println("future1 结果: " + future1.get());
        System.out.println("future2 完成: " + future2.get());
        System.out.println("future3 结果: " + future3.get());
        
        // Future 其他方法
        System.out.println("\nFuture 其他方法:");
        System.out.println("future1 是否完成: " + future1.isDone());
        System.out.println("future1 是否取消: " + future1.isCancelled());
        
        // 取消任务
        Future<Integer> cancelFuture = executor.submit(() -> {
            Thread.sleep(10000);
            return 100;
        });
        Thread.sleep(500);
        System.out.println("取消任务: " + cancelFuture.cancel(true));
        
        // 使用 CompletableFuture（Java 8+）
        System.out.println("\n=== CompletableFuture 演示 ===");
        
        CompletableFuture<String> cf1 = CompletableFuture.supplyAsync(() -> {
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {}
            return "结果1";
        });
        
        CompletableFuture<String> cf2 = CompletableFuture.supplyAsync(() -> {
            try {
                Thread.sleep(500);
            } catch (InterruptedException e) {}
            return "结果2";
        });
        
        // 组合结果
        CompletableFuture<String> combined = cf1.thenCombine(cf2, 
            (r1, r2) -> r1 + " + " + r2);
        
        System.out.println("组合结果: " + combined.get());
        
        // 异常处理
        CompletableFuture<Integer> exceptional = CompletableFuture.supplyAsync(() -> {
            throw new RuntimeException("任务异常");
        });
        
        exceptional.exceptionally(e -> {
            System.out.println("捕获异常: " + e.getMessage());
            return 0;
        });
        
        executor.shutdown();
    }
}
```

::: danger 多线程注意事项
1. 避免死锁：确保多个锁的获取顺序一致
2. 不要在同步块内调用可能阻塞的方法
3. 使用线程池管理线程，避免创建过多线程
4. 注意共享变量的可见性问题，使用 volatile 或同步
5. 优先使用高层 API（ExecutorService、ConcurrentHashMap 等）
6. 避免过度同步，减少锁的粒度
:::
