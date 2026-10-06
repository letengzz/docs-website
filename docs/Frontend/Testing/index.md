# 前端测试

<p style="text-align:center;"><img src="./assets/testing-logo.png" style="zoom:75%;" /></p>

「前端测试」专题系统讲解 Web 前端项目的自动化测试体系：从单元测试（Jest / Vitest）、组件测试（Testing Library / Vue Test Utils）、端到端测试（Playwright / Cypress）到覆盖率统计与测试策略，帮助你把「测试」从口号变成 CI 里可执行的门禁。

## 目录

- [测试体系概述与选型](Overview/index.md)
- [Jest 单元测试](Jest/index.md)
- [Vitest 单元测试](Vitest/index.md)
- [组件测试：Testing Library 与 Vue Test Utils](ComponentTesting/index.md)
- [E2E 测试：Playwright 与 Cypress](E2E/index.md)
- [覆盖率统计与门禁](Coverage/index.md)
- [测试策略与 CI 集成](Strategy/index.md)
- [常见问题与最佳实践](FAQ/index.md)

## 相关专题

- [前端工程化](../Others/FrontendEngineering/index.md)：测试是工程化的一环，配合代码规范与 CI 使用
- [JavaScript 测试](../Basic/JavaScript/Testing/index.md)：语言层面的测试基础概念
- [React 测试](../Frame/React/Testing/index.md)、[Vue3](../Frame/Vue/Vue3/index.md)：框架专属测试实践

## 相关专题与分工

- [Selenium 端到端测试](../../Tools/TestingTools/Selenium/index.md)：本专题讲**前端的单元/组件测试与 Playwright E2E**，加上前端侧的覆盖率门禁与 CI 接法；该页讲 **Selenium + WebDriver BiDi 的跨浏览器端到端**——多浏览器矩阵怎么跑、显式等待与隐式等待的等待策略、POM（Page Object Model）分层怎么写。两者按技术栈分工：前端组件行为与单页应用主链路用本专题的 Playwright，需要覆盖多浏览器 / 多版本的端到端回归走该页，**同一批用例不重复造两遍**。
- [AI 编程助手](../../AI/AICodingAssistant/index.md)：AI 参与生成测试后，本专题的口径更要用起来——**契约由人定、用例由 AI 补**，警惕断言被改弱来迁就实现；评审清单里的「测试被改弱」一查见 [团队规范](../../AI/AICodingAssistant/TeamStandard/index.md)。
- [国际化与无障碍 · 无障碍测试与门禁](../IntlA11y/A11yTesting/index.md)：**分工是**——本专题讲用户行为的测试与覆盖率门禁（单测 / 组件测试 / Playwright E2E），该页讲**无障碍这一条专门的门禁线**：axe-core 的规则分级（只把 `serious` / `critical` 设为阻断）、自动化只能覆盖三到四成的现实、**防退化基线**（对比增量而非总量）怎么设计。两者共用同一套 Playwright 基础设施，但断言对象完全不同。
- [PWA 与离线应用](../PWA/index.md)：**分工是**——本专题讲「怎么测一个页面」；PWA 新增的是**两种不在页面内的被测对象**：Service Worker 的注册与激活（有没有、scope 对不对）、以及离线状态下的行为（断网后是兜底页还是白屏）。Playwright 侧的最小手段是 `context.setOffline(true)` + 断言「页面出现离线文案」，但**测不到**的东西也要写清楚：SW 的 `waiting` 与更新流程、`beforeinstallprompt`（`userChoice` 无法在自动化里点）、以及真实设备上的安装与推送。完整的判据与自动化边界见[实战](../PWA/Practice/index.md)的 P1~P10 与[常见问题](../PWA/FAQ/index.md)的上线自查清单。
