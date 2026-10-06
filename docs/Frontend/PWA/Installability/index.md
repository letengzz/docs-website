# 安装体验：Manifest 与安装引导

「可安装」是 PWA 四项能力里**成本最低、收益最直接**的一项：不需要写一行缓存逻辑，只要一个 JSON 文件加一个 `<link>`。但它也是最容易「看起来没问题、实际装不上」的一项——因为**浏览器不会告诉你哪里不合格**。

一句话定位：**本页给出 2026 年现行的安装判据（三家浏览器各一套），逐字段讲清 Manifest，并给出 `beforeinstallprompt` 的正确用法与「为什么没有安装按钮」的完整排查表。**

## 一、安装判据：三家浏览器三套规则

先破除一个流传很广的旧公式。

:::danger 「Manifest + Service Worker + HTTPS 才能安装」已经不成立
Chrome 自 **108（Android）/ 112（桌面）** 起移除了「安装必须有带 `fetch` 处理器的 Service Worker」这一门槛；MDN 现行列出的安装判据里**没有 Service Worker**。所以：
- 「只想要桌面图标」→ **不需要 Service Worker**。
- 「写了 Service Worker 就一定能装」→ **不对**，Manifest 不合格照样装不上。
Lighthouse **12.0**（2024-04-22）也已移除 PWA 分类，验收只能看**运行时信号**，不能看分数。
:::

| 判据 | Chromium（Chrome / Edge / Samsung） | Safari（macOS） | Safari（iOS / iPadOS） |
| --- | --- | --- | --- |
| HTTPS（或 localhost） | ✅ 必须 | ✅ 必须 | ✅ 必须 |
| 链接一个可达的 Manifest | ✅ 必须 | ✅ 必须 | ✅ 必须 |
| `name` 或 `short_name` | ✅ 必须 | ✅ 必须 | ✅ 必须 |
| `icons` 含 **192×192 与 512×512** | ✅ 必须 | 参考 | 参考（**`apple-touch-icon` 优先级更高**） |
| `start_url` | ✅ 必须 | ✅ 必须 | ✅ 必须 |
| `display` 为 `standalone`/`fullscreen`/`minimal-ui`（非 `browser`） | ✅ 必须 | 参考 | 参考 |
| `prefer_related_applications` | 必须为 `false` 或缺省 | — | — |
| Service Worker | **不要求** | 不要求 | 不要求 |
| 程序化安装 API | `beforeinstallprompt` | ❌ 无 | ❌ 无 |
| 安装入口 | 地址栏图标 / 菜单「安装」 | 菜单「添加到程序坞」 | **仅**「分享 → 添加到主屏幕」 |
| 安装产物 | WebAPK（Android） | Web App | Web Clip（本质是书签） |

## 二、Manifest 逐字段

```json [public/manifest.webmanifest]
{
  "name": "博客平台",
  "short_name": "博客",
  "description": "个人技术博客：文章、评论与全文搜索",
  "id": "/?source=pwa",
  "start_url": "/?source=pwa",
  "scope": "/",
  "display": "standalone",
  "theme_color": "#2563eb",
  "background_color": "#ffffff",
  "lang": "zh-CN",
  "dir": "ltr",
  "orientation": "portrait-primary",
  "categories": ["news", "productivity"],
  "icons": [
    { "src": "/icons/pwa-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/pwa-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ],
  "screenshots": [
    { "src": "/screenshots/home-wide.png", "sizes": "1280x720", "type": "image/png", "form_factor": "wide" },
    { "src": "/screenshots/home-narrow.png", "sizes": "720x1280", "type": "image/png", "form_factor": "narrow" }
  ],
  "shortcuts": [
    { "name": "写文章", "url": "/admin/posts/new", "icons": [{ "src": "/icons/shortcut-write.png", "sizes": "96x96" }] }
  ]
}
```

按作用分组：

| 分组 | 字段 | 作用 | 不写的后果 |
| --- | --- | --- | --- |
| **门槛** | `name` / `short_name` | 安装后的应用名 | 装不上 |
| | `icons`（192 + 512） | 图标 | 装不上；或主屏显示白块 |
| | `start_url` | 从图标启动时打开的 URL | 装不上 |
| | `display` | 独立窗口 / 全屏 | `browser` 会失去独立窗口，装上也像书签 |
| | `prefer_related_applications` | 必须 `false` 或缺省 | 为 `true` 时浏览器转向推应用商店 |
| **观感** | `id` | **应用身份**。缺省时由 `start_url` 推导 | 日后改 `start_url` 会被当成**另一个应用**，产生两个图标 |
| | `scope` | 哪些 URL 算在应用内 | 超出 scope 的链接会跳浏览器，破坏沉浸感 |
| | `theme_color` / `background_color` | 工具栏色与启动闪屏底色 | 缺 `background_color` 会白闪一下 |
| | `icons[].purpose: "maskable"` | 让 Android 自适应裁切 | 图标被裁出白边或被切掉内容 |
| | `screenshots` / `description` | 让安装弹窗变成「应用商店样式」 | 只显示一行朴素提示 |
| | `shortcuts` | 长按图标出现快捷入口 | 少一个入口 |
| **元信息** | `lang` / `dir` | 语言与书写方向 | 影响字体选择与 RTL 布局 |

:::danger 三个 Manifest 高频错误
1. **把 `maskable` 图标当成普通图标用同一张图**。maskable 要求内容集中在**中心 80% 的安全区**内，普通图标直接当 maskable 会被裁掉边缘。正确做法：出两张图，普通图标留白边距，maskable 缩小内容。
2. **`start_url` 写成绝对外部地址**（如 `https://example.com/home`）。跨源 `start_url` 会被判为不合格。正确做法：用**相对本站的路径**，推荐 `/?source=pwa` 这种可统计的形式。
3. **`display: "browser"`**。它等于明确告诉浏览器「这就是普通网页」，安装入口直接不出现。正确做法：`standalone` 是绝大多数场景的正解。
:::

### 引用与 Content-Type

```html [index.html]
<link rel="manifest" href="/manifest.webmanifest" />
<meta name="theme-color" content="#2563eb" />
<!-- iOS：Safari 优先读 apple-touch-icon，manifest 的 icons 只是参考 -->
<link rel="apple-touch-icon" sizes="180x180" href="/icons/apple-touch-icon-180.png" />
```

服务器侧要保证两件事：**`.webmanifest` 的 MIME 类型是 `application/manifest+json`**（有些服务器默认给成 `text/plain`，Chromium 会拒绝），以及**该文件不需要鉴权**。用 Nginx 时：

```nginx
location = /manifest.webmanifest {
  default_type application/manifest+json;
  add_header Cache-Control "no-cache";
}
```

:::warning 一个静默失败的场景
Manifest **必须能被匿名 GET 到**。如果它被放在需要登录的路径下、或被 CORS / WAF 拦掉，浏览器**不会报错**，只是永远不给安装入口。排查时**用无痕窗口直接访问 manifest URL**，确认能看到 JSON。
:::

## 三、`beforeinstallprompt` 的正确用法

Chromium 在判定页面「可安装 + 用户有足够参与度」后触发 `beforeinstallprompt`。**它的存在本身就是「可以安装了」的信号**，所以最常见的用法是「用它来控制自定义安装按钮的显隐」。

```js [src/pwa/install.js]
let deferredPrompt = null
const installBtn = document.querySelector('#install-btn')

// ① 事件触发：先阻止默认迷你横幅，把机会留给我们自己的 UI
window.addEventListener('beforeinstallprompt', (event) => {
  event.preventDefault()
  deferredPrompt = event
  // 只有这时才显示按钮；Safari / Firefox 不会触发该事件，按钮也就不会出现
  if (installBtn) installBtn.hidden = false
})

// ② 必须由用户点击触发；且 event 只能用一次（用掉后要重新等事件）
installBtn?.addEventListener('click', async () => {
  if (!deferredPrompt) return
  await deferredPrompt.prompt()
  const { outcome } = await deferredPrompt.userChoice // 'accepted' | 'dismissed'
  // 无论接受还是拒绝，这个 event 都已失效，必须置空
  deferredPrompt = null
  installBtn.hidden = true
  track('pwa_install_prompt', { outcome })
})

// ③ 安装成功后清掉入口（避免已安装还显示按钮）
window.addEventListener('appinstalled', () => {
  deferredPrompt = null
  if (installBtn) installBtn.hidden = true
  track('pwa_installed')
})

// ④ 已经在独立窗口里运行 → 直接不要显示按钮
if (window.matchMedia('(display-mode: standalone)').matches) {
  if (installBtn) installBtn.hidden = true
}
```

四条纪律：

1. **`preventDefault()` 之后一定要自己给入口**。不阻止就是浏览器自己的迷你横幅；阻止了又不给入口，等于把安装机会完全丢掉。
2. **`prompt()` 只能在用户点击里调**。程序化弹出会被忽略，而且会消耗浏览器对该站点的信任。
3. **`event` 是一次性的**。`userChoice` 之后必须置空，否则下次点击会抛错或毫无反应。
4. **`beforeinstallprompt` 不出现 ≠ 出错**。Safari 与 Firefox 根本不实现它；Chromium 也可能因为**参与度不足**或**已安装**而不触发。

## 四、iOS：没有 API，只有手动路径

Safari（iOS 与 macOS）**不实现 `beforeinstallprompt`**，也不提供任何程序化安装 API。iOS 上唯一路径是：**分享按钮 → 添加到主屏幕**。

由此推出三条产品结论：

- **不要渲染一个"点我安装"的按钮然后直接调 `prompt()`**——在 iOS 上它什么都做不了，只会让用户以为按钮坏了。正确做法：iOS 上把这个按钮改成**图文引导**（一张标注「分享 → 添加到主屏幕」的示意）。
- **iOS 上图标以 `apple-touch-icon` 为准**（常用 180×180），manifest 的 `icons` 只作参考。**只配 manifest 会导致 iOS 主屏图标是网页截图**。
- **iOS 的安装成果是 Web Clip（书签）**，不是真正的应用包：不支持 `shortcuts`、`screenshots` 等字段，启动行为也更接近「全屏的网页」。

:::tip 怎么判断用户是「已经装了」还是「只是开着标签页」
```js
// iOS 上 navigator.standalone 是可靠信号；其他平台用 display-mode 媒体查询
const installed =
  window.matchMedia('(display-mode: standalone)').matches ||
  window.matchMedia('(display-mode: fullscreen)').matches ||
  window.navigator.standalone === true
```
这个判断在[推送](../Push/index.md)一节是**先决条件**——iOS 不装到主屏就没有 `PushManager`。
:::

## 五、图标：一套最小清单

用 `@vite-pwa/assets-generator`（**2.0.0**，2026-09-12）从一张 1024×1024 的源图生成全套，避免手搓尺寸：

```shell
pnpm add -D @vite-pwa/assets-generator
pnpm pwa-assets-generator --preset minimal-2023 public/logo.svg
```

生成物与用途：

| 文件 | 尺寸 | 用途 |
| --- | --- | --- |
| `pwa-192.png` | 192×192 | **Manifest 必填**；Android 主屏 |
| `pwa-512.png` | 512×512 | **Manifest 必填**；启动闪屏与安装弹窗 |
| `maskable-512.png` | 512×512 | Android 自适应图标（内容在中心安全区） |
| `apple-touch-icon-180.png` | 180×180 | **iOS 主屏图标（优先级最高）** |
| `favicon.ico` / `favicon.svg` | — | 浏览器标签页 |

## 六、装上之后：三个行为差异

| 行为 | 标签页里（`browser`） | 安装后（`standalone`） |
| --- | --- | --- |
| 窗口 | 有地址栏、有标签页 | 独立窗口（Android 为 WebAPK，接近原生） |
| 返回键 | 浏览器后退 | 系统返回手势；**站点要自己处理内部路由的后退** |
| 冷启动 | 每次访问都可能重新加载 | 从 `start_url` 启动，且同一时刻**通常只有一个实例** |
| 与外部链接 | 同窗口跳转 | **超出 `scope` 的链接会跳转浏览器**，破坏沉浸感 |

:::warning 安装后最常被投诉的两点
1. **「点了返回直接退出应用」**：Standalone 模式下系统返回键会退出应用，而用户以为该回到上一页。正确做法：在 SPA 里接管内部路由的返回（`history.pushState` + `popstate`），并在栈底时不拦截。
2. **「登录后跳出去了」**：OAuth 回调、支付跳转等跨域跳转在 Standalone 下会离开应用窗口。正确做法：把这类流程明确设计为「会离开应用」并在返回后给出明确的状态提示。
:::

## 七、「为什么没有安装按钮」排查表

| 现象 | 可能原因（按概率排序） |
| --- | --- |
| 从来没有迷你横幅，DevTools Manifest 干净 | **Chromium 参与度不足**（需一定停留时间与交互）；或**已经安装过** |
| DevTools → Manifest 面板有红色错误 | Manifest 缺字段 / 图标尺寸不对 / `display: browser` / `prefer_related_applications: true` |
| Manifest 面板显示「无法获取 Manifest」 | 路径 404、MIME 类型不是 `application/manifest+json`、或被鉴权/WAF 拦截 |
| 图标能显示但主屏图标是白块 | 图标不是 PNG、或尺寸声明与实际不符 |
| Chrome 有安装入口，**Safari 完全没有** | **正常**。Safari 无程序化 API，只能「分享 → 添加到主屏幕」 |
| iOS 主屏图标是网页截图 | 缺 `apple-touch-icon`（iOS 优先读它，manifest 的 `icons` 只是参考） |
| 装上了但每次打开都进浏览器 | `display` 不是 `standalone`/`fullscreen`/`minimal-ui` |

## 八、验证方式

```shell
pnpm build && pnpm preview
# 用无痕窗口打开，避免旧 SW 与已安装记录干扰
```

1. `http://localhost:4173/manifest.webmanifest` 直接访问 → 应返回 JSON，且响应头 `Content-Type: application/manifest+json`。
2. DevTools → Application → **Manifest** → 无红色错误；「Installability」区块显示可安装（不同 Chrome 版本措辞不同，关键是**没有报错条目**）。
3. 页面上多停留、点几下（凑参与度），然后刷新 → 地址栏右侧出现安装图标，或**你自己的自定义安装按钮出现**（说明 `beforeinstallprompt` 已触发）。
4. 点击安装按钮 → 系统弹窗出现；安装后重新打开 → 独立窗口、无地址栏。
5. 在页面里执行：

   ```js
   window.matchMedia('(display-mode: standalone)').matches   // 期望 true
   ```

6. 手机端（Android + iOS 各一台真机）：Android 走安装弹窗，iOS 走「分享 → 添加到主屏幕」，确认**主屏图标是品牌图而不是截图**。

## 参考资料

- [MDN：Making PWAs installable](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable)
- [MDN：Web app manifest](https://developer.mozilla.org/en-US/docs/Web/Manifest)
- [web.dev：Installing](https://web.dev/learn/pwa/installation)
- [Chrome：Update on the installability criteria](https://developer.chrome.com/blog/update-install-criteria)
- [Apple：Configuring Web Applications](https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/SafariWebContent/ConfiguringWebApplications/ConfiguringWebApplications.html)
- [@vite-pwa/assets-generator](https://github.com/vite-pwa/assets-generator)
