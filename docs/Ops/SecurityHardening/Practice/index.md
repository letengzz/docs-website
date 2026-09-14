# 实战：一条端到端安全流水线

前面的篇章分别讲了基线、扫描、漏洞、SBOM、密钥、审计。本篇把它们**串成一条能在本地跑通的完整流水线**，覆盖「提交 → 构建 → 部署 → 运行」四个阶段。

目标不是科普，而是给你一份「照着做就能复现」的落地脚本：任何阶段发现问题，都能**阻断或告警**。

## 一、场景与目标

假设有一个 Node.js 应用部署到 Kubernetes，我们要做到：

| 阶段 | 要保证的事 | 失败时的动作 |
| --- | --- | --- |
| 提交 | 没有硬编码密钥、没有明显代码缺陷 | 拒绝提交 |
| 构建 | 依赖无高危漏洞、产出 SBOM、镜像已签名 | 构建失败 |
| 部署 | 配置合规、镜像签名有效 | 准入拒绝 |
| 运行 | 异常行为被检测并告警 | 告警 / 隔离 |

![实战：一条端到端的安全流水线](../assets/security-practice.svg)

## 二、环境准备

```shell [环境要求]
# 本地需具备：Docker、kubectl、Git
docker --version        # >= 24
kubectl version --client
git --version

# 安装核心工具（以 Linux/macOS 为例）
# Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
trivy --version         # 预期 >= 0.74.0

# Syft + Grype
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin

# gitleaks 与 cosign
brew install gitleaks cosign   # 或从对应 Release 下载
```

:::info 当前使用的版本
本实战基于 Trivy 0.74.0、Grype 0.118.0、Falco 0.44.1、Kyverno 1.19.0、cosign（keyless 模式），核对时间 2026-09。若你的版本不同，请以官方文档为准。
:::

准备一个最小应用：

```text [app.js]
const http = require('http');
const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ status: 'ok' }));
});
server.listen(3000, () => console.log('listening on :3000'));
```

```dockerfile [Dockerfile]
# 多阶段构建 + 非 root + 固定 digest
FROM node:22.22.2-alpine3.21 AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev

FROM node:22.22.2-alpine3.21
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY app.js ./
USER node
EXPOSE 3000
CMD ["node", "app.js"]
```

## 三、阶段一：提交前拦截

### 3.1 pre-commit 钩子

```yaml [.pre-commit-config.yaml]
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.28.0
    hooks:
      - id: gitleaks
  - repo: https://github.com/semgrep/semgrep
    rev: v1.95.0
    hooks:
      - id: semgrep
        args: ["--config=auto", "--error", "--severity=ERROR"]
```

```shell
# 安装并启用钩子
pip install pre-commit
pre-commit install

# 手动跑一遍全部检查
pre-commit run --all-files
```

### 3.2 验证拦截生效

```shell
# 故意制造一个泄漏，提交应被拦下
echo 'const API_KEY = "AKIAIOSFODNN7EXAMPLE";' >> app.js
git add app.js && git commit -m "test leak"
# 预期：gitleaks 报错，提交失败

# 复原
git checkout app.js
```

## 四、阶段二：构建与签名

### 4.1 生成 SBOM 并扫描依赖

```shell
# 生成 SBOM（Source 侧）
syft dir:. -o cyclonedx-json=build/sbom-src.cdx.json

# 基于 SBOM 扫描依赖漏洞
grype sbom:build/sbom-src.cdx.json --fail-on high
# 预期：无高危则退出码 0；有则非 0
```

### 4.2 构建镜像并扫描

```shell
docker build -t registry.example.com/demo:v1 .

# 扫描镜像（只报有修复版本的漏洞）
trivy image --ignore-unfixed --severity HIGH,CRITICAL \
  --exit-code 1 registry.example.com/demo:v1

# 生成镜像的 SBOM
syft registry.example.com/demo:v1 -o cyclonedx-json=build/sbom-image.cdx.json
```

### 4.3 签名镜像

```shell
# 推送到仓库
docker push registry.example.com/demo:v1

# 用 cosign 签名（keyless 模式需 OIDC，CI 里自动可用）
cosign sign --yes registry.example.com/demo:v1

# 立即验签，确认签名有效
cosign verify \
  --certificate-identity-regexp=".*" \
  --certificate-oidc-issuer-regexp=".*" \
  registry.example.com/demo:v1
```

:::danger 注意
第 4.2 步的 `--exit-code 1` 是**构建门禁**：一旦有高危漏洞，构建直接失败，防止不安全的镜像进入仓库。很多人只做扫描不做阻断，结果不合格镜像照样上线，扫描形同虚设。
:::

### 4.4 把 SBOM 附加到镜像

```shell
cosign attest --yes --predicate build/sbom-image.cdx.json \
  --type cyclonedx registry.example.com/demo:v1
```

## 五、阶段三：部署准入

### 5.1 配置扫描

```shell
# 扫描 K8s 清单
trivy config --severity HIGH,CRITICAL --exit-code 1 ./deploy
```

### 5.2 准入策略：强制验签 + 禁止特权

```yaml [deploy/policies.yaml]
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: supply-chain-guard
spec:
  validationFailureAction: Enforce
  rules:
    - name: verify-signature
      match:
        any:
          - resources: { kinds: [Pod] }
      verifyImages:
        - imageReferences: ["registry.example.com/*"]
          attestors:
            - entries:
                - keyless:
                    subject: "https://github.com/your-org/*"
                    issuer: "https://token.actions.githubusercontent.com"
    - name: disallow-privileged
      match:
        any:
          - resources: { kinds: [Pod] }
      validate:
        message: "禁止使用特权容器"
        pattern:
          spec:
            containers:
              - securityContext:
                  privileged: "false"
```

```shell
kubectl apply -f deploy/policies.yaml

# 验证：未签名的镜像应被拒绝
kubectl run bad --image=nginx:latest
# 预期：admission webhook 拒绝（image not signed / policy violation）

# 验证：合规镜像可正常部署
kubectl run good --image=registry.example.com/demo:v1
```

## 六、阶段四：运行时检测

### 6.1 部署 Falco

```shell
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update
helm install falco falcosecurity/falco \
  -n falco --create-namespace \
  --set driver.kind=modern_ebpf
```

### 6.2 验证检测能力

```shell
# 场景一：容器内启动 shell（常见横向移动前兆）
kubectl exec -it good -- sh -c "whoami"
# 预期：Falco 告警 "Terminal shell in container"

# 场景二：读取敏感文件
kubectl exec -it good -- cat /etc/shadow 2>/dev/null
# 预期：Falco 告警 "Read sensitive file untrusted"

# 查看告警
kubectl logs -n falco -l app.kubernetes.io/name=falco --tail=30 | grep -i warning
```

### 6.3 审计日志落地

```shell
# 确认 K8s 审计日志（托管集群从云控制台开启）
# 确认主机 auditd 规则已加载（见 AuditDetection 篇）
sudo auditctl -l | grep -c priv_esc

# 确认日志已转发到远端集中存储
# 验证方法：本地清空后，远端仍能查到历史
```

## 七、端到端一键验证

把以上步骤固化为一个可重复执行的脚本：

```bash [scripts/security-gate.sh]
#!/usr/bin/env bash
# 端到端安全门禁：任一环节失败即退出
set -euo pipefail

IMAGE="registry.example.com/demo:${1:-v1}"

echo "==> [1/5] pre-commit 检查（密钥 + SAST）"
pre-commit run --all-files

echo "==> [2/5] 生成 SBOM 并扫描依赖"
mkdir -p build
syft dir:. -o cyclonedx-json=build/sbom-src.cdx.json
grype sbom:build/sbom-src.cdx.json --fail-on high

echo "==> [3/5] 构建镜像并扫描高危漏洞"
docker build -t "$IMAGE" .
trivy image --ignore-unfixed --severity HIGH,CRITICAL --exit-code 1 "$IMAGE"

echo "==> [4/5] 生成镜像 SBOM 并签名"
syft "$IMAGE" -o cyclonedx-json=build/sbom-image.cdx.json
docker push "$IMAGE"
cosign sign --yes "$IMAGE"

echo "==> [5/5] 配置扫描与验签"
trivy config --severity HIGH,CRITICAL --exit-code 1 ./deploy
cosign verify --certificate-identity-regexp=".*" \
  --certificate-oidc-issuer-regexp=".*" "$IMAGE"

echo "✅ 所有安全门禁通过：$IMAGE"
```

```shell
chmod +x scripts/security-gate.sh
./scripts/security-gate.sh v1
```

### 7.1 预期结果

| 步骤 | 通过条件 | 失败表现 |
| --- | --- | --- |
| [1/5] | 无密钥泄漏、无 ERROR 级 SAST | gitleaks / semgrep 非零退出 |
| [2/5] | 依赖无高危 | grype 报 `--fail-on` 命中 |
| [3/5] | 镜像无有修复版本的高危 | trivy 退出码 1 |
| [4/5] | 签名成功、验签通过 | cosign 报错 |
| [5/5] | 配置合规、签名有效 | trivy/kyverno 拒绝 |

## 八、验证清单

跑完上一步后，逐项确认：

```shell
# ✅ 1. 流水线本身可重复执行
./scripts/security-gate.sh v1 && echo "首次通过"
./scripts/security-gate.sh v1 && echo "重复执行仍通过（幂等）"

# ✅ 2. 有人为引入问题时能阻断（关键！）
echo "const K='AKIAIOSFODNN7EXAMPLE'" >> app.js
./scripts/security-gate.sh v1 || echo "成功阻断不合规提交"
git checkout app.js

# ✅ 3. 未签名镜像无法部署
kubectl run unsigned --image=nginx:latest 2>&1 | grep -i "denied\|violat"

# ✅ 4. 运行时异常能触发告警
kubectl exec -it good -- cat /etc/shadow 2>/dev/null
kubectl logs -n falco -l app.kubernetes.io/name=falco --tail=10 | grep -i sensitive

# ✅ 5. SBOM 已归档，可追溯
ls -l build/sbom-*.cdx.json
python -c "import json;d=json.load(open('build/sbom-image.cdx.json'));print('组件数:',len(d['components']))"
```

:::tip 验收标准
**「能跑通」不算成功，「能拦住」才算成功。** 必须验证第 2 步（人为破坏能阻断）与第 3 步（未签名不能部署），这才是安全流水线的真正价值。
:::

## 九、落地路线图

从零开始，建议按这个顺序推进（避免一次性铺太大）：

1. **第 1 周**：接 gitleaks + Trivy fs 到 pre-commit / CI（成本最低、收益最高）；
2. **第 2 周**：镜像扫描 + SBOM 生成，接通构建门禁；
3. **第 3 周**：cosign 签名 + K8s 准入验签；
4. **第 4 周**：Falco 运行时检测 + 审计日志集中，补齐「检测」能力。

## 十、参考资料

- Trivy：<https://trivy.dev/>
- Syft / Grype：<https://github.com/anchore>
- Sigstore cosign：<https://docs.sigstore.dev/>
- Kyverno 验签：<https://kyverno.io/docs/writing-policies/verify-images/>
- Falco：<https://falco.org/docs/>
- SLSA：<https://slsa.dev/>

## 相关专题

- [安全加固方法论](../Overview/index.md)
- [基线合规与自动化](../BaselineCompliance/index.md)
- [扫描工具链](../ScanningToolchain/index.md)
- [漏洞管理生命周期](../VulnerabilityManagement/index.md)
- [SBOM 与软件供应链](../SbomSupplyChain/index.md)
- [密钥与凭据治理](../SecretGovernance/index.md)
- [审计与检测](../AuditDetection/index.md)
- [工具：CI/CD](../../../Tools/CICD/index.md)
- [容器与集群安全加固](../../ContainerOrchestration/Security/index.md)
