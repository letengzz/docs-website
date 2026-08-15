# 基础语法

Java 基础语法是 Java 编程的入门知识，包括变量、数据类型、运算符、流程控制等核心概念。掌握这些基础知识是进行 Java 开发的前提。

## 程序入口

每个可执行的 Java 程序从 `main` 方法开始：

```java
// BasicSyntax/Hello.java
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
```

- `public`：访问修饰符，表示公开。
- `static`：静态方法，无需创建对象即可调用。
- `void`：无返回值。
- `args`：命令行参数。

## 变量与数据类型

### 变量

变量是程序中用于存储数据的基本单元，每个变量都有一个名称（标识符）和一个值。Java 是一种强类型语言，变量必须在使用前声明其类型。

```java
// BasicSyntax/VariableDemo.java
public class VariableDemo {
    public static void main(String[] args) {
        // 局部变量
        int age = 25;
        String name = "张三";
        double salary = 15000.50;
        boolean isMarried = false;
        
        // 使用变量
        System.out.println("姓名：" + name);
        System.out.println("年龄：" + age);
        System.out.println("薪资：" + salary);
        System.out.println("已婚：" + isMarried);
        
        // 修改变量值
        age = 26;
        salary = 18000.00;
        System.out.println("一年后年龄：" + age);
    }
}
```

```java
// BasicSyntax/VariableScope.java
public class VariableScope {
    // 成员变量（实例变量）
    private String instanceVariable = "实例变量";
    
    // 静态变量（类变量）
    private static String staticVariable = "静态变量";
    
    public void method() {
        // 局部变量
        String localVariable = "局部变量";
        System.out.println(localVariable);
        System.out.println(instanceVariable);
        System.out.println(staticVariable);
    }
    
    public static void main(String[] args) {
        VariableScope obj = new VariableScope();
        obj.method();
        System.out.println(VariableScope.staticVariable);
    }
}
```

### 基本数据类型

Java 有 8 种基本数据类型，分为 4 类：整数型、浮点型、字符型和布尔型。

```java
// BasicSyntax/PrimitiveTypes.java
public class PrimitiveTypes {
    public static void main(String[] args) {
        // 整数型
        byte byteMin = -128;
        byte byteMax = 127;
        short shortMin = -32768;
        short shortMax = 32767;
        int intMin = -2147483648;
        int intMax = 2147483647;
        long longMin = -9223372036854775808L;
        long longMax = 9223372036854775807L;
        
        System.out.println("byte 范围：" + byteMin + " 到 " + byteMax);
        System.out.println("short 范围：" + shortMin + " 到 " + shortMax);
        System.out.println("int 范围：" + intMin + " 到 " + intMax);
        System.out.println("long 范围：" + longMin + " 到 " + longMax);
        
        // 浮点型
        float floatNum = 3.14159f;
        double doubleNum = 3.141592653589793;
        
        System.out.println("float 精度：" + floatNum);
        System.out.println("double 精度：" + doubleNum);
        
        // 字符型
        char char1 = 'A';
        char char2 = '中';
        char char3 = 97;  // ASCII 码
        
        System.out.println("char1: " + char1);
        System.out.println("char2: " + char2);
        System.out.println("char3 (97对应的字符): " + char3);
        
        // 布尔型
        boolean flag1 = true;
        boolean flag2 = false;
        
        System.out.println("flag1: " + flag1);
        System.out.println("flag2: " + flag2);
    }
}
```

8 种基本数据类型汇总：

| 类型 | 大小 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `byte` | 1 字节 | `0` | 整数 |
| `short` | 2 字节 | `0` | 整数 |
| `int` | 4 字节 | `0` | 最常用的整数 |
| `long` | 8 字节 | `0L` | 长整数，字面量加 `L` |
| `float` | 4 字节 | `0.0f` | 单精度小数，字面量加 `f` |
| `double` | 8 字节 | `0.0` | 双精度小数，默认的小数类型 |
| `char` | 2 字节 | `'\u0000'` | 单个字符 |
| `boolean` | 1 字节 | `false` | `true` / `false` |

::: danger 注意
1. 小数默认是 `double`，赋给 `float` 必须加 `f`。
2. 整数默认是 `int`，超过范围要加 `L` 并使用 `long`。
3. 字符串必须用双引号，字符必须用单引号。
:::

### 引用数据类型

引用数据类型包括类、接口、数组、枚举等，它们存储的是对象的引用而非对象本身。

```java
// BasicSyntax/ReferenceTypes.java
public class ReferenceTypes {
    public static void main(String[] args) {
        // 字符串（String 是引用类型）
        String str1 = "Hello";
        String str2 = new String("World");
        
        // 数组
        int[] array = {1, 2, 3, 4, 5};
        String[] names = {"张三", "李四", "王五"};
        
        // 自定义类
        Person person = new Person("张三", 25);
        System.out.println(person.getName() + "今年" + person.getAge() + "岁");
        
        // 基本类型与引用类型的区别
        int a = 10;
        int b = a;  // 值传递
        b = 20;
        System.out.println("a = " + a + ", b = " + b);  // a=10, b=20
        
        Person p1 = new Person("李四", 30);
        Person p2 = p1;  // 引用传递
        p2.setAge(35);
        System.out.println("p1.age = " + p1.getAge());  // p1.age = 35
    }
}

class Person {
    private String name;
    private int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public String getName() { return name; }
    public int getAge() { return age; }
    public void setAge(int age) { this.age = age; }
}
```

::: tip 数据类型转换
Java 中的数据类型转换分为自动类型转换和强制类型转换：
- 自动类型转换：范围小的类型向范围大的类型转换（byte → short → int → long → float → double）
- 强制类型转换：需要使用强制转换符，可能造成数据丢失
:::

## 运算符

### 算术运算符

```java
// BasicSyntax/ArithmeticOperators.java
public class ArithmeticOperators {
    public static void main(String[] args) {
        int a = 10;
        int b = 3;
        
        System.out.println("加法: " + a + " + " + b + " = " + (a + b));  // 13
        System.out.println("减法: " + a + " - " + b + " = " + (a - b));  // 7
        System.out.println("乘法: " + a + " * " + b + " = " + (a * b));  // 30
        System.out.println("除法: " + a + " / " + b + " = " + (a / b));  // 3
        System.out.println("取余: " + a + " % " + b + " = " + (a % b));  // 1
        
        // 自增自减
        int c = 5;
        System.out.println("c++ = " + c++);  // 5 (先使用后增加)
        System.out.println("++c = " + ++c);  // 7 (先增加后使用)
        System.out.println("c-- = " + c--);  // 7 (先使用后减少)
        System.out.println("--c = " + --c);  // 5 (先减少后使用)
    }
}
```

### 关系运算符

```java
// BasicSyntax/RelationalOperators.java
public class RelationalOperators {
    public static void main(String[] args) {
        int a = 10;
        int b = 20;
        
        System.out.println("a == b: " + (a == b));  // false
        System.out.println("a != b: " + (a != b));  // true
        System.out.println("a > b: " + (a > b));    // false
        System.out.println("a < b: " + (a < b));    // true
        System.out.println("a >= b: " + (a >= b));  // false
        System.out.println("a <= b: " + (a <= b));  // true
    }
}
```

### 逻辑运算符

```java
// BasicSyntax/LogicalOperators.java
public class LogicalOperators {
    public static void main(String[] args) {
        boolean x = true;
        boolean y = false;
        
        // 与运算
        System.out.println("x && y: " + (x && y));  // false (短路与)
        System.out.println("x & y: " + (x & y));    // false (非短路与)
        
        // 或运算
        System.out.println("x || y: " + (x || y));  // true (短路或)
        System.out.println("x | y: " + (x | y));    // true (非短路或)
        
        // 非运算
        System.out.println("!x: " + (!x));          // false
        System.out.println("!y: " + (!y));          // true
        
        // 异或运算
        System.out.println("x ^ y: " + (x ^ y));    // true
        
        // 短路特性
        int m = 5;
        if (x && (++m > 10)) {
            System.out.println("条件成立");
        }
        System.out.println("m = " + m);  // m = 6 (因为 x 为 true，右侧被计算)
        
        m = 5;
        if (y && (++m > 10)) {
            System.out.println("条件成立");
        }
        System.out.println("m = " + m);  // m = 5 (因为 y 为 false，右侧被短路)
    }
}
```

### 位运算符

```java
// BasicSyntax/BitwiseOperators.java
public class BitwiseOperators {
    public static void main(String[] args) {
        int a = 60;  // 60 = 0011 1100
        int b = 13;  // 13 = 0000 1101
        
        System.out.println("a = " + a + " (二进制: " + Integer.toBinaryString(a) + ")");
        System.out.println("b = " + b + " (二进制: " + Integer.toBinaryString(b) + ")");
        
        System.out.println("a & b = " + (a & b));  // 12 = 0000 1100
        System.out.println("a | b = " + (a | b));  // 61 = 0011 1101
        System.out.println("a ^ b = " + (a ^ b));  // 49 = 0011 0001
        System.out.println("~a = " + (~a));         // -61 = 1100 0011
        System.out.println("a << 2 = " + (a << 2)); // 240 = 1111 0000 (左移2位)
        System.out.println("a >> 2 = " + (a >> 2)); // 15 = 0000 1111 (右移2位)
        System.out.println("a >>> 2 = " + (a >>> 2)); // 15 = 0000 1111 (无符号右移)
    }
}
```

### 三元运算符

```java
// BasicSyntax/TernaryOperator.java
public class TernaryOperator {
    public static void main(String[] args) {
        int a = 10;
        int b = 20;
        
        // 语法：条件 ? 值1 : 值2
        int max = (a > b) ? a : b;
        System.out.println("最大值: " + max);
        
        String result = (a % 2 == 0) ? "偶数" : "奇数";
        System.out.println(a + "是" + result);
        
        // 嵌套使用
        int score = 85;
        String grade = (score >= 90) ? "优秀" : 
                       (score >= 80) ? "良好" : 
                       (score >= 60) ? "及格" : "不及格";
        System.out.println("成绩等级: " + grade);
    }
}
```

## 流程控制

### 条件语句

```java
// BasicSyntax/ConditionalStatement.java
public class ConditionalStatement {
    public static void main(String[] args) {
        int score = 85;
        
        // if 语句
        if (score >= 90) {
            System.out.println("优秀");
        } else if (score >= 80) {
            System.out.println("良好");
        } else if (score >= 60) {
            System.out.println("及格");
        } else {
            System.out.println("不及格");
        }
        
        // switch 语句（Java 14+ 支持表达式形式）
        int day = 3;
        String dayName = switch (day) {
            case 1 -> "星期一";
            case 2 -> "星期二";
            case 3 -> "星期三";
            case 4 -> "星期四";
            case 5 -> "星期五";
            case 6, 7 -> "周末";
            default -> "无效日期";
        };
        System.out.println(dayName);
        
        // 传统 switch 语句
        switch (day) {
            case 1:
                System.out.println("Monday");
                break;
            case 2:
                System.out.println("Tuesday");
                break;
            default:
                System.out.println("Other day");
        }
    }
}
```

### 循环语句

```java
// BasicSyntax/LoopStatement.java
public class LoopStatement {
    public static void main(String[] args) {
        // for 循环
        System.out.println("=== for 循环 ===");
        for (int i = 1; i <= 5; i++) {
            System.out.println("第 " + i + " 次循环");
        }
        
        // 增强 for 循环（foreach）
        System.out.println("=== 增强 for 循环 ===");
        int[] numbers = {1, 2, 3, 4, 5};
        for (int num : numbers) {
            System.out.print(num + " ");
        }
        System.out.println();
        
        // while 循环
        System.out.println("=== while 循环 ===");
        int count = 1;
        while (count <= 5) {
            System.out.println("count = " + count);
            count++;
        }
        
        // do-while 循环
        System.out.println("=== do-while 循环 ===");
        int num = 1;
        do {
            System.out.println("num = " + num);
            num++;
        } while (num <= 5);
        
        // 嵌套循环
        System.out.println("=== 嵌套循环（打印乘法表） ===");
        for (int i = 1; i <= 9; i++) {
            for (int j = 1; j <= i; j++) {
                System.out.print(j + "*" + i + "=" + (i * j) + "\t");
            }
            System.out.println();
        }
    }
}
```

### 跳转语句

```java
// BasicSyntax/JumpStatement.java
public class JumpStatement {
    public static void main(String[] args) {
        // break 语句
        System.out.println("=== break 示例 ===");
        for (int i = 1; i <= 10; i++) {
            if (i == 5) {
                break;  // 跳出循环
            }
            System.out.println("i = " + i);
        }
        
        // continue 语句
        System.out.println("\n=== continue 示例 ===");
        for (int i = 1; i <= 10; i++) {
            if (i % 2 == 0) {
                continue;  // 跳过偶数
            }
            System.out.println("奇数: " + i);
        }
        
        // return 语句
        System.out.println("\n=== return 示例 ===");
        System.out.println("方法返回值: " + calculate(10, 20));
    }
    
    public static int calculate(int a, int b) {
        return a + b;
    }
}
```

## 数组

### 一维数组

```java
// BasicSyntax/OneDimensionalArray.java
public class OneDimensionalArray {
    public static void main(String[] args) {
        // 方式1：声明并初始化
        int[] arr1 = new int[5];  // 默认值 0
        int[] arr2 = {1, 2, 3, 4, 5};
        int[] arr3 = new int[]{1, 2, 3, 4, 5};
        
        // 方式2：动态初始化
        String[] names = new String[3];
        names[0] = "张三";
        names[1] = "李四";
        names[2] = "王五";
        
        // 遍历数组
        System.out.println("=== 遍历数组 ===");
        for (int i = 0; i < arr2.length; i++) {
            System.out.println("arr2[" + i + "] = " + arr2[i]);
        }
        
        // 使用增强 for 循环
        System.out.println("\n=== 增强 for 循环 ===");
        for (int num : arr2) {
            System.out.print(num + " ");
        }
        System.out.println();
        
        // 数组常见操作
        System.out.println("\n=== 数组操作 ===");
        System.out.println("数组长度: " + arr2.length);
        System.out.println("数组首元素: " + arr2[0]);
        System.out.println("数组末元素: " + arr2[arr2.length - 1]);
    }
}
```

### 二维数组

```java
// BasicSyntax/TwoDimensionalArray.java
public class TwoDimensionalArray {
    public static void main(String[] args) {
        // 声明并初始化二维数组
        int[][] matrix1 = new int[3][4];  // 3行4列
        int[][] matrix2 = {
            {1, 2, 3, 4},
            {5, 6, 7, 8},
            {9, 10, 11, 12}
        };
        
        // 不规则二维数组
        int[][] jaggedArray = new int[3][];
        jaggedArray[0] = new int[]{1, 2, 3};
        jaggedArray[1] = new int[]{4, 5};
        jaggedArray[2] = new int[]{6, 7, 8, 9};
        
        // 遍历二维数组
        System.out.println("=== 遍历二维数组 ===");
        for (int i = 0; i < matrix2.length; i++) {
            for (int j = 0; j < matrix2[i].length; j++) {
                System.out.print(matrix2[i][j] + "\t");
            }
            System.out.println();
        }
        
        // 使用增强 for 循环
        System.out.println("\n=== 增强 for 循环遍历 ===");
        for (int[] row : matrix2) {
            for (int num : row) {
                System.out.print(num + "\t");
            }
            System.out.println();
        }
        
        // 数组复制
        System.out.println("\n=== 数组复制 ===");
        int[] source = {1, 2, 3, 4, 5};
        int[] target = new int[source.length];
        System.arraycopy(source, 0, target, 0, source.length);
        System.out.println("复制后的数组: " + java.util.Arrays.toString(target));
    }
}
```

### 数组工具类

```java
// BasicSyntax/ArrayUtils.java
import java.util.Arrays;

public class ArrayUtils {
    public static void main(String[] args) {
        int[] arr = {5, 2, 8, 1, 9, 3};
        
        // 排序
        System.out.println("=== 数组排序 ===");
        int[] sortedArr = arr.clone();
        Arrays.sort(sortedArr);
        System.out.println("排序后: " + Arrays.toString(sortedArr));
        
        // 查找（二分查找）
        System.out.println("\n=== 二分查找 ===");
        int index = Arrays.binarySearch(sortedArr, 8);
        System.out.println("元素 8 的索引: " + index);
        
        // 填充
        System.out.println("\n=== 数组填充 ===");
        int[] filledArr = new int[5];
        Arrays.fill(filledArr, 10);
        System.out.println("填充后: " + Arrays.toString(filledArr));
        
        // 比较
        System.out.println("\n=== 数组比较 ===");
        int[] arr1 = {1, 2, 3};
        int[] arr2 = {1, 2, 3};
        int[] arr3 = {1, 2, 4};
        System.out.println("arr1 == arr2: " + Arrays.equals(arr1, arr2));
        System.out.println("arr1 == arr3: " + Arrays.equals(arr1, arr3));
        
        // 转字符串
        System.out.println("\n=== 数组转字符串 ===");
        System.out.println("数组内容: " + Arrays.toString(arr));
    }
}
```

::: danger 数组注意事项
1. 数组索引从 0 开始，访问越界会抛出 `ArrayIndexOutOfBoundsException`
2. 数组是固定长度的，创建后不能改变大小
3. 数组元素有默认值：数值型为 0，引用型为 null，布尔型为 false
4. 使用 `Arrays.equals()` 比较数组内容，而非 `==`
:::

## 完整示例：猜数字

综合运用变量、流程控制和数组知识，实现一个猜数字小游戏：

```java
// BasicSyntax/GuessNumber.java
import java.util.Random;
import java.util.Scanner;

public class GuessNumber {
    public static void main(String[] args) {
        Random random = new Random();
        int target = random.nextInt(100) + 1;
        Scanner scanner = new Scanner(System.in);
        int count = 0;

        while (true) {
            System.out.print("请输入 1-100 的数字：");
            int guess = scanner.nextInt();
            count++;
            if (guess > target) {
                System.out.println("大了");
            } else if (guess < target) {
                System.out.println("小了");
            } else {
                System.out.println("恭喜猜中，共猜了 " + count + " 次");
                break;
            }
        }
    }
}
```

验证：执行 `javac GuessNumber.java && java GuessNumber`，多次输入数字，确认能正常提示大小并最终猜中。

## 相关专题

- [常用类](../CommonClasses/index.md)
- [集合框架](../Collection/index.md)

## 参考资料

- Oracle Java 基础语法教程：https://docs.oracle.com/javase/tutorial/java/nutsandbolts/index.html
- Java 语言规范：https://docs.oracle.com/javase/specs/
