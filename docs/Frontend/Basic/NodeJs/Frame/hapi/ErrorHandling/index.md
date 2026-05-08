# Hapi 错误处理

Hapi 提供了完善的错误处理机制。

## 错误处理基础

### Boom 错误对象

Hapi 使用 Boom 库来创建 HTTP 友好的错误对象。

```shell [install-boom.sh]
npm i @hapi/boom
```

### 基本错误

```js [basic-error.js]
const Boom = require('@hapi/boom')

server.route({
  method: 'GET',
  path: '/error',
  handler: (request, h) => {
    throw Boom.badRequest('参数错误')
  }
})
```

## 常用 Boom 错误

### 客户端错误 (4xx)

```js [client-errors.js]
const Boom = require('@hapi/boom')

// 400 - 请求错误
throw Boom.badRequest('请求参数错误')

// 401 - 未授权
throw Boom.unauthorized('未授权访问')

// 403 - 禁止访问
throw Boom.forbidden('没有权限')

// 404 - 未找到
throw Boom.notFound('资源不存在')

// 409 - 冲突
throw Boom.conflict('资源冲突')

// 422 - 验证失败
throw Boom.badData('数据验证失败')
```

### 服务器错误 (5xx)

```js [server-errors.js]
const Boom = require('@hapi/boom')

// 500 - 内部错误
throw Boom.internal('服务器内部错误')

// 502 - 错误网关
throw Boom.badGateway('网关错误')

// 503 - 服务不可用
throw Boom.serverUnavailable('服务不可用')

// 504 - 网关超时
throw Boom.gatewayTimeout('网关超时')
```

## 自定义错误

### 创建自定义错误

```js [custom-error.js]
const Boom = require('@hapi/boom')

function createCustomError(message, statusCode, data) {
  return new Boom(message, {
    statusCode,
    data
  })
}

// 使用
throw createCustomError('自定义错误', 400, { field: 'name' })
```

## 错误处理扩展

### onPreResponse 扩展

```js [on-pre-response.js]
server.ext('onPreResponse', (request, h) => {
  const response = request.response
  
  // 如果是错误响应
  if (response.isBoom) {
    const error = response.output
    
    // 记录日志
    console.error(`${request.method} ${request.path} - ${error.statusCode} - ${error.payload.message}`)
    
    // 自定义错误响应格式
    return h.response({
      error: {
        message: error.payload.message,
        statusCode: error.statusCode,
        timestamp: new Date().toISOString()
      }
    }).code(error.statusCode)
  }
  
  return h.continue
})
```

## 验证错误

### Joi 验证错误

```js [validation-error.js]
const Joi = require('joi')

server.route({
  method: 'POST',
  path: '/users',
  options: {
    validate: {
      payload: Joi.object({
        name: Joi.string().min(2).required(),
        email: Joi.string().email().required()
      })
    }
  },
  handler: (request, h) => {
    return request.payload
  }
})

// 验证失败时自动返回 400 错误
```

### 自定义验证错误格式

```js [validation-format.js]
server.ext('onPreResponse', (request, h) => {
  const response = request.response
  
  if (response.isBoom && response.output.statusCode === 400) {
    return h.response({
      error: '验证失败',
      details: response.output.payload.message
    }).code(400)
  }
  
  return h.continue
})
```

## 404 错误处理

### 自定义 404

```js [404.js]
server.route({
  method: '*',
  path: '/{any*}',
  handler: (request, h) => {
    throw Boom.notFound(`路由 ${request.path} 不存在`)
  }
})
```

## 错误日志

### 记录错误日志

```js [error-log.js]
server.events.on('request-error', (request, err) => {
  console.error(`${new Date().toISOString()} - ${request.method} ${request.path} - ${err.message}`)
})

// 或使用扩展
server.ext('onPreResponse', (request, h) => {
  const response = request.response
  
  if (response.isBoom && response.output.statusCode >= 500) {
    // 记录服务器错误
    request.log('error', response.stack)
  }
  
  return h.continue
})
```

## 完整错误处理示例

```js [full-example.js]
const Hapi = require('@hapi/hapi')
const Boom = require('@hapi/boom')

const init = async () => {
  const server = Hapi.server({
    port: 3000,
    debug: {
      request: ['error']
    }
  })

  // 错误处理扩展
  server.ext('onPreResponse', (request, h) => {
    const response = request.response
    
    if (response.isBoom) {
      const error = response.output
      
      // 记录日志
      request.log('error', {
        message: error.payload.message,
        statusCode: error.statusCode,
        path: request.path
      })
      
      // 生产环境隐藏错误详情
      if (error.statusCode >= 500 && process.env.NODE_ENV === 'production') {
        return h.response({
          error: {
            message: '服务器内部错误',
            statusCode: 500
          }
        }).code(500)
      }
      
      // 开发环境返回详细错误
      return h.response({
        error: {
          message: error.payload.message,
          statusCode: error.statusCode,
          path: request.path
        }
      }).code(error.statusCode)
    }
    
    return h.continue
  })

  // 路由
  server.route({
    method: 'GET',
    path: '/users/{id}',
    handler: async (request, h) => {
      const user = await findUser(request.params.id)
      
      if (!user) {
        throw Boom.notFound('用户不存在')
      }
      
      return user
    }
  })

  // 404 处理
  server.route({
    method: '*',
    path: '/{any*}',
    handler: (request, h) => {
      throw Boom.notFound('路由不存在')
    }
  })

  await server.start()
  console.log('服务启动在', server.info.uri)
}

init()
```

::: tip 提示
- 使用 Boom 创建 HTTP 错误
- 使用 onPreResponse 扩展统一处理错误
- 生产环境不要暴露错误详情
:::
