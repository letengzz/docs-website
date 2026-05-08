# NestJS 管道 (Pipes)

管道用于数据验证和转换，在路由处理之前执行。

- 官方文档：https://docs.nestjs.com/pipes

## 管道基础

### 什么是管道

管道有两个典型用例：
- **转换**：将输入数据转换为所需格式
- **验证**：评估输入数据，如果无效则抛出异常

### 内置管道

NestJS 提供了几个内置管道：
- `ValidationPipe` - 数据验证
- `ParseIntPipe` - 解析整数
- `ParseUUIDPipe` - 解析 UUID
- `ParseBoolPipe` - 解析布尔值
- `ParseArrayPipe` - 解析数组
- `ParseEnumPipe` - 解析枚举

## 使用内置管道

### ParseIntPipe

```typescript [parse-int.ts]
import { Controller, Get, Param, ParseIntPipe } from '@nestjs/common'

@Controller('users')
export class UsersController {
  @Get(':id')
  findOne(@Param('id', ParseIntPipe) id: number) {
    return { id, name: '张三' }
  }
}
```

### ParseUUIDPipe

```typescript [parse-uuid.ts]
import { Controller, Get, Param, ParseUUIDPipe } from '@nestjs/common'

@Controller('users')
export class UsersController {
  @Get(':id')
  findOne(@Param('id', ParseUUIDPipe) id: string) {
    return { id }
  }
}
```

### ParseBoolPipe

```typescript [parse-bool.ts]
import { Controller, Get, Query, ParseBoolPipe } from '@nestjs/common'

@Controller('users')
export class UsersController {
  @Get()
  findAll(@Query('active', ParseBoolPipe) active: boolean) {
    return { active }
  }
}
```

## 创建自定义管道

### 基本管道

```typescript [custom-pipe.ts]
import { PipeTransform, Injectable, ArgumentMetadata, BadRequestException } from '@nestjs/common'

@Injectable()
export class ValidateUserPipe implements PipeTransform {
  transform(value: any, metadata: ArgumentMetadata) {
    if (!value.name) {
      throw new BadRequestException('用户名不能为空')
    }
    if (value.name.length < 2) {
      throw new BadRequestException('用户名至少 2 个字符')
    }
    return value
  }
}
```

### 使用自定义管道

```typescript [use-pipe.ts]
import { Controller, Post, Body, UsePipes } from '@nestjs/common'
import { ValidateUserPipe } from './validate-user.pipe'

@Controller('users')
export class UsersController {
  @Post()
  @UsePipes(new ValidateUserPipe())
  create(@Body() createUserDto: CreateUserDto) {
    return createUserDto
  }
}
```

## ValidationPipe

### 安装 class-validator

```shell [install.sh]
npm i class-validator class-transformer
```

### 创建 DTO

```typescript [create-user.dto.ts]
import { IsString, IsEmail, MinLength, IsOptional } from 'class-validator'

export class CreateUserDto {
  @IsString()
  @MinLength(2)
  name: string

  @IsEmail()
  email: string

  @IsOptional()
  @IsString()
  phone?: string
}
```

### 全局使用 ValidationPipe

```typescript [main.ts]
import { NestFactory } from '@nestjs/core'
import { ValidationPipe } from '@nestjs/common'
import { AppModule } from './app.module'

async function bootstrap() {
  const app = await NestFactory.create(AppModule)
  
  // 全局使用验证管道
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true, // 自动移除非定义的属性
      forbidNonWhitelisted: true, // 拒绝非定义属性
      transform: true, // 自动转换类型
      transformOptions: {
        enableImplicitConversion: true
      }
    })
  )
  
  await app.listen(3000)
}
bootstrap()
```

### 路由级使用

```typescript [route-pipe.ts]
import { Controller, Post, Body, UsePipes, ValidationPipe } from '@nestjs/common'

@Controller('users')
export class UsersController {
  @Post()
  @UsePipes(new ValidationPipe())
  create(@Body() createUserDto: CreateUserDto) {
    return createUserDto
  }
}
```

## 管道执行顺序

```typescript [order.ts]
import { Controller, Get, Param, ParseIntPipe, UsePipes } from '@nestjs/common'

@Controller('users')
@UsePipes(CustomPipe1) // 第一个执行
export class UsersController {
  @Get(':id')
  @UsePipes(CustomPipe2) // 第二个执行
  findOne(
    @Param('id', ParseIntPipe) id: number // 第三个执行
  ) {
    return { id }
  }
}
```

## 完整示例

```typescript [full-example.ts]
import {
  PipeTransform,
  Injectable,
  ArgumentMetadata,
  BadRequestException
} from '@nestjs/common'

// 自定义验证管道
@Injectable()
export class CustomValidationPipe implements PipeTransform {
  transform(value: any, metadata: ArgumentMetadata) {
    if (metadata.type === 'body') {
      if (!value || Object.keys(value).length === 0) {
        throw new BadRequestException('请求体不能为空')
      }
    }
    return value
  }
}

// 控制器中使用
import { Controller, Post, Body, UsePipes } from '@nestjs/common'

@Controller('users')
@UsePipes(CustomValidationPipe)
export class UsersController {
  @Post()
  create(@Body() createUserDto: CreateUserDto) {
    return createUserDto
  }
}
```

::: tip 提示
- 管道在路由处理之前执行
- 可以全局、控制器级或路由级使用
- ValidationPipe 是最常用的管道
:::
