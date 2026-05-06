# Uniapp 概述与安装

## Uniapp 简介

Uniapp 是由 DCloud（数字天堂）推出的跨平台开发框架，使用 Vue.js 语法编写，一套代码可同时发布到 iOS、Android、Web、以及各种小程序（微信/支付宝/百度/抖音/QQ/飞书等）和快应用等多个平台。

### Uniapp 核心特性

- **跨平台开发**：一套代码编译到多个平台
- **Vue.js 语法**：使用 Vue 3 组合式 API 或选项式 API
- **原生渲染**：编译为各平台原生组件，性能优异
- **丰富生态**：插件市场提供大量组件和模板
- **热更新**：支持应用内热更新
- **云开发**：uniCloud 提供一站式后端服务

### 支持平台

| 平台 | 说明 |
|------|------|
| H5 | 移动端网页和 PC 网页 |
| 微信小程序 | 微信生态小程序 |
| 支付宝小程序 | 支付宝生态小程序 |
| 百度小程序 | 百度生态小程序 |
| 抖音小程序 | 字节跳动生态小程序 |
| QQ 小程序 | QQ 生态小程序 |
| 快手小程序 | 快手生态小程序 |
| 京东小程序 | 京东生态小程序 |
| App | iOS 和 Android 原生应用 |
| 快应用 | 安卓快应用 |

## 环境要求

- **Node.js**：推荐 v18.x 或更高版本
- **包管理器**：npm / yarn / pnpm
- **代码编辑器**：推荐 VS Code 或 HBuilderX

## 安装方式

### 方式一：使用 HBuilderX（推荐）

HBuilderX 是 DCloud 官方推出的 IDE，内置 uniapp 开发环境：

1. 下载并安装 [HBuilderX](https://www.dcloud.io/hbuilderx.html)
2. 打开 HBuilderX，选择 文件 → 新建 → 项目
3. 选择 uni-app 项目模板
4. 填写项目名称和路径
5. 点击创建

### 方式二：使用 Vue CLI

```bash [终端]
npm install -g @vue/cli
vue create -p dcloudio/uni-preset-vue my-uniapp
```

### 方式三：使用 Vite（推荐）

```bash [终端]
npx degit dcloudio/uni-preset-vue#vite my-uniapp
cd my-uniapp
npm install
```

## 项目运行

### H5 平台

```bash [终端]
npm run dev:h5
```

### 微信小程序

```bash [终端]
npm run dev:mp-weixin
```

打开微信开发者工具，导入 `dist/dev/mp-weixin` 目录。

### App 平台

在 HBuilderX 中运行到手机或模拟器。

## 项目发布

```bash [终端]
# H5
npm run build:h5

# 微信小程序
npm run build:mp-weixin

# App
在 HBuilderX 中点击 发行 → 原生 App 打包
```

## Uniapp 与原生开发对比

| 维度 | Uniapp | 原生开发 |
|------|--------|----------|
| 开发效率 | 高，一套代码多端 | 低，每端独立开发 |
| 性能 | 接近原生 | 最优 |
| 学习成本 | 低，Vue 语法 | 高，需掌握多端技术 |
| 生态 | 丰富，插件市场 | 各平台独立生态 |
| 适用场景 | 中小型应用、快速迭代 | 大型应用、极致性能要求 |

## Uniapp 与 Taro 对比

| 维度 | Uniapp | Taro |
|------|--------|------|
| 语法 | Vue | React/Vue |
| 出品方 | DCloud | 京东 |
| App 支持 | 原生渲染 | WebView 渲染 |
| 小程序支持 | 全面 | 全面 |
| IDE | HBuilderX | 任意编辑器 |
| 云开发 | uniCloud | 需自行搭建 |
