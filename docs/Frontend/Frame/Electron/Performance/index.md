# Electron 性能优化

Electron 应用的性能问题有三个典型症状：**冷启动慢、内存高、窗口多起来变卡**。它们分别对应不同的根因与手段，先定位是哪一类，再对症下药。

![自动更新与质量保障闭环（含性能观察项）](../assets/electron-lifecycle.svg)

## 一句话定位

Electron 的性能成本来自「**Chromium + Node.js 双运行时**」：它带来了跨平台与 Web 技术栈，代价是启动与内存天然高于原生应用。优化的目标是**把这份成本控制在用户可接受的范围内**，而不是追求原生级指标。

## 三类指标与观测方式

| 指标 | 含义 | 观测方式 |
| --- | --- | --- |
| 冷启动耗时 | 双击图标到首屏可用 | 主进程打点 + 打包后实测 |
| 内存占用 | 主进程 + 各渲染进程之和 | 系统任务管理器 / 开发者工具任务管理器 |
| 交互流畅度 | 滚动、动画、输入响应 | DevTools Performance 面板 |
| 包体积 | 安装包与安装后占用 | 产物与安装目录大小 |

::: danger 注意
**必须测打包后的产物，而不是开发环境**。开发环境有 sourcemap、HMR 客户端、未压缩代码，指标与真实产物差异极大。**用 `--dev` 启动测出来的启动时间没有参考意义。**
:::

## 一、冷启动优化

启动耗时的构成：

```text
系统加载可执行文件 → 启动 Node/Chromium → 主进程执行 app.whenReady → 创建窗口
→ 渲染进程加载 HTML/JS → 首屏渲染完成
```

优化手段按收益排序：

| 手段 | 说明 | 收益 |
| --- | --- | --- |
| 延迟加载非首屏模块 | 主进程 `require` 放在真正用到时（或 `await import()`） | 高 |
| 减少 `app.whenReady` 前的工作 | 把初始化逻辑推到窗口创建之后 | 高 |
| 移除首屏不需要的渲染逻辑 | 首屏只渲染可见内容，其余异步 | 高 |
| 开启 V8 代码缓存 / 字节码保护 | 新版构建工具支持预编译，减少解析开销 | 中 |
| 用 `ready-to-show` 再显示窗口 | 避免先出现白屏再填充 | 中（体感） |
| 精简依赖 | 减少解析与执行代码量 | 中 |

```javascript [main.js]
const { app, BrowserWindow } = require('electron')

app.whenReady().then(() => {
  const win = new BrowserWindow({
    show: false,                      // 先不显示，避免白屏
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      preload: require('node:path').join(__dirname, 'preload.js'),
    },
  })

  win.once('ready-to-show', () => win.show())   // 准备好再显示
  win.loadFile('index.html')
})
```

::: tip 建议
**用「打点」代替猜测**：在主进程入口记 `process.hrtime()`，在窗口 `ready-to-show` 再记一次，把差值上报到日志。有了真实数据，才知道优化该从哪一步下手。
:::

```javascript [main.js · 启动打点]
const start = process.hrtime.bigint()

app.whenReady().then(() => {
  const win = new BrowserWindow({ show: false })
  win.once('ready-to-show', () => {
    const ms = Number(process.hrtime.bigint() - start) / 1e6
    console.log(`启动到可显示耗时：${ms.toFixed(1)}ms`)
    win.show()
  })
  win.loadFile('index.html')
})
```

## 二、内存优化

Electron 的内存 = 主进程 + 每个渲染进程 + 每个工具进程。多窗口应用的内存会随窗口数线性增长。

| 问题 | 原因 | 手段 |
| --- | --- | --- |
| 窗口关闭后内存不降 | 渲染进程未释放、监听未移除 | 关闭时移除监听、销毁引用 |
| 多窗口内存翻倍 | 每个窗口独立加载同一套资源 | 共享会话（session）、减少每窗口资源 |
| 内存缓慢上涨 | 事件监听或缓存无限增长 | 定位泄漏：对比多次操作前后的堆快照 |
| 长会话内存高 | 大数据长期驻留 | 分页、及时释放、用磁盘缓存替代内存缓存 |

```javascript [main.js · 关闭窗口时清理]
win.on('closed', () => {
  // 移除挂在该窗口上的监听，避免引用残留
  ipcMain.removeHandler('fs:read')
  ipcMain.removeHandler('fs:write')
  win = null
})
```

::: danger 注意
1. **`ipcMain.handle` 是全局注册的**：窗口关闭后如果重新创建窗口并再次 `handle` 同一 channel，会抛「Handler already registered」。正确做法是**只注册一次**（应用级），或关闭时 `removeHandler`。
2. **`ipcRenderer.on` 的监听若不移除**，页面重新加载后会叠加，导致一次消息触发多次回调——这是「内存与 CPU 双涨」的经典原因。
3. **不要把大数组长期放在全局变量里**：桌面应用往往长时间不关闭，任何「慢慢涨」的泄漏都会被放大。
:::

## 三、渲染与交互优化

渲染进程就是 Chromium，因此**通用前端性能手段全部适用**：

| 手段 | 说明 |
| --- | --- |
| 虚拟列表 | 长列表只渲染可视区域 |
| 减少重排重绘 | 用 `transform` / `opacity` 做动画 |
| 避免主线程长任务 | 重计算移出渲染主线程（Web Worker） |
| 图片与字体优化 | 压缩、按需加载、`font-display: swap` |
| 代码分割 | 路由级懒加载，减小首屏 JS |

具体做法见 [前端性能优化专题](../../../Others/PerformanceOptimization/index.md)。

## 四、进程与任务分配

把任务放对进程，本身就是性能优化：

| 任务 | 建议位置 | 原因 |
| --- | --- | --- |
| 界面渲染、用户交互 | 渲染进程 | 天然职责 |
| 文件读写、系统调用 | 主进程 | 需要 Node 能力 |
| 密集计算（解析、加解密） | 工具进程 / Web Worker | 不阻塞界面与主进程 |
| 定时轮询、后台同步 | 主进程（注意别阻塞） | 与界面解耦 |

```javascript [main.js · 用工具进程做重计算]
const { utilityProcess } = require('electron')
const path = require('node:path')

const worker = utilityProcess.fork(path.join(__dirname, 'heavy-worker.js'))
worker.postMessage({ type: 'parse-large-file', file: 'big.json' })
worker.on('message', (result) => {
  // 结果回到主进程，再由主进程推送给界面
  mainWindow?.webContents.send('parse:done', result)
})
```

## 五、包体积与安装体验

| 手段 | 说明 |
| --- | --- |
| 压缩 `dependencies` | 只保留运行时真正需要的包 |
| 用 `files` 白名单 | 精确控制打进 `asar` 的内容 |
| 移除 sourcemap | 生产包不携带 `.map` |
| 按平台构建 | 每个平台只出对应产物，不交叉包含 |
| 检查 `asar` 内容 | 用 `npx asar list app.asar` 核对，找出多余文件 |

## 优化清单

| 类别 | 检查项 |
| --- | --- |
| 启动 | 首屏模块是否懒加载？是否用 `ready-to-show`？依赖是否精简？ |
| 内存 | 窗口关闭是否清理监听与 handler？是否存在无限增长的缓存？ |
| 渲染 | 长列表是否虚拟化？是否有长任务阻塞主线程？ |
| 进程 | 重计算是否已移出主进程？ |
| 体积 | `asar` 是否只含必要文件？是否已移除 sourcemap？ |
| 度量 | 是否在打包产物上测过启动耗时与内存？ |

## 验证方式

1. 用打包产物实测冷启动耗时，并记录到基线；做一次优化后再测，对比是否有改善。
2. 打开多个窗口，在系统任务管理器中观察内存随窗口数增长的幅度，关闭后确认能回落。
3. 反复开关同一窗口 10 次，确认内存不持续上涨（排除 `ipcMain.handle` 重复注册与监听叠加）。
4. 在开发者工具 Performance 面板录制一次滚动，确认没有超过 50ms 的长任务。

## 相关专题

- [Electron 进程](../Process/index.md)：任务该放在哪个进程
- [Electron 构建工具](../BuildingTools/index.md)：包体积与产物组成
- [Electron 自动更新](../AutoUpdate/index.md)：后台更新对启动的影响
- [前端性能优化专题](../../../Others/PerformanceOptimization/index.md)：通用前端手段
- [Electron 自动化测试](../Testing/index.md)：把启动与内存纳入观测

## 参考资料

- Electron 官方文档 · 性能：https://www.electronjs.org/zh/docs/latest/tutorial/performance
- Chrome DevTools · Performance 面板：https://developer.chrome.com/docs/devtools/performance/
- 前端性能优化专题：见 [性能指标与评估](../../../Others/PerformanceOptimization/Metrics/index.md)
