# 浏览器原理

<p style="text-align:center;"><img src="./assets/browser-logo.png" alt="浏览器原理" style="zoom:75%;" /></p>

浏览器是前端代码的“运行时”。理解它的架构、渲染流程、事件循环与缓存机制，是前端性能优化和疑难问题排查的基础。

- [浏览器架构](Architecture/index.md)
- [URL 到渲染](Navigation/index.md)
- [渲染流程](Rendering/index.md)
- [事件循环](EventLoop/index.md)
- [浏览器存储](Storage/index.md)
- [HTTP 缓存](Cache/index.md)
- [浏览器安全](Security/index.md)
- [性能指标](Performance/index.md)
- [常见问题与最佳实践](FAQ/index.md)

## 与「状态管理与数据流」专题的分工

本页是**平台能力**：渲染流程、事件循环、`localStorage` / `IndexedDB`、HTTP 缓存。至于「用这些能力怎么让两台设备收敛到同一个状态」，归 [状态管理与数据流](/docs/Frontend/StateDataFlow/index.md) 的 [多端同步与收敛](/docs/Frontend/StateDataFlow/RealtimeSync/index.md)。

::: warning 三个与本页有关、但本页不展开的事实
1. `storage` 事件**不会在当前标签页触发**，用它做同页同步必然失败；同页要靠内存事件或 `BroadcastChannel`。
2. bfcache 恢复页面时**不触发 `load`**，只在 `pageshow` 里带 `persisted: true`；把「重新取数」写在 `load` 里，返回时看到的就是旧数据。
3. HTTP 的 `no-cache` 是「可以存但必须每次校验」，不是「不存」；把它当「不缓存」写进接口约定，会让 CDN 与浏览器行为都对不上预期。
:::
