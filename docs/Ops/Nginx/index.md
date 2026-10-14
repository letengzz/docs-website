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
- [云上架构 · 负载均衡](../CloudArchitecture/LoadBalancing/index.md)：本专题讲**自建 Nginx 的七层规则语法**（`location`/`upstream`/`proxy_pass` 怎么写、证书怎么配）；该页讲**托管负载均衡**的四层与七层分界、健康检查四参数、跨可用区开关与 TLS 终止位置。判据是一句话——**Nginx 是你要升级、要打补丁、要盯着它 reload 的进程；托管负载均衡是按时长与流量计费的资源**。两者混用时，「摘除时间」与「优雅停机时间」必须对齐，否则会互相误判对方是「后端挂了」。
- [网关深入](../../Backend/GatewayDeep/index.md)：本页讲的是**你自己写配置、自己 `reload` 的 Nginx**；该专题讲的是**带控制面与插件运行时的网关产品**（Kong / APISIX）——配置从 API 进、由网关自己热生效，路由与插件有独立的实体模型和优先级规则。判据同样是一句话：**出问题时「谁负责 reload、谁负责升级」是完全不同的答案。** 本专题的 `location`/`upstream` 语法是理解 Kong「路由 + 上游」模型的基础，但那两套配置不能互相搬运。

## 与「边缘计算与 CDN」专题的分工

Nginx 与 CDN 都要缓存、都要限流、都终结 TLS，指令名甚至可以直接互借（`proxy_cache` 与边缘平台的缓存规则、`limit_req` 与边缘的速率限制）。但两者是**两种东西**：

| 维度 | Nginx | [边缘计算与 CDN](../EdgeCDN/index.md) |
| --- | --- | --- |
| 是什么 | **你自己维护的一个进程** | **租出去的一张网** |
| 你在哪台机器上 | 每台都能登上去 | 一台也登不上 |
| 缓存放在几处 | 你说了算，通常一处或几处 | 几百个节点，各自独立、各自失效 |
| 出故障时 | 你看日志、改配置、重启 | 你只能看平台给的指标与日志，且取回有延迟 |

::: tip 一句话判据
`location` 与缓存指令的写法可以互借，但**「谁兜底、谁升级、谁背 SLA」完全不同**——本机 Nginx 挂了是你的故障，边缘节点挂了是厂商的故障但影响仍是你的。凡是「同一条规则要在几百个点上保持一致」的问题（缓存键、失效传播、配置生效窗口），归 [边缘计算与 CDN](../EdgeCDN/index.md)；凡是「一个进程内怎么配」的问题，归本页。
:::
