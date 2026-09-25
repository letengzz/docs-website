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
          { text: "配置 CSS 代码检查工具", link: "/project/Base/Vue3Template/Stylelint/index.md" },
          { text: "配置 SCSS", link: "/project/Base/Vue3Template/SCSS/index.md" },
          { text: "配置 UnoCSS", link: "/project/Base/Vue3Template/UnoCSS/index.md" },
          { text: "发布模块", link: "/project/Base/Vue3Template/Release/index.md" },
          { text: "常见问题与最佳实践", link: "/project/Base/Vue3Template/FAQ/index.md" },
        ],
      },
      {
        text: "后端通用模板",
        link: "/project/Base/BackendTemplate/index.md",
        collapsed: true,
        items: [
          { text: "需求与架构设计", link: "/project/Base/BackendTemplate/Architecture/index.md" },
          { text: "骨架与目录结构", link: "/project/Base/BackendTemplate/Skeleton/index.md" },
          { text: "统一响应与全局异常", link: "/project/Base/BackendTemplate/CommonResponse/index.md" },
          { text: "健康检查与配置", link: "/project/Base/BackendTemplate/HealthCheck/index.md" },
          { text: "请求追踪 ID 与日志切面", link: "/project/Base/BackendTemplate/TraceId/index.md" },
          { text: "参数校验增强", link: "/project/Base/BackendTemplate/Validation/index.md" },
          { text: "MockMvc 集成测试", link: "/project/Base/BackendTemplate/IntegrationTest/index.md" },
          { text: "数据访问：MyBatis-Plus 接入", link: "/project/Base/BackendTemplate/DataAccess/index.md" },
          { text: "认证授权：Spring Security 7 + JWT", link: "/project/Base/BackendTemplate/Security/index.md" },
          { text: "登录业务闭环与令牌生命周期", link: "/project/Base/BackendTemplate/AuthLifecycle/index.md" },
          { text: "压测与性能基线", link: "/project/Base/BackendTemplate/PerformanceTest/index.md" },
          { text: "测试数据隔离与边界用例", link: "/project/Base/BackendTemplate/TestIsolation/index.md" },
          { text: "技术栈可插拔：模块边界与选择器脚本", link: "/project/Base/BackendTemplate/StackSelect/index.md" },
          { text: "模板 CLI：设计与路线图", link: "/project/Base/BackendTemplate/TemplateCli/index.md" },
          { text: "异常路径联调收口与用例清单", link: "/project/Base/BackendTemplate/ErrorPath/index.md" },
          { text: "容器化：多阶段镜像与 Compose 编排", link: "/project/Base/BackendTemplate/Deployment/index.md" },
          { text: "CI 流水线：把门禁串成一条链", link: "/project/Base/BackendTemplate/CI/index.md" },
          { text: "镜像推送与发布策略", link: "/project/Base/BackendTemplate/Release/index.md" },
          { text: "主库可插拔：MySQL / PostgreSQL 双方言", link: "/project/Base/BackendTemplate/Database/index.md" },
          { text: "上线验收与监控接入", link: "/project/Base/BackendTemplate/Acceptance/index.md" },
          { text: "进展记录", link: "/project/Base/BackendTemplate/Progress/index.md" },
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
