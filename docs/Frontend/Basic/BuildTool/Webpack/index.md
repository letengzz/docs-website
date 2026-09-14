# Webpack

<p style="text-align:center;"><img src="./assets/webpack-logo.png" alt="Webpack" style="zoom:75%;" /></p>

Webpack 是一个**静态模块打包器**（module bundler）：它从入口出发递归构建依赖图，用 Loader 把各种类型的文件转换为模块，用 Plugin 干预整个构建过程，最终输出浏览器可用的静态资源。

本专题在原有单页基础上展开为完整主题，覆盖核心概念、配置、Loader 与 Plugin 原理、代码分割、构建优化、模块联邦、生产级配置与常见问题。

## 目录

### 入门

- [Webpack 概述与核心概念](Overview/index.md)
- [Webpack 配置详解](Config/index.md)

### 机制

- [Webpack Loader 详解](Loader/index.md)
- [Webpack Plugin 详解](Plugin/index.md)

### 进阶

- [Webpack 代码分割](CodeSplitting/index.md)
- [Webpack 构建优化](Optimize/index.md)
- [Webpack 模块联邦](ModuleFederation/index.md)

### 实战与排障

- [实战：生产级 Webpack 配置](Practice/index.md)
- [Webpack 常见问题与最佳实践](FAQ/index.md)

::: info 版本约定
本专题以 **Webpack 5** 为主线（当前 5.x 持续迭代，发布节奏稳定）。官方推荐的起步方式是 **webpack-cli 7**，它要求 **Node.js 20.9+** 与 **webpack 5.101+**，并默认通过动态 `import()` 加载配置文件，从而支持 Node 原生类型剥离读取 TypeScript 配置。

Webpack 4 及更早版本**保留说明并标注「仅存量项目使用」**，新项目不要采用。Webpack 5 的关键变化（持久化缓存、模块联邦、Asset Modules、移除 Node polyfill、确定性 chunk ID）见 [构建优化](Optimize/index.md)。
:::

::: tip 学习路径建议
先按「核心概念 → 配置 → Loader → Plugin」建立心智模型；再用「代码分割 → 构建优化」解决实际性能问题；「模块联邦」与「实战配置」按需查阅。与 Vite 的差异对照见 [Vite 概述与原理](../Vite/Overview/index.md)。
:::

## 各篇定位

| 页面 | 回答什么问题 |
| --- | --- |
| [Webpack 概述与核心概念](Overview/index.md) | Entry / Module / Chunk / Bundle 的关系与构建流程 |
| [Webpack 配置详解](Config/index.md) | 顶层字段职责、占位符、配置分层与验证方式 |
| [Webpack Loader 详解](Loader/index.md) | 执行顺序、常用 Loader、上下文 API 与自定义 Loader |
| [Webpack Plugin 详解](Plugin/index.md) | Tapable 钩子、compilation 能做什么、自定义插件 |
| [Webpack 代码分割](CodeSplitting/index.md) | 四种分割方式、splitChunks 参数与缓存友好原则 |
| [Webpack 构建优化](Optimize/index.md) | 持久化缓存、tree shaking、压缩、并行与分析 |
| [Webpack 模块联邦](ModuleFederation/index.md) | 运行时共享模块、微前端场景、代价与风险 |
| [实战：生产级 Webpack 配置](Practice/index.md) | common / dev / prod 三层配置与验证清单 |
| [Webpack 常见问题与最佳实践](FAQ/index.md) | 版本对齐、Node polyfill、hash 稳定与排障流程 |

## 相关专题

- [构建工具概述](../Overview/index.md)：Vite / Webpack / Rollup / esbuild 的横向对比与选型
- [Vite 深入](../Vite/index.md)：新项目的主流选择，与本专题互为对照
- [Rollup](../Rollup/index.md)：库项目打包的首选
- [esbuild](../esbuild/index.md)：极致快速的编译器与压缩器
- [前端工程化](../../../Others/FrontendEngineering/index.md)：Webpack 在工程体系中的定位
- [构建优化](../../../Others/FrontendEngineering/BuildOptimization/index.md)：分包、懒加载与体积分析
- [前端性能优化 · 构建优化](../../../Others/PerformanceOptimization/Build/index.md)：体积预算与产物评估
