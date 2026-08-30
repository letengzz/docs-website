# 常见问题与最佳实践

汇总前端性能优化中最高频的问题：优先级、Lab 与 Field、图片与字体、缓存、懒加载与监控选型，方便快速查阅。

## 方向类

### 先优化什么收益最大？

按 ROI 排序：

1. **体积与网络**：图片格式/尺寸、JS 压缩与分包、CDN、缓存——见效最快；
2. **关键路径**：preload LCP、内联关键 CSS、defer 脚本；
3. **运行时**：长任务拆分、虚拟列表；
4. **细节**：字体、动画合成属性。

先测量再决定，但「网络与体积」几乎总是第一步。

### Lighthouse 满分但用户觉得慢？

Lab 是模拟环境，真实用户可能：

- 弱网/4G 不如模拟；
- 低端设备 CPU 慢；
- 用户交互触发长任务；
- 缓存状态、地区 CDN 节点不同。

处理：以 **RUM（Field）为准**，Lab 用于定位与回归。

## 图片类

### 所有图片都转 AVIF 吗？

AVIF 体积最小但**编码慢、解码开销略高**：

- 照片/大图 → AVIF 优先，WebP 兜底；
- 小图标 → SVG；
- 需要兼容（~7% 老浏览器）→ WebP + JPEG fallback（picture 标签）。

### 图片懒加载影响 SEO 吗？

懒加载本身不影响抓取，但：

- LCP 图片**不能懒加载**；
- 确保 `src` 有兜底（无 JS 也能显示）；
- 用原生 `loading="lazy"`，避免脚本方案失败导致图片不显示。

## 字体类

### 字体加载导致文字闪烁（FOUT）怎么办？

`font-display: swap` 必然先显示回退字体再替换。想要更平滑：

1. 只 preload 首屏字体；
2. 子集化减小字体体积；
3. 关键文字接受 swap（默认推荐，CLS 用 `size-adjust` 缓解）；
4. 次要字体用 `optional` 直接放弃加载。

### 中文站字体优化怎么做？

中文字体几 MB，**必须子集化**：只打包页面用到的字符（常用 2000~3500 字），或用「按需字体」方案（fontmin、字蛛、在线子集化服务）。图标用 SVG/图标字体替代。

## 缓存类

### 为什么改了代码用户还是旧版？

排查：

1. 资源是否带 hash（`app.a1b2c3.js`）？不带 hash 会被浏览器/CDN 缓存；
2. HTML 是否被 CDN 长缓存？HTML 必须 `no-cache`；
3. 发布后 CDN 缓存是否 purge；
4. Service Worker 是否缓存了旧资源（需要版本管理）。

### 缓存与更新的平衡？

- 带 hash 资源：`immutable` 长缓存（1 年）；
- HTML：`no-cache`；
- 版本发布：新 hash 自动换新 URL，无需清缓存；
- 紧急修复：CDN purge + 短缓存过渡。

## 运行时类

### 页面越来越卡是什么原因？

大概率**内存泄漏**：

1. DevTools Memory 快照对比找增长对象；
2. 检查未清理的监听器、定时器、全局引用；
3. 检查 SPA 路由切换后旧组件是否被回收；
4. 检查大对象缓存是否无限增长。

### 数据量大，列表渲染卡怎么办？

- 数据量 < 1000：分页或「增量渲染」即可；
- 数据量大：虚拟列表（vue-virtual-scroller / @tanstack/virtual）；
- 纯展示列表：考虑服务端分页。

## 监控类

### 自建 RUM 还是用现成平台？

| 维度 | 自建 | 现成平台 |
| --- | --- | --- |
| 成本 | 存储与开发成本 | 按量付费 |
| 灵活性 | 完全可控 | 受平台限制 |
| 上手 | 慢 | 快（Sentry/Vercel 分钟级） |
| 数据主权 | 自持 | 第三方 |

小团队先上 Sentry/Vercel，规模大了再自建。

### 性能预算真的有用吗？

有用，但前提是**接入 CI**：

- 体积预算（size-limit）：PR 超预算即失败；
- 指标预算（Lighthouse CI）：LCP/CLS 超标即失败；
- 预算要「逐步收紧」，一开始定太严会天天失败。

## 最佳实践清单

::: tip 性能优化检查清单
1. 是否先测量基线（Lab + Field）？
2. LCP 资源是否 preload、图片是否 WebP/AVIF + 尺寸预留？
3. 首屏 JS 是否 ≤ 200KB（gzip）、路由是否懒加载？
4. 非首屏图片是否懒加载、字体是否子集化 + swap？
5. 脚本是否 defer、关键 CSS 是否内联？
6. 是否有长任务（>50ms）与强制同步布局？
7. 缓存策略是否「hash 长缓存 + HTML no-cache」？
8. 是否接入 RUM 监控与性能预算 CI？
9. 是否定期检查内存泄漏与依赖体积？
10. 优化是否有复测对比与回归防线？
:::

## 参考资料

- [web.dev：性能学习路径](https://web.dev/articles/learn-performance)
- [MDN：性能优化](https://developer.mozilla.org/zh-CN/docs/Web/Performance)
- [Lighthouse](https://developer.chrome.com/docs/lighthouse)
- [PageSpeed Insights](https://pagespeed.web.dev/)
