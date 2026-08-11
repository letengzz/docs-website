# 常用类

Java 提供了丰富的常用类库，涵盖了字符串处理、日期时间、数学运算、包装类型等核心功能。熟练掌握这些常用类是 Java 开发的基础。

## String 类

String 是 Java 中最常用的类之一，用于表示字符串。在 Java 中字符串是不可变的（immutable）。

### String 基本操作

```java
// CommonClasses/StringDemo.java

public class StringDemo {
    public static void main(String[] args) {
        // 创建字符串的方式
        String str1 = "Hello";  // 字面量方式（字符串常量池）
        String str2 = new String("World");  // new 方式
        String str3 = str1 + " " + str2;   // 字符串拼接
        
        System.out.println("str1: " + str1);
        System.out.println("str2: " + str2);
        System.out.println("str3: " + str3);
        
        // 字符串长度
        System.out.println("str1 长度: " + str1.length());
        
        // 字符串遍历
        System.out.print("str1 字符遍历: ");
        for (int i = 0; i < str1.length(); i++) {
            System.out.print(str1.charAt(i) + " ");
        }
        System.out.println();
        
        // 字符串比较
        String s1 = "Hello";
        String s2 = "Hello";
        String s3 = new String("Hello");
        
        System.out.println("s1 == s2: " + (s1 == s2));      // true（常量池复用）
        System.out.println("s1 == s3: " + (s1 == s3));      // false（不同对象）
        System.out.println("s1.equals(s3): " + s1.equals(s3));  // true（内容相同）
        
        // 字符串查找
        String text = "Hello, Java! Welcome to Java world.";
        System.out.println("'Java' 首次出现位置: " + text.indexOf("Java"));
        System.out.println("'Java' 最后出现位置: " + text.lastIndexOf("Java"));
        System.out.println("包含 'Welcome': " + text.contains("Welcome"));
        System.out.println("以 'Hello' 开头: " + text.startsWith("Hello"));
        System.out.println("以 '.' 结尾: " + text.endsWith("."));
        
        // 字符串截取
        System.out.println("substring(7, 11): " + text.substring(7, 11));
        System.out.println("substring(7): " + text.substring(7));
        
        // 字符串替换
        System.out.println("替换所有 Java: " + text.replace("Java", "Python"));
        System.out.println("替换首次 Java: " + text.replaceFirst("Java", "Python"));
        
        // 大小写转换
        String upper = text.toUpperCase();
        String lower = text.toLowerCase();
        System.out.println("转大写: " + upper);
        System.out.println("转小写: " + lower);
        
        // 去除空白
        String spaces = "  Hello World  ";
        System.out.println("去除两端空白: '" + spaces.trim() + "'");
        System.out.println("去除所有空白: '" + spaces.replace(" ", "") + "'");
        
        // 字符串分割
        String csv = "apple,banana,orange,grape";
        String[] fruits = csv.split(",");
        System.out.print("分割结果: ");
        for (String fruit : fruits) {
            System.out.print(fruit + " ");
        }
        System.out.println();
        
        // 字符串拼接
        String joined = String.join(" | ", fruits);
        System.out.println("拼接结果: " + joined);
        
        // 字符串格式化
        String name = "张三";
        int age = 25;
        double salary = 15000.50;
        System.out.println(String.format("姓名: %s, 年龄: %d, 薪资: %.2f", name, age, salary));
    }
}
```

### StringBuilder 与 StringBuffer

```java
// CommonClasses/StringBuilderDemo.java

public class StringBuilderDemo {
    public static void main(String[] args) {
        // StringBuilder - 非线程安全，性能好
        StringBuilder sb = new StringBuilder();
        sb.append("Hello");
        sb.append(" ");
        sb.append("World");
        System.out.println("追加后: " + sb.toString());
        
        sb.insert(6, "Java ");
        System.out.println("插入后: " + sb.toString());
        
        sb.replace(0, 5, "Hi");
        System.out.println("替换后: " + sb.toString());
        
        sb.delete(0, 3);
        System.out.println("删除后: " + sb.toString());
        
        sb.reverse();
        System.out.println("反转后: " + sb.toString());
        
        // StringBuffer - 线程安全
        StringBuffer sbf = new StringBuffer();
        sbf.append("线程安全");
        sbf.append("的字符串操作");
        System.out.println("StringBuffer: " + sbf.toString());
        
        // 性能对比
        long startTime = System.currentTimeMillis();
        String str = "";
        for (int i = 0; i < 10000; i++) {
            str += i;
        }
        long stringTime = System.currentTimeMillis() - startTime;
        
        startTime = System.currentTimeMillis();
        StringBuilder builder = new StringBuilder();
        for (int i = 0; i < 10000; i++) {
            builder.append(i);
        }
        long builderTime = System.currentTimeMillis() - startTime;
        
        System.out.println("String 耗时: " + stringTime + "ms");
        System.out.println("StringBuilder 耗时: " + builderTime + "ms");
    }
}
```

::: tip String 性能优化
- 频繁字符串拼接使用 StringBuilder
- 多线程环境使用 StringBuffer
- 字符串常量使用字面量方式创建，可利用常量池复用
- 大字符串操作优先考虑 StringBuilder
:::

## 日期时间类

### LocalDate、LocalTime、LocalDateTime

```java
// CommonClasses/LocalDateTimeDemo.java
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.LocalDateTime;
import java.time.Month;

public class LocalDateTimeDemo {
    public static void main(String[] args) {
        // LocalDate - 日期
        LocalDate today = LocalDate.now();
        System.out.println("今天: " + today);
        
        LocalDate specificDate = LocalDate.of(2024, 1, 15);
        System.out.println("指定日期: " + specificDate);
        
        LocalDate fromString = LocalDate.parse("2024-03-20");
        System.out.println("字符串解析: " + fromString);
        
        // 日期计算
        System.out.println("今天加5天: " + today.plusDays(5));
        System.out.println("今天减2月: " + today.minusMonths(2));
        System.out.println("今年最后一天: " = today.with(TemporalAdjusters.lastDayOfYear()));
        
        // 获取日期信息
        System.out.println("年: " + today.getYear());
        System.out.println("月: " + today.getMonthValue());
        System.out.println("月名: " + today.getMonth());
        System.out.println("日: " + today.getDayOfMonth());
        System.out.println("星期: " + today.getDayOfWeek());
        System.out.println("一年中的第几天: " + today.getDayOfYear());
        
        // LocalTime - 时间
        LocalTime now = LocalTime.now();
        System.out.println("\n当前时间: " + now);
        
        LocalTime specificTime = LocalTime.of(14, 30, 45);
        System.out.println("指定时间: " + specificTime);
        
        System.out.println("小时: " + now.getHour());
        System.out.println("分钟: " + now.getMinute());
        System.out.println("秒: " + now.getSecond());
        
        // LocalDateTime - 日期时间
        LocalDateTime nowDateTime = LocalDateTime.now();
        System.out.println("\n当前日期时间: " + nowDateTime);
        
        LocalDateTime dateTime = LocalDateTime.of(2024, 3, 20, 10, 30, 0);
        System.out.println("指定日期时间: " + dateTime);
        
        // 日期时间转换
        LocalDate localDate = nowDateTime.toLocalDate();
        LocalTime localTime = nowDateTime.toLocalTime();
        LocalDateTime fromLocalDate = LocalDateTime.of(localDate, localTime);
        
        // 格式化
        System.out.println("格式化: " + nowDateTime.format(
            java.time.format.DateTimeFormatter.ofPattern("yyyy年MM月dd日 HH:mm:ss")));
        
        // 解析
        String dateTimeStr = "2024-03-20 15:30:00";
        LocalDateTime parsed = LocalDateTime.parse(dateTimeStr,
            java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
        System.out.println("解析结果: " + parsed);
    }
}
```

### Period 与 Duration

```java
// CommonClasses/PeriodDurationDemo.java
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.Period;
import java.time.Duration;
import java.time.temporal.ChronoUnit;

public class PeriodDurationDemo {
    public static void main(String[] args) {
        // Period - 日期期间
        LocalDate birthDate = LocalDate.of(2000, 1, 1);
        LocalDate today = LocalDate.now();
        
        Period period = Period.between(birthDate, today);
        System.out.println("年龄: " + period.getYears() + "年" + 
                          period.getMonths() + "月" + 
                          period.getDays() + "天");
        
        // 直接获取总天数
        long days = ChronoUnit.DAYS.between(birthDate, today);
        System.out.println("总天数: " + days);
        
        // Duration - 时间期间
        LocalDateTime start = LocalDateTime.of(2024, 1, 1, 9, 0, 0);
        LocalDateTime end = LocalDateTime.of(2024, 1, 1, 17, 30, 0);
        
        Duration duration = Duration.between(start, end);
        System.out.println("\n时间差:");
        System.out.println("小时: " + duration.toHours());
        System.out.println("分钟: " + duration.toMinutes());
        System.out.println("秒: " = duration.getSeconds());
        System.out.println("毫秒: " + duration.toMillis());
    }
}
```

## 包装类

Java 为 8 种基本数据类型提供了对应的包装类，实现了基本数据类型与对象之间的转换。

### 包装类基本操作

```java
// CommonClasses/WrapperClassDemo.java

public class WrapperClassDemo {
    public static void main(String[] args) {
        // 装箱：将基本类型转换为包装类
        Integer int1 = 10;  // 自动装箱
        Integer int2 = Integer.valueOf(20);  // 手动装箱
        Double double1 = 3.14;  // 自动装箱
        Boolean bool1 = true;  // 自动装箱
        
        // 拆箱：将包装类转换为基本类型
        int num1 = int1;  // 自动拆箱
        int num2 = int2.intValue();  // 手动拆箱
        double d1 = double1;
        boolean b1 = bool1;
        
        System.out.println("int1: " + int1 + ", num1: " + num1);
        System.out.println("double1: " + double1 + ", d1: " + d1);
        
        // 字符串转基本类型
        String strInt = "123";
        String strDouble = "45.67";
        String strBool = "true";
        
        int parseInt = Integer.parseInt(strInt);
        double parseDouble = Double.parseDouble(strDouble);
        boolean parseBool = Boolean.parseBoolean(strBool);
        
        System.out.println("parseInt: " + parseInt);
        System.out.println("parseDouble: " + parseDouble);
        System.out.println("parseBool: " + parseBool);
        
        // 数值转字符串
        int num = 100;
        String s1 = Integer.toString(num);
        String s2 = String.valueOf(num);
        String s3 = num + "";  // 字符串拼接
        
        System.out.println("s1: " + s1 + ", s2: " + s2 + ", s3: " + s3);
        
        // 常用常量
        System.out.println("Integer.MAX_VALUE: " + Integer.MAX_VALUE);
        System.out.println("Integer.MIN_VALUE: " + Integer.MIN_VALUE);
        System.out.println("Double.MAX_VALUE: " + Double.MAX_VALUE);
        System.out.println("Double.NaN: " + Double.NaN);
        System.out.println("Double.POSITIVE_INFINITY: " + Double.POSITIVE_INFINITY);
        
        // 进制转换
        System.out.println("\n进制转换:");
        System.out.println("16进制: " + Integer.toHexString(255));
        System.out.println("8进制: " + Integer.toOctalString(255));
        System.out.println("2进制: " + Integer.toBinaryString(10));
    }
}
```

### 自动装箱与缓存

```java
// CommonClasses/AutoBoxingDemo.java

public class AutoBoxingDemo {
    public static void main(String[] args) {
        // 自动装箱时，Integer 会使用缓存
        Integer a = 100;  // -128 到 127 使用缓存
        Integer b = 100;
        System.out.println("a == b (100): " + (a == b));  // true
        
        Integer c = 200;
        Integer d = 200;
        System.out.println("c == d (200): " + (c == d));  // false
        
        // 使用 valueOf 确保使用缓存
        Integer e = Integer.valueOf(100);
        Integer f = Integer.valueOf(100);
        System.out.println("e == f (valueOf): " + (e == f));  // true
        
        // 运算符比较时会自动拆箱
        Integer x = 100;
        Integer y = 100;
        System.out.println("x + y: " + (x + y));  // 200
        
        // 注意事项
        Integer m = null;
        // int n = m;  // 自动拆箱会抛出 NullPointerException
        
        if (m != null) {
            int n = m;
        }
    }
}
```

## Math 类

```java
// CommonClasses/MathDemo.java

public class MathDemo {
    public static void main(String[] args) {
        // 常用常量
        System.out.println("π: " + Math.PI);
        System.out.println("e: " + Math.E);
        
        // 绝对值
        System.out.println("|-10|: " + Math.abs(-10));
        System.out.println("|-3.14|: " + Math.abs(-3.14));
        
        // 三角函数
        System.out.println("sin(30°): " + Math.sin(Math.toRadians(30)));
        System.out.println("cos(60°): " + Math.cos(Math.toRadians(60)));
        System.out.println("tan(45°): " = Math.tan(Math.toRadians(45)));
        
        // 反三角函数
        System.out.println("asin(0.5): " + Math.toDegrees(Math.asin(0.5)));
        System.out.println("acos(0.5): " + Math.toDegrees(Math.acos(0.5)));
        
        // 指数对数
        System.out.println("2^3: " + Math.pow(2, 3));
        System.out.println("√9: " + Math.sqrt(9));
        System.out.println("∛8: " + Math.cbrt(8));
        System.out.println("ln(e): " + Math.log(Math.E));
        System.out.println("log10(100): " + Math.log10(100));
        
        // 取整
        System.out.println("\n取整运算:");
        System.out.println("向上取整 3.14: " + Math.ceil(3.14));
        System.out.println("向下取整 3.14: " + Math.floor(3.14));
        System.out.println("四舍五入 3.6: " + Math.round(3.6));
        System.out.println("四舍五入 3.4: " + Math.round(3.4));
        System.out.println("截断 3.6: " + (int) 3.6);
        
        // 随机数
        System.out.println("\n随机数:");
        System.out.println("Random [0,1): " + Math.random());
        System.out.println("Random [0,100): " + (int) (Math.random() * 100));
        System.out.println("Random [10,20]: " + (10 + (int) (Math.random() * 11)));
        
        // 最大最小值
        System.out.println("\n极值:");
        System.out.println("max(10, 20): " + Math.max(10, 20));
        System.out.println("min(-5, 5): " + Math.min(-5, 5));
        System.out.println("max(三个数): " + Math.max(Math.max(1, 2), 3));
        
        // 其他
        System.out.println("\n其他运算:");
        System.out.println("hypot(3, 4) [直角边]: " + Math.hypot(3, 4));
        System.out.println("signum(-10): " + Math.signum(-10));
        System.out.println("copySign(-5, 10): " + Math.copySign(-5, 10));
    }
}
```

## Object 类与 Objects 工具类

```java
// CommonClasses/ObjectsDemo.java
import java.util.Objects;

public class ObjectsDemo {
    public static void main(String[] args) {
        // Objects 工具类提供空指针安全的操作
        
        String str1 = "Hello";
        String str2 = null;
        String str3 = "World";
        
        // 非空检查
        System.out.println("str1 非空: " + Objects.nonNull(str1));
        System.out.println("str2 非空: " + Objects.nonNull(str2));
        System.out.println("str1 为空: " + Objects.isNull(str1));
        System.out.println("str2 为空: " + Objects.isNull(str2));
        
        // 比较
        System.out.println("equals: " + Objects.equals(str1, str3));
        System.out.println("equals(null安全): " + Objects.equals(str2, str1));
        
        // requireNonNull - 验证参数非空
        try {
            Objects.requireNonNull(str2, "参数不能为空");
        } catch (NullPointerException e) {
            System.out.println("捕获异常: " + e.getMessage());
        }
        
        // deepEquals - 深度比较（适用于数组）
        int[] arr1 = {1, 2, 3};
        int[] arr2 = {1, 2, 3};
        System.out.println("数组比较 ==: " + (arr1 == arr2));
        System.out.println("数组比较 deepEquals: " + Objects.deepEquals(arr1, arr2));
        
        // hashCode - 空安全
        System.out.println("str1.hashCode: " + Objects.hashCode(str1));
        System.out.println("str2.hashCode(null安全): " + Objects.hashCode(str2));
        
        // toString - 空安全
        System.out.println("toString: " + Objects.toString(str1));
        System.out.println("toString(null安全): " + Objects.toString(str2, "默认值"));
        
        // compare - 比较器
        String[] names = {"Alice", "Bob", "Charlie"};
        java.util.Arrays.sort(names, (a, b) -> Objects.compare(a, b, String.CASE_INSENSITIVE_ORDER));
        System.out.println("排序后: " + java.util.Arrays.toString(names));
    }
}
```

## 正则表达式

```java
// CommonClasses/RegexDemo.java
import java.util.regex.*;

public class RegexDemo {
    public static void main(String[] args) {
        String text = "张三的手机号是13812345678，李四是13987654321";
        
        // Pattern 和 Matcher
        Pattern pattern = Pattern.compile("1[3-9]\\d{9}");
        Matcher matcher = pattern.matcher(text);
        
        System.out.println("手机号匹配结果:");
        while (matcher.find()) {
            System.out.println("  找到: " + matcher.group());
        }
        
        // 常用正则表达式
        System.out.println("\n常用匹配:");
        String[] patterns = {
            "^\\d+$",           // 纯数字
            "^[a-zA-Z]+$",      // 纯字母
            "^\\w+@\\w+\\.\\w+$", // 简单邮箱
            "^1[3-9]\\d{9}$",   // 手机号
            "^\\d{4}-\\d{2}-\\d{2}$" // 日期格式
        };
        
        String[] tests = {"12345", "abc", "test@email.com", "13812345678", "2024-01-15"};
        for (int i = 0; i < patterns.length; i++) {
            System.out.println(patterns[i] + " 匹配 " + tests[i] + ": " + 
                Pattern.matches(patterns[i], tests[i]));
        }
        
        // String 正则方法
        System.out.println("\nString 正则方法:");
        String email = "test@example.com";
        System.out.println("替换域名: " + email.replaceAll("@\\w+\\.\\w+", "@new-domain.com"));
        System.out.println("分割: " + java.util.Arrays.toString("a,b;c d".split("[,;\\s]")));
        System.out.println("替换数字: " = "a1b2c3".replaceAll("\\d", "#"));
    }
}
```
