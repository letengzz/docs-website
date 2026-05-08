# NestJS 概述

NestJS 是一个用于构建高效、可扩展的 Node.js 服务器端应用程序的框架。

- 官网：https://nestjs.com/
- 中文文档：https://docs.nestjs.cn/

NestJS 使用 TypeScript 构建，结合了 OOP（面向对象编程）、FP（函数式编程）和 FRP（函数响应式编程）的元素。

## 什么是 NestJS

NestJS 借鉴了 Angular 的设计模式，提供了开箱即用的架构：

**核心特性**：

- **TypeScript 优先**：完全使用 TypeScript 开发
- **依赖注入**：内置强大的 DI 容器
- **模块化架构**：清晰的代码组织结构
- **装饰器模式**：优雅的 API 设计
- **多平台支持**：支持 Express 和 Fastify
- **企业级**：适合大型项目开发

## NestJS vs Express

| 特性 | NestJS | Express |
|------|--------|---------|
| 语言 | TypeScript | JavaScript |
| 架构 | MVC + DI | 路由 + 中间件 |
| 学习曲线 | 陡峭 | 平缓 |
| 适用场景 | 大型企业项目 | 中小型项目 |
| 代码组织 | 模块化 | 自由组织 |

## 安装与创建项目

```shell [install.sh]
# 安装 CLI
npm i -g @nestjs/cli

# 创建项目
nest new project-name

# 进入项目
cd project-name

# 启动开发服务器
npm run start:dev
```

## 项目结构

```
project-name/
├── src/
│   ├── app.controller.ts    # 控制器
│   ├── app.module.ts        # 根模块
│   ├── app.service.ts       # 服务
│   └── main.ts              # 入口文件
├── test/                    # 测试文件
├── package.json
└── tsconfig.json
```

## 核心概念

### 模块 (Module)

模块是 NestJS 的基本组织单元：

```typescript [app.module.ts]
import { Module } from '@nestjs/common'
import { AppController } from './app.controller'
import { AppService } from './app.service'

@Module({
  imports: [],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
```

### 控制器 (Controller)

控制器处理 HTTP 请求：

```typescript [app.controller.ts]
import { Controller, Get, Post } from '@nestjs/common'

@Controller('users')
export class UsersController {
  @Get()
  findAll(): string {
    return '获取所有用户'
  }

  @Get(':id')
  findOne(): string {
    return '获取单个用户'
  }

  @Post()
  create(): string {
    return '创建用户'
  }
}
```

### 服务 (Service)

服务处理业务逻辑：

```typescript [app.service.ts]
import { Injectable } from '@nestjs/common'

@Injectable()
export class AppService {
  getHello(): string {
    return 'Hello World!'
  }
}
```

## 依赖注入

```typescript [users.service.ts]
import { Injectable } from '@nestjs/common'

@Injectable()
export class UsersService {
  private users = [
    { id: 1, name: '张三' },
    { id: 2, name: '李四' }
  ]

  findAll() {
    return this.users
  }

  findOne(id: number) {
    return this.users.find(user => user.id === id)
  }
}
```

```typescript [users.controller.ts]
import { Controller, Get, Param } from '@nestjs/common'
import { UsersService } from './users.service'

@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get()
  findAll() {
    return this.usersService.findAll()
  }

  @Get(':id')
  findOne(@Param('id') id: number) {
    return this.usersService.findOne(id)
  }
}
```

## 快速启动

```typescript [main.ts]
import { NestFactory } from '@nestjs/core'
import { AppModule } from './app.module'

async function bootstrap() {
  const app = await NestFactory.create(AppModule)
  await app.listen(3000)
  console.log('服务启动在 3000 端口')
}
bootstrap()
```
