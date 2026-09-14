// import { set_sidebar } from "../utils/auto-gen-sidebar.mjs";	// 改成自己的路径
import { Auth, DesignPatterns, DotNet, Go, Java, MessageQueue, Microservices, NetworkProgramming, Python, SpringCloud } from "./backend";

import { AI_Agent, AI_LLMApp, AI_LocalModel, AI_OpenClaw, AI_PromptEngineering, AI_RAG } from "./AI";
import { FrontBasic, FrontendEngineering, FrontFrame, FrontOthers, FrontTesting } from "./frontend";
import { ContainerOrchestration, Docker, JumpServer, Kubernetes, Linux, LogSystem, Monitoring, Network, Nginx, OpsOthers, VM } from "./ops";
import { DBOverview, DataModeling, NoRelational, Relational, SQLOptimization, TimeSeries } from "./db";
import { APITools, Build, CICD, Collaboration, DatabaseClients, IDE, Others, PackageManager, VC } from "./tools";
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
      items: [...DotNet, ...Go, ...Java, ...Auth, ...MessageQueue, ...Microservices, ...SpringCloud, ...DesignPatterns, ...NetworkProgramming, ...Python],
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
      items: [...VM, ...Linux, ...Nginx, ...Network, ...Docker, ...Kubernetes, ...ContainerOrchestration, ...Monitoring, ...LogSystem, ...JumpServer, ...OpsOthers],
    },
  ],
  "/docs/AI": [
    {
      text: "AI",
      collapsed: true,
      items: [...AI_LLMApp, ...AI_RAG, ...AI_LocalModel, ...AI_OpenClaw, ...AI_PromptEngineering, ...AI_Agent],
    },
  ],
  "/docs/Tools": [
    {
      text: "工具",
      collapsed: true,
      items: [...Build, ...CICD, ...DatabaseClients, ...APITools, ...PackageManager, ...IDE, ...VC, ...Collaboration, ...Others],
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
      ],
    },
  ],
  "/docs/Others/Review": OthersReview,
  "/docs/Others/AnnualReview": OthersAnnualReview,

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
  "/docs/DB/Overview": DBOverview,
  "/docs/DB/Relational": Relational,
  "/docs/DB/Relational/SQLOptimization": SQLOptimization,
  "/docs/DB/NoRelational": NoRelational,
  "/docs/DB/DataModeling": DataModeling,
  "/docs/DB/TimeSeries": TimeSeries,
  "/docs/Ops/VM": VM,
  "/docs/Ops/Linux": Linux,
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
  "/docs/AI/RAG": AI_RAG,
  "/docs/AI/LocalModel": AI_LocalModel,
  "/docs/Tools/Build": Build,
  "/docs/Tools/CICD": CICD,
  "/docs/Tools/DatabaseClients": DatabaseClients,
  "/docs/Tools/APITools": APITools,
  "/docs/Tools/PackageManager": PackageManager,
  "/docs/Tools/Collaboration": Collaboration,
  "/docs/Tools/IDE": IDE,
  "/docs/Tools/VersionControl": VC,
  "/docs/Tools/Others": Others,
  "/project/Base": BaseProject,
  "/project/Complete": CompleteProject,
};
