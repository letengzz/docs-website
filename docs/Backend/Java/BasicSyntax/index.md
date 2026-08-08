# Java 基础语法

## 程序入口

每个可执行的 Java 程序从 `main` 方法开始：

```java
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

Java 是强类型语言，变量必须先声明类型再使用。

8 种基本类型：

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

引用类型包括类（如 `String`）、接口、数组、枚举等，`String` 是最常用的引用类型。

```java
int age = 18;
long views = 10000000000L;
double price = 99.9;
boolean isOk = true;
char sex = '男';
String name = "张三";
```

::: danger 注意
1. 小数默认是 `double`，赋给 `float` 必须加 `f`。
2. 整数默认是 `int`，超过范围要加 `L` 并使用 `long`。
3. 字符串必须用双引号，字符必须用单引号。
:::

## 运算符

### 算术运算符

`+`、`-`、`*`、`/`、`%`，以及自增 `++`、自减 `--`：

```java
int a = 10;
int b = 3;
System.out.println(a / b);   // 3（整数除法）
System.out.println(a % b);   // 1
System.out.println(a++);     // 先取值后自增，输出 10
System.out.println(++a);     // 先自增后取值，输出 12
```

### 关系与逻辑运算符

- 关系：`==`、`!=`、`>`、`<`、`>=`、`<=`
- 逻辑：`&&`（短路与）、`||`（短路或）、`!`

### 三元运算符

```java
int age = 20;
String result = age >= 18 ? "成年" : "未成年";
```

## 流程控制

### if / else if / else

```java
int score = 85;
if (score >= 90) {
    System.out.println("优秀");
} else if (score >= 60) {
    System.out.println("及格");
} else {
    System.out.println("不及格");
}
```

### switch

```java
String day = "MON";
switch (day) {
    case "MON", "TUE", "WED", "THU", "FRI" -> System.out.println("工作日");
    case "SAT", "SUN" -> System.out.println("周末");
    default -> System.out.println("未知");
}
```

### 循环

```java
// for
for (int i = 0; i < 5; i++) {
    System.out.println(i);
}

// while
int i = 0;
while (i < 5) {
    i++;
}

// do-while：至少执行一次
int j = 0;
do {
    j++;
} while (j < 5);
```

`break` 用于跳出循环，`continue` 用于跳过本次循环。

## 数组

```java
// 声明并初始化
int[] nums = {1, 2, 3, 4, 5};

// 创建指定长度，默认值为 0 / null
String[] names = new String[3];
names[0] = "张三";

// 普通 for 遍历
for (int i = 0; i < nums.length; i++) {
    System.out.println(nums[i]);
}

// 增强 for 遍历
for (int num : nums) {
    System.out.println(num);
}
```

::: danger 注意
1. 数组下标从 0 开始，越界会抛出 `ArrayIndexOutOfBoundsException`。
2. 字符串比较用 `equals`，不要用 `==`（`==` 比较的是引用地址）。
3. 整数除以整数结果还是整数，需要小数时先转成 `double`。
:::

## 完整示例：猜数字

```java [GuessNumber.java]
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
