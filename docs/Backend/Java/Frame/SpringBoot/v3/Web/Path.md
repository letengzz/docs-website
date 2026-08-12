# 路径匹配

**Spring5.3** 之后加入了更多的请求路径匹配的实现策略：以前只支持 AntPathMatcher 策略, 现在提供了 **PathPatternParser** 策略。并且可以指定到底使用那种策略。

在`Spring Boot3`中，对web请求的路径匹配提供了两种规则：

1. AntPathMatcher (Ant风格)
2. PathPatternParser (从Spring5.3中引入的。在SpringBoot2.4中引入的。效率比Ant高，一般新项目中使用)

## 路径匹配相关源码

底层选择路径匹配规则的源码是：

![](assets/img202411222312359.png)

## Ant风格路径用法

Ant 风格的路径模式**语法规则**：

- `*`：表示**任意数量**的字符。匹配任意长度的任意字符序列 (不包括路径分隔符)。

  例：/foo/\*.html 匹配 /foo/bar.html 和 /foo/baz.html。

- `?`：表示任意**一个字符**。匹配任意单个字符。

  例：/foo?bar 匹配 /foobar 和 /fooxbar。

- `**`：表示 **任意数量的目录**。匹配任意数量的目录层级。

  例：/foo/\*\* 匹配 /foo/bar、/foo/bar/baz 和 /foo/bar/baz/qux。

- `{}`：表示一个命名的模式**占位符**。路径变量，用于提取路径的一部分作为参数。

  例：/users/{userId} 匹配 /users/123，提取 userId=123。

- `[]`：表示**字符集合**，例如[a-z]表示小写字母。匹配指定范围内的单个字符。

  例：/foo[a-z]bar 匹配 /fooabar、/foobbar 等。

例如：

- `*.html`：匹配任意名称，扩展名为.html的文件。
- `/folder1/*/*.java`：匹配在folder1目录下的任意两级目录下的.java文件。
- `/folder2/**/*.jsp`：匹配在folder2目录下任意目录深度的.jsp文件。
- `/{type}/{id}.html`：匹配任意文件名为{id}.html，在任意命名的{type}目录下的文件。

:::danger 注意

Ant 风格的路径模式语法中的**特殊字符需要转义**：

- 要匹配文件路径中的星号，则需要转义为`\\*`
- 要匹配文件路径中的问号，则需要转义为`\\?`

:::

## 模式切换

SpringBoot3中默认使用的是`PathPatternParser`，不需要任何配置。如果要使用`AntPathMatcher`需要切换。

**修改路径匹配策略**：

```properties
# 改变路径匹配策略：
# ant_path_matcher 老版策略；
# path_pattern_parser 新版策略；
spring.mvc.pathmatch.matching-strategy=ant_path_matcher
```

## AntPathMatcher 与 PathPatternParser

- PathPatternParser 在 jmh 基准测试下，有 6~8 倍吞吐量提升，降低 30%~40%空间分配率
- PathPatternParser 兼容 AntPathMatcher语法，并支持更多类型的路径模式
- PathPatternParser "`**`" **多段匹配**的支持**仅允许在模式末尾使用**

```java
/**
* 默认使用 PathPatternParser 进行路径匹配
* 不能匹配 **在中间的情况，剩下的和 AntPathMatcher 语法兼容
*/
@GetMapping("/a*/b?/{p1:[a-f]+}")
public String hello(HttpServletRequest request,
                        @PathVariable("p1") String path) {

	log.info("路径变量p1： {}", path);
    //获取请求路径
    String uri = request.getRequestURI();
    return uri;
}
```

![image-20230804215103710](assets/202308042151831.png)

:::danger 注意

- 当使用`**`不在末尾时，使用PathPatternParser模式会提示使用AntPathMatcher，所以如果路径中间需要有 `**`，替换成ant风格路径

  ![image-20230804215403804](assets/202308042154951.png)

  ```properties
  spring.mvc.pathmatch.matching-strategy=ant_path_matcher
  ```

  ```yaml
  # 改变路径匹配策略：ant_path_matcher 老版策略；path_pattern_parser 新版策略
  spring:
    mvc:
      pathmatch:
        matching-strategy: ant_path_matcher
  ```

  ![image-20230804220011048](assets/202308042200968.png)

- 使用默认的路径匹配规则，是由 PathPatternParser 提供的

  ![image-20230804222136420](assets/202308042221159.png)

  ![image-20230804222217814](assets/202308042222032.png)

:::
