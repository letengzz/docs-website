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
export const OpsOthers = [{ text: "运维其他", link: "/docs/Ops/Others/index.md" }];
export const VM = [{ text: "虚拟机", link: "/docs/Ops/VM/index.md" }];
export const ContainerOrchestration = [
  {
    text: "容器编排进阶",
    link: "/docs/Ops/ContainerOrchestration/index.md",
    items: [
      { text: "Helm：Kubernetes 应用包管理", link: "/docs/Ops/ContainerOrchestration/Helm/index.md" },
      { text: "Operator：把运维经验变成代码", link: "/docs/Ops/ContainerOrchestration/Operator/index.md" },
      { text: "服务网格：Istio 流量与安全治理", link: "/docs/Ops/ContainerOrchestration/ServiceMesh/index.md" },
      { text: "弹性伸缩：HPA、VPA 与 KEDA", link: "/docs/Ops/ContainerOrchestration/Autoscaling/index.md" },
      { text: "多集群：联邦、MCS 与容灾", link: "/docs/Ops/ContainerOrchestration/MultiCluster/index.md" },
      { text: "GitOps：Argo CD 声明式交付", link: "/docs/Ops/ContainerOrchestration/GitOps/index.md" },
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
