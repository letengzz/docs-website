# Nginx

<p style="text-align:center;"><img src="./assets/nginx-logo.png" alt="Nginx 官方 Logo" style="zoom:75%;" /></p>

Nginx 是高性能的 HTTP 服务器与反向代理，同时支持负载均衡、缓存和限流，是 Web 架构中最常用的接入层组件。

- [Nginx 概述与安装](Overview/index.md)
- [配置文件详解](ConfigFile/index.md)
- [静态资源服务](StaticResources/index.md)
- [反向代理](ReverseProxy/index.md)
- [负载均衡](LoadBalance/index.md)
- [HTTPS 配置](Https/index.md)
- [缓存配置](Cache/index.md)
- [限流配置](RateLimit/index.md)
- [常见问题与最佳实践](FAQ/index.md)

## 相关专题

- [Ansible 自动化运维](../Ansible/index.md)：批量安装 Nginx、下发配置、平滑 reload 与灰度验收
- [Terraform](../Terraform/index.md)：Nginx 所在的主机与网络（VPC、子网、安全组的 80/443 放行）由 IaC 声明式交付，参见 [实战：交付一套云上环境](../Terraform/Practice/index.md)
- [Linux](../Linux/index.md)：Nginx 运行环境的系统层基础
