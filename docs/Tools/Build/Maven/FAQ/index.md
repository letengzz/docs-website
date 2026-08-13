# Maven 常见问题与最佳实践

这一篇汇总 Maven 使用中最常遇到的 10 个问题和一套可以直接落地的工程实践。

## 常见问题

### 1. 依赖下载慢或失败

原因：访问中央仓库超时或网络受限。

解决：配置阿里云镜像，必要时用 `-U` 强制刷新：

```shell
mvn clean install -U
```

仍然失败时检查 DNS、代理，以及私服地址是否可达。

### 2. 依赖冲突导致运行期报错

用 `dependency:tree` 找到冲突路径，再决定排除或提升版本：

```shell
mvn dependency:tree -Dverbose | findstr jackson
```

### 3. 编译报错：`invalid target release: 17`

说明 JDK 版本低于 17 或 `release` 配置与 JDK 不匹配。确认 `java -version` 与 `mvn -v` 使用的是同一 JDK，并把 `maven.compiler.release` 改为本机支持的版本。

### 4. 中文乱码

在 POM 中显式声明编码：

```xml
<properties>
  <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
</properties>
```

同时保证源码文件本身是 UTF-8 保存。

### 5. 打出的 jar 无法运行

普通 jar 不会自动带主类清单，用 `mvn package` 后 `java -jar` 报 `no main manifest attribute`。解决：

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-jar-plugin</artifactId>
  <configuration>
    <archive>
      <manifest>
        <mainClass>com.example.App</mainClass>
      </manifest>
    </archive>
  </configuration>
</plugin>
```

Spring Boot 项目则使用 `spring-boot-maven-plugin` 的 `repackage` 目标生成可执行 fat jar。

### 6. `package` 和 `install` 有什么区别

- `package`：只生成 `target/` 下的包。
- `install`：生成包并安装到本地仓库，供本机其他模块/项目引用。

多模块联调时使用 `install`，CI 发布使用 `deploy`。

### 7. 测试全部被跳过

检查命令中是否误带了 `-DskipTests` 或 `-Dmaven.test.skip=true`；再检查测试类命名是否满足 Surefire 默认规则（以 `Test` 结尾等）。

### 8. 子模块报 `Non-resolvable parent POM`

检查父 POM 的 `groupId`、`artifactId`、`version` 与子模块 `parent` 是否一致，`relativePath` 是否正确，并先在父目录执行一次 `mvn install`。

### 9. IDEA 中依赖不生效

在 IDEA 右侧 Maven 面板点击刷新（Reload All Maven Projects）；若本地仓库损坏，删除 `~/.m2/repository` 中对应目录后重新构建（该目录可安全重建）。

### 10. 修改了 pom.xml 但构建没变化

先 `mvn clean` 再构建；涉及快照依赖时加 `-U`；插件版本变化用 `mvn help:effective-pom` 确认。

## 工程最佳实践

::: tip 可直接落地的清单
1. 使用 Maven Wrapper（`mvn wrapper:wrapper`），让团队用同一版本构建。
2. 所有模块用父 POM 的 `dependencyManagement` 管版本，模块内不写死版本。
3. CI 中执行 `mvn clean verify`，发布执行 `mvn clean deploy`，不要跳过测试。
4. 版本号遵循语义化版本，发版打 Git tag，并同步更新 `README`。
5. 敏感信息（私服账号、密码）只放 `settings.xml`，并加密或环境变量注入，绝不入库。
6. `target/` 和 IDE 文件加入 `.gitignore`。
7. 依赖升级前用 `mvn versions:display-dependency-updates` 查看，升级后跑完整测试。
8. 每周检查一次 `mvn dependency:analyze` 的告警，清理未使用依赖。
:::

## 验证方式

对一个已有项目执行：

```shell
mvn clean verify -DskipTests=false
```

确认 `BUILD SUCCESS`、测试报告生成、目标 jar 可运行；再执行 `git status`，确认 `target/` 没有被提交。

## 参考资料

- Maven 官方指南：https://maven.apache.org/guides/
- Maven 常见问题：https://maven.apache.org/general.html
- Maven Wrapper：https://maven.apache.org/wrapper/
