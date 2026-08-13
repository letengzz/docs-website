# Next API 路由

Next.js 提供了内置的 API 路由功能，允许你在同一个应用中创建后端 API。

## API 路由基础

### 创建 API 路由

在 App Router 中，API 路由位于 `app/api/` 目录下：

```text
app/
└── api/
    └── users/
        └── route.ts
```

### 基本路由处理

```typescript [app/api/users/route.ts]
import { NextResponse } from 'next/server'

export async function GET() {
  const users = await fetchUsers()
  return NextResponse.json(users)
}

export async function POST(request: Request) {
  const body = await request.json()
  const user = await createUser(body)
  return NextResponse.json(user, { status: 201 })
}

export async function PUT(request: Request) {
  const body = await request.json()
  const user = await updateUser(body)
  return NextResponse.json(user)
}

export async function DELETE(request: Request) {
  const { id } = await request.json()
  await deleteUser(id)
  return NextResponse.json({ success: true })
}
```

## 动态路由

### 带参数的 API

```text
app/
└── api/
    └── users/
        └── [id]/
            └── route.ts
```

```typescript [app/api/users/[id]/route.ts]
import { NextResponse } from 'next/server'

interface Props {
  params: Promise<{ id: string }>
}

export async function GET(request: Request, { params }: Props) {
  const { id } = await params
  const user = await fetchUser(id)
  
  if (!user) {
    return NextResponse.json({ error: '用户不存在' }, { status: 404 })
  }
  
  return NextResponse.json(user)
}

export async function PATCH(request: Request, { params }: Props) {
  const { id } = await params
  const body = await request.json()
  const user = await updateUser(id, body)
  
  return NextResponse.json(user)
}
```

## 请求处理

### 获取请求体

```typescript [app/api/users/route.ts]
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  // JSON 数据
  const json = await request.json()
  
  // 表单数据
  const formData = await request.formData()
  const name = formData.get('name')
  
  // 文本数据
  const text = await request.text()
  
  return NextResponse.json({ success: true })
}
```

### 获取查询参数

```typescript [app/api/users/route.ts]
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const page = searchParams.get('page') || '1'
  const limit = searchParams.get('limit') || '10'
  const search = searchParams.get('search')
  
  const users = await fetchUsers({ page, limit, search })
  
  return NextResponse.json(users)
}
```

### 获取请求头

```typescript [app/api/users/route.ts]
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const authorization = request.headers.get('authorization')
  const contentType = request.headers.get('content-type')
  const userAgent = request.headers.get('user-agent')
  
  return NextResponse.json({ headers: { authorization, contentType, userAgent } })
}
```

## 响应处理

### 基本响应

```typescript [app/api/users/route.ts]
import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({ data: [] })
}

export async function POST() {
  return NextResponse.json({ data: {} }, { status: 201 })
}

export async function DELETE() {
  return NextResponse.json({ message: '删除成功' })
}
```

### 自定义响应头

```typescript [app/api/users/route.ts]
import { NextResponse } from 'next/server'

export async function GET() {
  const response = NextResponse.json({ data: [] })
  
  response.headers.set('X-Custom-Header', 'custom-value')
  response.headers.set('Cache-Control', 'public, max-age=3600')
  
  return response
}
```

### 错误响应

```typescript [app/api/users/[id]/route.ts]
import { NextResponse } from 'next/server'

export async function GET(request: Request, { params }: { params: { id: string } }) {
  const user = await fetchUser(params.id)
  
  if (!user) {
    return NextResponse.json(
      { error: '用户不存在', code: 'USER_NOT_FOUND' },
      { status: 404 }
    )
  }
  
  return NextResponse.json(user)
}
```

## 文件上传

### 处理文件上传

```typescript [app/api/upload/route.ts]
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  const formData = await request.formData()
  const file = formData.get('file') as File
  
  if (!file) {
    return NextResponse.json({ error: '没有文件' }, { status: 400 })
  }
  
  const bytes = await file.arrayBuffer()
  const buffer = Buffer.from(bytes)
  
  // 保存文件
  await saveFile(file.name, buffer)
  
  return NextResponse.json({ success: true, filename: file.name })
}
```

## 流式响应

### Server-Sent Events

```typescript [app/api/stream/route.ts]
import { NextResponse } from 'next/server'

export async function GET() {
  const encoder = new TextEncoder()
  
  const stream = new ReadableStream({
    async start(controller) {
      for (let i = 0; i < 5; i++) {
        controller.enqueue(encoder.encode(`data: ${i}\n\n`))
        await new Promise(resolve => setTimeout(resolve, 1000))
      }
      controller.close()
    },
  })
  
  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  })
}
```

## 中间件集成

### API 中间件

```typescript [app/api/users/route.ts]
import { NextResponse } from 'next/server'
import { verifyToken } from '@/lib/auth'

export async function GET(request: Request) {
  const token = request.headers.get('authorization')?.replace('Bearer ', '')
  
  if (!token) {
    return NextResponse.json({ error: '未授权' }, { status: 401 })
  }
  
  const user = await verifyToken(token)
  if (!user) {
    return NextResponse.json({ error: '令牌无效' }, { status: 401 })
  }
  
  const users = await fetchUsers()
  return NextResponse.json(users)
}
```

## 错误处理

### 全局错误处理

```typescript [app/api/users/route.ts]
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const users = await fetchUsers()
    return NextResponse.json(users)
  } catch (error) {
    console.error('API 错误:', error)
    return NextResponse.json(
      { error: '服务器内部错误' },
      { status: 500 }
    )
  }
}
```

### 自定义错误类

```typescript [lib/errors.ts]
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number = 500,
    public code?: string
  ) {
    super(message)
    this.name = 'ApiError'
  }
}
```

```typescript [app/api/users/route.ts]
import { NextResponse } from 'next/server'
import { ApiError } from '@/lib/errors'

export async function GET() {
  try {
    const users = await fetchUsers()
    
    if (!users) {
      throw new ApiError('用户不存在', 404, 'USER_NOT_FOUND')
    }
    
    return NextResponse.json(users)
  } catch (error) {
    if (error instanceof ApiError) {
      return NextResponse.json(
        { error: error.message, code: error.code },
        { status: error.status }
      )
    }
    
    return NextResponse.json(
      { error: '服务器内部错误' },
      { status: 500 }
    )
  }
}
```

## 路由处理器

### HTTP 方法

| 方法 | 用途 |
|------|------|
| `GET` | 获取资源 |
| `POST` | 创建资源 |
| `PUT` | 更新资源（全量） |
| `PATCH` | 更新资源（部分） |
| `DELETE` | 删除资源 |
| `HEAD` | 获取资源头信息 |
| `OPTIONS` | 获取支持的 HTTP 方法 |

### 方法处理

```typescript [app/api/users/route.ts]
import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({ method: 'GET' })
}

export async function POST(request: Request) {
  return NextResponse.json({ method: 'POST' })
}

export async function PUT(request: Request) {
  return NextResponse.json({ method: 'PUT' })
}

export async function DELETE(request: Request) {
  return NextResponse.json({ method: 'DELETE' })
}
```

## 最佳实践

### 1. 输入验证

::: tip
始终验证用户输入，防止注入攻击和无效数据。
:::

```typescript [app/api/users/route.ts]
import { z } from 'zod'

const userSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  age: z.number().int().min(0).max(150),
})

export async function POST(request: Request) {
  const body = await request.json()
  
  try {
    const validated = userSchema.parse(body)
    const user = await createUser(validated)
    return NextResponse.json(user, { status: 201 })
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: '验证失败', details: error.errors },
        { status: 400 }
      )
    }
    throw error
  }
}
```

### 2. 分页处理

```typescript [app/api/users/route.ts]
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const page = parseInt(searchParams.get('page') || '1')
  const limit = parseInt(searchParams.get('limit') || '10')
  
  const { users, total } = await fetchUsers({ page, limit })
  
  return NextResponse.json({
    data: users,
    pagination: {
      page,
      limit,
      total,
      pages: Math.ceil(total / limit),
    },
  })
}
```

### 3. 缓存控制

```typescript [app/api/users/route.ts]
export async function GET() {
  const users = await fetchUsers()
  
  const response = NextResponse.json(users)
  response.headers.set('Cache-Control', 'public, s-maxage=60, stale-while-revalidate=300')
  
  return response
}
```

