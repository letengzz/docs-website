# 文档体系建设

文档体系建设（Documentation Infrastructure）解决的是「技术知识写下来之后，能不能被找到、被信任、被长期维护」的问题：从静态站点生成、全文搜索、多版本组织，到写作规范与自动化巡检，给出一条从零搭起一个可持续文档站的完整路径。适用于所有需要沉淀团队知识、产品手册或学习笔记的开发者。

<p style="text-align:center;"><img src="./assets/docsinfra-logo.png" style="zoom:75%;" /></p>

## 页面导航

- [文档体系概览](Overview/index.md)：文档体系的四层结构、Docs-as-Code 理念与「什么时候不该自建」
- [静态站点生成选型](Ssg/index.md)：VitePress、Docusaurus、Rspress、Starlight、MkDocs Material 的 2026-10 版图与选型判据
- [全文搜索](Search/index.md)：构建期本地索引与托管搜索两条路线、中文分词折中与索引构建流程
- [多版本文档](Versioning/index.md)：版本目录策略与生成器内置版本化两种方式的取舍与落地
- [写作规范](Standards/index.md)：页面骨架、语言表达、代码块与表格规范、评审清单
- [文档自动化](Automation/index.md)：文档 CI 流水线、巡检门禁设计（错误 / 告警分级）与自动部署
- [实战：从零搭一个文档站](Practice/index.md)：以 VitePress 为例，从初始化到带搜索、巡检、自动部署的可复现路径
- [常见问题](FAQ/index.md)：选型、迁移、搜索体验、维护成本等高频问题分诊

## 相邻主题分工

| 主题 | 讲什么 | 与本专题的边界 |
| --- | --- | --- |
| 前端工程化 | 代码规范、构建优化、脚手架 | 本专题只管「文档」这个产物，不讲应用工程化 |
| CI/CD | 通用流水线设计、制品管理 | 本专题只把文档当作流水线的一种交付物 |
| API 设计与治理 | API 契约与治理 | API 参考文档的「生成与发布」归口本专题讲 |
| Git 进阶 | 分支与协作 | 文档的版本管理与代码同一套机制，不重复讲 |

## 版本状态速览（2026-10，均已联网核对）

| 工具 | 当前状态 | 说明 |
| --- | --- | --- |
| VitePress | 稳定线 1.6.4（2025-08-05），2.0.0-alpha.20（2026-09-04） | 2.0 处于 alpha，生产站建议留在 1.x |
| Docusaurus | 3.10.2（2026-07），v4 通过 future flags 渐进迁移 | React 团队首选，内置多版本 |
| MkDocs / Material for MkDocs | MkDocs 1.6.1（2024-08）后无发版；主题 9.7.x 维护模式 | 新项目不建议，存量可评估 Zensical |
| Rspress | 2.0.21，活跃 | Rspack 驱动，中文社区活跃 |
| Starlight（Astro） | 0.42.0，pre-1.0，活跃 | 内容优先，零 JS 默认 |
| Docsify | 5.0.0（2026-07-23）转稳定 | 无构建渲染，不适合公开 SEO 站点 |

:::tip 一句话理解
文档体系 = **用工程化的方式维护文档**：Markdown 是源码，构建器是编译器，巡检门禁是测试，CI 是发布管道——代码工程里被验证过的纪律，全部可以搬到文档上。
:::

## 学习路径

1. 先读[文档体系概览](Overview/index.md)建立四层结构与 Docs-as-Code 的整体认知；
2. 按[静态站点生成选型](Ssg/index.md)选定工具，跟随[实战](Practice/index.md)从零搭起站点；
3. 站点能跑后，依次接入[全文搜索](Search/index.md)、[多版本](Versioning/index.md)（如有需要）；
4. 最后用[写作规范](Standards/index.md)约束内容产出，用[文档自动化](Automation/index.md)把质量检查交给 CI，让体系**不依赖人的自觉**。
