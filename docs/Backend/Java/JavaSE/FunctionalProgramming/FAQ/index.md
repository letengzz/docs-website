# 常见问题与最佳实践

汇总 Java 函数式编程中最常遇到的疑问与坑，覆盖 Stream 使用、性能、并行、Optional 与工程实践，方便快速查阅。

## 基础类

### Lambda 和匿名内部类有什么区别？

| 维度 | Lambda | 匿名内部类 |
| --- | --- | --- |
| 要求 | 必须是函数式接口 | 任意接口/类 |
| `this` | 外部类实例 | 匿名类自身 |
| 字节码 | invokedynamic 动态生成 | 编译期生成 class |
| 局部变量捕获 | effectively final | 同样限制 |

### 什么时候用方法引用？

方法引用是 Lambda 的**简化形式**，当 Lambda 体就是「调用某个已有方法」时使用：

```java
list.forEach(System.out::println);       // 而不是 s -> System.out.println(s)
list.stream().map(String::toUpperCase);  // 而不是 s -> s.toUpperCase()
list.sort(Integer::compareTo);
```

## Stream 类

### Stream 为什么只能消费一次？

Stream 设计为一次性管线：终端操作执行后流水线即关闭。复用数据请：

1. 重新从数据源创建 Stream；
2. 或先把结果 `toList()` 保存。

### `toList()` 和 `collect(Collectors.toList())` 怎么选？

```java
List<String> a = list.stream().toList();                  // Java 16+，不可变
List<String> b = list.stream().collect(Collectors.toList()); // 可变 ArrayList
```

- 只要「读」→ `toList()`，更简洁且不可变安全；
- 需要后续 `add`/`remove` → `collect(Collectors.toList())` 或 `toCollection(ArrayList::new)`。

### forEach 和 for 循环哪个好？

`forEach` 适合「对每个元素做独立处理」；涉及**外部可变状态、break/continue、索引**时传统 for 更直观。不要为了「看起来函数式」而硬用 forEach。

### 如何调试 Stream 流水线？

1. 用 `peek()` 打印每个阶段：

```java
list.stream()
    .peek(x -> System.out.println("filter 前: " + x))
    .filter(...)
    .peek(x -> System.out.println("filter 后: " + x))
    .toList();
```

2. 用 IDE 的 Stream 调试器（IntelliJ 支持逐步查看元素流转）；
3. 复杂逻辑拆成命名方法，便于单独测试。

## 性能类

### Stream 比 for 循环慢吗？

现代 JVM 下 Stream 与 for 循环性能差距很小（通常 5%~20%），且**可读性与并行化收益**更值得关注：

- 顺序流：差距可忽略；
- 并行流（大数据）：可能更快；
- 极端性能敏感（高频热点）：手工循环 + 数组可能最优，但先测量再优化。

### 并行流什么时候用？

满足全部条件才用：

1. 数据量大（建议十万级以上）；
2. 元素处理无共享可变状态；
3. 顺序无关；
4. 单个元素处理成本较高。

不符合就串行，避免线程调度开销。

### 如何避免装箱拆箱开销？

数值场景用基本类型流：

```java
int sum = list.stream()
        .mapToInt(Integer::intValue)   // IntStream
        .sum();
```

收集回对象用 `boxed()`：

```java
List<Integer> list = IntStream.range(1, 10).boxed().toList();
```

## Optional 类

### Optional 能不能做字段？

**不建议**：Optional 不可序列化、语义混乱（null 与 empty 并存）、数据库映射困难。字段用 null/默认值，方法返回值才用 Optional。

### `orElse` 和 `orElseGet` 怎么选？

```java
String v1 = opt.orElse(expensiveDefault());      // 先执行 expensiveDefault()
String v2 = opt.orElseGet(() -> expensiveDefault());  // 为空才执行
```

默认值计算廉价用 `orElse`，昂贵/有副作用用 `orElseGet`。

### `isPresent() + get()` 为什么被诟病？

它把 Optional 用成了「可以拿 null 的盒子」，代码退化为命令式判断。链式写法更安全：

```java
// 差：ifPresent 判断 + get
if (opt.isPresent()) {
    String v = opt.get();
}

// 好：map + orElse 链式
String v = opt.map(String::trim).orElse("默认");
```

## 收集器类

### `groupingBy` 结果顺序不稳定怎么办？

传入 `LinkedHashMap::new` 保持插入顺序：

```java
Map<String, Long> map = list.stream()
        .collect(Collectors.groupingBy(
                key, LinkedHashMap::new, Collectors.counting()));
```

### `toMap` 重复键报错怎么处理？

```java
Map<String, String> map = list.stream()
        .collect(Collectors.toMap(
                s -> s,
                s -> s.toUpperCase(),
                (oldV, newV) -> newV));   // 冲突保留后者
```

## 框架协作类

### MyBatis/Spring 中能用 Stream 吗？

可以。MyBatis 的 `selectList` 返回 List 可直接 `.stream()`；Spring Data JPA 支持返回 `Stream<T>`（注意用完关闭）。大数据量分页查询优先数据库层完成，不要在内存里全量过滤。

### 函数式风格与现有 for 代码怎么共存？

渐进式替换：新代码优先 Stream；重构时从「过滤 + 转换 + 汇总」这类纯数据操作开始，不要为了重构而重构有复杂状态的代码。

## 最佳实践清单

::: tip 函数式代码检查清单
1. 是否有终端操作？（没有则不执行）
2. 无限流是否 `limit`？
3. 并行流是否满足条件（大数据 + 无共享状态）？
4. `toMap`/`groupingBy` 是否处理了键冲突与顺序？
5. Optional 是否只在返回值使用、是否避免了 `get()`？
6. 数值统计是否用了基本类型流 / `summaryStatistics`？
7. 收集结果是否需要可变集合（`toList()` 不可变）？
8. 复杂逻辑是否拆成了可单测的纯函数？
:::

## 参考资料

- [Stream API 文档](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/stream/Stream.html)
- [Collectors API 文档](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/stream/Collectors.html)
- [Optional API 文档](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Optional.html)
- [Java 8 函数式编程官方教程](https://docs.oracle.com/javase/tutorial/java/javaOO/lambdaexpressions.html)
