# UmiJS 概述

UmiJS 是一个企业级的 React 前端框架，由蚂蚁集团开发并维护。它提供了一站式的解决方案，集成了路由、构建、部署、测试等功能。它通过约定式的目录结构和配置方式，减少了开发者的配置工作，同时提供了丰富的插件系统来扩展功能。

- 官网：https://umijs.org/
- 中文网：https://umijs.org/zh-CN

## 核心特性

### 开箱即用

UmiJS 内置了开发中常用的功能，无需额外配置即可使用：

- 路由系统（约定式路由和配置式路由）
- 构建系统（支持 Webpack 和 Vite 双引擎）
- 开发服务器（支持热更新）
- 代码分割和懒加载
- TypeScript 支持
- CSS 预处理器支持
- MFSU V3（默认开启，极速编译）

### 插件化架构

UmiJS 采用插件化架构，所有功能都通过插件实现：

- 核心功能由官方插件提供
- 支持自定义插件扩展功能
- 插件之间可以相互依赖
- 按需启用所需插件

::: tip UmiJS 4.x 变化
在 UmiJS 4.x 中，一些之前版本默认启用的插件规则需要显式配置，以减少"黑盒"行为。例如：

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  model: {},        // 数据流插件
  antd: {},         // Ant Design 集成
  request: {},      // 请求封装
  initialState: {}, // 初始状态
  mock: {},         // Mock 数据
})
```
:::

### 约定优于配置

UmiJS 遵循约定优于配置的原则：

- 约定式路由：根据文件目录自动生成路由
- 约定式目录结构：标准的项目结构
- 约定式配置：默认配置满足大部分需求

### 企业级支持

UmiJS 内置了企业级应用常用的功能：

- 权限管理（路由权限、组件权限）
- 国际化（多语言支持）
- 数据流（内置简易数据流方案）
- 布局系统（全局布局、路由布局）
- Mock 数据（本地 Mock 服务）

### 多构建引擎

UmiJS 4.x 同时支持 Vite 和 Webpack 两种构建方式，并尽量确保它们之间功能的一致性，让开发者可以通过一行配置进行切换。

```typescript [.umirc.ts]
import { defineConfig } from 'umi'

export default defineConfig({
  // 使用 Vite 构建
  vite: {},
  
  // 或使用 Webpack（默认）
  // webpack: {},
})
```

## 与其他框架对比

| 特性 | UmiJS 4 | Next.js | Create React App |
|------|---------|---------|------------------|
| 路由方式 | 约定式/配置式 | 文件系统路由 | 需手动配置 |
| 构建工具 | Webpack/Vite | Webpack | Webpack |
| SSR 支持 | 支持 | 支持 | 不支持 |
| SSG 支持 | 支持 | 支持 | 不支持 |
| 插件系统 | 完善 | 有限 | 无 |
| 企业级功能 | 内置 | 需自行集成 | 需自行集成 |
| 学习曲线 | 中等 | 中等 | 低 |
| 生态 | 蚂蚁生态 | Vercel 生态 | React 官方 |
| MFSU 加速 | 支持（V3） | 不支持 | 不支持 |

## 适用场景

### 适合使用 UmiJS 的场景

- 企业级后台管理系统
- 中大型 React 应用
- 需要快速原型开发的项目
- 需要 SSR/SSG 的内容型网站
- 需要权限管理、国际化等企业级功能的项目
- 使用 Ant Design 组件库的项目

### 不适合使用 UmiJS 的场景

- 简单的单页面应用（可能过于重量级）
- 需要高度自定义构建流程的项目
- 非 React 技术栈的项目

## 版本历史

### Umi 4.x（当前版本）

- 默认支持 React 18
- 支持 Vite 和 Webpack 双构建引擎
- MFSU V3 默认开启，编译速度大幅提升
- 改进的插件系统，需要显式配置
- 更好的 TypeScript 支持
- 性能优化和开发体验提升

### Umi 3.x

- 引入配置式路由
- 改进的插件系统
- 内置数据流方案
- 更好的国际化支持

### Umi 2.x

- 基于 React 16
- 约定式路由
- 插件化架构
- 企业级功能集成

## 学习资源

- [UmiJS 官方文档](https://umijs.org/)
- [UmiJS GitHub](https://github.com/umijs/umi)
- [UmiJS 插件市场](https://umijs.org/plugins)
- [Ant Design](https://ant.design/) - 与 UmiJS 配合良好的 UI 组件库
- [Ant Design Pro](https://pro.ant.design/) - 基于 UmiJS 的企业级中后台解决方案
