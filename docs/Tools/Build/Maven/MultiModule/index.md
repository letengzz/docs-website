# 多模块工程

多模块（Multi-Module）工程把一个大型项目拆成多个可独立构建的模块，公共代码单独成模块，业务模块按依赖关系组装。这是中大型 Java 项目的标准组织方式。

## 为什么拆分

| 收益 | 说明 |
| --- | --- |
| 复用 | 公共代码（common）被多个模块依赖，只维护一份 |
| 边界 | 模块间通过 API 交互，强制依赖清晰 |
| 版本统一 | 父 POM 统一管理依赖与插件版本 |
| 构建提速 | 只改某个模块时用 `-pl` 只构建它 |
| 便于测试 | 模块级单元测试与集成测试分层 |

## 聚合（Aggregation）与继承（Inheritance）

- **聚合**：父 POM 用 `modules` 列出子模块，执行一次 `mvn install` 全部构建。
- **继承**：子模块用 `parent` 指向父 POM，继承依赖管理、插件配置、属性。

通常两者同时使用：父 POM 既聚合子模块，又作为公共配置的继承源。

## 目录结构

```text
my-platform/
├─ pom.xml                 # 父 POM（packaging = pom）
├─ common/                 # 公共模块（工具类、统一返回结构）
│  ├─ pom.xml
│  └─ src/main/java/...
├─ service/                # 业务服务模块
│  ├─ pom.xml
│  └─ src/main/java/...
└─ web/                    # Web 入口模块（打包成可运行 jar）
   ├─ pom.xml
   └─ src/main/java/...
```

## 父 POM

```xml [my-platform/pom.xml]
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                             https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <groupId>com.example</groupId>
  <artifactId>my-platform</artifactId>
  <version>1.0.0-SNAPSHOT</version>
  <packaging>pom</packaging>

  <modules>
    <module>common</module>
    <module>service</module>
    <module>web</module>
  </modules>

  <properties>
    <maven.compiler.release>17</maven.compiler.release>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>

  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>org.junit</groupId>
        <artifactId>junit-bom</artifactId>
        <version>5.10.2</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
    </dependencies>
  </dependencyManagement>
</project>
```

## 子模块 POM

```xml [my-platform/service/pom.xml]
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                             https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <parent>
    <groupId>com.example</groupId>
    <artifactId>my-platform</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <relativePath>../pom.xml</relativePath>
  </parent>

  <artifactId>service</artifactId>

  <dependencies>
    <dependency>
      <groupId>com.example</groupId>
      <artifactId>common</artifactId>
      <version>${project.version}</version>
    </dependency>
  </dependencies>
</project>
```

要点：

1. 子模块可省略 `groupId` 和 `version`，继承父 POM。
2. `relativePath` 指向父 POM 相对路径，默认是 `../pom.xml`，可省略。
3. 模块间依赖用 `${project.version}`，保证与父版本一致。

## Reactor 构建顺序

Maven 根据模块依赖关系自动排序（Reactor）：

```shell
mvn install   # 在父目录执行，按依赖顺序构建全部模块
```

输出会先构建 `common`，再 `service`，最后 `web`。只构建部分模块：

```shell
mvn -pl web -am install
```

- `-pl`（projects）：指定模块。
- `-am`（also make）：同时构建它依赖的上游模块。
- `-amd`（also make dependents）：同时构建依赖它的下游模块。

## 构建与发布规范

1. 本地开发：父目录 `mvn install` 把全部模块装进本地仓库。
2. CI 发布：`mvn clean deploy` 按 Reactor 顺序发布，快照版本进 snapshots 仓库。
3. 模块版本尽量跟随父版本，减少维护成本；确实需要独立版本时，在子模块中显式声明。

## 易错点

::: danger 常见错误
1. 父 POM 忘记写 `<packaging>pom</packaging>`：`modules` 不生效，子模块不会被聚合。
2. `relativePath` 写错：报 `Non-resolvable parent POM`，先检查父 POM 路径与版本是否一致。
3. 模块间循环依赖：service 依赖 common，common 又依赖 service，Maven 会直接报错；出现循环时重新划模块边界。
4. 子模块直接写死依赖版本（如 `common:1.0.0`）：发版时容易忘记同步，改用 `${project.version}` 或 dependencyManagement。
5. 只 `mvn package` 不 `mvn install`：下游模块从本地仓库拉不到刚改的 SNAPSHOT。
:::

## 验证方式

1. 在父目录执行 `mvn validate`，观察输出中按顺序列出三个模块。
2. 执行 `mvn install`，确认 `BUILD SUCCESS` 且 `~/.m2/repository/com/example/` 下出现三个模块。
3. 修改 `common` 后执行 `mvn -pl service -am install`，确认只构建 common 和 service，构建日志中没有 web。

## 参考资料

- 多模块构建指南：https://maven.apache.org/guides/mini/guide-multiple-modules.html
- Reactor 构建说明：https://maven.apache.org/guides/mini/guide-reactor.html
- 继承与聚合：https://maven.apache.org/pom.html#Aggregation
