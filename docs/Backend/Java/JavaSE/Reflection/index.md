# Java 反射与注解

<p style="text-align:center;"><img src="./assets/java-logo.png" style="zoom:75%;" /></p>

反射（Reflection）让 Java 程序在**运行时**动态获取类的结构并操作对象，注解（Annotation）则是一种附着在代码上的元数据。二者组合是 Spring、MyBatis、Lombok 等框架的底层基石，也是理解 Java 生态的关键。

本专题默认基于 **Java 25 LTS**（2025 年 9 月发布），涉及版本差异（如 JDK 23+ 注解处理默认关闭、JDK 25 反射访问限制）时在文中标注。

- [反射概述与 Class 对象](Overview/index.md)
- [字段与方法反射](FieldsMethods/index.md)
- [构造器与对象创建](Constructor/index.md)
- [动态代理](DynamicProxy/index.md)
- [注解：定义与使用](Annotation/index.md)
- [注解处理器（APT）](AnnotationProcessor/index.md)
- [实战：注解驱动简易 ORM](Practice/index.md)
- [常见问题与最佳实践](FAQ/index.md)
