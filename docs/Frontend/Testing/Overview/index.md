# 前端测试体系概述与选型

前端测试是**用代码验证代码**的工程实践：把「手动点一遍页面」变成「一条命令跑完全部回归」。本页回答三个问题：测试分几层、每层用什么工具、新项目如何选型。适用于所有前端开发者，尤其是要为团队建立测试规范的人。

:::info 当前生态版本（2026-09 核对）
- Vitest **5.0**（2026-09-03 发布，Vite 生态默认选择）
- Jest **30.x**（存量项目仍占多数，Node 18.14+ / TS 5.4+）
- Playwright **1.63**、Testing Library jest-dom **7.x**
- Cypress 14/15.x（以[官网](https://www.cypress.io/)为准）
:::

## 测试金字塔：分层模型

前端测试通常按「测试金字塔（Testing Pyramid）」分层，越往下数量越多、速度越快、成本越低：

![测试金字塔](../assets/test-pyramid.svg)

| 层级 | 测试对象 | 典型工具 | 数量占比 | 反馈速度 |
| --- | --- | --- | --- | --- |
| 单元测试（Unit） | 纯函数、组合式函数、工具类 | Vitest / Jest | ~70% | 毫秒级 |
| 组件测试（Component） | 单个组件的渲染与交互 | Testing Library、Vue Test Utils | ~20% | 秒级 |
| 集成测试（Integration） | 多组件 + 路由 + 状态协作 | Vitest + Testing Library | 并入上两层 | 秒级 |
| E2E 测试（End-to-End） | 真浏览器里的完整用户流程 | Playwright / Cypress | ~10% | 分钟级 |

::: tip 一句话理解
单元测试保证「零件没问题」，组件测试保证「零件装起来没问题」，E2E 保证「整辆车能开到目的地」。
:::

## 工具全景与选型

### 单元/组件测试运行器

| 维度 | Vitest | Jest |
| --- | --- | --- |
| 定位 | Vite 原生测试运行器 | 通用 JS 测试框架（Meta 维护） |
| 构建 | 复用项目 Vite 配置（别名、插件、JSX/TS 开箱即用） | 需要 `jest-transform` + `moduleNameMapper` 单独配置 |
| 启动速度 | 快（esbuild 按需转译，支持 HMR 式 watch） | 较慢（转译整个依赖图） |
| ESM | 原生支持 | 30.x 改善明显但仍需 `--experimental-vm-modules` |
| API | 与 Jest 高度兼容（`describe/it/expect/vi.mock`） | 事实标准 |
| 适用 | Vite 项目（Vue3、React+Vite、库开发）首选 | 存量 Webpack/Babel 项目、老项目延续 |

::: tip 选型建议
新项目一律 **Vitest**（Vite 项目零配置成本）；存量 Jest 项目**不必迁移**——Jest 30 仍在积极维护，两者 API 几乎一致，团队技能可复用。
:::

### 组件测试查询/操作层

| 库 | 适用框架 | 理念 |
| --- | --- | --- |
| Testing Library（`@testing-library/react` / `vue`） | React / Vue / Svelte 等 | 以用户行为为中心，通过可访问性角色查询 |
| Vue Test Utils（`@vue/test-utils`） | Vue 专属 | 官方底层 API，可精确操作组件实例，偏实现细节 |

实践推荐：**查询与断言用 Testing Library，Vue 特有场景（emit、provide、插件挂载）用 Vue Test Utils 补充**。

### E2E 测试

| 维度 | Playwright | Cypress |
| --- | --- | --- |
| 浏览器 | Chromium / Firefox / WebKit 全支持（自研驱动） | Chromium 系为主（Firefox/WebKit 受限） |
| 并行 | 多进程并行，免费 CI 友好 | 依赖付费 Dashboard 做编排 |
| 语言 | TS / Python / Java / .NET | JS / TS |
| 调试 | Trace Viewer、codegen 录制 | Time Travel、界面直观 |
| 多 Tab/域 | 原生支持 | 历史限制较多 |
| 适用 | 新项目默认选择 | 存量项目、重调试体验团队 |

## 一个最小的分层示例

以「登录表单校验」为例看三层各测什么：

```ts
// 1. 单元测试：校验函数
// src/utils/validate.ts
export function validatePhone(phone: string): boolean {
  return /^1\d{10}$/.test(phone);
}
```

```ts
// src/utils/__tests__/validate.spec.ts（Vitest）
import { describe, it, expect } from "vitest";
import { validatePhone } from "../validate";

describe("validatePhone", () => {
  it("合法手机号返回 true", () => {
    expect(validatePhone("13800138000")).toBe(true);
  });
  it("10 位号码返回 false", () => {
    expect(validatePhone("1380013800")).toBe(false);
  });
});
```

```tsx
// 2. 组件测试：输入非法手机号时展示错误提示（Testing Library 思路）
render(<LoginForm />);
await userEvent.type(screen.getByRole("textbox", { name: /手机号/ }), "123");
await userEvent.click(screen.getByRole("button", { name: /登录/ }));
expect(screen.getByText("手机号格式不正确")).toBeVisible();
```

```ts
// 3. E2E 测试（Playwright）：真实走完登录流程
import { test, expect } from "@playwright/test";

test("用户可用正确账号登录", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("手机号").fill("13800138000");
  await page.getByLabel("密码").fill("pass1234");
  await page.getByRole("button", { name: "登录" }).click();
  await expect(page.getByText("欢迎回来")).toBeVisible();
});
```

## 验证方式

选型落地后应能通过以下检查：

1. `pnpm test` 能跑通全部单元/组件测试并输出汇总；
2. `pnpm test:e2e` 能拉起浏览器完成至少一条冒烟流程；
3. `pnpm coverage` 能生成覆盖率报告（详见[覆盖率统计与门禁](../Coverage/index.md)）。

## 易错点

::: danger 选型与分层的常见坑
1. **只有 E2E**：把所有验证塞进 E2E，导致回归一次 40 分钟、失败定位困难——按金字塔分层，E2E 只留主流程。
2. **新 Vite 项目硬上 Jest**：别名、`.vue` 文件、ESM 依赖处处报错——用 Vitest 直接复用 Vite 配置。
3. **测试内部实现**：断言组件内部 state 或私有方法，重构即全红——断言用户可见的行为与输出。
4. **追求 100% 覆盖率**：为凑数字写无断言的「快照刷行数」——覆盖率是门禁下限，不是目标（见[覆盖率](../Coverage/index.md)）。
:::

## 参考资料

- [Testing Pyramid - Martin Fowler](https://martinfowler.com/bliki/TestPyramid.html)
- [Vitest 官方文档](https://vitest.dev/)
- [Jest 官方文档](https://jestjs.io/)
- [Playwright 官方文档](https://playwright.dev/)
- [Testing Library 官方文档](https://testing-library.com/)
