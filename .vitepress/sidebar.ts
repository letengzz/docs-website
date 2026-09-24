// import { set_sidebar } from "../utils/auto-gen-sidebar.mjs";	// 改成自己的路径
import { Auth, DesignPatterns, DotNet, Ecommerce, Go, Java, MessageQueue, Microservices, NetworkProgramming, Python, SpringCloud } from "./backend";

import { AI_Agent, AI_FineTuning, AI_LangChain, AI_LLMApp, AI_LocalModel, AI_Multimodal, AI_OpenClaw, AI_PromptEngineering, AI_RAG } from "./AI";
import { FrontBasic, FrontendEngineering, FrontFrame, FrontOthers, FrontTesting } from "./frontend";
import { Ansible, ContainerOrchestration, Docker, JumpServer, Kubernetes, Linux, LogSystem, Monitoring, Network, Nginx, OpsOthers, SecurityHardening, Terraform, VM } from "./ops";
import { DBOverview, DataModeling, NoRelational, Relational, SQLOptimization, TimeSeries } from "./db";
import { APITools, Build, CICD, Collaboration, DatabaseClients, Efficiency, IDE, Others, PackageManager, VC } from "./tools";
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
      items: [...FrontBasic, ...FrontFrame, ...FrontTesting, ...FrontOthers],
    },
  ],
  "/docs/Backend": [
    {
      text: "后端",
      collapsed: true,
      items: [...DotNet, ...Go, ...Java, ...Auth, ...MessageQueue, ...Microservices, ...SpringCloud, ...DesignPatterns, ...NetworkProgramming, ...Python, ...Ecommerce],
    },
  ],
  "/docs/DB": [
    {
      text: "数据库",
      collapsed: true,
      items: [...DBOverview, ...Relational, ...NoRelational, ...DataModeling, ...TimeSeries],
    },
  ],
  "/docs/Ops": [
    {
      text: "运维",
      collapsed: true,
      items: [...VM, ...Linux, ...Ansible, ...Terraform, ...SecurityHardening, ...Nginx, ...Network, ...Docker, ...Kubernetes, ...ContainerOrchestration, ...Monitoring, ...LogSystem, ...JumpServer, ...OpsOthers],
    },
  ],
  "/docs/AI": [
    {
      text: "AI",
      collapsed: true,
      items: [...AI_LLMApp, ...AI_LangChain, ...AI_RAG, ...AI_Multimodal, ...AI_FineTuning, ...AI_LocalModel, ...AI_OpenClaw, ...AI_PromptEngineering, ...AI_Agent],
    },
  ],
  "/docs/Tools": [
    {
      text: "工具",
      collapsed: true,
      items: [...Build, ...CICD, ...DatabaseClients, ...APITools, ...PackageManager, ...IDE, ...Efficiency, ...VC, ...Collaboration, ...Others],
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
  "/docs/Frontend/Others": FrontOthers,
  "/docs/Frontend/Others/FrontendEngineering": FrontendEngineering,
  "/docs/Frontend/Testing": FrontTesting,
  "/docs/Backend/DotNet": DotNet,
  "/docs/Backend/Go": Go,
  "/docs/Backend/Java": Java,
  "/docs/Backend/MessageQueue": MessageQueue,
  "/docs/Backend/Auth": Auth,
  "/docs/Backend/Microservices": Microservices,
  "/docs/Backend/SpringCloud": SpringCloud,
  "/docs/Backend/DesignPatterns": DesignPatterns,
  "/docs/Backend/NetworkProgramming": NetworkProgramming,
  "/docs/Backend/Python": Python,
  "/docs/Backend/Ecommerce": Ecommerce,
  "/docs/DB/Overview": DBOverview,
  "/docs/DB/Relational": Relational,
  "/docs/DB/Relational/SQLOptimization": SQLOptimization,
  "/docs/DB/NoRelational": NoRelational,
  "/docs/DB/DataModeling": DataModeling,
  "/docs/DB/TimeSeries": TimeSeries,
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
  "/docs/Ops/Monitoring": Monitoring,
  "/docs/Ops/LogSystem": LogSystem,
  "/docs/Ops/JumpServer": JumpServer,
  "/docs/Ops/Others": OpsOthers,
  "/docs/AI/OpenClaw": AI_OpenClaw,
  "/docs/AI/PromptEngineering": AI_PromptEngineering,
  "/docs/AI/Agent": AI_Agent,
  "/docs/AI/LLMApp": AI_LLMApp,
  "/docs/AI/LangChain": AI_LangChain,
  "/docs/AI/RAG": AI_RAG,
  "/docs/AI/Multimodal": AI_Multimodal,
  "/docs/AI/FineTuning": AI_FineTuning,
  "/docs/AI/LocalModel": AI_LocalModel,
  "/docs/Tools/Build": Build,
  "/docs/Tools/CICD": CICD,
  "/docs/Tools/DatabaseClients": DatabaseClients,
  "/docs/Tools/APITools": APITools,
  "/docs/Tools/PackageManager": PackageManager,
  "/docs/Tools/Collaboration": Collaboration,
  "/docs/Tools/IDE": IDE,
  "/docs/Tools/Efficiency": Efficiency,
  "/docs/Tools/VersionControl": VC,
  "/docs/Tools/Others": Others,
  "/project/Base": BaseProject,
  "/project/Complete": CompleteProject,
};
