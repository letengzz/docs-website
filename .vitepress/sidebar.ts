// import { set_sidebar } from "../utils/auto-gen-sidebar.mjs";	// 改成自己的路径
import { Auth, DDD, DesignPatterns, DistributedCache, DotNet, Ecommerce, Go, GoMicroservices, HighPerformanceJava, Java, Ledger, MessageQueue, Microservices, NetworkProgramming, Python, PythonWeb, ReactiveProgramming, SpringCloud, WorkflowEngine } from "./backend";

import { AI_Agent, AI_AgentFramework, AI_AICodingAssistant, AI_FineTuning, AI_LangChain, AI_LLMApp, AI_LLMObservability, AI_LocalModel, AI_Multimodal, AI_OpenClaw, AI_PromptEngineering, AI_PromptSecurity, AI_RAG } from "./AI";
import { FrontBasic, FrontDataVisualization, FrontIntlA11y, FrontLowCode, FrontMicroFrontend, FrontOthers, FrontPWA, FrontSSR, FrontWebAssembly, FrontWebGL, FrontendEngineering, FrontFrame, FrontTesting } from "./frontend";
import { Ansible, BackupDR, ChaosEngineering, CloudArchitecture, CloudNative, ContainerOrchestration, Docker, IncidentResponse, JumpServer, Kubernetes, Linux, LogSystem, Monitoring, Network, Nginx, OpsOthers, SecurityHardening, Terraform, VM } from "./ops";
import { BigData, CDC, ClickHouse, DBOverview, DataModeling, DataWarehouse, Middleware, Neo4j, NoRelational, Relational, SQLOptimization, Sharding, TimeSeries } from "./db";
import { APIDesign, APITools, Build, CICD, Collaboration, DatabaseClients, DependencyGovernance, DocsInfra, Efficiency, IDE, Others, PackageManager, TestingTools, VC } from "./tools";
import { BaseProject, CompleteProject } from "./project";

const OthersReview = [
  {
    text: "复盘杂项",
    link: "/docs/Others/Review/index.md",
    items: [
      { text: "30 天阶段复盘", link: "/docs/Others/Review/Overview/index.md" },
      { text: "知识体系整理", link: "/docs/Others/Review/KnowledgeMap/index.md" },
      { text: "面试题集", link: "/docs/Others/Review/Interview/index.md" },
      { text: "效率工具安利", link: "/docs/Others/Review/EfficiencyTools/index.md" },
      { text: "学习方法与规划", link: "/docs/Others/Review/LearningMethod/index.md" },
      { text: "项目复盘模板", link: "/docs/Others/Review/ProjectRetro/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Others/Review/FAQ/index.md" },
    ],
  },
];

const OthersAnnualReview = [
  {
    text: "年度复盘",
    link: "/docs/Others/AnnualReview/index.md",
    items: [
      { text: "复盘方法论", link: "/docs/Others/AnnualReview/Overview/index.md" },
      { text: "文档库与资产盘点", link: "/docs/Others/AnnualReview/DocsAudit/index.md" },
      { text: "知识体系重构", link: "/docs/Others/AnnualReview/KnowledgeRefactor/index.md" },
      { text: "年度总结怎么写", link: "/docs/Others/AnnualReview/AnnualSummary/index.md" },
      { text: "下一年规划", link: "/docs/Others/AnnualReview/NextYearPlan/index.md" },
      { text: "个人成长复盘", link: "/docs/Others/AnnualReview/GrowthReview/index.md" },
      { text: "实战：走完一次年度复盘", link: "/docs/Others/AnnualReview/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Others/AnnualReview/FAQ/index.md" },
    ],
  },
];

const OthersProjectDelivery = [
  {
    text: "完整项目交付",
    link: "/docs/Others/ProjectDelivery/index.md",
    collapsed: true,
    items: [
      { text: "交付全景与验收标准", link: "/docs/Others/ProjectDelivery/Overview/index.md" },
      { text: "需求拆分与验收条件", link: "/docs/Others/ProjectDelivery/Requirements/index.md" },
      { text: "架构设计与技术选型", link: "/docs/Others/ProjectDelivery/Architecture/index.md" },
      { text: "接口契约先行", link: "/docs/Others/ProjectDelivery/Contract/index.md" },
      { text: "数据建模与迁移", link: "/docs/Others/ProjectDelivery/DataModel/index.md" },
      { text: "测试策略与门禁", link: "/docs/Others/ProjectDelivery/Testing/index.md" },
      { text: "一键部署与上线验收", link: "/docs/Others/ProjectDelivery/Delivery/index.md" },
      { text: "常见问题与排错", link: "/docs/Others/ProjectDelivery/FAQ/index.md" },
    ],
  },
];

export const sidebar = {

  // 与 nav.ts 的大类保持一致（key 不要带尾斜杠，避免与主题 key 同级匹配冲突）
  "/docs/Frontend": [
    {
      text: "前端",
      collapsed: true,
      items: [...FrontBasic, ...FrontFrame, ...FrontMicroFrontend, ...FrontDataVisualization, ...FrontLowCode, ...FrontWebAssembly, ...FrontWebGL, ...FrontPWA, ...FrontSSR, ...FrontIntlA11y, ...FrontTesting, ...FrontOthers],
    },
  ],
  "/docs/Backend": [
    {
      text: "后端",
      collapsed: true,
      items: [...DotNet, ...Go, ...GoMicroservices, ...Java, ...HighPerformanceJava, ...Auth, ...MessageQueue, ...Microservices, ...SpringCloud, ...DesignPatterns, ...NetworkProgramming, ...Python, ...PythonWeb, ...Ecommerce, ...Ledger, ...DDD, ...WorkflowEngine, ...DistributedCache, ...ReactiveProgramming],
    },
  ],
  "/docs/DB": [
    {
      text: "数据库",
      collapsed: true,
      items: [...DBOverview, ...Relational, ...Middleware, ...NoRelational, ...DataModeling, ...DataWarehouse, ...BigData, ...ClickHouse, ...Neo4j, ...TimeSeries, ...CDC],
    },
  ],
  "/docs/Ops": [
    {
      text: "运维",
      collapsed: true,
      items: [...VM, ...Linux, ...Ansible, ...Terraform, ...SecurityHardening, ...Nginx, ...Network, ...Docker, ...Kubernetes, ...ContainerOrchestration, ...CloudNative, ...CloudArchitecture, ...Monitoring, ...LogSystem, ...BackupDR, ...ChaosEngineering, ...IncidentResponse, ...JumpServer, ...OpsOthers],
    },
  ],
  "/docs/AI": [
    {
      text: "AI",
      collapsed: true,
      items: [...AI_LLMApp, ...AI_AICodingAssistant, ...AI_LangChain, ...AI_AgentFramework, ...AI_RAG, ...AI_Multimodal, ...AI_FineTuning, ...AI_LocalModel, ...AI_OpenClaw, ...AI_PromptEngineering, ...AI_PromptSecurity, ...AI_Agent, ...AI_LLMObservability],
    },
  ],
  "/docs/Tools": [
    {
      text: "工具",
      collapsed: true,
      items: [...Build, ...CICD, ...DatabaseClients, ...APIDesign, ...APITools, ...PackageManager, ...IDE, ...Efficiency, ...VC, ...Collaboration, ...TestingTools, ...DocsInfra, ...DependencyGovernance, ...Others],
    },
  ],
  "/project": [
    {
      text: "项目",
      collapsed: true,
      items: [...BaseProject, ...CompleteProject],
    },
  ],
  "/docs/Others": [
    {
      text: "其他",
      collapsed: true,
      items: [
        { text: "其他", link: "/docs/Others/index.md" },
        { text: "开源软件许可证", link: "/docs/Others/OpenSourceLicense/index.md" },
        ...OthersReview,
        ...OthersAnnualReview,
        ...OthersProjectDelivery,
      ],
    },
  ],
  "/docs/Others/Review": OthersReview,
  "/docs/Others/AnnualReview": OthersAnnualReview,
  "/docs/Others/ProjectDelivery": OthersProjectDelivery,

  // 主题级侧边栏：进入具体主题时才展示该主题的侧边栏（子内容默认折叠）
  "/docs/Frontend/Basic": FrontBasic,
  "/docs/Frontend/Frame": FrontFrame,
  "/docs/Frontend/MicroFrontend": FrontMicroFrontend,
  "/docs/Frontend/DataVisualization": FrontDataVisualization,
  "/docs/Frontend/LowCode": FrontLowCode,
  "/docs/Frontend/WebAssembly": FrontWebAssembly,
  "/docs/Frontend/WebGL": FrontWebGL,
  "/docs/Frontend/PWA": FrontPWA,
  "/docs/Frontend/SSR": FrontSSR,
  "/docs/Frontend/IntlA11y": FrontIntlA11y,
  "/docs/Frontend/Others": FrontOthers,
  "/docs/Frontend/Others/FrontendEngineering": FrontendEngineering,
  "/docs/Frontend/Testing": FrontTesting,
  "/docs/Backend/DotNet": DotNet,
  "/docs/Backend/Go": Go,
  "/docs/Backend/GoMicroservices": GoMicroservices,
  "/docs/Backend/Java": Java,
  "/docs/Backend/HighPerformanceJava": HighPerformanceJava,
  "/docs/Backend/MessageQueue": MessageQueue,
  "/docs/Backend/Auth": Auth,
  "/docs/Backend/Microservices": Microservices,
  "/docs/Backend/SpringCloud": SpringCloud,
  "/docs/Backend/DesignPatterns": DesignPatterns,
  "/docs/Backend/NetworkProgramming": NetworkProgramming,
  "/docs/Backend/Python": Python,
  "/docs/Backend/PythonWeb": PythonWeb,
  "/docs/Backend/Ecommerce": Ecommerce,
  "/docs/Backend/Ledger": Ledger,
  "/docs/Backend/DDD": DDD,
  "/docs/Backend/WorkflowEngine": WorkflowEngine,
  "/docs/Backend/DistributedCache": DistributedCache,
  "/docs/Backend/ReactiveProgramming": ReactiveProgramming,
  "/docs/DB/Overview": DBOverview,
  "/docs/DB/Relational": Relational,
  "/docs/DB/Relational/SQLOptimization": SQLOptimization,
  "/docs/DB/Relational/Sharding": Sharding,
  "/docs/DB/NoRelational": NoRelational,
  "/docs/DB/DataWarehouse": DataWarehouse,
  "/docs/DB/BigData": BigData,
  "/docs/DB/DataModeling": DataModeling,
  "/docs/DB/TimeSeries": TimeSeries,
  "/docs/DB/ClickHouse": ClickHouse,
  "/docs/DB/Neo4j": Neo4j,
  "/docs/DB/Middleware": Middleware,
  "/docs/DB/CDC": CDC,
  "/docs/Ops/VM": VM,
  "/docs/Ops/Linux": Linux,
  "/docs/Ops/Ansible": Ansible,
  "/docs/Ops/Terraform": Terraform,
  "/docs/Ops/SecurityHardening": SecurityHardening,
  "/docs/Ops/Nginx": Nginx,
  "/docs/Ops/Network": Network,
  "/docs/Ops/Docker": Docker,
  "/docs/Ops/Kubernetes": Kubernetes,
  "/docs/Ops/ContainerOrchestration": ContainerOrchestration,
  "/docs/Ops/CloudNative": CloudNative,
  "/docs/Ops/CloudArchitecture": CloudArchitecture,
  "/docs/Ops/Monitoring": Monitoring,
  "/docs/Ops/LogSystem": LogSystem,
  "/docs/Ops/BackupDR": BackupDR,
  "/docs/Ops/ChaosEngineering": ChaosEngineering,
  "/docs/Ops/IncidentResponse": IncidentResponse,
  "/docs/Ops/JumpServer": JumpServer,
  "/docs/Ops/Others": OpsOthers,
  "/docs/AI/OpenClaw": AI_OpenClaw,
  "/docs/AI/AICodingAssistant": AI_AICodingAssistant,
  "/docs/AI/PromptEngineering": AI_PromptEngineering,
  "/docs/AI/PromptSecurity": AI_PromptSecurity,
  "/docs/AI/Agent": AI_Agent,
  "/docs/AI/AgentFramework": AI_AgentFramework,
  "/docs/AI/LLMApp": AI_LLMApp,
  "/docs/AI/LLMObservability": AI_LLMObservability,
  "/docs/AI/LangChain": AI_LangChain,
  "/docs/AI/RAG": AI_RAG,
  "/docs/AI/Multimodal": AI_Multimodal,
  "/docs/AI/FineTuning": AI_FineTuning,
  "/docs/AI/LocalModel": AI_LocalModel,
  "/docs/Tools/Build": Build,
  "/docs/Tools/CICD": CICD,
  "/docs/Tools/DatabaseClients": DatabaseClients,
  "/docs/Tools/APITools": APITools,
  "/docs/Tools/APIDesign": APIDesign,
  "/docs/Tools/PackageManager": PackageManager,
  "/docs/Tools/DocsInfra": DocsInfra,
  "/docs/Tools/DependencyGovernance": DependencyGovernance,
  "/docs/Tools/Collaboration": Collaboration,
  "/docs/Tools/IDE": IDE,
  "/docs/Tools/Efficiency": Efficiency,
  "/docs/Tools/TestingTools": TestingTools,
  "/docs/Tools/VersionControl": VC,
  "/docs/Tools/Others": Others,
  "/project/Base": BaseProject,
  "/project/Complete": CompleteProject,
};
