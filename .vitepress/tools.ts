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
export const IDE = [{ text: "IDE 工具", link: "/docs/Tools/IDE/index.md" }];
export const Others = [{ text: "其他工具", link: "/docs/Tools/Others/index.md" }];
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
