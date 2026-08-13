# 依赖管理与仓库

Maven 的依赖管理解决三件事：自动下载、传递依赖、版本冲突调解。仓库是 jar 的“货架”，理解本地仓库、中央仓库、私服的关系，才能快速定位下载失败和版本错乱。

## 依赖声明与作用域

```xml [pom.xml]
<dependencies>
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <version>3.3.5</version>
  </dependency>
  <dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <scope>provided</scope>
  </dependency>
  <dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <scope>test</scope>
  </dependency>
</dependencies>
```

### scope（依赖作用域）

| scope | 编译 | 测试 | 运行 | 是否传递 | 典型场景 |
| --- | --- | --- | --- | --- | --- |
| `compile`（默认） | 是 | 是 | 是 | 是 | 业务库 |
| `provided` | 是 | 是 | 否 | 否 | Servlet API、Lombok |
| `runtime` | 否 | 是 | 是 | 是 | JDBC 驱动 |
| `test` | 否 | 是 | 否 | 否 | JUnit、Mockito |
| `system` | 是 | 是 | 是 | 否 | 本机 jar（已不推荐） |
| `import` | - | - | - | - | 仅用于 `dependencyManagement` 导入 BOM |

## 传递依赖与冲突

A 依赖 B，B 依赖 C，则 A 自动获得 C（C 是 A 的传递依赖）。当多条路径引入不同版本的 C 时产生冲突，Maven 的默认策略是**最短路径优先**，路径相同时先声明者优先。

查看依赖树：

```shell
mvn dependency:tree
mvn dependency:tree -Dverbose   # 显示被省略的依赖与冲突原因
```

输出示例：

```text
com.example:my-app:jar:1.0.0-SNAPSHOT
+- org.springframework.boot:spring-boot-starter-web:jar:3.3.5:compile
|  \- com.fasterxml.jackson.core:jackson-databind:jar:2.17.2:compile
\- org.projectlombok:lombok:jar:1.18.34:provided
```

## 排除依赖

当传递依赖版本不想要时，用 `exclusions` 排除：

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-data-redis</artifactId>
  <exclusions>
    <exclusion>
      <groupId>io.lettuce</groupId>
      <artifactId>lettuce-core</artifactId>
    </exclusion>
  </exclusions>
</dependency>
```

排除后要自行声明替代依赖，否则运行期可能 `NoClassDefFoundError`。

## dependencyManagement：统一版本

`dependencyManagement` 只“定版本”，不“引入依赖”：

```xml
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
```

子模块声明依赖时可以省略版本号，统一由父 POM 管理。Spring Boot 项目使用 `spring-boot-dependencies` BOM 就是这个原理。

## 仓库体系

```text
本地仓库 ~/.m2/repository  ← 优先查找
        │ 未命中
        ▼
中央仓库 repo.maven.apache.org
        │ 可配置镜像
        ▼
镜像/私服（阿里云、Nexus、Artifactory）
```

| 仓库 | 位置 | 说明 |
| --- | --- | --- |
| 本地仓库 | `~/.m2/repository` | 本机缓存，优先查找 |
| 中央仓库 | `https://repo.maven.apache.org/maven2` | 官方公共仓库 |
| 私服 | Nexus / Artifactory | 公司内网统一管理构件 |

## settings.xml 关键配置

### 镜像

```xml [~/.m2/settings.xml]
<mirrors>
  <mirror>
    <id>aliyun</id>
    <mirrorOf>central</mirrorOf>
    <url>https://maven.aliyun.com/repository/public</url>
  </mirror>
</mirrors>
```

`mirrorOf` 常见取值：`central`（只镜像中央仓库）、`*`（所有仓库都走镜像，私服场景慎用）、`external:*`（除本机外全部镜像）。

### 私服认证

```xml
<servers>
  <server>
    <id>nexus-releases</id>
    <username>deploy-user</username>
    <password>加密后的密码</password>
  </server>
</servers>
```

密码建议用 `mvn -emp` 生成加密后的密文，不要把明文密码提交到 Git。

### 快照更新策略

```xml
<repositories>
  <repository>
    <id>nexus</id>
    <url>https://nexus.example.com/repository/maven-public/</url>
    <snapshots>
      <enabled>true</enabled>
      <updatePolicy>daily</updatePolicy>
    </snapshots>
  </repository>
</repositories>
```

`updatePolicy` 可选 `always`、`daily`、`never`；命令行 `mvn -U` 可强制检查快照更新。

## 发布到私服

```xml
<distributionManagement>
  <repository>
    <id>nexus-releases</id>
    <url>https://nexus.example.com/repository/maven-releases/</url>
  </repository>
  <snapshotRepository>
    <id>nexus-snapshots</id>
    <url>https://nexus.example.com/repository/maven-snapshots/</url>
  </snapshotRepository>
</distributionManagement>
```

执行 `mvn deploy` 时，正式版进 releases 仓库，`-SNAPSHOT` 版本进 snapshots 仓库。

## 常用诊断命令

```shell
mvn dependency:tree                          # 查看依赖树
mvn dependency:analyze                       # 分析未使用/未声明依赖
mvn dependency:get -Dartifact=...            # 单独拉取构件
mvn versions:display-dependency-updates      # 查看依赖新版本
mvn help:effective-settings                  # 查看生效的 settings
```

## 常见问题

::: danger 常见错误
1. 报 `Could not resolve dependencies`：先检查网络，再确认 GAV 是否存在（可在 mvnrepository.com 查询），最后确认私服地址是否可达。
2. 本地 jar 更新了但构建仍用旧版：快照依赖用 `mvn -U` 强制更新；正式版依赖需先由发布方 `mvn deploy` 或 `mvn install`。
3. 出现 `ClassNotFoundException` 但编译通过：依赖 scope 设置错误（如 `provided` 打成可运行 jar 后缺失），用 `dependency:tree` 检查。
4. 中央仓库下载慢：配置阿里云镜像，不要每次 `-U` 全量刷新。
5. 把 `~/.m2/settings.xml` 的私服密码提交到仓库：密码属于机密，用 Maven 密码加密或环境变量注入。
:::

## 验证方式

1. 在项目中添加 JUnit 5 依赖后执行 `mvn dependency:tree`，确认出现 `junit-jupiter`。
2. 执行 `mvn test` 跑通测试，验证依赖在 test 作用域可用。
3. 删除本地仓库中的某个 jar（`~/.m2/repository/...`），重新 `mvn compile`，确认自动重新下载。

## 参考资料

- 依赖机制介绍：https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html
- Settings 参考：https://maven.apache.org/settings.html
- 依赖插件：https://maven.apache.org/plugins/maven-dependency-plugin/
- 中央仓库检索：https://mvnrepository.com/
