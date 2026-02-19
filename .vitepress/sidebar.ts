// import { set_sidebar } from "../utils/auto-gen-sidebar.mjs";	// 改成自己的路径
import { DotNet, Go, Java, Python } from "./backend";

import { AI_Java } from "./AI";
import { FrontBasic, FrontFrame, FrontOthers } from "./frontend";
import { Docker, JumpServer, Kubernetes, Linux, Nginx, OpsOthers, VM } from "./ops";
import { NoRelational, Relational } from "./db";
import { Build, CICD, IDE, Others, VC } from "./tools";
import { BaseProject, CompleteProject } from "./project";


export const sidebar = {

  //前端
  "/docs/Frontend/Basic": FrontBasic,
  "/docs/Frontend/Frame": FrontFrame,
  "/docs/Frontend/Others": FrontOthers,

//   //后端
  "/docs/Backend/Go": Go,
  "/docs/Backend/DotNet": DotNet,
  "/docs/Backend/Java": Java,
  "/docs/Backend/Python": Python,

  //运维
  "/docs/Ops/VM": VM,
  "/docs/Ops/Linux": Linux,
  "/docs/Ops/Nginx": Nginx,
  "/docs/Ops/Docker": Docker,
  "/docs/Ops/Kubernetes": Kubernetes,
  "/docs/Ops/JumpServer": JumpServer,
  "/docs/Ops/Others": OpsOthers,

  // AI
  "/docs/AI/Java": AI_Java,

  //NoRelational
  "/docs/DB/NoRelational": NoRelational,
  //Relational
  "/docs/DB/Relational": Relational,

  // Tools
  "/docs/Tools/Build": Build,
  // CICD
  "/docs/Tools/CICD": CICD,
  // IDE
  "/docs/Tools/IDE": IDE,
  // VC
  "/docs/Tools/VersionControl": VC,
  // Others
  "/docs/Tools/Others": Others,

//   //其他
//   "/docs/Others": set_sidebar("/docs/Others"),

  //Base Project
  "/project/Base": BaseProject,
  "/project/Complete": CompleteProject,
};
