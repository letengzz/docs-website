# NestJS 基础操作

## 控制器

控制器负责处理传入的请求并返回响应。

### 基本控制器

```typescript [basic.controller.ts]
import { Controller, Get } from '@nestjs/common'

@Controller()
export class AppController {
  @Get()
  getHello(): string {
    return 'Hello World!'
  }
}
```

### 路由前缀

```typescript [prefix.controller.ts]
import { Controller, Get, Post } from '@nestjs/common'

@Controller('users')
export class UsersController {
  // GET /users
  @Get()
  findAll() {
    return '获取所有用户'
  }

  // GET /users/profile
  @Get('profile')
  getProfile() {
    return '用户资料'
  }

  // POST /users
  @Post()
  create() {
    return '创建用户'
  }
}
```

## HTTP 方法

### GET 请求

```typescript [get.controller.ts]
import { Controller, Get, Param, Query } from '@nestjs/common'

@Controller('users')
export class UsersController {
  // GET /users
  @Get()
  findAll() {
    return [{ id: 1, name: '张三' }]
  }

  // GET /users/1
  @Get(':id')
  findOne(@Param('id') id: string) {
    return { id, name: '张三' }
  }

  // GET /users?page=1&limit=10
  @Get()
  findWithQuery(@Query('page') page: number, @Query('limit') limit: number) {
    return { page, limit }
  }
}
```

### POST 请求

```typescript [post.controller.ts]
import { Controller, Post, Body } from '@nestjs/common'

@Controller('users')
export class UsersController {
  @Post()
  create(@Body() createUserDto: CreateUserDto) {
    return {
      id: Date.now(),
      ...createUserDto
    }
  }
}
```

### PUT 请求

```typescript [put.controller.ts]
import { Controller, Put, Param, Body } from '@nestjs/common'

@Controller('users')
export class UsersController {
  @Put(':id')
  update(@Param('id') id: string, @Body() updateUserDto: UpdateUserDto) {
    return {
      id,
      ...updateUserDto,
      message: '更新成功'
    }
  }
}
```

### DELETE 请求

```typescript [delete.controller.ts]
import { Controller, Delete, Param, HttpCode } from '@nestjs/common'

@Controller('users')
export class UsersController {
  @Delete(':id')
  @HttpCode(204)
  remove(@Param('id') id: string) {
    return { id, message: '删除成功' }
  }
}
```

## DTO (Data Transfer Object)

DTO 用于定义数据传输格式：

```typescript [create-user.dto.ts]
export class CreateUserDto {
  name: string
  email: string
  age: number
}
```

```typescript [update-user.dto.ts]
export class UpdateUserDto {
  name?: string
  email?: string
  age?: number
}
```

## 服务层

服务层处理业务逻辑：

```typescript [users.service.ts]
import { Injectable } from '@nestjs/common'
import { CreateUserDto } from './dto/create-user.dto'

@Injectable()
export class UsersService {
  private users = [
    { id: 1, name: '张三', email: 'zhangsan@example.com' },
    { id: 2, name: '李四', email: 'lisi@example.com' }
  ]

  findAll() {
    return this.users
  }

  findOne(id: number) {
    return this.users.find(user => user.id === id)
  }

  create(createUserDto: CreateUserDto) {
    const user = {
      id: Date.now(),
      ...createUserDto
    }
    this.users.push(user)
    return user
  }

  update(id: number, updateUserDto: UpdateUserDto) {
    const user = this.users.find(u => u.id === id)
    Object.assign(user, updateUserDto)
    return user
  }

  remove(id: number) {
    this.users = this.users.filter(u => u.id !== id)
    return { message: '删除成功' }
  }
}
```

## 完整示例

### 模块

```typescript [users.module.ts]
import { Module } from '@nestjs/common'
import { UsersController } from './users.controller'
import { UsersService } from './users.service'

@Module({
  controllers: [UsersController],
  providers: [UsersService],
  exports: [UsersService]
})
export class UsersModule {}
```

### 控制器

```typescript [users.controller.ts]
import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Param,
  Body,
  HttpCode,
  HttpStatus
} from '@nestjs/common'
import { UsersService } from './users.service'
import { CreateUserDto } from './dto/create-user.dto'
import { UpdateUserDto } from './dto/update-user.dto'

@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get()
  findAll() {
    return this.usersService.findAll()
  }

  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.usersService.findOne(+id)
  }

  @Post()
  @HttpCode(HttpStatus.CREATED)
  create(@Body() createUserDto: CreateUserDto) {
    return this.usersService.create(createUserDto)
  }

  @Put(':id')
  update(@Param('id') id: string, @Body() updateUserDto: UpdateUserDto) {
    return this.usersService.update(+id, updateUserDto)
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  remove(@Param('id') id: string) {
    return this.usersService.remove(+id)
  }
}
```

### 入口文件

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

::: tip 提示
- 使用装饰器定义路由
- 控制器处理请求，服务处理业务逻辑
- 使用 DTO 定义数据格式
:::
