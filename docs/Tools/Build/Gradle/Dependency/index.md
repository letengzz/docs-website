# 依赖管理与版本目录

Gradle 的依赖管理比 Maven 更精细：多种 Configuration 控制作用域，依赖约束（Constraints）统一版本，Version Catalog（版本目录）集中管理坐标。这一篇讲清楚“怎么声明、怎么统一、怎么查”。

## 依赖 Configuration

`dependencies {}` 中的每一行都挂在某个 Configuration 上：

```kotlin
dependencies {
    implementation("org.apache.commons:commons-lang3:3.17.0")
    api("com.example:common:1.0.0")
    compileOnly("org.projectlombok:lombok:1.18.34")
    runtimeOnly("com.mysql:mysql-connector-j:8.4.0")
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.2")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
    annotationProcessor("org.projectlombok:lombok:1.18.34")
}
```

| Configuration | 编译 | 测试 | 运行 | 对外传递 | 典型场景 |
| --- | --- | --- | --- | --- | --- |
| `implementation` | 是 | 是 | 是 | 否 | 内部实现依赖 |
| `api` | 是 | 是 | 是 | 是 | 对外暴露的类型依赖（需 `java-library` 插件） |
| `compileOnly` | 是 | 是 | 否 | 否 | Lombok、Servlet API |
| `runtimeOnly` | 否 | 是 | 是 | 否 | JDBC 驱动 |
| `testImplementation` | 否 | 是 | 否 | 否 | JUnit、Mockito |
| `testRuntimeOnly` | 否 | 是 | 否 | 否 | 测试运行器 |
| `annotationProcessor` | - | - | - | 否 | 注解处理器 |

::: tip implementation 与 api
默认只依赖内部使用时用 `implementation`，避免把传递依赖暴露给使用者；只有依赖类型出现在对外 API 签名中时才用 `api`（引入 `java-library` 插件后可用）。
:::

## 仓库声明

```kotlin
repositories {
    mavenCentral()
    mavenLocal()
    maven {
        url = uri("https://maven.aliyun.com/repository/public")
    }
    maven {
        url = uri("https://nexus.example.com/repository/maven-public/")
        credentials {
            username = "dev"
            password = "******"
        }
    }
}
```

凭据建议通过环境变量或 `gradle.properties` 注入，不要硬编码提交。

## 依赖冲突：谁胜出

默认策略是**取最高版本**（与 Maven 的“最短路径优先”不同），并输出冲突报告：

```shell
./gradlew dependencies
./gradlew :web:dependencies --configuration runtimeClasspath
```

强制某个版本：

```kotlin
dependencies {
    implementation("com.fasterxml.jackson.core:jackson-databind:2.17.2")
    implementation("com.fasterxml.jackson.core:jackson-databind") {
        version { strictly("2.17.2") }
    }
}
```

用 `strictly` 时所有路径都会被强制到该版本，需谨慎使用。

## 依赖约束（Constraints）

不直接引入依赖，只约束版本：

```kotlin
dependencies {
    constraints {
        implementation("org.apache.commons:commons-lang3:3.17.0")
        implementation("com.google.guava:guava:33.2.1-jre")
    }
}
```

子项目只要引入同名依赖，就会自动使用约束版本。这是多项目统一版本的推荐方式。

## 版本目录（Version Catalog）

在 `gradle/` 目录创建 `libs.versions.toml`：

```toml [gradle/libs.versions.toml]
[versions]
junit = "5.10.2"
guava = "33.2.1-jre"

[libraries]
junit-jupiter = { module = "org.junit.jupiter:junit-jupiter", version.ref = "junit" }
guava = { module = "com.google.guava:guava", version.ref = "guava" }

[plugins]
spring-boot = { id = "org.springframework.boot", version = "3.3.5" }
```

构建脚本引用：

```kotlin
plugins {
    alias(libs.plugins.spring.boot)
}

dependencies {
    implementation(libs.guava)
    testImplementation(libs.junit.jupiter)
}
```

优点：版本集中管理、IDE 自动补全、多模块共享同一份目录。

## 常用命令

```shell
./gradlew dependencies                        # 查看项目依赖
./gradlew dependencyInsight --dependency guava # 分析某个依赖来源
./gradlew :web:dependencies --configuration runtimeClasspath
./gradlew build --refresh-dependencies          # 强制刷新依赖
```

## 常见问题

::: danger 常见错误
1. 使用已移除的 `compile`、`runtime` 配置：Gradle 7+ 必须改用 `implementation` / `runtimeOnly`。
2. 依赖版本不统一：多项目里各写各的版本，建议用 Version Catalog 或 constraints 统一。
3. `api` 与 `implementation` 混用混乱：默认全部用 `implementation`，只有对外 API 需要暴露时用 `api`。
4. 版本冲突时依赖“碰运气”：先 `./gradlew dependencyInsight` 定位，再决定排除还是严格版本，不要盲目升到最高版本。
5. 快照依赖缓存不更新：执行 `./gradlew build --refresh-dependencies`。
6. 私服凭据入库：凭据从环境变量读取，例如 `username = System.getenv("NEXUS_USER")`。
:::

## 验证方式

1. 执行 `./gradlew dependencies --configuration runtimeClasspath`，确认依赖树符合预期。
2. 用 `./gradlew dependencyInsight --dependency junit` 查看 junit 的来源与版本。
3. 删除 `~/.gradle/caches` 中对应缓存后重新构建，确认能自动重新下载（缓存目录可安全重建）。

## 参考资料

- 依赖管理基础：https://docs.gradle.org/current/userguide/dependency_management.html
- 版本目录：https://docs.gradle.org/current/userguide/version_catalogs.html
- 依赖约束：https://docs.gradle.org/current/userguide/dependency_constraints.html
