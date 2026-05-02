# Angular 项目结构

Angular 项目有严格的目录组织规范，理解项目结构有助于高效开发。

## 根目录文件

```
my-angular-app/
├── src/                    # 源代码目录
├── e2e/                    # 端到端测试
├── node_modules/           # 依赖包
├── angular.json            # Angular CLI 配置
├── package.json            # 项目依赖和脚本
├── tsconfig.json           # TypeScript 根配置
├── tsconfig.app.json       # 应用 TypeScript 配置
├── tsconfig.spec.json      # 测试 TypeScript 配置
├── karma.conf.js           # Karma 测试配置
├── .editorconfig           # 编辑器配置
└── .gitignore              # Git 忽略配置
```

## angular.json 配置

Angular CLI 的核心配置文件：

```json [angular.json]
{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "version": 1,
  "newProjectRoot": "projects",
  "projects": {
    "my-angular-app": {
      "projectType": "application",
      "root": "",
      "sourceRoot": "src",
      "prefix": "app",
      "architect": {
        "build": {
          "builder": "@angular/build:application",
          "options": {
            "outputPath": "dist/my-angular-app",
            "index": "src/index.html",
            "browser": "src/main.ts",
            "polyfills": ["zone.js"],
            "tsConfig": "tsconfig.app.json",
            "assets": ["src/assets", "src/favicon.ico"],
            "styles": ["src/styles.scss"],
            "scripts": []
          }
        },
        "serve": {
          "builder": "@angular/build:dev-server",
          "options": {
            "port": 4200
          }
        }
      }
    }
  }
}
```

## src 目录结构

### 核心文件

```
src/
├── app/                    # 应用代码
│   ├── app.component.ts    # 根组件
│   ├── app.component.html  # 根组件模板
│   ├── app.component.scss  # 根组件样式
│   ├── app.config.ts       # 应用配置
│   └── app.routes.ts       # 路由配置
├── assets/                 # 静态资源（图片、字体等）
├── environments/           # 环境配置
│   ├── environment.ts      # 开发环境
│   └── environment.prod.ts # 生产环境
├── index.html              # HTML 入口
├── main.ts                 # 应用入口
├── styles.scss             # 全局样式
└── favicon.ico             # 网站图标
```

### index.html

```html [src/index.html]
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>My Angular App</title>
  <base href="/">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" type="image/x-icon" href="favicon.ico">
</head>
<body>
  <app-root></app-root>
</body>
</html>
```

### main.ts

```typescript [src/main.ts]
import { bootstrapApplication } from '@angular/platform-browser'
import { AppComponent } from './app/app.component'
import { appConfig } from './app/app.config'

bootstrapApplication(AppComponent, appConfig)
  .catch(err => console.error(err))
```

## 推荐的目录组织

### 按功能模块组织

```
src/app/
├── core/                   # 核心模块（只导入一次）
│   ├── services/           # 全局服务
│   ├── guards/             # 路由守卫
│   ├── interceptors/       # HTTP 拦截器
│   └── core.module.ts      # 核心模块
├── shared/                 # 共享模块
│   ├── components/         # 共享组件
│   ├── pipes/              # 共享管道
│   ├── directives/         # 共享指令
│   └── shared.module.ts    # 共享模块
├── features/               # 功能模块（按业务拆分）
│   ├── auth/               # 认证模块
│   │   ├── components/     # 模块组件
│   │   ├── services/       # 模块服务
│   │   ├── guards/         # 模块守卫
│   │   └── auth.routes.ts  # 模块路由
│   ├── dashboard/          # 仪表盘模块
│   └── users/              # 用户模块
├── layouts/                # 布局组件
├── models/                 # 数据模型
├── app.component.ts        # 根组件
├── app.config.ts           # 应用配置
└── app.routes.ts           # 路由配置
```

## 环境配置

### 开发环境

```typescript [src/environments/environment.ts]
export const environment = {
  production: false,
  apiUrl: 'http://localhost:3000/api',
  debug: true
}
```

### 生产环境

```typescript [src/environments/environment.prod.ts]
export const environment = {
  production: true,
  apiUrl: 'https://api.example.com',
  debug: false
}
```

### 使用环境变量

```typescript [src/app/services/api.service.ts]
import { Injectable, inject } from '@angular/core'
import { HttpClient } from '@angular/common/http'
import { environment } from '../../environments/environment'

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient)
  private baseUrl = environment.apiUrl

  getData() {
    return this.http.get(`${this.baseUrl}/data`)
  }
}
```

## TypeScript 配置

### tsconfig.json

```json [tsconfig.json]
{
  "compileOnSave": false,
  "compilerOptions": {
    "outDir": "./dist/out-tsc",
    "forceConsistentCasingInFileNames": true,
    "strict": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "sourceMap": true,
    "declaration": false,
    "experimentalDecorators": true,
    "moduleResolution": "node",
    "importHelpers": true,
    "target": "ES2022",
    "module": "ES2022",
    "useDefineForClassFields": false,
    "lib": ["ES2022", "dom"]
  },
  "angularCompilerOptions": {
    "enableI18nLegacyMessageIdFormat": false,
    "strictInjectionParameters": true,
    "strictInputAccessModifiers": true,
    "strictTemplates": true
  }
}
```

## 常用 CLI 命令

```bash [终端]
# 生成组件
ng generate component components/user-list

# 生成服务
ng generate service services/user

# 生成模块
ng generate module modules/users

# 生成管道
ng generate pipe pipes/format-date

# 生成指令
ng generate directive directives/highlight

# 生成守卫
ng generate guard guards/auth

# 生成拦截器
ng generate interceptor interceptors/auth

# 构建项目
ng build

# 启动开发服务器
ng serve

# 运行测试
ng test

# 运行 E2E 测试
ng e2e
```
