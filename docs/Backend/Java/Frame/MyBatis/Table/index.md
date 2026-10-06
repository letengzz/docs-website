# MyBatis 表结构专题

这一组页面回答的是「**MyBatis 的映射到底贴着什么样的数据库结构写**」——`t_dept` / `t_emp`、`student`、`user` 三组练习表各自覆盖一类典型的映射场景：**多表关联与连接查询**、**一对多与类型处理器**、**通用 CRUD 与主键回填**。

一句话定位：**这一组页面是配套的练习用表与它们的建表语句**，配合 [MyBatis 核心映射](../CoreMapping.md)、[动态 SQL](../DynamicSQL.md) 与 [特殊操作](../SpecialOperation.md) 食用——每张表都对应上面几页里的一类写法。

## 子页导航

- [关于 t_dept、t_emp 表相关操作](dept_emp.md)：**多表关联与连接查询**的典型场景，用来练多参数映射与结果集嵌套
- [关于 student 表相关操作](student.md)：**一对多与类型处理器**，用来练 `resultMap` 的 `collection` 与自定义 `TypeHandler`
- [关于 user 表相关操作](user.md)：**通用 CRUD 与主键回填**，用来练 `useGeneratedKeys` 与 `keyProperty`

## 怎么用这三张表

1. 先按各页给出的建表语句在本地库建表（`CREATE TABLE` 语句完整可复制）。
2. 再回到 [MyBatis 核心映射](../CoreMapping.md)，把该页的映射写法套到表上，跑一遍查询。
3. 需要造数据时按各页的 `INSERT` 示例插入几行，**不要只建表不插数据**——映射问题的表现往往依赖数据分布（例如 `collection` 在结果为空时的行为）。

::: tip 章节关系
这三页是**练习数据与结构**，不讲 MyBatis 的 API；API 与映射语法分别见 [MyBatis 目录页](../index.md) 下的核心映射、动态 SQL、分页、缓存等页。
:::

## 相关页面

- [MyBatis 目录页](../index.md)：全部子页入口
- [MyBatis 核心映射](../CoreMapping.md)：`resultMap`、`association` 与 `collection`
- [MyBatis 动态 SQL](../DynamicSQL.md)：`<if>` / `<foreach>` / `<choose>` 与复合条件的写法
- [MyBatis 分页](../Paging.md)：这些表在分页场景下的查询组织
- [MyBatis 缓存](../Cache.md)：一级与二级缓存对「同一张表多次查询」的影响
