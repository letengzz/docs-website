# Map 接口与实现

`Map` 是**键值对（key-value）**存储体系，key 唯一、value 可重复。它不属于 Collection，但同样是集合框架的核心组成部分，日常开发中使用频率最高。

## Map 的特点

1. 每个 key 最多映射一个 value，重复 put 会**覆盖旧值**。
2. 按 key 查找，HashMap 查找 `O(1)`。
3. 遍历方式多样：keySet、values、entrySet。

```text
Map
├── HashMap              哈希表，通用首选
├── LinkedHashMap        哈希 + 链表，保持插入/访问顺序
├── TreeMap              红黑树，按键排序
├── Hashtable            线程安全但性能差（遗留类）
└── ConcurrentHashMap    高并发线程安全（见并发集合篇）
```

## HashMap：通用首选

HashMap 底层是“数组 + 链表/红黑树”，允许一个 null key 和多个 null value。

```java [Collection/Map/HashMapDemo.java]
import java.util.HashMap;
import java.util.Map;

public class HashMapDemo {
    public static void main(String[] args) {
        Map<String, Integer> map = new HashMap<>();
        map.put("苹果", 5);
        map.put("香蕉", 3);
        map.put("苹果", 6);           // 覆盖旧值
        map.put(null, 1);             // 允许 null 键
        map.put("葡萄", null);         // 允许 null 值

        System.out.println(map.get("苹果"));              // 6
        System.out.println(map.get("西瓜"));              // null
        System.out.println(map.getOrDefault("西瓜", 0));  // 0
        System.out.println(map.containsKey("香蕉"));      // true
        System.out.println(map.size());                   // 4

        map.remove("香蕉");
        System.out.println(map.containsKey("香蕉"));      // false
    }
}
```

输出：

```text
6
null
0
true
4
false
```

## 常用方法

| 方法 | 作用 |
| --- | --- |
| `put(K, V)` | 放入键值对，返回旧值 |
| `get(Object)` | 按键取值，不存在返回 null |
| `getOrDefault(K, V)` | 不存在时返回默认值 |
| `putIfAbsent(K, V)` | 键不存在才放入（Java 8+） |
| `computeIfAbsent(K, Function)` | 键不存在时计算并放入（Java 8+） |
| `merge(K, V, BiFunction)` | 合并旧值和新值（Java 8+） |
| `remove(K)` / `remove(K, V)` | 删除 / 键值都匹配才删除 |
| `keySet()` / `values()` / `entrySet()` | 三种视图 |
| `forEach(BiConsumer)` | 遍历（Java 8+） |

## compute 系列：避免“先查再写”的竞态

```java [Collection/Map/ComputeDemo.java]
import java.util.HashMap;
import java.util.Map;

public class ComputeDemo {
    public static void main(String[] args) {
        Map<String, Integer> counter = new HashMap<>();

        // 等价于：如果不存在就放 1，存在就 +1
        for (String word : java.util.List.of("a", "b", "a", "c", "a")) {
            counter.merge(word, 1, Integer::sum);
        }
        System.out.println(counter);   // {a=3, b=1, c=1}

        Map<String, String> cache = new HashMap<>();
        cache.computeIfAbsent("key", k -> "value-" + k);
        System.out.println(cache.get("key"));  // value-key
    }
}
```

输出：

```text
{a=3, b=1, c=1}
value-key
```

## LinkedHashMap：保持顺序与 LRU

LinkedHashMap 在哈希表基础上维护双向链表，默认按**插入顺序**遍历；开启 `accessOrder=true` 后按**访问顺序**，可用来实现 LRU 缓存。

```java [Collection/Map/LruCacheDemo.java]
import java.util.LinkedHashMap;
import java.util.Map;

public class LruCacheDemo {
    public static void main(String[] args) {
        LinkedHashMap<String, String> cache =
            new LinkedHashMap<>(16, 0.75f, true) {
                @Override
                protected boolean removeEldestEntry(Map.Entry<String, String> eldest) {
                    return size() > 3;
                }
            };

        cache.put("A", "1");
        cache.put("B", "2");
        cache.put("C", "3");
        cache.get("A");            // 访问 A，A 变为最近使用
        cache.put("D", "4");       // 超过 3 个，淘汰最久未用的 B
        System.out.println(cache); // {C=3, A=1, D=4}
    }
}
```

输出：

```text
{C=3, A=1, D=4}
```

## TreeMap：按键排序

TreeMap 按键的自然顺序或比较器排序，提供 `firstKey`、`lastKey`、`subMap` 等导航方法。

```java [Collection/Map/TreeMapDemo.java]
import java.util.TreeMap;

public class TreeMapDemo {
    public static void main(String[] args) {
        TreeMap<String, Integer> map = new TreeMap<>();
        map.put("orange", 5);
        map.put("apple", 3);
        map.put("banana", 2);

        System.out.println(map);                        // {apple=3, banana=2, orange=5}
        System.out.println(map.firstKey());             // apple
        System.out.println(map.lastKey());              // orange
        System.out.println(map.lowerKey("orange"));     // banana
        System.out.println(map.subMap("a", true, "m", true)); // {apple=3, banana=2}
    }
}
```

输出：

```text
{apple=3, banana=2, orange=5}
apple
orange
banana
{apple=3, banana=2}
```

## Hashtable：遗留类

Hashtable 方法带 `synchronized`，**不允许 null 键值**，性能不如 HashMap；需要线程安全时用 `ConcurrentHashMap`（见「并发集合」篇），不要在新代码中使用 Hashtable。

## 遍历方式

```java [Collection/Map/TraverseDemo.java]
import java.util.HashMap;
import java.util.Map;

public class TraverseDemo {
    public static void main(String[] args) {
        Map<String, Integer> map = new HashMap<>();
        map.put("a", 1);
        map.put("b", 2);

        // 方式1：keySet + get（多一次查找，不推荐）
        for (String key : map.keySet()) {
            System.out.println(key + "=" + map.get(key));
        }

        // 方式2：entrySet（推荐）
        for (Map.Entry<String, Integer> entry : map.entrySet()) {
            System.out.println(entry.getKey() + "=" + entry.getValue());
        }

        // 方式3：forEach（Java 8+，最简洁）
        map.forEach((k, v) -> System.out.println(k + "=" + v));
    }
}
```

## 易错点

::: danger 常见错误
1. 用 `get` 判断键是否存在时，value 本身可能为 null，导致误判；用 `containsKey`。
2. 修改了自定义 key 对象的字段：哈希值变化后 `get` 找不到原条目。
3. `ConcurrentHashMap` 不允许 null 键/值：从 HashMap 迁移并发场景时会踩坑。
4. 遍历时直接 `put`/`remove` 结构：抛 `ConcurrentModificationException`，需要收集后统一处理或用 `entrySet().removeIf`。
5. `Map.of` 传了重复 key 或超过 10 对：编译/运行期异常，注意限制。
:::

## 验证方式

1. 运行 `HashMapDemo`、`ComputeDemo`，对照输出确认。
2. 运行 `LruCacheDemo`，确认访问 A 后淘汰的是 B。
3. 在 `map.get("西瓜")` 返回 null 的场景下，用 `containsKey` 与 `getOrDefault` 各写一版，对比结果。

## 参考资料

- Map 接口文档：https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Map.html
- HashMap 文档：https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/HashMap.html
- TreeMap 文档：https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/TreeMap.html
