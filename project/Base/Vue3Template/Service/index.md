# 配置服务

vite.config.ts配置：

```typescript [vite.config.ts]
// ...

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // 根据当前工作目录中的 `mode` 加载 .env 文件
  // 设置第三个参数为 '' 来加载所有环境变量，而不管是否有
  // `VITE_` 前缀。
  const env = loadEnv(mode, process.cwd(), '')
  const { VITE_VERSION, VITE_BASE_URL, VITE_API_URL } = env
  const isHttps = httpsRE.test(VITE_API_URL) // [!code focus] [!code ++]
  console.log(`🚀 API_URL = ${VITE_API_URL}`)
  console.log(`🚀 VERSION = ${VITE_VERSION}`)
  return {
    // vite 配置
    // ...
    server: {
      // [!code focus] [!code ++]
      // 监听所有公共ip  // [!code focus] [!code ++]
      host: '0.0.0.0', // [!code focus] [!code ++]
      // cors: true,  // [!code focus] [!code ++]
      hmr: true, // [!code focus] [!code ++]
      port: Number(env.VITE_PORT) || 3000, // 👈 将端口转换为 number，默认 3000  // [!code focus] [!code ++]
      proxy: {
        // [!code focus] [!code ++]
        '/api': {
          // [!code focus] [!code ++]
          target: VITE_API_URL, // [!code focus] [!code ++]
          changeOrigin: true, // [!code focus] [!code ++]
          ws: true, // [!code focus] [!code ++]
          rewrite: (path: string) => path.replace(/^\/api/, ''), // [!code focus] [!code ++]
          ...(isHttps ? { secure: false } : {}), // [!code focus] [!code ++]
        }, // [!code focus] [!code ++]
      }, // [!code focus] [!code ++]
      // 提前转换和缓存文件以进行预热。可以在服务器启动时提高初始页面加载速度，并防止转换瀑布。  // [!code focus] [!code ++]
      warmup: {
        // [!code focus] [!code ++]
        // 请注意，只应该预热频繁使用的文件，以免在启动时过载 Vite 开发服务器  // [!code focus] [!code ++]
        // 可以通过运行 npx vite --debug transform 并检查日志来找到频繁使用的文件  // [!code focus] [!code ++]
        clientFiles: ['./index.html', './src/{components,api}/*'], // [!code focus] [!code ++]
      }, // [!code focus] [!code ++]
    }, // [!code focus] [!code ++]
    // ...
  }
})
```

在环境文件中添加：

::: code-group

```properties [.env]{12-13}
# 通用环境变量

# 项目名称
VITE_APP_TITLE = 'base-vue3-template'
# 版本号
VITE_VERSION = 1.0.0
# 端口号
# VITE_PORT = 3000

# 网站地址前缀
VITE_BASE_URL = /
# API 地址前缀
VITE_API_URL = http://localhost:8080
```

```properties [.env.development]{9-10}
# 开发环境变量

# 网站地址前缀
VITE_BASE_URL = /

# 端口号
VITE_PORT = 9999

# API 地址前缀
VITE_API_URL = http://localhost:5173
```

```properties [.env.production]{15-16}
# 生产环境变量

# 网站地址前缀
VITE_BASE_URL = /base/

# 部署线上 第三方库合并为vendor.js
VITE_BUILD_VENDOR = true

# 部署线上 压缩gzip
VITE_BUILD_GZIP = true

# 端口号
VITE_PORT = 5174

# API 地址前缀
VITE_API_URL = http://localhost:8080
```

:::