# 封装SqlSessionUtils工具类

```java
public SqlSession SqlSessionUtils()  {
	InputStream is = null;
	try {
		is = Resources.getResourceAsStream("mybatis核心配置文件");
    } catch (IOException e) {
        throw new RuntimeException(e);
	}
    SqlSessionFactory build = new SqlSessionFactoryBuilder().build(is);
    return build.openSession(true);
}
```

