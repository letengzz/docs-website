# MyBatis介绍

MyBatis 是一个开源、轻量级的数据持久化框架。它支持定制化 SQL、存储过程以及高级映射。MyBatis 免除了几乎所有的 JDBC 代码以及设置参数和获取结果集的工作。MyBatis 可以通过简单的 XML 或注解来配置和映射原始类型、接口和 Java POJO(`Plain Old Java Objects`，普通老式 Java 对象)为数据库中的记录。MyBatis在实体类和 SQL 语句之间建立映射关系，是一种半自动化的 ORM 实现。其封装性低于 Hibernate，但性能优秀、小巧、简单易学、应用广泛。

- [数据持久化](../../../../Other/Concept/DataPersistence/README.md)
- [ORM对象关系映射](../../../../Other/Concept/ORM/README.md)

## MyBatis历史

MyBatis最初是Apache的一个开源项目`iBatis`, 2010年6月这个项目由Apache Software Foundation迁移到了Google Code。随着开发团队转投Google Code旗下， iBatis3.x正式更名为MyBatis。代码于2013年11月迁移到Github。

## MyBatis下载地址

https://github.com/mybatis/mybatis-3

![./images](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202303010949745.png)

![./images](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202303010949678.png)

## Mybatis特性

- **简单易学**：MyBatis 本身就很小且简单，没有任何第三方依赖，最简单安装只要两个 jar 文件 + 配置几个 sql 映射文件即可工作。易于学习和使用。
- **灵活**：MyBatis 不会对应用程序或者数据库的现有设计强加任何影响。SQL 写在 XML 里，便于统一管理和优化。通过 SQL 语句可以满足操作数据库的所有需求。
- **解除 SQL 与代码的耦合**：通过提供 DAO 层，将业务逻辑和数据访问逻辑分离，使系统的设计更清晰，更易维护，更易单元测试。SQL l和代码的分离，提高了可维护性。
- **可实现 ORM 映射**：MyBatis 是一个半自动的ORM(`Object Relation Mapping`)框架。提供了 ORM 映射的 XML 标签，支持对象与数据库的 ORM 字段关系映射。
- **支持对象关系映射**：MyBatis 提供了对象关系映射的 XML 标签，支持对象关系组建和维护。
- **支持动态SQL**：MyBatis 提供了支持编写动态 SQL 的 XML 标签，可以编写强大的动态 SQL。

## MyBatis优缺点

### 优点

- MyBatis 是免费且开源的。
- 与 JDBC 相比，减少了 50% 以上的代码量。
- MyBatis 是最简单的持久化框架，小巧并且简单易学。
- MyBatis 相当灵活，不会对应用程序或者数据库的现有设计强加任何影响，SQL 写在 XML 中，和程序逻辑代码分离，降低耦合度，便于同一管理和优化，提高了代码的可重用性。
- 提供 XML 标签，支持编写动态 SQL 语句。
- 提供映射标签，支持对象与数据库的 ORM 字段关系映射。
- 支持存储过程。MyBatis 以存储过程的形式封装 SQL，可以将业务逻辑保留在数据库之外，增强应用程序的可移植性、更易于部署和测试。

### 缺点

- 编写 SQL 语句工作量较大，对开发人员编写 SQL 语句的功底有一定要求。
- SQL 语句依赖于数据库，导致数据库移植性差，不能随意更换数据库。

## 和其它持久化层技术对比

- JDBC：
  - SQL 夹杂在Java代码中耦合度高，导致硬编码内伤
  - 维护不易且实际开发需求中 SQL 有变化，频繁修改的情况多见
  - 代码冗长，开发效率低
- Hibernate 和 JPA：
  - 操作简便，开发效率高
  - 程序中的长难复杂 SQL 需要绕过框架
  - 内部自动生成的 SQL，不容易做特殊优化
  - 基于全映射的全自动框架，大量字段的 POJO 进行部分映射时比较困难。
  - 反射操作太多，导致数据库性能下降
- MyBatis：
  - 轻量级，性能出色
  - SQL 和 Java 编码分开，功能边界清晰。Java代码专注业务、SQL语句专注数据
  - MyBatis 封装性低于 Hibernate。开发效率稍逊于 HIbernate，但是完全能够接收