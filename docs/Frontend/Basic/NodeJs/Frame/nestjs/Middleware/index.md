# NestJS 中间件

中间件在请求到达路由之前执行。

- 官方文档：https://docs.nestjs.com/middleware

## 中间件基础

### 什么是中间件

中间件函数可以访问请求对象、响应对象和 next 中间件函数。

### NestJS 中间件 vs Express 中间件

NestJS 中间件本质上是 Express 中间件，只是使用了 NestJS 的模块化方式组织。

## 创建中间件

### 基本中间件

```typescript [logger.middleware.ts]
import { Injectable, NestMiddleware } from '@nestjs/common'
import { Request, Response, NextFunction } from 'express'

@Injectable()
export class LoggerMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction) {
    console.log(`${req.method} ${req.url}`)
    next()
  }
}
```

### 函数式中间件

```typescript [functional.middleware.ts]
import { Request, Response, NextFunction } from 'express'

export function loggerMiddleware(req: Request, res: Response, next: NextFunction) {
  console.log(`${req.method} ${req.url} - ${new Date().toISOString()}`)
  next()
}
```

## 使用中间件

### 在模块中配置

```typescript [app.module.ts]
import { Module, NestModule, MiddlewareConsumer } from '@nestjs/common'
import { LoggerMiddleware } from './logger.middleware'
import { UsersController } from './users.controller'

@Module({
  controllers: [UsersController]
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer
      .apply(LoggerMiddleware)
      .forRoutes('users')
  }
}
```

### 多个中间件

```typescript [multiple-middleware.ts]
import { Module, NestModule, MiddlewareConsumer } from '@nestjs/common'
import { LoggerMiddleware } from './logger.middleware'
import { AuthMiddleware } from './auth.middleware'

@Module({})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer
      .apply(LoggerMiddleware, AuthMiddleware)
      .forRoutes('users')
  }
}
```

### 路由匹配

```typescript [route-matching.ts]
import { Module, NestModule, MiddlewareConsumer } from '@nestjs/common'

@Module({})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    // 匹配所有路由
    consumer.apply(LoggerMiddleware).forRoutes('*')
    
    // 匹配特定路由
    consumer.apply(LoggerMiddleware).forRoutes('users')
    
    // 匹配路由模式
    consumer.apply(LoggerMiddleware).forRoutes('users/*')
  }
}
```

### 排除路由

```typescript [exclude.ts]
import { Module, NestModule, MiddlewareConsumer } from '@nestjs/common'

@Module({})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer
      .apply(LoggerMiddleware)
      .exclude('users/health')
      .forRoutes('users')
  }
}
```

## 常用中间件

### CORS 中间件

```typescript [cors.ts]
import { Module, NestModule, MiddlewareConsumer } from '@nestjs/common'

@Module({})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer
      .apply((req, res, next) => {
        res.header('Access-Control-Allow-Origin', '*')
        res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
        res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        next()
      })
      .forRoutes('*')
  }
}
```

### Body Parser 中间件

```typescript [body-parser.ts]
import { NestFactory } from '@nestjs/core'
import { json, urlencoded } from 'express'
import { AppModule } from './app.module'

async function bootstrap() {
  const app = await NestFactory.create(AppModule)
  
  app.use(json({ limit: '50mb' }))
  app.use(urlencoded({ extended: true, limit: '50mb' }))
  
  await app.listen(3000)
}
bootstrap()
```

### 静态文件中间件

```typescript [static.ts]
import { NestFactory } from '@nestjs/core'
import { join } from 'path'
import { serve, static as serveStatic } from 'express'
import { AppModule } from './app.module'

async function bootstrap() {
  const app = await NestFactory.create(AppModule)
  
  app.use('/public', serveStatic(join(__dirname, '..', 'public')))
  
  await app.listen(3000)
}
bootstrap()
```

## 依赖注入中间件

```typescript [di-middleware.ts]
import { Injectable, NestMiddleware } from '@nestjs/common'
import { Request, Response, NextFunction } from 'express'
import { UsersService } from './users.service'

@Injectable()
export class UserMiddleware implements NestMiddleware {
  constructor(private usersService: UsersService) {}

  async use(req: Request, res: Response, next: NextFunction) {
    const userId = req.headers['x-user-id']
    
    if (userId) {
      req['user'] = await this.usersService.findById(Number(userId))
    }
    
    next()
  }
}
```

## 完整示例

```typescript [full-example.ts]
// logger.middleware.ts
import { Injectable, NestMiddleware } from '@nestjs/common'
import { Request, Response, NextFunction } from 'express'

@Injectable()
export class LoggerMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction) {
    const start = Date.now()
    
    res.on('finish', () => {
      const duration = Date.now() - start
      console.log(`${req.method} ${req.url} - ${res.statusCode} - ${duration}ms`)
    })
    
    next()
  }
}

// app.module.ts
import { Module, NestModule, MiddlewareConsumer } from '@nestjs/common'
import { LoggerMiddleware } from './logger.middleware'
import { UsersController } from './users.controller'

@Module({
  controllers: [UsersController]
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer
      .apply(LoggerMiddleware)
      .forRoutes('*')
  }
}
```

::: tip 提示
- 中间件在模块的 configure 方法中配置
- 支持函数式和类中间件
- 可以排除特定路由
:::
