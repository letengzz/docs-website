# 密钥与凭据治理

**凭据泄漏是数据泄露的头号成因之一**。密钥（Secret）、令牌（Token）、证书（Certificate）、密码都属于凭据（Credential）。它们的共同特点是：**一旦泄漏，攻击者就能以「合法身份」访问系统**，绕过多层防御。

密钥治理的核心原则只有一句：**不落库、不进 Git、最小可见、可轮换、可追溯、可吊销**。

## 一、密钥生命周期六阶段

![密钥与凭据治理：生命周期六阶段](../assets/security-secret-governance.svg)

| 阶段 | 目标 | 关键做法 |
| --- | --- | --- |
| **生成** | 高熵、不可预测 | 由 KMS/Vault 生成，禁止 `Math.random` 之类弱随机 |
| **存储** | 集中托管、静态加密 | 存 Vault / 云 Secrets Manager，不用明文文件 |
| **分发** | 运行时注入、短期有效 | 环境变量或挂载卷注入，优先用动态凭据 |
| **使用** | 不落盘、不打日志 | 内存读取，日志脱敏，禁止 `echo $SECRET` |
| **轮换** | 定期 + 事件驱动 | 自动滚动，缩短泄漏窗口 |
| **吊销** | 泄漏即失效 | 一键失效 + 审计追溯，确认无残留使用 |

## 二、常见的反模式

这些写法在真实项目里极其常见，每一项都是高危：

| 反模式 | 为什么危险 |
| --- | --- |
| 硬编码在源码 | 进入 Git 历史，永久留存，任何有仓库权限的人都能看到 |
| 提交 `.env` 且未 ignore | 同上，且常被 CI 缓存、被 Docker 打进镜像层 |
| CI 日志打印环境变量 | 日志常被上传到可搜索的存储，等于公开 |
| 全环境共用同一密钥 | 测试环境泄漏即生产失守，无法单独吊销 |
| 永不轮换 | 泄漏后无法判断影响范围，也无法止血 |
| 用 base64「加密」 | base64 是编码不是加密，等于明文 |

:::danger 注意
**Base64 / URL 编码 / 简单异或都不是加密。** 把密钥 base64 后放进配置，感觉上「看不出来」，实际上任何工具都能一眼解码。要么用真正的加密（KMS 信封加密），要么干脆不写进配置文件。
:::

## 三、集中托管：Vault 与云服务

### 3.1 HashiCorp Vault 的核心概念

| 概念 | 说明 |
| --- | --- |
| **Secret Engine** | 密钥后端，如 KV（键值）、Database（动态数据库凭据） |
| **Auth Method** | 认证方式，如 Token、AppRole、Kubernetes、OIDC |
| **Policy** | 授权策略，定义谁能读哪些路径 |
| **Lease / TTL** | 租约，密钥的有效期，到期自动失效 |

### 3.2 动态凭据：数据库密码不再是「长期密钥」

传统做法是「建一个数据库账号，密码写死」。Vault 的动态凭据引擎可以做到：**每次请求，生成一个临时账号，用完即销**。

```shell
# 启用数据库密钥引擎
vault secrets enable database

# 配置 PostgreSQL 连接（管理账号仅用于创建临时账号）
vault write database/config/mydb \
  plugin_name=postgresql-database-plugin \
  allowed_roles="app-role" \
  connection_url="postgresql://{{username}}:{{password}}@db:5432/mydb?sslmode=disable" \
  username="vault_admin" \
  password="admin-password"

# 定义角色：生成的账号有效期 1 小时
vault write database/roles/app-role \
  db_name=mydb \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
    GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"

# 应用请求凭据：返回一个 1 小时后自动失效的临时账号
vault read database/creds/app-role
```

:::tip 一句话理解
动态凭据把「长期密钥」变成「短期租约」。**即使租约被截获，攻击窗口也只有 1 小时**，且到期自动失效——这是比轮换更彻底的方案。
:::

### 3.3 Kubernetes 场景：External Secrets

在 K8s 中，推荐用 External Secrets Operator 把云/Vault 的密钥**同步为 K8s Secret**，而不是手工 `kubectl create secret`：

```yaml [external-secret.yaml]
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-db
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: ClusterSecretStore
  target:
    name: app-db-secret
  data:
    - secretKey: DB_PASSWORD
      remoteRef:
        key: secret/data/mydb
        property: password
```

这样密钥的**唯一真相源在 Vault**，K8s 里只是缓存；轮换后 1 小时内自动同步。

## 四、CI/CD 中的凭据

### 4.1 用 OIDC 换短期凭据，替代长期 Token

传统做法把云账号的长期 AccessKey 存进 CI Secret，一旦泄漏就是灾难。现代做法用 **OIDC 联合身份**：CI 用「我是哪个仓库、哪个分支」的身份，去云平台换取**几分钟有效的临时凭据**。

```yaml [.github/workflows/deploy.yaml]
permissions:
  id-token: write        # 关键：允许获取 OIDC token
  contents: read
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-deploy
          aws-region: ap-northeast-1
          # 无需存储任何长期 AccessKey
      - run: aws sts get-caller-identity
```

:::warning 说明
OIDC 的前提是云平台侧配置了**信任策略**（信任你 CI 的 OIDC 提供方，并按仓库/分支限制）。这个策略必须收紧：只允许特定仓库、特定分支（如 `main`）扮演角色，否则等于把门开着。
:::

### 4.2 CI 日志脱敏

即使配置正确，也可能因为打印调试信息而泄漏：

```shell
# 错误：直接把凭据打到日志
echo "Connecting with token=$API_TOKEN"

# 正确：只打印存在性
echo "token configured: $([ -n "$API_TOKEN" ] && echo yes || echo no)"

# 在脚本开头启用命令回显时屏蔽敏感变量
set +x
```

多数 CI 平台支持**掩码（masking）**已配置的 Secret，但它只对「完全匹配的字符串」生效，**经过拼接、编码、截断后就失效**。所以根本做法是不打印。

## 五、密钥泄漏检测

### 5.1 事前：提交前拦截

```shell
# gitleaks：扫描暂存区（pre-commit 钩子）
gitleaks protect --staged --verbose

# 扫描整个仓库历史
gitleaks detect --source . --report-format sarif --report-path gitleaks.sarif
```

### 5.2 事中：持续扫描

即便本地有钩子，也无法保证所有协作者都装了。应在 CI 中对**每次提交**与**仓库历史**都跑一遍扫描。

### 5.3 事后：泄漏响应流程

发现泄漏后，正确的响应顺序是**先止血、后清理**：

1. **立即轮换/吊销**该凭据（这一步最重要，且必须最先做）；
2. 排查该凭据被使用的所有位置（配置、代码、第三方系统）；
3. 检查审计日志，确认是否已被异常使用；
4. 清理仓库历史（`git filter-repo`），强推并通知所有协作者重新 clone；
5. 补上检测规则，防止同类泄漏再次发生。

:::danger 注意
最常见的错误顺序是「先删代码里的密钥，再去想轮换」。**代码删了但密钥没换，等于没做任何事**——Git 历史里还在，攻击者照样能用。永远**先轮换，再清理**。
:::

## 六、密钥轮换策略

| 密钥类型 | 推荐轮换周期 | 方式 |
| --- | --- | --- |
| 数据库密码 | 动态凭据（1 小时级） | Vault 自动生成 |
| API Token | 90 天 | 双密钥并行，灰度切换 |
| TLS 证书 | 90 天（Let's Encrypt）/ 1 年 | 自动化续签（cert-manager） |
| 加密主密钥（KEK） | 1 年 | KMS 密钥版本轮换，历史版本保留解密能力 |
| SSH 密钥 | 1 年 | 集中管理（如 JumpServer） |

:::tip 一句话理解
轮换的关键是**「双密钥并行期」**：新密钥先上线、旧密钥保留一小段时间，确保所有调用方都切过去后再吊销旧密钥。直接替换会导致正在使用旧密钥的服务立刻中断。
:::

## 七、验证方式

```shell
# 1. 确认本地钩子生效：造一个假密钥，提交应被拦下
echo 'AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE' > fake.txt
git add fake.txt && git commit -m "test"
# 预期：gitleaks 报错，commit 失败

# 2. 确认仓库历史里没有残留密钥
gitleaks detect --source . --no-banner; echo "exit=$? (0 表示无泄漏)"

# 3. Vault 动态凭据可用且会过期
vault read database/creds/app-role
# 预期：返回 username/password + lease_duration（如 1h）

# 4. K8s External Secret 能同步
kubectl get externalsecret app-db -o jsonpath='{.status.conditions[0].type}'
# 预期：Ready

# 5. 确认日志里没有明文密钥
grep -riE "(password|secret|token)\s*[:=]\s*\S{8,}" /var/log/app/ | head
# 预期：无输出，或仅脱敏占位符
```

## 八、参考资料

- HashiCorp Vault 文档：<https://developer.hashicorp.com/vault/docs>
- Vault 动态数据库凭据：<https://developer.hashicorp.com/vault/docs/secrets/databases>
- External Secrets Operator：<https://external-secrets.io/>
- gitleaks：<https://github.com/gitleaks/gitleaks>
- OWASP Secrets Management Cheat Sheet：<https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html>
- GitHub OIDC 硬编码凭据：<https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services>

## 相关专题

- [扫描工具链](../ScanningToolchain/index.md)（密钥扫描工具）
- [SBOM 与软件供应链](../SbomSupplyChain/index.md)
- [审计与检测](../AuditDetection/index.md)（凭据读取的审计）
- [Linux 安全加固](../../Linux/Advanced/SecurityHardening/index.md)
- [JumpServer](../../JumpServer/index.md)（特权访问管理）
