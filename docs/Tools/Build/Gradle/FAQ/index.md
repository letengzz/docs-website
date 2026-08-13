# Gradle 常见问题与最佳实践

这一篇汇总 Gradle 高频问题与团队工程实践，覆盖从“构建慢”到“依赖冲突”的日常场景。

## 常见问题

### 1. 第一次构建下载很慢

Gradle 发行版和依赖都要走网络。解决：

1. 统一用 Wrapper，版本由 `distributionUrl` 决定。
2. 配置国内镜像仓库：

```kotlin
repositories {
    maven { url = uri("https://maven.aliyun.com/repository/public") }
    mavenCentral()
}
```

3. 不要频繁 `--refresh-dependencies`，信任缓存。

### 2. 构建报 `Unsupported class file major version`

Gradle 9.x 需要 JVM 17+。检查：

```shell
java -version
./gradlew --version
```

确认两个命令使用同一个 JDK（可在 `gradle.properties` 中指定 `org.gradle.java.home`，或配置 Java Toolchain）。

### 3. 任务一直执行但没输出

把打印逻辑放在 `doFirst {}` / `doLast {}`：

```kotlin
tasks.register("hello") {
    doLast {
        println("hello")
    }
}
```

### 4. 依赖冲突怎么办

Gradle 默认取最高版本。先用命令定位：

```shell
./gradlew dependencyInsight --dependency jackson-databind
```

再选择：升级项目里依赖的版本、用 `strictly` 强制版本、或排除传递依赖。

### 5. `compile` 配置不存在

Gradle 7+ 移除了 `compile` / `runtime`，改用：

| 旧配置 | 新配置 |
| --- | --- |
| `compile` | `implementation` 或 `api` |
| `runtime` | `runtimeOnly` |
| `testCompile` | `testImplementation` |
| `testRuntime` | `testRuntimeOnly` |

### 6. 守护进程内存不足

在 `gradle.properties` 调整：

```properties
org.gradle.jvmargs=-Xmx2g -XX:MaxMetaspaceSize=512m
```

必要时停止旧守护进程：

```shell
./gradlew --stop
```

### 7. Kotlin DSL 报类型错误

先确认 `.kts` 扩展名、依赖字符串带引号；再在 IDEA/Android Studio 中刷新 Gradle，查看错误行号。常见问题是 `tasks.test { }` 与 `tasks.named<Test>("test") { }` 混用。

### 8. 配置缓存报不兼容

Gradle 9 默认推荐配置缓存，个别插件不兼容时会告警。临时关闭：

```properties
org.gradle.configuration-cache=false
```

排查插件版本，升级到兼容版本后再开启。

### 9. 多项目之间找不到模块

确认 `settings.gradle.kts` 中 `include` 了所有子项目，且依赖写成 `implementation(project(":common"))`。子项目名与目录名不一致时检查 `projectDir` 配置。

### 10. 构建产物不一致

固定 Gradle 版本（Wrapper）、JDK（Toolchain 或 CI 镜像）和依赖版本（Version Catalog + 依赖锁定），并在 CI 中执行 `clean build` 验证可复现。

## 工程最佳实践

::: tip 可直接落地的清单
1. 所有项目提交 Wrapper（`gradlew`、`gradlew.bat`、`gradle/wrapper/`），统一版本。
2. 使用 Kotlin DSL，新项目不再创建 Groovy 脚本。
3. 用 Version Catalog（`gradle/libs.versions.toml`）管理所有依赖与插件版本。
4. `implementation` 优先，`api` 只在对外暴露类型时使用。
5. 开启构建缓存和并行构建，CI 与本地共享缓存。
6. 敏感凭据走环境变量，`gradle.properties` 中不要写密码。
7. 定期升级 Gradle 小版本，升级前跑完整 `clean build`。
8. 使用 Java Toolchain 统一编译版本，避免“本地能过、CI 报错”。
:::

## 验证方式

对示例项目执行：

```shell
./gradlew clean build --warning-mode all
```

确认无弃用告警、`BUILD SUCCESSFUL`、`build/libs/` 下产物存在。再连续构建两次，确认增量构建与缓存生效（第二次大量任务 `UP-TO-DATE`）。

## 参考资料

- Gradle 官方文档：https://docs.gradle.org/
- 升级指南：https://docs.gradle.org/current/userguide/upgrading_version_8.html
- Gradle 论坛：https://discuss.gradle.org/
