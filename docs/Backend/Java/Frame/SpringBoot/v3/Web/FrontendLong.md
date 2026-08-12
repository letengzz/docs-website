# 前端丢失大Long精度问题

## 将Long转换为String

JSON数据：后端对象转为JSON交给前端。利用内部的Converters转换器。

转换器最终调用Jackson的ObjectMapper将对象转为Json，而对象转为Json转是jackson决定的。

## 不改变模型类

JSON 相关的注解不要标注在entity实体类，entity和数据库对应。

JSON 相关注解标注在vo上，vo和entity是一个模型。只不过entity对应数据库，vo对应前端，对前端的所有规则都在vo中设置。

响应给前端的和接收前端的都用vo，自定义vo和entity属性进行对拷即可。

### 局部解决

```java
@Data
public class SysResource implements Serializable {
    /**
     * 主键id
     */
    @JsonSerialize(using = LongToStringConverter.class)
    private Long id;
}
```

```java
@Component
public class LongToStringConverter extends JsonSerializer<Long> {

    @Override
    public void serialize(Long aLong, JsonGenerator jsonGenerator,
                          SerializerProvider serializerProvider) throws IOException {
        jsonGenerator.writeString(aLong.toString());
    }
}
```

### 统一解决

```java
//统一将 Long 类型序列化为 String
@Configuration
public class JacksonConfiguration {

   	//定义转换规则
    @Bean
    public Jackson2ObjectMapperBuilderCustomizer jackson2ObjectMapperBuilderCustomizer() {
        return builder -> {
            // 把 Long 类型序列化为 String
            builder.serializerByType(Long.class, ToStringSerializer.instance);
        };
    }
}
```
