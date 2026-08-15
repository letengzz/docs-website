# 源码要点

面试和调优都绕不开集合源码。这一篇只讲最核心、最稳定的三个点：**ArrayList 扩容、HashMap 结构与树化、fail-fast 机制**，并给出关键结论和验证方法。

::: info 版本说明
以下结论基于 JDK 8~25 的长期稳定实现（HashMap 数组+链表+红黑树的结构自 JDK 8 起未变）。
:::

## ArrayList：动态扩容

关键事实（`ArrayList.java`）：

1. 默认初始容量 **10**（懒初始化：第一次 add 才创建数组）。
2. 扩容为旧容量的 **1.5 倍**：`int newCapacity = oldCapacity + (oldCapacity >> 1)`。
3. 扩容时 `Arrays.copyOf` 把旧数组整体拷贝到新数组，**O(n)**。
4. 最大容量上限 `Integer.MAX_VALUE - 8`（预留对象头空间）。

```java [Collection/Source/ArrayListGrowDemo.java]
import java.util.ArrayList;

public class ArrayListGrowDemo {
    public static void main(String[] args) {
        ArrayList<Integer> list = new ArrayList<>();   // 默认容量 10
        for (int i = 0; i < 11; i++) {
            list.add(i);
        }                                              // 第 11 个触发扩容到 15
        System.out.println(list.size());
    }
}
```

::: tip 实践结论
能预估大小时直接 `new ArrayList<>(1000)`，避免多次扩容拷贝；但“预分配过大”会浪费内存，按数量级估算即可。
:::

## HashMap：数组 + 链表 + 红黑树

关键事实（`HashMap.java`）：

| 参数 | 默认值 | 含义 |
| --- | --- | --- |
| `DEFAULT_INITIAL_CAPACITY` | 16 | 初始桶数量 |
| `DEFAULT_LOAD_FACTOR` | 0.75 | 负载因子 |
| `TREEIFY_THRESHOLD` | 8 | 链表长度 ≥ 8 时尝试树化 |
| `UNTREEIFY_THRESHOLD` | 6 | 红黑树节点 < 6 时退化为链表 |
| `MIN_TREEIFY_CAPACITY` | 64 | 桶数 < 64 时先扩容而不是树化 |

```text
put(key, value)
  → hash(key) 扰动
  → 定位桶：tab[(n - 1) & hash]
  → 桶为空：直接放 Node
  → 桶是链表：尾插，长度 ≥ 8 且容量 ≥ 64 → 转红黑树
  → 桶是红黑树：树插
  → 元素个数 > 容量 × 0.75 → resize 翻倍
```

几个稳定结论：

1. **扩容是翻倍**（`newCap = oldCap << 1`），旧元素要么留在原桶，要么移到 `原位置 + 旧容量`。
2. 哈希扰动 `(h = key.hashCode()) ^ (h >>> 16)`，让高位参与定位，降低碰撞。
3. 负载因子 0.75 是时间与空间的折中；调低更省哈希冲突但更费内存。
4. JDK 8 之前链表**头插**，并发扩容会成环；JDK 8+ 改**尾插**，缓解死循环，但 HashMap 仍非线程安全。

```java [Collection/Source/HashMapCapacityDemo.java]
import java.lang.reflect.Field;
import java.util.HashMap;

public class HashMapCapacityDemo {
    public static void main(String[] args) throws Exception {
        HashMap<String, String> map = new HashMap<>();
        Field table = HashMap.class.getDeclaredField("table");
        table.setAccessible(true);

        for (int i = 0; i < 12; i++) {
            map.put("k" + i, "v");
        }
        Object[] buckets = (Object[]) table.get(map);
        System.out.println("桶数量: " + buckets.length);  // 16
    }
}
```

::: warning 说明
反射查看桶数量仅供学习，生产代码不要依赖内部结构；`table` 字段在 JDK 17+ 强封装下默认不可访问，可加 `--add-opens` 参数或在较旧 JDK 上运行。
:::

## HashSet：HashMap 的马甲

`HashSet` 内部就是 `HashMap`，元素作为 key，所有 value 指向同一个静态空对象 `PRESENT`。所以 HashSet 去重规则 = HashMap key 的规则 = `hashCode` + `equals`。

## TreeMap / TreeSet：红黑树

- TreeMap 是红黑树（自平衡二叉查找树），插入/删除/查找都是 `O(log n)`。
- 比较规则由 `Comparable` 或构造传入的 `Comparator` 决定。
- 遍历按 key 升序，支持 `subMap`、`headMap`、`tailMap` 等范围视图。

## fail-fast：modCount

ArrayList、HashMap 等内部维护 `modCount`（结构修改次数）。迭代器创建时记录 `expectedModCount`，每次 `next()` 校验；被其他途径修改后立刻抛 `ConcurrentModificationException`。

```text
iterator.next()
  → checkForComodification()
  → modCount != expectedModCount ? 抛异常 : 继续
```

这是**检测机制而非同步机制**：多线程场景要使用并发集合，而不是“靠异常兜底”。

## 常见面试追问

1. HashMap 为什么容量是 2 的幂？→ 为了 `(n - 1) & hash` 替代取模，且扩容时元素位置计算简单。
2. 为什么树化阈值是 8？→ 泊松分布下链表长度到 8 的概率极低，兼顾退化成本。
3. 为什么负载因子是 0.75？→ 时间与空间的折中（官方注释给出的经验值）。
4. JDK 7 的 HashMap 并发死循环怎么来的？→ 头插法在并发扩容时形成环；JDK 8 改尾插，但并发安全问题依旧存在。
5. `String` 为什么适合做 key？→ 不可变 + 正确重写 hashCode/equals，哈希值稳定。

## 易错点

::: danger 常见错误
1. 把 HashMap 扩容机制当成“线程安全”的挡箭牌：JDK 8 尾插只是缓解死循环，数据丢失/覆盖依旧可能。
2. 用可变对象做 key 后修改内容：哈希值变化，`get` 找不到。
3. 以为树化阈值到了 8 就一定转红黑树：桶数不足 64 时先扩容。
4. 用 `HashMap` 的迭代器做“快速失败”保护：异常只能暴露问题，不能作为正确性保证。
5. 面试背结论不验证：建议按本页源码要点自己写 demo 验证扩容、树化等行为。
:::

## 验证方式

1. 运行 `ArrayListGrowDemo`，配合 debugger 观察 elementData 容量变化。
2. 运行 `HashMapCapacityDemo`（JDK 8~16 直接跑），确认 12 个元素时桶数为 16。
3. 在遍历中通过另一个线程修改 HashMap，观察 `ConcurrentModificationException`；换成 `ConcurrentHashMap` 后异常消失但结果弱一致。

## 参考资料

- ArrayList 源码：https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/util/ArrayList.java
- HashMap 源码：https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/util/HashMap.java
- Oracle 官方集合实现说明：https://docs.oracle.com/javase/tutorial/collections/implementations/
