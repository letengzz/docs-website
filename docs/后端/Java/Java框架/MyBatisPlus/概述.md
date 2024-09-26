# Mybatis-Plus简介

MyBatis-Plus(简称 MP)是一个 MyBatis 的**增强工具**，在 MyBatis 的基础上**只做增强不做改变，为简化开发、提高效率而生**。

**MyBatis-Plus提供了通用的mapper和service，可以在不编写任何SQL语句的情况下，快速的实现对单表的CRUD、批量、逻辑删除、分页等操作。**

- **官方地址**：http://mp.baomidou.com 

- **代码发布地址**： 

  Github: https://github.com/baomidou/mybatis-plus 

  Gitee: https://gitee.com/baomidou/mybatis-plus 

- **文档发布地址**：https://baomidou.com/pages/24112f

****

**特性**：

- **无侵入**：只做增强不做改变，引入它不会对现有工程产生影响，如丝般顺滑
- **损耗小**：启动即会自动注入基本 CURD，性能基本无损耗，直接面向对象操作
- **强大的 CRUD 操作**：内置通用 Mapper、通用 Service，仅仅通过少量配置即可实现单表大部分 CRUD 操作，更有强大的条件构造器，满足各类使用需求
- **支持 Lambda 形式调用**：通过 Lambda 表达式，方便的编写各类查询条件，无需再担心字段写错
- **支持主键自动生成**：支持多达 4 种主键策略（内含分布式唯一 ID 生成器 - Sequence），可自由配置，完美解决主键问题
- **支持 ActiveRecord 模式**：支持 ActiveRecord 形式调用，实体类只需继承 Model 类即可进行强大的 CRUD 操作
- **支持自定义全局通用操作**：支持全局通用方法注入 (Write once, use anywhere) 
- **内置代码生成器**：采用代码或者 Maven 插件可快速生成 Mapper 、 Model 、 Service 、 Controller 层代码，支持模板引擎，更有超多自定义配置等您来使用
- **内置分页插件**：基于 MyBatis 物理分页，开发者无需关心具体操作，配置好插件之后，写分页等同于普通 List 查询
- **分页插件支持多种数据库**：支持 MySQL、MariaDB、Oracle、DB2、H2、HSQL、SQLite、Postgre、SQLServer 等多种数据库
- **内置性能分析插件**：可输出 Sql 语句以及其执行时间，建议开发测试时启用该功能，能快速揪出慢查询
- **内置全局拦截插件**：提供全表 delete 、 update 操作智能分析阻断，也可自定义拦截规则，预防误操作

****

**支持数据库**：

- mysql 、mariadb 、oracle 、db2 、h2 、hsql 、sqlite 、postgresql 、sqlserver 、presto 、Gauss 、Firebird
- Phoenix 、clickhouse 、Sybase ASE 、 OceanBase 、达梦数据库 、虚谷数据库 、人大金仓数据库 、南大通用数据库

****

**框架结构**：

![img](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202302261311313.jpeg)

扫描实体类，通过反射抽取实体类中的属性并分析其与表中字段之间的关系，最后调用MyBatis-Plus提供的一堆方法生成SQL语句注入到MyBatis的容器中，从而实现不同的增删改查功能