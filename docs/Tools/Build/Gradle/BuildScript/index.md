# 构建脚本与 Kotlin DSL

Gradle 构建脚本从 Maven 的 XML 换成了编程语言：Kotlin DSL（`.kts`）是目前官方推荐的主流写法。这一篇把 `settings.gradle.kts`、`build.gradle.kts`、`gradle.properties` 三个文件讲透。

## 三个核心文件

```text
my-project/
├─ settings.gradle.kts   # 项目名、模块列表、插件仓库
├─ build.gradle.kts      # 插件、依赖、任务、构建逻辑
├─ gradle.properties     # JVM 参数、项目属性
└─ gradlew / gradlew.bat # Wrapper 启动脚本
```

| 文件 | 职责 |
| --- | --- |
| `settings.gradle.kts` | 声明构建包含哪些项目，配置插件仓库 |
| `build.gradle.kts` | 声明插件、依赖、仓库、自定义任务 |
| `gradle.properties` | 键值对配置，如内存、编码、镜像 |

## settings.gradle.kts

单项目最小配置：

```kotlin [settings.gradle.kts]
rootProject.name = "my-app"
```

多项目时需要列出所有子项目（详见「多项目工程」篇）：

```kotlin
rootProject.name = "my-platform"
include("common", "service", "web")
```

插件仓库建议放在 `pluginManagement`：

```kotlin
pluginManagement {
    repositories {
        mavenCentral()
        gradlePluginPortal()
    }
}
```

## build.gradle.kts：Java 应用示例

```kotlin [build.gradle.kts]
plugins {
    java
    application
}

group = "com.example"
version = "1.0.0-SNAPSHOT"

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.apache.commons:commons-lang3:3.17.0")
    testImplementation(platform("org.junit:junit-bom:5.10.2"))
    testImplementation("org.junit.jupiter:junit-jupiter")
}

application {
    mainClass = "com.example.App"
}

tasks.test {
    useJUnitPlatform()
}
```

对照说明：

| 元素 | 作用 |
| --- | --- |
| `plugins { java }` | 引入 Java 插件，获得 `compileJava`、`test`、`jar` 等任务 |
| `application` | 让项目可执行，提供 `run` 任务 |
| `repositories` | 声明依赖仓库 |
| `dependencies` | 声明依赖（`implementation` 等配置） |
| `tasks.test` | 对 `test` 任务做配置 |

## 依赖配置与常用写法

```kotlin
dependencies {
    implementation("com.google.guava:guava:33.2.1-jre")
    compileOnly("org.projectlombok:lombok:1.18.34")
    annotationProcessor("org.projectlombok:lombok:1.18.34")
    runtimeOnly("com.mysql:mysql-connector-j:8.4.0")
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.2")
}
```

依赖坐标写法与 Maven 相同，仍是 `group:artifact:version`。

## gradle.properties

```properties [gradle.properties]
org.gradle.jvmargs=-Xmx2g -Dfile.encoding=UTF-8
org.gradle.daemon=true
org.gradle.parallel=true
org.gradle.caching=true
```

| 属性 | 作用 |
| --- | --- |
| `org.gradle.jvmargs` | Gradle 守护进程 JVM 参数 |
| `org.gradle.daemon` | 是否常驻守护进程 |
| `org.gradle.parallel` | 多项目并行配置 |
| `org.gradle.caching` | 启用构建缓存 |
| `org.gradle.configuration-cache` | 启用配置缓存（9.x 推荐） |

## 自定义任务

```kotlin
tasks.register("printInfo") {
    doLast {
        println("项目名: ${project.name}")
        println("版本: ${version}")
    }
}
```

执行：

```shell
./gradlew printInfo
```

用 `tasks.register` 延迟注册，避免配置阶段做多余工作。

## 生命周期钩子（简版）

```kotlin
plugins {
    java
}

tasks.named<Test>("test") {
    useJUnitPlatform()
    testLogging {
        events("passed", "failed", "skipped")
    }
}
```

`tasks.named<Test>("test")` 比直接改 `test {}` 更安全，不会在配置阶段强制创建任务。

## 易错点

::: danger 常见错误
1. Kotlin DSL 字符串漏了引号：`implementation("org.junit:junit:5")` 写成 `implementation("org.junit:junit:5)` 或 Groovy 式 `implementation '...'` 会直接编译失败。
2. 在 `doFirst` / `doLast` 外写业务逻辑：任务配置阶段就会执行，可能重复运行；把执行逻辑放进 `doLast {}`。
3. 使用 `tasks.test { }` 直接配置但项目还没引入 java 插件：任务不存在导致报错，先 `plugins { java }`。
4. 依赖写成 `compile '...'`：`compile` 配置在 Gradle 7+ 已移除，用 `implementation` 或 `api`。
5. 每台机器直接 `gradle build` 而不是 `./gradlew build`：版本不一致是团队项目最常见的坑。
:::

## 验证方式

创建示例项目后执行：

```shell
./gradlew clean build
```

预期输出包含 `compileJava`、`processResources`、`classes`、`test`、`jar` 等任务，最后 `BUILD SUCCESSFUL`；`build/libs/` 下生成 jar。再执行 `./gradlew printInfo` 验证自定义任务输出。

## 参考资料

- Kotlin DSL 文档：https://docs.gradle.org/current/userguide/kotlin_dsl.html
- Gradle 编写构建脚本：https://docs.gradle.org/current/userguide/writing_build_scripts.html
- Gradle 属性参考：https://docs.gradle.org/current/userguide/gradle_properties.html
