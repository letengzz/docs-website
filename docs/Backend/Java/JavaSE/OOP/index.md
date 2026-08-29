# Java 面向对象

面向对象有三大特征：**封装、继承、多态**。

## 类与对象

类是对一类事物的抽象，对象是类的具体实例。

```java [Student.java]
public class Student {
    // 属性（成员变量）
    String name;
    int age;

    // 构造方法：创建对象时调用
    public Student(String name, int age) {
        this.name = name;
        this.age = age;
    }

    // 方法
    public void sayHello() {
        System.out.println("大家好，我是 " + name);
    }
}
```

创建对象：

```java
Student stu = new Student("张三", 18);
stu.sayHello();
```

::: tip
`this` 表示当前对象，用来区分成员变量和同名参数。
:::

## 封装

将属性私有化，对外提供受控的访问方法，避免外部随意修改内部状态。

```java [Account.java]
public class Account {
    private double balance;

    public double getBalance() {
        return balance;
    }

    public void deposit(double money) {
        if (money > 0) {
            balance += money;
        }
    }
}
```

访问修饰符：

| 修饰符 | 同类 | 同包 | 子类 | 任意位置 |
| --- | --- | --- | --- | --- |
| `private` | ✔ | | | |
| 默认（不写） | ✔ | ✔ | | |
| `protected` | ✔ | ✔ | ✔ | |
| `public` | ✔ | ✔ | ✔ | ✔ |

## 继承

子类通过 `extends` 继承父类的属性和方法，用 `super` 调用父类的成员。

```java [Animal.java]
public class Animal {
    public void eat() {
        System.out.println("吃东西");
    }
}
```

```java [Dog.java]
public class Dog extends Animal {
    @Override
    public void eat() {
        super.eat();
        System.out.println("狗吃骨头");
    }
}
```

::: danger 注意
1. Java 是单继承：一个类只能有一个直接父类。
2. 子类构造方法默认调用父类无参构造；父类没有无参构造时，子类要显式写 `super(...)`。
3. 方法重写要求签名一致，建议加上 `@Override` 注解让编译器帮忙检查。
:::

## 多态

同一方法在不同对象上表现出不同行为。

```java
Animal animal = new Dog();
animal.eat();   // 实际调用 Dog 的 eat
```

要点：

- 向上转型：父类引用指向子类对象。
- 动态绑定：运行时根据实际对象决定调用哪个方法。
- `instanceof` 用于判断对象实际类型。

```java
if (animal instanceof Dog dog) {
    dog.watchDoor();
}
```

## 抽象类与接口

### 抽象类

用 `abstract` 声明，可以包含抽象方法和普通方法，不能直接实例化：

```java [Shape.java]
public abstract class Shape {
    public abstract double area();
}
```

### 接口

用 `interface` 定义「能做什么」，类用 `implements` 实现，可以同时实现多个接口：

```java
public interface Runnable {
    void run();
}

public interface Swimmable {
    void swim();
}

public class Duck implements Runnable, Swimmable {
    @Override
    public void run() {
        System.out.println("鸭子跑");
    }

    @Override
    public void swim() {
        System.out.println("鸭子游泳");
    }
}
```

::: tip
Java 8+ 的接口支持 `default` 方法（带默认实现），方便给接口扩展能力而不破坏已有实现类。
:::

## static 与 final

| 关键字 | 作用 |
| --- | --- |
| `static` | 属于类本身，不依赖对象：静态变量、静态方法、静态代码块 |
| `final` | 修饰类不可继承、修饰方法不可重写、修饰变量不可重新赋值（常量） |

```java [Config.java]
public class Config {
    public static final String APP_NAME = "docs-website";
}
```

## 完整示例：员工薪资

```java [Employee.java]
public class Employee {
    private String name;
    private double salary;

    public Employee(String name, double salary) {
        this.name = name;
        this.salary = salary;
    }

    public double getSalary() {
        return salary;
    }
}
```

```java [Manager.java]
public class Manager extends Employee {
    private double bonus;

    public Manager(String name, double salary, double bonus) {
        super(name, salary);
        this.bonus = bonus;
    }

    @Override
    public double getSalary() {
        return super.getSalary() + bonus;
    }
}
```

```java [Main.java]
public class Main {
    public static void main(String[] args) {
        Employee e = new Manager("李四", 8000, 2000);
        System.out.println(e.getSalary());   // 10000.0
    }
}
```

验证：编译运行后输出 `10000.0`，说明多态和重写生效。

## 相关专题

- [面向对象基础](../ObjectOriented/index.md)
- [集合框架](../Collection/index.md)
- [反射与注解](../Reflection/index.md)：动态获取类结构、调用方法与自定义元数据
