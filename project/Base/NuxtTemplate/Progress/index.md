# 进展记录

## 一、这次是「重做」而不是「新建」

本专题此前已有一版实现，走的是**「把 UI 组件库做成可替换零件」**的路线：业务层 → 契约层 → 实现层 → 组件库，靠构建期 alias 在 Element Plus / Ant Design Vue / Nuxt UI / Vuetify 之间切换，换库只改生成物里的一行。

那版方案在评审中被判定为**方案偏移**，原因是它的重心落在了「运行期可切换」——而这个能力带来的复杂度（契约组件、适配器、令牌桥接、切换脚本、多形态构建）与它的实际价值不成比例：

| | 旧方案（可插拔运行时） | 新方案（一次性自举初始化） |
| --- | --- | --- |
| 换技术栈 | 运行期改一行 + 跑脚本，契约层永久保留 | 初始化时选一次，之后不存在「切换」这个概念 |
| 仓库里的抽象层 | 契约层 + 实现层 + 令牌桥接（长期维护成本） | 无（产物就是普通 Nuxt 工程） |
| 用户第一步 | clone 后读文档理解契约 | clone 后 `pnpm dev`，网页上点选 |
| 自测对象 | 切换脚本（逐字节正确） | 初始化引擎（逐字节正确） |
| 代价 | 抽象层永远在，业务代码要迁就契约 | 选择页要能自删干净 |

结论：**把复杂度从「产物」挪到「初始化过程」**。产物回到一个任何人都能接手的普通 Nuxt 工程，而复杂性集中在一次性的、可预演可回滚的引擎里。旧目录已整体删除（31 个文件），本专题按新方案重建。

## 二、本次产出

| 步骤 | 页面 | 行数 | 配图 |
| --- | --- | --- | --- |
| — | [`index.md`](../index.md)（专题入口，含 Logo） | 196 | `template-lifecycle.svg` |
| 0 | [`Requirement/`](../Requirement/index.md) 需求与方案定位 | 151 | `initializr-forms.svg` |
| 1 | [`Bootstrap/`](../Bootstrap/index.md) 零依赖引导期骨架 | 397 | `bootstrap-structure.svg`、`pure-css-baseline.svg` |
| 2 | [`WizardFrontend/`](../WizardFrontend/index.md) 引导页：信息架构与选择模型 | 331 | `wizard-layout.svg`、`option-model.svg` |
| 3 | [`WizardBackend/`](../WizardBackend/index.md) 引导器服务端与安全边界 | 358 | `wizard-api-sequence.svg` |
| 4 | [`InitEngine/`](../InitEngine/index.md) 初始化引擎：自删除与依赖安装 | 442 | `init-pipeline.svg`、`self-delete-scope.svg` |
| 5 | [`StackMatrix/`](../StackMatrix/index.md) 技术栈矩阵与组合兼容 | 226 | `stack-matrix.svg` |
| 6 | [`AppBaseline/`](../AppBaseline/index.md) 初始化后的应用基线 | 389 | `app-layers.svg` |
| 7 | [`Quality/`](../Quality/index.md) 质量门禁与自测 | 359 | `gates-chain.svg` |
| 8 | [`Build/`](../Build/index.md) 构建与产物形态 | 187 | `build-artifacts.svg` |
| 9 | [`Deployment/`](../Deployment/index.md) 部署与上线 | 346 | `deploy-topology.svg` |
| 10 | [`Acceptance/`](../Acceptance/index.md) 验收与上线检查 | 285 | `acceptance-flow.svg` |

合计 **12 页 / 3667 行 / 15 张 SVG / 1 张官方 Logo**（不含本篇）。

## 三、每一步的验收方式

| 步骤 | 怎么确认这一步是对的 |
| --- | --- |
| 0 需求 | 三条硬约束各自能被写成命令：引导期能跑、产物可复现、引导器残留 0 |
| 1 骨架 | `pnpm list --prod --depth 0` 只输出一行 `nuxt`；`pnpm dev` 打开 `/setup` 无 console error |
| 2 引导页 | 制造 `Nuxt UI + UnoCSS` 冲突 → 按钮必须禁用；改回 Tailwind → 冲突消失且提示降级为 info |
| 3 服务端 | 未带令牌 403、非法枚举 400、阻断冲突 422、生产构建后 `/api/wizard/schema` 返回 404 |
| 4 引擎 | `--dry-run` 两次输出 `diff` 为空；真跑后 `verify.mjs` 12/12；手工制造漂移后 `--check` 返回 1 |
| 5 矩阵 | 176 种有效组合全矩阵 `--dry-run` 通过；12 条规则逐条命中测试 |
| 6 基线 | 首页能看到令牌色板与技术栈摘要；`curl /about` 能拿到 SSR 直出的内容 |
| 7 门禁 | 每条门禁配一个变异实验，改坏一格必须报红 |
| 8 构建 | `pnpm build && pnpm preview` 首屏正常；`.output` 中 grep 不到 `wizard` |
| 9 部署 | 镜像非 root、`docker stop` 秒级退出、运行期变量改值生效 |
| 10 验收 | `--strict` 在签名前**必须**返回 1（设计如此），签名后返回 0 |

## 四、版本事实（2026-10-01 核对）

| 事实 | 结论 | 来源 |
| --- | --- | --- |
| Nuxt 当前稳定版 | **4.5.2**（2026-08-05，安全补丁） | Nuxt 官方发布记录 / 版本追踪 |
| Nuxt 3 状态 | **2026-07-31 已 EOL** | Nuxt 4.5 发布公告 |
| Nuxt 4.5 的关键变化 | Vite 8、Rspack 2（Rsbuild）、实验性 SSR streaming、稳定错误码体系、`useLayout`、named views，并为 Nuxt 5 铺路 | Nuxt 官方 blog |
| Node.js | 24 为 **Active LTS**；22 为 Maintenance LTS；26 为 Current（2026-10 转 LTS） | Node.js 官方发布日程 |
| pnpm | **11.x**（v11 起不再读 `package.json` 的 `pnpm` 字段，`strictDepBuilds` 默认开启） | pnpm 发布说明 |
| Element Plus | 2.14.x（2.14.6 / 2026-09-18） | 官方 changelog |
| Ant Design Vue | 4.2.x | 生态统计（2026-07） |
| Nuxt UI | **4.11.0**（2026-08-21），要求 Nuxt ≥ 4.1，`tailwindcss` 为独立 peer 依赖 | 官方 release note |
| Vuetify | 4.x（Material Design 3）；`vuetify-nuxt-module` 仍为 **1.0.0-rc** 线 | 模块仓库发布记录 |
| Tailwind CSS | 4.3.x，CSS-first（`@theme`），无 `tailwind.config.js` | 官方文档 |
| UnoCSS | 66.10.x；`preset-uno` / `preset-wind` 已在 66.0.0 更名为 `preset-wind3` | 官方 presets 文档 |
| Dart Sass | 1.105.0（2026-09-22），推荐 `sass-embedded` | sass-lang / 发行记录 |
| Vitest | 4.1.x（最新 4.1.11）；5.0 仅有 rc，**暂缓** | npm dist-tag 记录 |
| `@nuxt/test-utils` | 4.x（4.0.0 起要求 Vitest v4，环境初始化移到 `beforeAll`） | 4.0.0 发布说明 |

::: info 三条被纠正的常见说法
1. **「Nuxt 3 还能用」**——2026-07-31 起 OSS 支持已结束，新项目不应以 3.x 为基线。
2. **「装 `@nuxt/ui` 就够了」**——还需自己装 `tailwindcss`，并在 CSS 入口写 `@import "tailwindcss"; @import "@nuxt/ui";` 两行；少任何一步都是**静默失效**（组件渲染但没有样式）。
3. **「UnoCSS 用 `preset-uno`」**——该包已更名为 `preset-wind3`，旧包仍发布且不报弃用警告，照抄旧教程不会报错但语义已过时。
:::

## 五、落地与验证（2026-10-02 补记）

引擎与自测已落地在**独立仓库**（本仓是文档库，不放脚本），并按每页的「验证方式」在本机实跑过：

| 验证项 | 命令 | 实测结果 |
| --- | --- | --- |
| 引擎自测 | `node scripts/selftest.mjs` | **76/76 通过**（A~H 九组，含变异测试），耗时 9 秒 |
| 全矩阵扫描 | `node scripts/matrix.mjs --dry-run-all` | 名义 240 / 有效 **176** / 阻断 64；扫描通过 176、失败 0 |
| 产物复核 | `node scripts/verify.mjs` | 12 项断言全部符合预期（跳过 2 项耗时段），引导器残留 0 |
| 门禁清单 | `node scripts/run-gates.mjs` | 模板本体上 2 条 PASS、5 条 BLOCKED（未初始化，属预期） |
| 真跑一次初始化 | `node scripts/init.mjs --skip-install --fast` | 删除 22 / 生成 15 / 覆盖 2，`--check` 连跑两次仍为 0 漂移 |

**仍未验证的部分**（诚实登记）：

| # | 项 | 现状 |
| --- | --- | --- |
| 1 | 依赖安装阶段 | 本机 `registry.npmjs.org` 不可达，**未跑通**；引擎会打印可粘贴的补齐命令，网络恢复后需补跑一次完整 `verify` 12/12 |
| 2 | 端到端流程 | 浏览器点选 → 初始化 → 新工程起服务，未实测（暂无 Playwright 用例） |
| 3 | 体积预算基线 | 预算值仍按经验给出，未用真实组合构建回填 |

## 六、下一步

1. **补跑完整安装**（最优先）：网络恢复后跑一次带安装的初始化，把 `verify` 第 11 项从 SKIP 变成 PASS。
2. **端到端验收**：用一个真实组合（Element Plus + Sass + 无原子化 + SSR + Pinia + ESLint + 测试）从 clone 到 `pnpm dev` 走完整流程，并接入 [验收](../Acceptance/index.md) 的 AUTO 项。
3. **体积预算回填**：用三个典型组合构建后记录实测体积，把预算值换成实测值。
4. **部署验证**：用 Docker 形态部署一次，跑 `smoke.sh`。

## 七、相关

- 专题入口：[Nuxt 通用模板](../index.md)
- 需求与取舍：[需求与方案定位](../Requirement/index.md)
- 另一条技术路线：[后端通用模板 · 模板 CLI](../../BackendTemplate/TemplateCli/index.md)（生成器 vs 自举的对照）
- 框架层背景：[Nuxt 全栈开发](../../../../docs/Frontend/Frame/Nuxt/index.md)
