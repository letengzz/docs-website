# 项目结构与 POM 详解

`pom.xml`（Project Object Model，项目对象模型）是 Maven 项目的“身份证和说明书”：声明坐标、依赖、插件和构建行为。这一篇把标准目录和 POM 的每个核心元素讲清楚。

## 标准目录结构

Maven 约定目录（不用配置，直接生效）：

```text
my-app/
├─ pom.xml
└─ src/
   ├─ main/
   │  ├─ java/       # 主源码
   │  └─ resources/  # 主资源（配置文件等）
   └─ test/
      ├─ java/       # 测试源码
      └─ resources/  # 测试资源
```

构建产物默认输出到 `target/`，其中的 `classes/` 是编译后的 class，`*.jar` 是最终包。

| 目录 | 用途 | 说明 |
| --- | --- | --- |
| `src/main/java` | 主源码 | Java 包路径与目录一致 |
| `src/main/resources` | 主资源 | 会复制到 classpath |
| `src/test/java` | 单元测试源码 | 仅测试阶段使用 |
| `src/test/resources` | 测试资源 | 测试时覆盖同名的主资源 |
| `target/` | 构建输出 | 可随时删除，不提交 Git |

## 最小 POM

```xml [pom.xml]
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                             https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <groupId>com.example</groupId>
  <artifactId>my-app</artifactId>
  <version>1.0.0-SNAPSHOT</version>
  <packaging>jar</packaging>

  <properties>
    <maven.compiler.release>17</maven.compiler.release>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>
</project>
```

## 核心元素

| 元素 | 必填 | 说明 |
| --- | --- | --- |
| `modelVersion` | 是 | POM 模型版本，目前固定 `4.0.0` |
| `groupId` | 是 | 组织/公司标识，通常是反写域名，如 `com.example` |
| `artifactId` | 是 | 项目名，与目录名对应，如 `my-app` |
| `version` | 是 | 项目版本，如 `1.0.0-SNAPSHOT` |
| `packaging` | 否 | 打包方式，默认 `jar` |
| `properties` | 否 | 全局属性，供 POM 内 `${...}` 引用 |
| `dependencies` | 否 | 项目依赖列表 |
| `build` | 否 | 插件、输出名、资源目录等构建配置 |
| `parent` | 否 | 父 POM（继承） |
| `modules` | 否 | 聚合的子模块 |
| `dependencyManagement` | 否 | 统一管理依赖版本（不直接引入） |
| `pluginManagement` | 否 | 统一管理插件配置（不直接执行） |

## 坐标：groupId : artifactId : version

坐标（GAV）是依赖的唯一标识：

```text
com.example:my-app:1.0.0-SNAPSHOT
```

- `groupId`：公司/组织唯一性，一般反写域名，如 `org.springframework.boot`。
- `artifactId`：模块名，如 `spring-boot-starter-web`。
- `version`：版本号，`1.0.0` 为正式版，`1.0.0-SNAPSHOT` 为快照版。

::: tip 版本命名建议
遵循语义化版本 `主版本.次版本.修订号`：主版本破坏兼容、次版本新增功能、修订号修复缺陷。开发中用 `-SNAPSHOT`，发版时改为正式版本并打 Git tag。
:::

## packaging 类型

| packaging | 用途 |
| --- | --- |
| `jar` | 普通 Java 库（默认） |
| `war` | Web 应用（部署到 Tomcat 等） |
| `pom` | 父 POM / 聚合工程，只管理依赖和模块 |
| `maven-plugin` | Maven 插件 |
| `ear` | Java EE 企业应用归档 |

## properties 与占位符

```xml
<properties>
  <java.version>17</java.version>
  <junit.version>5.10.2</junit.version>
</properties>
```

引用方式：

```xml
<version>${junit.version}</version>
<release>${java.version}</release>
```

内置常用属性：

| 属性 | 含义 |
| --- | --- |
| `${project.groupId}` | 当前项目 groupId |
| `${project.artifactId}` | 当前项目 artifactId |
| `${project.version}` | 当前项目版本 |
| `${basedir}` | 项目根目录 |

## 查看 effective-pom

POM 存在继承和默认配置，实际生效的是“合并后的 POM”。查看方式：

```shell
mvn help:effective-pom
```

输出会展示默认继承的超级 POM（super POM）内容，例如默认编译插件版本、默认仓库地址。排查“为什么配置没生效”时优先看它。

## 依赖声明示例

```xml
<dependencies>
  <dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.10.2</version>
    <scope>test</scope>
  </dependency>
</dependencies>
```

依赖的完整配置在「依赖管理与仓库」篇展开。

## 易错点

::: danger 常见错误
1. `maven.compiler.source` / `target` 只写 8，但本机 JDK 是 17：编译仍按 8 的字节码版本，且容易触发交叉编译警告。推荐只用 `maven.compiler.release=17`，它同时约束 source 和 target。
2. `groupId` 使用大写或中文：发布到中央仓库/私服时可能被拒绝，规范做法是小写域名反写。
3. 把 `target/`、`*.iml`、`.idea/` 提交进 Git：构建产物和 IDE 文件不应入库，加入 `.gitignore`。
4. 版本号固定为 `1.0-SNAPSHOT` 长期不更新：多模块联调时容易用错旧快照，配合 `-U` 强制更新。
:::

## 验证方式

在项目根目录执行：

```shell
mvn validate
```

预期输出以 `BUILD SUCCESS` 结束，同时 `mvn help:effective-pom` 能看到最终生效的编译版本和仓库地址。再运行一次 `mvn compile`，确认 `target/classes/` 下生成 class 文件。

## 参考资料

- POM 参考文档：https://maven.apache.org/pom.html
- 标准目录布局：https://maven.apache.org/guides/introduction/introduction-to-the-standard-directory-layout.html
- Maven 坐标与命名：https://maven.apache.org/guides/mini/guide-naming-conventions.html
