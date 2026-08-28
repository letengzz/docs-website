# 性能指标

性能优化的前提是**可测量**。Core Web Vitals（核心 Web 指标）是 Google 与行业通用的量化标准：LCP、INP、CLS。

## 核心 Web Vitals

| 指标 | 含义 | 达标 |
| --- | --- | --- |
| LCP | 最大内容绘制（首屏主要内容） | ≤ 2.5s |
| INP | 交互到下一次绘制延迟 | ≤ 200ms |
| CLS | 累计布局偏移 | ≤ 0.1 |

## 常用性能指标

| 指标 | 含义 |
| --- | --- |
| TTFB | 首字节时间（网络+后端） |
| FCP | 首次内容绘制 |
| FID（已废弃） | 首次输入延迟（被 INP 取代） |
| TBT | 主线程阻塞总时间 |
| SI | 视觉稳定性 |

## 用 Lighthouse 测量

```shell
npx lighthouse https://example.com --view
```

或 DevTools → Lighthouse 面板。

## 指标优化方向

### LCP（≤2.5s）

1. 压缩/裁剪首屏图片，`fetchpriority="high"`。
2. 关键 CSS 内联，去掉渲染阻塞脚本。
3. CDN + HTTP/2 + 预连接。
4. 服务端渲染/预渲染。

### INP（≤200ms）

1. 长任务拆分，主线程空闲。
2. 事件处理轻量化，避免同步重布局。
3. 大列表虚拟化。
4. 用 Web Worker 做重计算。

### CLS（≤0.1）

1. 图片/广告位预留尺寸（width/height、aspect-ratio）。
2. 字体加载用 `font-display: swap`。
3. 动态内容预留空间，避免插入即跳动。

## 性能预算

```text
首屏 JS ≤ 200KB（gzip）
LCP ≤ 2.5s
INP ≤ 200ms
CLS ≤ 0.1
```

把预算写进 CI，超预算构建失败。

## 易错点

::: danger 常见错误
1. 只看本地/公司网络：用 Lighthouse 预设的 Mobile + Slow 4G。
2. 图片不设尺寸：首屏加载后布局跳动，CLS 飙升。
3. 全量引入大依赖：按需引入 + Tree-shaking。
4. 忽略第三方脚本：广告/统计脚本阻塞主线程。
5. 用 FID 评估现代站点：已被 INP 取代。
6. 指标只在优化后测一次：上线后持续监控（RUM）。
:::

## 验证方式

1. Lighthouse 跑一轮，记录五项分数。
2. Performance 面板录制，定位 Long Task 与布局抖动。
3. 用 web-vitals 库接入线上 RUM 监控。

## 参考资料

- Core Web Vitals：https://web.dev/learn-core-web-vitals/
- Lighthouse：https://developer.chrome.com/docs/lighthouse/overview/
- web-vitals：https://github.com/GoogleChrome/web-vitals
