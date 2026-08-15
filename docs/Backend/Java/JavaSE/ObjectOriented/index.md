# 面向对象

面向对象编程（OOP）是 Java 的核心编程范式，通过类和对象来组织代码，提高代码的可维护性、可扩展性和复用性。Java 是一种纯面向对象的语言，所有的代码都必须写在类中。

## 类与对象

### 类的定义

类是面向对象编程的基本单元，它定义了一类事物的属性和行为。

```java
// ObjectOriented/ClassDefinition.java

/**
 * 学生类 - 演示类的定义
 */
public class Student {
    // 成员变量（属性）
    private String name;
    private int age;
    private String studentId;
    
    // 静态变量（类变量）
    private static String school = "清华大学";
    
    // 构造方法
    public Student() {
    }
    
    public Student(String name, int age, String studentId) {
        this.name = name;
        this.age = age;
        this.studentId = studentId;
    }
    
    // 成员方法（行为）
    public void study() {
        System.out.println(name + "正在学习...");
    }
    
    public void exam() {
        System.out.println(name + "正在参加考试");
    }
    
    // getter 和 setter 方法
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public int getAge() {
        return age;
    }
    
    public void setAge(int age) {
        if (age < 0 || age > 150) {
            throw new IllegalArgumentException("年龄不合法");
        }
        this.age = age;
    }
    
    public String getStudentId() {
        return studentId;
    }
    
    public void setStudentId(String studentId) {
        this.studentId = studentId;
    }
    
    public static String getSchool() {
        return school;
    }
    
    public static void setSchool(String school) {
        Student.school = school;
    }
}
```

### 对象的创建与使用

```java
// ObjectOriented/ObjectCreation.java

public class ObjectCreation {
    public static void main(String[] args) {
        // 使用 new 关键字创建对象
        Student student1 = new Student();
        student1.setName("张三");
        student1.setAge(20);
        student1.setStudentId("2023001");
        
        // 使用有参构造方法创建对象
        Student student2 = new Student("李四", 21, "2023002");
        
        // 调用对象方法
        System.out.println("=== 学生信息 ===");
        System.out.println("姓名: " + student1.getName());
        System.out.println("年龄: " + student1.getAge());
        System.out.println("学号: " + student1.getStudentId());
        System.out.println("学校: " + Student.getSchool());
        
        student1.study();
        student2.study();
        
        // 同一个类的多个对象是相互独立的
        student1.setName("王五");
        System.out.println("\n修改后 student1 的姓名: " + student1.getName());
        System.out.println("student2 的姓名不变: " + student2.getName());
    }
}
```

### 成员变量与局部变量

```java
// ObjectOriented/VariableScope.java

public class VariableScope {
    // 成员变量 - 定义在类中，方法外
    private String instanceVariable = "实例变量";
    private static String staticVariable = "静态变量";
    
    public void method(String param) {
        // 局部变量 - 定义在方法内部
        String localVariable = "局部变量";
        
        // 形参也是局部变量
        System.out.println("局部变量: " + localVariable);
        System.out.println("参数: " + param);
        System.out.println("实例变量: " + this.instanceVariable);
        System.out.println("静态变量: " + staticVariable);
    }
    
    public static void main(String[] args) {
        VariableScope obj = new VariableScope();
        obj.method("传入参数");
    }
}
```

::: tip 成员变量与局部变量的区别
| 区别点 | 成员变量 | 局部变量 |
|--------|----------|----------|
| 定义位置 | 类中、方法外 | 方法内或代码块内 |
| 内存位置 | 堆内存 | 栈内存 |
| 初始化 | 有默认值 | 需手动初始化 |
| 生命周期 | 对象创建时存在，垃圾回收时消失 | 方法调用时存在，方法结束时消失 |
| 修饰符 | 可使用访问修饰符 | 不能使用访问修饰符 |
:::

## 封装

封装是面向对象的第一大特性，通过访问修饰符控制属性的可见性，并通过 getter 和 setter 方法提供受控的访问方式。

```java
// ObjectOriented/Encapsulation.java

/**
 * 银行账户类 - 演示封装
 */
class BankAccount {
    // private 实现封装，外部不能直接访问
    private String accountId;
    private String accountName;
    private double balance;
    
    // 无参构造方法
    public BankAccount() {
    }
    
    // 有参构造方法
    public BankAccount(String accountId, String accountName, double balance) {
        this.accountId = accountId;
        this.accountName = accountName;
        this.balance = balance;
    }
    
    // getter 方法 - 提供只读访问
    public String getAccountId() {
        return accountId;
    }
    
    public String getAccountName() {
        return accountName;
    }
    
    public double getBalance() {
        return balance;
    }
    
    // setter 方法 - 提供受控的写入访问
    public void setAccountName(String accountName) {
        this.accountName = accountName;
    }
    
    // 存款方法 - 包含业务逻辑验证
    public void deposit(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("存款金额必须大于0");
        }
        balance += amount;
        System.out.println("成功存款: " + amount + "，当前余额: " + balance);
    }
    
    // 取款方法 - 包含业务逻辑验证
    public void withdraw(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("取款金额必须大于0");
        }
        if (amount > balance) {
            throw new IllegalArgumentException("余额不足");
        }
        balance -= amount;
        System.out.println("成功取款: " + amount + "，当前余额: " + balance);
    }
}

public class Encapsulation {
    public static void main(String[] args) {
        BankAccount account = new BankAccount("123456", "张三", 10000);
        
        // 不能直接访问私有属性
        // account.balance = 999999;  // 编译错误
        
        // 通过公共方法访问
        System.out.println("账户ID: " + account.getAccountId());
        System.out.println("账户姓名: " + account.getAccountName());
        System.out.println("账户余额: " + account.getBalance());
        
        // 通过公共方法操作
        account.deposit(5000);
        account.withdraw(3000);
    }
}
```

## 继承

继承是面向对象的第二大特性，允许一个类（子类）继承另一个类（父类）的属性和方法，实现代码的复用。

### 单继承

```java
// ObjectOriented/Inheritance.java

/**
 * 动物类 - 父类
 */
class Animal {
    protected String name;
    protected int age;
    
    public Animal() {
        System.out.println("Animal 无参构造方法被调用");
    }
    
    public Animal(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public void eat() {
        System.out.println(name + "正在吃东西");
    }
    
    public void sleep() {
        System.out.println(name + "正在睡觉");
    }
    
    public String getInfo() {
        return "名字: " + name + ", 年龄: " + age;
    }
}

/**
 * 狗类 - 继承自动物类
 */
class Dog extends Animal {
    private String breed;
    
    public Dog() {
        super();  // 调用父类构造方法
        System.out.println("Dog 无参构造方法被调用");
    }
    
    public Dog(String name, int age, String breed) {
        super(name, age);  // 调用父类有参构造方法
        this.breed = breed;
    }
    
    // 重写父类方法
    @Override
    public void eat() {
        System.out.println(name + "（" + breed + "）正在吃狗粮");
    }
    
    // 新增方法
    public void bark() {
        System.out.println(name + "正在汪汪叫");
    }
    
    public String getBreed() {
        return breed;
    }
    
    @Override
    public String getInfo() {
        return super.getInfo() + ", 品种: " + breed;
    }
}

/**
 * 猫类 - 继承自动物类
 */
class Cat extends Animal {
    public Cat(String name, int age) {
        super(name, age);
    }
    
    @Override
    public void eat() {
        System.out.println(name + "正在吃猫粮");
    }
    
    public void meow() {
        System.out.println(name + "正在喵喵叫");
    }
}

public class Inheritance {
    public static void main(String[] args) {
        Dog dog = new Dog("旺财", 3, "金毛");
        System.out.println(dog.getInfo());
        dog.eat();  // 调用重写后的方法
        dog.sleep();  // 调用父类方法
        dog.bark();  // 调用子类方法
        
        System.out.println();
        
        Cat cat = new Cat("咪咪", 2);
        cat.eat();
        cat.meow();
    }
}
```

### 方法重写与重载

```java
// ObjectOriented/OverrideOverload.java

class Parent {
    public void method() {
        System.out.println("父类 method()");
    }
    
    public void method(int num) {
        System.out.println("父类 method(int): " + num);
    }
    
    public final void finalMethod() {
        System.out.println("这是 final 方法，不能被重写");
    }
    
    private void privateMethod() {
        System.out.println("私有方法");
    }
}

class Child extends Parent {
    // 方法重写 - 方法签名必须相同
    @Override
    public void method() {
        System.out.println("子类 method()");
    }
    
    // 不是重写，是重载
    public void method(String str) {
        System.out.println("子类 method(String): " + str);
    }
    
    // 编译错误 - final 方法不能被重写
    // public void finalMethod() { }
    
    // 编译错误 - 不能重写 private 方法
    // public void privateMethod() { }
}

public class OverrideOverload {
    public static void main(String[] args) {
        Child child = new Child();
        
        // 调用重写的方法（运行时多态）
        child.method();        // 子类 method()
        child.method(123);     // 父类 method(int)
        child.method("hello"); // 子类 method(String)
        
        Parent parent = new Child();
        // 调用的是子类重写的方法
        parent.method();  // 输出：子类 method()
    }
}
```

::: danger 重写规则
1. 方法名和参数列表必须完全相同
2. 返回类型可以是父类返回类型的子类型（协变返回类型）
3. 访问权限不能比父类更严格
4. 不能抛出比父类更多的异常
5. 不能重写 static 方法或 final 方法
6. 构造方法不能被重写
:::

## 多态

多态是面向对象的第三大特性，指同一个行为具有不同的表现形式或形态。Java 通过继承和方法重写实现多态。

### 编译时多态（方法重载）

```java
// ObjectOriented/CompileTimePolymorphism.java

class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    public double add(double a, double b) {
        return a + b;
    }
    
    public int add(int a, int b, int c) {
        return a + b + c;
    }
    
    public String add(String a, String b) {
        return a + b;
    }
}

public class CompileTimePolymorphism {
    public static void main(String[] args) {
        Calculator calc = new Calculator();
        
        System.out.println(calc.add(1, 2));           // 3
        System.out.println(calc.add(1.5, 2.5));       // 4.0
        System.out.println(calc.add(1, 2, 3));        // 6
        System.out.println(calc.add("Hello", "World")); // HelloWorld
    }
}
```

### 运行时多态（方法重写）

```java
// ObjectOriented/RuntimePolymorphism.java

abstract class Shape {
    protected String color;
    
    public Shape(String color) {
        this.color = color;
    }
    
    // 抽象方法 - 子类必须实现
    public abstract double getArea();
    
    public void draw() {
        System.out.println("绘制" + color + "的形状");
    }
}

class Circle extends Shape {
    private double radius;
    
    public Circle(String color, double radius) {
        super(color);
        this.radius = radius;
    }
    
    @Override
    public double getArea() {
        return Math.PI * radius * radius;
    }
    
    @Override
    public void draw() {
        System.out.println("绘制" + color + "的圆形，面积: " + getArea());
    }
}

class Rectangle extends Shape {
    private double width;
    private double height;
    
    public Rectangle(String color, double width, double height) {
        super(color);
        this.width = width;
        this.height = height;
    }
    
    @Override
    public double getArea() {
        return width * height;
    }
    
    @Override
    public void draw() {
        System.out.println("绘制" + color + "的长方形，面积: " + getArea());
    }
}

public class RuntimePolymorphism {
    public static void main(String[] args) {
        // 父类引用指向子类对象
        Shape shape1 = new Circle("红色", 5);
        Shape shape2 = new Rectangle("蓝色", 4, 6);
        
        // 调用方法时，实际执行的是子类的方法
        shape1.draw();  // 输出：绘制红色的圆形，面积: 78.5398...
        shape2.draw();  // 输出：绘制蓝色的长方形，面积: 24.0
        
        // 使用多态进行批量处理
        Shape[] shapes = {
            new Circle("黄色", 3),
            new Rectangle("绿色", 5, 8),
            new Circle("紫色", 2)
        };
        
        double totalArea = 0;
        for (Shape shape : shapes) {
            System.out.println("形状面积: " + shape.getArea());
            totalArea += shape.getArea();
        }
        System.out.println("总面积: " + totalArea);
    }
}
```

## 抽象类与接口

### 抽象类

```java
// ObjectOriented/AbstractClass.java

/**
 * 抽象类 - 不能实例化，只能被继承
 */
abstract class Animal {
    protected String name;
    
    public Animal(String name) {
        this.name = name;
    }
    
    // 抽象方法 - 没有方法体，必须由子类实现
    public abstract void makeSound();
    
    // 普通方法
    public void eat() {
        System.out.println(name + "正在吃东西");
    }
}

/**
 * 抽象类的子类
 */
abstract class Mammal extends Animal {
    public Mammal(String name) {
        super(name);
    }
    
    // 可以选择实现部分抽象方法，保持抽象
    public abstract void move();
}

class Dog extends Mammal {
    public Dog(String name) {
        super(name);
    }
    
    @Override
    public void makeSound() {
        System.out.println(name + "：汪汪汪！");
    }
    
    @Override
    public void move() {
        System.out.println(name + "用四条腿奔跑");
    }
}

public class AbstractClass {
    public static void main(String[] args) {
        // Animal animal = new Animal();  // 编译错误
        
        Dog dog = new Dog("旺财");
        dog.makeSound();
        dog.move();
        dog.eat();
    }
}
```

### 接口

```java
// ObjectOriented/Interface.java

/**
 * 接口 - 抽象方法的集合
 */
interface Drawable {
    // 接口中的变量默认是 public static final
    int MAX_SIZE = 100;
    
    // 抽象方法（Java 8 之前）
    void draw();
    
    // 默认方法（Java 8+）
    default void setColor(String color) {
        System.out.println("设置颜色: " + color);
    }
    
    // 静态方法（Java 8+）
    static void printInfo() {
        System.out.println("这是一个可绘制的对象");
    }
}

interface Movable {
    void move();
    void stop();
}

/**
 * 一个类可以实现多个接口
 */
class Circle implements Drawable, Movable {
    private double radius;
    private String color;
    
    public Circle(double radius) {
        this.radius = radius;
    }
    
    @Override
    public void draw() {
        System.out.println("绘制半径为 " + radius + " 的圆形");
    }
    
    @Override
    public void move() {
        System.out.println("圆形正在移动");
    }
    
    @Override
    public void stop() {
        System.out.println("圆形停止移动");
    }
    
    @Override
    public void setColor(String color) {
        this.color = color;
        System.out.println("圆形颜色设置为: " + color);
    }
}

/**
 * 接口可以继承其他接口（多继承）
 */
interface AdvancedDrawable extends Drawable, Movable {
    void resize(double factor);
}

public class Interface {
    public static void main(String[] args) {
        // 接口引用指向实现类对象
        Drawable drawable = new Circle(5);
        drawable.draw();       // 调用 Circle 的 draw
        drawable.setColor("红色");  // 调用默认方法
        
        Movable movable = new Circle(3);
        movable.move();
        movable.stop();
        
        // 调用静态方法
        Drawable.printInfo();
        
        // 多接口实现
        Circle circle = new Circle(10);
        circle.draw();
        circle.move();
    }
}
```

::: tip 抽象类与接口的区别
| 区别点 | 抽象类 | 接口 |
|--------|--------|------|
| 继承 | 单继承 | 多实现 |
| 方法 | 抽象方法、默认方法、静态方法 | Java 8+ 支持默认方法和静态方法 |
| 成员变量 | 任意类型 | 只能是 public static final |
| 构造方法 | 有 | 没有 |
| 访问修饰符 | 可以有各种访问修饰符 | 方法默认 public |
| 适用场景 | 表达 "is-a" 关系 | 表达 "has-a" 关系 |
:::

## 内部类

```java
// ObjectOriented/InnerClass.java

/**
 * 外部类
 */
class OuterClass {
    private String outerField = "外部类成员";
    private static String staticOuterField = "外部类静态成员";
    
    /**
     * 成员内部类 - 可以访问外部类的所有成员
     */
    class MemberInnerClass {
        public void display() {
            System.out.println("成员内部类访问外部类成员: " + outerField);
            System.out.println("访问外部类静态成员: " + staticOuterField);
        }
    }
    
    /**
     * 静态内部类 - 不能访问外部类的非静态成员
     */
    static class StaticInnerClass {
        public void display() {
            // System.out.println(outerField);  // 编译错误
            System.out.println("静态内部类访问外部类静态成员: " + staticOuterField);
        }
    }
    
    /**
     * 局部内部类 - 定义在方法内部
     */
    public void localInnerClassDemo() {
        class LocalInnerClass {
            public void show() {
                System.out.println("局部内部类");
            }
        }
        LocalInnerClass local = new LocalInnerClass();
        local.show();
    }
    
    /**
     * 匿名内部类 - 没有名字的内部类
     */
    public void anonymousClassDemo() {
        // 匿名内部类实现接口
        Runnable runnable = new Runnable() {
            @Override
            public void run() {
                System.out.println("Runnable 匿名内部类");
            }
        };
        runnable.run();
        
        // Lambda 表达式（匿名内部类的简化）
        Runnable lambdaRunnable = () -> System.out.println("Lambda 表达式");
        lambdaRunnable.run();
    }
}

public class InnerClass {
    public static void main(String[] args) {
        // 创建成员内部类对象
        OuterClass outer = new OuterClass();
        OuterClass.MemberInnerClass memberInner = outer.new MemberInnerClass();
        memberInner.display();
        
        // 创建静态内部类对象
        OuterClass.StaticInnerClass staticInner = new OuterClass.StaticInnerClass();
        staticInner.display();
        
        // 局部内部类和匿名内部类
        outer.localInnerClassDemo();
        outer.anonymousClassDemo();
    }
}
```

## Object 类

Java 中所有类的根类，提供了一些重要的方法。

```java
// ObjectOriented/ObjectClass.java

class Person {
    private String name;
    private int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    @Override
    public String toString() {
        return "Person{name='" + name + "', age=" + age + "}";
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Person person = (Person) obj;
        return age == person.age && java.util.Objects.equals(name, person.name);
    }
    
    @Override
    public int hashCode() {
        return java.util.Objects.hash(name, age);
    }
}

public class ObjectClass {
    public static void main(String[] args) {
        Person p1 = new Person("张三", 25);
        Person p2 = new Person("张三", 25);
        Person p3 = new Person("李四", 30);
        
        // toString()
        System.out.println("p1.toString(): " + p1);
        System.out.println("p1: " + p1.toString());
        
        // equals()
        System.out.println("p1.equals(p2): " + p1.equals(p2));  // true
        System.out.println("p1.equals(p3): " + p1.equals(p3));  // false
        
        // hashCode()
        System.out.println("p1.hashCode(): " + p1.hashCode());
        System.out.println("p2.hashCode(): " + p2.hashCode());
        
        // getClass()
        System.out.println("p1.getClass(): " + p1.getClass());
        
        // == 与 equals 的区别
        System.out.println("p1 == p2: " + (p1 == p2));  // false（引用比较）
        System.out.println("p1.equals(p2): " + p1.equals(p2));  // true（内容比较）
    }
}
```

## 相关专题

- [面向对象核心（OOP）](../OOP/index.md)
- [Java 并发](../Multithreading/index.md)
