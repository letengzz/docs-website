# Hapi 基础操作

## 安装与启动

```shell [install.sh]
npm i @hapi/hapi
```

```js [app.js]
const Hapi = require('@hapi/hapi')

const init = async () => {
  const server = Hapi.server({
    port: 3000,
    host: 'localhost'
  })

  server.route({
    method: 'GET',
    path: '/',
    handler: (request, h) => {
      return 'Hello World!'
    }
  })

  await server.start()
  console.log('服务启动在', server.info.uri)
}

init()
```

## 路由配置

### 基本路由

```js [basic-routes.js]
// GET 请求
server.route({
  method: 'GET',
  path: '/',
  handler: (request, h) => {
    return '首页'
  }
})

// POST 请求
server.route({
  method: 'POST',
  path: '/users',
  handler: (request, h) => {
    return '创建用户'
  }
})

// 多方法路由
server.route({
  method: ['GET', 'POST'],
  path: '/multi',
  handler: (request, h) => {
    return '支持多种方法'
  }
})
```

### 路径参数

```js [path-params.js]
server.route({
  method: 'GET',
  path: '/users/{id}',
  handler: (request, h) => {
    return { id: request.params.id }
  }
})

// 多个参数
server.route({
  method: 'GET',
  path: '/users/{userId}/posts/{postId}',
  handler: (request, h) => {
    return {
      userId: request.params.userId,
      postId: request.params.postId
    }
  }
})

// 可选参数
server.route({
  method: 'GET',
  path: '/users/{id?}',
  handler: (request, h) => {
    return { id: request.params.id || '全部' }
  }
})
```

### 查询参数

```js [query-params.js]
server.route({
  method: 'GET',
  path: '/users',
  handler: (request, h) => {
    const { page, limit, sort } = request.query
    return {
      page: page || 1,
      limit: limit || 10,
      sort: sort || 'desc'
    }
  }
})
```

## 输入验证

### 安装 Joi

```shell [install-joi.sh]
npm i joi
```

### 请求体验证

```js [body-validation.js]
const Joi = require('joi')

server.route({
  method: 'POST',
  path: '/users',
  options: {
    validate: {
      payload: Joi.object({
        name: Joi.string().min(2).max(50).required(),
        email: Joi.string().email().required(),
        age: Joi.number().integer().min(0).max(150)
      })
    }
  },
  handler: (request, h) => {
    return request.payload
  }
})
```

### 查询参数验证

```js [query-validation.js]
server.route({
  method: 'GET',
  path: '/users',
  options: {
    validate: {
      query: Joi.object({
        page: Joi.number().integer().min(1).default(1),
        limit: Joi.number().integer().min(1).max(100).default(10)
      })
    }
  },
  handler: (request, h) => {
    return {
      page: request.query.page,
      limit: request.query.limit
    }
  }
})
```

### 路径参数验证

```js [params-validation.js]
server.route({
  method: 'GET',
  path: '/users/{id}',
  options: {
    validate: {
      params: Joi.object({
        id: Joi.number().integer().min(1)
      })
    }
  },
  handler: (request, h) => {
    return { id: request.params.id }
  }
})
```

## 响应处理

### 设置状态码

```js [status.js]
server.route({
  method: 'POST',
  path: '/users',
  handler: (request, h) => {
    return h.response({ message: '创建成功' }).code(201)
  }
})
```

### 设置响应头

```js [headers.js]
server.route({
  method: 'GET',
  path: '/download',
  handler: (request, h) => {
    return h
      .response(fileContent)
      .header('Content-Type', 'application/octet-stream')
      .header('Content-Disposition', 'attachment; filename=file.txt')
  }
})
```

### 重定向

```js [redirect.js]
server.route({
  method: 'GET',
  path: '/old',
  handler: (request, h) => {
    return h.redirect('/new')
  }
})
```

## 生命周期方法

### 前置处理

```js [pre.js]
server.route({
  method: 'GET',
  path: '/users/{id}',
  options: {
    pre: [
      {
        method: async (request, h) => {
          const user = await getUser(request.params.id)
          if (!user) {
            throw Boom.notFound('用户不存在')
          }
          return user
        },
        assign: 'user'
      }
    ]
  },
  handler: (request, h) => {
    return request.pre.user
  }
})
```

## 插件使用

### 静态文件

```shell [install-inert.sh]
npm i @hapi/inert
```

```js [static.js]
const Inert = require('@hapi/inert')

await server.register(Inert)

server.route({
  method: 'GET',
  path: '/{param*}',
  handler: {
    directory: {
      path: 'public'
    }
  }
})
```

### 模板引擎

```shell [install-vision.sh]
npm i @hapi/vision
```

```js [template.js]
const Vision = require('@hapi/vision')

await server.register(Vision)

server.views({
  engines: {
    html: require('handlebars')
  },
  path: __dirname + '/templates'
})

server.route({
  method: 'GET',
  path: '/',
  handler: (request, h) => {
    return h.view('index', { title: '首页' })
  }
})
```

## 完整示例

```js [full-example.js]
const Hapi = require('@hapi/hapi')
const Joi = require('joi')

const init = async () => {
  const server = Hapi.server({
    port: 3000,
    host: 'localhost'
  })

  // 用户数据
  const users = [
    { id: 1, name: '张三', email: 'zhangsan@example.com' },
    { id: 2, name: '李四', email: 'lisi@example.com' }
  ]

  // 获取所有用户
  server.route({
    method: 'GET',
    path: '/users',
    handler: (request, h) => {
      return users
    }
  })

  // 获取单个用户
  server.route({
    method: 'GET',
    path: '/users/{id}',
    options: {
      validate: {
        params: Joi.object({
          id: Joi.number().integer().min(1)
        })
      }
    },
    handler: (request, h) => {
      const user = users.find(u => u.id === parseInt(request.params.id))
      if (!user) {
        return h.response({ error: '用户不存在' }).code(404)
      }
      return user
    }
  })

  // 创建用户
  server.route({
    method: 'POST',
    path: '/users',
    options: {
      validate: {
        payload: Joi.object({
          name: Joi.string().min(2).max(50).required(),
          email: Joi.string().email().required()
        })
      }
    },
    handler: (request, h) => {
      const user = {
        id: users.length + 1,
        ...request.payload
      }
      users.push(user)
      return h.response(user).code(201)
    }
  })

  // 更新用户
  server.route({
    method: 'PUT',
    path: '/users/{id}',
    handler: (request, h) => {
      const user = users.find(u => u.id === parseInt(request.params.id))
      if (!user) {
        return h.response({ error: '用户不存在' }).code(404)
      }
      Object.assign(user, request.payload)
      return user
    }
  })

  // 删除用户
  server.route({
    method: 'DELETE',
    path: '/users/{id}',
    handler: (request, h) => {
      const index = users.findIndex(u => u.id === parseInt(request.params.id))
      if (index === -1) {
        return h.response({ error: '用户不存在' }).code(404)
      }
      users.splice(index, 1)
      return h.response().code(204)
    }
  })

  await server.start()
  console.log('服务启动在', server.info.uri)
}

process.on('unhandledRejection', (err) => {
  console.log(err)
  process.exit(1)
})

init()
```

::: tip 提示
- Hapi 使用配置对象定义路由
- 内置 Joi 验证库
- 插件系统提供扩展功能
:::
