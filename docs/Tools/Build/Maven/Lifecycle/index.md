# 构建生命周期与插件

生命周期（Lifecycle）是 Maven 构建的“时间轴”，插件是“在每个时间点干活的人”。理解两者关系后，`mvn` 的命令就不再是死记硬背。

## 三个内置生命周期

| 生命周期 | 用途 | 主要阶段 |
| --- | --- | --- |
| `default` | 项目构建主流程 | validate → compile → test → package → verify → install → deploy |
| `clean` | 清理构建产物 | clean |
| `site` | 生成站点文档 | site、site-deploy |

`mvn clean install` 同时触发 `clean` 生命周期和 `default` 生命周期。

## default 生命周期核心阶段

| 阶段 | 含义 | 典型产出 |
| --- | --- | --- |
| `validate` | 校验项目与配置正确 | 无 |
| `compile` | 编译主源码 | `target/classes/` |
| `test` | 运行单元测试 | `target/surefire-reports/` |
| `package` | 按 packaging 打包 | `target/*.jar` 或 `*.war` |
| `verify` | 运行集成测试、质量检查 | 校验结果 |
| `install` | 安装到本地仓库 | `~/.m2/repository/` 中的构件 |
| `deploy` | 发布到远程仓库/私服 | 私服上的构件 |

执行后面的阶段会**自动先执行前面所有阶段**，例如 `mvn package` 会先 validate、compile、test。

## 常用命令

```shell
mvn clean                     # 删除 target
mvn compile                   # 编译主代码
mvn test                      # 编译并运行单元测试
mvn package                   # 编译、测试并打包
mvn verify                    # 打包 + 集成测试/校验（推荐 CI 使用）
mvn install                   # 安装到本地仓库
mvn deploy                    # 发布到远程仓库
mvn clean install -DskipTests # 跳过测试并安装
```

## 插件与目标（Goal）

插件提供“目标”，生命周期阶段绑定默认目标。例如：

| 插件 | 目标 | 默认绑定阶段 |
| --- | --- | --- |
| maven-compiler-plugin | `compile`、`testCompile` | compile、test-compile |
| maven-surefire-plugin | `test` | test |
| maven-jar-plugin | `jar` | package |
| maven-install-plugin | `install` | install |
| maven-deploy-plugin | `deploy` | deploy |

执行阶段 = 依次执行绑定到各阶段的目标。

## 配置编译插件

```xml [pom.xml]
<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-compiler-plugin</artifactId>
      <version>3.13.0</version>
      <configuration>
        <release>17</release>
        <encoding>UTF-8</encoding>
      </configuration>
    </plugin>
  </plugins>
</build>
```

也可以只配置属性，让默认插件读取：

```xml
<properties>
  <maven.compiler.release>17</maven.compiler.release>
  <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
</properties>
```

## 自定义插件执行

在阶段中额外执行插件的目标：

```xml
<plugin>
  <groupId>org.codehaus.mojo</groupId>
  <artifactId>exec-maven-plugin</artifactId>
  <version>3.5.0</version>
  <executions>
    <execution>
      <phase>test</phase>
      <goals>
        <goal>java</goal>
      </goals>
      <configuration>
        <mainClass>com.example.App</mainClass>
      </configuration>
    </execution>
  </executions>
</plugin>
```

`executions` 中每个 `execution` 可以绑定任意阶段；不写 `phase` 时执行该目标的默认阶段。

## pluginManagement 与 plugins

- `pluginManagement`：只“统一配置”，不激活插件；子模块继承配置。
- `plugins`：真正激活并参与构建。

```xml
<build>
  <pluginManagement>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.13.0</version>
      </plugin>
    </plugins>
  </pluginManagement>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-compiler-plugin</artifactId>
    </plugin>
  </plugins>
</build>
```

这样版本只在 `pluginManagement` 中声明一次，多模块统一。

## 跳过测试的正确姿势

```shell
mvn package -DskipTests      # 编译测试代码，但不运行（推荐日常使用）
mvn package -Dmaven.test.skip=true  # 连测试代码都不编译
```

::: danger 常见错误
1. 用 `-DskipTests` 跳过测试后直接发版：跳过不等于没问题，发布前至少跑一次完整 `mvn verify`。
2. 多模块项目只用 `mvn package`：其他模块从本地仓库找不到新版本时要用 `mvn install`。
3. 改了 pom 后不重新构建，IDE 里还在用旧 class：先 `mvn clean` 再构建。
4. `mvn test` 报 `No tests were executed`：确认测试类名以 `Test` 结尾（Surefire 默认匹配 `*Test`、`Test*`、`*Tests`、`*TestCase`）。
:::

## 验证方式

准备一个带 JUnit 5 测试的最小项目，执行：

```shell
mvn clean verify
```

预期输出依次出现 `compiler:compile`、`surefire:test`、`jar:jar`，最终 `BUILD SUCCESS`；`target/` 下出现 jar 包，`target/surefire-reports/` 出现测试报告。

## 参考资料

- 生命周期介绍：https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html
- 插件列表：https://maven.apache.org/plugins/
- Surefire 官方文档：https://maven.apache.org/surefire/maven-surefire-plugin/
