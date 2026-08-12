# MyBatis 常见错误

- [mabatis报错:Result typenot match for select id=XXX](#jump1)
- [判断Integer类型，值为0动态SQL不生效](#jump2)

## <span id="jump1">mabatis报错：Result type not match for select id=XXX</span>

在使用模块编程时会出现![image-20230111110547086](assets/202303011650479.png)

实际上并不影响运行，但是会飘红

:::tip 原因

两个模块使用了相同的名字，更改名字即可。

:::

## <span id="jump2">判断Integer类型,值为0动态SQL不生效</span>

SQL语句：

```xml
select * from tableName
where 1 = 1
<if test="status != null and status != ''">and `status` = #{status}</if>
```

:::danger 错误

当status=0时动态SQL不生效。

:::

通过分析Mybatis的源码分析可知：mybatis在预编译sql时，使用OGNL表达式来解析if标签，对于Integer类型属性，在判断不等于''时，例如status !=''，OGNL会返回''的长度，

源码：`(s.length() == 0) ? 0.0 : Double.parseDouble( s )`

因此表达式status != ''被当做status != 0来判断，所以当status=0时，if条件判断不通过。

只需要将status!=''条件去掉就可以解决上面这个问题。

尽量使用包装类：java的基本数据类型都会有默认值，如果直接使用基本数据类型会给查询带来不必要的麻烦，所以尽量使用包装类代替。
