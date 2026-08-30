# 前端安全

<p style="text-align:center;"><img src="./assets/security-logo.png" style="zoom:75%;" /></p>

前端安全聚焦浏览器侧的攻击面：XSS、CSRF、CSP、HTTPS、安全响应头与依赖供应链。核心原则是**纵深防御（Defense in Depth）**——每一层防护独立失效都不至于被攻破，以及**默认拒绝、不信任任何输入**。

参考基线：本专题以 OWASP Top 10（2025 版）与 2026 年主流浏览器能力为准，涉及新特性会标注支持情况。

- [XSS 跨站脚本](XSS/index.md)
- [CSRF 跨站请求伪造](CSRF/index.md)
- [CSP 内容安全策略](CSP/index.md)
- [HTTPS 与证书](Https/index.md)
- [安全响应头](Headers/index.md)
- [依赖与供应链安全](Dependency/index.md)
- [实战：安全基线落地](Practice/index.md)
- [常见问题与最佳实践](FAQ/index.md)
