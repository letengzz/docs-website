# 浏览器存储

前端存储家族：Cookie、localStorage、sessionStorage、IndexedDB、Cache API。按**容量、时效、作用域、同步/异步**选择，别把什么都塞 Cookie。

## 存储对比

| 存储 | 容量 | 持久 | 作用域 | 同步/异步 | 自动发送到服务器 |
| --- | --- | --- | --- | --- | --- |
| Cookie | ~4KB | 可设过期 | 域名 | 同步 | 是（每次请求） |
| localStorage | ~5MB | 永久 | 源（origin） | 同步 | 否 |
| sessionStorage | ~5MB | 标签页关闭即清 | 源 + 标签页 | 同步 | 否 |
| IndexedDB | 大（GB 级） | 永久 | 源 | 异步 | 否 |
| Cache API | 大 | 永久 | 源 | 异步 | 否 |

## Cookie

```javascript
document.cookie = "token=abc; path=/; max-age=3600; SameSite=Lax";
```

属性：

- `Max-Age` / `Expires`：有效期。
- `HttpOnly`：JS 不可读（防 XSS 窃取）。
- `Secure`：仅 HTTPS 发送。
- `SameSite`：跨站发送策略（Lax/Strict/None）。

::: danger 注意
Cookie 每次请求都会带上，**不要存大对象**；认证令牌优先考虑 HttpOnly Cookie 或 Authorization 头。
:::

## localStorage 与 sessionStorage

```javascript
localStorage.setItem("theme", "dark");
const theme = localStorage.getItem("theme");
localStorage.removeItem("theme");
```

仅存字符串，对象要 `JSON.stringify`。同步 API，频繁读写大对象会阻塞主线程。

## IndexedDB

异步、容量大，适合离线数据、缓存结构数据：

```javascript
const request = indexedDB.open("mydb", 1);
request.onupgradeneeded = () => {
  const db = request.result;
  db.createObjectStore("items", { keyPath: "id" });
};
```

配合库（Dexie、idb）使用更友好。

## Cache API（Service Worker）

```javascript
const cache = await caches.open("v1");
await cache.add("/index.html");
const res = await cache.match("/index.html");
```

用于 PWA 离线缓存与运行时缓存。

## 选型建议

| 需求 | 推荐 |
| --- | --- |
| 服务端需要读（会话） | Cookie（HttpOnly） |
| 简单键值（主题、偏好） | localStorage |
| 标签页级临时数据 | sessionStorage |
| 大量结构化数据/离线 | IndexedDB |
| 静态资源缓存 | Cache API |

## 易错点

::: danger 常见错误
1. 把 Token 放 localStorage：XSS 即可窃取，敏感数据用 HttpOnly Cookie + 后端校验。
2. Cookie 存大对象：每次请求膨胀，性能与隐私双输。
3. 忽略 `SameSite`：跨站请求伪造（CSRF）风险。
4. localStorage 存对象不序列化：读出变成 "[object Object]"。
5. 隐私数据（身份证、密码）明文存前端：前端存储没有机密性。
6. 容量超限静默失败：写入前 try/catch 并降级。
:::

## 验证方式

1. DevTools → Application 面板查看各存储的实际内容。
2. 设置 Cookie 后刷新页面，观察请求头里的 Cookie。
3. 写一个 IndexedDB 增删改查 demo，确认异步读写。

## 参考资料

- Web Storage（MDN）：https://developer.mozilla.org/zh-CN/docs/Web/API/Web_Storage_API
- IndexedDB（MDN）：https://developer.mozilla.org/zh-CN/docs/Web/API/IndexedDB_API
- Cookie 与 SameSite：https://web.dev/articles/samesite-cookies-explained
