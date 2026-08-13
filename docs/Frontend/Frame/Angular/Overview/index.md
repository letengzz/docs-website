# Angular 概述与安装

## Angular 简介

Angular 是由 Google 开发的一个完整的前端框架，自 2016 年发布 Angular 2（完全重写）以来，已经成为企业级应用开发的主流选择之一。Angular 采用 TypeScript 作为开发语言，提供了从路由、表单处理到 HTTP 客户端等一整套解决方案。

截止 2026 年，Angular 最新稳定版本为 **Angular 20**，带来了 Signals 全面稳定、新的控制流语法、独立组件等重大更新。

### Angular 核心特性

- **完整的框架**：内置路由、表单、HTTP 客户端、动画等模块
- **TypeScript 原生支持**：强类型、接口、装饰器
- **依赖注入**：强大的 DI 系统，便于测试和模块化管理
- **组件化架构**：基于组件的 UI 构建方式
- **双向数据绑定**：通过 `[(ngModel)]` 实现视图与模型同步
- **RxJS 集成**：强大的响应式编程支持
- **CLI 工具**：官方命令行工具，简化开发流程
- **Signals**：Angular 16+ 引入的细粒度响应式系统

### Angular 与 React/Vue 对比

| 特性 | Angular | React | Vue |
|------|---------|-------|-----|
| 类型 | 完整框架 | UI 库 | 渐进式框架 |
| 语言 | TypeScript | JSX/TSX | 模板/TSX |
| 数据绑定 | 双向绑定 | 单向数据流 | 双向绑定（v-model） |
| 状态管理 | Services/RxJS | Context/Redux/Zustand | Pinia/Vuex |
| 学习曲线 | 较陡 | 中等 | 较低 |
| 适合场景 | 企业级应用 | 通用 | 中小型项目 |
| 包体积 | 较大 | 中等 | 较小 |
| 渲染机制 | 增量 DOM | 虚拟 DOM | 虚拟 DOM + 编译器 |

## 环境要求

在开始 Angular 项目之前，请确保开发环境满足以下要求：

- **Node.js**：推荐 v20.x 或更高版本
- **包管理器**：npm / yarn / pnpm
- **Angular CLI**：全局安装 `@angular/cli`
- **代码编辑器**：推荐 VS Code + Angular Language Service 扩展

## 安装 Angular CLI

```bash [终端]
npm install -g @angular/cli
```

验证安装：

```bash [终端]
ng version
```

## 创建 Angular 项目

### 使用 Angular CLI

```bash [终端]
ng new my-angular-app
```

创建时会提示选择：

- **样式表格式**：CSS / SCSS / SASS / LESS
- **是否启用 SSR**：是 / 否
- **是否使用 Standalone 组件**：是（推荐）

### 项目结构

一个标准的 Angular 项目结构如下：

```text
my-angular-app/
├── src/
│   ├── app/
│   │   ├── components/      # 自定义组件
│   │   ├── services/        # 服务
│   │   ├── guards/          # 路由守卫
│   │   ├── interceptors/    # HTTP 拦截器
│   │   ├── models/          # 数据模型
│   │   ├── pipes/           # 自定义管道
│   │   ├── directives/      # 自定义指令
│   │   ├── app.component.ts # 根组件
│   │   ├── app.component.html
│   │   ├── app.component.scss
│   │   ├── app.config.ts    # 应用配置
│   │   └── app.routes.ts    # 路由配置
│   ├── assets/              # 静态资源
│   ├── environments/        # 环境配置
│   ├── index.html           # HTML 模板
│   ├── main.ts              # 入口文件
│   └── styles.scss          # 全局样式
├── angular.json             # Angular 配置
├── tsconfig.json            # TypeScript 配置
├── package.json             # 项目依赖
└── tsconfig.app.json        # 应用 TypeScript 配置
```

### 入口文件示例

```typescript [src/main.ts]
import { bootstrapApplication } from '@angular/platform-browser'
import { AppComponent } from './app/app.component'
import { appConfig } from './app/app.config'

bootstrapApplication(AppComponent, appConfig)
  .catch(err => console.error(err))
```

## Angular 核心概念

### 组件（Component）

Angular 应用由组件构成，每个组件包含：

```typescript [src/app/app.component.ts]
import { Component } from '@angular/core'

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'My Angular App'
}
```

### 模块（NgModule）

Angular 15+ 推荐使用 Standalone 组件，不再强制需要 NgModule：

```typescript [src/app/app.config.ts]
import { ApplicationConfig } from '@angular/core'
import { provideRouter } from '@angular/router'
import { routes } from './app.routes'

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes)
  ]
}
```

### 依赖注入

Angular 内置强大的依赖注入系统：

```typescript [src/app/services/user.service.ts]
import { Injectable, inject } from '@angular/core'
import { HttpClient } from '@angular/common/http'

@Injectable({ providedIn: 'root' })
export class UserService {
  private http = inject(HttpClient)

  getUsers() {
    return this.http.get('/api/users')
  }
}
```

## Signals（响应式系统）

Angular 16+ 引入 Signals，提供更细粒度的响应式更新：

```typescript [src/app/components/counter.component.ts]
import { Component, signal, computed } from '@angular/core'

@Component({
  selector: 'app-counter',
  template: `
    <p>计数: {{ count() }}</p>
    <p>双倍: {{ double() }}</p>
    <button (click)="increment()">+1</button>
  `
})
export class CounterComponent {
  count = signal(0)
  double = computed(() => this.count() * 2)

  increment() {
    this.count.update(c => c + 1)
  }
}
```

## 包管理器镜像配置

国内安装依赖时推荐配置镜像源：

```bash [终端]
# npm
npm config set registry https://registry.npmmirror.com

# pnpm
pnpm config set registry https://registry.npmmirror.com

# yarn
yarn config set registry https://registry.npmmirror.com
```

