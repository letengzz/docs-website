# Set 接口与实现

`Set` 是**不可重复**元素的集合体系，核心价值是去重。实现上 HashSet 依赖 `hashCode()` / `equals()`，TreeSet 依赖 `Comparable` / `Comparator`。

## Set 的特点

1. **不可重复**：重复元素会被忽略。
2. **无索引**：不能 `get(index)`，只能遍历或 `contains`。
3. **顺序语义由实现决定**：HashSet 无序、LinkedHashSet 保持插入顺序、TreeSet 按规则排序。

```text
Set
├── HashSet          哈希表，查找 O(1)
├── LinkedHashSet    哈希 + 链表，保持插入顺序
├── TreeSet          红黑树，按自然顺序/比较器排序
└── EnumSet          枚举专用，效率极高
```

## HashSet：哈希去重

HashSet 底层就是 HashMap（元素作为 key），`contains`、`add` 都是 `O(1)`。

```java [Collection/Set/HashSetDemo.java]
import java.util.HashSet;
import java.util.Set;

public class HashSetDemo {
    public static void main(String[] args) {
        Set<String> set = new HashSet<>();
        set.add("苹果");
        set.add("香蕉");
        set.add("苹果");        // 重复，被忽略
        set.add(null);          // HashSet 允许 null
        System.out.println(set.size());          // 3
        System.out.println(set.contains("苹果")); // true
        set.remove("香蕉");
        System.out.println(set); // [null, 苹果]（顺序不保证）
    }
}
```

输出（顺序可能不同）：

```text
3
true
[null, 苹果]
```

## 去重的依据：equals 与 hashCode

自定义对象放入 HashSet 时，必须同时重写 `equals` 和 `hashCode`，且满足契约：**相等的对象 hashCode 必须相等**。

```java [Collection/Set/StudentSetDemo.java]
import java.util.HashSet;
import java.util.Objects;
import java.util.Set;

public class StudentSetDemo {
    public static void main(String[] args) {
        Set<Student> students = new HashSet<>();
        students.add(new Student("张三", 20));
        students.add(new Student("李四", 21));
        students.add(new Student("张三", 20));   // 内容相同，不重复
        System.out.println(students.size());      // 2
    }
}

class Student {
    private final String name;
    private final int age;

    public Student(String name, int age) {
        this.name = name;
        this.age = age;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Student other)) return false;
        return age == other.age && name.equals(other.name);
    }

    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }
}
```

输出：

```text
2
```

只重写 `equals` 不重写 `hashCode` 时，两个内容相同的对象哈希值不同，会被当成两个元素——这是最经典的坑。

## LinkedHashSet：去重且保序

```java [Collection/Set/LinkedHashSetDemo.java]
import java.util.LinkedHashSet;

public class LinkedHashSetDemo {
    public static void main(String[] args) {
        LinkedHashSet<String> set = new LinkedHashSet<>();
        set.add("第三个");
        set.add("第一个");
        set.add("第二个");
        set.add("第一个");   // 重复，忽略
        System.out.println(set);  // [第三个, 第一个, 第二个]
    }
}
```

输出：

```text
[第三个, 第一个, 第二个]
```

## TreeSet：有序去重

TreeSet 底层是红黑树，元素按自然顺序或指定比较器排序，提供范围查询能力。

```java [Collection/Set/TreeSetDemo.java]
import java.util.TreeSet;

public class TreeSetDemo {
    public static void main(String[] args) {
        TreeSet<Integer> set = new TreeSet<>();
        set.add(5);
        set.add(2);
        set.add(8);
        set.add(1);
        System.out.println(set);                    // [1, 2, 5, 8]
        System.out.println(set.first());            // 1
        System.out.println(set.last());             // 8
        System.out.println(set.lower(5));           // 2
        System.out.println(set.higher(5));          // 8
        System.out.println(set.subSet(2, true, 8, true)); // [2, 5, 8]
    }
}
```

输出：

```text
[1, 2, 5, 8]
1
8
2
8
[2, 5, 8]
```

自定义对象进 TreeSet，要么实现 `Comparable`，要么传入 `Comparator`：

```java [Collection/Set/TreeSetComparatorDemo.java]
import java.util.TreeSet;

public class TreeSetComparatorDemo {
    public static void main(String[] args) {
        TreeSet<Student2> set = new TreeSet<>(
            (a, b) -> Integer.compare(a.age, b.age));
        set.add(new Student2("张三", 20));
        set.add(new Student2("李四", 19));
        set.add(new Student2("王五", 20));  // 年龄相同，比较器返回 0 → 视为重复
        System.out.println(set.size());      // 2
    }
}

class Student2 {
    String name;
    int age;

    Student2(String name, int age) {
        this.name = name;
        this.age = age;
    }
}
```

输出：

```text
2
```

注意：比较器返回 0 会被 TreeSet 判定为“同一个元素”，所以比较规则必须与“业务唯一性”一致。

## 集合运算

```java [Collection/Set/SetOperationDemo.java]
import java.util.HashSet;
import java.util.Set;

public class SetOperationDemo {
    public static void main(String[] args) {
        Set<String> a = new HashSet<>(java.util.Set.of("A", "B", "C"));
        Set<String> b = new HashSet<>(java.util.Set.of("B", "C", "D"));

        Set<String> union = new HashSet<>(a);
        union.addAll(b);
        System.out.println("并集: " + union);           // [A, B, C, D]

        Set<String> intersection = new HashSet<>(a);
        intersection.retainAll(b);
        System.out.println("交集: " + intersection);    // [B, C]

        Set<String> diff = new HashSet<>(a);
        diff.removeAll(b);
        System.out.println("差集: " + diff);            // [A]
    }
}
```

## 易错点

::: danger 常见错误
1. 只重写 `equals` 不重写 `hashCode`：HashSet 去重失效。
2. 把可变对象放进 HashSet 后修改其字段：哈希值变化，导致 `contains` 找不到、元素无法删除。
3. 元素没有实现 `Comparable` 也没传 Comparator 就放进 TreeSet：运行期抛 `ClassCastException`。
4. TreeSet 比较器把“排序相等”和“业务相等”混为一谈：按年龄排序时，同龄不同人会被去重。
5. 以为 HashSet 有顺序：遍历顺序不稳定，需要顺序用 LinkedHashSet。
:::

## 验证方式

1. 运行 `StudentSetDemo`，确认 size 为 2；删除 `hashCode` 重写后重新运行，观察 size 变为 3。
2. 运行 `TreeSetComparatorDemo`，确认同龄人被去重。
3. 用 `HashSet` 和 `LinkedHashSet` 各插入相同数据，对比输出顺序差异。

## 参考资料

- Set 接口文档：https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Set.html
- HashSet 文档：https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/HashSet.html
- TreeSet 文档：https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/TreeSet.html
