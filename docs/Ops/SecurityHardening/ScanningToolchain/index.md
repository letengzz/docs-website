# 扫描工具链

安全扫描工具非常多，但**工具不是越多越好**。一个可维护的工具链应当做到：每个阶段只选 1~2 个主力工具、统一输出格式（SARIF / CycloneDX / JSON）、结果能进流水线被消费。

本篇按「代码 → 依赖 → 镜像 → 配置 → 集群 → 运行时」六个阶段，给出工具选型、常用命令与 CI 集成方式。

## 一、按阶段选工具

![扫描工具链全景：按阶段选工具](../assets/security-toolchain.svg)

| 阶段 | 检查对象 | 代表工具 | 输出 |
| --- | --- | --- | --- |
| 代码 | 源码缺陷、注入、硬编码密钥 | CodeQL、Semgrep、gitleaks | SARIF |
| 依赖 | 第三方库已知漏洞 | Trivy fs、Grype、OSV-Scanner | SARIF / JSON |
| 镜像 | 容器镜像 OS 包 + 语言依赖 | Trivy image、Grype | SARIF / CycloneDX |
| 配置 | IaC、K8s YAML、Dockerfile | Trivy config、checkov、Kubescape | SARIF |
| 集群 | 运行中的集群与合规基线 | kube-bench、Kubescape | JSON |
| 运行时 | 异常行为、越权、逃逸 | Falco | JSON / 告警 |

:::tip 一句话理解
先用 **Trivy** 打通「依赖 + 镜像 + 配置」三个场景（一个工具、同一套规则库），团队上手成本最低；等流程跑顺了再按需要引入专用工具。
:::

## 二、代码扫描（SAST）

### 2.1 Semgrep

Semgrep 以「语义化模式匹配」著称，规则可读性强、上手快：

```shell
# 安装
pip install semgrep

# 用官方规则集扫描当前目录
semgrep --config=auto .

# 指定输出 SARIF，供 CI 消费
semgrep --config=auto --sarif --output semgrep.sarif .

# 只报高置信度、高严重度问题
semgrep --config=auto --severity=ERROR --error .
```

### 2.2 硬编码密钥扫描（gitleaks）

密钥是最容易被顺手提交进 Git 的东西。**在 pre-commit 阶段拦截**成本最低：

```shell
# 安装后扫描仓库历史（含所有 commit）
gitleaks detect --source . --report-format sarif --report-path gitleaks.sarif

# 只扫描暂存区（pre-commit 用）
gitleaks protect --staged
```

```yaml [.pre-commit-config.yaml]
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.28.0
    hooks:
      - id: gitleaks
```

:::danger 注意
密钥一旦进入 Git 历史，**即使后续 commit 删除，历史里依然存在**。发现泄漏后的正确处理是：① 立即轮换/吊销该凭据；② 用 `git filter-repo` 重写历史并强推（需协调所有协作者）；③ 排查该密钥被使用的所有位置。详见[密钥与凭据治理](../SecretGovernance/index.md)。
:::

## 三、依赖扫描（SCA）

```shell
# Trivy 扫描文件系统依赖（含 lock 文件）
trivy fs --scanners vuln --severity HIGH,CRITICAL .

# 扫描并生成 SBOM
trivy fs --format cyclonedx --output sbom.cdx.json .

# Grype：基于 Syft 生成的 SBOM 做漏洞匹配
syft dir:. -o spdx-json > sbom.spdx.json
grype sbom:sbom.spdx.json --fail-on high
```

| 工具 | 强项 | 备注 |
| --- | --- | --- |
| Trivy | 一体化、规则全 | 注意升级到 0.74.0+（旧版有投毒事件） |
| Grype + Syft | SBOM 驱动、可复现 | SBOM 是中间产物，可存档审计 |
| OSV-Scanner | 直接查 OSV 数据库 | Google 维护，覆盖多生态 |

## 四、镜像扫描

镜像扫描是容器安全的必答题，细节见 [Docker 安全加固](../../Docker/Security/index.md)，这里给工具链视角的命令：

```shell
# 扫描本地镜像
trivy image --severity HIGH,CRITICAL --exit-code 1 nginx:1.27-alpine

# 扫描远程仓库镜像并输出 SBOM
trivy image --format cyclonedx --output image.cdx.json registry.example.com/app:v1

# 只报告「已修复版本存在」的漏洞（减少噪声）
trivy image --ignore-unfixed --severity HIGH,CRITICAL registry.example.com/app:v1
```

:::warning 说明
`--ignore-unfixed` 会过滤掉「上游还没修复版本」的漏洞。这不代表风险消失，而是把这类无法通过升级解决的问题单独管理（用配置缓解或接受）。是否开启取决于团队策略，**但必须一致**，否则门禁结果会来回抖动。
:::

## 五、配置扫描

```shell
# 扫描 IaC 与 K8s 清单
trivy config --severity HIGH,CRITICAL ./deploy

# checkov：规则可自定义
checkov -d ./terraform --output sarif --output-file-path .

# Kubescape：集群 + YAML 一起看
kubescape scan --enable-host-scan --format sarif --output kubescape.sarif
```

## 六、集群与运行时

集群基线的检查工具见[基线合规](../BaselineCompliance/index.md)；运行时检测的工具与规则见[审计与检测](../AuditDetection/index.md)。这里强调两者的**分工**：

- **集群扫描（kube-bench / Kubescape）**：周期性体检，回答「当前配置是否合规」，是**快照**；
- **运行时检测（Falco）**：持续监控，回答「此刻有没有异常行为」，是**流**。

:::tip 一句话理解
快照回答「门锁了没有」，流回答「有人正在撬锁吗」。两者缺一不可。
:::

## 七、统一接入 CI

多个工具的输出格式各异，CI 里要做的第一件事是**统一格式**。SARIF 是代码扫描的事实标准，GitHub/GitLab 都能直接消费：

```yaml [.github/workflows/security-scan.yaml]
name: security-scan
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write      # 上传 SARIF 需要
    steps:
      - uses: actions/checkout@v4

      - name: Secret scan (gitleaks)
        run: |
          docker run --rm -v "$PWD:/src" \
            zricethezav/gitleaks:latest detect --source /src \
            --report-format sarif --report-path /src/gitleaks.sarif
        continue-on-error: true

      - name: Dependency + config scan (Trivy)
        uses: aquasecurity/trivy-action@0.28.0
        with:
          scan-type: fs
          scan-ref: .
          severity: HIGH,CRITICAL
          exit-code: "1"
          format: sarif
          output: trivy.sarif

      - name: Upload SARIF (gitleaks)
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with: { sarif_file: gitleaks.sarif }

      - name: Upload SARIF (Trivy)
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with: { sarif_file: trivy.sarif }
```

### 7.1 门禁策略设计

门禁太松没用，太严会让团队想办法绕过。推荐分级：

| 阶段 | 阻断策略 |
| --- | --- |
| PR / pre-commit | 仅阻断**密钥泄漏**与**明确高危** |
| 主干构建 | 阻断所有 CRITICAL + 有修复版本的高危 |
| 发布前 | 需附 SBOM，镜像必须已签名验签通过 |

:::danger 注意
不要一开始就把**所有中低危**设为阻断。结果是开发者被迫写一堆 `ignore` 注释，门禁形同虚设，还留下大量无主例外。正确做法是「只阻断真正要立刻处理的那部分」，其余进看板排期。
:::

## 八、结果治理：让扫描有价值

扫描最容易失败的形态是「扫了但没人看」。三个必要动作：

1. **去重与基线化**：把存量问题记为基线，只对**新增**问题阻断（ratchet 策略），否则历史欠债会淹没真实信号。
2. **进 PR 评论**：让问题出现在开发者最关注的地方，而不是某个孤立看板。
3. **趋势看板**：按周统计各阶段新增/修复数，让「债在减少」看得见。

## 九、验证方式

```shell
# 1. 逐个工具确认可运行（以 Trivy 为例）
trivy --version            # 应 >= 0.74.0
trivy fs --severity CRITICAL . | tail -5

# 2. 确认输出格式可被 CI 消费
trivy fs --format sarif --output /tmp/t.sarif .
python -c "import json;d=json.load(open('/tmp/t.sarif'));print('runs=',len(d['runs']))"

# 3. 确认门禁生效：故意引入一个高危依赖/密钥，CI 应失败
echo "AWS_KEY=AKIAIOSFODNN7EXAMPLE" > /tmp/leak.txt
gitleaks detect --source /tmp --no-git ; echo "exit=$? (预期非 0)"
```

## 十、参考资料

- Semgrep 文档：<https://semgrep.dev/docs/>
- gitleaks：<https://github.com/gitleaks/gitleaks>
- Trivy 文档：<https://trivy.dev/latest/docs/>
- Grype / Syft：<https://github.com/anchore/grype>
- SARIF 规范：<https://sarifweb.azurewebsites.net/>
- OSV（开源漏洞数据库）：<https://osv.dev/>

## 相关专题

- [基线合规与自动化](../BaselineCompliance/index.md)
- [漏洞管理生命周期](../VulnerabilityManagement/index.md)
- [SBOM 与软件供应链](../SbomSupplyChain/index.md)
- [Docker 安全加固](../../Docker/Security/index.md)
- [工具：CI/CD](../../../Tools/CICD/index.md)
