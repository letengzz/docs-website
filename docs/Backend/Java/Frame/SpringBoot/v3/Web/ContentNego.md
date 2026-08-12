# 内容协商

内容协商机制是指服务器根据客户端的请求来决定返回资源的最佳表示形式 (一套系统适配多端数据返回)。

- 客户端要JSON，咱就响应JSON。
- 客户端要XML，咱就响应XML。
- 客户端要YAML，咱就响应YAML。

因此，在现代的开发中，不同的客户端可能需要后端系统返回不同格式的数据。总之后端应该满足这种多样化的需求。

![img](assets/202308021001821.png)

## 多端内容适配

### 默认规则

通常通过HTTP请求头 (如 Accept) 或请求参数 (如 format) 来指定客户端偏好接收的内容类型 (如JSON、XML等)。服务器会根据这些信息选择最合适的格式进行响应。

**SpringBoot 多端内容适配**：

1. **基于请求头内容协商(默认开启)**：

   客户端向服务端发送请求，携带HTTP标准的**Accept请求头**。

   **Accept**: `application/json`、`text/xml`、`text/yaml`

   服务端根据**客户端请求头期望的数据类型进行动态返回**

   ![image-20230804222924773](assets/202308042229351.png)

2. **基于请求参数内容协商(需要开启)**：

   1. 送请求 GET /projects/spring-boot?format=json

   1. 匹配到 `@GetMapping("/projects/spring-boot")`

   1. 根据**参数协商**，优先返回 json 类型数据 (**需要开启参数匹配设置**)

   1. 发送请求 GET /projects/spring-boot?format=xml,优先返回 xml 类型数据

      ![image-20230804223135250](assets/202308042231999.png)

默认支持把对象转化为JSON，因为默认web场景导入了Jackson处理的包：jackson-core

```java
@Data
public class Person {
    private Long id;
    private String userName;
    private String email;
    private Integer age;
}
```

```java
@RestController
public class PersonController {
    @RequestMapping("/person")
    public Person person(){
        Person person = new Person();
        person.setId(1L);
        person.setUserName("张三");
        person.setEmail("111@qq.com");
        person.setAge(22);
        return person;
    }
}
```

![image-20230805152218210](assets/202308051522439.png)

**例**：请求同一个接口，可以返回json和xml不同格式数据：

1. 引入支持写出xml内容依赖 (jackson 支持把数据写为xml)：

   ```xml
   <dependency>
       <groupId>com.fasterxml.jackson.dataformat</groupId>
       <artifactId>jackson-dataformat-xml</artifactId>
   </dependency>
   ```

2. 标注注解：

   ```java
   @JacksonXmlRootElement  // 可以写出为xml文档
   @Data
   public class Person {
       private Long id;
       private String userName;
       private String email;
       private Integer age;
   }
   ```

3. 进行了内容协商 默认返回了文本：

   ![image-20230805152754450](assets/202308051527240.png)

4. 使用**基于请求头内容协商**：

   ![image-20230805153315918](assets/202308051533147.png)

   ![image-20230805153423806](assets/202308051534407.png)

5. 使用**基于请求参数内容协商**：开启基于请求参数的内容协商

   ```properties
   # 开启基于请求参数的内容协商功能。 默认参数名：format。 默认此功能不开启
   spring.mvc.contentnegotiation.favor-parameter=true
   # 指定内容协商时使用的参数名。默认是 format
   spring.mvc.contentnegotiation.parameter-name=type
   ```

   ```yaml
   spring:
     mvc:
       contentnegotiation:
         # 开启基于请求参数的内容协商功能。 默认参数名：format。 默认此功能不开启
         favor-parameter: true
         # 指定内容协商时使用的参数名。默认是 format
         parameter-name: type
   ```

   ![image-20230805154210686](assets/202308051542142.png)

### 配置协商规则与支持类型

修改**内容协商方式**：

```properties
#使用参数进行内容协商
spring.mvc.contentnegotiation.favor-parameter=true
#自定义参数名，默认为format
spring.mvc.contentnegotiation.parameter-name=myparam
```

```yaml
spring:
  mvc:
    contentnegotiation:
      # 开启基于请求参数的内容协商功能。 默认参数名：format。 默认此功能不开启
      favor-parameter: true
      # 指定内容协商时使用的参数名。默认是 format
      parameter-name: myparam
```

大多数 MediaType 都是开箱即用的。也可以**自定义内容类型**：

```properties
spring.mvc.contentnegotiation.media-types.yaml=text/yaml
```

```yaml
spring:
  mvc:
    contentnegotiation:
      # 新增一种媒体类型
      media-types:
        yaml: text/yaml
```

## 自定义内容返回

**步骤**：

- 配置媒体类型支持:

  - `spring.mvc.contentnegotiation.media-types.yaml=text/yaml`

- 编写对应的`HttpMessageConverter`，要告诉Boot这个支持的媒体类型

- 把MessageConverter组件加入到底层
  - 容器中放一个`WebMvcConfigurer` 组件，并配置底层的`MessageConverter`

### 增加yaml返回支持

任何一个能够处理yaml格式数据的库都可以，这里选择使用jackson的库，因为它既可以处理json，xml，又可以处理yaml。

导入依赖：

```xml
<!-- 支持返回YAML格式数据-->
<dependency>
    <groupId>com.fasterxml.jackson.dataformat</groupId>
    <artifactId>jackson-dataformat-yaml</artifactId>
</dependency>
```

把对象写出成YAML：

```java
public static void main(String[] args) throws JsonProcessingException {
	Person person = new Person();
    person.setId(1L);
    person.setUserName("张三");
    person.setEmail("aaa@qq.com");
    person.setAge(18);

    //YAMLGenerator.Feature.WRITE_DOC_START_MARKER：yaml开头“---”
    YAMLFactory factory = new YAMLFactory().disable(YAMLGenerator.Feature.WRITE_DOC_START_MARKER);
    ObjectMapper mapper = new ObjectMapper(factory);

    String s = mapper.writeValueAsString(person);
    System.out.println(s);
}
```

默认支持xml和json两种媒体类型，要支持yaml格式的，需要新增一个yaml媒体类型，在springboot的配置文件中进行配置：

```properties
#新增一种媒体类型
spring.mvc.contentnegotiation.media-types.yaml=text/yaml
```

```yaml
#新增一种媒体类型
spring:
  mvc:
    contentnegotiation:
      media-types:
        yaml: text/yaml
```

增加`HttpMessageConverter`组件，专门负责把对象写出为yaml格式：

```java
@Bean
public WebMvcConfigurer webMvcConfigurer(){
    return new WebMvcConfigurer() {
        @Override //配置一个能把对象转为yaml的messageConverter
        public void configureMessageConverters(List<HttpMessageConverter<?>> converters) {
            converters.add(new MyYamlHttpMessageConverter());
        }
    };
}
```

### HttpMessageConverter写法

继承`AbstractHttpMessageConverter`：

```java
public class MyYamlHttpMessageConverter extends AbstractHttpMessageConverter<Object> {

    private ObjectMapper objectMapper = null; //把对象转成yaml

    public MyYamlHttpMessageConverter(){
        //告诉SpringBoot这个MessageConverter支持哪种媒体类型
        //媒体类型
        // 让 消息转换器 和 媒体类型 application/yaml 绑定在一起。
        super(new MediaType("text", "yaml", Charset.forName("UTF-8")));
        YAMLFactory factory = new YAMLFactory()
                .disable(YAMLGenerator.Feature.WRITE_DOC_START_MARKER);
        this.objectMapper = new ObjectMapper(factory);
    }

    //支持某种类型
    @Override
    protected boolean supports(Class<?> clazz) {
        //只要是对象类型，不是基本类型 此判断忽略 可自行添加
        // 表示User类型的数据支持yaml，其他类型不支持
        //return User.class.isAssignableFrom(clazz);
        return true;
    }

    //重写读指定对象的操作 处理 @RequestBody（将提交的yaml格式数据转换为java对象）
    @Override  //@RequestBody
    protected Object readInternal(Class<?> clazz, HttpInputMessage inputMessage) throws IOException, HttpMessageNotReadableException {
        return null;
    }

    //重写写指定对象的操作 处理 @ResponseBody（将java对象转换为yaml格式的数据）
    @Override //@ResponseBody
    protected void writeInternal(Object methodReturnValue, HttpOutputMessage outputMessage) throws IOException, HttpMessageNotWritableException {

        //try-with写法，自动关流
        try(OutputStream os = outputMessage.getBody()){
            this.objectMapper.writeValue(os,methodReturnValue);
        }

    }
}
```

![image-20230805230556304](assets/202308052305785.png)

![image-20230805230615593](assets/202308052306842.png)

## 内容协商原理-`HttpMessageConverter`

通过定制 `HttpMessageConverter` 来实现多端内容协商完成请求/响应时的数据格式转换的。

### `@ResponseBody`由`HttpMessageConverter`处理

标注了`@ResponseBody`的返回值 将会由支持它的 `HttpMessageConverter`写给浏览器

1. 如果controller方法的返回值标注了 `@ResponseBody `注解

   1. 请求进来先来到`DispatcherServlet`的`doDispatch()`进行处理
   1. 找到一个 `HandlerAdapter `适配器。利用适配器执行目标方法
   1. `RequestMappingHandlerAdapter`来执行，调用`invokeHandlerMethod()`来执行目标方法
   1. 目标方法执行之前，准备好两个东西：

      1. `HandlerMethodArgumentResolver`：参数解析器，确定目标方法每个参数值
      1. `HandlerMethodReturnValueHandler`：返回值处理器，确定目标方法的返回值改怎么处理

   1. `RequestMappingHandlerAdapter` 里面的`invokeAndHandle()`真正执行目标方法
   1. 目标方法执行完成，会返回**返回值对象**
   1. **找到一个合适的返回值处理器** `HandlerMethodReturnValueHandler`
   1. 最终找到 `RequestResponseBodyMethodProcessor`能处理 标注了 `@ResponseBody`注解的方法
   1. `RequestResponseBodyMethodProcessor` 调用`writeWithMessageConverters `，利用`MessageConverter`把返回值写出去

上面解释：`@ResponseBody`由`HttpMessageConverter`处理

1. `HttpMessageConverter` 会**先进行内容协商**

   1. 遍历所有的`MessageConverter`看谁支持这种**内容类型的数据**

   1. 默认`MessageConverter`：

      ![img](assets/202308051623295.png)

   1. 最终因为要`json`所以`MappingJackson2HttpMessageConverter`支持写出json

   1. jackson用`ObjectMapper`把对象写出去

### `WebMvcAutoConfiguration`提供几种默认`HttpMessageConverters`

- `EnableWebMvcConfiguration`通过 `addDefaultHttpMessageConverters`添加了默认的`MessageConverter`：
  - `ByteArrayHttpMessageConverter`： 支持字节数据读写。用于将字节数组(byte[])与HTTP消息体之间进行转换。这通常用于处理二进制数据，如图片或文件。
  - `StringHttpMessageConverter`： 支持字符串读写。用于将字符串(String)与HTTP消息体之间进行转换。它支持多种字符集编码，能够处理纯文本内容。
  - `ResourceHttpMessageConverter`：支持资源读写。用于将Spring的Resource对象与HTTP消息体之间进行转换。Resource是Spring中表示资源的接口，可以读取文件等资源。这个转换器对于下载文件或发送静态资源有用。
  - `ResourceRegionHttpMessageConverter`: 支持分区资源写出。用于处理资源的部分内容（即“Range”请求），特别是当客户端请求大文件的一部分时。这对于实现视频流媒体等功能很有用。
  - `AllEncompassingFormHttpMessageConverter`：支持表单xml/json读写。用于处理表单，是一个比较全面的form消息转换器。处理标准的application/x-www-form-urlencoded格式的数据，以及包含文件上传的multipart/form-data格式的数据。
  - `MappingJackson2HttpMessageConverter`： 支持请求响应体Json读写。使用Jackson库来序列化和反序列化JSON数据。可以将Java对象转换为JSON格式的字符串，反之亦然。

默认8个：

![img](assets/202308052235292.png)

系统提供默认的MessageConverter 功能有限，仅用于json或者普通返回数据。额外增加新的内容协商功能，必须增加新的`HttpMessageConverter`

## WebMvcConfigurationSupport

提供了很多的默认配置。判断系统中是否有相应的类：如果有，就加入相应的HttpMessageConverter

![image-20230805224337466](assets/202308052243134.png)
