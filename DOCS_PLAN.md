# 每日文档生成计划

本计划用于让文档库每天持续、大量积累。每天生成 **1 个大主题（6~10 篇）或 2 个小主题（各 3~5 篇）**，同时完成 **1 项存量文档整理**，并严格遵循仓库根目录的 `AGENTS.md`。

## 使用方式

1. 每天从下方表格按顺序取下一个「未完成」的主题；也可以临时替换为当天更想写的主题。
2. 动手前通读 `AGENTS.md`，并打开范本 `docs/Frontend/Basic/HTML` 与目标分类现有文档，模仿其风格。
3. 生成完成后：
   - 更新对应侧边栏分支文件（`frontend.ts`、`backend.ts`、`db.ts`、`ops.ts`、`AI.ts`、`tools.ts`、`project.ts`）；
   - 涉及新分类或导航时更新 `nav.ts`；
   - 运行 `pnpm docs:build` 验证；
   - 按 Conventional Commits 规范提交（`docs(分类): 描述`），并 `git push origin main` 同步到 GitHub。
4. 完成一个主题后，在本表中标记 ✅，下次从下一个主题继续。
5. 每天的「存量整理」任务从下方清单中顺延取一项，与当天新主题一起完成。

## 每日产出要求

1. 新主题默认按「完整主题模板」展开：Overview → Environment → CoreConcepts → Basic → Advanced → Practice → FAQ → References（可按主题合并或拆分）。
2. 大主题每天 6~10 篇；小主题至少 3~5 篇；每篇正文必须满足 `AGENTS.md` 第 5 节「内容深度与完整性要求」，禁止空壳页。
3. 每篇至少包含：概念/原理 + 可运行示例 + 表格/清单 + 易错点/最佳实践 + 验证方式 + 参考资料。
4. 复杂概念、架构、流程必须配示意图（本地 SVG 或可授权图源）。
5. 版本、命令、API 信息必须联网核对，以官方文档为准。
6. 每天除新主题外，还要挑选 **5~10 篇存量文档**进行调整、补充与更新（内容过期、结构不规范、缺示例/配图、链接失效等），并同步侧边栏/导航。
7. 主题涉及大版本时按版本建目录（如 `Spring5/Spring6`、`Vue2/Vue3`）：新文档面向最新稳定版，旧版本保留并标注维护状态，不覆盖旧内容。

## 1-30 天轮换表

| 天数 | 分类 | 主题 | 建议章节 |
| --- | --- | --- | --- |
| 1 | Backend | Java 入门 ✅ | 概述、环境搭建、基础语法、面向对象 |
| 2 | Backend | Python 进阶 ✅ | 环境管理、装饰器、异步、常用库 |
| 3 | DB | MySQL 基础 ✅ | 概述与版本、安装配置、核心概念、库表操作、数据增删改查、查询进阶、事务与隔离级别、索引与性能、常见问题 |
| 4 | DB | Redis 基础 ✅ | 概述与版本、安装配置、通用命令、String/Hash、List/Set/ZSet、过期与淘汰策略、持久化 RDB/AOF、发布订阅与事务、常见问题 |
| 5 | Ops | Linux 基础 ✅ | 概述与发行版、目录结构、文件与目录命令、文本处理 grep/sed/awk、权限与用户、进程与服务、网络命令、Shell 基础、常见问题 |
| 6 | Ops | Docker 进阶 ✅ | Dockerfile 最佳实践、多阶段构建、Compose、网络模式、数据卷与挂载、容器监控、安全加固、CI 集成、常见问题 |
| 7 | Frontend | Vue3 核心 ✅ | 概述与创建、响应式原理、模板语法、组件通信、Composition API、路由、Pinia、生命周期、实战案例 |
| 8 | Frontend | React 核心 ✅ | 概述与环境、JSX、组件与 Props、State 与事件、Hooks 详解、Context、路由、状态管理、性能优化、实战案例 |
| 9 | Backend | Spring Boot ✅ | 概述与版本、项目搭建、配置与 Profile、Web 开发、数据访问、REST API、异常处理、测试、部署、常见问题 |
| 10 | Tools | Git 进阶 ✅ | 分支模型、Rebase 与 Merge、Stash、reset/revert、cherry-pick、子模块、协作工作流、常见问题 |
| 11 | Tools | Maven / Gradle ✅ | 概述与安装、项目结构、构建生命周期、依赖管理、私服、多模块、Gradle 对比、常见问题 |
| 12 | Backend | Java 集合 ✅ | 集合框架总览、List、Set、Map、迭代与遍历、排序与比较器、并发集合、源码要点、常见问题 |
| 13 | Backend | Java 并发 ✅ | 线程基础、线程池、synchronized 与 Lock、volatile、并发工具类、CompletableFuture、ThreadLocal、常见问题 |
| 14 | Backend | JVM 基础 ✅ | 内存结构、对象创建与布局、类加载机制、GC 算法、垃圾收集器、调优参数、故障排查、常见问题 |
| 15 | Frontend | TypeScript 进阶 ✅ | 类型系统、泛型、类型工具、条件类型、装饰器、工程化配置、与 Vue/React 结合、常见问题 |
| 16 | Ops | Nginx ✅ | 概述与安装、配置文件、静态资源、反向代理、负载均衡、HTTPS、缓存、限流、常见问题 |
| 17 | Ops | Kubernetes ✅ | 核心概念、安装、Pod、Deployment、Service、Ingress、ConfigMap/Secret、存储、监控、常见问题 |
| 18 | DB | MongoDB ✅ | 概述与安装、文档与集合、CRUD、索引、聚合管道、副本集、分片、备份恢复、常见问题 |
| 19 | AI | 提示词工程 ✅ | 原理与模型行为、结构化提示词、角色与上下文、few-shot、思维链、模板库、效果评估、常见问题 |
| 20 | AI | Agent 应用 | Agent 原理、工具调用、工作流编排、多智能体、记忆与上下文、安全边界、落地案例、常见问题 |
| 21 | Frontend | 浏览器原理 | 浏览器架构、URL 到渲染、渲染流程、事件循环、存储、缓存、安全、性能指标、常见问题 |
| 22 | Backend | 消息队列 | 概念与选型、Kafka、RabbitMQ、可靠投递、消费幂等、集群部署、对比总结、常见问题 |
| 23 | Backend | 微服务 | 服务拆分、注册中心、配置中心、网关、负载均衡、熔断限流、链路追踪、分布式事务、常见问题 |
| 24 | Tools | CI/CD | CI/CD 概念、GitHub Actions、流水线设计、自动化测试、制品管理、自动部署与回滚、常见问题 |
| 25 | Ops | 监控告警 | 监控体系、Prometheus、指标采集、Grafana、告警规则、日志监控、常见问题 |
| 26 | Frontend | 前端工程化 | 工程化概览、代码规范、Git 规范、单元测试、构建优化、CI 集成、脚手架、常见问题 |
| 27 | DB | SQL 优化 | 执行计划、索引原理、慢查询、分页优化、JOIN 优化、锁与事务、优化案例、常见问题 |
| 28 | Backend | 设计模式 | 设计原则、创建型、结构型、行为型、框架中的应用、实战案例、常见问题 |
| 29 | Backend | 网络编程 | 网络分层、TCP/UDP、HTTP/HTTPS、Socket、Netty、粘包拆包、实战案例、常见问题 |
| 30 | Others | 复盘杂项 | 阶段复盘、知识体系整理、面试题集、效率工具安利 |

## 31-60 天轮换表

| 天数 | 分类 | 主题 | 建议章节 |
| --- | --- | --- | --- |
| 31 | Backend | Java IO/NIO | 文件 IO、字节/字符流、NIO、Channel/Buffer、网络 IO 模型、实战案例、常见问题 |
| 32 | Backend | Java 反射与注解 | Class 对象、反射 API、动态代理、注解定义与处理、实战案例、常见问题 |
| 33 | Backend | Java 函数式编程 | Lambda、Stream、Optional、方法引用、实战案例、常见问题 |
| 34 | Frontend | CSS 进阶 | 布局体系、动画、响应式、工程化、原子化 CSS、常见问题 |
| 35 | Frontend | 前端安全 | XSS、CSRF、CSP、HTTPS、安全响应头、依赖安全、常见问题 |
| 36 | Frontend | 前端性能优化 | 加载优化、构建优化、运行时优化、监控与指标、实战案例、常见问题 |
| 37 | DB | PostgreSQL | 概述与版本、安装、SQL 基础、高级特性、索引、备份恢复、常见问题 |
| 38 | DB | MySQL 索引深入 | B+ 树原理、联合索引、索引失效场景、覆盖索引、优化案例、常见问题 |
| 39 | Ops | 网络基础 | 网络分层、DNS、TCP/IP、HTTP/HTTPS、抓包分析、常见问题 |
| 40 | Ops | 容器编排进阶 | Helm、Operator、服务网格、弹性伸缩、多集群、常见问题 |
| 41 | Tools | 数据库客户端 | Navicat、DBeaver、RedisInsight、常用操作、连接管理、常见问题 |
| 42 | Tools | 接口调试工具 | Postman、Apifox、环境与脚本、Mock、自动化测试、常见问题 |
| 43 | Tools | 包管理器深入 | npm/pnpm/yarn 对比、pnpm 原理、monorepo、发布流程、常见问题 |
| 44 | Backend | Spring Cloud | 注册中心、配置中心、网关、熔断限流、链路追踪、实战案例、常见问题 |
| 45 | Backend | Kafka 深入 | 架构、生产者、消费者、分区与副本、可靠性、集群、实战、常见问题 |
| 46 | Backend | 分布式事务 | 2PC、TCC、SAGA、Seata、本地消息表、实践对比、常见问题 |
| 47 | AI | 大模型应用开发 | API 调用、Function Calling、RAG、Agent 框架、成本与限流、实战、常见问题 |
| 48 | AI | RAG 检索增强 | Embedding、向量库、Chunking、检索优化、评估、实战案例、常见问题 |
| 49 | AI | 本地模型部署 | Ollama、量化、API 接入、GPU/内存规划、实战案例、常见问题 |
| 50 | Frontend | 微信小程序 | 框架与目录、组件、API、路由、发布流程、性能优化、常见问题 |
| 51 | Frontend | 跨端开发 | UniApp、Taro、Electron、方案对比、实战案例、常见问题 |
| 52 | Frontend | 前端测试 | Vitest、Jest、组件测试、E2E、覆盖率、测试策略、常见问题 |
| 53 | DB | Elasticsearch | 概述与安装、索引与映射、查询 DSL、聚合、集群、中文分词、常见问题 |
| 54 | DB | Redis 进阶 | 持久化、主从与哨兵、Cluster、缓存设计、性能调优、常见问题 |
| 55 | Ops | 日志体系 | ELK、Loki、日志采集、日志分析、告警联动、常见问题 |
| 56 | Ops | Linux 进阶 | Shell 编程、系统调优、服务管理、定时任务、安全加固、常见问题 |
| 57 | Tools | 协作与项目管理 | Jira、Confluence、飞书、研发流程、文档协作、常见问题 |
| 58 | Project | Vue3 模板补充 | 权限、主题、组件库集成、多环境、发布、常见问题 |
| 59 | Project | 完整项目实战 | 需求拆分、数据库设计、前后端联调、测试、部署、复盘 |
| 60 | Others | 年度复盘 | 文档库盘点、知识体系重构、年度总结、下一年规划 |

## 61-90 天轮换表

| 天数 | 分类 | 主题 | 建议章节 |
| --- | --- | --- | --- |
| 61 | Backend | Java 设计模式实战 | 设计原则、创建型、结构型、行为型、框架源码分析、实战案例 |
| 62 | Backend | Java 网络编程 | Socket、NIO、Netty、粘包拆包、编解码、实战案例 |
| 63 | Backend | Go 入门 | 概述与环境、语法基础、并发模型、Web 开发、实战案例 |
| 64 | Backend | 认证与授权 | JWT、OAuth2、Session、SSO、安全最佳实践、常见问题 |
| 65 | Frontend | Vite 深入 | 原理、配置、插件开发、环境变量、构建优化、实战案例 |
| 66 | Frontend | Webpack 深入 | 核心概念、Loader、Plugin、代码分割、优化实践 |
| 67 | Frontend | 小程序进阶 | 分包、自定义组件、云开发、性能优化、发布 |
| 68 | Frontend | Electron 深入 | 进程模型、IPC、窗口管理、打包、自动更新 |
| 69 | DB | 数据建模 | 范式、ER 图、设计原则、反范式、实战案例 |
| 70 | DB | 时序数据库 | InfluxDB、TDengine、数据模型、查询、应用场景 |
| 71 | Ops | Ansible | 概述、Playbook、常用模块、角色、实战案例 |
| 72 | Ops | Terraform | 概述、资源、状态管理、模块、实战案例 |
| 73 | Ops | 安全加固 | 系统基线、容器安全、K8s 安全、漏洞管理 |
| 74 | Tools | IDE 配置 | IntelliJ IDEA、VS Code、插件、快捷键、配置同步 |
| 75 | Tools | 效率工具 | 终端、剪贴板、截图、笔记、自动化 |
| 76 | AI | LangChain | 概述、Chain、Agent、Memory、实战案例 |
| 77 | AI | Embedding 与向量库 | 概念、Milvus/pgvector、检索优化、实战 |
| 78 | AI | 多模态应用 | 图像、语音、视频处理、模型接入、实战 |
| 79 | Project | 后端模板搭建 | 项目结构、认证、数据库、统一响应、部署 |
| 80 | Project | 完整项目（电商/博客） | 需求、架构、编码、测试、部署、复盘 |
| 81 | Frontend | 数据可视化 | ECharts、Canvas、SVG、数据大屏、实战 |
| 82 | Frontend | 状态管理 | Pinia、Redux/Zustand、对比选型、实战 |
| 83 | Backend | 缓存设计 | 缓存策略、穿透/击穿/雪崩、一致性、实战 |
| 84 | Backend | 搜索引擎深入 | ES 调优、中文分词、索引生命周期、实战 |
| 85 | DB | 分库分表 | 拆分策略、中间件、分布式 ID、迁移、常见问题 |
| 86 | Ops | 云原生 | 云厂商、Serverless、容器服务、成本优化 |
| 87 | Tools | 测试工具 | JMeter、Selenium、接口自动化、性能测试 |
| 88 | AI | 智能体工作流 | n8n、Coze、Dify、落地案例、对比 |
| 89 | Project | 全流程部署实战 | Docker、K8s、CI/CD、监控、回滚 |
| 90 | Others | 年度复盘与规划 | 文档盘点、知识体系、下一年规划 |

## 存量整理任务清单

与每日新主题并行，从以下清单按顺序取一项完成（完成后标记 ✅）；同时每天挑选 **5~10 篇存量文档**做调整补充与更新（长期任务，持续执行）：

- [x] 平铺文档迁移：DB 概述、DotNet、Docker（含安装卸载）、AI 核心概念、Node.js 模块、包管理工具、前端基础页已迁移为「英文目录 + index.md」
- [x] 侧边栏补全：Docker、Python、Java、AI 核心概念已挂载
- [x] 占位页面补充：Tools 分类、DB 关系型/非关系型、Others 页面已创建
- [x] 清理不规范 frontmatter：Python 页面已移除 `layout:doc`
- [x] 全库链接巡检：已修复 Vue 概述、Pinia、Vant、LXC 等失效引用；侧边栏无残留旧链接
- [x] 图片路径巡检：检查存量文档图片是否全部使用相对路径（巡检通过，无绝对路径或外链图片）
- [x] 标题与 H1 规范巡检：全库扫描并修复（DotNet 基础页已调整为单 H1 + 章节结构）
- [x] Frontend 存量补全：Frame 目录页修复失效链接并补齐 UmiJS/Next；Others 补充索引并挂载侧边栏
- [x] Backend 存量补全：Java 侧边栏修复失效链接并挂载全部 JavaSE 章节；.NET 章节已完备
- [x] DB 存量补全：MySQL、Redis 专题（第 3、4 天已建设完整专题）
- [x] Ops 存量补全：Linux 专题已在第 5 天建设完成；Nginx、Kubernetes 由第 16/17 天轮换主题覆盖（清单已结清）
- [x] Tools 存量补全：Git（第 10 天）与 Maven/Gradle（第 11 天）专题已建设；CI/CD 按第 24 天计划继续
- [x] AI 存量补全：OpenClaw 核心概念补充渠道、技能、工具三篇并挂载侧边栏
- [x] 文档风格统一巡检：修复 3 处结构问题（未闭合容器/围栏）；全库 381 处裸代码块（54 个历史文件）已统一补 `text` 语言标注
- [x] 存量版本检查：Vue2/Vue3、ES5~ES12+ 已按版本分目录；MySQL（8.4/9.7）、Redis（8.x/7.x）、Java（LTS）、.NET（DotNet5/WebApiNet6）在页内标注版本现状；其余主题暂无需拆分
- [x] 分类目录页与侧边栏结构：AI/Backend/DB/Frontend/Ops/Tools 已补 `index.md` 目录页；主题按路径挂载侧边栏且默认展开
- [x] 存量整理清单已全部结清；后续新增存量任务按需追加（第 14 天：JVM 专题配套更新 JavaSE 目录与交叉链接）
- [x] 配图补全：为 Maven/Gradle、Java 集合/并发、JVM 专题补充 23 张 SVG 示意图并明确「text 图不算配图」规范
- [x] Frontend 存量补全：TypeScript 进阶专题已建设（8 篇）并补充 Vue3/React 交叉链接与配图
- [x] Logo 与配图规则：AGENTS.md 新增「主题首页必须放官方 Logo（PNG、缩放到 75%）、每篇正文必须配图」规范；Nginx/Spring Boot 首页已补官方 Logo
- [x] Ops 存量补全：Kubernetes 专题已建设（10 篇，第 17 天）并补充 Docker/Linux/Nginx 交叉链接
- [x] DB 存量补全：MongoDB 专题已建设（10 篇，第 18 天）并补充 MySQL/Redis 交叉链接
- [x] AI 存量补全：提示词工程专题已建设（8 篇，第 19 天），移除 AI/Java 残留入口并补充 OpenClaw 交叉链接

## 节奏建议

- 每天至少产出 6 篇（1 个大主题或 2 个小主题）；当天写不完时把欠量顺延到次日补齐，不要用 1 篇概述代替。
- 每天同步调整、补充、更新 **5~10 篇存量文档**，优先处理过期版本、结构不规范、缺图缺示例、链接失效的页面。
- 遇到大版本升级（如 Spring 5 → Spring 6）时，先建新版本目录，旧版本文档保留并标注状态，不要覆盖。
- 保质保量：篇幅宁多勿少，但每篇必须满足 `AGENTS.md` 的「内容深度与完整性要求」，禁止空壳页、禁止凑字数。
- 建议每周轮换大类（后端 / 数据库 / 运维 / 前端 / 工具 / AI / 项目），避免连续同类。
- 已有内容的主题（如 Python）优先做「进阶补全」，不要重复写已有章节。
- 存量整理优先处理：平铺文件迁移、侧边栏缺口、失效链接、空页面、图片相对路径。

## 接入定时任务

在 Codex App 中创建「每日」定时任务时，可使用以下提示词模板：

```text
请阅读仓库根目录的 DOCS_PLAN.md 和 AGENTS.md，按顺序取出下一个未完成的主题，
按「完整主题模板」生成 6~10 篇细致全面的技术文档（每篇满足内容深度要求），
并从存量文档中挑选 5~10 篇进行调整、补充与更新，同时从「存量整理任务清单」中取一项；
更新侧边栏（必要时更新导航），
运行 pnpm docs:build 验证，最后按 Conventional Commits 规范提交并 push 到 GitHub 远程仓库。

补充要求：涉及大版本的主题按版本目录组织（如 Spring5/Spring6），旧版本保留并标注状态，不覆盖旧内容。
```
