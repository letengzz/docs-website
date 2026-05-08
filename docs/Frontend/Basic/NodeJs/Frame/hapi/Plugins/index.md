# Hapi 插件系统

Hapi 拥有强大的插件系统，支持模块化和代码复用。

- 官方文档：https://hapi.dev/api/?v=21.3.2#-serverregisterplugins-options

## 插件基础

### 创建插件

```js [plugin.js]
const myPlugin = {
  name: 'myPlugin',
  version: '1.0.0',
  register: async (server, options) => {
    // 注册路由
    server.route({
      method: 'GET',
      path: '/plugin',
      handler: (request, h) => {
        return { message: '来自插件', options }
      }
    })
    
    // 注册扩展
    server.ext('onRequest', (request, h) => {
      console.log('请求开始')
      return h.continue
    })
  }
}

module.exports = myPlugin
```

### 注册插件

```js [register.js]
const Hapi = require('@hapi/hapi')
const myPlugin = require('./myPlugin')

const init = async () => {
  const server = Hapi.server({ port: 3000 })
  
  // 注册单个插件
  await server.register(myPlugin)
  
  // 注册多个插件
  await server.register([
    myPlugin,
    require('./otherPlugin')
  ])
  
  // 带选项注册
  await server.register({
    plugin: myPlugin,
    options: { prefix: '/api' }
  })
  
  await server.start()
}

init()
```

## 常用插件

### @hapi/inert - 静态文件

```shell [install-inert.sh]
npm i @hapi/inert
```

```js [inert.js]
const Inert = require('@hapi/inert')

await server.register(Inert)

// 静态文件路由
server.route({
  method: 'GET',
  path: '/{param*}',
  handler: {
    directory: {
      path: 'public',
      listing: false,
      index: ['index.html']
    }
  }
})

// 单个文件
server.route({
  method: 'GET',
  path: '/file',
  handler: {
    file: 'public/file.txt'
  }
})
```

### @hapi/vision - 模板引擎

```shell [install-vision.sh]
npm i @hapi/vision
```

```js [vision.js]
const Vision = require('@hapi/vision')
const Handlebars = require('handlebars')

await server.register(Vision)

server.views({
  engines: {
    html: Handlebars
  },
  path: __dirname + '/templates',
  isCached: process.env.NODE_ENV === 'production'
})

server.route({
  method: 'GET',
  path: '/',
  handler: (request, h) => {
    return h.view('index', {
      title: '首页',
      users: [
        { name: '张三' },
        { name: '李四' }
      ]
    })
  }
})
```

### @hapi/basic - 基础认证

```shell [install-basic.sh]
npm i @hapi/basic
```

```js [basic-auth.js]
const Basic = require('@hapi/basic')

await server.register(Basic)

// 验证函数
const validate = async (request, username, password, h) => {
  const users = {
    admin: { password: 'admin123', name: '管理员' }
  }
  
  const user = users[username]
  
  if (!user || user.password !== password) {
    return { isValid: false }
  }
  
  return { isValid: true, credentials: { name: user.name } }
}

server.auth.strategy('simple', 'basic', { validate })

server.route({
  method: 'GET',
  path: '/protected',
  options: {
    auth: 'simple',
    handler: (request, h) => {
      return { message: '认证成功', user: request.auth.credentials }
    }
  }
})
```

### @hapi/jwt - JWT 认证

```shell [install-jwt.sh]
npm i @hapi/jwt
```

```js [jwt.js]
const Jwt = require('@hapi/jwt')

await server.register(Jwt)

server.auth.strategy('jwt', 'jwt', {
  keys: 'your-secret-key',
  verify: {
    aud: 'your-app',
    iss: 'your-issuer'
  },
  validate: (artifacts, request, h) => {
    return {
      isValid: true,
      credentials: {
        userId: artifacts.decoded.payload.userId
      }
    }
  }
})

server.route({
  method: 'GET',
  path: '/profile',
  options: {
    auth: 'jwt',
    handler: (request, h) => {
      return { userId: request.auth.credentials.userId }
    }
  }
})
```

## 插件依赖

```js [dependencies.js]
const pluginA = {
  name: 'pluginA',
  register: async (server) => {
    server.decorate('server', 'serviceA', {
      getData: () => 'data from A'
    })
  }
}

const pluginB = {
  name: 'pluginB',
  dependencies: ['pluginA'],
  register: async (server) => {
    // 可以使用 pluginA 的装饰
    const data = server.serviceA.getData()
  }
}

await server.register([pluginA, pluginB])
```

## 扩展点

```js [ext.js]
// onRequest - 请求开始时
server.ext('onRequest', (request, h) => {
  console.log('请求开始')
  return h.continue
})

// onPreHandler - 处理程序执行前
server.ext('onPreHandler', (request, h) => {
  console.log('处理前')
  return h.continue
})

// onPreResponse - 响应发送前
server.ext('onPreResponse', (request, h) => {
  console.log('响应前')
  return h.continue
})
```

## 完整示例

```js [full-example.js]
const Hapi = require('@hapi/hapi')

// 用户插件
const usersPlugin = {
  name: 'usersPlugin',
  register: async (server, options) => {
    const users = [
      { id: 1, name: '张三' },
      { id: 2, name: '李四' }
    ]
    
    server.route({
      method: 'GET',
      path: '/users',
      handler: () => users
    })
    
    server.route({
      method: 'GET',
      path: '/users/{id}',
      handler: (request) => {
        const user = users.find(u => u.id === parseInt(request.params.id))
        return user || { error: '用户不存在' }
      }
    })
  }
}

// 认证插件
const authPlugin = {
  name: 'authPlugin',
  dependencies: ['usersPlugin'],
  register: async (server) => {
    server.auth.strategy('simple', 'basic', {
      validate: async (request, username, password) => {
        if (username === 'admin' && password === 'admin') {
          return { isValid: true, credentials: { name: '管理员' } }
        }
        return { isValid: false }
      }
    })
  }
}

const init = async () => {
  const server = Hapi.server({ port: 3000 })
  
  await server.register([usersPlugin, authPlugin])
  
  await server.start()
  console.log('服务启动在', server.info.uri)
}

init()
```

::: tip 提示
- 插件是 Hapi 的核心扩展机制
- 支持依赖声明
- 可以注册路由、扩展、装饰器
:::
