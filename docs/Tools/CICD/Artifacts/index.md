# 制品管理

制品（Artifact）是流水线产出的**可部署交付物**：jar 包、前端 dist、Docker 镜像、Helm Chart 等。制品管理的核心是三条：**集中存储、不可变版本、可追溯**。本页覆盖构建产物规范、Nexus/Harbor 制品库、Docker 镜像管理与依赖安全。

## 为什么要单独管制品

| 问题 | 制品管理的解法 |
| --- | --- |
| 构建产物散落在 CI 机器上 | 统一制品库集中存储 |
| 同一个版本被覆盖 | 不可变 Tag，一个版本只对应一个制品 |
| 上线的是哪份代码说不清 | 制品元数据记录 commit、构建号、构建时间 |
| 制品无法找回 | 保留策略 + 备份 |
| 镜像/依赖带漏洞 | 入库前扫描 + 签名 |

## 制品分类与仓库

| 制品类型 | 仓库 | 说明 |
| --- | --- | --- |
| Java jar | Nexus / Artifactory | Maven 私服，代理中央仓库 |
| npm 包 | Verdaccio / npm registry | 私有 npm 源 |
| Python 包 | Nexus / PyPI 私有源 | pip 源 |
| Docker 镜像 | Harbor / Docker Registry | 镜像仓库 + 扫描 + 签名 |
| Helm Chart | Harbor / ChartMuseum | K8s 应用包 |
| 通用文件 | Nexus Raw / OSS | 安装包、配置文件 |

::: info 常见版本
Nexus Repository 当前主版本为 3.x；Harbor 当前主版本为 2.x（社区在推进 3.x 研发）。
:::

## 版本命名规范

推荐 [语义化版本](https://semver.org/) + 构建信息：

```text
主版本.次版本.补丁-构建号-commitSHA
示例：
order-service-1.2.0-45-a1b2c3d.jar
registry.example.com/shop/order-service:1.2.0-45-a1b2c3d
```

| 版本类型 | 命名 | 用途 |
| --- | --- | --- |
| 开发版 | `1.3.0-SNAPSHOT` | 开发联调，可覆盖 |
| 发布候选 | `1.3.0-RC1` | 预发布验证 |
| 正式版 | `1.3.0` | 生产部署，不可变 |

## Maven 私服（Nexus）

### 部署制品

```xml [pom.xml]
<distributionManagement>
    <repository>
        <id>releases</id>
        <url>https://nexus.example.com/repository/maven-releases/</url>
    </repository>
    <snapshotRepository>
        <id>snapshots</id>
        <url>https://nexus.example.com/repository/maven-snapshots/</url>
    </snapshotRepository>
</distributionManagement>
```

```shell
mvn deploy
```

### 代理中央仓库

在 Nexus 配置 `maven-central` 代理仓库，开发机与 CI 都从私服拉依赖：加速内网下载、统一管理、可审计。

```xml [settings.xml]
<mirrors>
    <mirror>
        <id>nexus</id>
        <mirrorOf>*</mirrorOf>
        <url>https://nexus.example.com/repository/maven-public/</url>
    </mirror>
</mirrors>
```

## Docker 镜像管理（Harbor）

### 推送到 Harbor

```shell
docker login harbor.example.com
docker tag shop/order-service:1.2.0-45-a1b2c3d \
  harbor.example.com/shop/order-service:1.2.0-45-a1b2c3d
docker push harbor.example.com/shop/order-service:1.2.0-45-a1b2c3d
```

### 项目与策略

| 策略 | 建议 |
| --- | --- |
| 项目隔离 | 每个团队/应用一个项目，访问权限分级 |
| 不可变 Tag | 开启 Immutable Tag，防止覆盖 |
| 漏洞扫描 | 推送即扫描，高危阻断 |
| 签名 | Cosign 签名，供应链可信 |
| 保留策略 | 保留最近 N 个版本，定期清理 |
| 复制 | 跨机房/容灾复制 |

### 流水线推送

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: docker/setup-buildx-action@v3
      - name: 登录 Harbor
        uses: docker/login-action@v3
        with:
          registry: harbor.example.com
          username: ${{ secrets.HARBOR_USER }}
          password: ${{ secrets.HARBOR_PASSWORD }}
      - name: 构建并推送
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            harbor.example.com/shop/order-service:1.2.0-45-a1b2c3d
```

## 前端构建产物

```yaml
jobs:
  build:
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v6
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v7
        with:
          name: web-dist
          path: dist/
```

部署时下载制品直接发到 CDN/服务器，保证上线即验证过的构建产物。

## 制品可追溯性

每个制品附带元数据：

```text
应用名、版本号、commit SHA、构建号、构建时间、构建人、触发分支、扫描结果
```

实现方式：

1. 镜像 Label 记录元数据（`org.label-schema.*`、`git.commit`）。
2. 制品库支持 SBOM（SPDX/CycloneDX）生成与查询。
3. 发布记录与制品绑定：Deployment 页面显示镜像 SHA 与 commit 链接。

## 易错点与最佳实践

::: danger 常见错误
1. **`latest` 满天飞**：`latest` 每次覆盖，无法回滚；生产部署必须用不可变 Tag。
2. **制品在 CI 机器上攒着不清理**：磁盘爆掉；统一入库并设保留策略。
3. **镜像明文密码登录**：在流水线里 `docker login -p 明文`；用 CI 密钥库。
4. **私服单点**：Nexus/Harbor 不备份，仓库挂了全公司构建停摆；备份 + 高可用。
5. **不扫描直接入库**：带漏洞镜像进生产；入库前 Trivy/Harbor 扫描。
6. **版本号手工维护**：忘记升级导致制品覆盖；用 CI 变量/自动生成版本。
:::

::: tip 最佳实践
1. 生产只用不可变 Tag，回滚 = 切回旧 Tag 的镜像。
2. 构建号用 GitHub 的 `run_number` 上下文（或 GitLab 的 `CI_PIPELINE_IID`）自动生成。
3. 私服做异地备份，Harbor 配置复制规则。
4. 制品与源代码同保留周期（至少与代码一样久）。
5. 镜像多阶段构建 + 精简基础镜像（alpine/distroless），减小体积与攻击面。
:::

## 验证方式

1. `mvn deploy` 后到 Nexus 仓库确认制品存在且版本正确。
2. 构建并推送镜像，用 `docker pull` 验证可拉取，检查 Harbor 扫描结果。
3. 用旧版本 Tag 重新部署，确认回滚可用（旧镜像仍存在）。
4. 检查镜像 Label/SBOM，确认 commit 元数据完整。

## 参考资料

- 语义化版本规范：https://semver.org/lang/zh-CN/
- Nexus Repository 文档：https://help.sonatype.com/en/sonatype-nexus-repository.html
- Harbor 文档：https://goharbor.io/docs/
- Open Container Initiative（OCI）：https://opencontainers.org/
- SBOM 与供应链安全（SPDX）：https://spdx.dev/
