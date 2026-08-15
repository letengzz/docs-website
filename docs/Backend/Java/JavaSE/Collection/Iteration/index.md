# 迭代与遍历

遍历是集合使用频率最高的操作。这一篇把 `for-each`、`Iterator`、`ListIterator`、`removeIf`、Stream 五种方式讲清楚，并重点解决“**遍历时删除元素**”这个高频报错点。

## 五种遍历方式

```java [Collection/Iteration/ListTraverseDemo.java]
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public class ListTraverseDemo {
    public static void main(String[] args) {
        List<String> list = new ArrayList<>(java.util.List.of("A", "B", "C"));

        // 1. 普通 for（仅 List 可用）
        for (int i = 0; i < list.size(); i++) {
            System.out.print(list.get(i));
        }

        // 2. 增强 for（本质是 Iterator 语法糖）
        for (String s : list) {
            System.out.print(s);
        }

        // 3. Iterator 显式遍历
        Iterator<String> it = list.iterator();
        while (it.hasNext()) {
            System.out.print(it.next());
        }

        // 4. forEach 方法（Java 8+）
        list.forEach(System.out::print);

        // 5. Stream（可继续链式操作）
        list.stream().forEach(System.out::print);
    }
}
```

输出（连续打印三遍）：

```text
ABCABCABCABCABC
```

## Iterator 的工作机制

```text
hasNext() → next() → hasNext() → next() → ...
```

- `hasNext()`：判断是否还有下一个。
- `next()`：返回下一个元素并移动游标。
- `remove()`：删除**刚返回的元素**，是遍历中安全删除的入口。

## 遍历时删除：正确与错误

::: danger 经典报错
在增强 for 循环里调用 `list.remove(...)`，第二次循环时抛出：

```text
java.util.ConcurrentModificationException
```

原因：增强 for 使用迭代器遍历，`remove` 修改了 `modCount`，迭代器检测到结构变化后立即失败（fail-fast）。
:::

正确的三种删除方式：

```java [Collection/Iteration/RemoveWhileIteratingDemo.java]
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public class RemoveWhileIteratingDemo {
    public static void main(String[] args) {
        // 方式1：Iterator.remove（Java 8 前通用）
        List<String> list1 = new ArrayList<>(java.util.List.of("A", "B", "C"));
        Iterator<String> it = list1.iterator();
        while (it.hasNext()) {
            if (it.next().equals("B")) {
                it.remove();
            }
        }
        System.out.println(list1);   // [A, C]

        // 方式2：removeIf（Java 8+，最推荐）
        List<String> list2 = new ArrayList<>(java.util.List.of("A", "B", "C"));
        list2.removeIf(s -> s.equals("B"));
        System.out.println(list2);   // [A, C]

        // 方式3：先收集后删除
        List<String> list3 = new ArrayList<>(java.util.List.of("A", "B", "C"));
        List<String> toRemove = new ArrayList<>();
        for (String s : list3) {
            if (s.equals("B")) {
                toRemove.add(s);
            }
        }
        list3.removeAll(toRemove);
        System.out.println(list3);   // [A, C]
    }
}
```

输出：

```text
[A, C]
[A, C]
[A, C]
```

## ListIterator：双向遍历

ListIterator 支持向前遍历和修改元素，仅 List 可用：

```java [Collection/Iteration/ListIteratorDemo.java]
import java.util.ArrayList;
import java.util.List;
import java.util.ListIterator;

public class ListIteratorDemo {
    public static void main(String[] args) {
        List<String> list = new ArrayList<>(java.util.List.of("A", "B", "C"));
        ListIterator<String> it = list.listIterator(list.size());
        while (it.hasPrevious()) {
            System.out.print(it.previous());   // CBA
        }
    }
}
```

## 遍历 Map 的三种视图

```java [Collection/Iteration/MapIterationDemo.java]
import java.util.HashMap;
import java.util.Map;

public class MapIterationDemo {
    public static void main(String[] args) {
        Map<String, Integer> map = new HashMap<>();
        map.put("a", 1);
        map.put("b", 2);

        map.forEach((k, v) -> System.out.println(k + "=" + v));

        map.entrySet().removeIf(e -> e.getValue() == 1);  // 安全删除
        System.out.println(map);   // {b=2}
    }
}
```

## fail-fast 与弱一致性

| 集合 | 遍历时并发修改 | 说明 |
| --- | --- | --- |
| ArrayList / HashMap 等 | 抛 `ConcurrentModificationException` | fail-fast：快速失败 |
| ConcurrentHashMap | 不抛异常，但结果可能不包含最新修改 | 弱一致迭代 |
| CopyOnWriteArrayList | 遍历的是快照，修改不影响当前遍历 | 写时复制 |

## 易错点

::: danger 常见错误
1. 遍历时用 `list.remove(i)` 按索引删除：删除后索引前移，会跳过元素；要么倒序遍历，要么用迭代器。
2. 在 `forEach` 方法中调用 `list.remove`：同样抛 `ConcurrentModificationException`。
3. 迭代器用完不关心：Iterator 是一次性的，不能复用。
4. Map 遍历时通过 `map.get(key)` 取值：多一次哈希查找；直接遍历 `entrySet` 更高效。
5. 多线程遍历 ArrayList：即使没抛异常也可能读到不一致数据，使用并发集合（见「并发集合」篇）。
:::

## 验证方式

1. 先跑一段“增强 for 中 remove”的代码，确认抛出 `ConcurrentModificationException`。
2. 改用 `removeIf` 后重新运行，确认输出 `[A, C]`。
3. 用 `ListIterator` 倒序遍历，确认输出 `CBA`。
4. 在 `HashMap` 上执行 `entrySet().removeIf`，确认安全删除。

## 参考资料

- Iterator 接口文档：https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Iterator.html
- ListIterator 接口文档：https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/ListIterator.html
- Collection.removeIf 文档：https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Collection.html#removeIf(java.util.function.Predicate)
