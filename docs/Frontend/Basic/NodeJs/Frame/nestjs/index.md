# NestJS 框架

NestJS 是一个用于构建高效、可扩展的 Node.js 服务器端应用程序的框架。

- 官网：https://nestjs.com/
- 中文文档：https://docs.nestjs.cn/

NestJS 使用 TypeScript 构建，结合了 OOP（面向对象编程）、FP（函数式编程）和 FRP（函数响应式编程）的元素。

## NestJS 特点

- **TypeScript 优先**：完全使用 TypeScript 开发
- **依赖注入**：内置强大的 DI 容器
- **模块化架构**：清晰的代码组织结构
- **装饰器模式**：优雅的 API 设计
- **多平台支持**：支持 Express 和 Fastify
- **企业级**：适合大型项目开发

## 技术栈

| 技术 | 说明 |
|------|------|
| TypeScript | 类型安全的编程语言 |
| 依赖注入 | IoC 容器管理 |
| 装饰器 | 元数据编程 |
| 模块系统 | 代码组织方式 |
| 中间件 | 请求处理管道 |
| 管道 | 数据验证和转换 |
| 守卫 | 权限控制 |
| 拦截器 | 请求/响应处理 |

## 安装

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

## 快速开始

```typescript [main.ts]
import { NestFactory } from '@nestjs/core'
import { AppModule } from './app.module'

async function bootstrap() {
  const app = await NestFactory.create(AppModule)
  await app.listen(3000)
}
bootstrap()
```

```typescript [app.module.ts]
import { Module } from '@nestjs/common'

@Module({
  imports: [],
  controllers: [],
  providers: [],
})
export class AppModule {}
```

```typescript [app.controller.ts]
import { Controller, Get } from '@nestjs/common'

@Controller()
export class AppController {
  @Get()
  getHello(): string {
    return 'Hello World!'
  }
}
```
