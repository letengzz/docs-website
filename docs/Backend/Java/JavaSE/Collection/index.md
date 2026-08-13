# 集合框架

Java 集合框架（Collection Framework）是 Java 标准库中用于存储和操作对象组的一组类和接口。它提供了丰富的数据结构，包括 List、Set、Map 等，可以满足各种不同的需求。

## 集合框架概述

### 集合体系结构

```text
Collection（接口）
├── List（接口） - 有序、可重复
│   ├── ArrayList - 动态数组
│   ├── LinkedList - 双向链表
│   └── Vector - 线程安全的动态数组
│
└── Set（接口） - 无序、不可重复
    ├── HashSet - 基于哈希表
    ├── LinkedHashSet - 保持插入顺序
    └── TreeSet - 基于红黑树（有序）

Map（接口） - 键值对映射
├── HashMap - 基于哈希表
├── LinkedHashMap - 保持插入顺序
├── TreeMap - 基于红黑树（有序）
└── Hashtable - 线程安全的哈希表
```

## List 接口

### ArrayList

ArrayList 是最常用的 List 实现类，基于动态数组实现，支持随机访问。

```java
// Collection/ArrayListDemo.java
import java.util.ArrayList;
import java.util.List;

public class ArrayListDemo {
    public static void main(String[] args) {
        // 创建 ArrayList
        List<String> list = new ArrayList<>();
        List<Integer> numbers = new ArrayList<>(20);  // 指定初始容量
        
        // 添加元素
        list.add("苹果");
        list.add("香蕉");
        list.add("橘子");
        list.add(1, "葡萄");  // 指定位置插入
        System.out.println("添加后: " + list);
        
        // 批量添加
        List<String> moreFruits = java.util.Arrays.asList("西瓜", "哈密瓜");
        list.addAll(moreFruits);
        System.out.println("批量添加后: " + list);
        
        // 获取元素
        System.out.println("第一个元素: " + list.get(0));
        System.out.println("最后一个元素: " + list.get(list.size() - 1));
        
        // 修改元素
        list.set(0, "芒果");
        System.out.println("修改后: " + list);
        
        // 删除元素
        list.remove(0);  // 按索引删除
        list.remove("香蕉");  // 按对象删除
        System.out.println("删除后: " + list);
        
        // 查找元素
        System.out.println("包含 '葡萄': " + list.contains("葡萄"));
        System.out.println("'苹果' 索引: " + list.indexOf("苹果"));
        System.out.println("'香蕉' 索引: " + list.indexOf("香蕉"));  // 不存在返回 -1
        
        // 遍历方式
        System.out.println("\n=== 遍历 ArrayList ===");
        
        // 方式1：普通 for 循环
        for (int i = 0; i < list.size(); i++) {
            System.out.print(list.get(i) + " ");
        }
        System.out.println();
        
        // 方式2：增强 for 循环
        for (String fruit : list) {
            System.out.print(fruit + " ");
        }
        System.out.println();
        
        // 方式3：迭代器
        java.util.Iterator<String> iterator = list.iterator();
        while (iterator.hasNext()) {
            String fruit = iterator.next();
            System.out.print(fruit + " ");
        }
        System.out.println();
        
        // 方式4：forEach 方法
        list.forEach(fruit -> System.out.print(fruit + " "));
        System.out.println();
        
        // 子列表
        List<String> subList = list.subList(0, 2);
        System.out.println("子列表: " + subList);
        
        // 转换为数组
        String[] array = list.toArray(new String[0]);
        System.out.println("转换为数组: " + java.util.Arrays.toString(array));
        
        // 清空
        list.clear();
        System.out.println("清空后大小: " + list.size());
        System.out.println("是否为空: " + list.isEmpty());
    }
}
```

### LinkedList

LinkedList 基于双向链表实现，适合频繁的插入和删除操作。

```java
// Collection/LinkedListDemo.java
import java.util.LinkedList;

public class LinkedListDemo {
    public static void main(String[] args) {
        LinkedList<String> linkedList = new LinkedList<>();
        
        // 添加元素（LinkedList 实现了 Queue 接口）
        linkedList.add("A");
        linkedList.addFirst("First");  // 添加到头部
        linkedList.addLast("Last");    // 添加到尾部
        linkedList.offer("Offer");     // 添加到尾部（Queue 方法）
        linkedList.push("Push");       // 压入头部（Stack 方法）
        
        System.out.println("添加后: " + linkedList);
        
        // 获取元素
        System.out.println("头部元素: " + linkedList.getFirst());
        System.out.println("尾部元素: " + linkedList.getLast());
        System.out.println("peek: " + linkedList.peek());  // 查看头部不删除
        System.out.println("poll: " + linkedList.poll());  // 取出头部并删除
        
        System.out.println("弹出: " + linkedList.pop());   // 从头部弹出
        System.out.println("移除头部: " + linkedList.removeFirst());
        
        System.out.println("操作后: " + linkedList);
        
        // 作为栈使用
        LinkedList<Integer> stack = new LinkedList<>();
        stack.push(1);
        stack.push(2);
        stack.push(3);
        System.out.println("\n栈演示:");
        System.out.println("弹出: " + stack.pop());  // 3
        System.out.println("弹出: " + stack.pop());  // 2
        System.out.println("弹出: " = stack.pop());  // 1
        
        // 作为队列使用
        LinkedList<String> queue = new LinkedList<>();
        queue.offer("任务1");
        queue.offer("任务2");
        queue.offer("任务3");
        System.out.println("\n队列演示:");
        System.out.println("取出: " + queue.poll());
        System.out.println("取出: " + queue.poll());
        System.out.println("取出: " + queue.poll());
    }
}
```

### Vector 与线程安全

```java
// Collection/VectorDemo.java
import java.util.Vector;
import java.util.List;

public class VectorDemo {
    public static void main(String[] args) {
        // Vector 是线程安全的 ArrayList
        Vector<String> vector = new Vector<>();
        
        // 同步方法
        vector.add("元素1");
        vector.add("元素2");
        vector.add("元素3");
        
        synchronized (vector) {
            for (String element : vector) {
                System.out.println(element);
            }
        }
        
        // 线程安全列表的其他实现方式
        List<String> synchronizedList = java.util.Collections.synchronizedList(
            new java.util.ArrayList<>());
        
        // 使用 CopyOnWriteArrayList
        java.util.concurrent.CopyOnWriteArrayList<String> copyOnWriteList = 
            new java.util.concurrent.CopyOnWriteArrayList<>();
        
        // 性能对比
        long startTime = System.currentTimeMillis();
        java.util.ArrayList<Integer> arrayList = new java.util.ArrayList<>();
        for (int i = 0; i < 100000; i++) {
            arrayList.add(i);
        }
        long arrayTime = System.currentTimeMillis() - startTime;
        
        startTime = System.currentTimeMillis();
        Vector<Integer> vectorList = new Vector<>();
        for (int i = 0; i < 100000; i++) {
            vectorList.add(i);
        }
        long vectorTime = System.currentTimeMillis() - startTime;
        
        System.out.println("\n性能对比:");
        System.out.println("ArrayList 耗时: " + arrayTime + "ms");
        System.out.println("Vector 耗时: " + vectorTime + "ms");
    }
}
```

## Set 接口

### HashSet

HashSet 基于 HashMap 实现，元素无序且不可重复。

```java
// Collection/HashSetDemo.java
import java.util.HashSet;
import java.util.Set;

public class HashSetDemo {
    public static void main(String[] args) {
        Set<String> hashSet = new HashSet<>();
        
        // 添加元素
        hashSet.add("苹果");
        hashSet.add("香蕉");
        hashSet.add("橘子");
        hashSet.add("苹果");  // 重复元素，不会添加
        hashSet.add(null);    // 允许 null
        hashSet.add("葡萄");
        
        System.out.println("HashSet 内容: " + hashSet);
        System.out.println("元素数量: " + hashSet.size());
        
        // 查找元素
        System.out.println("包含 '苹果': " + hashSet.contains("苹果"));
        System.out.println("包含 '西瓜': " + hashSet.contains("西瓜"));
        System.out.println("包含 null: " + hashSet.contains(null));
        
        // 删除元素
        hashSet.remove("香蕉");
        hashSet.remove(null);
        System.out.println("删除后: " + hashSet);
        
        // 遍历
        System.out.println("\n遍历 HashSet:");
        for (String element : hashSet) {
            System.out.println(element);
        }
        
        // 迭代器遍历
        java.util.Iterator<String> iterator = hashSet.iterator();
        while (iterator.hasNext()) {
            System.out.println(iterator.next());
        }
        
        // HashSet 的去重原理
        System.out.println("\n=== HashSet 去重演示 ===");
        Set<Student> studentSet = new HashSet<>();
        studentSet.add(new Student("张三", 20));
        studentSet.add(new Student("李四", 21));
        studentSet.add(new Student("张三", 20));  // 根据 hashCode 和 equals 判断重复
        
        System.out.println("学生数量: " + studentSet.size());  // 应该是 2
        
        // 集合运算
        Set<String> set1 = new HashSet<>(java.util.Arrays.asList("A", "B", "C"));
        Set<String> set2 = new HashSet<>(java.util.Arrays.asList("B", "C", "D"));
        
        System.out.println("\n集合运算:");
        System.out.println("set1: " + set1);
        System.out.println("set2: " + set2);
        System.out.println("并集: " + union(set1, set2));
        System.out.println("交集: " + intersection(set1, set2));
        System.out.println("差集(set1-set2): " = difference(set1, set2));
    }
    
    public static <T> Set<T> union(Set<T> set1, Set<T> set2) {
        Set<T> result = new HashSet<>(set1);
        result.addAll(set2);
        return result;
    }
    
    public static <T> Set<T> intersection(Set<T> set1, Set<T> set2) {
        Set<T> result = new HashSet<>(set1);
        result.retainAll(set2);
        return result;
    }
    
    public static <T> Set<T> difference(Set<T> set1, Set<T> set2) {
        Set<T> result = new HashSet<>(set1);
        result.removeAll(set2);
        return result;
    }
}

class Student {
    private String name;
    private int age;
    
    public Student(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Student student = (Student) o;
        return age == student.age && java.util.Objects.equals(name, student.name);
    }
    
    @Override
    public int hashCode() {
        return java.util.Objects.hash(name, age);
    }
    
    @Override
    public String toString() {
        return name + "(" + age + ")";
    }
}
```

### LinkedHashSet 与 TreeSet

```java
// Collection/OrderedSetDemo.java
import java.util.LinkedHashSet;
import java.util.TreeSet;
import java.util.Set;

public class OrderedSetDemo {
    public static void main(String[] args) {
        // LinkedHashSet - 保持插入顺序
        System.out.println("=== LinkedHashSet ===");
        LinkedHashSet<String> linkedHashSet = new LinkedHashSet<>();
        linkedHashSet.add("第三个");
        linkedHashSet.add("第一个");
        linkedHashSet.add("第二个");
        linkedHashSet.add("第一个");  // 重复，不添加
        System.out.println("插入顺序: " + linkedHashSet);
        
        // TreeSet - 自然排序
        System.out.println("\n=== TreeSet ===");
        TreeSet<Integer> treeSet = new TreeSet<>();
        treeSet.add(5);
        treeSet.add(2);
        treeSet.add(8);
        treeSet.add(1);
        treeSet.add(9);
        System.out.println("自然排序: " = treeSet);
        
        // TreeSet 方法
        System.out.println("第一个: " + treeSet.first());
        System.out.println("最后一个: " + treeSet.last());
        System.out.println("小于 5 的最大元素: " + treeSet.lower(5));
        System.out.println("大于 5 的最小元素: " + treeSet.higher(5));
        System.out.println("子集 [2, 8]: " + treeSet.subSet(2, true, 8, true));
        System.out.println("头部 [1, 2]: " = treeSet.headSet(3, true));
        System.out.println("尾部 [5, 9]: " + treeSet.tailSet(5, true));
        
        // TreeSet 自定义排序
        TreeSet<Student> studentSet = new TreeSet<>((s1, s2) -> {
            int ageCompare = Integer.compare(s1.getAge(), s2.getAge());
            if (ageCompare != 0) return ageCompare;
            return s1.getName().compareTo(s2.getName());
        });
        
        studentSet.add(new Student("张三", 20));
        studentSet.add(new Student("李四", 19));
        studentSet.add(new Student("王五", 20));
        System.out.println("\n按年龄排序的学生: " + studentSet);
    }
}

class Student implements Comparable<Student> {
    private String name;
    private int age;
    
    public Student(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public int getAge() { return age; }
    public String getName() { return name; }
    
    // 实现 Comparable 接口
    @Override
    public int compareTo(Student other) {
        int ageCompare = Integer.compare(this.age, other.age);
        if (ageCompare != 0) return ageCompare;
        return this.name.compareTo(other.name);
    }
    
    @Override
    public String toString() {
        return name + "(" + age + ")";
    }
}
```

## Map 接口

### HashMap

HashMap 是最常用的 Map 实现，基于哈希表实现键值对存储。

```java
// Collection/HashMapDemo.java
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

public class HashMapDemo {
    public static void main(String[] args) {
        Map<String, Integer> hashMap = new HashMap<>();
        
        // 添加键值对
        hashMap.put("苹果", 5);
        hashMap.put("香蕉", 3);
        hashMap.put("橘子", 8);
        hashMap.put("苹果", 6);  // 覆盖原有值
        hashMap.put(null, 1);    // 允许 null 键
        hashMap.put("葡萄", null);  // 允许 null 值
        
        System.out.println("HashMap 内容: " + hashMap);
        System.out.println("元素数量: " + hashMap.size());
        
        // 获取值
        System.out.println("苹果的价格: " + hashMap.get("苹果"));
        System.out.println("不存在的键: " + hashMap.get("西瓜"));  // null
        System.out.println("getOrDefault: " + hashMap.getOrDefault("西瓜", 0));
        
        // 判断键值存在
        System.out.println("包含键 '香蕉': " + hashMap.containsKey("香蕉"));
        System.out.println("包含值 8: " + hashMap.containsValue(8));
        
        // 删除
        hashMap.remove("香蕉");
        hashMap.remove("葡萄", null);  // 键值都匹配才删除
        System.out.println("删除后: " + hashMap);
        
        // 遍历方式
        System.out.println("\n=== 遍历 HashMap ===");
        
        // 方式1：遍历键
        System.out.println("遍历键:");
        for (String key : hashMap.keySet()) {
            System.out.println(key + " = " + hashMap.get(key));
        }
        
        // 方式2：遍历值
        System.out.println("遍历值:");
        for (Integer value : hashMap.values()) {
            System.out.println(value);
        }
        
        // 方式3：遍历键值对（推荐）
        System.out.println("遍历键值对:");
        for (Map.Entry<String, Integer> entry : hashMap.entrySet()) {
            System.out.println(entry.getKey() + " -> " + entry.getValue());
        }
        
        // 方式4：forEach 方法
        System.out.println("forEach 遍历:");
        hashMap.forEach((key, value) -> System.out.println(key + " = " + value));
        
        // 批量操作
        System.out.println("\n=== 批量操作 ===");
        Map<String, Integer> map2 = new HashMap<>();
        map2.put("西瓜", 10);
        map2.put("哈密瓜", 15);
        
        hashMap.putAll(map2);
        System.out.println("putAll 后: " + hashMap);
        
        // 替换
        hashMap.replace("苹果", 6, 10);  // 旧值匹配才替换
        hashMap.replace("不存在", 20);   // 键不存在不操作
        System.out.println("replace 后: " + hashMap);
        
        // compute 方法
        hashMap.compute("苹果", (k, v) -> v == null ? 1 : v + 5);
        hashMap.computeIfAbsent("葡萄", k -> 20);
        hashMap.computeIfPresent("橘子", (k, v) -> v + 1);
        System.out.println("compute 后: " + hashMap);
        
        // 清空
        hashMap.clear();
        System.out.println("清空后: " + hashMap.isEmpty());
    }
}
```

### LinkedHashMap 与 TreeMap

```java
// Collection/OrderedMapDemo.java
import java.util.LinkedHashMap;
import java.util.TreeMap;
import java.util.Map;

public class OrderedMapDemo {
    public static void main(String[] args) {
        // LinkedHashMap - 保持插入顺序
        System.out.println("=== LinkedHashMap ===");
        LinkedHashMap<String, Integer> linkedHashMap = new LinkedHashMap<>();
        linkedHashMap.put("third", 3);
        linkedHashMap.put("first", 1);
        linkedHashMap.put("second", 2);
        linkedHashMap.put("first", 10);  // 覆盖，但保持位置
        
        System.out.println("插入顺序: " + linkedHashMap);
        
        // LRU 缓存示例
        LinkedHashMap<String, String> lruCache = new LinkedHashMap<>(5, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry eldest) {
                return size() > 3;
            }
        };
        lruCache.put("A", "1");
        lruCache.put("B", "2");
        lruCache.put("C", "3");
        lruCache.get("A");  // 访问 A
        lruCache.put("D", "4");
        
        System.out.println("LRU 缓存: " + lruCache);  // 淘汰了 B
        
        // TreeMap - 有序
        System.out.println("\n=== TreeMap ===");
        TreeMap<String, Integer> treeMap = new TreeMap<>();
        treeMap.put("orange", 5);
        treeMap.put("apple", 3);
        treeMap.put("banana", 2);
        
        System.out.println("自然排序: " + treeMap);
        System.out.println("第一个键: " + treeMap.firstKey());
        System.out.println("最后一个键: " = treeMap.lastKey());
        System.out.println("小于 'orange' 的最大键: " + treeMap.lowerKey("orange"));
        
        // 子视图
        System.out.println("子Map (a-m): " + treeMap.subMap("a", true, "m", true));
        System.out.println("头部Map: " + treeMap.headMap("orange", true));
        System.out.println("尾部Map: " + treeMap.tailMap("orange", true));
        
        // TreeMap 自定义排序
        TreeMap<Student, String> studentMap = new TreeMap<>((s1, s2) -> {
            int ageCompare = Integer.compare(s1.getAge(), s2.getAge());
            if (ageCompare != 0) return ageCompare;
            return s1.getName().compareTo(s2.getName());
        });
        
        studentMap.put(new Student("张三", 20), "class1");
        studentMap.put(new Student("李四", 19), "class2");
        System.out.println("\n按年龄排序的学生Map: " + studentMap);
    }
}
```

## Collections 工具类

```java
// Collection/CollectionsDemo.java
import java.util.*;

public class CollectionsDemo {
    public static void main(String[] args) {
        List<Integer> list = new ArrayList<>(Arrays.asList(5, 2, 8, 1, 9, 3));
        System.out.println("原列表: " + list);
        
        // 排序
        Collections.sort(list);
        System.out.println("排序后: " + list);
        
        // 反转
        Collections.reverse(list);
        System.out.println("反转后: " + list);
        
        // 洗牌
        Collections.shuffle(list);
        System.out.println("洗牌后: " = list);
        
        // 查找
        System.out.println("最大值: " + Collections.max(list));
        System.out.println("最小值: " + Collections.min(list));
        System.out.println("二分查找: " + Collections.binarySearch(list, 8));
        
        // 填充
        List<String> strList = new ArrayList<>(Arrays.asList("A", "B", "C"));
        Collections.fill(strList, "X");
        System.out.println("填充后: " + strList);
        
        // 交换
        Collections.swap(list, 0, list.size() - 1);
        System.out.println("交换后: " + list);
        
        // 不可变集合
        List<String> immutableList = Collections.unmodifiableList(
            new ArrayList<>(Arrays.asList("A", "B", "C")));
        // immutableList.add("D");  // 抛出 UnsupportedOperationException
        
        // 同步集合
        List<String> synchronizedList = Collections.synchronizedList(
            new ArrayList<>());
        
        // 单元素集合
        Set<String> singletonSet = Collections.singleton("唯一元素");
        List<String> singletonList = Collections.singletonList("唯一元素");
        Map<String, Integer> singletonMap = Collections.singletonMap("key", 100);
        
        // 空集合
        List<String> emptyList = Collections.emptyList();
        Set<String> emptySet = Collections.emptySet();
        Map<String, Integer> emptyMap = Collections.emptyMap();
    }
}
```

::: tip 集合选择指南
| 需求 | 推荐选择 | 原因 |
|------|----------|------|
| 需要快速随机访问 | ArrayList | 数组实现，随机访问 O(1) |
| 频繁插入删除 | LinkedList | 链表实现，插入删除 O(1) |
| 需要去重 | HashSet | 哈希实现，查找 O(1) |
| 需要保持顺序 | LinkedHashSet | 保持插入顺序 |
| 需要排序 | TreeSet | 红黑树实现，有序 O(log n) |
| 键值对存储 | HashMap | 哈希实现，查找 O(1) |
| 需要有序键值对 | TreeMap | 红黑树实现，有序 O(log n) |
| 线程安全 | CopyOnWriteArrayList | 读多写少场景 |
:::
