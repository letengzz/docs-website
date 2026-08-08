// import { set_sidebar } from "../utils/auto-gen-sidebar.mjs";	// 改成自己的路径
import { DotNet, Go, Java, Python } from "./backend";

import { AI_Java, AI_OpenClaw } from "./AI";
import { FrontBasic, FrontFrame, FrontOthers } from "./frontend";
import { Docker, JumpServer, Kubernetes, Linux, Nginx, OpsOthers, VM } from "./ops";
import { DBOverview, NoRelational, Relational } from "./db";
import { Build, CICD, IDE, Others, VC } from "./tools";
import { BaseProject, CompleteProject } from "./project";


export const sidebar = {

  // 与 nav.ts 的大类保持一致（key 不要带尾斜杠，避免与主题 key 同级匹配冲突）
  "/docs/Frontend": [
    {
      text: "前端",
      items: [...FrontBasic, ...FrontFrame, ...FrontOthers],
    },
  ],
  "/docs/Backend": [
    {
      text: "后端",
      items: [...DotNet, ...Go, ...Java, ...Python],
    },
  ],
  "/docs/DB": [
    {
      text: "数据库",
      items: [...DBOverview, ...Relational, ...NoRelational],
    },
  ],
  "/docs/Ops": [
    {
      text: "运维",
      items: [...VM, ...Linux, ...Nginx, ...Docker, ...Kubernetes, ...JumpServer, ...OpsOthers],
    },
  ],
  "/docs/AI": [
    {
      text: "AI",
      items: [...AI_Java, ...AI_OpenClaw],
    },
  ],
  "/docs/Tools": [
    {
      text: "工具",
      items: [...Build, ...CICD, ...IDE, ...VC, ...Others],
    },
  ],
  "/project": [
    {
      text: "项目",
      items: [...BaseProject, ...CompleteProject],
    },
  ],
  "/docs/Others": [
    {
      text: "其他",
      items: [{ text: "其他", link: "/docs/Others/index.md" }],
    },
  ],

  // 主题级侧边栏：进入具体主题时才展示该主题的侧边栏（子内容默认折叠）
  "/docs/Frontend/Basic": FrontBasic,
  "/docs/Frontend/Frame": FrontFrame,
  "/docs/Frontend/Others": FrontOthers,
  "/docs/Backend/DotNet": DotNet,
  "/docs/Backend/Go": Go,
  "/docs/Backend/Java": Java,
  "/docs/Backend/Python": Python,
  "/docs/DB/Overview": DBOverview,
  "/docs/DB/Relational": Relational,
  "/docs/DB/NoRelational": NoRelational,
  "/docs/Ops/VM": VM,
  "/docs/Ops/Linux": Linux,
  "/docs/Ops/Nginx": Nginx,
  "/docs/Ops/Docker": Docker,
  "/docs/Ops/Kubernetes": Kubernetes,
  "/docs/Ops/JumpServer": JumpServer,
  "/docs/Ops/Others": OpsOthers,
  "/docs/AI/Java": AI_Java,
  "/docs/AI/OpenClaw": AI_OpenClaw,
  "/docs/Tools/Build": Build,
  "/docs/Tools/CICD": CICD,
  "/docs/Tools/IDE": IDE,
  "/docs/Tools/VersionControl": VC,
  "/docs/Tools/Others": Others,
  "/project/Base": BaseProject,
  "/project/Complete": CompleteProject,
};
