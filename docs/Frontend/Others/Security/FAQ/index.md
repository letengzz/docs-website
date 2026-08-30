# 常见问题与最佳实践

汇总前端安全落地中最高频的问题：防护边界、Token 存储、CSP 取舍、扫描工具与团队流程，方便快速查阅。

## 概念类

### 前端安全到底能防什么、不能防什么？

**能防**：XSS 执行、CSRF 伪造、点击劫持、来源泄露、依赖漏洞、传输窃听。

**不能防**：业务逻辑漏洞（越权、支付篡改）、服务端注入、账号爆破——这些必须后端处理。**前端安全是纵深防御的第一层，不是全部**。

### XSS 和 CSRF 有什么区别？

| 维度 | XSS | CSRF |
| --- | --- | --- |
| 本质 | 恶意脚本**执行** | 伪造请求**提交** |
| 攻击对象 | 用户浏览器 | 用户会话 |
| 前端重点 | 输出编码 + CSP | SameSite + Token |
| 危害 | 窃取 Cookie、篡改页面 | 转账、改密等操作 |

### CSP 有了还需要转义吗？

**需要**。CSP 是「最后一公里」，但：

1. CSP 配置错误/太松会失效；
2. 旧浏览器不支持部分指令；
3. 存储型 XSS 即使不执行脚本，也可能破坏页面展示。

正确姿势：**编码/白名单为主，CSP 兜底**。

## 会话类

### Token 存在哪里？

| 存储位置 | 风险 |
| --- | --- |
| localStorage / sessionStorage | XSS 可读，**不推荐** |
| HttpOnly Cookie | XSS 读不到，推荐 |
| 内存变量 | 刷新丢失，需重新获取 |

推荐：会话凭证放 HttpOnly Cookie；CSRF Token 放 meta 标签 + 请求头回传。

### JWT 怎么存储最安全？

- 短有效期（15 分钟~1 小时）+ 刷新令牌；
- 刷新令牌用 HttpOnly Cookie（`SameSite=Lax`）；
- 敏感操作（改密、支付）要求重新认证；
- 服务端维护吊销名单兜底。

## 配置类

### CSP 上线怕误伤业务怎么办？

三步走：

1. `Content-Security-Policy-Report-Only` 观察 2~4 周；
2. 收集违规报告，区分误报与真实风险；
3. 误报清零后切换为强制模式。

### 响应头在哪里配置最好？

**网关/CDN 层**（Nginx、Cloudflare、WAF）：

- 一处配置全站生效；
- 静态资源也覆盖；
- 不依赖应用框架。

应用内可用 helmet（Node）、Spring Security 等兜底。

### HTTPS 都加密了，还需要别的吗？

需要。HTTPS 解决传输安全，但**应用层攻击**（XSS、CSRF、越权）与**业务逻辑**不归它管。加密 ≠ 安全，是安全的一部分。

## 依赖类

### npm audit 报告漏洞怎么办？

1. 看 `patched in` 修复版本；
2. 直接依赖 → 升级；
3. 传递依赖 → `overrides` 强制版本或升级父包；
4. 无修复版本 → 评估暴露面，临时缓解 + 跟进公告；
5. 高危且无法修复 → 评估替代库。

### 怎么防止引入恶意包？

- 新依赖审查：维护活跃度、下载量、最近发布时间、作者；
- lockfile 提交 + `--frozen-lockfile`；
- CI 接入 Socket.dev 等恶意包检测；
- 发布权限双因素 + 私有源代理审计。

## 工具类

### 有哪些免费安全测试工具？

| 工具 | 用途 |
| --- | --- |
| OWASP ZAP | Web 应用漏洞扫描（免费） |
| Lighthouse | 基础安全审计（HTTPS、CSP 缺失提示） |
| securityheaders.com | 响应头评级 |
| Google CSP Evaluator | CSP 有效性检查 |
| `pnpm audit` / Dependabot | 依赖漏洞 |
| CodeQL | 代码语义扫描 |

## 团队流程类

### 安全怎么融入日常开发？

1. **模板基线**：脚手架默认带响应头、CSP、审计 CI；
2. **Code Review 检查项**：innerHTML、动态 class、Token 存储、请求封装；
3. **安全门禁**：CI 中审计失败即阻塞；
4. **例行巡检**：每周自动扫描 + 每月人工抽查；
5. **漏洞响应**：明确 SLA 与责任人。

## 最佳实践清单

::: tip 前端安全检查清单
1. 所有用户输入是否输出编码（textContent/模板转义）？
2. 富文本是否白名单过滤（DOMPurify）？
3. 会话 Cookie 是否 HttpOnly + Secure + SameSite？
4. CSRF Token / SameSite 是否覆盖敏感操作？
5. CSP 是否部署（先 Report-Only 再强制）？
6. 全站 HTTPS + HSTS + 无混合内容？
7. 依赖是否锁定 + 审计门禁 + 定期扫描？
8. 响应头基座是否在网关层配置？
9. 敏感信息是否不在前端硬编码？
10. 是否有漏洞响应流程与巡检计划？
:::

## 参考资料

- [OWASP Top 10（2025）](https://owasp.org/Top10/)
- [OWASP 速查表系列](https://cheatsheetseries.owasp.org/)
- [MDN：Web 安全](https://developer.mozilla.org/zh-CN/docs/Web/Security)
- [securityheaders.com](https://securityheaders.com/)
