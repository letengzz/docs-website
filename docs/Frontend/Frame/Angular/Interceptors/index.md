# Angular HTTP 拦截器

HTTP 拦截器用于在请求发出前或响应返回后进行处理，常用于添加认证头、错误处理等。

## 创建拦截器

```bash [终端]
ng generate interceptor interceptors/auth
```

## 函数式拦截器（Angular 15+）

### 认证拦截器

```typescript [src/app/interceptors/auth.interceptor.ts]
import { HttpInterceptorFn } from '@angular/common/http'

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('token')
  
  if (token) {
    const cloned = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    })
    return next(cloned)
  }
  
  return next(req)
}
```

### 日志拦截器

```typescript [src/app/interceptors/logging.interceptor.ts]
import { HttpInterceptorFn } from '@angular/common/http'
import { inject } from '@angular/core'
import { tap } from 'rxjs'

export const loggingInterceptor: HttpInterceptorFn = (req, next) => {
  const started = Date.now()
  
  return next(req).pipe(
    tap({
      next: (event) => {
        const elapsed = Date.now() - started
        console.log(`${req.method} ${req.url} 耗时 ${elapsed}ms`)
      },
      error: (error) => {
        const elapsed = Date.now() - started
        console.error(`${req.method} ${req.url} 失败 耗时 ${elapsed}ms`, error)
      }
    })
  )
}
```

### 错误处理拦截器

```typescript [src/app/interceptors/error.interceptor.ts]
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http'
import { inject } from '@angular/core'
import { Router } from '@angular/router'
import { catchError } from 'rxjs/operators'
import { throwError } from 'rxjs'

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router)
  
  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let errorMessage = '未知错误'
      
      if (error.error instanceof ErrorEvent) {
        // 客户端错误
        errorMessage = `错误: ${error.error.message}`
      } else {
        // 服务端错误
        switch (error.status) {
          case 400:
            errorMessage = '请求参数错误'
            break
          case 401:
            errorMessage = '未授权，请重新登录'
            router.navigate(['/login'])
            break
          case 403:
            errorMessage = '权限不足'
            break
          case 404:
            errorMessage = '请求的资源不存在'
            break
          case 500:
            errorMessage = '服务器内部错误'
            break
          default:
            errorMessage = `错误码: ${error.status}`
        }
      }
      
      console.error(errorMessage, error)
      return throwError(() => new Error(errorMessage))
    })
  )
}
```

## 配置拦截器

```typescript [src/app/app.config.ts]
import { ApplicationConfig } from '@angular/core'
import { provideRouter } from '@angular/router'
import { provideHttpClient, withInterceptors } from '@angular/common/http'
import { routes } from './app.routes'
import { authInterceptor } from './interceptors/auth.interceptor'
import { loggingInterceptor } from './interceptors/logging.interceptor'
import { errorInterceptor } from './interceptors/error.interceptor'

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(
      withInterceptors([
        authInterceptor,
        loggingInterceptor,
        errorInterceptor
      ])
    )
  ]
}
```

## 跳过拦截器

某些请求不需要拦截器处理：

```typescript
import { HttpContext } from '@angular/common/http'

export const SKIP_AUTH = new HttpContextToken<boolean>(() => false)

// 请求时跳过认证
this.http.get('/api/public', {
  context: new HttpContext().set(SKIP_AUTH, true)
})
```

```typescript
// 拦截器中检查
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  if (req.context.get(SKIP_AUTH)) {
    return next(req)
  }
  
  const token = localStorage.getItem('token')
  if (token) {
    const cloned = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` }
    })
    return next(cloned)
  }
  
  return next(req)
}
```

## 类拦截器（传统方式）

```typescript [src/app/interceptors/auth.interceptor.ts]
import { Injectable } from '@angular/core'
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http'
import { Observable } from 'rxjs'

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = localStorage.getItem('token')
    
    if (token) {
      const cloned = req.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      })
      return next.handle(cloned)
    }
    
    return next.handle(req)
  }
}
```

