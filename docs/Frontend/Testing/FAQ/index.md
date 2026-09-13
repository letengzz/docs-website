# 常见问题与最佳实践

汇总前端测试落地时的高频问题（选型、工具报错、稳定性、团队协作）与可直接执行的最佳实践清单。前序页面：[概述](../Overview/index.md)、[Jest](../Jest/index.md)、[Vitest](../Vitest/index.md)、[组件测试](../ComponentTesting/index.md)、[E2E](../E2E/index.md)、[覆盖率](../Coverage/index.md)、[测试策略](../Strategy/index.md)。

## 选型类

### 新项目选 Vitest 还是 Jest？

Vite 构建的项目选 **Vitest**：别名、插件、TS/JSX 直接复用，不用维护两套管线。存量 Jest 30 项目不必迁移，两者 API 兼容，团队技能互通。判据只有一个：**你的构建工具是不是 Vite**。

### E2E 选 Playwright 还是 Cypress？

新项目默认 **Playwright**（1.63+）：三内核、免费并行、Trace 调试。已深度使用 Cypress 且依赖其 Dashboard 编排的团队继续用 Cypress，不要为了「新」重写全部用例。

### 要不要测内部实现（state、私有方法）？

不要。测试应该**面向行为**：用户看到什么、触发什么、发生什么变化。断言内部实现的测试在重构时必然全红，反而拖慢迭代。

## 工具报错类

### Vitest：`ReferenceError: test is not defined`

两种解法：在文件头 `import { test, expect } from "vitest"`；或在配置开启 `globals: true` 并给 `tsconfig` 加 `"types": ["vitest/globals"]`。

### Vitest：`environment "jsdom" not found` / coverage 命令报错

缺依赖包：`pnpm add -D jsdom`（或 `happy-dom`）、`pnpm add -D @vitest/coverage-v8`。

### Vitest：`vi.mock` 之后拿到的是 undefined

1. 路径必须与被测模块 import 的路径一致（相对当前测试文件解析）；
2. 工厂函数要返回**完整的导出对象**：
   ```typescript
   vi.mock("../api", () => ({ fetchUser: vi.fn() })); // 命名导出都要列出
   ```
3. 需要保留真实实现时用 `vi.importActual` 组合部分 Mock。

### React 测试：`Warning: An update to X inside a test was not wrapped in act(...)`

说明有状态更新发生在 React 追踪之外。优先用 `userEvent`（内部自动包 act）；自己异步触发时用 `await act(async () => { ... })`。另外检查是否忘了 `await` 交互调用。

### Vue 测试：`trigger("click")` 后断言失败

`trigger` 返回 Promise，必须 `await`：`await wrapper.find("button").trigger("click")`，否则 DOM 尚未更新就断言。

### Playwright：本地通过、CI 全红

按序排查：

1. CI 是否执行了 `pnpm exec playwright install --with-deps`；
2. 是否配置了 `webServer`（或流水线先起服务）；
3. CI 机器慢，超时是否过短（默认 30s，可加到 60s）；
4. 时区/语言差异导致文案断言失败——断言用 `data-testid` 或稳定文案。

## 稳定性（Flaky）类

### 测试偶尔失败怎么办？

1. 复跑定位：`vitest run --retry 3` 或 Playwright `--retries` 只是止血；
2. 用 Trace（Playwright）或失败截图还原现场；
3. 根因通常是三类：**硬等待**（改 web-first 断言）、**测试间共享状态**（每例重置 storage/localStorage，`storageState` 隔离）、**真实网络**（`page.route` 或 MSW Mock）。

### 如何断言「不出现」某元素？

- 组件测试：`expect(screen.queryByText("加载中")).not.toBeInTheDocument()`（`queryBy` 不抛错）；
- Playwright：`await expect(page.getByText("错误")).toBeHidden()` 或 `toHaveCount(0)`，避免用 `waitForTimeout` 猜时间。

## 实践清单

::: tip 上线前自查（可直接当 Code Review 清单用）
1. 测试文件与源码同目录（`__tests__/`），命名 `*.spec.ts`；
2. 每个测试独立可跑、可单独跑，不依赖执行顺序；
3. 断言面向用户可见行为，无内部 state 断言；
4. 外部依赖（网络、定时器、storage）全部 Mock；
5. 没有裸 `setTimeout` / `waitForTimeout` 硬等待；
6. 一个测试只验证一件事，失败信息能直接定位原因；
7. `pnpm test:ci` 在 CI 绿色且时长 < 5 分钟（不含 E2E）；
8. 覆盖率门禁生效（全量或 diff 阈值），无人为绕过。
:::

### 命名与组织

```text
src/
├─ utils/
│  ├─ format.ts
│  └─ __tests__/format.spec.ts      # 单元测试与源码就近
├─ components/
│  └─ Counter/
│     ├─ Counter.vue
│     └─ __tests__/Counter.spec.ts  # 组件测试
e2e/                                # E2E 独立目录，不混入 src
```

### 测试用例模板

```typescript
// 结构：准备（Arrange）→ 执行（Act）→ 断言（Assert）
test("手机号输入 10 位时展示格式错误提示", async () => {
  // Arrange
  const user = userEvent.setup();
  render(<LoginForm />);
  // Act
  await user.type(screen.getByLabelText("手机号"), "1380013800");
  await user.click(screen.getByRole("button", { name: "登录" }));
  // Assert
  expect(screen.getByText("手机号格式不正确")).toBeInTheDocument();
});
```

用例名推荐中文描述「**条件 + 预期**」，失败输出即可读：`✓ 手机号输入 10 位时展示格式错误提示`。

## 参考资料

- [Vitest FAQ](https://vitest.dev/guide/improving-performance.html)
- [Writing Tests - Testing Library](https://testing-library.com/docs/writing-tests)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Google Testing Blog: Flaky Tests](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)
