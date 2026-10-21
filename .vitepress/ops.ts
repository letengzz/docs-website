export const Ansible = [
  {
    text: "Ansible 自动化运维",
    link: "/docs/Ops/Ansible/index.md",
    items: [
      { text: "Ansible 概述", link: "/docs/Ops/Ansible/Overview/index.md" },
      { text: "安装与配置", link: "/docs/Ops/Ansible/Install/index.md" },
      { text: "Inventory 主机清单", link: "/docs/Ops/Ansible/Inventory/index.md" },
      { text: "模块详解", link: "/docs/Ops/Ansible/Module/index.md" },
      { text: "Playbook 剧本", link: "/docs/Ops/Ansible/Playbook/index.md" },
      { text: "变量与事实", link: "/docs/Ops/Ansible/Variable/index.md" },
      { text: "Role 角色", link: "/docs/Ops/Ansible/Role/index.md" },
      { text: "实战：批量交付 Web 服务器", link: "/docs/Ops/Ansible/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Ops/Ansible/FAQ/index.md" },
    ],
  },
];
export const Terraform = [
  {
    text: "Terraform",
    link: "/docs/Ops/Terraform/index.md",
    items: [
      { text: "概述与选型", link: "/docs/Ops/Terraform/Overview/index.md" },
      { text: "安装与初始化", link: "/docs/Ops/Terraform/Install/index.md" },
      { text: "HCL 语法与表达式", link: "/docs/Ops/Terraform/HCL/index.md" },
      { text: "资源、数据源与变量", link: "/docs/Ops/Terraform/Resource/index.md" },
      { text: "State 与远程后端", link: "/docs/Ops/Terraform/State/index.md" },
      { text: "模块与注册表", link: "/docs/Ops/Terraform/Module/index.md" },
      { text: "实战：交付一套云上环境", link: "/docs/Ops/Terraform/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Ops/Terraform/FAQ/index.md" },
    ],
  },
];
export const SecurityHardening = [
  {
    text: "安全加固",
    link: "/docs/Ops/SecurityHardening/index.md",
    items: [
      { text: "安全加固方法论", link: "/docs/Ops/SecurityHardening/Overview/index.md" },
      { text: "基线合规与自动化", link: "/docs/Ops/SecurityHardening/BaselineCompliance/index.md" },
      { text: "扫描工具链", link: "/docs/Ops/SecurityHardening/ScanningToolchain/index.md" },
      { text: "漏洞管理生命周期", link: "/docs/Ops/SecurityHardening/VulnerabilityManagement/index.md" },
      { text: "SBOM 与软件供应链", link: "/docs/Ops/SecurityHardening/SbomSupplyChain/index.md" },
      { text: "密钥与凭据治理", link: "/docs/Ops/SecurityHardening/SecretGovernance/index.md" },
      { text: "审计与检测", link: "/docs/Ops/SecurityHardening/AuditDetection/index.md" },
      { text: "实战：端到端安全流水线", link: "/docs/Ops/SecurityHardening/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Ops/SecurityHardening/FAQ/index.md" },
    ],
  },
];
export const Docker = [
  {
    text: "Docker",
    link: "/docs/Ops/Docker/index.md",
    items: [
      { text: "Docker 概述", link: "/docs/Ops/Docker/Overview/index.md" },
      { text: "Docker 安装与卸载", link: "/docs/Ops/Docker/InstallUninstall/index.md" },
      { text: "Docker 容器与沙盒", link: "/docs/Ops/Docker/ContainersSandboxes/index.md" },
      { text: "Docker 进程命令", link: "/docs/Ops/Docker/ProcessCommand/index.md" },
      { text: "Docker 镜像", link: "/docs/Ops/Docker/Images/index.md" },
      { text: "Docker 容器", link: "/docs/Ops/Docker/Containers/index.md" },
      { text: "Docker 数据卷", link: "/docs/Ops/Docker/Volumes/index.md" },
      { text: "Dockerfile", link: "/docs/Ops/Docker/Dockerfile/index.md" },
      { text: "Docker 网络", link: "/docs/Ops/Docker/Network/index.md" },
      { text: "Docker Compose", link: "/docs/Ops/Docker/DockerCompose/index.md" },
      { text: "Docker 管理平台", link: "/docs/Ops/Docker/ManagePlatform/index.md" },
      { text: "Docker 监控平台", link: "/docs/Ops/Docker/CIG/index.md" },
      { text: "镜像上传阿里云", link: "/docs/Ops/Docker/DockerToAli/index.md" },
      { text: "Docker 常见错误", link: "/docs/Ops/Docker/Errors/index.md" },
      {
        text: "Docker 进阶",
        collapsed: true,
        items: [
          { text: "Dockerfile 最佳实践", link: "/docs/Ops/Docker/BestPractices/index.md" },
          { text: "多阶段构建", link: "/docs/Ops/Docker/Multistage/index.md" },
          { text: "Docker Compose 进阶", link: "/docs/Ops/Docker/ComposeAdvanced/index.md" },
          { text: "网络模式深入", link: "/docs/Ops/Docker/NetworkAdvanced/index.md" },
          { text: "数据卷与挂载最佳实践", link: "/docs/Ops/Docker/VolumesAdvanced/index.md" },
          { text: "容器监控", link: "/docs/Ops/Docker/Monitor/index.md" },
          { text: "安全加固", link: "/docs/Ops/Docker/Security/index.md" },
          { text: "Docker 与 CI/CD 集成", link: "/docs/Ops/Docker/CIIntegration/index.md" },
          { text: "常见问题与最佳实践", link: "/docs/Ops/Docker/FAQ/index.md" },
        ],
      },
    ],
  },
];
export const JumpServer = [{ text: "JumpServer", link: "/docs/Ops/JumpServer/index.md" }];
export const Kubernetes = [
  {
    text: "Kubernetes",
    link: "/docs/Ops/Kubernetes/index.md",
    collapsed: true,
    items: [
      { text: "核心概念与架构", link: "/docs/Ops/Kubernetes/Overview/index.md" },
      { text: "安装与集群搭建", link: "/docs/Ops/Kubernetes/Install/index.md" },
      { text: "Pod 详解", link: "/docs/Ops/Kubernetes/Pod/index.md" },
      { text: "Deployment 与工作负载", link: "/docs/Ops/Kubernetes/Deployment/index.md" },
      { text: "Service 与网络", link: "/docs/Ops/Kubernetes/Service/index.md" },
      { text: "Ingress 入口", link: "/docs/Ops/Kubernetes/Ingress/index.md" },
      { text: "ConfigMap 与 Secret", link: "/docs/Ops/Kubernetes/ConfigMapSecret/index.md" },
      { text: "存储与 PV/PVC", link: "/docs/Ops/Kubernetes/Storage/index.md" },
      { text: "监控与运维", link: "/docs/Ops/Kubernetes/Monitoring/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Ops/Kubernetes/FAQ/index.md" },
    ],
  },
];
export const Linux = [
  {
    text: "Linux",
    link: "/docs/Ops/Linux/index.md",
    items: [
      { text: "Linux 概述", link: "/docs/Ops/Linux/Overview/index.md" },
      { text: "目录结构", link: "/docs/Ops/Linux/DirectoryStructure/index.md" },
      { text: "文件与目录命令", link: "/docs/Ops/Linux/FileCommand/index.md" },
      { text: "文本处理命令", link: "/docs/Ops/Linux/TextProcessing/index.md" },
      { text: "权限与用户", link: "/docs/Ops/Linux/PermissionUser/index.md" },
      { text: "进程与服务", link: "/docs/Ops/Linux/ProcessService/index.md" },
      { text: "网络命令", link: "/docs/Ops/Linux/NetworkCommand/index.md" },
      { text: "Shell 基础", link: "/docs/Ops/Linux/ShellBasic/index.md" },
      {
        text: "Linux 进阶",
        link: "/docs/Ops/Linux/Advanced/index.md",
        collapsed: true,
        items: [
          { text: "Shell 脚本编程", link: "/docs/Ops/Linux/Advanced/ShellScripting/index.md" },
          { text: "systemd 服务管理", link: "/docs/Ops/Linux/Advanced/Systemd/index.md" },
          { text: "定时任务", link: "/docs/Ops/Linux/Advanced/CronTasks/index.md" },
          { text: "性能调优", link: "/docs/Ops/Linux/Advanced/PerformanceTuning/index.md" },
          { text: "安全加固", link: "/docs/Ops/Linux/Advanced/SecurityHardening/index.md" },
          { text: "故障排查", link: "/docs/Ops/Linux/Advanced/Troubleshooting/index.md" },
          { text: "实战：交付一台生产可用的服务器", link: "/docs/Ops/Linux/Advanced/Practice/index.md" },
          { text: "进阶常见问题与最佳实践", link: "/docs/Ops/Linux/Advanced/FAQ/index.md" },
        ],
      },
      { text: "常见问题与最佳实践", link: "/docs/Ops/Linux/FAQ/index.md" },
    ],
  },
];
export const Monitoring = [
  {
    text: "监控告警",
    link: "/docs/Ops/Monitoring/index.md",
    items: [
      { text: "监控体系与可观测性", link: "/docs/Ops/Monitoring/Overview/index.md" },
      { text: "Prometheus 入门", link: "/docs/Ops/Monitoring/Prometheus/index.md" },
      { text: "指标采集", link: "/docs/Ops/Monitoring/MetricsCollect/index.md" },
      { text: "Grafana 可视化", link: "/docs/Ops/Monitoring/Grafana/index.md" },
      { text: "告警规则与 Alertmanager", link: "/docs/Ops/Monitoring/Alerting/index.md" },
      { text: "日志监控", link: "/docs/Ops/Monitoring/LogMonitoring/index.md" },
      { text: "实战：监控微服务与容器环境", link: "/docs/Ops/Monitoring/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Ops/Monitoring/FAQ/index.md" },
    ],
  },
];
export const Observability = [
  {
    text: "可观测性深入",
    link: "/docs/Ops/Observability/index.md",
    items: [
      { text: "概述：从监控到可观测性的四条边界", link: "/docs/Ops/Observability/Overview/index.md" },
      { text: "OpenTelemetry：统一标准与接入", link: "/docs/Ops/Observability/OpenTelemetry/index.md" },
      { text: "Collector：管道工程化", link: "/docs/Ops/Observability/Collector/index.md" },
      { text: "采样决策：看到什么，与不能宣称什么", link: "/docs/Ops/Observability/Sampling/index.md" },
      { text: "持续剖析：第四类信号与火焰图", link: "/docs/Ops/Observability/Profiles/index.md" },
      { text: "后端与存储选型", link: "/docs/Ops/Observability/Backends/index.md" },
      { text: "观测成本治理", link: "/docs/Ops/Observability/Cost/index.md" },
      { text: "实战：给实时监控大盘接入端到端观测", link: "/docs/Ops/Observability/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Ops/Observability/FAQ/index.md" },
    ],
  },
];
export const Nginx = [
  {
    text: "Nginx",
    link: "/docs/Ops/Nginx/index.md",
    collapsed: true,
    items: [
      { text: "Nginx 概述与安装", link: "/docs/Ops/Nginx/Overview/index.md" },
      { text: "配置文件详解", link: "/docs/Ops/Nginx/ConfigFile/index.md" },
      { text: "静态资源服务", link: "/docs/Ops/Nginx/StaticResources/index.md" },
      { text: "反向代理", link: "/docs/Ops/Nginx/ReverseProxy/index.md" },
      { text: "负载均衡", link: "/docs/Ops/Nginx/LoadBalance/index.md" },
      { text: "HTTPS 配置", link: "/docs/Ops/Nginx/Https/index.md" },
      { text: "缓存配置", link: "/docs/Ops/Nginx/Cache/index.md" },
      { text: "限流配置", link: "/docs/Ops/Nginx/RateLimit/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Ops/Nginx/FAQ/index.md" },
    ],
  },
];
export const Network = [
  {
    text: "网络基础",
    link: "/docs/Ops/Network/index.md",
    collapsed: true,
    items: [
      { text: "网络分层与 TCP/IP 模型", link: "/docs/Ops/Network/Layering/index.md" },
      { text: "DNS 解析与配置", link: "/docs/Ops/Network/Dns/index.md" },
      { text: "TCP/IP 核心机制", link: "/docs/Ops/Network/TcpIp/index.md" },
      { text: "HTTP 与 HTTPS", link: "/docs/Ops/Network/HttpHttps/index.md" },
      { text: "网络排查方法论", link: "/docs/Ops/Network/Troubleshoot/index.md" },
      { text: "抓包分析：tcpdump 与 Wireshark", link: "/docs/Ops/Network/Capture/index.md" },
      { text: "实战：网络故障排查全流程", link: "/docs/Ops/Network/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Ops/Network/FAQ/index.md" },
    ],
  },
];
export const LogSystem = [
  {
    text: "日志体系",
    link: "/docs/Ops/LogSystem/index.md",
    items: [
      { text: "日志体系概述", link: "/docs/Ops/LogSystem/Overview/index.md" },
      { text: "日志采集与传输", link: "/docs/Ops/LogSystem/Collection/index.md" },
      { text: "Elastic Stack（ELK）", link: "/docs/Ops/LogSystem/ElasticStack/index.md" },
      { text: "Grafana Loki", link: "/docs/Ops/LogSystem/Loki/index.md" },
      { text: "日志查询与分析", link: "/docs/Ops/LogSystem/QueryAnalysis/index.md" },
      { text: "日志告警与联动", link: "/docs/Ops/LogSystem/Alerting/index.md" },
      { text: "存储、保留与成本优化", link: "/docs/Ops/LogSystem/Retention/index.md" },
      { text: "实战：搭建集中式日志平台", link: "/docs/Ops/LogSystem/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Ops/LogSystem/FAQ/index.md" },
    ],
  },
];
export const BackupDR = [
  {
    text: "备份与容灾",
    link: "/docs/Ops/BackupDR/index.md",
    items: [
      { text: "体系概述：备份、高可用与容灾的边界", link: "/docs/Ops/BackupDR/Overview/index.md" },
      { text: "备份策略设计：全量、增量与保留轮转", link: "/docs/Ops/BackupDR/Strategy/index.md" },
      { text: "备份工具矩阵：从 mysqldump 到 Velero", link: "/docs/Ops/BackupDR/Toolchain/index.md" },
      { text: "恢复与演练：PITR、校验与演练设计", link: "/docs/Ops/BackupDR/Recovery/index.md" },
      { text: "容灾架构：冷备、温备、热备与多活", link: "/docs/Ops/BackupDR/DisasterRecovery/index.md" },
      { text: "实战：给博客平台做一套备份与容灾方案", link: "/docs/Ops/BackupDR/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Ops/BackupDR/FAQ/index.md" },
    ],
  },
];
export const ChaosEngineering = [
  {
    text: "混沌工程",
    link: "/docs/Ops/ChaosEngineering/index.md",
    items: [
      { text: "概述与稳态假设", link: "/docs/Ops/ChaosEngineering/Overview/index.md" },
      { text: "故障注入分类", link: "/docs/Ops/ChaosEngineering/FaultInjection/index.md" },
      { text: "实验设计方法", link: "/docs/Ops/ChaosEngineering/ExperimentDesign/index.md" },
      { text: "Chaos Mesh 深入", link: "/docs/Ops/ChaosEngineering/ChaosMesh/index.md" },
      { text: "工具全景与选型", link: "/docs/Ops/ChaosEngineering/Platforms/index.md" },
      { text: "演练中的可观测", link: "/docs/Ops/ChaosEngineering/Observability/index.md" },
      { text: "演练日组织（GameDay）", link: "/docs/Ops/ChaosEngineering/GameDays/index.md" },
      { text: "实战：博客平台故障注入演练", link: "/docs/Ops/ChaosEngineering/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Ops/ChaosEngineering/FAQ/index.md" },
    ],
  },
];
export const OpsOthers = [{ text: "运维其他", link: "/docs/Ops/Others/index.md" }];
export const VM = [{ text: "虚拟机", link: "/docs/Ops/VM/index.md" }];
export const ContainerOrchestration = [
  {
    text: "容器编排进阶",
    link: "/docs/Ops/ContainerOrchestration/index.md",
    items: [
      { text: "Helm：Kubernetes 应用包管理", link: "/docs/Ops/ContainerOrchestration/Helm/index.md" },
      { text: "Operator：把运维经验变成代码", link: "/docs/Ops/ContainerOrchestration/Operator/index.md" },
      {
        text: "服务网格：Istio 流量与安全治理",
        link: "/docs/Ops/ContainerOrchestration/ServiceMesh/index.md",
        collapsed: true,
        items: [
          { text: "架构原理：控制面与两种数据面", link: "/docs/Ops/ContainerOrchestration/ServiceMesh/Architecture/index.md" },
          { text: "版本演进与升级策略", link: "/docs/Ops/ContainerOrchestration/ServiceMesh/Version/index.md" },
          { text: "流量管理：匹配、路由与灰度", link: "/docs/Ops/ContainerOrchestration/ServiceMesh/TrafficManagement/index.md" },
          { text: "韧性设计：超时、重试、熔断与限流", link: "/docs/Ops/ContainerOrchestration/ServiceMesh/Resilience/index.md" },
          { text: "可观测性：指标、日志与追踪", link: "/docs/Ops/ContainerOrchestration/ServiceMesh/Observability/index.md" },
          { text: "安全：mTLS、身份与授权", link: "/docs/Ops/ContainerOrchestration/ServiceMesh/Security/index.md" },
          { text: "Ambient 模式：无 Sidecar 的分层网格", link: "/docs/Ops/ContainerOrchestration/ServiceMesh/AmbientMesh/index.md" },
          { text: "实战：为博客平台接入网格", link: "/docs/Ops/ContainerOrchestration/ServiceMesh/Practice/index.md" },
          { text: "常见问题与排错", link: "/docs/Ops/ContainerOrchestration/ServiceMesh/FAQ/index.md" },
        ],
      },
      { text: "弹性伸缩：HPA、VPA 与 KEDA", link: "/docs/Ops/ContainerOrchestration/Autoscaling/index.md" },
      { text: "多集群：联邦、MCS 与容灾", link: "/docs/Ops/ContainerOrchestration/MultiCluster/index.md" },
      {
        text: "GitOps：声明式持续交付",
        link: "/docs/Ops/ContainerOrchestration/GitOps/index.md",
        collapsed: true,
        items: [
          { text: "GitOps 理念与工作原理", link: "/docs/Ops/ContainerOrchestration/GitOps/Overview/index.md" },
          { text: "Argo CD：安装与核心对象", link: "/docs/Ops/ContainerOrchestration/GitOps/ArgoCD/index.md" },
          { text: "Flux：另一条主线", link: "/docs/Ops/ContainerOrchestration/GitOps/FluxCD/index.md" },
          { text: "配置仓库设计与多环境", link: "/docs/Ops/ContainerOrchestration/GitOps/RepoStructure/index.md" },
          { text: "密钥管理", link: "/docs/Ops/ContainerOrchestration/GitOps/Secrets/index.md" },
          { text: "渐进发布与回滚", link: "/docs/Ops/ContainerOrchestration/GitOps/ProgressiveDelivery/index.md" },
          { text: "镜像更新与 CI 分工", link: "/docs/Ops/ContainerOrchestration/GitOps/ImageUpdate/index.md" },
          { text: "实战：博客平台 GitOps 交付", link: "/docs/Ops/ContainerOrchestration/GitOps/Practice/index.md" },
          { text: "常见问题与最佳实践", link: "/docs/Ops/ContainerOrchestration/GitOps/FAQ/index.md" },
        ],
      },
      { text: "容器与集群安全加固", link: "/docs/Ops/ContainerOrchestration/Security/index.md" },
      { text: "实战：GitOps + 弹性伸缩交付闭环", link: "/docs/Ops/ContainerOrchestration/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Ops/ContainerOrchestration/FAQ/index.md" },
    ],
  },
];
export const CloudNative = [
  {
    text: "云原生",
    link: "/docs/Ops/CloudNative/index.md",
    items: [
      { text: "概述与选型", link: "/docs/Ops/CloudNative/Overview/index.md" },
      { text: "Serverless 与函数计算", link: "/docs/Ops/CloudNative/Serverless/index.md" },
      { text: "云函数工程化", link: "/docs/Ops/CloudNative/FunctionEngineering/index.md" },
      { text: "托管容器服务", link: "/docs/Ops/CloudNative/ContainerService/index.md" },
      { text: "云成本治理（FinOps）", link: "/docs/Ops/CloudNative/FinOps/index.md" },
      { text: "实战：迁移与验收", link: "/docs/Ops/CloudNative/Practice/index.md" },
      { text: "常见问题与排错", link: "/docs/Ops/CloudNative/FAQ/index.md" },
    ],
  },
];
export const IncidentResponse = [
  {
    text: "故障应急体系",
    link: "/docs/Ops/IncidentResponse/index.md",
    items: [
      { text: "总览：故障应急的四条边界", link: "/docs/Ops/IncidentResponse/Overview/index.md" },
      { text: "值班制度：保证有人能醒", link: "/docs/Ops/IncidentResponse/OnCall/index.md" },
      { text: "故障定级", link: "/docs/Ops/IncidentResponse/Severity/index.md" },
      { text: "应急指挥与协同", link: "/docs/Ops/IncidentResponse/Command/index.md" },
      { text: "应急预案与运行手册", link: "/docs/Ops/IncidentResponse/Runbook/index.md" },
      { text: "定位与止损", link: "/docs/Ops/IncidentResponse/Diagnosis/index.md" },
      { text: "演练与预案校验", link: "/docs/Ops/IncidentResponse/Drill/index.md" },
      { text: "实战：一次连接池耗尽事故", link: "/docs/Ops/IncidentResponse/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Ops/IncidentResponse/FAQ/index.md" },
    ],
  },
];
export const CloudArchitecture = [
  {
    text: "云上架构",
    link: "/docs/Ops/CloudArchitecture/index.md",
    items: [
      { text: "总览：上云先要决定的五件事", link: "/docs/Ops/CloudArchitecture/Overview/index.md" },
      { text: "VPC 与网络边界", link: "/docs/Ops/CloudArchitecture/Network/index.md" },
      { text: "负载均衡", link: "/docs/Ops/CloudArchitecture/LoadBalancing/index.md" },
      { text: "弹性伸缩", link: "/docs/Ops/CloudArchitecture/AutoScaling/index.md" },
      { text: "可用性拓扑", link: "/docs/Ops/CloudArchitecture/Availability/index.md" },
      { text: "云上安全边界", link: "/docs/Ops/CloudArchitecture/Security/index.md" },
      { text: "成本与规格选型", link: "/docs/Ops/CloudArchitecture/Cost/index.md" },
      { text: "实战：把监控大盘搬上云", link: "/docs/Ops/CloudArchitecture/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Ops/CloudArchitecture/FAQ/index.md" },
    ],
  },
];
export const EdgeCDN = [
  {
    text: "边缘计算与 CDN",
    link: "/docs/Ops/EdgeCDN/index.md",
    items: [
      { text: "总览：边缘与 CDN 的四条边界", link: "/docs/Ops/EdgeCDN/Overview/index.md" },
      { text: "CDN 原理：从调度到回源", link: "/docs/Ops/EdgeCDN/CDNPrinciple/index.md" },
      { text: "缓存策略：键、时效与失效", link: "/docs/Ops/EdgeCDN/CacheStrategy/index.md" },
      { text: "边缘计算与边缘函数", link: "/docs/Ops/EdgeCDN/EdgeCompute/index.md" },
      { text: "边缘数据与状态", link: "/docs/Ops/EdgeCDN/EdgeData/index.md" },
      { text: "边缘安全", link: "/docs/Ops/EdgeCDN/Security/index.md" },
      { text: "性能与成本", link: "/docs/Ops/EdgeCDN/PerformanceCost/index.md" },
      { text: "实战：把一个站点与 API 迁到边缘", link: "/docs/Ops/EdgeCDN/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Ops/EdgeCDN/FAQ/index.md" },
    ],
  },
];
export const PerformanceEngineering = [
  {
    text: "性能与容量工程",
    link: "/docs/Ops/PerformanceEngineering/index.md",
    items: [
      { text: "总览：性能与容量的四条边界", link: "/docs/Ops/PerformanceEngineering/Overview/index.md" },
      { text: "SLO 与性能需求", link: "/docs/Ops/PerformanceEngineering/SLO/index.md" },
      { text: "定量建模：并发、排队与扩展性", link: "/docs/Ops/PerformanceEngineering/Modeling/index.md" },
      { text: "压测方法论与工具", link: "/docs/Ops/PerformanceEngineering/LoadTesting/index.md" },
      { text: "瓶颈定位", link: "/docs/Ops/PerformanceEngineering/Bottleneck/index.md" },
      { text: "容量规划与弹性", link: "/docs/Ops/PerformanceEngineering/Capacity/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Ops/PerformanceEngineering/FAQ/index.md" },
    ],
  },
];
export const CapacityCost = [
  {
    text: "容量与成本治理",
    link: "/docs/Ops/CapacityCost/index.md",
    items: [
      { text: "总览：三本账与四个决策点（CCO-A~CCO-H）", link: "/docs/Ops/CapacityCost/Overview/index.md" },
      { text: "容量台账与预测（CCF-A~CCF-H）", link: "/docs/Ops/CapacityCost/CapacityPlan/index.md" },
      { text: "归集与分摊（CCA-A~CCA-H）", link: "/docs/Ops/CapacityCost/Allocation/index.md" },
      { text: "单位成本（CCU-A~CCU-H）", link: "/docs/Ops/CapacityCost/UnitEconomics/index.md" },
      { text: "预算与告警（CCB-A~CCB-H）", link: "/docs/Ops/CapacityCost/BudgetAlert/index.md" },
      { text: "闲置与浪费治理（CCW-A~CCW-H）", link: "/docs/Ops/CapacityCost/Waste/index.md" },
      { text: "承诺折扣治理（CCK-A~CCK-H）", link: "/docs/Ops/CapacityCost/Commitment/index.md" },
      { text: "实战：一个季度的治理循环（CCP-A~CCP-H）", link: "/docs/Ops/CapacityCost/Practice/index.md" },
      { text: "常见问题与最佳实践（CCQ-A~CCQ-H）", link: "/docs/Ops/CapacityCost/FAQ/index.md" },
    ],
  },
];
export const MultiActive = [
  {
    text: "多活与单元化",
    link: "/docs/Ops/MultiActive/index.md",
    items: [
      { text: "体系概述：多活、容灾与单元化的边界（MAO-A~MAO-H）", link: "/docs/Ops/MultiActive/Overview/index.md" },
      { text: "单元化模型：把用户切成能独立承载的组（MAC-A~MAC-H）", link: "/docs/Ops/MultiActive/CellModel/index.md" },
      { text: "路由：请求怎么找到自己的单元（MAR-A~MAR-H）", link: "/docs/Ops/MultiActive/Routing/index.md" },
      { text: "跨单元数据同步：单向、双向与事件流（MAS-A~MAS-H）", link: "/docs/Ops/MultiActive/DataSync/index.md" },
      { text: "冲突裁决：收敛不等于正确（MAX-A~MAX-H）", link: "/docs/Ops/MultiActive/Conflict/index.md" },
      { text: "流量切换：三段时间与回切（MAT-A~MAT-H）", link: "/docs/Ops/MultiActive/TrafficSwitch/index.md" },
      { text: "演练：五级金字塔与可证伪判据（MAD-A~MAD-H）", link: "/docs/Ops/MultiActive/Drill/index.md" },
      { text: "成本：单元化是乘法（MAE-A~MAE-H）", link: "/docs/Ops/MultiActive/Cost/index.md" },
      { text: "实战：给协作看板做双单元 + 切流（MAP-A~MAP-H）", link: "/docs/Ops/MultiActive/Practice/index.md" },
      { text: "常见问题与最佳实践（MAF-A~MAF-H）", link: "/docs/Ops/MultiActive/FAQ/index.md" },
    ],
  },
];
export const ChangeManagement = [
  {
    text: "变更管理与发布工程",
    link: "/docs/Ops/ChangeManagement/index.md",
    items: [
      { text: "体系概述：分级、授权、留痕（CHG-A~CHG-H）", link: "/docs/Ops/ChangeManagement/Overview/index.md" },
      { text: "变更分级：把「多大的事」算出来（CLS-A~CLS-H）", link: "/docs/Ops/ChangeManagement/Classification/index.md" },
      { text: "窗口与冻结期：什么时候能做（CWN-A~CWN-H）", link: "/docs/Ops/ChangeManagement/ChangeWindow/index.md" },
      { text: "审批留痕：批的是哪一个产物（ATR-A~ATR-H）", link: "/docs/Ops/ChangeManagement/ApprovalTrail/index.md" },
      { text: "变更日历：冲突要在入库时挡住（CCL-A~CCL-H）", link: "/docs/Ops/ChangeManagement/ChangeCalendar/index.md" },
      { text: "高危变更：能写进规则的形状（HRS-A~HRS-H）", link: "/docs/Ops/ChangeManagement/HighRiskChange/index.md" },
      { text: "紧急变更：破窗的边界与额度（EMG-A~EMG-H）", link: "/docs/Ops/ChangeManagement/EmergencyChange/index.md" },
      { text: "实战：一次加列 + 回填 + 切读（CHP-A~CHP-H）", link: "/docs/Ops/ChangeManagement/Practice/index.md" },
      { text: "常见问题与最佳实践（CHQ-A~CHQ-H）", link: "/docs/Ops/ChangeManagement/FAQ/index.md" },
    ],
  },
];
export const CertificateLifecycle = [
  {
    text: "证书与信任链生命周期",
    link: "/docs/Ops/CertificateLifecycle/index.md",
    items: [
      { text: "体系概述：链、时间、用途（CLO-A~CLO-H）", link: "/docs/Ops/CertificateLifecycle/Overview/index.md" },
      { text: "信任链与 X.509：谁签了谁（CLT-A~CLT-H）", link: "/docs/Ops/CertificateLifecycle/TrustChain/index.md" },
      { text: "签发：CSR、SAN 与 ACME（CLI-A~CLI-H）", link: "/docs/Ops/CertificateLifecycle/Issuance/index.md" },
      { text: "部署与链路完整性（CLC-A~CLC-H）", link: "/docs/Ops/CertificateLifecycle/Serving/index.md" },
      { text: "轮换：重叠窗口与密钥不重用（CLR-A~CLR-H）", link: "/docs/Ops/CertificateLifecycle/Rotation/index.md" },
      { text: "过期治理：谁先过期（CLE-A~CLE-H）", link: "/docs/Ops/CertificateLifecycle/Expiry/index.md" },
      { text: "mTLS：证书即身份（CLM-A~CLM-H）", link: "/docs/Ops/CertificateLifecycle/MutualTLS/index.md" },
      { text: "自动化：cert-manager 与 ARI（CLA-A~CLA-H）", link: "/docs/Ops/CertificateLifecycle/Automation/index.md" },
      { text: "实战：一条可轮换的私有链（CLP-A~CLP-H）", link: "/docs/Ops/CertificateLifecycle/Practice/index.md" },
    ],
  },
];
export const DatabaseUpgrade = [
  {
    text: "数据库大版本升级与切换",
    link: "/docs/Ops/DatabaseUpgrade/index.md",
    items: [
      { text: "总览：四类风险与五个阶段（UGO-A~UGO-H）", link: "/docs/Ops/DatabaseUpgrade/Overview/index.md" },
      { text: "支持矩阵：哪些能升、哪些必须先过一站（UGV-A~UGV-H）", link: "/docs/Ops/DatabaseUpgrade/SupportMatrix/index.md" },
      { text: "升级前检查：六道闸门（UGC-A~UGC-H）", link: "/docs/Ops/DatabaseUpgrade/Precheck/index.md" },
      { text: "演练与时间估算：把「停多久」算出来（UGD-A~UGD-H）", link: "/docs/Ops/DatabaseUpgrade/Rehearsal/index.md" },
      { text: "逻辑复制迁移：行过去了，序列没过去（UGL-A~UGL-H）", link: "/docs/Ops/DatabaseUpgrade/LogicalMigration/index.md" },
      { text: "MySQL 8.0 → 8.4：三条路与三个断点（UGM-A~UGM-H）", link: "/docs/Ops/DatabaseUpgrade/MySQL80To84/index.md" },
      { text: "PostgreSQL 17 → 18：pg_upgrade 在搬什么（UGP-A~UGP-H）", link: "/docs/Ops/DatabaseUpgrade/PostgreSQL17To18/index.md" },
      { text: "切换窗口与回滚：0.78 秒里做了什么（UGT-A~UGT-H）", link: "/docs/Ops/DatabaseUpgrade/Cutover/index.md" },
      { text: "切换后验证：四道闸门（UGX-A~UGX-H）", link: "/docs/Ops/DatabaseUpgrade/Verify/index.md" },
      { text: "常见问题与分诊（UGQ-A~UGQ-H）", link: "/docs/Ops/DatabaseUpgrade/FAQ/index.md" },
    ],
  },
];
