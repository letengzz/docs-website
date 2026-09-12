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
| 20 | AI | Agent 应用 ✅ | Agent 原理、工具调用、工作流编排、多智能体、记忆与上下文、安全边界、落地案例、常见问题 |
| 21 | Frontend | 浏览器原理 ✅ | 浏览器架构、URL 到渲染、渲染流程、事件循环、存储、缓存、安全、性能指标、常见问题 |
| 22 | Backend | 消息队列 ✅ | 概念与选型、Kafka、RabbitMQ、可靠投递、消费幂等、集群部署、对比总结、常见问题 |
| 23 | Backend | 微服务 ✅ | 服务拆分、注册中心、配置中心、网关、负载均衡、熔断限流、链路追踪、分布式事务、实战、常见问题 |
| 24 | Tools | CI/CD ✅ | CI/CD 概念、GitHub Actions、GitLab CI、Jenkins、流水线设计、自动化测试与质量门禁、制品管理、自动部署与回滚、常见问题 |
| 25 | Ops | 监控告警 ✅ | 监控体系与可观测性、Prometheus、指标采集、Grafana、告警规则、日志监控、实战、常见问题 |
| 26 | Frontend | 前端工程化 ✅ | 工程化概览、代码规范、Git 规范、单元测试与组件测试、构建优化、CI 集成、脚手架与工程结构、常见问题 |
| 27 | DB | SQL 优化 ✅ | 概述、执行计划、索引原理与失效、慢查询、分页优化、JOIN 优化、锁与事务、优化案例、常见问题 |
| 28 | Backend | 设计模式 ✅ | 设计原则、创建型、结构型、行为型、框架中的应用、实战案例、常见问题 |
| 29 | Backend | 网络编程 ✅ | 网络分层、TCP/UDP、HTTP/HTTPS、Socket 与 IO 模型、Netty、粘包拆包、实战、常见问题 |
| 30 | Others | 复盘杂项 ✅ | 30 天阶段复盘、知识体系整理、面试题集、效率工具安利、学习方法与规划、项目复盘模板、常见问题 |

## 31-60 天轮换表

| 天数 | 分类 | 主题 | 建议章节 |
| --- | --- | --- | --- |
| 31 | Backend | Java IO/NIO ✅ | 文件 IO、字节/字符流、NIO、Channel/Buffer、网络 IO 模型、实战案例、常见问题 |
| 32 | Backend | Java 反射与注解 ✅ | Class 对象、反射 API、动态代理、注解定义与处理、实战案例、常见问题 |
| 33 | Backend | Java 函数式编程 ✅ | Lambda、Stream、Optional、方法引用、实战案例、常见问题 |
| 34 | Frontend | CSS 进阶 ✅ | 布局体系、动画、响应式、工程化、原子化 CSS、常见问题 |
| 35 | Frontend | 前端安全 ✅ | XSS、CSRF、CSP、HTTPS、安全响应头、依赖安全、常见问题 |
| 36 | Frontend | 前端性能优化 ✅ | 加载优化、构建优化、运行时优化、监控与指标、实战案例、常见问题 |
| 37 | DB | PostgreSQL ✅ | 概述与版本、安装、SQL 基础、高级特性、索引、备份恢复、常见问题 |
| 38 | DB | MySQL 索引深入 ✅ | B+ 树原理、联合索引、索引失效场景、覆盖索引、优化案例、常见问题 |
| 39 | Ops | 网络基础 ✅ | 网络分层、DNS、TCP/IP、HTTP/HTTPS、抓包分析、常见问题 |
| 40 | Ops | 容器编排进阶 ✅ | Helm、Operator、服务网格、弹性伸缩、多集群、GitOps、安全、实战、常见问题 |
| 41 | Tools | 数据库客户端 ✅ | Navicat、DBeaver、RedisInsight、常用操作、连接管理、常见问题 |
| 42 | Tools | 接口调试工具 ✅ | Postman、Apifox、环境与脚本、Mock、自动化测试、常见问题 |
| 43 | Tools | 包管理器深入 ✅ | npm/pnpm/yarn 对比、pnpm 原理、monorepo、发布流程、常见问题 |
| 44 | Backend | Spring Cloud ✅ | 版本与 Train 存档、环境搭建、注册中心、服务调用、网关、配置中心、熔断限流、链路追踪、消息驱动、实战案例、常见问题 |
| 45 | Backend | Kafka 深入 ✅ | 架构、生产者、消费者、分区与副本、可靠性、集群、实战、常见问题 |
| 46 | Backend | 分布式事务 ✅ | 2PC、TCC、SAGA、Seata、本地消息表、实践对比、常见问题 |
| 47 | AI | 大模型应用开发 ✅ | API 调用、Function Calling、RAG、Agent 框架、成本与限流、实战、常见问题 |
| 48 | AI | RAG 检索增强 ✅ | Embedding、向量库、Chunking、检索优化、评估、实战案例、常见问题 |
| 49 | AI | 本地模型部署 ✅ | Ollama、量化、API 接入、GPU/内存规划、实战案例、常见问题 |
| 50 | Frontend | 微信小程序 ✅ | 框架与目录、组件、API、路由、发布流程、性能优化、常见问题 |
| 51 | Frontend | 跨端开发 ✅ | UniApp、Taro、Electron、方案对比、实战案例、常见问题 |
| 52 | Frontend | 前端测试 | Vitest、Jest、组件测试、E2E、覆盖率、测试策略、常见问题 |
| 53 | DB | Elasticsearch | 概述与安装、索引与映射、查询 DSL、聚合、集群、中文分词、常见问题 |
| 54 | DB | Redis 进阶 | 持久化、主从与哨兵、Cluster、缓存设计、性能调优、常见问题 |
| 55 | Ops | 日志体系 | ELK、Loki、日志采集、日志分析、告警联动、常见问题 |
| 56 | Ops | Linux 进阶 | Shell 编程、系统调优、服务管理、定时任务、安全加固、常见问题 |
| 57 | Tools | 协作与项目管理 | Jira、Confluence、飞书、研发流程、文档协作、常见问题 |
| 58 | Project | Vue3 模板补充 ✅ | 权限、主题、组件库集成、多环境、发布、常见问题 |
| 59 | Project | 完整项目实战 | 需求拆分、数据库设计、前后端联调、测试、部署、复盘 |
| 60 | Others | 年度复盘 | 文档库盘点、知识体系重构、年度总结、下一年规划 |

## 61-90 天轮换表

| 天数 | 分类 | 主题 | 建议章节 |
| --- | --- | --- | --- |
| 61 | Backend | Java 设计模式实战 | 设计原则、创建型、结构型、行为型、框架源码分析、实战案例 |
| 62 | Backend | Java 网络编程 | Socket、NIO、Netty、粘包拆包、编解码、实战案例 |
| 63 | Backend | Go 入门 | 概述与环境、语法基础、并发模型、Web 开发、实战案例 |
| 64 | Backend | 认证与授权 ✅ | JWT、OAuth2、Session、SSO、安全最佳实践、常见问题 |
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
- [x] AI 存量补全：Agent 应用专题已建设（8 篇，第 20 天）并补充 OpenClaw/提示词工程交叉链接
- [x] Frontend 存量补全：浏览器原理专题已建设（9 篇，第 21 天）并补充 AJAX/JavaScript/HTML/HTTP/SPA 交叉链接
- [x] Backend 存量补全：消息队列专题已建设（9 篇，第 22 天）并补充 Spring Boot/Python/Redis/Java 并发/Spring Cloud/Docker/K8s 交叉链接；Spring Cloud 空占位页已补正文
- [x] Backend 存量补全：微服务专题已建设（11 篇，第 23 天）并补充 Spring Cloud/Spring Boot/消息队列/Nginx/MySQL 等交叉链接
- [x] Tools 存量补全：CI/CD 专题已建设（10 篇，第 24 天）并补充 Docker/Git/微服务/Spring Boot/Kubernetes 等交叉链接
- [x] Ops 存量补全：监控告警专题已建设（9 篇，第 25 天）并补充 Kubernetes/Docker/微服务/CI/CD 等交叉链接
- [x] Frontend 存量补全：前端工程化专题已建设（9 篇，第 26 天）并补充 Vite/TypeScript/Vue/React/CI/CD 等交叉链接
- [x] DB 存量补全：SQL 优化专题已建设（10 篇，第 27 天）并补充 MySQL/监控/微服务等交叉链接
- [x] Backend 存量补全：设计模式专题已建设（8 篇，第 28 天）并补充 Java/Spring/MyBatis/前端 JS 等交叉链接
- [x] Backend 存量补全：网络编程专题已建设（10 篇，第 29 天）并补充 Java IO/线程池/AJAX/HTTP/浏览器/Nginx 等交叉链接
- [x] Others 存量补全：复盘杂项专题已建设（8 篇，第 30 天）；全库链接巡检完成（781 个文件，修复 18 处失效链接）
- [x] Backend 存量补全：Java IO/NIO 专题已建设（9 篇，第 31 天），旧「IO 流」单页拆分为完整专题并保留入口；补充 NetworkProgramming（SocketIO/Netty/FAQ）与 JVM（Tuning/Troubleshoot）交叉链接，修复 CommonClasses 相关专题位置错乱
- [x] Backend 存量补全：Java 反射与注解专题已建设（8 篇，第 32 天），补充 JVM ClassLoading/OOP/Spring AOP/IoC/MyBatis 注解交叉链接
- [x] Backend 存量补全：Java 函数式编程专题已建设（8 篇，第 33 天），补充 Collection（Iteration/FAQ/SortCompare）、Overview、CompletableFuture、CommonClasses、MyBatis-Plus 交叉链接
- [x] Frontend 存量补全：CSS 进阶专题已建设（8 篇，第 34 天），补充 CSS3（Animation/Flex/Media）、AtomicCSS、Layout、Optimize 交叉链接
- [x] Frontend 存量补全：前端安全专题已建设（8 篇，第 35 天），补充 Browser/Security、HTTP、Electron/Security、工程化 CI、SPA 交叉链接
- [x] Frontend 存量补全：前端性能优化专题已建设（8 篇，第 36 天），补充 Browser/Performance、Rendering、工程化构建优化、CSS 动画、Vite 交叉链接
- [x] DB 存量补全：PostgreSQL 专题已建设（9 篇，第 37 天），补充 MySQL（概述/FAQ/索引）、SQL 优化、MongoDB 交叉链接与选型对比
- [x] DB 存量补全：MySQL 索引深入专题已建设（8 篇，第 38 天），补充 MySQL 索引与 SQL 优化（索引原理/慢查询/执行计划/分页）交叉链接
- [x] Ops 存量补全：网络基础专题已建设（8 篇，第 39 天），补充 Docker 网络、K8s Service、Nginx 反向代理、监控概览、后端网络编程交叉链接
- [x] 断链修复：LangChain4j Rag/Concepts 缺失的架构图已补 SVG（rag-architecture、architecture），构建恢复正常
- [x] Ops 存量补全：容器编排进阶专题已建设（9 篇，第 40 天），补充 Kubernetes（Overview/Deployment/Ingress/Monitoring）、Docker Compose 进阶、监控概览、后端微服务概览交叉链接与 Logo/示意图
- [x] Tools 存量补全：数据库客户端专题已建设（8 篇，第 41 天），补充 MySQL/Redis/MongoDB/PostgreSQL 概览与 FAQ、IDE 工具交叉链接，并修复 3 处失效 PostgreSQL 相对链接
- [x] Tools 存量补全：接口调试工具专题已建设（8 篇，第 42 天），补充 CI/CD 测试、前端 HTTP、后端网络编程 HTTP、运维网络 HTTP、IDE 工具、数据库客户端交叉链接
- [x] Tools 存量补全：包管理器深入专题已建设（8 篇，第 43 天），补充 Node.js 包管理工具（npm/yarn/NpmYarn/发布管理）与前端工程化交叉链接，修复 npm 页损坏代码围栏并更新 npm unpublish 政策（24h→72h）
- [x] Backend 存量补全：Spring Cloud 专题已建设（第 44 天，13 个页面：索引 + 概述 + 版本存档 + 环境 + 8 个组件/收尾页 + 当前版本页），按 Release Train 组织并保留 EOL 存档；补充 Microservices（索引/注册/网关/负载均衡/熔断/追踪）、Spring Boot 概述、Spring、Spring Cloud 旧入口、MessageQueue 交叉链接与版本联动提示
- [x] Backend 存量补全：Kafka 深入专题已建设（第 45 天，10 个页面：概述 + 版本演进与迁移 + 架构与存储 + 分区与副本 + 生产者 + 消费者 + 可靠性/Exactly-Once + 集群运维 + 实战 + FAQ），按「既有主题内加深、不新建重复章节」原则挂在 MessageQueue/Kafka 下并保留原「Kafka 入门」内容；补充 MessageQueue（索引/概览/可靠投递/集群/FAQ/对比/幂等）与 Spring Cloud Stream 交叉链接、版本状态与命令修正（`kafka-metadata-quorum.sh`）
- [x] 大版本状态标注巡检：Kafka 按「4.x KRaft 主线 + 3.9.x ZooKeeper 仅存量集群使用」在页面内标注状态并单列迁移页，旧配置说明不删除、不覆盖；对照 Spring 5/6、Vue2/Vue3 的版本目录策略形成统一约定
- [x] Backend 存量补全：分布式事务专题已建设（第 46 天，10 个页面：概述 + 一致性基础 + 2PC/XA + TCC + SAGA + 本地消息表与事务消息 + Seata 2.x + Seata 1.x 存档 + 实战 + FAQ），按「既有主题内加深、不新建重复章节」原则挂在 Microservices/DistributedTransaction 下并保留原单页内容；补充 Microservices（索引/概览/FAQ/实战）、Spring Cloud（索引/实战）、MessageQueue（幂等/可靠投递）与 DB（MySQL 事务、锁与事务）交叉链接
- [x] 存量版本核对：Seata 版本信息更新为 2.7.0（2026-09-06 发布）并补充 Spring Cloud Alibaba 2021.0.6.0 / 2022.0.0.0 / 2023.0.1.0 组件矩阵（含 Nacos、RocketMQ、Seata 版本对照）；Seata 1.x（1.8.0 为最后版本）按版本目录存档并标注「仅存量项目使用」，同时补充 Maven 坐标差异（io.seata → 2.1.0 起 org.apache.seata）与 MySQL XA 官方限制
- [x] AI 存量补全：大模型应用开发专题已建设（第 47 天，10 个页面：概述与环境、API 调用基础、Chat Completions 兼容用法、工具与函数调用、上下文与记忆管理、RAG 检索增强接入、Agent 框架与应用集成、成本核算与限流降级、实战、FAQ），按「主线 + 存量存档」组织：主线面向 Responses API，Chat Completions 单独成页并标注存量兼容状态；补充 AI（索引/提示词工程/Agent/OpenClaw）交叉链接与官方文档地址更新
- [x] AI 事实与版本核对：按官方文档核对 Responses 与 Chat Completions 的推荐关系与迁移指南、速率限制维度（RPM/RPD/TPM/TPD 与用量层级）、提示缓存折扣与最小可缓存长度、嵌入模型维度可选、结构化输出与 strict 模式约束、工具检索的模型要求；模型 ID 与单价在文中统一标注「以官方模型页/定价页为准」，不写死版本清单
- [x] AI 存量补全：RAG 检索增强专题已建设（第 48 天，10 个页面：概述、嵌入与向量基础、文档解析与切分、向量库与索引、检索优化、评估体系、生产工程化、组件版本状态与升级、实战、FAQ），并按「主线 + 旧版本标注」组织组件版本状态（Milvus 3.x/2.6.x/1.x、pgvector 0.8.x、Qdrant 1.x、Chroma 1.x、Elasticsearch 9.x/8.x/7.x、嵌入模型代际）；补充 AI 索引、LLMApp（导航/接入页/成本/FAQ）、提示词评估与 Agent 记忆的交叉链接
- [x] 存量交叉链接与去重：把 LLMApp/RagOverview 的评估指标段收敛为「摘要 + 链接」，避免与 RAG 评估体系重复；补充「深入阅读」表引导到切分/向量库/检索/评估/工程化各页
- [x] AI 存量补全：本地模型部署专题已建设（第 49 天，10 个页面：概述与选型、Ollama 快速落地、推理服务与 API 接入、量化与模型格式、GPU 与显存规划、性能调优与压测、生产部署与运维、版本与兼容矩阵、实战：内网知识库助手、FAQ），引擎版本按官方仓库核对（Ollama v0.34.0、vLLM v0.29.0、llama.cpp v0.4.0）并按「主线 + 旧版本标注」组织（CUDA 13.x/12.x、GGUF/safetensors/AWQ/GPTQ 与仅存量的 GGML/GGJT）；补充 AI 索引、LLMApp（模型与集成）、OpenClaw（概述/架构）、RAG 实战与成本页的交叉链接
- [x] 存量接口事实核对：按 Ollama 官方文档核对 OpenAI 兼容接口能力（/v1/chat/completions、流式、JSON 模式、seed、视觉、工具调用；/v1/responses 自 v0.13.3 起且仅无状态）与原生 /api/* 端点，统一写入本地模型部署专题的 Ollama 与推理接入页面
- [x] Frontend 存量补全：微信小程序专题已就地加深（第 50 天）——WxMini 主题原本有 19 个页面但侧边栏只挂入口，本轮把全部 22 个页面挂载为分组；新增 [路由与页面栈]、[性能优化]、[基础库版本与兼容]、[调试工具链] 4 篇（补齐原缺失章节），重写 [目录页]（补官方 Logo、去 `@@@` 占位标记）、[概述]、[常见错误]（原为 2 行空壳）、扩充 [上线发布]、[全局数据共享]、[页面间通信]，并在 [原生 API] 路由章节加入深入阅读指引
- [x] 存量事实核对：按官方文档核对小程序基础库版本策略（版本号 Major.Minor.Patch、`wx.getAppBaseInfo().SDKVersion`、`wx.canIUse`、API 存在性判断、禁止字符串比较版本号、后台「基础库最低版本设置」与近 30 天版本分布），沉淀为 [基础库版本与兼容] 页面
- [x] Frontend 存量补全：跨端开发专题已建设（第 51 天，8 个页面：概述与选型、Taro 多端开发、多端工程架构、多端兼容与差异处理、桌面端跨端、实战、版本与兼容矩阵、FAQ），并遵循「已有内容不重复」原则——uni-app 与 Electron 沿用既有专题，本专题只补方案对比方法论、Taro（原库完全缺失）与多端工程化；补充 Frame 目录页、Uniapp 目录页、Electron 目录页、WxMini 目录页与前端工程化页的交叉链接
- [x] 存量版本核对：跨端组件版本按官方渠道核对（Taro v4.2.1 / 2026-07-17、Electron v44.3.0 / 2026-09-08、uni-app npm 日期构建号与 Vue3 主线），并建立「主线 + 上一代 + 仅存量」状态约定（Taro 3.x、uni-app Vue2、旧 Electron 主版本）
- [x] Backend 存量补全：认证与授权专题已建设（第 64 天，10 个页面：概述与选型、会话与 Cookie、JWT 深入、OAuth 2.1 与 OIDC、单点登录、权限模型、服务端落地、安全最佳实践、版本与兼容矩阵、FAQ），语言中立，Java 实现指向既有 Spring Security / Sa-Token 专题；同时就地补全 Spring Security 主题（v5 存档页由 1 行空壳重写、v6 目录页补全目录与状态、新增 v7 版本目录页、会话页由 13 行扩充为完整对比页）并把整棵子树挂进侧边栏，补充 Spring Cloud Gateway 与 Sa-Token 交叉链接
- [x] 存量版本核对：按官方渠道核对认证授权版本事实（Spring Security 7.1.1 / 2026-08-20、Spring Boot 4.1.1、jjwt 0.13.0、RFC 9700 OAuth 2.0 安全最佳实践、OAuth 2.1 草案 Rev 16 / draft-ietf-oauth-v2-1、RFC 7636 PKCE、RFC 9068 JWT 访问令牌），建立「主线 / 上一代 / 仅存量」状态标注（隐式与密码模式、CAS、Spring Security 5.x 标注为仅存量）
- [x] Project 存量补全：Vue3 模板新增 5 个模块（权限、主题、组件库集成、发布、常见问题），补齐 VueRequest 空壳页（原 0 行），重写项目目录页（修复 `[代码提交检查]()` 空链接、按分类重排、增加「迭代记录」），环境变量页追加多环境章节；侧边栏把基础项目展开为 20 个章节并新建 `project/Complete` 目录页（修复原先指向不存在页面的导航链接）；同时在 AGENTS.md 新增第 13 节「计划完成后的项目沉淀要求」（每次迭代都要在 project 中加模块、宁精勿滥、逐步细化）

## 节奏建议

- 每天至少产出 6 篇（1 个大主题或 2 个小主题）；当天写不完时把欠量顺延到次日补齐，不要用 1 篇概述代替。
- 每天同步调整、补充、更新 **5~10 篇存量文档**，优先处理过期版本、结构不规范、缺图缺示例、链接失效的页面。
- 遇到大版本升级（如 Spring 5 → Spring 6）时，先建新版本目录，旧版本文档保留并标注状态，不要覆盖。
- 保质保量：篇幅宁多勿少，但每篇必须满足 `AGENTS.md` 的「内容深度与完整性要求」，禁止空壳页、禁止凑字数。
- 建议每周轮换大类（后端 / 数据库 / 运维 / 前端 / 工具 / AI / 项目），避免连续同类。
- 已有内容的主题（如 Python、MySQL）**不做「进阶补全」**：不新建重复章节；需要加深、补充的内容直接在既有章节页面上更新调整，发现重复章节先合并再维护。
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
