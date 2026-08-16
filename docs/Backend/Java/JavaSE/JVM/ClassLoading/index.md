# 类加载机制

类加载机制负责把 `.class` 字节码变为 JVM 可以使用的运行时结构。核心知识有三块：**类生命周期**、**双亲委派模型**、**打破双亲委派**。

## 类的生命周期

```text
加载 → 验证 → 准备 → 解析 → 初始化 → 使用 → 卸载
├── 前五步为「链接（Linking）」
```

| 阶段 | 做什么 |
| --- | --- |
| 加载 | 读取字节码，生成 `Class` 对象，存入元空间 |
| 验证 | 校验字节码格式、语义、符号引用 |
| 准备 | 为静态变量分配内存并设默认值（如 0、null） |
| 解析 | 把符号引用替换为直接引用 |
| 初始化 | 执行静态代码块、静态变量赋值（`<clinit>`） |

## 触发初始化的时机

以下情况会触发类的初始化（主动引用）：

1. `new`、反射、静态方法/静态字段访问。
2. 初始化子类时先初始化父类。
3. 作为 JVM 启动入口（main 所在类）。

以下情况**不会**触发（被动引用）：

1. 通过子类访问父类的静态字段。
2. 定义数组引用：`User[] users = new User[10]`。
3. 引用常量（编译期已放入常量池）：`static final String NAME = "JVM"`。

```java [JVM/ClassLoading/PassiveRefDemo.java]
class Parent {
    static { System.out.println("Parent init"); }
    static int value = 42;
}

class Child extends Parent {
    static { System.out.println("Child init"); }
}

public class PassiveRefDemo {
    public static void main(String[] args) {
        System.out.println(Child.value);   // 只初始化 Parent
    }
}
```

输出：

```text
Parent init
42
```

## 双亲委派模型

```text
Application ClassLoader（应用类加载器）
        ↑ 委托
Platform ClassLoader（平台类加载器，JDK 9+ 取代 Extension）
        ↑ 委托
Bootstrap ClassLoader（启动类加载器，C++ 实现，加载 JDK 核心类）
```

工作流程：加载某个类时，先让父加载器尝试加载；父加载不了才由自己加载。

```java [JVM/ClassLoading/ClassLoaderDemo.java]
public class ClassLoaderDemo {
    public static void main(String[] args) {
        ClassLoader cl = ClassLoaderDemo.class.getClassLoader();
        while (cl != null) {
            System.out.println(cl.getName());
            cl = cl.getParent();
        }
        // 输出：
        // app（应用类加载器）
        // platform（平台类加载器）
        // Bootstrap 由 null 表示
    }
}
```

### 双亲委派的好处

1. **避免重复加载**：同一个类只会被加载一次。
2. **安全**：核心类（如 `java.lang.String`）永远由 Bootstrap 加载，防止自定义同名类冒充。

## 打破双亲委派

典型场景：

| 场景 | 做法 |
| --- | --- |
| JDBC SPI | 线程上下文类加载器（`Thread.currentThread().getContextClassLoader()`） |
| Web 容器（Tomcat） | 每个应用一个 WebAppClassLoader，优先加载应用自己的类 |
| OSGi / 热部署 | 自定义类加载器，实现类隔离与卸载 |

Tomcat 之所以要打破：多个 Web 应用部署在同一容器，需要隔离各自的 `lib`，同时又要共享容器的公共类。

## 常见异常

| 异常 | 含义 | 常见原因 |
| --- | --- | --- |
| `ClassNotFoundException` | 找不到类 | 依赖缺失、jar 未引入 |
| `NoClassDefFoundError` | 类加载后初始化失败/被卸载 | 静态初始化抛异常、编译期存在运行期缺失 |
| `LinkageError` | 类冲突 | 同一个类被不同加载器加载，版本不一致 |

## 热部署原理

热部署 = 使用新的类加载器加载新版本类，旧类加载器及旧类可以被卸载。Spring Boot DevTools、IDEA 热更新、Tomcat reload 都基于这个思路；类卸载前提是**不再被引用**，这也是自定义类加载器要配合规范清理的原因。

## 易错点

::: danger 常见错误
1. 把 `ClassNotFoundException` 当普通日志忽略：往往是启动后运行期才发现，先检查依赖与 classpath。
2. 静态初始化抛异常：`NoClassDefFoundError` 的根源常常是 `<clinit>` 失败，而不是类真的缺失。
3. 认为双亲委派“不可破”：SPI、容器都打破了，面试要能说出场景和方式。
4. 用 `Class.forName` 触发初始化却忘了它会执行静态块：只想拿 Class 对象时用 `ClassLoader.loadClass`。
5. 热部署后内存泄漏：旧类加载器被静态引用，无法卸载，元空间不断增长。
:::

## 验证方式

1. 运行 `PassiveRefDemo`，确认只输出 `Parent init`。
2. 运行 `ClassLoaderDemo`，观察加载器层级。
3. 在 classpath 里放一个与 JDK 核心类同名的类（如自定义 `java.lang.String`），确认不会被加载（双亲委派安全保护）。

## 参考资料

- 类加载机制（Oracle 教程）：https://docs.oracle.com/javase/tutorial/essential/network/classLoader.html
- JVM 规范第 5 章（加载/链接/初始化）：https://docs.oracle.com/javase/specs/jvms/se25/html/jvms-5.html
- 平台类加载器说明：https://openjdk.org/jeps/261
