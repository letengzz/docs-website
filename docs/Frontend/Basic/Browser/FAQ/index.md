# 常见问题与最佳实践

这一篇汇总浏览器原理高频问题与团队实践，覆盖渲染、缓存、安全、性能与调试。

## 常见问题

### 1. 为什么 `setTimeout(0)` 不立即执行

它进入宏任务队列，必须等当前同步代码和微任务清空后才执行。顺序：同步 → 微任务 → 宏任务。

### 2. 页面卡顿怎么定位

DevTools → Performance 录制，找 Long Task（>50ms）与 Layout/Paint 高峰；再用 Lighthouse 看指标归属。

### 3. 首屏慢在哪

按链路段看：TTFB（网络/后端）→ 资源加载（体积/阻塞）→ 渲染（布局/绘制）。Network 与 Performance 面板配合。

### 4. 为什么改了代码页面还是旧的

强缓存命中：JS/CSS 用 hash 文件名 + 长缓存；HTML 用 `no-cache`；调试时禁用缓存。

### 5. localStorage 能存敏感信息吗

不建议。XSS 一次即泄露，认证凭证用 HttpOnly Cookie + 后端校验。

### 6. 动画卡顿

动画用 `transform` / `opacity`（只触发合成），避免改 `left/top`（触发重排）。

### 7. 前端如何防 XSS

输出转义、CSP 限制脚本来源、Cookie HttpOnly、输入白名单；富文本用成熟库清洗。

### 8. CLS 为什么一直很高

图片/字体/动态内容没预留空间。给图片设宽高或 aspect-ratio，字体 `font-display: swap`。

### 9. 事件循环里渲染什么时候发生

一帧内，宏任务与微任务之后、下一宏任务之前；`requestAnimationFrame` 在渲染前执行。

### 10. 性能优化从哪开始

先测量：Lighthouse + Performance + 线上 RUM；再按 LCP/INP/CLS 优先级优化，改完回归对比。

## 最佳实践清单

::: tip 可直接落地的清单
1. 缓存策略：HTML `no-cache`，hash 静态资源长缓存。
2. 图片设尺寸 + 懒加载，首屏图加 fetchpriority。
3. 动画只用 transform/opacity。
4. 安全头齐全：CSP、HSTS、nosniff、frame-ancestors。
5. Cookie 加 HttpOnly + SameSite。
6. 长任务拆分，重计算进 Worker。
7. 建立性能预算并接入 CI。
8. 上线后接 RUM 持续监控。
9. 跨源数据用 postMessage，不信任输入。
10. 疑难问题用 Performance/Network/Application 面板定位，不靠猜。
:::

## 验证方式

1. 对 FAQ 10 问各做一次最小实验。
2. 用 DevTools 完整走一遍“卡顿定位”流程。
3. 用 Lighthouse CI 把性能预算接入流水线。

## 参考资料

- 浏览器工作原理：https://web.dev/learn/performance/
- DevTools 文档：https://developer.chrome.com/docs/devtools/
- MDN Web 性能：https://developer.mozilla.org/zh-CN/docs/Web/Performance
