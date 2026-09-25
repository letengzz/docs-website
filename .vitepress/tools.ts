export const Build = [
  {
    text: "构建和依赖管理工具",
    link: "/docs/Tools/Build/index.md",
    items: [
      {
        text: "Maven",
        link: "/docs/Tools/Build/Maven/index.md",
        collapsed: true,
        items: [
          { text: "Maven 概述与安装", link: "/docs/Tools/Build/Maven/Overview/index.md" },
          { text: "项目结构与 POM 详解", link: "/docs/Tools/Build/Maven/Pom/index.md" },
          { text: "构建生命周期与插件", link: "/docs/Tools/Build/Maven/Lifecycle/index.md" },
          { text: "依赖管理与仓库", link: "/docs/Tools/Build/Maven/Dependency/index.md" },
          { text: "多模块工程", link: "/docs/Tools/Build/Maven/MultiModule/index.md" },
          { text: "常见问题与最佳实践", link: "/docs/Tools/Build/Maven/FAQ/index.md" },
        ],
      },
      {
        text: "Gradle",
        link: "/docs/Tools/Build/Gradle/index.md",
        collapsed: true,
        items: [
          { text: "Gradle 概述与安装", link: "/docs/Tools/Build/Gradle/Overview/index.md" },
          { text: "构建脚本与 Kotlin DSL", link: "/docs/Tools/Build/Gradle/BuildScript/index.md" },
          { text: "生命周期与任务", link: "/docs/Tools/Build/Gradle/Lifecycle/index.md" },
          { text: "依赖管理与版本目录", link: "/docs/Tools/Build/Gradle/Dependency/index.md" },
          { text: "多项目工程与 Wrapper", link: "/docs/Tools/Build/Gradle/MultiModule/index.md" },
          { text: "常见问题与最佳实践", link: "/docs/Tools/Build/Gradle/FAQ/index.md" },
        ],
      },
      { text: "Maven 与 Gradle 对比", link: "/docs/Tools/Build/MavenVsGradle/index.md" },
    ],
  },
];
export const CICD = [
  {
    text: "CI/CD",
    link: "/docs/Tools/CICD/index.md",
    items: [
      { text: "概念与流水线设计", link: "/docs/Tools/CICD/Overview/index.md" },
      { text: "GitHub Actions 入门", link: "/docs/Tools/CICD/GithubActions/index.md" },
      { text: "GitLab CI/CD", link: "/docs/Tools/CICD/GitlabCI/index.md" },
      { text: "Jenkins 流水线", link: "/docs/Tools/CICD/Jenkins/index.md" },
      { text: "流水线设计最佳实践", link: "/docs/Tools/CICD/PipelineDesign/index.md" },
      { text: "自动化测试与质量门禁", link: "/docs/Tools/CICD/Testing/index.md" },
      { text: "制品管理", link: "/docs/Tools/CICD/Artifacts/index.md" },
      { text: "自动部署与回滚", link: "/docs/Tools/CICD/DeployRollback/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Tools/CICD/FAQ/index.md" },
    ],
  },
];
export const PackageManager = [
  {
    text: "包管理器深入",
    link: "/docs/Tools/PackageManager/index.md",
    items: [
      { text: "生态与选型", link: "/docs/Tools/PackageManager/Overview/index.md" },
      { text: "lockfile 与依赖解析", link: "/docs/Tools/PackageManager/Lockfile/index.md" },
      { text: "pnpm 原理：存储、链接与安全", link: "/docs/Tools/PackageManager/Pnpm/index.md" },
      { text: "monorepo 与 workspaces", link: "/docs/Tools/PackageManager/Monorepo/index.md" },
      { text: "包发布流程与版本管理", link: "/docs/Tools/PackageManager/Publish/index.md" },
      { text: "依赖安全与供应链防护", link: "/docs/Tools/PackageManager/Security/index.md" },
      { text: "实战：迁移 pnpm 与 monorepo 落地", link: "/docs/Tools/PackageManager/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Tools/PackageManager/FAQ/index.md" },
    ],
  },
];
export const APITools = [
  {
    text: "接口调试工具",
    link: "/docs/Tools/APITools/index.md",
    items: [
      { text: "概述与选型", link: "/docs/Tools/APITools/Overview/index.md" },
      { text: "Postman：请求调试与协作", link: "/docs/Tools/APITools/Postman/index.md" },
      { text: "Apifox：接口设计到测试一体化", link: "/docs/Tools/APITools/Apifox/index.md" },
      { text: "环境变量与脚本", link: "/docs/Tools/APITools/Environment/index.md" },
      { text: "Mock 数据与模拟服务", link: "/docs/Tools/APITools/Mock/index.md" },
      { text: "自动化测试与 CI 集成", link: "/docs/Tools/APITools/Automation/index.md" },
      { text: "实战：接口调试全流程", link: "/docs/Tools/APITools/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Tools/APITools/FAQ/index.md" },
    ],
  },
];
export const DatabaseClients = [
  {
    text: "数据库客户端",
    link: "/docs/Tools/DatabaseClients/index.md",
    items: [
      { text: "概述与选型", link: "/docs/Tools/DatabaseClients/Overview/index.md" },
      { text: "Navicat：多库统一管理", link: "/docs/Tools/DatabaseClients/Navicat/index.md" },
      { text: "DBeaver：开源通用查询", link: "/docs/Tools/DatabaseClients/DBeaver/index.md" },
      { text: "RedisInsight：Redis 官方可视化", link: "/docs/Tools/DatabaseClients/RedisInsight/index.md" },
      { text: "连接管理与问题排查", link: "/docs/Tools/DatabaseClients/Connection/index.md" },
      { text: "常用操作：查询、导入导出与备份", link: "/docs/Tools/DatabaseClients/DataOps/index.md" },
      { text: "实战：多环境多库统一管理", link: "/docs/Tools/DatabaseClients/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Tools/DatabaseClients/FAQ/index.md" },
    ],
  },
];
export const Collaboration = [
  {
    text: "协作与项目管理",
    link: "/docs/Tools/Collaboration/index.md",
    items: [
      { text: "概述与工具选型", link: "/docs/Tools/Collaboration/Overview/index.md" },
      { text: "Jira 实战", link: "/docs/Tools/Collaboration/Jira/index.md" },
      { text: "Confluence 知识库", link: "/docs/Tools/Collaboration/Confluence/index.md" },
      { text: "飞书协作", link: "/docs/Tools/Collaboration/Feishu/index.md" },
      { text: "研发流程", link: "/docs/Tools/Collaboration/RdProcess/index.md" },
      { text: "文档协作规范", link: "/docs/Tools/Collaboration/DocCollaboration/index.md" },
      { text: "实战：10 人团队协作体系落地", link: "/docs/Tools/Collaboration/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Tools/Collaboration/FAQ/index.md" },
    ],
  },
];
export const IDE = [
  {
    text: "IDE 配置",
    link: "/docs/Tools/IDE/index.md",
    items: [
      { text: "概述与选型", link: "/docs/Tools/IDE/Overview/index.md" },
      { text: "IntelliJ IDEA 深入", link: "/docs/Tools/IDE/IntelliJIDEA/index.md" },
      { text: "VS Code 深入", link: "/docs/Tools/IDE/VSCode/index.md" },
      { text: "插件与扩展", link: "/docs/Tools/IDE/Plugins/index.md" },
      { text: "快捷键与高效操作", link: "/docs/Tools/IDE/Shortcuts/index.md" },
      { text: "配置同步与团队统一", link: "/docs/Tools/IDE/ConfigSync/index.md" },
      { text: "远程开发与容器化环境", link: "/docs/Tools/IDE/RemoteDev/index.md" },
      { text: "实战：搭一套统一的 IDE 环境", link: "/docs/Tools/IDE/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Tools/IDE/FAQ/index.md" },
    ],
  },
];
export const Efficiency = [
  {
    text: "效率工具",
    link: "/docs/Tools/Efficiency/index.md",
    items: [
      { text: "概述与选型", link: "/docs/Tools/Efficiency/Overview/index.md" },
      { text: "终端与 Shell 环境", link: "/docs/Tools/Efficiency/Terminal/index.md" },
      { text: "命令行提效", link: "/docs/Tools/Efficiency/ShellProductivity/index.md" },
      { text: "剪贴板与输入效率", link: "/docs/Tools/Efficiency/Clipboard/index.md" },
      { text: "截图与标注", link: "/docs/Tools/Efficiency/Screenshot/index.md" },
      { text: "笔记与知识管理", link: "/docs/Tools/Efficiency/Notes/index.md" },
      { text: "桌面与任务自动化", link: "/docs/Tools/Efficiency/Automation/index.md" },
      { text: "实战：搭一套个人效率工具链", link: "/docs/Tools/Efficiency/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Tools/Efficiency/FAQ/index.md" },
    ],
  },
];
export const Others = [{ text: "其他工具", link: "/docs/Tools/Others/index.md" }];
export const TestingTools = [
  {
    text: "测试工具",
    link: "/docs/Tools/TestingTools/index.md",
    items: [
      { text: "概述与选型", link: "/docs/Tools/TestingTools/Overview/index.md" },
      { text: "JMeter 性能测试", link: "/docs/Tools/TestingTools/JMeter/index.md" },
      { text: "Selenium 与 UI 自动化", link: "/docs/Tools/TestingTools/Selenium/index.md" },
      { text: "接口自动化", link: "/docs/Tools/TestingTools/APIAutomation/index.md" },
      { text: "实战：回归与压测流水线", link: "/docs/Tools/TestingTools/Practice/index.md" },
      { text: "常见问题与排错", link: "/docs/Tools/TestingTools/FAQ/index.md" },
    ],
  },
];
export const VC = [
  {
    text: "版本控制工具",
    link: "/docs/Tools/VersionControl/index.md",
    items: [
      {
        text: "Git 进阶",
        link: "/docs/Tools/VersionControl/Git/index.md",
        collapsed: true,
        items: [
          { text: "Git 进阶概述", link: "/docs/Tools/VersionControl/Git/Overview/index.md" },
          { text: "分支模型", link: "/docs/Tools/VersionControl/Git/BranchModel/index.md" },
          { text: "Rebase 与 Merge", link: "/docs/Tools/VersionControl/Git/RebaseMerge/index.md" },
          { text: "Stash 暂存", link: "/docs/Tools/VersionControl/Git/Stash/index.md" },
          { text: "Reset 与 Revert", link: "/docs/Tools/VersionControl/Git/ResetRevert/index.md" },
          { text: "Cherry-Pick", link: "/docs/Tools/VersionControl/Git/CherryPick/index.md" },
          { text: "子模块", link: "/docs/Tools/VersionControl/Git/Submodule/index.md" },
          { text: "协作工作流", link: "/docs/Tools/VersionControl/Git/Workflow/index.md" },
          { text: "常见问题与最佳实践", link: "/docs/Tools/VersionControl/Git/FAQ/index.md" },
        ],
      },
    ],
  },
];
