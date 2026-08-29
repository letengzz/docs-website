# 常见问题与最佳实践

汇总反射与注解开发中最常遇到的问题，覆盖性能、安全、框架协作与调试，方便快速查阅。

## 性能类

### 反射真的慢吗？慢多少？

反射调用比直接调用慢，但**没有传说中那么可怕**：

1. 慢的部分主要是方法查找与访问检查；
2. 缓存 `Method`/`Field` 对象后，差距显著缩小；
3. JDK 17+ 的 `MethodHandle`、`VarHandle` 性能接近直接调用；
4. 现代 JVM 对反射有内联缓存优化。

```java
// FAQ/ReflectPerfTip.java
import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.Map;

public class ReflectPerfTip {
    // 缓存 Method，避免每次查找
    private static final Map<String, Method> CACHE = new HashMap<>();

    static Method methodOf(Class<?> clazz, String name) throws Exception {
        return CACHE.computeIfAbsent(clazz.getName() + "#" + name,
                k -> {
                    try {
                        return clazz.getMethod(name);
                    } catch (Exception e) {
                        throw new RuntimeException(e);
                    }
                });
    }

    public static void main(String[] args) throws Exception {
        Method m = methodOf(String.class, "length");
        System.out.println(m.invoke("hello"));
    }
}
```

### 反射性能优化三板斧

1. **缓存元数据**：`Class`、`Method`、`Field`、`Constructor` 只取一次；
2. **批量反射**：减少 `setAccessible` 次数，一次设置整类字段；
3. **编译期替代**：能用 APT/泛型/接口解决就不反射（Lombok 的思路）。

## 安全类

### `setAccessible(true)` 在 JDK 9+ 报错怎么办？

模块化 JDK 下，跨模块访问私有成员受 `java.base` 等模块封装限制：

```text
java.lang.reflect.InaccessibleObjectException
```

解决办法：

| 方案 | 说明 |
| --- | --- |
| 同模块内访问 | 自己的类私有成员反射无限制 |
| `--add-opens` | JVM 启动参数打开指定包，如 `--add-opens java.base/java.lang=ALL-UNNAMED` |
| 避免私有访问 | 框架改用 public API、`MethodHandles.privateLookupIn`（受限） |

::: danger 非法反射访问
JDK 25 进一步收紧了非法反射访问（`sun.misc.Unsafe` 与跨模块强访问），**应用应通过公开 API 或 `--add-opens` 显式声明**，不要依赖 hack。
:::

### 反射有安全风险吗？

反射本身不是漏洞，但它可能被攻击链利用：

- 反序列化 + 反射 → RCE（历史 Fastjson/原生序列化漏洞）；
- `setAccessible(true)` 绕过访问控制；
- 动态代理被滥用来混淆恶意行为。

防御：不反序列化不可信数据、最小权限、及时升级依赖。

## 注解类

### 为什么 `getAnnotation` 返回 null？

排查顺序：

1. 注解的 `@Retention` 是否为 `RUNTIME`（默认 CLASS，运行期不可反射）；
2. 注解是否真的标注在目标元素上（位置与 `@Target` 匹配）；
3. 是否通过代理/继承获取（`@Inherited` 只对类生效）；
4. 是否用错 API（`getAnnotation` vs `getDeclaredAnnotation` vs `getAnnotationsByType`）。

### 注解能不能继承？

`@Inherited` 让**子类继承父类上的注解**，但仅限类级别；接口、方法、字段上的注解不继承。`@Repeatable` 则需要配套容器注解才能重复标注。

### 注解里能放对象吗？

不能。注解成员类型只能是：基本类型、`String`、`Class`、枚举、注解、以上类型的数组。需要复杂配置时用 `Class<?>` 引用配置类，或改用 XML/属性文件。

## 动态代理类

### Spring AOP 为什么不生效？

常见原因：

| 原因 | 表现 | 解决 |
| --- | --- | --- |
| 目标没有接口 | JDK 代理无法创建 | 配置 `proxy-target-class=true` 用 CGLIB |
| 方法不是 public | 代理无法拦截 | 切点只对 public 方法生效 |
| `final` 方法 | CGLIB 无法覆写 | 去掉 final |
| 自调用 | `this.method()` 不走代理 | 注入代理对象或拆类 |
| 类没注册 Bean | 无代理对象 | 确认 `@Component`/扫描范围 |

### JDK 代理和 CGLIB 怎么选？

Spring Boot 2.x+ 默认 CGLIB（`spring.aop.proxy-target-class=true`）；显式规则：

- 目标有接口且关心接口隔离 → JDK 代理；
- 无接口或需要代理具体类 → CGLIB；
- 绝大多数场景直接依赖 Spring 默认配置即可。

## 框架协作类

### MyBatis 的 Mapper 为什么不用写实现类？

MyBatis 在启动时用 **JDK 动态代理**为 Mapper 接口生成代理对象，`invoke` 里根据方法名/注解查找 SQL 并执行。接口 + 代理让「声明式 SQL」成为可能。

### Lombok 是反射吗？

不是。Lombok 是**编译期注解处理器（APT）**：在 javac 阶段直接生成 getter/setter/构造器代码，运行期没有反射开销。这也是「能编译期解决就不用运行期反射」的代表。

### 反射与泛型擦除的关系？

泛型类型参数在运行期被擦除，但 `getGenericSuperclass()`、`getGenericReturnType()` 可以读到字节码中保留的泛型签名（如 `List<String>`）。Spring `ResolvableType`、Jackson `TypeReference` 都基于此。

## 最佳实践清单

::: tip 反射/注解代码检查清单
1. 注解是否声明 `@Retention(RUNTIME)`（需要运行期读取时）？
2. 是否缓存了 `Class`/`Method`/`Field` 元数据？
3. `getField` vs `getDeclaredField` 是否选对？
4. 私有成员访问是否考虑模块化限制与 `--add-opens`？
5. 动态代理是否确认了接口/代理方式？
6. 生成 SQL 等动态内容是否做了注入防护？
7. 业务代码能否用接口/泛型/APT 替代反射？
:::

## 参考资料

- [Oracle 反射教程](https://docs.oracle.com/javase/tutorial/reflect/index.html)
- [Oracle 注解教程](https://docs.oracle.com/javase/tutorial/java/annotations/index.html)
- [Spring AOP 文档](https://docs.spring.io/spring-framework/reference/core/aop.html)
- [Lombok 文档](https://projectlombok.org/)
