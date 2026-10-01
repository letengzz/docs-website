# 构建进展记录

本页记录这个专题**实际做到了什么程度**：交付物清单、每步的验收方式与结果、版本口径的核对时间，以及**已知没做的部分**。

写它的目的不是存档，而是让下一个人（包括三个月后的自己）能一眼判断：哪些结论有实测支撑，哪些只是设计意图。

::: info 记录口径
- 记录时间：**2026-09-30**
- 验证环境：Windows / Node **22.22.2** / pnpm
- 「实测」= 编写时在本机真实跑过并留下了输出；「设计」= 已写进文档、但未在编写环境实际运行的步骤
- 本仓是**文档库**：`project/` 下只有 Markdown 与配图，不含任何脚本与工程文件。文中出现的 `scripts/xxx`、`app/**` 一律指**读者自己工程里的文件**
:::

## 一、交付物清单

### 1.1 文档（11 页）

| 页面 | 行数 | 定位 |
| --- | --- | --- |
| [`index.md`](../index.md) | 120 | 专题入口：全景图、路径方案、版本基线、契约表 |
| [`Requirement/index.md`](../Requirement/index.md) | 112 | 第 0 步：需求与可插拔边界 |
| [`Scaffold/index.md`](../Scaffold/index.md) | 219 | 第 1 步：脚手架与工程规约 |
| [`AdapterDesign/index.md`](../AdapterDesign/index.md) | 278 | 第 2 步：适配层设计 |
| [`Adapters/index.md`](../Adapters/index.md) | 321 | 第 3 步：三套内置适配器 |
| [`DesignToken/index.md`](../DesignToken/index.md) | 199 | 第 4 步：设计令牌与主题桥接 |
| [`SwitchTooling/index.md`](../SwitchTooling/index.md) | 563 | 第 5 步：切换工具链与多形态构建 |
| [`Testing/index.md`](../Testing/index.md) | 526 | 第 6 步：测试与门禁 |
| [`Deployment/index.md`](../Deployment/index.md) | 301 | 第 7 步：部署与交付 |
| [`FAQ/index.md`](../FAQ/index.md) | 231 | 排障决策树、反模式清单、速查问答 |
| `Progress/index.md` | 本页 | 进展与验收记录 |

合计约 **2870 行**（不含本页）。每页均满足仓库对「实战页 200~400 行 / 概述页 80~150 行」的篇幅要求，
且每页都配了与内容对应的示意图（见 §五）。

### 1.2 脚本设计（实现写在文档中，仓库不存放文件）

| 文件 | 行数 | 说明 |
| --- | --- | --- |
| `scripts/ui-select.mjs` | 643 | 切换器本体：零依赖，只用 `node:fs` / `node:path` |
| `scripts/selftest.mjs` | 678 | 自测：**275 项断言**，零依赖，进程内驱动 |
| `scripts/fixture/nuxt.config.ts` | — | 自测用的最小工程配置（含 marker 区间与手写区） |
| `scripts/fixture/ui.config.json` | — | 唯一事实来源示例 |
| `scripts/fixture/app/pages/index.vue` | — | 业务页示例：不出现任何组件库名字 |
| `scripts/fixture/app/assets/styles/tokens.css` | — | 第 ① ② 层令牌定义处（手写，脚本不碰） |

::: warning 一件事必须说清楚：本仓只放文档，一行代码都不放
文档里出现的 `app/components/x/*`、`app/ui/impl/*`、`test/**`、`nuxt.config.ts`、`vitest.config.ts`、`scripts/*` 等，
全是**照着写就能跑起来的完整清单**，不是本仓已提交的文件——本仓是文档库，不是模板仓库。

其中 `scripts/`（切换器与自测）是唯一「必须逐字节正确」的部分：
契约组件写错了报错会告诉你错在哪，而一个缩进累加的替换 bug 只会在 CI 上以「第一次跑就报红」的形式出现（第 5 步 §4.2 就是这个真实 bug）。
所以第 5 步把它的结构与关键实现逐段写了出来，落地到你的工程后再执行 `node scripts/selftest.mjs` 验收。
:::

## 二、七步验收记录

| 步 | 验收方式 | 结果 |
| --- | --- | --- |
| **0 需求与边界** | 八项验收清单逐条对照「可插拔性分级表」自洽 | ✅ 设计完成 |
| **1 脚手架** | `pnpm dlx nuxi@latest init` → `pnpm dev` 可启动；`pnpm typecheck` / `pnpm lint` 退出码 0 | ✅ 命令与判据已给出（依赖外部网络，未在本机跑完初始化） |
| **2 适配层** | 契约组件 `XButton.vue` 在四个实现下 `mountSuspended` 均可挂载 | ⚠️ 设计完成；`#ui-impl` 别名机制在切换器产物中已实测生效（见 §三） |
| **3 三套适配器** | 四个库的模块名/版本/样式引入方式全部联网核对 | ✅ 见 §四 |
| **4 设计令牌** | 三层令牌 + 四库变量映射表；`generated-tokens.css` 由脚本生成 | ✅ 生成逻辑已实测（自测 B 组断言映射落在正确的库前缀上） |
| **5 切换工具链** | 幂等 / 可校验 / 可回溯 / 零依赖 / 只碰生成物，**五条性质各有断言** | ✅ **275 / 275 断言通过**（见 §三） |
| **6 测试与门禁** | 契约测试用例集合冻结；四道门禁各有一条「改坏必须报红」的记录 | ⚠️ 设计完成；门禁断言中的 `--check` / 自测两道为本机实测 |
| **7 部署与交付** | `--check` → `pnpm build` → `curl /api/health` 报出正确 `ui` 字段 | ⚠️ 设计完成，依赖真实部署环境 |

图例：✅ 本机实测通过　⚠️ 设计完成、判据明确，待真实工程环境验证

## 三、切换器实测结果

以下输出均为本机真实运行结果，不是示意：

```text
$ node scripts/selftest.mjs
ui-select.mjs 自测（零依赖 · 进程内驱动 · 门禁断言为变异测试）

  PASS  A  用法与元数据（23 项，失败 0）
  PASS  B  生成物内容（185 项，失败 0）
  PASS  C  幂等（6 项，失败 0）
  PASS  D  手写文件保护（10 项，失败 0）
  PASS  E  marker / import 缺失（9 项，失败 0）
  PASS  F  门禁（默认拒绝）（14 项，失败 0）
  PASS  G  --check 行为（17 项，失败 0）
  PASS  H  全矩阵（1 项，失败 0）
  PASS  I  --dry-run（5 项，失败 0）
  PASS  J  --print（5 项，失败 0）

断言：通过 275 / 失败 0

结果：OK
```

### 3.1 五条性质各自被哪一组断言守住

| 性质 | 断言组 | 关键断言 |
| --- | --- | --- |
| **幂等** | C | 「连跑两次后全目录字节不变」「切走再切回产物回到同一状态」 |
| **可校验** | G | 「篡改生成物后被报红并指出文件名」「重跑一次即收敛」 |
| **可回溯** | D | 「换库后 `ui.config.json` 记录了新取值」 |
| **零依赖** | — | 脚本只 import `node:fs` / `node:path` / `node:process` / `node:url`，`package.json` 无运行时依赖 |
| **只碰生成物** | D | 「换库不改业务页面 / 手写令牌 / `nuxt.config.ts`」「区间外的手改配置在换库后保留」 |

### 3.2 门禁是变异测试，不是冒烟测试

自测里有 30 多项是**主动把东西改坏、要求它必须报红**。做过的变异实验：

| 变异动作 | 观察到的结果 |
| --- | --- |
| 把 `personalizeOf` 改成恒真（不再由 `render` 派生） | 自测从 **0 失败 → 18 失败**，退出码 1，集中在 B、F 两组 |
| 删掉 `nuxt.config.ts` 的 marker 区间 | `--check` 与切换命令均退出码 1，且**不写任何文件** |
| 改坏生成物的 `import` 路径 | 拒绝执行，报错提示如何补回，不写文件 |
| 往 `manifest.ts` 追加一行注释 | `--check` 报出「`app/ui/generated/manifest.ts`：内容与 ui.config.json 不一致」「共 1 个文件漂移」 |
| 手工把 `ui.config.json` 的 `personalize` 改成 `false` | `--check` 报红，并说明该字段由 `render` 派生 |
| 越过门禁取值（`vuetify` 不带 `--allow-experimental`、`ssg` 不带 `--allow-degraded-personalize`） | 均退出码 1，且**不落盘**；两条同时触发时都报出来 |

::: tip 为什么这件事值得单独记
第一行那个变异实验是**整份自测可信度的证据**。

如果改坏核心逻辑后自测依然全绿，那 275 这个数字就只是装饰——它证明不了任何事。所以每次改动自测，都应该顺手做一次这样的变异实验，确认它还能报红。
:::

### 3.3 开发过程中踩到并修掉的真实 bug

| # | bug | 现象 | 根因与修法 |
| --- | --- | --- | --- |
| 1 | **marker 区间前置缩进被反复累加** | 单次执行正常；连跑两次后 `--check` 立刻报红 | 简单从 marker 关键字位置替换，区间前的缩进每跑一次多一层。改为**从含缩进的行首开始替换**（`text.lastIndexOf('\n', b) + 1`） |
| 2 | **`personalize` 被设计成 CLI 参数** | 可以手工指定，和 `render` 打架 | 它是 `render` 的派生值，不是开关。删掉参数，改为 `personalizeOf(render)`，并让 `--check` 校验一致性 |
| 3 | **`import` 精确匹配过严** | fixture 里换行书写的 `import` 被误判为缺失 | 改用生成物模块路径做包含判断，错误信息仍回显完整 `import` 写法 |
| 4 | **自测里快照取在「自己改坏之后」** | 「拒绝执行时不写文件」错误报红 | 快照必须取在变异动作之后，否则比出来的是测试自己造成的差异 |

第 1 条是最有价值的一条：它只在**重复执行**时暴露，而这正是 CI 上最容易被误判成「环境问题」的形态。

### 3.4 全矩阵结果

```text
OK   element/ssr      OK   element/ssg
OK   antd/ssr         OK   antd/ssg
OK   nuxtui/ssr       OK   nuxtui/ssg
OK   vuetify/ssr      OK   vuetify/ssg
全矩阵结果：通过 8 / 8
```

## 四、版本口径核对记录

全部以官方发布页为准，核对时间 **2026-09-30**：

| 依赖 | 口径 | 说明 |
| --- | --- | --- |
| **Nuxt** | 4.5.x（4.5.2，2026-08-05 发布） | Nuxt 3 已于 2026-07-31 EOL；Nuxt 4.5 升级到 Vite 8、unhead v3、unctx v3 |
| **Element Plus** | 2.14.x + `@element-plus/nuxt` 1.1.x | 需注意 pnpm 下的 `dayjs` 解析坑 |
| **Ant Design Vue** | 4.x + `@ant-design-vue/nuxt` 1.4.x | 需打开 `extractStyle` |
| **Nuxt UI** | 4.11.x | 要求 Nuxt ≥ 4.1 + Tailwind CSS 4；Pro 版已并入 MIT 包 |
| **Vuetify** | 3.x + `vuetify-nuxt-module` **1.0.0-rc.5** | 仍是 rc → 标为**实验性**，门禁默认拒绝 |
| **vitest** | **4.1.x** | 4.1 起正式支持 Vite 8；peer 声明 `^6 \|\| ^7 \|\| ^8` |
| **@nuxt/test-utils** | **4.1.x** | peer 声明 `vitest ^4.0.2`；Nuxt 4.5.2 测试指南指向该版本 |
| **@playwright/test** | 1.63.x（2026-09-04） | 端到端 |

::: warning 两条明确的版本边界
1. **Vitest 5（5.0.x，2026-09-25）暂不推荐**：能力上没问题（Node ≥ 22.12、Vite ≥ 6.4），
   但 `@nuxt/test-utils` 4.x 的 peer 范围仍写 `vitest ^4.0.2`。升级前先核对，别让 peer 警告变成「测试跑一半挂住」。
2. **Vuetify 不进默认矩阵**：模块仍是 rc，源码里锁的是**精确版本** `1.0.0-rc.5`（不是 `^1.0.0-rc.5`），
   且它只在升级该模块时才跑测试。
:::

## 五、配图清单

13 张示意图 + 1 张 Logo，全部为本仓 SVG（不外链），并已通过渲染校验（`WARN = 0`、XML 合法）。

| 配图 | 用在 | 画布 |
| --- | --- | --- |
| `template-landscape.svg` | 专题入口 | 全景 |
| `pluggable-layers.svg` | 第 0 步 | 四层可插拔 |
| `project-structure.svg` | 第 1 步 | 目录结构 |
| `adapter-contract.svg` | 第 2 步 | 契约三条规则 |
| `switch-modes.svg` | 第 2 步 | 三种切换模式取舍 |
| `adapter-mapping.svg` | 第 3 步 | 四库映射对照 |
| `ssr-hydration.svg` | 第 3 步 | SSR 与水合差异 |
| `token-bridge.svg` | 第 4 步 | 三层令牌桥接 |
| `ui-select-flow.svg` | 第 5 步 | 切换脚本五条性质 |
| `build-matrix.svg` | 第 5 步 | 多形态构建矩阵 |
| `test-pyramid.svg` | 第 6 步 | 四层测试 |
| `deploy-topology.svg` | 第 7 步 | 五种交付形态 |
| `troubleshoot-tree.svg` | FAQ | 排障决策树 |
| `nuxt-logo.png` | 专题入口 | 官方 Logo（75% 居中） |

## 六、已知限制与未做项

如实列出，避免读者高估完成度：

| # | 限制 | 影响 | 后续 |
| --- | --- | --- | --- |
| 1 | **本仓不包含可运行的模板工程** | 无法 `git clone` 后直接 `pnpm dev` | 若要做成模板仓库，见第 7 步 §六 的四种交付方式 |
| 2 | 第 2、6、7 步的工程代码为**完整清单而非已提交文件** | 需要照文档自行落地 | 落地后按对应步骤的「验证方式」逐条验收 |
| 3 | 未在真实 Nuxt 工程里跑通 `pnpm build` | 构建期行为（尤其 Nuxt UI 的 Tailwind 4 CSS-first）未实测 | 首次落地时优先验证这一项 |
| 4 | 端到端用例只写了 2 条示例 | 三条关键路径里「表单提交」未给完整用例 | 落地时补齐第三条 |
| 5 | 契约用例集合示例为 2 个组件、10 条用例 | 真实项目通常 8~15 个契约组件 | 按业务实际用量扩展，并同步 `frozen.json` |
| 6 | Vuetify 实现层未实测 | 实验性，风险已知 | 升级该模块版本时一并验证 |

## 七、后续可做项

按「投入产出比」排序：

1. **把模板工程独立成仓**（对应第 7 步 §六）：`package.json` 加 `"ui:check"` / `"ui:set"` 脚本，提交初始生成物，仓库勾选 Template。
2. **补第三条端到端用例**：表单提交路径（命令式 API 在四个实现下的可用性差异最大）。
3. **给实现层加逃生口文档**：把「某个库缺能力时怎么在实现层适配」的三条纪律配上真实案例。
4. **扩展第 5 个实现层**：比如 Naive UI 或 PrimeVue，用来检验契约层的扩展成本——如果加一个实现只需新增一个目录加一行取值，说明契约层设计成立。
5. **把边界门禁从 shell grep 升级为脚本**：当前用 `grep -rnE` 实现，好处是零维护；若规则变复杂（需要忽略注释、允许白名单），再考虑独立成 `scripts/check-boundaries.mjs`。

## 八、这份记录怎么用

| 你的处境 | 建议先看 |
| --- | --- |
| 想判断这套设计值不值得抄 | §三 的五条性质与变异实验（结论有实测支撑） |
| 准备照着落地 | §六 的已知限制（尤其第 1、3 条） |
| 想改切换器 | §3.3 的四个真实 bug（尤其 marker 缩进那条） |
| 遇到了怪问题 | [FAQ](../FAQ/index.md) 的排障决策树 |

## 参考资料

- [Conventional Commits](https://www.conventionalcommits.org/zh-hans/)：本专题的文档变更按此规范提交
- [Nuxt](https://nuxt.com/docs)：版本基线的官方来源
- [Vitest](https://vitest.dev/)：测试运行器版本与迁移说明的官方来源
