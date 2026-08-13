# Maven 与 Gradle 对比

Maven 和 Gradle 都是 JVM 生态的主流构建工具，没有绝对的“谁更好”，只有“哪个更适合当前项目”。这一篇从模型、性能、配置、生态四个维度对比，并给出选型建议。

## 定位差异

| 维度 | Maven | Gradle |
| --- | --- | --- |
| 核心模型 | 生命周期阶段（Phase）+ 插件 | 任务图（Task DAG） |
| 配置文件 | `pom.xml`（XML） | `build.gradle.kts`（Kotlin DSL） |
| 学习曲线 | 低，约定固定 | 中，灵活但概念多 |
| 增量构建 | 较弱 | 原生强项 |
| 构建缓存 | 依赖插件支持 | 内置 |
| 守护进程 | 无（每次新 JVM） | 有（默认开启） |
| 多项目 | 聚合 + 继承 | 多项目 + 项目依赖 |
| 版本管理 | dependencyManagement | Version Catalog / Constraints |
| 典型场景 | 传统 Java 服务、存量系统 | 新 Java 项目、Android、Spring 官方示例 |

## 构建模型对比

```text
Maven：validate → compile → test → package → verify → install → deploy

Gradle：init → configuration → execution（Task DAG）
        compileJava → test → jar → assemble / check → build
```

Maven 通过“阶段 + 插件目标”组织构建，顺序固定、容易理解；Gradle 通过任务依赖组织，灵活但需要理解 DAG 和配置/执行阶段。

## 性能对比

| 机制 | Maven | Gradle |
| --- | --- | --- |
| 增量构建 | 无内置（插件可部分实现） | 内置，输入输出判断 |
| 并行构建 | `-T` 参数 | 默认支持 |
| 缓存 | 需额外插件 | 构建缓存 + 配置缓存 |
| 守护进程 | 无 | 默认开启 |
| 大型项目实测 | 基线 | 通常更快，冷启动除外 |

::: tip 性能结论
大型多模块项目 Gradle 优势明显；小型项目两者差距不大，不应只因为“快”而迁移。
:::

## 依赖管理对比

| 能力 | Maven | Gradle |
| --- | --- | --- |
| 作用域 | scope：compile/provided/runtime/test | Configuration：implementation/api/compileOnly/runtimeOnly 等 |
| 冲突策略 | 最短路径优先 | 最高版本优先 |
| 统一版本 | dependencyManagement | constraints + Version Catalog |
| 传递依赖排除 | `exclusions` | `exclude` |
| 严格版本 | 不原生支持 | `strictly` |
| 依赖锁定 | 插件支持 | 原生支持（dependency locking） |

## 插件与生态

- Maven 插件体系成熟：compiler、surefire、jar、spring-boot、maven-publish 等，几乎所有 Java 工具都有 Maven 插件。
- Gradle 生态同样完善：Java、Java Library、Spring Boot、Android Gradle Plugin（AGP）等，官方示例与新框架越来越倾向 Gradle。
- 二者都有 IDE 支持：IDEA 原生识别 Maven 和 Gradle 项目。

## 迁移成本

从 Maven 迁移 Gradle 的常见工作量：

1. `pom.xml` → `build.gradle.kts`：插件、依赖、构建配置重写。
2. 多模块 `modules` → `settings.gradle.kts` 的 `include`。
3. `dependencyManagement` → constraints / Version Catalog。
4. 自定义插件目标 → 自定义 Task。
5. CI 脚本中的 `mvn` 命令 → `./gradlew`。

建议先建一个独立分支做“影子构建”，对比两者的产物与测试结果，确认一致后再切换。

## 选型建议

| 场景 | 推荐 |
| --- | --- |
| 存量 Maven 项目、团队熟悉 XML | 继续 Maven，保持稳定 |
| 新 Java 服务、Spring Boot 新项目 | Gradle（Spring 官方生成器已默认可选 Gradle） |
| Android 项目 | Gradle（唯一选择） |
| 大型多模块、追求构建速度 | Gradle |
| 快速上手、约定化开发 | Maven |
| 内部工具/小型库 | 两者皆可，看团队 |

::: danger 常见错误
1. 因为“Gradle 更快”就盲目迁移：先量化构建时间与团队学习成本，再决定。
2. 迁移时直接用根项目的 `subprojects {}` 把所有子项目统一处理：容易把职责不同的模块配置成一样，建议逐步重构。
3. 认为两者命令完全一致：`mvn install` 与 Gradle 的 `publish` 语义不同，CI 脚本需要重写。
4. 忽略版本一致性：无论选哪个，都要用 Wrapper（`mvnw` / `gradlew`）锁定版本。
:::

## 验证方式

1. 用同一份源码分别建 Maven 与 Gradle 项目，执行 `clean build`，对比产物。
2. 在各自项目里跑 `mvn dependency:tree` 与 `./gradlew dependencies`，对比依赖树是否一致。
3. 记录两次全量构建与增量构建耗时，用数据决定选型。

## 参考资料

- Maven 官方文档：https://maven.apache.org/
- Gradle 官方文档：https://docs.gradle.org/
- Spring Initializr（对比脚手架）：https://start.spring.io/
