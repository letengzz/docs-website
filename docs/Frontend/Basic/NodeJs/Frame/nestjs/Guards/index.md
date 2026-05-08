# NestJS 守卫 (Guards)

守卫用于权限控制，决定请求是否会被路由处理。

- 官方文档：https://docs.nestjs.com/guards

## 守卫基础

### 什么是守卫

守卫用于确定路由处理程序是否应该处理请求。它们主要用于身份验证和授权。

### 守卫 vs 中间件

| 特性 | 中间件 | 守卫 |
|------|--------|------|
| 执行时机 | 请求到达时 | 中间件之后，路由之前 |
| 访问权限 | 无法访问执行上下文 | 可以访问执行上下文 |
| 返回值 | 无 | boolean |

## 创建守卫

### 基本守卫

```typescript [auth.guard.ts]
import { Injectable, CanActivate, ExecutionContext, UnauthorizedException } from '@nestjs/common'

@Injectable()
export class AuthGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest()
    
    const token = request.headers.authorization
    
    if (!token) {
      throw new UnauthorizedException('未提供认证令牌')
    }
    
    // 验证 token
    if (token !== 'valid-token') {
      throw new UnauthorizedException('无效的认证令牌')
    }
    
    return true
  }
}
```

## 使用守卫

### 控制器级

```typescript [controller-guard.ts]
import { Controller, Get, UseGuards } from '@nestjs/common'
import { AuthGuard } from './auth.guard'

@Controller('users')
@UseGuards(AuthGuard)
export class UsersController {
  @Get()
  findAll() {
    return [{ id: 1, name: '张三' }]
  }

  @Get(':id')
  findOne() {
    return { id: 1, name: '张三' }
  }
}
```

### 路由级

```typescript [route-guard.ts]
import { Controller, Get, UseGuards } from '@nestjs/common'
import { AuthGuard } from './auth.guard'

@Controller('users')
export class UsersController {
  @Get()
  findAll() {
    return [{ id: 1, name: '张三' }]
  }

  @Get('admin')
  @UseGuards(AuthGuard)
  findAdmin() {
    return { role: 'admin' }
  }
}
```

### 全局守卫

```typescript [global-guard.ts]
import { NestFactory } from '@nestjs/core'
import { AuthGuard } from './auth.guard'
import { AppModule } from './app.module'

async function bootstrap() {
  const app = await NestFactory.create(AppModule)
  
  app.useGlobalGuards(new AuthGuard())
  
  await app.listen(3000)
}
bootstrap()
```

## 基于角色的守卫

### 角色装饰器

```typescript [roles.decorator.ts]
import { SetMetadata } from '@nestjs/common'

export const Roles = (...roles: string[]) => SetMetadata('roles', roles)
```

### 角色守卫

```typescript [roles.guard.ts]
import { Injectable, CanActivate, ExecutionContext } from '@nestjs/common'
import { Reflector } from '@nestjs/core'

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const roles = this.reflector.get<string[]>('roles', context.getHandler())
    
    if (!roles) {
      return true
    }
    
    const request = context.switchToHttp().getRequest()
    const user = request.user
    
    return roles.some(role => user.roles?.includes(role))
  }
}
```

### 使用角色守卫

```typescript [use-roles.ts]
import { Controller, Get, UseGuards } from '@nestjs/common'
import { RolesGuard } from './roles.guard'
import { Roles } from './roles.decorator'

@Controller('users')
@UseGuards(RolesGuard)
export class UsersController {
  @Get()
  @Roles('user', 'admin')
  findAll() {
    return [{ id: 1, name: '张三' }]
  }

  @Get('admin')
  @Roles('admin')
  findAdmin() {
    return { role: 'admin' }
  }
}
```

## JWT 守卫

### 安装

```shell [install.sh]
npm i @nestjs/passport passport passport-jwt
```

### JWT 策略

```typescript [jwt.strategy.ts]
import { ExtractJwt, Strategy } from 'passport-jwt'
import { PassportStrategy } from '@nestjs/passport'
import { Injectable } from '@nestjs/common'

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor() {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: 'your-secret-key'
    })
  }

  async validate(payload: any) {
    return { userId: payload.sub, username: payload.username }
  }
}
```

### 使用 JWT 守卫

```typescript [jwt-guard.ts]
import { Controller, Get, UseGuards } from '@nestjs/common'
import { AuthGuard } from '@nestjs/passport'

@Controller('users')
@UseGuards(AuthGuard('jwt'))
export class UsersController {
  @Get('profile')
  getProfile() {
    return { userId: 1, username: '张三' }
  }
}
```

## 完整示例

```typescript [full-example.ts]
// auth.guard.ts
import { Injectable, CanActivate, ExecutionContext, UnauthorizedException } from '@nestjs/common'

@Injectable()
export class AuthGuard implements CanActivate {
  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest()
    const token = this.extractTokenFromHeader(request)
    
    if (!token) {
      throw new UnauthorizedException()
    }
    
    try {
      const payload = await this.verifyToken(token)
      request['user'] = payload
    } catch {
      throw new UnauthorizedException()
    }
    
    return true
  }

  private extractTokenFromHeader(request: Request): string | undefined {
    const [type, token] = request.headers['authorization']?.split(' ') ?? []
    return type === 'Bearer' ? token : undefined
  }

  private async verifyToken(token: string): Promise<any> {
    // 验证 token
    return { userId: 1, roles: ['user'] }
  }
}

// 控制器中使用
import { Controller, Get, UseGuards } from '@nestjs/common'

@Controller('users')
@UseGuards(AuthGuard)
export class UsersController {
  @Get('profile')
  getProfile() {
    return { userId: 1, username: '张三' }
  }
}
```

::: tip 提示
- 守卫返回 boolean 决定是否继续
- 可以全局、控制器级或路由级使用
- 常与装饰器配合使用
:::
