# docs-website 文档库编写与维护规则

本文档是仓库的「约定总纲」，供人工与 AI 协作维护时共同遵守。新增或修改任何文档前，先通读本文档，并打开范本目录 `docs/Frontend/Basic/HTML`（以及目标分类下的现有文档）对照风格。

## 1. 仓库结构与职责

```text
docs-website/
├─ index.md                  # 首页（layout: home）
├─ .vitepress/
│  ├─ config.mts             # VitePress 全局配置（标题、搜索、容器文案、outline 等）
│  ├─ nav.ts                 # 顶部导航
│  ├─ sidebar.ts             # 侧边栏汇总（路径前缀 → 分支配置）
│  ├─ frontend.ts            # 前端侧边栏分支
│  ├─ backend.ts             # 后端侧边栏分支
│  ├─ db.ts                  # 数据库侧边栏分支
│  ├─ ops.ts                 # 运维侧边栏分支
│  ├─ AI.ts                  # AI 侧边栏分支
│  ├─ tools.ts               # 工具侧边栏分支
│  └─ project.ts             # 项目侧边栏分支
├─ docs/                     # 技术文档：AI / Backend / DB / Frontend / Ops / Others（Tools 已预留）
├─ project/                  # 项目文档：Base（现有）、Complete（预留）
├─ public/                   # 全局静态资源（logo、背景图），不放文档图片
└─ utils/                    # 侧边栏自动生成脚本（备用，当前以手动维护为准）
```

要点：

- `docs/` 只放技术文档，分类与顶部导航保持一致。
- `project/` 只放项目实战文档，与 `docs/` 区分。
- 已规划但未建设的内容保留占位（如 `docs/Tools/`、`project/Complete/`、侧边栏中的空数组），不要删除。
- 所有源码文件统一 UTF-8 编码（`.editorconfig` 已配置），避免出现中文乱码。

## 2. 常用命令

| 命令 | 作用 |
| --- | --- |
| `pnpm install` | 安装依赖 |
| `pnpm docs:dev` | 本地启动开发预览 |
| `pnpm docs:build` | 生产构建，写完文档后必须跑一次验证 |
| `pnpm docs:preview` | 预览构建产物 |
| `pnpm lint` / `pnpm lint:fix` | 检查/修复 `.vitepress` 下 TypeScript 配置代码（Markdown 不在检查范围内） |

## 3. 目录与命名规范

### 顶级分类

- `docs/` 下使用与导航一致的大类目录：`Frontend`、`Backend`、`DB`、`Ops`、`AI`、`Tools`、`Others`。
- `project/` 下使用 `Base`（基础项目）与 `Complete`（完整项目）。
- 分类目录名一律 PascalCase。

### 主题目录

- 一个主题一个目录，目录内必须有 `index.md` 作为入口/目录页。
- 主题目录命名优先使用技术官方写法（如 `jQuery`、`NodeJs`、`AJAX`、`ECMAScript`、`UnoCSS`、`SCSS`、`pnpm`），其余使用 PascalCase（如 `Overview`、`Basic`、`InstallUninstall`）。
- 每个「页面」也是一个英文目录，目录内 `index.md` 就是页面正文，例如 `OOP/index.md`、`BasicSyntax/index.md`。
- 不要平铺创建 `OOP.md` 这类单文件页面；新增内容统一使用「英文目录 + index.md」结构。
- 存量平铺文件在整理时逐步迁移为「英文目录 + index.md」，并同步更新目录页链接与侧边栏，避免残留失效引用。
- 页面较少时，主题目录下直接放页面子目录；页面增多后按层级继续扩展。

### 文章文件

- 页面文件统一命名为 `index.md`，放在英文目录内；目录名使用 PascalCase 或技术官方写法（如 `Overview`、`OOP`、`BasicSyntax`，官方小写如 `fs`、`npm` 保留小写）。
- 不要使用中文目录名、空格或特殊字符（图片资源不受此限制）。

### 大版本管理

当主题出现**大版本（Major）**差异时，旧版本文档**不删除、不覆盖**，按「官方名 + 大版本号」建目录存留，例如：

- `Spring5/index.md` 与 `Spring6/index.md`
- `Vue2/index.md` 与 `Vue3/index.md`
- `Node16/index.md` 与 `Node18/index.md`（需要区分大版本时）

规则：

1. 新内容一律面向**当前最新稳定大版本**，并说明适用版本。
2. 旧版本目录保留原内容，并在页面顶部标注版本与维护状态（如「维护中」「已停止维护」「仅存量项目使用」）。
3. 小版本、补丁版本（如 Spring 6.1.x）不需要单独建目录，在页内用 `:::info` 说明适用版本即可。
4. 主题目录页（如 `Spring/index.md`）同时列出各版本入口，并提供「版本差异 / 升级指南」说明。
5. 侧边栏中旧版本可以折叠（`collapsed: true`），但必须保留入口，方便存量项目查阅。
6. 生成新大版本文档时，新建版本目录并更新目录页与侧边栏，**不要改写旧版本内容**。

## 4. Markdown 编写规范

范本：`docs/Frontend/Basic/HTML` 下的 `Overview/index.md`、`Basic/index.md`、`Form/index.md`、`Table/index.md`。

### 页面结构

1. 每页只允许一个 `# 标题`（H1），标题与侧边栏 `text` 保持一致。
2. 正文用 H2 分节、H3 分小节，逐级递进、不要跳级；站点 outline 配置为 `[2, 6]`，只有 H2 及以上会出现在右侧目录。
3. 普通文档不写 frontmatter；仅根目录 `index.md` 使用 `layout: home`。
4. 一页只讲一个主题，避免“大而全”的超长页面；内容多时拆成多页，用目录页串联。

### 语言与表达

1. 统一简体中文，口语化、讲人话：先给结论/定义，再解释细节。
2. 关键术语、重点用 **加粗**；专业术语首次出现时给出英文原文，如「HTML（HyperText Markup Language，超文本标记语言）」。
3. 属性清单、使用场景、操作步骤用无序/有序列表；属性对照、版本要求、平台支持用 Markdown 表格。
4. 步骤类内容必须给出可验证的收尾，例如「启动后访问 http://localhost:5173/，确认页面正常、控制台无报错」。

### 提示容器

注意：`config.mts` 已自定义容器标题，与 VitePress 默认不同：

| 容器 | 用途 | 页面显示标题 |
| --- | --- | --- |
| `:::tip` | 建议、技巧、一句话总结 | 提示 |
| `:::warning` | 补充说明 | 说明 |
| `:::danger` | 易错点、必须注意的坑 | 注意 |
| `:::info` | 背景、版本、环境信息 | 信息 |
| `:::details` | 折叠的详细信息 | 详细信息 |

写法：

```markdown
::: tip 一句话理解
传统 AI 告诉你“怎么做”，OpenClaw **直接帮你做**。
:::
```

`:::danger` 容器中，易错点用有序列表逐条写清，并给出正确写法。

### 代码块

1. 代码块必须标注语言：`html`、`css`、`js`、`ts`、`shell`、`json`、`properties`、`vue`、`sql`、`yaml`、`dockerfile` 等。
2. 涉及具体文件时使用代码块标题语法：

   ```markdown
   ```typescript [src/main.ts]
   ```

3. 示例代码保持可复制、可运行；超长配置用 `...` 省略并注释说明。
4. 命令行统一放 `shell` 代码块，完整给出 `cd`、安装、启动等命令。

### 表格

1. 表头与分隔行必须齐全。
2. 单元格内容过长时用 `<br/>` 换行（参考 `HTML/Table/index.md` 的写法）。
3. 表格只放可对照的信息，不要用表格写大段说明文字。

### 反例

容易写错的写法放入 `:::danger`，或直接在代码块注释中说明错误原因，并给出正确写法。

## 5. 内容深度与完整性要求

目标：每篇文档都要“讲透”，禁止空壳页、凑字数、只贴代码不解释。

### 页面级要求

每篇正文至少覆盖以下模块（可按主题取舍，但“示例 + 易错点 + 验证”不允许缺失）：

1. 一句话定位：H1 下方用 1~2 句说明“这是什么、解决什么问题、适用于谁”。
2. 概念与原理：关键概念给出定义、英文术语和工作原理；复杂内容配示意图。
3. 分类/结构/属性：用表格或列表完整罗列，每一项都要有解释，不要只列名称。
4. 示例代码：每个语法、API、命令都要有可复制示例，标注语言与文件路径；关键示例给出运行输出。
5. 常用清单：常用命令、API、配置项、参数表。
6. 易错点与最佳实践：`:::danger` 列坑并配正确写法，`:::tip` 给建议。
7. 实战/综合案例：每个主题至少 1 个完整可运行的实战章节。
8. 验证方式：给出可验证的收尾（命令、预期输出、页面地址）。
9. 参考资料：文末附官方文档或权威链接。

### 主题级要求

1. 每个主题默认按「完整主题模板」展开：Overview → Environment → CoreConcepts → Basic → Advanced → Practice → FAQ → References（按主题调整）。
2. 大主题 6~10 篇，小主题至少 3~5 篇；不允许“一篇概述就结束”。
3. 复杂流程、架构、对比场景至少配 1 张示意图（本地 SVG 或可授权图源）。

### 信息质量要求

1. 版本与事实必须联网核对（如 Java 25 LTS、Python 3.14），以官方来源为准并在文中说明。
2. 代码示例尽量本地验证；无法验证的要注明“按官方文档编写，建议本地验证”。
3. 不编造 API、参数、命令；不确定就写“待核实”或查阅官方文档。
4. 默认按当前最新稳定版撰写，同时说明常用旧版本的差异。

### 篇幅参考

| 页面类型 | 参考篇幅 |
| --- | --- |
| 概述/环境页 | 80~150 行 |
| 基础/进阶页 | 150~350 行 |
| 实战页 | 200~400 行 |

少于 60 行的页面视为「未完成」，需要补充后再提交。

## 6. 目录页（index.md）规范

- 每个主题/项目目录的 `index.md` 是该主题的目录页：`# 主题名` + 子页链接无序列表。
- `docs/` 下每个**大类目录**（`AI`、`Backend`、`DB`、`Frontend`、`Ops`、`Tools`、`Others`）的 `index.md` **只放 `# 分类名` + 子目录链接列表**，不写正文。
- 主题目录的 `index.md` 是**侧边栏入口**：侧边栏根节点 `text` 用主题名，`link` 指向该 `index.md`，`items` 是该主题的子页面，**默认折叠**（`collapsed: true`）。
- 链接使用相对路径：`(Overview/index.md)`、`(../Compose/index.md)`。
- 需要分组时可在列表上加小标题（参考 `project/Base/Vue3Template/index.md` 将 CSS 相关拆成一组）。
- 目录页也可以直接承载正文（如 `docs/AI/OpenClaw/Overview/index.md`），此时它同时作为侧边栏叶子项。

## 7. 图片与资源规范

1. 文档图片放在「当前主题」的 `assets/` 子目录，与文档同级（如 `HTML/Basic/assets/`）。
2. 引用一律使用相对路径：`![描述](assets/图片.png)` 或 `![描述](./assets/图片.png)`；**不要**使用 `/assets/...` 绝对路径（站点 base 为 `/docs-website/`，绝对路径会导致图片失效）。
3. 截图工具的自动命名（如 `image-20250706231134947.png`）可以直接使用，不必重命名；如需重命名，使用英文小写加短横线。
4. 需要控制图片大小时使用既有写法：`<img src="./assets/xxx.png" style="zoom:25%;" />`。
5. 全局资源（`logo.svg`、`background.svg`）才放 `public/`，文档图片一律放对应 `assets/`。
6. 不提交大文件、临时文件；图片随文档一并提交到 Git。

## 8. 导航与侧边栏维护

### 分工

- `nav.ts`：顶部导航，新增分类或子项时必须同步。
- `sidebar.ts`：侧边栏汇总入口，格式为 `路径前缀: 分支数组`，如 `"/docs/Frontend/Basic": FrontBasic`。
- 各分类分支文件（`frontend.ts`、`backend.ts`、`db.ts`、`ops.ts`、`AI.ts`、`tools.ts`、`project.ts`）维护具体侧边栏树。

### 节点写法

分组节点：

```typescript
{
  text: "HTML",
  link: "/docs/Frontend/Basic/HTML/index.md",
  collapsed: true,
  items: [
    { text: "HTML 概述", link: "/docs/Frontend/Basic/HTML/Overview/index.md" },
  ],
}
```

叶子节点：

```typescript
{ text: "HTML 概述", link: "/docs/Frontend/Basic/HTML/Overview/index.md" }
```

规则：

1. 链接统一以 `/docs/` 或 `/project/` 开头；推荐与 `frontend.ts` 一致，使用带 `index.md` 的完整形式。
2. 侧边栏 `text` 使用人类可读的中文名称（如「HTML 表格标签」），不要直接用文件夹名。
3. 空分类保留空数组占位（`tools.ts`、`db.ts` 目前如此），不要删除导出。
4. 新增、移动、重命名文档后依次执行：更新对应分支文件 → 检查 `sidebar.ts` 汇总 → 检查 `nav.ts` → 运行 `pnpm docs:dev` 或 `pnpm docs:build` 验证。
5. `utils/` 中的自动生成脚本是备选方案，当前仓库以手动维护侧边栏为准。
6. 每个主题在 `sidebar.ts` 中按**主题路径**挂载（如 `"/docs/Backend/Java": Java`）：进入 `docs/Backend/Java` 才展示 Java 的侧边栏，根节点是 `Java/index.md`，子内容默认折叠。
7. 大类路径（如 `"/docs/Backend"`）挂分类级侧边栏，与 `nav.ts` 的大类保持一致；大类 key **不要带尾斜杠**，确保主题 key（如 `"/docs/Backend/Java"`）更具体并优先匹配；大类 `index.md` 只放标题和子目录链接。

## 9. 项目文档（project/）规范

1. `project/Base`、`project/Complete` 各代表一种项目类型；每个项目一个子目录（如 `Base/Vue3Template`），`index.md` 为项目总目录。
2. 每个章节一个子目录 + `index.md`；内容少的小节可以平铺为 `xxx.md`。
3. 范本：`project/Base/Vue3Template`（`InitProject`、`Env`、`Http`、`Build` 等章节）。
4. 项目文档必须“能照着做一遍”：
   - 环境与版本用 `:::info 当前使用的版本` 列出（Node、pnpm 等）；
   - 每个配置贴完整文件内容，并用 `[文件名]` 代码块标题标明文件路径；
   - 每个操作给完整命令与验证方式；
   - 截图存放在本章节 `assets/` 下。

## 10. Git 提交规范

采用 Conventional Commits 风格（与仓库历史一致）：

| 类型 | 适用场景 | 示例 |
| --- | --- | --- |
| `docs` | 文档新增、修改 | `docs(Frame): 添加前端框架文档索引` |
| `feat` | 新功能、新脚本 | `feat: add docker` |
| `chore` | 配置、依赖、构建 | `chore(vitepress): 配置ignoreDeadLinks和metaChunk` |
| `fix` | 修正链接、标题、图片路径等错误 | `docs(NodeJs Modules): 修正文档中图片的相对路径` |

规则：scope 使用分类或主题（`docs(Frame)`、`docs(DB/Overview)`）；描述保持单行、简洁，中文或英文均可。

## 11. 新增/修改文档检查清单

新增文档时：

1. 确定所属顶级分类与主题目录；目录不存在则按命名规范新建。
2. 新主题先建 `index.md` 目录页；每个页面使用「英文目录 + index.md」结构，不平铺单文件。
3. 按第 4、5 节规范写正文：结构规范 + 内容深度与完整性要求全部满足。
4. 图片放入对应页面目录的 `assets/`，使用相对路径引用。
5. 更新对应侧边栏分支文件；涉及新分类或导航时更新 `nav.ts`。
6. 内容自查：概念/原理、可运行示例、表格/清单、易错点、验证方式、参考资料齐全；篇幅达标；版本信息已联网核对。
7. 运行 `pnpm docs:build`（或 `docs:dev`）确认构建成功、链接可达。
8. 按第 10 节规范提交。
9. 大版本检查：主题存在大版本差异时按版本目录拆分（如 `Spring5/Spring6`），新内容面向最新稳定版，旧版本保留并标注状态。

修改文档时：

1. 保持既有文件名与 URL 稳定；确需改名时，全库搜索并更新所有引用（侧边栏、目录页、正文链接）。
2. 只修改目标文件，不动无关内容，不批量重排既有文档。
3. 涉及存量平铺文件时，顺手迁移为「英文目录 + index.md」结构并更新引用。
4. 每个任务日除新增主题外，还要挑选 **5~10 篇存量文档**进行调整、补充与更新：内容过期（版本/命令/API）、结构不规范、缺示例或配图、链接失效、标题与侧边栏不一致等。
5. 存量文档没有明显问题时，做质量巡检（标题、链接、图片、版本信息），并把结果记录到 `DOCS_PLAN.md` 的存量整理清单。
6. 修改后同样运行构建验证。

## 12. 对 AI 协作的要求

- 开始任何文档任务前，先阅读本文件，并打开范本 `docs/Frontend/Basic/HTML` 与目标分类现有文件，模仿其风格。
- 统一使用简体中文；不要擅自改成英文或中英混排。
- 保持 UTF-8 编码；不要重排或重构无关文件。
- 新增内容必须同步侧边栏/导航，完成后必须构建验证。
- 生成内容必须达到第 5 节的深度要求，并按 `DOCS_PLAN.md` 的数量产出，宁多勿少、禁止空壳页。
- 每个任务日除新主题外，还要挑选 **5~10 篇存量文档**进行调整补充与更新，不能只写新文档、放任旧文档过期。
- 主题出现大版本调整时，按版本目录组织（如 `Spring5/Spring6`），保留旧版本文档并标注状态，不要用新版覆盖旧版。
