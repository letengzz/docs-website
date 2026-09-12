// 基础项目：工程模板与基础设施
export const BaseProject = [
  {
    text: "基础项目",
    link: "/project/Base/index.md",
    items: [
      {
        text: "Vue3 模板",
        link: "/project/Base/Vue3Template/index.md",
        collapsed: true,
        items: [
          { text: "初始化项目", link: "/project/Base/Vue3Template/InitProject/index.md" },
          { text: "配置环境变量", link: "/project/Base/Vue3Template/Env/index.md" },
          { text: "拆分配置", link: "/project/Base/Vue3Template/SplitConfig/index.md" },
          { text: "配置打包构建优化", link: "/project/Base/Vue3Template/Build/index.md" },
          { text: "封装 Pinia", link: "/project/Base/Vue3Template/Pinia/index.md" },
          { text: "配置自动路由", link: "/project/Base/Vue3Template/Router/index.md" },
          { text: "配置自动导入", link: "/project/Base/Vue3Template/AutoImport/index.md" },
          { text: "配置组件自动注册", link: "/project/Base/Vue3Template/AutoComponent/index.md" },
          { text: "配置 VueUse 工具集", link: "/project/Base/Vue3Template/VueUse/index.md" },
          { text: "配置 VueRequest", link: "/project/Base/Vue3Template/VueRequest/index.md" },
          { text: "配置国际化", link: "/project/Base/Vue3Template/i18n/index.md" },
          { text: "自定义配置网络请求", link: "/project/Base/Vue3Template/Http/index.md" },
          { text: "权限模块", link: "/project/Base/Vue3Template/Permission/index.md" },
          { text: "主题模块", link: "/project/Base/Vue3Template/Theme/index.md" },
          { text: "组件库集成", link: "/project/Base/Vue3Template/ComponentLibrary/index.md" },
          { text: "配置 CSS 代码检查工具", link: "/project/Base/Vue3Template/‌Stylelint/index.md" },
          { text: "配置 SCSS", link: "/project/Base/Vue3Template/SCSS/index.md" },
          { text: "配置 UnoCSS", link: "/project/Base/Vue3Template/UnoCSS/index.md" },
          { text: "发布模块", link: "/project/Base/Vue3Template/Release/index.md" },
          { text: "常见问题与最佳实践", link: "/project/Base/Vue3Template/FAQ/index.md" },
        ],
      },
    ],
  },
];

// 完整项目：端到端交付实战
export const CompleteProject = [
  {
    text: "完整项目",
    link: "/project/Complete/index.md",
    items: [
      { text: "完整项目总览", link: "/project/Complete/index.md" },
      {
        text: "全栈项目实战",
        link: "/project/Complete/FullStackProject/index.md",
        collapsed: true,
        items: [
          { text: "需求拆分", link: "/project/Complete/FullStackProject/Requirements/index.md" },
          { text: "数据库设计", link: "/project/Complete/FullStackProject/Database/index.md" },
          { text: "接口联调", link: "/project/Complete/FullStackProject/Api/index.md" },
          { text: "编码实现", link: "/project/Complete/FullStackProject/Development/index.md" },
          { text: "测试", link: "/project/Complete/FullStackProject/Testing/index.md" },
          { text: "部署", link: "/project/Complete/FullStackProject/Deployment/index.md" },
          { text: "复盘", link: "/project/Complete/FullStackProject/Retrospective/index.md" },
        ],
      },
    ],
  },
];
