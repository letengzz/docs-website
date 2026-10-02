# 集合框架

Java 集合框架（Java Collections Framework）是标准库中用于存储和操作对象组的接口与实现体系，覆盖 List、Set、Map、队列等常用数据结构。

- [集合框架总览](Overview/index.md)
- [List 接口与实现](List/index.md)
- [Set 接口与实现](Set/index.md)
- [Map 接口与实现](Map/index.md)
- [迭代与遍历](Iteration/index.md)
- [排序与比较器](SortCompare/index.md)
- [并发集合](Concurrent/index.md)
- [源码要点](Source/index.md)
- [常见问题与最佳实践](FAQ/index.md)

## 相关专题

- [高性能 Java](../../../HighPerformanceJava/index.md)：集合在**真实负载**下的开销——自动装箱与拆箱的分配成本、扩容时的数组拷贝、`hashCode` 分布对桶冲突的影响，以及这些开销怎么用 JMH 测出来。本专题讲**复杂度与用法**（O(1) 与 O(log n) 的区别、怎么选容器），那里讲同样一次操作实际花了多少纳秒、省在哪儿
