# 内存结构

JVM 在执行 Java 程序时会把内存划分为若干区域，称为**运行时数据区（Runtime Data Area）**。理解每个区域“存什么、什么时候分配、什么时候报错”，是 JVM 调优和故障排查的基础。

::: info 版本现状（2026-08 核对）
本文基于 **Java 25 LTS**：JDK 8 起方法区由**元空间（Metaspace）**实现，使用本地内存；字符串常量池在堆中。
:::

## 运行时数据区总览

```text
┌───────────────────────────────────────────────┐
│ 线程私有                                         │
│   程序计数器（PC Register）                     │
│   虚拟机栈（Java Virtual Machine Stack）        │
│   本地方法栈（Native Method Stack）             │
├───────────────────────────────────────────────┤
│ 线程共享                                         │
│   堆（Heap）                ← 对象实例          │
│   方法区 / 元空间（Metaspace）← 类元信息、常量   │
│   直接内存（Direct Memory，NIO，本地内存）       │
└───────────────────────────────────────────────┘
```

## 各区域详解

| 区域 | 线程 | 存储内容 | 异常 |
| --- | --- | --- | --- |
| 程序计数器 | 私有 | 当前线程执行的字节码行号 | 无 |
| 虚拟机栈 | 私有 | 栈帧：局部变量表、操作数栈、方法返回地址 | `StackOverflowError` / 堆 OOM |
| 本地方法栈 | 私有 | native 方法调用 | `StackOverflowError` |
| 堆 | 共享 | 对象实例、数组、字符串常量池 | `OutOfMemoryError: Java heap space` |
| 方法区（元空间） | 共享 | 类元信息、运行时常量池、静态变量 | `OutOfMemoryError: Metaspace` |
| 直接内存 | 共享 | NIO 缓冲区（`DirectByteBuffer`） | `OutOfMemoryError: Direct buffer memory` |

### 虚拟机栈与栈帧

每个方法调用对应一个**栈帧**：

```text
main() 调用 add() 调用 calc()
栈帧1（main）→ 栈帧2（add）→ 栈帧3（calc）→ 方法返回后弹出
```

递归过深会抛 `StackOverflowError`：

```java [JVM/MemoryStructure/StackOverflowDemo.java]
public class StackOverflowDemo {
    public static void main(String[] args) {
        recurse(0);
    }

    static void recurse(int depth) {
        System.out.println("深度: " + depth);
        recurse(depth + 1);   // 无限递归
    }
}
```

运行后抛出 `java.lang.StackOverflowError`。

### 堆

堆是**所有线程共享**的最大内存区域，几乎所有的对象实例和数组都在这里分配。堆逻辑上分为新生代和老年代（见 GC 专题）。

### 元空间（Metaspace）

JDK 8 之前方法区由**永久代（PermGen）**实现（在堆内，有上限）；JDK 8 起改为**元空间**，使用**本地内存**，默认上限由物理内存决定，可通过 `-XX:MaxMetaspaceSize` 限制。

## 对象分配位置

```text
new Object()
  → 优先在 TLAB（线程本地分配缓冲）分配
  → 放不下？在 Eden 分配
  → 大对象？直接进老年代
  → 满足逃逸分析？可能栈上分配（标量替换）
```

## 常见内存参数

| 参数 | 作用 |
| --- | --- |
| `-Xms` | 堆初始大小（建议与 -Xmx 相同） |
| `-Xmx` | 堆最大大小 |
| `-Xmn` | 新生代大小 |
| `-Xss` | 每个线程栈大小（默认 1MB，Linux x64） |
| `-XX:MetaspaceSize` | 元空间初始阈值 |
| `-XX:MaxMetaspaceSize` | 元空间上限 |
| `-XX:MaxDirectMemorySize` | 直接内存上限（默认等于 -Xmx） |

## 查看当前 JVM 内存配置

```shell
java -XshowSettings:vm -version
```

输出示例：

```text
VM settings:
    Max. Heap Size (Estimated): 3.50G
    Ergonomics Machine Class: server
    Using VM: OpenJDK 64-Bit Server VM
```

查看运行中进程的堆配置：

```shell
jcmd <pid> VM.flags
jcmd <pid> GC.heap_info
```

## 易错点

::: danger 常见错误
1. 把元空间当成“堆的一部分”：元空间用本地内存，`-Xmx` 管不到它；类太多（反射/动态代理）可能 `Metaspace OOM`。
2. `-Xms` 与 `-Xmx` 不一致：启动时堆小，运行中频繁扩容收缩，影响性能；生产建议两者相等。
3. 栈大小随意调大：每个线程都占一块栈内存，`-Xss` 过大等于浪费内存，线程多时反而先 OOM。
4. 只关注堆 OOM：线程创建失败（`unable to create native thread`）、直接内存 OOM 也都属于内存问题。
5. 把静态变量当“不占内存”：静态引用会让对象长期存活，是内存泄漏的常见来源。
:::

## 验证方式

1. 运行 `StackOverflowDemo`，观察异常抛出速度与递归深度。
2. 执行 `java -XshowSettings:vm -version`，确认堆大小与 GC 相关默认值。
3. 用 `jcmd <pid> GC.heap_info` 观察运行中进程的堆与元空间使用。

## 参考资料

- JVM 规范（运行时数据区）：https://docs.oracle.com/javase/specs/jvms/se25/html/jvms-2.html
- HotSpot 内存管理白皮书：https://www.oracle.com/technetwork/java/javase/memorymanagement-whitepaper-2155844.html
- jcmd 工具文档：https://docs.oracle.com/en/java/javase/25/docs/specs/man/jcmd.html
