export const Build = [{ text: "构建和依赖管理工具", link: "/docs/Tools/Build/index.md" }];
export const CICD = [{ text: "持续集成工具", link: "/docs/Tools/CICD/index.md" }];
export const IDE = [{ text: "IDE 工具", link: "/docs/Tools/IDE/index.md" }];
export const Others = [{ text: "其他工具", link: "/docs/Tools/Others/index.md" }];
export const VC = [
  {
    text: "版本控制工具",
    link: "/docs/Tools/VersionControl/index.md",
    collapsed: true,
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
