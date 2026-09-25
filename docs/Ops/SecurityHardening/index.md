# 安全加固

<p style="text-align:center;"><img src="./assets/security-logo.png" style="zoom:75%;" /></p>

安全加固（Security Hardening）是**在系统上线前后，持续削减攻击面、降低被利用概率并缩短暴露窗口**的一整套工程实践。它不是某一台机器的配置清单，而是覆盖「身份 → 主机 → 容器 → 集群 → 应用 → 数据」六层的**横向治理体系**。

本专题讲的是**跨层的治理与流程**：如何选基线、如何管理漏洞生命周期、如何治理密钥、如何做审计与检测、如何把工具串成流水线。**具体某一层的命令级加固**（SSH、防火墙、capability、RBAC、NetworkPolicy 等）分别见下表的既有专题，本专题与之互补而不重复。

## 本专题与其他安全页面的分工

| 层次 | 关心的问题 | 去哪看 |
| --- | --- | --- |
| 主机与系统 | SSH、账户权限、防火墙、SELinux/AppArmor、内核参数 | [Linux 安全加固](../Linux/Advanced/SecurityHardening/index.md) |
| 容器运行时 | 镜像、非 root、capabilities、seccomp、只读根、网络 | [Docker 安全加固](../Docker/Security/index.md) |
| 集群与编排 | RBAC、NetworkPolicy、PSA、策略即代码、运行时检测 | [容器与集群安全加固](../ContainerOrchestration/Security/index.md) |
| **跨层治理（本专题）** | 方法论、基线合规、漏洞管理、SBOM、密钥、审计、工具链 | 本页以下各篇 |

## 专题导航

- [安全加固方法论](Overview/index.md)：纵深防御、威胁建模、NIST CSF、量化度量
- [基线合规与自动化](BaselineCompliance/index.md)：CIS Benchmark、kube-bench、合规闭环与门禁
- [扫描工具链](ScanningToolchain/index.md)：SAST/SCA/镜像/配置/集群/运行时工具选型与 CI 集成
- [漏洞管理生命周期](VulnerabilityManagement/index.md)：发现→评估→定级→修复→验证→闭环，CVSS/EPSS/KEV
- [SBOM 与软件供应链](SbomSupplyChain/index.md)：SPDX/CycloneDX、Syft/Grype、SLSA、cosign 签名验签
- [密钥与凭据治理](SecretGovernance/index.md)：Vault/KMS、动态凭据、轮换与泄漏检测
- [审计与检测](AuditDetection/index.md)：auditd、Falco、云审计、SIEM 与告警闭环
- [实战：一条端到端安全流水线](Practice/index.md)：从提交到运行的四阶段完整实现
- [常见问题与最佳实践](FAQ/index.md)：15 个高频问答、易错点清单、落地路线图

## 核心概念速览

| 概念 | 英文 / 缩写 | 一句话解释 |
| --- | --- | --- |
| 攻击面 | Attack Surface | 外部可触达的入口总和；加固的本质是持续缩小它 |
| 纵深防御 | Defense in Depth | 多层独立控制叠加，单层失守不等于全局失守 |
| 最小权限 | Least Privilege | 主体只拿到完成当前任务所需的最小权限、最短时限 |
| 基线 | Baseline | 一组「必须满足」的安全配置，通常来自 CIS/等保等标准 |
| 合规即代码 | Compliance as Code | 把基线检查写进流水线，回归即失败，而非人工抽查 |
| 软件物料清单 | SBOM | 一份列出软件全部组件与版本关系的「配料表」 |
| 漏洞可利用性 | EPSS / KEV | 预测漏洞被利用的概率 / 已确认在野被利用的目录 |
| 安全 SLA | MTTR | 从发现高危到修复完成的时间目标，按等级约定 |

## 版本状态速览

> 版本与事实均按官方发布页于 **2026-09** 联网核对，具体适用性以官方为准。

| 工具 / 标准 | 当前状态 | 说明 |
| --- | --- | --- |
| Trivy | **0.74.0**（2026-08-14） | 一体化扫描器；注意 v0.69.5/0.69.6 存在投毒事件（CVE-2026-33634），务必升级 |
| Grype | **0.118.0**（2026-08-27） | 漏洞匹配引擎，常与 Syft 生成的 SBOM 搭配 |
| Syft | 与 Grype 同源发布 | SBOM 生成器，输出 SPDX / CycloneDX |
| Falco | **0.44.1**（2026-06-11） | CNCF 毕业项目；0.44 起 eBPF 为现代默认，移除 gRPC/gVisor/legacy-ebpf |
| Kyverno | **1.19.0**（2026-08-20） | Kubernetes 策略即代码；支持 K8s 1.33–1.35 |
| OPA Gatekeeper | **1.19.1** | 基于 Rego 的准入策略引擎 |
| Kubescape | **v4.0.12**（2026-08-12） | 集群安全态势与合规（含 NSA/CIS 框架） |
| kube-bench | **0.8.x** | 按 CIS Kubernetes Benchmark 检查集群 |
| CIS Kubernetes Benchmark | **v1.12.0** | 集群基线标准 |
| CIS Docker Benchmark | **v1.8.0** | Docker 守护进程与容器基线 |
| CIS Ubuntu 24.04 LTS | **v2.0.0**（2026-06） | 主机操作系统基线 |

:::warning 说明
CIS Benchmark 是**版本强相关**的：检查项会随内核、发行版、K8s 版本变化。务必选用与你的操作系统/K8s 主版本**精确对应**的那一版，否则会出现大量「本应合规却报 fail」的误报。托管集群（EKS/GKE/AKS）的控制面由云厂商托管，CIS 中有专门面向托管场景的变体，检测范围需按「你能控制的部分」裁剪。
:::

## 适用对象

- 需要把安全从「出事再补」变成「持续可运营」的运维 / DevSecOps 工程师；
- 要落地合规（等保 2.0、ISO 27001、SOC 2）却不知从哪一控制项下手的团队；
- 需要给 CI/CD 加安全门禁、给集群加准入与运行时检测的平台工程师。

:::tip 一句话理解
安全加固不是「把一堆参数调严」，而是**用工程化手段让「不安全」在流水线里就通不过**——基线进 CI、漏洞进 SLA、密钥进托管、检测进运行时。
:::

## 云上身份与最小权限

自建环境的第一道门是**主机基线与容器加固**（见本页上方分工表）；托管环境（Lambda、托管 K8s、各类云服务）里机器不是你的，**第一道门就变成了「执行身份」**——谁以什么身份去调云 API。托管场景下真正决定爆炸半径的，往往不是这台机器怎么配，而是**这个工作负载拿到了什么角色**。

| 托管形态 | 身份载体 | 常见叫法 |
| --- | --- | --- |
| Serverless 函数 | 函数绑定一个执行角色 | Lambda Execution Role、函数服务账号 |
| 托管 K8s | Pod 关联云身份，无需把密钥塞进容器 | IRSA（EKS）、Workload Identity（GKE / Azure）、RRSA（阿里云 ACK） |
| 托管数据库 / 消息 | 实例级访问策略 + 调用方角色 | 实例 RAM 角色 / 服务关联角色 |

三条纪律：

1. **一个函数（工作负载）一个角色**：不要所有负载共用一个「万能角色」。共用意味着任何一处被攻破，等于全部权限被拿走；审计时也分不清是谁调的。
2. **只列必需的 Action，并写全资源 ARN**：`"Resource": "*"` 与 `"Action": "s3:*"` 这类通配符等于没有限制——一旦触发 SSRF 或依赖投毒，攻击者就能读写整个账号的资源。把资源限定到具体的桶、前缀、表名。
3. **密钥放密钥管理服务，不要塞进环境变量明文**：环境变量会出现在控制台、日志与崩溃转储里。优先用云密钥管理服务（KMS / Secrets Manager / 参数仓库）在运行时注入，或用上面说的身份载体免密钥调用。

```json [最小权限 IAM 策略片段]
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadWriteOneBucketPrefix",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::shop-order-attachments/prod/uploads/*"
    },
    {
      "Sid": "WriteLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:cn-north-1:123456789012:log-group:/aws/lambda/order-processor:*"
    },
    {
      "Sid": "ReadOneSecretOnly",
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:cn-north-1:123456789012:secret:order/db-*"
    }
  ]
}
```

::: danger 托管环境里最容易踩的三个坑
1. **给函数挂 `AdministratorAccess`「先跑起来再说」**：省下的十分钟，会在某次依赖投毒或 SSRF 时以整个账号为代价还回来。正确做法是从最小集合起步，缺什么补什么，用云审计日志反推还缺哪些 Action。
2. **用一个角色给所有环境（dev/staging/prod）**：一处泄漏全环境沦陷。按环境拆分角色与资源 ARN，prod 角色只挂到 prod 函数上。
3. **把密钥写进环境变量或代码**：环境变量在控制台可见、可能进日志；代码进了 Git 就永久留痕。正确做法是走密钥管理服务 + 免密钥身份，轮换时无需改代码。
:::

更细的密钥生命周期与轮换见 [密钥与凭据治理](SecretGovernance/index.md)，函数侧的身份配置与最小权限实践见 [云原生 · 函数工程](../CloudNative/FunctionEngineering/index.md)。
