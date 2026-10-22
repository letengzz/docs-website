# 设计系统与组件库工程

<p style="text-align:center;"><img src="./assets/design-system-logo.png" alt="设计系统专题标识：三层 token 与组件方块的组合" style="zoom:75%;" /></p>

<p style="text-align:center;"><img src="./assets/ds-topic-map.svg" alt="设计系统专题地图：token 层、组件 API 层、文档与版本、消费侧、主题、视觉回归、治理与实战七个环节" style="zoom:75%;" /></p>

设计系统不是「一套好看的组件」，而是一条**从设计决定到线上产物的链**：token 被写下来、组件被订阅、文档被生成、版本被声明、产物被消费、主题被叠加、基线被比对、改动被治理。链上任何一环没有闸门，问题都会顺流而下放大：token 改错 → 组件全变 → 文档没同步 → 基线漂移 → 消费方在升级时才发现。

本专题按环拆章，每一章只回答三个问题：**这一环的失败模式是什么、判据是什么、怎么在本地验证它没被破坏**。

::: tip 一句话理解
组件库的门槛是「能跑起来」，设计系统的门槛是「**改一个值之后，你知道谁会变、变了怎么被发现、发版时谁需要动手**」。前者靠写组件，后者靠一条能验的链。
:::

## 与相邻专题的分工

本专题最容易和九个已有专题重叠。下表把边界写死——**同一件事只在一处讲透，其余处只做链接**。

| 相邻专题 | 它回答什么 | 本专题回答什么 | 为什么不能互相替代 |
| --- | --- | --- | --- |
| [CSS 进阶](../Basic/CSS/Advanced/index.md) | 层叠、布局、选择器、动画的**语法与机制** | 哪些值该提升成 token、变量在哪一层落盘 | 那一层讲 CSS 怎么工作，本专题讲「值由谁决定」 |
| [原子化 CSS](../Basic/CSS/AtomicCSS/index.md) | Tailwind / UnoCSS 的类名体系与配置方式 | 原子类与 token 谁是谁的上游、`@theme` 之后 token 还剩什么职责 | 那一页讲工具，本专题讲「工具读取的那份数据从哪来」 |
| [低代码平台 · 物料体系](../LowCode/Materials/index.md) | 物料的**协议**（schema / setter / 渲染器）与搭建器加载 | 组件的**API 契约**（受控、组合、变体维度）与版本语义 | 物料协议解决「怎么被搭出来」，组件 API 解决「怎么被写出来」 |
| [微交互与动效工程 · 时长](../Motion/Timing/index.md) | 时长分级、缓动曲线、弹簧参数怎么选 | 这些时长怎么进 token 层、跨端怎么保持同一套 | 那一页给取值，本专题给「取值怎么被复用与版本化」 |
| [国际化与无障碍 · 无障碍基础](../IntlA11y/A11yFoundation/index.md) | 语义化、对比度、ARIA、焦点 | 对比度怎么在 token 层被**强制**（CI 里拦） | 那一页讲标准，本专题讲「标准怎么变成构建步骤」 |
| [状态管理与数据流](../StateDataFlow/Overview/index.md) | 本地态、远端态、缓存与同步 | 组件内部状态与外部状态的**所有权边界** | 那一页讲应用状态，本专题讲「一个组件该持有什么」 |
| [前端测试 · 组件测试](../Testing/ComponentTesting/index.md) | 断言方式、查询优先级、交互测试 | 视觉回归为什么不能用断言替代、阈值怎么定 | 测试判「行为对不对」，视觉回归判「看起来变没变」 |
| [前端工程化](../Others/FrontendEngineering/index.md) | 规范、构建、CI、脚手架 | 包产物形态（`exports` / `sideEffects` / 双格式）为什么影响体积 | 那一页讲流水线，本专题讲「流水线里发出去的那个包」 |
| [文档体系建设](../../Tools/DocsInfra/Overview/index.md) | 静态站点、搜索、多版本、写作规范 | 组件文档的 props 表怎么**从类型生成**、漂移怎么拦 | 那一页讲站点怎么搭，本专题讲「站点里的那张表从哪来」 |
| [技术决策与评审](../../Others/TechDecision/Overview/index.md) | 决策怎么记录、评审、推翻 | 一次 token 改动的**影响面**怎么算出来给评审用 | 那一页讲流程，本专题给流程的输入数据 |

::: info 版本组织说明
本专题**不建版本目录**，三条理由：

1. **它不是某个产品的文档，而是一类工程问题**——Style Dictionary 换一个大版本，三层 token 的职责不会变；
2. 真正的版本差异集中在两处：**token 格式规范**（DTCG 2025.10 与旧的自定义 JSON）与**构建工具**（Style Dictionary v4 → v5），两者都在页内用「版本对照表 + 迁移注意」处理，拆目录会制造两份要同步维护的清单；
3. 组件库侧的版本差异已经收敛进 [版本、废弃与发布治理](ReleaseGovernance/index.md) 的分类器判据里——它判的是「这次改动算不算破坏性」，与具体版本号无关。

仓库内已有版本目录范式可对照，三者都遵守「旧版本保留 + 页顶标注状态 + 新版不覆盖」：

| 版本目录范式 | 入口 | 组织方式 |
| --- | --- | --- |
| Spring 框架 | [Spring 版本入口](../../Backend/Java/Frame/Spring/index.md) | `Spring5/`（存量维护）与 `Spring6/`（当前基线）并存 |
| 配置管理 | [配置管理与动态配置](../../Ops/ConfigManagement/index.md) | `Nacos2/`（仅存量项目）与 `Nacos3/`（当前基线）并存 |
| Vue 框架 | [Vue 框架](../Frame/Vue/index.md) | `Vue2/` 与 `Vue3/` 并存，`Vue2` 标注为存量项目使用 |
:::

## 十篇正文

按「先看清整条链，再从 token 往上走到产物与治理」的顺序排列。

| # | 页面 | 一句话说明 |
| --- | --- | --- |
| 1 | [总览：一条链、七环与三张账](Overview/index.md) | 链上七环各自的失败模式；设计账 / 代码账 / 产物账怎么对 |
| 2 | [Token：三层、双产物与解析](Tokens/index.md) | raw 164 / semantic 91 / component 168 怎么分工；13,197 B 为什么比 7,644 B 更难改 |
| 3 | [主题与多品牌：覆盖式与编译式](Theming/index.md) | 一个主题 293 B 还是 2,821 B；什么时候必须把主题升级成构建目标 |
| 4 | [组件 API：表面积与状态所有权](ComponentAPI/index.md) | 8 个布尔 prop 的 256 种组合怎么剪到 90；受控组件丢值为什么不报错 |
| 5 | [文档与代码同源](DocsSync/index.md) | props 表从类型生成；六类漂移里哪一类比对器抓不到 |
| 6 | [产物体积：摇树、样式与 exports](Distribution/index.md) | 同一个组件深路径 162 B、barrel 645 B；CSS 为什么摇不掉 |
| 7 | [视觉回归：8 个变体与 6 种口径](VisualRegression/index.md) | 最准的口径只拦对 6/8；环境噪声必须先治、再谈阈值 |
| 8 | [版本、废弃与发布治理](ReleaseGovernance/index.md) | 24 条变更里 13 条破坏性；影响面 24 个组件的改动只能整包发版 |
| 9 | [实战：12 个组件的最小设计系统](Practice/index.md) | 五天走完整条链，每天一个可验证的收尾 |
| 10 | [常见问题与分诊](FAQ/index.md) | 三类根因、九种症状，先看产物再看计算值最后看基线 |

## 判据族总览

全专题 **10 族 80 条**判据，每条只回答三件事：**约定是什么 / 定错了会怎样 / 怎么验证它没被破坏**。

| 页面 | 判据族 | 覆盖的约定 | 条数 |
| --- | --- | --- | --- |
| [总览](Overview/index.md) | `DSOV` | 每一环都有闸门，账对得上才算完 | 8 |
| [Token](Tokens/index.md) | `DSTN` | 值只写一次，引用可解析，产物可 diff | 8 |
| [主题与多品牌](Theming/index.md) | `DSTH` | 主题只改映射，不改组件 | 8 |
| [组件 API](ComponentAPI/index.md) | `DSA` | 状态只有一个所有者，组合优于布尔 | 8 |
| [文档同源](DocsSync/index.md) | `DSDC` | 表由类型生成，不一致就失败 | 8 |
| [产物体积](Distribution/index.md) | `DSDT` | 声明副作用，给出深路径，按需才成立 | 8 |
| [视觉回归](VisualRegression/index.md) | `DSRG` | 基线与环境绑定，先遮罩再谈阈值 | 8 |
| [版本与治理](ReleaseGovernance/index.md) | `DSVR` | 分类看契约，发版看影响面 | 8 |
| [实战](Practice/index.md) | `DSPR` | 每天一个可验证收尾，红灯不带下去 | 8 |
| [分诊](FAQ/index.md) | `DSFQ` | 先产物、再计算值、最后基线 | 8 |

## 阅读顺序建议

1. **只想建立判断力**：读 [总览](Overview/index.md) + [Token](Tokens/index.md)。两页够你在评审里问出「这个值由谁决定、它编译成了什么」。
2. **正在救一个线上问题**：直接看 [常见问题与分诊](FAQ/index.md) 的分诊表，它会把你送回正确的页面。
3. **要动手搭一套**：从 [Token](Tokens/index.md) 的双产物开始，按 [实战](Practice/index.md) 的五天顺序走。
4. **只关心「为什么包这么大」**：读 [产物体积](Distribution/index.md)，再回头看 [组件 API](ComponentAPI/index.md) 的每渲染成本表。

## 本机实测：五个反直觉的读数

以下数字全部来自本机可复跑脚本（Node 22.22.2，标准库 + esbuild，脚本不入库），每一页会重新给出对应脚本与读数。

| 结论 | 读数 | 说明 |
| --- | --- | --- |
| **全量落盘比两层落盘只大 72%，但维护成本差一个量级** | 两层 **7,644 B**（gzip 1,556 B）vs 三层 **13,197 B**（gzip 2,326 B） | 组件层一旦落盘，改一个语义 token 要改两处 |
| **主题增量决定实现方式** | 覆盖式 **293 B**（基础的 3.8%）vs 编译式 **2,821 B**（36.9%）；10 品牌 **2,930 B** vs **28,210 B** | 判据：增量 < 10% 用覆盖式，否则把主题升级成构建目标 |
| **摇树对 JS 有效，对 CSS 基本无效** | 12 个组件的包：深路径 JS **162 B** = barrel **162 B**，但 CSS **118 B** vs **1,428 B**（12.1×） | CSS 不在 ES 模块图里，`sideEffects` 才是开关 |
| **视觉回归的最优口径只拦对 6/8** | 8 个变体 × 6 种口径，严格逐像素 + 面积阈值最好；漏 V2（色差 2/255）与 V7（0.109% 面积） | 「全绿」不等于「没变」，阈值必须配遮罩与环境绑定 |
| **语义化版本管不了视觉** | 24 条真实变更里 13 条破坏性；朴素分类器准确率 54%，判据表分类器 92%（判错 2） | 版本号管「编译期会不会报错」，基线管「看起来变没变」 |

::: warning 关于这五条的口径
读数都是**单机、冷启动后、固定输入**的中位数，用于比较**数量级**，不作为性能承诺。包体积数字来自 esbuild 真实打包（`--bundle --minify`），不是压缩工具估算；视觉差异百分比是**差异像素 / 画布像素**，与具体截图尺寸绑定。
:::

## 事实与规格速览（2026-10 口径）

| 事项 | 结论 | 依据 |
| --- | --- | --- |
| DTCG 格式规范 | **2025.10**（2025-10-28 发布）是第一个稳定版；13 种类型 = 7 种原始（`color` `dimension` `fontFamily` `fontWeight` `duration` `cubicBezier` `number`）+ 6 种复合（`strokeStyle` `border` `transition` `shadow` `gradient` `typography`） | designtokens.org 2025.10 |
| 规范地位 | **社区组规范，不是 W3C 标准**，也不在 W3C 标准轨道上；文件扩展名 `.tokens.json`，键名带 `$` 前缀（`$value` / `$type` / `$description` / `$deprecated`） | DTCG 规范状态声明 |
| 结构化取值 | `dimension` / `duration` 是对象（`{value, unit}`），`cubicBezier` 是四元数组；旧的自定义 JSON 把 `"16px"` 当字符串，迁移时**必须逐条转格式** | DTCG 2025.10 类型定义 |
| Style Dictionary | **5.6.0**（2026-10-04）；v5 以 DTCG 2025.10 为基础格式，v4 已原生读 DTCG | npm 发布记录与官方文档 |
| Storybook | **10.6**（2026-09）；10.x 无破坏性变更，11 处于 alpha（目标 2026-12 稳定） | storybook.js.org releases |
| Tailwind CSS v4 | `@theme` 里声明的变量同时成为 CSS 变量与工具类；token 与原子类的上游关系因此改写 | tailwindcss.com 文档 |
| Node 包导出 | `exports` 子路径、`sideEffects` 声明、`"type": "module"` 与双格式产物是「按需加载」成立的三件套 | Node.js Packages 文档 |
| 语义化版本 | `MAJOR.MINOR.PATCH`；`0.y.z` 期间公开 API 视为不稳定；`peerDependencies` 范围属于接口契约的一部分 | semver.org 2.0.0 |

## 参考资料

- [Design Tokens Format Module 2025.10（DTCG）](https://www.designtokens.org/tr/2025.10/format/)
- [Style Dictionary 官方文档](https://styledictionary.com/)
- [Storybook 10.6 发布说明](https://storybook.js.org/releases/10.6)
- [Tailwind CSS · Theme variables](https://tailwindcss.com/docs/theme)
- [Node.js · Packages（`exports` 与 `imports`）](https://nodejs.org/api/packages.html)
- [Node.js · `sideEffects` 与 tree shaking（webpack 文档）](https://webpack.js.org/guides/tree-shaking/)
- [Semantic Versioning 2.0.0](https://semver.org/)
- [W3C · WCAG 2.2 对比度（1.4.3 / 1.4.11）](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
