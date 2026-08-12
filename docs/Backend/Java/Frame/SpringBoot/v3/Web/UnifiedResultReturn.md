# 统一结果返回

对于前后端分离的系统来说，为了降低沟通成本，有必要给前端系统开发人员返回统一格式的JSON数据。多数开发团队一般都会封装一个RestBean对象来解决统一响应格式的问题。

设计目的：
1. 统一API响应格式，便于前端统一处理。
2. 封装业务状态码和错误信息，提高可读性。
3. 支持泛型，灵活处理不同类型的返回数据。
4. 提供静态工厂方法，简化对象创建过程。

响应格式设计：
```json
{
  "code": 200,           // 业务状态码
  "message": "操作成功",  // 响应消息
  "data": {...}          // 具体数据（可为null）
}
```

HTTP状态码 vs 业务状态码：

* HTTP状态码：由Web服务器返回，表示HTTP请求的状态。
* 业务状态码：由应用程序定义，表示业务操作的结果。
* 本系统约定：200成功，500业务失败，可扩展其他错误码。

前后端协作：

* 前端根据code字段判断操作是否成功。
* message字段可直接显示给用户。
* data字段包含具体的业务数据。

使用Fastjson2处理JSON，导入依赖：

```xml
<dependency>
    <groupId>com.alibaba.fastjson2</groupId>
    <artifactId>fastjson2</artifactId>
    <version>2.0.47</version>
</dependency>
```

记录类作为统一返回结果：

```java [com.hjc.entity.RestBean]
public record RestBean<T>(int code, T data, String message) {
    //请求成功
    public static <T> RestBean<T> success(T data){
        return new RestBean<>(200,data,"请求成功");
    }

    //请求成功 无data
    public static <T> RestBean<T> success(){
        return RestBean.success(null);
    }

    //请求失败
    public  static <T> RestBean<T> failure(int code,String message){
        return new RestBean<>(code,null,message);
    }

    //转化为JSON字符串
    public String asJsonString(){
        //JSONWriter.Feature.WriteNulls 防止null值错误
        return JSON.toJSONString(this, JSONWriter.Feature.WriteNulls);
    }

}
```

使用：

```java
@GetMapping("/list")
private RestBean<Void> list(){
        return RestBean.success();
}
```
