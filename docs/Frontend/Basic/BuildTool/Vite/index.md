# Vite

<p style="text-align:center;"><img src="./assets/vite-logo.png" alt="Vite" style="zoom:75%;" /></p>

Vite（法语「快」，读作 `/viːt/`）是新一代前端构建工具。它由两部分组成：一个基于**浏览器原生 ES 模块**的开发服务器，以及一套基于 **Rolldown**（Rust 实现的打包器）的生产构建命令。相比 Webpack 的「先打包再启动」，Vite 在开发期**按需编译**，因此启动与热更新快得几乎无感。

本专题在原有单页基础上展开为完整主题，覆盖原理、环境、配置、环境变量、插件开发、构建优化、版本迁移与实战配置。

## 目录

### 入门

- [Vite 概述与原理](Overview/index.md)
- [Vite 环境与项目创建](Environment/index.md)

### 配置

- [Vite 配置详解](Config/index.md)
- [Vite 环境变量与模式](EnvVariables/index.md)

### 进阶

- [Vite 插件开发](Plugin/index.md)
- [Vite 构建优化](BuildOptimize/index.md)
- [Vite 版本演进与迁移](Migration/index.md)

### 实战与排障

- [实战：生产级 Vite 配置](Practice/index.md)
- [Vite 常见问题与最佳实践](FAQ/index.md)

::: info 版本约定
本专题以 **Vite 8**（当前稳定线）为主线。Vite 8 于 2026-03-12 发布，最大变化是把开发期的 esbuild 与生产期的 Rollup **统一为 Rust 实现的 Rolldown**，并内置 Oxc 编译器。Node.js 要求为 **20.19+ 或 22.12+**（与 Vite 7 相同），原因是需要原生支持 `require(esm)` 以便以 ESM-only 形式分发。Vite 5/6/7 的差异与迁移要点见 [版本演进与迁移](Migration/index.md)，旧版本说明**保留并标注状态**，不覆盖。
:::

::: tip 学习路径建议
按「概述 → 环境 → 配置 → 环境变量」跑通一个项目，再学「插件开发」与「构建优化」；真正遇到构建瓶颈时再看「版本迁移」与「实战配置」。示例以 Vue 为主，但 Vite 与框架无关，React / Svelte / 纯 TS 的配置方式完全一致。
:::

## 各篇定位

| 页面 | 回答什么问题 |
| --- | --- |
| [Vite 概述与原理](Overview/index.md) | 为什么快、No-Bundle 与依赖预构建是怎么回事 |
| [Vite 环境与项目创建](Environment/index.md) | Node 版本要求、脚手架创建、目录结构 |
| [Vite 配置详解](Config/index.md) | `vite.config` 常用字段、别名、代理与条件配置 |
| [Vite 环境变量与模式](EnvVariables/index.md) | `.env` 文件、`import.meta.env`、mode 与类型声明 |
| [Vite 插件开发](Plugin/index.md) | 插件钩子、虚拟模块、与 Rollup 插件的关系 |
| [Vite 构建优化](BuildOptimize/index.md) | 分包、压缩、体积分析与产物诊断 |
| [Vite 版本演进与迁移](Migration/index.md) | 各大版本变化、从 Webpack 迁移的步骤与坑 |
| [实战：Vite 生产工程配置](Practice/index.md) | 一套可直接上生产的分层配置 |
| [Vite 常见问题与最佳实践](FAQ/index.md) | 依赖预构建、HMR、路径与部署类问题速查 |

## 相关专题

- [构建工具概述](../Overview/index.md)：Vite / Webpack / Rollup / esbuild 的横向对比与选型
- [Webpack 深入](../Webpack/index.md)：老项目仍在使用的打包器
- [esbuild](../esbuild/index.md)：Vite 曾用于开发期转换的高速编译器
- [Rollup](../Rollup/index.md)：Vite 生产构建的兼容目标与插件 API 来源
- [前端工程化](../../../Others/FrontendEngineering/index.md)：Vite 在工程体系中的定位
- [构建优化](../../../Others/FrontendEngineering/BuildOptimization/index.md)：分包、懒加载与体积分析
- [前端性能优化 · 构建优化](../../../Others/PerformanceOptimization/Build/index.md)：体积预算与产物评估
