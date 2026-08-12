# listObjs() 方法

`listObjs()`方法用于取出通过MybatisPlus查询到的数据并放入List中，其中取出的数据并不包括对象所有的字段，最多只能返回一个字段。

- 返回所有数据：public List listObjs();
- 返回指定条件下的数据：public List listObjs(Wrapper wrapper);
- 可以将返回对象进行转换：public List listObjs(Function mapper);
- 返回指定条件下的数据并将返回对象进行转换：public List listObjs(Wrapper wrapper, Function mapper);

**源码**：

```java
default List<Object> listObjs() {
	return listObjs(Function.identity());
}


default <V> List<V> listObjs(Function<? super Object, V> mapper) {
    return listObjs(Wrappers.emptyWrapper(), mapper);
}

default List<Object> listObjs(Wrapper<T> queryWrapper) {
    return listObjs(queryWrapper, Function.identity());
}

default <V> List<V> listObjs(Wrapper<T> queryWrapper, Function<? super Object, V> mapper) {
    return getBaseMapper().selectObjs(queryWrapper).stream().filter(Objects::nonNull).map(mapper).collect(Collectors.toList());    
}
```

对于Function入参，其中通过实现apply接口，进行类型转换，其中Object类型的参数是我们实体类中使用Mp的`@TableId`注解标注的属性。

如果没有标注注解，则根据属性名对应数据库表的字段进行匹配查找 (参数一般都是主键id，除非使用`@TableId`注解标注了其他字段)。

分为：

- 查询主键。此时会将查询到的所有主键id放入list中。 


- select *。默认查询数据库的主键，查询结果为主键（id），并将其放入list中。


- 查询非主键的其他字段，将查询字段放入list中。


- 查询多个字段，默认查询传入的第一个字段，并将第一个字段的查询结果放入list中。

****

在实际开发中使用Springboot整合Mybatis-Plus时，调用底层baseMapper封装好的`selectObjs()`方法或者service层封装的`listObjs()`方法时返回的是`List<Object>`集合，需要将Object对象转换为指定的对象类型，例如String等。

解决方法：自定义转换工具类，将Object对象集合转换为指定对象集合

```java
public class SwitchUtil {
    public static <T> List<T> objToList(Object obj, Class<T> cla) {
        List<T> list = new ArrayList<T>();
        if (obj instanceof ArrayList<?>) {
            for (Object o : (List<?>) obj) {
                list.add(cla.cast(o));
            }
            return list;
        }
        return null;
    }
}
```

使用方法：

```java
List<Object> infos = businessService.listObjs(wrapper);
List<String> stockCodes = SwitchUtil.objToList(infos, String.class);
```

