# NestJS 拦截器 (Interceptors)

拦截器可以在请求处理前后执行逻辑，用于转换数据、日志记录等。

- 官方文档：https://docs.nestjs.com/interceptors

## 拦截器基础

### 什么是拦截器

拦截器使用 `@Injectable()` 装饰器，实现 `NestInterceptor` 接口。

### 拦截器 vs 中间件 vs 守卫

| 类型 | 执行时机 | 用途 |
|------|---------|------|
| 中间件 | 请求到达时 | 日志、CORS、解析 |
| 守卫 | 中间件之后 | 权限控制 |
| 拦截器 | 守卫之后 | 数据转换、日志 |

## 创建拦截器

### 基本拦截器

```typescript [logging.interceptor.ts]
import { Injectable, NestInterceptor, ExecutionContext, CallHandler } from '@nestjs/common'
import { Observable } from 'rxjs'
import { tap } from 'rxjs/operators'

@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const now = Date.now()
    const request = context.switchToHttp().getRequest()
    
    console.log(`${request.method} ${request.url}`)
    
    return next
      .handle()
      .pipe(
        tap(() => console.log(`执行耗时: ${Date.now() - now}ms`))
      )
  }
}
```

## 使用拦截器

### 控制器级

```typescript [controller-interceptor.ts]
import { Controller, Get, UseInterceptors } from '@nestjs/common'
import { LoggingInterceptor } from './logging.interceptor'

@Controller('users')
@UseInterceptors(LoggingInterceptor)
export class UsersController {
  @Get()
  findAll() {
    return [{ id: 1, name: '张三' }]
  }
}
```

### 路由级

```typescript [route-interceptor.ts]
import { Controller, Get, UseInterceptors } from '@nestjs/common'
import { LoggingInterceptor } from './logging.interceptor'

@Controller('users')
export class UsersController {
  @Get()
  @UseInterceptors(LoggingInterceptor)
  findAll() {
    return [{ id: 1, name: '张三' }]
  }
}
```

### 全局拦截器

```typescript [global-interceptor.ts]
import { NestFactory } from '@nestjs/core'
import { LoggingInterceptor } from './logging.interceptor'
import { AppModule } from './app.module'

async function bootstrap() {
  const app = await NestFactory.create(AppModule)
  
  app.useGlobalInterceptors(new LoggingInterceptor())
  
  await app.listen(3000)
}
bootstrap()
```

## 数据转换拦截器

### 响应格式统一

```typescript [transform.interceptor.ts]
import { Injectable, NestInterceptor, ExecutionContext, CallHandler } from '@nestjs/common'
import { Observable } from 'rxjs'
import { map } from 'rxjs/operators'

export interface Response<T> {
  data: T
  message: string
  code: number
}

@Injectable()
export class TransformInterceptor<T> implements NestInterceptor<T, Response<T>> {
  intercept(context: ExecutionContext, next: CallHandler): Observable<Response<T>> {
    return next.handle().pipe(
      map(data => ({
        data,
        message: 'success',
        code: 200
      }))
    )
  }
}
```

### 使用转换拦截器

```typescript [use-transform.ts]
import { Controller, Get, UseInterceptors } from '@nestjs/common'
import { TransformInterceptor } from './transform.interceptor'

@Controller('users')
@UseInterceptors(TransformInterceptor)
export class UsersController {
  @Get()
  findAll() {
    return [{ id: 1, name: '张三' }]
  }
}

// 响应格式：
// {
//   "data": [{ "id": 1, "name": "张三" }],
//   "message": "success",
//   "code": 200
// }
```

## 超时拦截器

```typescript [timeout.interceptor.ts]
import { Injectable, NestInterceptor, ExecutionContext, CallHandler, RequestTimeoutException } from '@nestjs/common'
import { Observable, throwError, TimeoutError } from 'rxjs'
import { catchError, timeout } from 'rxjs/operators'

@Injectable()
export class TimeoutInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    return next.handle().pipe(
      timeout(5000),
      catchError(err => {
        if (err instanceof TimeoutError) {
          return throwError(() => new RequestTimeoutException('请求超时'))
        }
        return throwError(() => err)
      })
    )
  }
}
```

## 缓存拦截器

```typescript [cache.interceptor.ts]
import { Injectable, NestInterceptor, ExecutionContext, CallHandler } from '@nestjs/common'
import { Observable, of } from 'rxjs'

@Injectable()
export class CacheInterceptor implements NestInterceptor {
  private cache = new Map<string, any>()

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const request = context.switchToHttp().getRequest()
    const key = request.url
    
    if (this.cache.has(key)) {
      return of(this.cache.get(key))
    }
    
    return next.handle().pipe(
      tap(data => {
        this.cache.set(key, data)
      })
    )
  }
}
```

## 完整示例

```typescript [full-example.ts]
import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler
} from '@nestjs/common'
import { Observable } from 'rxjs'
import { tap, map } from 'rxjs/operators'

// 日志 + 转换拦截器
@Injectable()
export class FullInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const now = Date.now()
    const request = context.switchToHttp().getRequest()
    
    console.log(`请求: ${request.method} ${request.url}`)
    
    return next.handle().pipe(
      tap(() => {
        console.log(`响应耗时: ${Date.now() - now}ms`)
      }),
      map(data => ({
        data,
        message: 'success',
        code: 200,
        timestamp: new Date().toISOString()
      }))
    )
  }
}

// 控制器中使用
import { Controller, Get, UseInterceptors } from '@nestjs/common'

@Controller('users')
@UseInterceptors(FullInterceptor)
export class UsersController {
  @Get()
  findAll() {
    return [{ id: 1, name: '张三' }]
  }
}
```

::: tip 提示
- 拦截器可以转换请求和响应数据
- 可以全局、控制器级或路由级使用
- 常用于日志、缓存、超时处理
:::
