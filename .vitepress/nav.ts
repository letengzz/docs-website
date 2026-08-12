export const nav = [
  { text: "首页", link: "/" },
  {
    text: "前端", items: [
      { text: "基础", link: "/docs/Frontend/Basic" },
      { text: "框架", link: "/docs/Frontend/Frame" },
      { text: "其他", link: "/docs/Frontend/Others" }
    ]
  },
  {
    text: "后端", items: [
      { text: ".Net", link: "/docs/Backend/DotNet" },
      { text: "Go", link: "/docs/Backend/Go" },
      { text: "Java", link: "/docs/Backend/Java" },
      { text: "Python", link: "/docs/Backend/Python" },]
  },
  {
    text: "数据库",
    items: [
      { text: "概述", link: "/docs/DB/Overview" },
      { text: "关系型数据库", link: "/docs/DB/Relational" },
      { text: "MySQL", link: "/docs/DB/Relational/MySQL" },
      { text: "非关系型数据库", link: "/docs/DB/NoRelational" },
      { text: "Redis", link: "/docs/DB/NoRelational/Redis" },
    ]
  },
  {
    text: "运维", items: [
      { text: "虚拟机", link: "/docs/Ops/VM" },
      { text: "Linux", link: "/docs/Ops/Linux" },
      { text: "Nginx", link: "/docs/Ops/Nginx" },
      { text: "Docker", link: "/docs/Ops/Docker" },
      { text: "Kubernetes", link: "/docs/Ops/Kubernetes" },
      { text: "JumpServer", link: "/docs/Ops/JumpServer" },
      { text: "其他", link: "/docs/Ops/Others" },
    ]
  },
  { text: "AI", items: [
    { text: "OpenClaw", link: "/docs/AI/OpenClaw" },
  ] },
  {
    text: "工具", items: [
      { text: "构建和依赖管理工具", link: "/docs/Tools/Build" },
      { text: "持续集成工具", link: "/docs/Tools/CICD" },
      { text: "IDE工具", link: "/docs/Tools/IDE" },
      { text: "版本控制工具", link: "/docs/Tools/VersionControl" },
      { text: "其他", link: "/docs/Tools/Others" }
    ]
  },
  {
    text: "项目", items: [
      { text: "基础项目", link: "/project/Base" },
      { text: "完整项目", link: "/project/Complete" },
    ]
  },
  { text: "其他", link: "/docs/Others" },
];
