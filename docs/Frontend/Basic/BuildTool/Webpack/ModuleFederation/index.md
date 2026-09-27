# Webpack 模块联邦

**模块联邦（Module Federation，简称 MF）让多个独立构建、独立部署的应用在运行时共享模块**。它是微前端落地的核心机制，也是 Webpack 5 相比 4 最具分量的能力之一。

![Module Federation：运行时共享模块](../assets/webpack-mf.svg)

## 一句话定位

传统的「共享」发生在**构建期**（npm 包、monorepo 软链）；模块联邦的共享发生在**运行时**——宿主应用在浏览器里动态加载远程应用暴露的模块，因此各应用可以独立发版、互不阻塞。

## 三个核心角色

| 角色 | 配置项 | 职责 |
| --- | --- | --- |
| **Host**（宿主） | `remotes` | 声明要消费哪些远程模块 |
| **Remote**（远程） | `exposes` | 声明对外暴露哪些模块 |
| **Shared**（共享依赖） | `shared` | 声明运行时共享的依赖（如 React） |

```text
Host  ──请求 remoteEntry.js──▶  Remote
  │                                │
  └──── 加载 exposes 的模块 ◀──────┘
           │
      shared 里的 react 只加载一份
```

## 最小可运行示例

### Remote 应用（被消费方）

```javascript [remote/webpack.config.js]
const { ModuleFederationPlugin } = require('webpack').container;
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  mode: 'development',
  devtool: false,
  entry: './src/index.js',
  output: {
    publicPath: 'http://localhost:3001/',
    clean: true,
  },
  devServer: { port: 3001, headers: { 'Access-Control-Allow-Origin': '*' } },
  plugins: [
    new ModuleFederationPlugin({
      name: 'remoteApp',
      filename: 'remoteEntry.js',          // 远程入口清单
      exposes: {
        './Button': './src/Button.js',     // 对外暴露的模块
      },
      shared: { react: { singleton: true }, 'react-dom': { singleton: true } },
    }),
    new HtmlWebpackPlugin({ template: './public/index.html' }),
  ],
};
```

```javascript [remote/src/Button.js]
import React from 'react';

export default function Button({ children }) {
  return <button style={{ background: '#3b82f6', color: '#fff' }}>{children}</button>;
}
```

### Host 应用（消费方）

```javascript [host/webpack.config.js]
const { ModuleFederationPlugin } = require('webpack').container;

module.exports = {
  mode: 'development',
  devtool: false,
  output: { publicPath: 'http://localhost:3000/', clean: true },
  devServer: { port: 3000 },
  plugins: [
    new ModuleFederationPlugin({
      name: 'hostApp',
      remotes: {
        // key 是使用时的前缀，值是"远程名@远程入口地址"
        remoteApp: 'remoteApp@http://localhost:3001/remoteEntry.js',
      },
      shared: { react: { singleton: true }, 'react-dom': { singleton: true } },
    }),
  ],
};
```

```javascript [host/src/index.js]
import React, { lazy, Suspense } from 'react';
import { createRoot } from 'react-dom/client';

// 从远程应用加载 Button
const RemoteButton = lazy(() => import('remoteApp/Button'));

function App() {
  return (
    <Suspense fallback={<p>loading remote module...</p>}>
      <RemoteButton>来自远程的按钮</RemoteButton>
    </Suspense>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

```shell
# 终端 1：启动远程
cd remote && npx webpack serve

# 终端 2：启动宿主
cd host && npx webpack serve
```

**验证**：访问 `http://localhost:3000`，页面渲染出远程应用的按钮，且网络面板中 `remoteEntry.js` 加载成功、`react` 只加载一份。

::: danger 注意
1. **`output.publicPath` 必须是远程应用的绝对地址**：写相对路径会导致宿主从自己的域名去找 `remoteEntry.js`，必然 404。
2. **CORS**：跨域加载远程 chunk 需要远程服务返回 `Access-Control-Allow-Origin`，开发环境在 `devServer.headers` 里加。
3. **`shared` 里必须 `singleton: true`**：React、Vue 这类要求全局单例的库，若不设单例会出现「两份 React 实例」，`Context` 失效、Hooks 报错。
4. **版本要匹配**，否则运行时报 `Unsatisfied version` 或直接白屏。
:::

## shared 的版本策略

```javascript
shared: {
  react: {
    singleton: true,             // 全局只保留一份
    requiredVersion: '^19.0.0',  // 宿主对版本的要求
    eager: false,                // 是否把共享依赖打进初始包
    strictVersion: false,        // 版本不满足时是否硬报错
  },
}
```

| 选项 | 说明 |
| --- | --- |
| `singleton` | 只保留一个实例，避免多实例问题 |
| `requiredVersion` | 声明可接受的版本范围 |
| `eager` | `true` 表示立即加载（不异步），会增大初始包 |
| `strictVersion` | 版本不符时是否直接抛错（调试期建议 `true`，便于暴露问题） |

::: warning 说明
`eager: true` 能让共享模块同步可用（某些场景下 `lazy` 无法正常工作），代价是**共享依赖会被打进每个应用的初始包**，失去「只加载一份」的优势。除非有明确的同步加载需求，否则保持 `false`。
:::

## 典型应用场景

| 场景 | 说明 |
| --- | --- |
| **微前端** | 多个团队独立交付模块，主应用负责编排 |
| **跨应用复用** | 组件库、工具函数在多个站点间运行时共享 |
| **渐进式迁移** | 老应用暴露模块，新应用逐步接管部分页面 |
| **插件化系统** | 第三方在运行时交付功能插件 |

## 与「构建期共享」的对比

| 维度 | npm 包 / monorepo | 模块联邦 |
| --- | --- | --- |
| 共享时机 | 构建期 | 运行时 |
| 发版耦合 | 需重新构建宿主 | 各自独立发版 |
| 依赖重复 | 各应用各自打包 | 可运行时共享 |
| 调试复杂度 | 低 | 高（跨应用链路） |
| 失败影响面 | 构建失败 | 运行时可能白屏 |

## 代价与风险

| 风险 | 缓解 |
| --- | --- |
| 版本不匹配运行时报错 | `shared` 明确 `requiredVersion`，CI 校验版本 |
| 远程不可用导致整页白屏 | 用 `lazy` + `Suspense` / 错误边界兜底 |
| 调试链路长 | 开发环境保证 sourcemap 可用，日志带应用标识 |
| 循环依赖 | 明确依赖方向：宿主依赖远程，远程不反向依赖宿主 |
| 首屏依赖远程可用性 | 关键路径模块不要放远程 |

::: danger 注意
**不要让远程模块成为首屏阻塞项**。远程服务挂了、网络慢，都会直接拖垮宿主。把远程加载限制在非关键路径，并配置降级方案（加载失败时渲染本地兜底组件）。
:::

## 与 Vite / 现代方案的关系

Vite 生态通过 `@originjs/vite-plugin-federation` 与 `@module-federation/enhanced` 支持 MF，但实现路径与 Webpack 不同（Vite 的开发期是 No-Bundle，需要额外协调）。跨构建工具共享时，务必对齐 **shared 依赖的版本与单例策略**，否则仍会出现多实例。

## 与运行时集成（qiankun）的分工

Module Federation 常被当作「微前端的实现」，但它只是**构建期集成**的一种手段。与运行时集成（qiankun / single-spa）的分工需要先认清，否则会在「该不该有沙箱」「独立部署怎么回滚」这类问题上反复摇摆。

| 维度 | 构建期集成（本页的 Module Federation） | 运行时集成（qiankun） |
| --- | --- | --- |
| 远程内容的形态 | **模块**（被 `import` 的代码） | **应用**（有生命周期、有容器） |
| 独立路由 / URL | 通常没有（作为宿主的子路由） | **有**，可独立访问、可分享链接 |
| 隔离能力 | **无**（共享运行时，全局变量直接互通） | 有沙箱（JS + 样式） |
| 依赖去重 | **`shared` 按 semver 自动去重，最优** | 需手动 external + 挂全局 |
| 版本冲突 | **可编译期检测**（`requiredVersion`） | 可能同时加载两份框架，运行时才发现 |
| 首屏 | 构建期可知，可预加载优化 | 运行时才知道要加载什么 |
| 技术栈异构 | 支持，但共享依赖会很别扭 | 支持（各自带运行时） |

::: tip 一句话分工
**「需要独立部署的应用，且有隔离需求」→ qiankun；「同一产品内分包解耦，追求体积最优」→ Module Federation。**

实践中最稳的组合是**两者互补**：用 Module Federation 共享基础库与组件库（Vue、UI 库、工具函数），用 qiankun 做应用级集成。代价是同时引入两套复杂度，只在确有必要时使用。

完整的架构取舍（拆分维度、边界判据、通信协议、独立部署与回滚）见 [微前端](../../../../MicroFrontend/index.md)：[拆分策略](../../../../MicroFrontend/Overview/index.md)、[运行时集成与沙箱](../../../../MicroFrontend/Runtime/index.md)、[工程化与独立部署](../../../../MicroFrontend/Practice/index.md)。
:::

::: danger 注意：把 Module Federation 当微前端用时最容易忽略的两件事
1. **远程模块没有沙箱**：它和宿主共享同一个 `window`、同一份 Vue 实例、同一个全局样式作用域。远程模块里写一条 `body { font-size: 14px }` 会直接改掉宿主的样式。
2. **远程模块的版本兼容靠 `requiredVersion` 兜底，不靠约定**。声明 `{ vue: { requiredVersion: '^3.5.0', singleton: true } }`，让不满足的版本在**构建期**就报错——比运行时出现「响应式行为不一致」好排查得多。
:::

## 参考资料

- [Webpack 官方 Module Federation](https://webpack.js.org/concepts/module-federation/)
- [Module Federation 官方站点](https://module-federation.io/)
- [Vite 模块联邦插件](https://github.com/originjs/vite-plugin-federation)
