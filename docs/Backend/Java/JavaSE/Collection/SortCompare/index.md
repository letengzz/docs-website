# 排序与比较器

排序是集合的标配能力。Java 提供两条比较规则：**Comparable（自然顺序）** 和 **Comparator（比较器）**，掌握它们的区别和链式写法，才能正确排序自定义对象。

## Comparable 与 Comparator

| 维度 | Comparable | Comparator |
| --- | --- | --- |
| 所在位置 | 类自身实现 | 外部独立实现 |
| 方法 | `compareTo(T)` | `compare(T, T)` |
| 改变目标类 | 需要 | 不需要 |
| 排序规则 | 一种自然顺序 | 可以多种 |
| 典型场景 | 实体类默认排序 | 按不同字段临时排序 |

```text
Comparable：String、Integer 等自带自然顺序
Comparator：Collections.sort(list, comparator) / list.sort(comparator)
```

## 自然顺序：Comparable

```java [Collection/SortCompare/Person.java]
public class Person implements Comparable<Person> {
    private final String name;
    private final int age;

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public String name() { return name; }
    public int age() { return age; }

    @Override
    public int compareTo(Person other) {
        return Integer.compare(this.age, other.age);
    }

    @Override
    public String toString() {
        return name + "(" + age + ")";
    }
}
```

```java [Collection/SortCompare/ComparableDemo.java]
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class ComparableDemo {
    public static void main(String[] args) {
        List<Person> people = new ArrayList<>(List.of(
            new Person("张三", 25),
            new Person("李四", 20),
            new Person("王五", 30)));

        Collections.sort(people);          // 按 compareTo 排序
        System.out.println(people);        // [李四(20), 张三(25), 王五(30)]
    }
}
```

输出：

```text
[李四(20), 张三(25), 王五(30)]
```

## 外部比较器：Comparator

```java [Collection/SortCompare/ComparatorDemo.java]
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public class ComparatorDemo {
    public static void main(String[] args) {
        List<Person> people = new ArrayList<>(List.of(
            new Person("张三", 25),
            new Person("李四", 20),
            new Person("王五", 25)));

        // 按年龄升序，再按姓名升序
        people.sort(Comparator.comparingInt(Person::age)
                              .thenComparing(Person::name));
        System.out.println(people);   // [李四(20), 王五(25), 张三(25)]

        // 按年龄降序
        people.sort(Comparator.comparingInt(Person::age).reversed());
        System.out.println(people);   // [王五(25), 张三(25), 李四(20)]
    }
}
```

输出：

```text
[李四(20), 王五(25), 张三(25)]
[王五(25), 张三(25), 李四(20)]
```

## Comparator 常用工厂方法

| 方法 | 作用 |
| --- | --- |
| `comparing(Function)` | 按提取的键排序 |
| `comparingInt` / `comparingLong` / `comparingDouble` | 按基本类型键排序，避免装箱 |
| `thenComparing(...)` | 多级排序 |
| `reversed()` | 反转顺序 |
| `nullsFirst(...)` / `nullsLast(...)` | null 值处理 |
| `naturalOrder()` / `reverseOrder()` | 自然顺序/反序 |

## 排序方法对比

```java [Collection/SortCompare/SortMethodsDemo.java]
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public class SortMethodsDemo {
    public static void main(String[] args) {
        List<Integer> list = new ArrayList<>(List.of(5, 2, 8, 1, 9));

        list.sort(null);                  // 自然顺序（Java 8+，推荐）
        System.out.println(list);         // [1, 2, 5, 8, 9]

        Collections.sort(list);           // 老写法，效果相同
        System.out.println(list);

        int[] array = {5, 2, 8, 1, 9};
        Arrays.sort(array);               // 数组排序
        System.out.println(Arrays.toString(array));  // [1, 2, 5, 8, 9]
    }
}
```

## 排序算法：稳定的 TimSort

- 对象数组/集合排序使用 **TimSort**（归并 + 插入结合），**稳定**：相等元素保持原相对顺序。
- `Arrays.sort` 对基本类型数组使用双轴快排（Dual-Pivot Quicksort），**不稳定**，但基本类型没有“相等顺序”概念。

## TreeSet / TreeMap 中的比较器

```java [Collection/SortCompare/TreeMapComparatorDemo.java]
import java.util.TreeMap;

public class TreeMapComparatorDemo {
    public static void main(String[] args) {
        TreeMap<Person, String> map = new TreeMap<>(
            java.util.Comparator.comparingInt(Person::age));
        map.put(new Person("张三", 25), "a");
        map.put(new Person("李四", 20), "b");
        System.out.println(map.firstKey());   // 李四(20)
    }
}
```

## 易错点

::: danger 常见错误
1. 用 `return a - b` 比较整数：可能整数溢出（如 `Integer.MAX_VALUE - (-1)`），必须用 `Integer.compare`。
2. 比较器返回 0 但对象业务上不同：TreeSet/TreeMap 会判定为同一个元素，导致数据丢失。
3. 比较规则不具备传递性：排序结果不稳定甚至抛 `IllegalArgumentException: Comparison method violates its general contract!`。
4. `Collections.sort` 与 `list.sort` 混用旧新 API：结果一样，但新代码统一用 `list.sort`。
5. 忘记 null 处理：`Comparator.comparing(Person::name)` 遇到 name 为 null 会 NPE，用 `nullsLast` 或自定义逻辑。
:::

## 验证方式

1. 运行 `ComparableDemo`、`ComparatorDemo`，对照输出确认多级排序。
2. 把 `Integer.compare(age, other.age)` 改成 `age - other.age`，用 `Integer.MIN_VALUE` 场景验证溢出风险。
3. 给 TreeMap 传一个返回 0 的比较器，确认重复键被覆盖。

## 参考资料

- 用 Stream 排序与分组：[Collectors 收集器详解](../../FunctionalProgramming/Collectors/index.md)
- Comparable 文档：https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Comparable.html
- Comparator 文档：https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Comparator.html
- List.sort 文档：https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/List.html#sort(java.util.Comparator)
