# 浏览器安全

浏览器安全的核心是**同源策略**与各类攻击防护：XSS、CSRF、CSP、HTTPS。前端安全的目标是“攻击面最小、默认拒绝”。

## 同源策略

协议 + 域名 + 端口都相同才叫同源：

```text
https://a.com:443 与 https://a.com:443 同源
https://a.com 与 http://a.com 不同源（协议不同）
https://a.com 与 https://b.a.com 不同源（子域）
```

跨源读取被阻止；跨源请求可发但读取受限（配合 CORS 授权）。

## XSS（跨站脚本）

把用户输入当代码执行：

```javascript
// 危险：innerHTML 直接插入用户输入
el.innerHTML = userInput;
```

防御：

1. 输出转义（`textContent`、模板引擎自动转义）。
2. `Content-Security-Policy` 限制脚本来源。
3. Cookie 加 `HttpOnly`，降低凭证窃取。
4. 输入校验 + 富文本白名单。

## CSRF（跨站请求伪造）

用户已登录时，恶意站点诱导浏览器发请求：

防御：

1. `SameSite=Lax/Strict` Cookie。
2. CSRF Token 校验。
3. 敏感操作二次确认 / 校验 Origin 头。

## CSP（内容安全策略）

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://cdn.example.com
```

限制脚本、样式、图片等资源来源，是 XSS 的重要防线。

## HTTPS 与安全头

```http
Strict-Transport-Security: max-age=31536000
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin
```

## 前端常见漏洞

| 漏洞 | 场景 | 防御 |
| --- | --- | --- |
| XSS | 评论、搜索词回显 | 转义 + CSP |
| CSRF | 登录态下的伪造请求 | SameSite + Token |
| 点击劫持 | iframe 覆盖 | X-Frame-Options / frame-ancestors |
| 开放重定向 | 跳转参数可控 | 白名单校验 |
| 敏感信息泄露 | localStorage 存 Token | HttpOnly Cookie |
| 供应链 | 恶意依赖 | 锁版本 + 审计 |

## 易错点

::: danger 常见错误
1. 只用 `innerHTML` 不转义：XSS 高危，优先 `textContent`。
2. Token 存 localStorage：XSS 一次即泄露，用 HttpOnly Cookie。
3. 忽略 SameSite：CSRF 防护缺一环。
4. CSP 用 `'unsafe-inline'` 一开到底：等于没限制。
5. 后端跨域开 `*` + 带凭证：CORS 配置错误，随意被读取。
6. 自研加密代替 HTTPS：前端加密没有机密性，必须走 TLS。
:::

## 验证方式

1. 用 `curl -I` 检查安全响应头是否齐全。
2. 用浏览器 DevTools 检查 CSP 报错。
3. 用 OWASP ZAP 或浏览器审计工具扫描常见漏洞。

## 参考资料

- 前端安全专题：[前端安全目录](../../Others/Security/index.md)（XSS/CSRF/CSP/HTTPS/响应头/依赖安全）
- 同源策略（MDN）：https://developer.mozilla.org/zh-CN/docs/Web/Security/Same-origin_policy
- OWASP XSS 防护：https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- Web 安全基础：https://web.dev/learn/security/
