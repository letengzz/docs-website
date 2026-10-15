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

- 前端性能优化专题：[性能指标与评估](../../../Others/PerformanceOptimization/Metrics/index.md)、[监控与性能预算](../../../Others/PerformanceOptimization/Monitoring/index.md)
- Core Web Vitals：https://web.dev/learn-core-web-vitals/
- Lighthouse：https://developer.chrome.com/docs/lighthouse/overview/
- web-vitals：https://github.com/GoogleChrome/web-vitals

## 与移动端 H5 深入的分工（第 142 天补充）


「浏览器渲染与性能」与新增的[移动端 H5 深入](../../../MobileH5/index.md)专题最容易重复。把边界写死如下——**判据可以互相借用，结论不能互相搬运**。

| 本页回答什么 | 移动端 H5 深入回答什么 | 为什么不能互相替代 |
| --- | --- | --- |
| 渲染管线本身：解析 → 样式 → 布局 → 绘制 → 合成，以及每一步的触发条件 | 这套管线在手机上会被**三类系统事件打断**：软键盘（改视觉视口）、动态工具栏（改视口高度）、内存回收（整页重载） | 管线是同一套，打断来源是手机独有的 |
| 重排 / 重绘 / 合成的代价模型 | 移动端的代价**量级**：同一次布局在低端机上可能是中端机的 3~5 倍 | 代价模型不含量级，量级决定了该不该修 |
| 长任务的成因（同步 JS、布局抖动） | 长任务在**移动端的具体来源**：第三方 SDK、整表重建、首屏一次性初始化 | 成因分类相同，触发场景不同 |

**可以共用的两条**：

1. 「主线程是瓶颈」这个判断
2. `requestAnimationFrame` / 分片渲染的基本手段

**绝不能共用的两条**：

1. **`dvh` 与软键盘的关系**：管线知识推不出「`dvh` 不随键盘变化」，那是视口语义
2. **`100vh` 的取舍**：`svh` / `lvh` / `dvh` 三者的选择依据属于移动端尺寸体系

一句话分诊：**「为什么会卡」看本页，「在什么机器上卡、卡在哪个系统事件上」看那一页。**
