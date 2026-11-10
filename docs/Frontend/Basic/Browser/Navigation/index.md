# URL 到渲染

从输入 URL 到页面显示，浏览器经历：**DNS → TCP → TLS → HTTP 请求/响应 → 解析 → 渲染**。理解这条链路，才能定位“慢在哪一步”。

![URL 到渲染的关键路径](../assets/navigation.svg)

## 完整流程

```text
1. 输入 URL
2. DNS 解析域名 → IP
3. 建立 TCP 连接（三次握手）
4. HTTPS：TLS 握手（四次/1.3 一次往返）
5. 发送 HTTP 请求
6. 服务器响应（HTML）
7. 浏览器解析 HTML → 构建 DOM
8. 加载子资源（CSS、JS、图片）
9. 执行渲染流程
10. 首次绘制完成
```

## 关键步骤详解

### DNS

```text
浏览器缓存 → 系统缓存 → 本地 hosts → 递归 DNS → 权威 DNS
```

优化：减少域名数量、开启预解析（`dns-prefetch` / `preconnect`）。

### TCP / TLS

1. TCP 三次握手建立连接。
2. HTTPS 需要 TLS 握手协商密钥。
3. HTTP/2 多路复用减少连接数；HTTP/3（QUIC）基于 UDP，握手更快。

### HTTP 请求与响应

```shell
curl -v https://example.com
```

关注：状态码、响应头（Cache-Control、Content-Type）、资源大小。

## 关键路径资源

页面首屏取决于关键路径资源：

1. HTML（必须首先拿到）。
2. CSS：渲染阻塞资源（Render-Blocking）。
3. JS：默认解析器阻塞（Parser-Blocking），`defer` / `async` 可调整。
4. 图片/字体：非阻塞，但影响 LCP。

## 优化方向

| 阶段 | 手段 |
| --- | --- |
| DNS | dns-prefetch、preconnect |
| TCP/TLS | HTTP/2、HTTP/3、减少握手 |
| 请求 | 缓存、CDN、压缩 |
| 解析 | 精简 HTML、内联关键 CSS |
| 渲染 | 减少阻塞脚本、懒加载 |

## 易错点

::: danger 常见错误
1. 把“后端响应慢”和“浏览器渲染慢”混为一谈：先看 DevTools Network 分段。
2. 忽略渲染阻塞资源：CSS/JS 不优化，HTML 再快首屏也慢。
3. 一个页面几十个域名请求：DNS 查询多，收敛域名或 preconnect。
4. 不用 HTTP/2：多请求串行等待，开启后多路复用。
5. 只看 TTFB 不看整体：TTFB 快但 LCP 慢，问题在资源加载。
:::

## 验证方式

1. DevTools → Network 面板，开启“Slow 4G”模拟，观察各阶段耗时。
2. 用 Lighthouse 看 TTFB、FCP、LCP 分解。
3. `curl -w` 输出 DNS/TCP/TLS/请求各阶段耗时。

## 相关专题

- [网络编程专题](../../../../Backend/NetworkProgramming/index.md)：TCP 握手、HTTP/HTTPS 与 Socket
- [TCP 与 UDP 详解](../../../../Backend/NetworkProgramming/TCPUDP/index.md)：导航请求底层的可靠传输

## 与「DNS 解析工程与域名治理」专题的分工（第 271 天补充）

| 维度 | 本页 | [DNS 解析工程与域名治理](../../../../Ops/DnsResolution/index.md) |
| --- | --- | --- |
| 回答的问题 | URL 到页面渲染的导航流程、DNS 在其中的位置 | 一次解析的答案凭什么可信、变更凭什么可控 |
| 不重复什么 | 不再讲渲染链路；本专题讲客户端 stub 缓存与加密传输策略 | 不重写既有组件文档 |

**一页一坑**：**浏览器自择 DoH 会绕过企业递归器**：内网 split-horizon 名字（内外不同答案）可能突然解析到公网地址，基于 DNS 的审计与拦截同时失效。本专题把路径观察点从 4 处降到 2 处建模，但递归器仍看得到 **100%** 的查询——加密只覆盖 stub → 递归这一跳。

::: tip 回归判据
在企业策略开/关两种状态下各访问一次内网域名，确认两边答案一致或差异被显式登记。
:::

## 参考资料

- 关键路径（Web Fundamentals）：https://web.dev/articles/critical-rendering-path
- 导航流程（Inside look at modern web browser）：https://developer.chrome.com/blog/inside-browser-part1/
- HTTP/3 说明：https://developer.chrome.com/blog/http3-roughly-half-the-time-to-first-byte/
