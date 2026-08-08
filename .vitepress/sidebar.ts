// import { set_sidebar } from "../utils/auto-gen-sidebar.mjs";	// 改成自己的路径
import { DotNet, Go, Java, Python } from "./backend";

import { AI_Java, AI_OpenClaw } from "./AI";
import { FrontBasic, FrontFrame, FrontOthers } from "./frontend";
import { Docker, JumpServer, Kubernetes, Linux, Nginx, OpsOthers, VM } from "./ops";
import { DBOverview, NoRelational, Relational } from "./db";
import { Build, CICD, IDE, Others, VC } from "./tools";
import { BaseProject, CompleteProject } from "./project";


export const sidebar = {

  // 与 nav.ts 的大类保持一致
  "/docs/Frontend/": [
    {
      text: "前端",
      items: [...FrontBasic, ...FrontFrame, ...FrontOthers],
    },
  ],
  "/docs/Backend/": [
    {
      text: "后端",
      items: [...DotNet, ...Go, ...Java, ...Python],
    },
  ],
  "/docs/DB/": [
    {
      text: "数据库",
      items: [...DBOverview, ...Relational, ...NoRelational],
    },
  ],
  "/docs/Ops/": [
    {
      text: "运维",
      items: [...VM, ...Linux, ...Nginx, ...Docker, ...Kubernetes, ...JumpServer, ...OpsOthers],
    },
  ],
  "/docs/AI/": [
    {
      text: "AI",
      items: [...AI_Java, ...AI_OpenClaw],
    },
  ],
  "/docs/Tools/": [
    {
      text: "工具",
      items: [...Build, ...CICD, ...IDE, ...VC, ...Others],
    },
  ],
  "/project/": [
    {
      text: "项目",
      items: [...BaseProject, ...CompleteProject],
    },
  ],
  "/docs/Others/": [
    {
      text: "其他",
      items: [{ text: "其他", link: "/docs/Others/index.md" }],
    },
  ],
};
