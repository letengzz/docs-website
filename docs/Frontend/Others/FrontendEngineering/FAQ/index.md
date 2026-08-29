# 前端工程化常见问题与最佳实践

本页汇总前端工程化落地中最常遇到的坑：本地过 CI 挂、ESLint 与 Prettier 冲突、测试跑不起来、构建体积失控、Monorepo 依赖问题等，并给出生产级最佳实践清单。

## 本地能跑，CI 挂掉

| 差异 | 解法 |
| --- | --- |
| Node/pnpm 版本不同 | `package.json` 加 `engines`，CI 用 `actions/setup-node` 固定 |
| lockfile 未提交/过期 | 提交 lockfile，CI 用 `--frozen-lockfile` / `npm ci` |
| 大小写敏感 | 文件名大小写统一，CI 是 Linux |
| 环境变量缺失 | CI 中显式配置所有 `VITE_` 变量（含默认值） |
| 换行符 | `.editorconfig` 统一 `lf` |
| 时区/随机性 | 测试避免依赖本地时间与随机顺序 |

## ESLint 与 Prettier 冲突

```text
症状：Prettier 格式化后 ESLint 报格式错误
```

解法：安装 `eslint-config-prettier` 关掉冲突规则：

```js
import eslintConfigPrettier from 'eslint-config-prettier'

export default [...baseConfig, eslintConfigPrettier]
```

顺序：**先 Prettier 格式化，再 ESLint 查质量**；两者不要同时管格式。

## 测试运行不起来/不稳定

1. **jsdom 环境缺失**：组件测试需要 `environment: 'jsdom'`。
2. **TS 语法**：Vitest 用 esbuild 转译，`typescript` 需正确配置；`vi.mock` 必须在顶层。
3. **异步测试**：`await` 触发器/`flushPromises`，别用 setTimeout 猜测。
4. **随机失败**：并发测试共享状态 → 每个测试独立实例/mock。
5. **中文/编码**：文件统一 UTF-8。

## 构建产物太大

```text
首屏 JS > 500KB，加载慢
```

排查顺序：

1. `rollup-plugin-visualizer` 看最大 chunk 构成。
2. 大依赖是否全量引入（echarts/lodash）→ 按需。
3. 是否缺少分包 → manualChunks 拆分。
4. 页面是否懒加载 → 路由懒加载。
5. 是否开了 gzip/brotli → 服务器压缩。

## lint 很慢

1. `ignores` 排除 `dist`、`node_modules`、生成文件。
2. 本地只 lint 改动文件（lint-staged），CI 全量。
3. 升级到 ESLint 10 + typescript-eslint 新版本，性能更好。
4. 避免在每行都运行的规则里做重计算。

## Monorepo 依赖问题

```text
症状：共享包改动，其他 app 没生效
```

1. **符号链接**：pnpm workspace 默认链接，确认 `linkWorkspacePackages` 行为。
2. **构建顺序**：用 `pnpm --filter ... --filter ... build` 或 Turborepo 依赖图排序。
3. **版本不一致**：用 pnpm catalog 统一版本。
4. **重复依赖**：不同版本同库并存 → `pnpm why <pkg>` 排查，`pnpm dedupe`。

## Git 钩子不生效

1. Husky 9 用 `husky init` 生成 `.husky/`，确认脚本有执行权限。
2. `.git/hooks` 被 Husky 接管，检查 `core.hooksPath`。
3. `lint-staged` 找不到配置 → package.json 或 `.lintstagedrc`。
4. 在 CI 环境钩子不生效是正常的，CI 全量检查兜底。

## 前端工程化最佳实践清单

::: tip 工程化十诫
1. 规范进 CI：lint 0 警告、typecheck 通过、覆盖率 ≥ 80%。
2. 提交信息走 Conventional Commits，历史可读可自动生成 CHANGELOG。
3. 本地钩子快而准（只查暂存），CI 全量兜底。
4. 测试金字塔：单测 70%+、组件测试、E2E 保核心流程。
5. 构建产物 hash + CDN 长缓存，index.html 不缓存。
6. 同一制品从 PR 验证到生产发布，禁止重新构建。
7. 环境变量 `VITE_` 前缀 + `.env.example`，密钥绝不进客户端。
8. 模板工程统一结构，新项目开箱即用。
9. Monorepo 用 pnpm workspace + catalog 管版本。
10. 定期复盘构建时长、测试时长、CI 失败率，持续优化。
:::

## 验证方式

1. 对照十诫给自己的项目打分，找出最薄弱的三项。
2. 做一次“断 CI”演练：本地注释一个测试，确认 CI 标红、PR 被阻断。
3. 统计一次 PR 全流程耗时（提交 → 合并 → 预览），设定优化目标。

## 参考资料

- Vite 故障排查：https://vitejs.dev/guide/troubleshooting.html
- ESLint 迁移到 flat config：https://eslint.org/docs/latest/use/configure/migration-guide
- pnpm 排障：https://pnpm.io/zh/troubleshooting
- 本专题章节入口：[前端工程化目录](../index.md)
