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
6. 每天还要为「每月项目轮换表」中的当月项目添加一个可验证的构建步骤（见下文项目规则）。

## 每日产出要求

1. 新主题默认按「完整主题模板」展开：Overview → Environment → CoreConcepts → Basic → Advanced → Practice → FAQ → References（可按主题合并或拆分）。
2. 大主题每天 6~10 篇；小主题至少 3~5 篇；每篇正文必须满足 `AGENTS.md` 第 5 节「内容深度与完整性要求」，禁止空壳页。
3. 每篇至少包含：概念/原理 + 可运行示例 + 表格/清单 + 易错点/最佳实践 + 验证方式 + 参考资料。
4. 复杂概念、架构、流程必须配示意图（本地 SVG 或可授权图源）。
5. 版本、命令、API 信息必须联网核对，以官方文档为准。
6. 每天除新主题外，还要挑选 **5~10 篇存量文档**进行调整、补充与更新（内容过期、结构不规范、缺示例/配图、链接失效等），并同步侧边栏/导航。
7. 主题涉及大版本时按版本建目录（如 `Spring5/Spring6`、`Vue2/Vue3`）：新文档面向最新稳定版，旧版本保留并标注维护状态，不覆盖旧内容。
8. 每周产出文档的同时，**每天为当月项目添加一个构建步骤**（模块、接口、页面、配置或测试均可），必须能本地运行验证，并在项目目录沉淀当日文档；项目规则见「每月项目轮换表」。
9. **不再安排复盘类主题**：轮换表与建议章节中均不出现「复盘 / 年度复盘 / 阶段总结」内容，对应位置由新主题或项目里程碑日替代。

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
| 52 | Frontend | 前端测试 ✅ | Vitest、Jest、组件测试、E2E、覆盖率、测试策略、常见问题 |
| 53 | DB | Elasticsearch ✅ | 概述与安装、索引与映射、查询 DSL、聚合、集群、中文分词、常见问题 |
| 54 | DB | Redis 进阶 ✅ | 持久化、主从与哨兵、Cluster、缓存设计、性能调优、常见问题 |
| 55 | Ops | 日志体系 ✅ | ELK、Loki、日志采集、日志分析、告警联动、常见问题 |
| 56 | Ops | Linux 进阶 ✅ | Shell 编程、系统调优、服务管理、定时任务、安全加固、常见问题 |
| 57 | Tools | 协作与项目管理 ✅ | Jira、Confluence、飞书、研发流程、文档协作、常见问题 |
| 58 | Project | Vue3 模板补充 ✅ | 权限、主题、组件库集成、多环境、发布、常见问题 |
| 59 | Project | 完整项目实战 ✅ | 需求拆分、数据库设计、前后端联调、测试、部署、复盘 |
| 60 | Others | 年度复盘 ✅ | 文档库盘点、知识体系重构、年度总结、下一年规划 |

## 61-90 天轮换表

| 天数 | 分类 | 主题 | 建议章节 |
| --- | --- | --- | --- |
| 61 | Backend | Java 设计模式实战 ✅ | 设计原则、创建型、结构型、行为型、框架源码分析、实战案例 |
| 62 | Backend | Java 网络编程 ✅ | Socket、NIO、Netty、粘包拆包、编解码、实战案例 |
| 63 | Backend | Go 入门 | 概述与环境、语法基础、并发模型、Web 开发、实战案例 |
| 64 | Backend | 认证与授权 ✅ | JWT、OAuth2、Session、SSO、安全最佳实践、常见问题 |
| 65 | Frontend | Vite 深入 ✅ | 原理、配置、插件开发、环境变量、构建优化、实战案例 |
| 66 | Frontend | Webpack 深入 ✅ | 核心概念、Loader、Plugin、代码分割、优化实践 |
| 67 | Frontend | 小程序进阶 ✅ | 分包、自定义组件、云开发、性能优化、发布 |
| 68 | Frontend | Electron 深入 ✅ | 进程模型、IPC、窗口管理、打包、自动更新 |
| 69 | DB | 数据建模 ✅ | 范式、ER 图、设计原则、反范式、实战案例 |
| 70 | DB | 时序数据库 ✅ | InfluxDB、TDengine、数据模型、查询、应用场景 |
| 71 | Ops | Ansible ✅ | 概述、Playbook、常用模块、角色、实战案例 |
| 72 | Ops | Terraform ✅ | 概述、资源、状态管理、模块、实战案例 |
| 73 | Ops | 安全加固 ✅ | 系统基线、容器安全、K8s 安全、漏洞管理 |
| 74 | Tools | IDE 配置 ✅ | IntelliJ IDEA、VS Code、插件、快捷键、配置同步 |
| 75 | Tools | 效率工具 ✅ | 终端、剪贴板、截图、笔记、自动化 |
| 76 | AI | LangChain ✅ | 概述、Chain、Agent、Memory、实战案例 |
| 77 | AI | Embedding 与向量库 | 概念、Milvus/pgvector、检索优化、实战 |
| 78 | AI | 多模态应用 | 图像、语音、视频处理、模型接入、实战 |
| 79 | Project | 后端模板搭建 | 项目结构、认证、数据库、统一响应、部署 |
| 80 | Project | 完整项目（电商/博客） | 需求、架构、编码、测试、部署、验收 |
| 81 | Frontend | 数据可视化 | ECharts、Canvas、SVG、数据大屏、实战 |
| 82 | Frontend | 状态管理 | Pinia、Redux/Zustand、对比选型、实战 |
| 83 | Backend | 缓存设计 | 缓存策略、穿透/击穿/雪崩、一致性、实战 |
| 84 | Backend | 搜索引擎深入 | ES 调优、中文分词、索引生命周期、实战 |
| 85 | DB | 分库分表 | 拆分策略、中间件、分布式 ID、迁移、常见问题 |
| 86 | Ops | 云原生 | 云厂商、Serverless、容器服务、成本优化 |
| 87 | Tools | 测试工具 | JMeter、Selenium、接口自动化、性能测试 |
| 88 | AI | 智能体工作流 | n8n、Coze、Dify、落地案例、对比 |
| 89 | Project | 全流程部署实战 | Docker、K8s、CI/CD、监控、回滚 |
| 90 | Frontend | WebAssembly 入门 | 概述与场景、编译工具链、与 JS 互操作、性能对比、实战案例、常见问题 |

## 91-120 天轮换表

| 天数 | 分类 | 主题 | 建议章节 |
| --- | --- | --- | --- |
| 91 | Backend | Go 进阶 | 并发模式、内存模型、pprof 性能分析、泛型、实战案例、常见问题 |
| 92 | Backend | Go 微服务 | gRPC、Protobuf、go-zero/Kratos、服务治理、实战案例、常见问题 |
| 93 | Backend | Python Web 框架 | FastAPI、Django、SQLAlchemy、异步视图、部署、实战、常见问题 |
| 94 | Frontend | Nuxt 全栈开发 | 渲染模式、文件路由、数据获取、Server API、部署、实战、常见问题 |
| 95 | Frontend | 微前端 | 拆分策略、qiankun、Module Federation、应用通信、实战、常见问题 |
| 96 | DB | ClickHouse | 列式存储、MergeTree 引擎、分区与索引、物化视图、实战、常见问题 |
| 97 | DB | 数据库中间件 | ShardingSphere、读写分离、影子库、分布式事务、实战、常见问题 |
| 98 | Ops | 服务网格 Istio | 架构、流量治理、熔断限流、可观测、mTLS、实战、常见问题 |
| 99 | Ops | 备份与容灾 | 备份策略、RTO/RPO、容灾架构、演练流程、实战、常见问题 |
| 100 | Tools | API 设计与治理 | REST 规范、OpenAPI、版本策略、Mock 与文档、网关对接、常见问题 |
| 101 | AI | Agent 框架深入 | LangGraph 状态机、CrewAI 角色编排、人工介入、持久化、实战 |
| 102 | AI | 模型微调 | 数据集构建、LoRA/QLoRA、训练与评估、部署、实战、常见问题 |
| 103 | Backend | 高性能 Java | JMH 基准测试、JIT、内存与对象布局、锁优化、实战、常见问题 |
| 104 | Frontend | WebGL 与 Three.js | 渲染管线、场景与相机、材质光照、动画、实战、常见问题 |
| 105 | DB | 图数据库 Neo4j | 图模型、Cypher、索引与约束、图算法、实战、常见问题 |
| 106 | Ops | GitOps 落地 | Argo CD、Flux、多环境管理、密钥管理、回滚、实战、常见问题 |
| 107 | Tools | 终端进阶 | Zsh、tmux、fzf、现代 CLI 工具、自动化脚本、常见问题 |
| 108 | AI | AI 编程助手 | Copilot/Cursor/CodeBuddy、提示技巧、团队规范、度量、常见问题 |
| 109 | Project | 当月项目：账号与权限模块 | 需求、表设计、接口、页面、测试、验收 |
| 110 | Project | 当月项目：核心业务流 | 领域建模、状态机、接口联调、测试、验收 |
| 111 | Backend | 领域驱动设计 | 战略设计、战术设计、聚合与仓储、落地架构、实战、常见问题 |
| 112 | Frontend | 国际化与无障碍 | i18n 方案、多语言工作流、a11y 规范、实战、常见问题 |
| 113 | DB | 数据同步与 CDC | Canal、Debezium、Flink CDC、一致性保障、实战、常见问题 |
| 114 | Ops | 混沌工程 | 稳态假设、故障注入、演练设计、平台工具、实战、常见问题 |
| 115 | Tools | 文档体系建设 | 静态站点生成、全文搜索、多版本、写作规范、实战、常见问题 |
| 116 | AI | 提示词安全与评估 | 注入攻击与防护、红队测试、评估集建设、回归门禁、常见问题 |
| 117 | Backend | 工作流与规则引擎 | Flowable、Drools、审批流设计、实战、常见问题 |
| 118 | Frontend | PWA 与离线应用 | Service Worker、缓存策略、消息推送、安装体验、实战、常见问题 |
| 119 | Project | 当月项目：联调与压测 | 前后端联调、压测脚本、瓶颈定位、优化、验收清单 |
| 120 | Project | 当月项目：部署与验收 | 一键部署、监控接入、上线清单、文档沉淀、验收 |

## 121-150 天轮换表

| 天数 | 分类 | 主题 | 建议章节 |
| --- | --- | --- | --- |
| 121 | Backend | 分布式缓存深入 | 多级缓存、一致性方案、热点治理、实战、常见问题 |
| 122 | Backend | 响应式编程 | Reactor、WebFlux、背压、实战、常见问题 |
| 123 | Backend | 支付与订单系统 | 支付对接、对账、幂等与补偿、风控、实战、常见问题 |
| 124 | Frontend | 服务端渲染深入 | SSR/SSG/ISR、水合、流式渲染、缓存、实战、常见问题 |
| 125 | Frontend | 低代码平台 | 协议设计、渲染引擎、物料体系、搭建器、实战、常见问题 |
| 126 | DB | 数仓建模 | 分层设计、维度建模、缓慢变化维、实战、常见问题 |
| 127 | DB | 大数据生态 | Hadoop、Hive、Spark、Flink、选型、实战、常见问题 |
| 128 | Ops | 云上架构 | VPC、负载均衡、弹性伸缩、多可用区、成本、实战、常见问题 |
| 129 | Ops | 故障应急体系 | 值班制度、故障定级、应急预案、演练、常见问题 |
| 130 | Tools | 依赖与安全治理 | SBOM、漏洞扫描、许可证合规、私服治理、常见问题 |
| 131 | AI | AI 应用观测与评估 | LangSmith/Langfuse、Trace、在线评估、成本看板、实战 |
| 132 | AI | 语音与音视频 AI | ASR/TTS、实时通话、接入方案、实战、常见问题 |
| 133 | Backend | 网关深入 | Kong/APISIX、插件开发、灰度发布、实战、常见问题 |
| 134 | Frontend | 桌面应用深入 | Tauri、原生能力、安全模型、实战、常见问题 |
| 135 | DB | 向量数据库深入 | HNSW 原理、量化、混合检索、实战、常见问题 |
| 136 | Ops | 边缘计算与 CDN | CDN 原理、边缘函数、缓存策略、实战、常见问题 |
| 137 | Tools | 代码质量平台 | SonarQube、规则定制、质量门禁、实战、常见问题 |
| 138 | AI | 企业知识库落地 | 权限隔离、数据治理、问答评估、实战、常见问题 |
| 139 | Project | 新周期项目：需求与架构 | 需求拆分、技术选型、架构设计、数据库设计、验收 |
| 140 | Project | 新周期项目：核心链路编码 | 核心模块、接口契约、可运行验证、常见问题 |
| 141 | Backend | 高并发系统设计 | 分层限流、排队与削峰、热点拆分、实战、常见问题 |
| 142 | Frontend | 移动端 H5 深入 | 适配方案、性能、桥接通信、实战、常见问题 |
| 143 | DB | 数据治理入门 | 元数据、血缘、质量规则、实战、常见问题 |
| 144 | Ops | 可观测性深入 | OpenTelemetry、Trace 采样、Profiles、实战、常见问题 |
| 145 | Tools | 自建工具链 | 脚手架、CLI 开发、内部平台、实战、常见问题 |
| 146 | AI | AI 安全与合规 | 数据脱敏、内容安全、审计、合规清单、常见问题 |
| 147 | Backend | 遗留系统改造 | 绞杀者模式、防腐层、灰度迁移、实战、常见问题 |
| 148 | Project | 新周期项目：联调与测试 | 联调、自动化测试、覆盖率门禁、验收 |
| 149 | Project | 新周期项目：部署与交付 | 部署脚本、监控告警、交付文档、验收 |
| 150 | Others | 技术写作与分享 | 写作方法、图表表达、演讲与分享、实战、常见问题 |

## 每月项目轮换表

项目以**一个月（30 天）为一个周期**，从 0 到 1 构建一个**完整项目**。规则如下：

1. 每周正常产出文档的同时，**每天为当月项目添加一个构建步骤**：可以是一个模块、一组接口、一个页面、一份配置或一组测试，必须能本地运行验证（启动成功 / 接口可调 / 测试通过），并在项目目录沉淀当日文档（当日做了什么、如何验证、下一步是什么）。
2. 项目必须**广度与深度兼备**：广度上覆盖需求、设计、编码、测试、部署全链路；深度上每个核心模块都要有真实实现（可执行的 SQL、可调用的接口、可运行的页面），禁止只有设计文档没有代码。
3. 项目必须是**完整项目**：月末交付时具备一键部署脚本、上线验收清单与完整文档，能按文档从零复现。
4. 每周里程碑固定，全部可验证：
   - 第 1 周：需求拆分 + 技术选型 + 架构设计 + 数据库设计（验收：设计文档、ER 图、接口契约齐全）
   - 第 2 周：核心模块编码（验收：服务可启动、接口可调用、页面可访问）
   - 第 3 周：联调 + 测试（验收：联调通过、自动化测试全绿、压测达标）
   - 第 4 周：部署 + 文档沉淀（验收：一键部署成功、监控接入、上线验收清单全部通过）
5. 项目沉淀在 `project/` 下（基础模板放 `Base/`、完整项目放 `Complete/`），并同步更新 `project.ts` 侧边栏。

| 周期 | 天数 | 项目 | 目标 |
| --- | --- | --- | --- |
| 1 | 1-30 | Vue3 前端模板 ✅ | 已沉淀至 `project/Base/Vue3Template` |
| 2 | 31-60 | 全栈项目实战 ✅ | 已沉淀至 `project/Complete/FullStackProject` |
| 3 | 61-90 | 后端通用模板 | 认证、权限、统一响应、多环境配置、部署脚本 |
| 4 | 91-120 | 全栈博客平台 | 前后台 + 评论 + 全文搜索 + 一键部署，0→1 完整交付 |
| 5 | 121-150 | 实时监控大盘 | 指标采集 + 可视化看板 + 告警通知，0→1 完整交付 |

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
- [x] Project 存量补全：完成第 59 天「完整项目实战」，新建 `project/Complete/FullStackProject`（8 个页面：项目总览、需求拆分、数据库设计、接口联调、编码实现、测试、部署、复盘），含可直接执行的建表 SQL、接口契约、状态机代码、发布脚本与复盘模板；`project/Complete` 目录页把该项目从占位改为可点击入口，侧边栏挂载 7 个章节
- [x] Frontend 存量补全：前端测试专题已建设（第 52 天，`docs/Frontend/Testing` 9 个页面：概述与选型、Jest、Vitest、组件测试、E2E、覆盖率、测试策略与 CI、FAQ），新建主题级目录与侧边栏挂载（`/docs/Frontend/Testing`），补充前端分类目录页入口；工具版本按官方渠道核对（Vitest 5.0 / 2026-09-03、Jest 30.x、Playwright 1.63、jest-dom 7.x）并修正前端工程化概述页过期的 Vitest 4.x 版本表述；同步更新 7 篇存量文档交叉链接（JS 测试、React 测试、工程化测试速览/CI 集成/FAQ、CI/CD 测试门禁页）
- [x] DB 存量补全：Elasticsearch 专题已建设（第 53 天，`docs/DB/NoRelational/Elasticsearch` 9 个页面：概述与安装、索引与映射、查询 DSL、聚合分析、中文分词与 IK、集群架构与高可用、商品搜索实战、FAQ），版本按官方渠道核对（ES 9.5.3 / 2026-09-03，8.x 维护期），Logo 由 simple-icons 官方路径生成 PNG；侧边栏 `db.ts` 挂载 ES 子树，非关系型目录页与 DB 概述页补入口；同步更新 6 篇存量文档（SpringBoot v3 整合 ES 页由 13 行空壳扩写为完整整合页并回链专题、MongoDB FAQ 补选型对比、RAG 版本页补专题链接）
- [x] DB 存量补全：Redis 进阶专题已就地加深（第 54 天，`docs/DB/NoRelational/Redis/Advanced` 11 个页面：进阶导览 + 主从复制 + 哨兵高可用 + Cluster 分片集群 + 缓存设计 + 缓存防护 + 分布式锁与 Lua + 性能调优 + 版本演进与升级迁移 + 实战：高可用缓存集群 + 进阶常见问题），遵循「既有主题内加深、不新建重复章节」原则挂在 Redis 下并保留原基础内容；Redis 主题首页补官方 Logo（PNG，75% 居中，未标注来源）；同步更新 9 篇存量文档（Redis 目录页新增进阶分组并补 Logo、概述页版本现状改为 8.10 GA + Standard/Extended 与 EOL 表并修正「8.0 起多线程」表述、持久化页新增多部分 AOF（MP-AOF）与 8.10 `BACKUP` 命令及配图、过期淘汰页补 8.6 新增 `allkeys-lrm`/`volatile-lrm` 策略并把缓存三问题收敛为速览、通用命令页扩写内存诊断/客户端统计/8.x 新命令并补配图、基础 FAQ 与缓存三问题去重并补进阶入口、非关系型目录页补进阶子页链接、RedisInsight 页补性能与版本交叉链接、SpringBoot v3 整合 Redis 页补连接池/哨兵/集群配置与序列化说明）
- [x] 存量版本核对：Redis 版本事实按官方渠道核对（Redis 8.10 Q3 2026 GA 为最新稳定版、8.8/8.6/8.4/8.0 为 Standard、8.2 Extended EOL 2030-09-01、7.4/7.2 Extended EOL 2029-12-01、6.2 EOL 2027-04-01；8.10 新增 BACKUP/HIMPORT/LMOVEM/SUNIONCARD/SDIFFCARD、8.6 新增 HOTKEYS/IDMP/LRM、8.8 新增 Array 与 INCREX），据此建立「主线 / 维护中 / 仅存量」状态标注并写入版本页；确认 Redis 7.x 与 8.x 兼容性高，暂按单主题维护而不拆分版本目录（未来出现破坏性主版本再按 AGENTS.md 第 3 节建目录）
- [x] Ops 存量补全：日志体系专题已建设（第 55 天，`docs/Ops/LogSystem` 9 个页面：概述与选型、日志采集与传输、Elastic Stack（ELK）、Grafana Loki、日志查询与分析、日志告警与联动、存储保留与成本优化、实战：搭建集中式日志平台、常见问题与最佳实践），含主题 Logo（PNG）与 9 张 SVG 示意图；侧边栏（`ops.ts`/`sidebar.ts`）与导航（`nav.ts`）已挂载，Ops 目录页与导航「运维」分组补入口
- [x] 日志栈过期表述巡检（全库）：把存量 Monitoring 专题从「Promtail + Loki 单页」更新为「Alloy 主线 + 收敛为速览并回链新专题」——重写 [日志监控] 页（Promtail → Grafana Alloy，新增深入阅读表）、重写实战页第五步（`promtail-config.yml` → `config.alloy` + Alloy 服务与 `alloy-data` 卷）、修正 `Monitoring/assets/log-pipeline.svg` 采集器标注、更新 [监控体系与可观测性] 版本说明（Grafana 13.2.1 / Loki 3.7.7 / Alloy 1.19.x + Promtail EOL 提示）、[监控告警] 目录页与 [Grafana] [告警规则] [常见问题] 补交叉链接；同步修正 Kubernetes（Monitoring/Pod）、Docker（Monitor）、SpringBoot（Common/Deploy）、微服务（Tracing）、Elasticsearch 专题、CI/CD（PipelineDesign）等 6 处过期采集器表述与缺失链接
- [x] 大版本状态标注巡检：Elastic Stack 按「9.5.3 主线 + 8.19.x 维护中 + 7.x 已于 2026-01-15 停止维护」、Loki 按「3.7.7 主线 + 3.6.16 维护 + 3.5 已 EOL + Promtail 已 EOL 并从 3.7.3 移除 + boltdb-shipper 弃用待 4.0 移除」在页内标注状态；旧配置说明不删除、不覆盖，对照 Spring 5/6、Vue2/Vue3、Kafka 4.x/3.9.x 的既有版本目录策略保持统一约定

- [x] Ops 存量补全：Linux 进阶专题已就地加深（第 56 天，`docs/Ops/Linux/Advanced` 9 个页面：进阶总览 + Shell 脚本编程 + systemd 服务管理 + 定时任务 + 性能调优 + 安全加固 + 故障排查 + 实战：交付一台生产可用的服务器 + 进阶常见问题），遵循「既有主题内加深、不新建重复章节」原则挂在 Linux 下并保留原基础内容（Overview/DirectoryStructure/FileCommand/TextProcessing/PermissionUser/ProcessService/NetworkCommand/ShellBasic/FAQ），侧边栏以折叠子分组挂载；环境基线按官方渠道核对（Ubuntu 26.04 LTS 2026-04-23 发布、内核 7.0、systemd 259 仅支持 cgroup v2、APT 3.x 移除 `apt-key`、OpenSSH 10.2、OpenSSL 3.5 后量子算法；RHEL 系用 dnf/firewalld/SELinux），并给出升级前检查清单；含 9 张 SVG 示意图与主题 Logo（PNG）；同步更新 5 篇存量文档（ProcessService/ShellBasic 补进阶交叉链接、Linux/FAQ 补进阶入口、Docker/Security 补宿主机加固链接）
- [x] Tools 存量补全：协作与项目管理专题已建设（第 57 天，`docs/Tools/Collaboration` 9 个页面：目录页 + 概述与工具选型 + Jira 实战 + Confluence 知识库 + 飞书协作 + 研发流程 + 文档协作规范 + 实战：10 人团队协作体系落地 + 常见问题），新建主题级侧边栏挂载（`/docs/Tools/Collaboration`）与导航「工具」分组入口；版本事实按官方渠道核对（Jira Software Data Center 11.3.x LTS / 11.3.10、Jira 12 在途（Lucene 7.3→10.3.1、React 19、Jackson 3）、Confluence Data Center 10.2.x LTS、Confluence 11 在途、Cloud 持续交付），建立「自托管 / Cloud」形态说明与升级风险清单；含 9 张 SVG 示意图与主题 Logo（PNG）；同步更新 Git 工作流页补研发流程与文档规范交叉链接
- [x] Others 存量补全：年度复盘专题已建设（第 60 天，`docs/Others/AnnualReview` 9 个页面：目录页 + 复盘方法论 + 文档库与资产盘点 + 知识体系重构 + 年度总结怎么写 + 下一年规划 + 个人成长复盘 + 实战：走完一次年度复盘 + 常见问题），含取数/巡检脚本、四份产出清单与能力雷达；`sidebar.ts` 新增 `OthersAnnualReview` 并挂载 `/docs/Others/AnnualReview`，`nav.ts` 的「其他」改为下拉并补「年度复盘」入口，`docs/Others/index.md` 与「复盘杂项」互链；含 9 张 SVG 示意图与主题 Logo（PNG）；同步更新复盘杂项目录页与学习方法页交叉链接
- [x] Backend 存量补全：设计模式专题已就地加深（第 61 天，`docs/Backend/DesignPatterns` 新增 4 页：JDK 源码中的设计模式 + 现代 Java 与设计模式 + 反模式与过度设计 + 重构实战：安全地改代码），遵循「已有内容不重复」原则，只补「源码识别、语言演进替代、反模式判定、安全重构方法」四块原专题缺失的内容；版本事实按官方渠道核对（JDK 26 为最新非 LTS / 2026-03-17 发布、JDK 25 为当前 LTS / 2025-09-16 发布且 Premier Support 至 2030-09、JDK 27 计划 2026-09-14、JDK 21 上一代 LTS；Scoped Values 于 JDK 25 正式、结构化并发仍为预览），据此标注「哪些模式已被语言特性替代、哪些仍必要」；含 5 张 SVG 示意图；同步更新目录页与设计原则页交叉链接
- [x] Backend 存量补全：网络编程专题已就地加深（第 62 天，`docs/Backend/NetworkProgramming` 新增 4 页：Netty 进阶：线程模型与性能调优 + 虚拟线程与高并发模型 + 自定义协议设计 + 性能基准与压测），只补「EventLoop/ByteBuf 内存管理、虚拟线程迁移与 pinning、协议帧与兼容演进、指标定义与压测方法」四块原专题缺失的内容；版本事实按官方渠道核对（Netty 4.2.18.Final 与 4.1.138.Final / 2026-09-09，Netty 5 仍在开发不可用于生产；并补齐 4.1.136/4.2.16 之前多个安全 CVE（SPDY 内存耗尽、DNS 缓存投毒、TLS 主机名校验绕过）的升级建议；虚拟线程 JDK 21 正式、JDK 25 稳定）；新增 `benchmark-method.svg`，共 5 张 SVG 示意图；同步更新 Netty 入门页与 SocketIO 页交叉链接
- [x] 全库相对链接巡检（第 56 天取用项）：以脚本建立全库文件索引后逐条校验 Markdown 相对链接（含图片），初始发现 106 处断链（覆盖 Backend 69、Frontend 19、Ops 18、Tools 13、DB 7、Others 2，另含本次新增页面 19 处路径错误），逐条修正后 **1675 条相对链接全部可解析（0 断链）**；本次共修改 66 个文件：修正本次新增页面图片路径（`./assets/` → `../assets/`）与跨专题链接深度、Langchain4j 8 个子页 24 处 `./Xxx/` → `../Xxx/`、Microservices → SpringCloud 5 处、JavaSE/JVM 3 处、SpringBoot v3 整合 ES/Redis 5 处、SQL 优化与 MySQL/IndexPerformance 6 处、Frontend（Browser/Vite/CSS/Electron/工程化）12 处、Ops（Docker/K8s/Nginx）5 处、Tools（PackageManager）1 处；对 6 处「目标页面确实不存在」的历史悬挂引用去掉链接保留文字（MyBatis ORM/数据持久化、Spring 组件概念、SpringBoot Yaml、Spring Security 网络安全基础），不新增杜撰内容
- [x] 存量文档更新（第 56 天配套）：挑选 10 篇存量文档补充交叉链接与进阶指引——Linux/ProcessService（systemd、定时任务、排障）、Linux/ShellBasic（Shell 脚本编程）、Linux/FAQ（进阶总览与进阶 FAQ）、设计模式/Principles（四条深入阅读）、网络编程/Netty（进阶/协议/压测/虚拟线程）、网络编程/SocketIO（虚拟线程与压测）、复盘杂项目录页（年度复盘）、学习方法与规划（下一年规划、个人成长复盘）、Git/Workflow（研发流程、文档协作、流水线门禁）、Docker/Security（宿主机加固、编排安全）
- [x] DB 存量补全：数据建模专题已建设（第 69 天，`docs/DB/DataModeling` 10 个页面：目录页 + 概述与三层模型 + 核心概念 + ER 图与建模步骤 + 范式与函数依赖 + 反范式与权衡 + 设计原则与规范 + 建模工具选型 + 实战：内容社区数据库设计（含 7 张表完整可执行 DDL、索引设计表、四项验证 SQL、迁移与回滚脚本）+ 常见问题），含 10 张 SVG 示意图与主题 Logo（PNG，75% 居中）；`db.ts` 新增 `DataModeling` 并挂载 `/docs/DB/DataModeling`，`sidebar.ts` 加入 DB 大类与主题级挂载，`nav.ts` 数据库分组与 `docs/DB/index.md` 补入口；版本事实按官方渠道核对（drawDB v1.8.1 / AGPL-3.0 / 约 38k stars、SAP PowerDesigner 16.7 SP10（文档版本 16.7.10 / 2026-04-02）、Hackolade 8.12.x、DBML 与 Mermaid 语法）
- [x] 存量文档更新（第 69 天配套，9 篇）：DB/Overview（学习路线建议 + 数据建模入口）、DB/Relational 目录页（建表之前先建模 + SQL 优化入口）、MySQL/DatabaseTable（DDL 前先有模型 + 三条建模约定）、MySQL/BasicConcept（类型选择判断标准）、MySQL/IndexPerformance（索引前置考虑）、SQLOptimization/Overview（优化上限在建模阶段决定）、PostgreSQL/Practice（标注为建模方法论的 PG 落地版并互链 MySQL 版）、MongoDB/DocumentCollection（文档建模 vs 关系建模）、Tools/DatabaseClients/Navicat（客户端改表结构风险 + 迁移脚本要求）
- [x] 存量整理任务（第 69 天取一项）：**全库相对链接 + 侧边栏/导航链接双重巡检**。`linkcheck.py` 校验 1958 条相对链接（含图片）、`sidebarlink.py` 校验 1113 条侧边栏/导航链接；本次新增页面暴露 11 处断链（9 处子页图片误写 `./assets/` 应为 `../assets/`、Navicat 跨专题链接层级多一级），逐条修复后 **1958 条相对链接 0 断链、1113 条侧边栏/导航链接 0 缺失**；`bracecheck_all.py` 扫描 1222 个文件，围栏外 `{{ }}` 0 处。
- [x] Project 存量补全：当月项目（周期 3「后端通用模板」，第 69 天）添加第 1 个可验证构建步骤——新建 `project/Base/BackendTemplate`，覆盖目录结构、统一响应、全局异常、健康检查四个模块，含需求与架构文档、可运行骨架与当日进展文档（做了什么 / 如何验证 / 下一步）。
- [x] DB 存量补全：时序数据库专题已建设（第 70 天，`docs/DB/TimeSeries` 9 个页面：目录页 + 概述与选型 + 数据模型 + InfluxDB 深入 + TDengine 深入 + 查询与降采样 + 存储与保留策略 + 实战：设备监控指标平台（含建库 DDL、模拟写入脚本、两级流计算、看板查询、告警规则与验收清单）+ 常见问题），含 9 张 SVG 示意图与主题 Logo（PNG，75% 居中）；`db.ts` 新增 `TimeSeries` 并挂载 `/docs/DB/TimeSeries`，`sidebar.ts` 加入 DB 大类与主题级挂载，`nav.ts` 数据库分组与 `docs/DB/index.md` 补入口
- [x] 大版本状态标注巡检（第 70 天取一项）：InfluxDB 按「3.11.x 主线 + 3.10.x / OSS 2.9.x / OSS 1.13.x 维护中 + 3.9 及更早仅存量（3.9 已于 2026-07-30 结束支持）」、TDengine 按「3.4.1.x 主线 + 3.3.6.x/3.3.8.x 维护中 + 2.x 仅存量」在页内标注状态；旧版本说明不删除、不覆盖，对照 Spring 5/6、Vue2/Vue3、Kafka 4.x/3.9.x、Elastic Stack 9.x/8.x/7.x 的既有版本目录策略保持统一约定（确认 1.x/2.x/3.x 内容可在同一主题内按状态表并存，暂不拆分版本目录）
- [x] 存量文档更新（第 70 天配套，10 篇）：Ops/Monitoring/Overview（相关专题补时序库）、Prometheus（remote write 长期存储）、MetricsCollect（采集后如何落地存储）、Grafana（时序数据源与看板查询优化）、Alerting（时序侧告警取数与抑制）、Practice（指标长期存储落地）、FAQ（高基数与序列爆炸治理）、Monitoring 目录页（指标存哪里 tip）、DB/index.md（时序库入口）、DB/DataModeling/index.md（时序建模规则差异）
- [x] Project 存量补全：当月项目（周期 3「后端通用模板」，第 70 天）添加第 2 个可验证构建步骤——新增 3 个模块页（[请求追踪 ID 与日志切面]、[参数校验增强]、[MockMvc 集成测试]）与 2 张 SVG 示意图，覆盖 TraceIdFilter（MDC + 响应头透传）、Logback pattern 串联、WebLogAspect 日志切面、分组校验 + 自定义 `@Mobile` 注解 + 字段级错误明细、MockMvc 契约测试与 JaCoCo 覆盖率门禁；同步更新 [进展记录]（新增第 70 天段落：做了什么 / 如何验证 / 下一步）与项目总览（进度表、交付内容、`project.ts` 侧边栏补 3 个条目并把「当日进展」更名为「进展记录」）
- [x] Ops 存量补全：Ansible 自动化运维专题已建设（第 71 天，`docs/Ops/Ansible` 9 个页面：目录页 + 概述与选型 + 安装与环境准备 + Inventory 主机清单 + 模块详解 + Playbook 剧本 + 变量与事实 + Role 角色 + 实战：批量交付生产 Web 服务器 + 常见问题与最佳实践），含 9 张 SVG 示意图与主题 Logo（PNG，75% 居中，源图为官方 simple-icons 兼容图形）；`ops.ts` 新增 `Ansible` 并挂载 `/docs/Ops/Ansible`，`sidebar.ts` 加入 Ops 大类与主题级挂载，`nav.ts` 运维分组与 `docs/Ops/index.md` 补入口；版本事实按官方渠道核对（ansible-core 2.21.x 主线 2.21.2 / 2026-07-13、2.20.x 维护中 2.20.7、2.19.x 2026-11-30 结束支持、2.18 及更早已 EOL；ansible 社区聚合包 13.x 依赖 ansible-core 2.20、12.x 依赖 2.19 与 2026-12 EOL；控制节点 Python 3.12-3.14（2.21/2.20）/3.11-3.13（2.19）、被管节点 Python 3.9-3.14、Windows 自 2.21 起支持 PowerShell 5.1 + 7.x LTS）
- [x] 大版本状态标注巡检（第 71 天取一项）：Ansible 按「ansible-core 2.21.x 主线 + 2.20.x 维护中 + 2.19.x 仅存量（2026-11-30 结束支持）+ 2.18 及更早已 EOL」与「ansible 社区包 13.x 主线（依赖 core 2.20）+ 12.x 维护中（依赖 2.19，2026-12 EOL）+ 11.x 及更早仅存量」在主题首页与页内标注状态；同时把 2.19 起的破坏性变更按状态标注清楚——**Data Tagging**（条件表达式必须返回布尔值，历史 `when: some_string` 写法会报错）、**2.20 的 `INJECT_FACTS_AS_VARS` 弃用**（`ansible_facts` 字典取数、顶层变量取数将移除）、**2.21 的 `ansible-galaxy` 行为变更与 CVE-2026-11332（2.21.1 修复）**；旧写法说明不删除、保留并给出迁移路径，对照 Spring 5/6、Vue2/Vue3、Kafka 4.x/3.9.x、Elastic Stack 9.x/8.x/7.x、InfluxDB/TDengine 的既有版本目录策略保持统一约定（确认 Ansible 内容可在同一主题内按状态表并存，暂不拆分版本目录）
- [x] 存量文档更新（第 71 天配套，10 篇）：Ops/Linux 目录页（相关专题补 Ansible 批量交付）、Linux/Advanced 导览（手工步骤固化成剧本）、Linux/Advanced/Practice（交付步骤一键执行）、Linux/Advanced/ShellScripting（脚本 → 声明式幂等）、Linux/Advanced/CronTasks（定时任务批量下发与版本管理）、Nginx 目录页（批量安装/下发/reload）、Docker 目录页（批量装引擎与容器验收）、JumpServer 页面（人-机分离，Ansible 接管机器）、Ops/Others 页面（配置管理入口）、Tools/CICD/DeployRollback（虚机/裸机场景的批量部署与灰度）
- [x] Project 存量补全：当月项目（周期 3「后端通用模板」，第 71 天）添加第 3 个可验证构建步骤——新增数据访问模块页 [数据访问：MyBatis-Plus 接入] 与 1 张 SVG 示意图，覆盖 `BaseEntity`（雪花 ID + 审计字段 + `@TableLogic` + `@Version`）、`MybatisPlusInterceptor` 拦截器链注册顺序（分页 → 乐观锁 → 防全表更新）、分页 `maxLimit` 封顶、`MetaObjectHandler` 审计字段自动填充（`strictInsertFill`/`strictUpdateFill`）、逻辑删除与唯一索引冲突解法、乐观锁失效三类原因与 `PageResult<T>` 统一分页出参、雪花 ID 在 JS 侧精度处理、建表脚本 `V1__init_user.sql`、Testcontainers 数据层四类测试（填充/分页/逻辑删除/乐观锁）与 12 条常见坑；同步更新 [进展记录]（新增第 71 天段落：做了什么 / 如何验证 / 下一步）与项目总览（进度表、交付内容、`project.ts` 侧边栏补 1 个条目），并把 [MockMvc 集成测试] 的「相关文档」接上下一节

- [x] Ops 存量补全：Terraform 专题已建设（第 72 天，9 个页面：目录页 + 概述与选型 + 安装与初始化 + HCL 语法与表达式 + 资源、数据源与变量 + State 与远程后端 + 模块与注册表 + 实战：交付一套云上环境 + 常见问题与最佳实践），含 9 张 SVG 示意图与主题 Logo（PNG，75% 居中，源图为官方 simple-icons 兼容图形）；`ops.ts` 新增 `Terraform` 并挂载 `/docs/Ops/Terraform`，`sidebar.ts` 加入 Ops 大类与主题级挂载，`nav.ts` 运维分组与 `docs/Ops/index.md` 补入口；版本事实按官方渠道核对（Terraform 1.16.x 主线 1.16.2 / 2026-09-09、1.15.x 维护中、1.14 及更早仅存量、1.17 已进 beta；OpenTofu 1.12.x 主线 1.12.6 / 2026-08-19、1.11.x 维护中、1.10 及更早仅存量、1.13 已进 beta）
- [x] 大版本状态标注巡检（第 72 天取一项）：**Terraform / OpenTofu 分叉与 1.6 许可证变更**。按「Terraform 1.16.x 主线 + 1.15.x 维护中 + 1.14 及更早仅存量」与「OpenTofu 1.12.x 主线 + 1.11.x 维护中 + 1.10 及更早仅存量」在主题首页与 FAQ 页标注状态，并单列版本时间线 SVG（2023-08-10 MPL→BUSL 1.1 自 1.6.0 生效、1.5.7 为最后 MPL 版；2023-09-20 OpenTofu 进 Linux Foundation；2024-01-10 OpenTofu 1.6 GA；2025-02-27 IBM 完成收购 HashiCorp；2025-04-23 OpenTofu 进 CNCF；2026-08~09 功能实质分化）；明确两条线**state 格式互通、可交替 apply**，并给出选型判据表（内部自用 / 对外嵌入产品 / 许可证合规 / HCP Terraform 商业能力 / state 客户端加密 / provider for_each 与 episodic 资源）；旧写法说明不删除、保留并给出迁移路径（命令 `terraform` → `tofu`），对照 Spring 5/6、Vue2/Vue3、Kafka 4.x/3.9.x、Elastic Stack 9.x/8.x/7.x、InfluxDB/TDengine、Ansible 的既有版本目录策略保持统一约定
- [x] 存量文档更新（第 72 天配套，10 篇）：Ops/Ansible 目录页（补 Terraform 互补分工：Terraform 建机器、Ansible 配机器）、Ops/Kubernetes 目录页（集群本身由 IaC 建，业务负载交给 GitOps）、Ops/Docker 目录页（云主机+网络+存储交 IaC，容器由 CI/CD 拉起）、Ops/ContainerOrchestration 目录页（基础设施层 vs 应用层的交付边界）、Ops/Others 页面（配置管理入口补 IaC）、Ops/Network 目录页（网络怎么工作 vs 网络怎么被声明，含 `cidrsubnet` 网段切分）、Ops/Monitoring/Overview（告警规则与看板若由 IaC 管理需纳入漂移巡检，`plan -detailed-exitcode` 做定时巡检）、Ops/Linux/Advanced 导览（机器建好后的声明式收敛工具）、Ops/Nginx 目录页（主机与 80/443 放行由 IaC 交付）、Tools/CICD/DeployRollback（禁用 CI 直接 `apply -auto-approve`，改用「已审批 plan 文件 + apply 该文件」）
- [x] Project 存量补全：当月项目（周期 3「后端通用模板」，第 72 天）添加第 4 个可验证构建步骤——新增 [认证授权：Spring Security 7 + JWT] 模块页与 1 张 SVG 示意图（`security-auth-flow.svg`），覆盖无状态认证链路与过滤器顺序（TraceIdFilter → JwtAuthFilter → AuthorizationFilter，`addFilterBefore(..., UsernamePasswordAuthenticationFilter.class)`）、jjwt 0.13.0 令牌签发与校验、`UserContext` 桥接审计字段自动填充（接上第 71 天预留的调用点）、`RestAuthenticationEntryPoint` / `RestAccessDeniedHandler` 让 401/403 统一走 `Result<T>`、`@EnableMethodSecurity` + `@PreAuthorize` 声明式权限与数据级越权防护、`app.jwt.*` 走环境变量注入与密钥长度 >= 32 字节自检、`SecurityIT` 四个 MockMvc 用例（匿名 401 / 有效 200 / 越权 403 / 篡改 401）与 12 条常见坑；同步更新 [进展记录]（新增第 72 天段落：做了什么 / 如何验证 / 下一步）与项目总览（进度表、交付内容、`project.ts` 侧边栏补 1 个条目），并把 [数据访问：MyBatis-Plus 接入] 的「下一步」标注为已完成并接上下一节

- [x] Ops 存量补全：安全加固专题已建设（第 73 天，`docs/Ops/SecurityHardening` 10 个页面：目录页 + 安全加固方法论 + 基线合规与自动化 + 扫描工具链 + 漏洞管理生命周期 + SBOM 与软件供应链 + 密钥与凭据治理 + 审计与检测 + 实战：一条端到端安全流水线 + 常见问题与最佳实践），采用**跨层治理视角**，与既有三篇分层安全页（[Linux 安全加固]/[Docker 安全加固]/[容器与集群安全加固]）互补不重复——本专题负责方法论、基线合规闭环、漏洞生命周期、供应链、密钥、审计与工具链统一；含 9 张 SVG 示意图与主题 Logo（PNG，盾牌 + 对勾，75% 居中）；`ops.ts` 新增 `SecurityHardening` 并挂载 `/docs/Ops/SecurityHardening`，`sidebar.ts` 加入 Ops 大类与主题级挂载，`nav.ts` 运维分组与 `docs/Ops/index.md` 补入口；版本事实按官方渠道核对（Trivy 0.74.0 / 2026-08-14 且警示 v0.69.5/v0.69.6 投毒事件 CVE-2026-33634、Grype 0.118.0 / 2026-08-27、Falco 0.44.1 / 2026-06-11 且 0.44 起 modern eBPF 为默认并移除 gRPC/gVisor/legacy-ebpf、Kyverno 1.19.0 / 2026-08-20 支持 K8s 1.33-1.35、OPA Gatekeeper 1.19.1、Kubescape v4.0.12 / 2026-08-12、kube-bench 0.8.x；CIS Benchmarks：Ubuntu 24.04 LTS v2.0.0 / 2026-06、Kubernetes v1.12.0、Docker v1.8.0、RHEL 9 v2.0.0、Windows Server 2022 v4.0.0）
- [x] 大版本状态标注巡检（第 73 天取一项）：**安全基线与检查工具的版本强相关性核对**。按「CIS Benchmark 必须与系统/K8s 主版本精确对应」逐条标注状态——Ubuntu 24.04 LTS v2.0.0、Kubernetes v1.12.0、Docker v1.8.0、RHEL 9 v2.0.0、Windows Server 2022 v4.0.0；同时标注**工具版本状态**：Trivy 0.74.0 主线（旧版 v0.69.5/v0.69.6 存在投毒事件，必须升级）、Falco 0.44 起驱动默认切换为 modern eBPF 且移除三种旧驱动（升级需评估兼容性）、Kyverno 1.19.0 支持 K8s 1.33-1.35；按状态标注 CIS Level 1（基础线，几乎不影响功能）与 Level 2（更严，可能限制功能需评估）的取舍，并明确托管集群（EKS/GKE/AKS）控制面检查项应视为 notapplicable、需按「你能控制的部分」裁剪；旧写法说明不删除、保留并给出迁移路径，对照 Spring 5/6、Vue2/Vue3、Kafka 4.x/3.9.x、Elastic Stack 9.x/8.x/7.x、InfluxDB/TDengine、Ansible、Terraform/OpenTofu 的既有版本目录策略保持统一约定（确认安全基线与工具内容可在同一主题内按状态表并存，暂不拆分版本目录）
- [x] 存量文档更新（第 73 天配套，8 篇）：Ops/Linux/Advanced/SecurityHardening（主机层 → 跨层治理专题入口）、Ops/Docker/Security（镜像与运行时 → 供应链与密钥治理）、Ops/ContainerOrchestration/Security（集群层 → 基线合规与审计检测，并补「相关专题」段）、Ops/JumpServer（特权访问 → 凭据托管与操作审计）、Tools/CICD/DeployRollback（部署前安全门禁：依赖/镜像扫描与签名验签）、Ops/Kubernetes/ConfigMapSecret（Secret 集中托管、动态凭据与轮换）、Ops/Monitoring/Alerting（安全事件告警）、Ops/LogSystem/Collection（安全审计日志采集与留存）
- [x] Project 存量补全：当月项目（周期 3「后端通用模板」，第 73 天）添加第 5 个可验证构建步骤，同时作为**第 3 周（联调与测试）起点**——新增 [登录业务闭环与令牌生命周期] 模块页与 1 张 SVG 示意图（`auth-lifecycle.svg`，登录锁定 / 使用刷新 / 登出吊销三段），覆盖 `AuthService` 账号锁定（连续失败 5 次锁 15 分钟、成功清计数、统一错误码防账号枚举）、自定义 `@StrongPassword` 校验器（8~64 位 + 四类字符取三 + 弱口令字典）、登录审计表 `t_login_log` 与建表脚本 `V2__init_login_log.sql`、Redis 键设计（`auth:refresh`/`auth:blacklist`/`auth:fail`/`auth:lock`）、双令牌刷新（Refresh 一次性消费防重放、复用即吊销全部会话）与登出 `jti` 黑名单（TTL = Access 剩余有效期）、`SecurityIT` 从 4 个用例扩到 8 个（新增过期令牌 / 黑名单命中 / Refresh 复用 / 连续失败锁定）与 10 条常见坑；同步更新 [进展记录]（新增第 73 天段落：做了什么 / 如何验证 / 下一步）与项目总览（进度表、交付内容、`project.ts` 侧边栏补 1 个条目），并把 [认证授权：Spring Security 7 + JWT] 的「下一步（第 73 天）」标注为已完成并接上下一节

- [x] Tools 存量补全：IDE 配置专题已建设（第 74 天，`docs/Tools/IDE` 10 个页面：目录页 + 概述与选型 + IntelliJ IDEA 深入 + VS Code 深入 + 插件管理 + 快捷键与效率 + 配置同步 + 远程与容器化开发 + 实战：团队统一 IDE 环境 + 常见问题与最佳实践），围绕**个人同步 / 团队统一（入库）/ 环境可复现（Dev Container）三层配置分层**展开，并与既有 [配置规范与团队协作]、[Docker]、[后端通用模板] 互链；含 10 张 SVG 示意图与主题 Logo（PNG，75% 居中）；`tools.ts` 新增 `IDE` 子页树并挂载，`nav.ts` 顶部导航「IDE工具」更名为「IDE 配置」、`docs/Tools/index.md` 同步；版本事实按官方渠道核对（IntelliJ IDEA 2026.2.2 / 2026-09-02（2026.2.1 / 2026-08-10）、**2025.3 起为统一发行版**且 Core 免费 + Ultimate 订阅、AI Free 在 IDEA 中需 Ultimate 才可用；VS Code 1.137 / 2026-09-09，2026 年已发 27 个版本；Eclipse 2026-09 / Platform 4.41；JetBrains Fleet 已于 2025-12-22 停售并停止支持、由 Air 承接）
- [x] 大版本状态标注巡检（第 74 天取一项）：**全库 IDE 过期表述巡检**。按「IDE 主版本状态」逐页核对存量文档中的版本口径，共修出 2 类过期表述——① [Spring Boot 创建项目] 中「IntelliJ IDEA 2024.3+」已不在主流支持周期内，改为「2025.3+（统一发行版起）」并补社区版/旗舰版在 Spring 初始化器与 AI 能力上的差异说明；② [Vue3 模板 · 配置 CSS 代码检查工具] 与 [初始化项目] 中的 VS Code 扩展 ID 写错（`prettier.prettier-vscode` 应为 `esbenp.prettier-vscode`、`stylelint.vstylelint` 应为 `stylelint.vscode-stylelint`、`Vue.volar` 应为 `Vue.vue-official`），这类错误会让团队统一清单里的 `--install-extension` 直接失败，逐条改正并补 `:::danger` 说明扩展 ID 的 publisher 前缀不能想当然；旧写法不删除、保留并给出替代路径，对照 Spring 5/6、Vue2/Vue3、Kafka 4.x/3.9.x、Elastic Stack 9.x/8.x/7.x、InfluxDB/TDengine、Ansible、Terraform/OpenTofu、安全基线工具的既有版本目录与状态标注策略保持统一约定
- [x] 存量文档更新（第 74 天配套，10 篇）：Backend/Java/JavaSE/Environment（安装 IDE 一节按统一发行版改写，并交叉链接 IDE 配置）、Backend/Go/Environment（补「相关文档」接 IDE 页）、Backend/Python 目录页（解释器选择 tip 接 IDE 配置）、Backend/Java/Frame/SpringBoot/Common/CreateProject（版本口径修正 + 相关文档）、Frontend/Others/FrontendEngineering/CodeStandard（补「相关文档」接配置同步与实践页）、Others/Review/EfficiencyTools（补 IDE/快捷键/插件交叉链接）、Tools/Build/Maven/FAQ（补 IDEA 索引与 Maven 联动）、Tools/VersionControl/Git/FAQ（补快捷键与配置同步交叉链接）、Tools/APITools/Overview（补 VS Code 与远程开发链接）、Ops/Docker 目录页（`devcontainer` ≠ 生产镜像的边界说明，接远程开发页），另修复 [Vue3 模板 · 配置 CSS 代码检查工具]/[初始化项目] 的扩展 ID 错误
- [x] Project 存量补全：当月项目（周期 3「后端通用模板」，第 74 天）添加第 6 个可验证构建步骤，同时作为**第 3 周（联调与测试）第二阶段**——新增 [压测与性能基线] 模块页与 3 张 SVG 示意图（`performance-baseline.svg` 压测闭环四步 + 三道门禁、`coverage-gate.svg` 按模块设覆盖率阈值与 `verify` 阶段门禁、`contract-regression.svg` 契约导出与比对流程），覆盖 k6 2.x 双场景压测脚本（登录 20 VU + 受保护接口 50 VU 阶梯、`thresholds` 直接作门禁、`setup()` 复用令牌）、指标口径统一（TPS/QPS/VU/P50-P99/错误率/饱和度）与「并发数当 TPS 汇报」「只报均值」等三类错误写法、基线三要素（环境 + 数据量 + 脚本版本）与 YAML 记录模板、工具分工（k6 做门禁 / wrk 做极限初筛 / JMeter 5.6.3 保存量多协议，`jmeter -n -t -l -e -o` 无界面跑）、JaCoCo 0.8.15 三段配置（`prepare-agent`→`report`→`check`）与按模块阈值（common 80 / web 70 / security 75 / data 60）及排除项、springdoc-openapi 3.1.x 契约导出（`jq -S` 排序入库）与 `check-openapi-contract.sh` 破坏性变更拦截、三道门禁的 CI 接入与豁免规则（性能门禁默认不进 PR、夜间跑趋势）、「JWT/Redis 是否瓶颈」的三条对照判定法与 9 条常见坑；同步修正项目总览的 springdoc 版本口径（`2.x 线` → `3.x 线`，Boot 4.x 必须用 3.x）与遗留的 `/p>` 残片，更新 [进展记录]（新增第 74 天段落：做了什么 / 如何验证 / 下一步）与项目总览（进度表、交付内容、`project.ts` 侧边栏补 1 个条目），并把 [登录业务闭环与令牌生命周期] 的「下一步（第 74 天）」三项标注为已完成
- [x] Tools 存量补全：效率工具专题已建设（第 75 天，`docs/Tools/Efficiency` 10 个页面：目录页 + 概述与选型 + 终端与 Shell 环境 + 命令行提效 + 剪贴板与输入效率 + 截图与标注 + 笔记与知识管理 + 桌面与任务自动化 + 实战：搭一套个人效率工具链 + 常见问题与最佳实践），以**「终端 → 命令行 → 剪贴板 → 截图 → 笔记 → 自动化」六环节链路**为主线，核心方法论是「三条底线（键盘优先/版本化/只留天天用的）」与「回本周期 = 学习成本 ÷ 每周节省」的选型算法，并与既有 [IDE 配置]、[版本控制工具]、[协作与项目管理]、[运维 · Linux]、[后端通用模板] 互链；含 10 张 SVG 示意图（工具地图/终端四层栈/命令行链路/剪贴板流水线/截图工作流/笔记三层结构/自动化三标准/工具链协同/回本周期账/排障决策树）与主题 Logo（PNG，75% 居中）；`tools.ts` 新增 `Efficiency` 子页树并挂载 `/docs/Tools/Efficiency`，`sidebar.ts` 引入并加入 `/docs/Tools` 汇总项与主题级挂载，`nav.ts` Tools 分组与 `docs/Tools/index.md` 补入口；版本事实按官方发布页逐条核对（Windows Terminal 1.24.11911.0 / 2026-08-31 且需 Win10 2004+、Shell Integration command marks 自 1.21 稳定；PowerShell 7.6 LTS 最新补丁 7.6.5 / 2026-08-14 支持至 2028-11-14、非 LTS 线 7.5.10 于 2026-11-10 结束、7.6.0 起 winget 默认装 MSIX、与 Windows PowerShell 5.1 并存且 `$PROFILE` 互相独立；PowerToys 0.101.2362.0 / 2026-08-25 且 Advanced Paste 端侧 AI 转换依赖 Copilot+ PC 的 NPU 与 Phi Silica、普通机器上置灰；AutoHotkey v2.0.28 / 2026-09-12 且 v1 已不再维护；Obsidian 1.13.8 / 2026-08-20 且 1.13 起设置界面重构为独立窗口并加入全局搜索、1.14.x 处早期访问；fzf 0.74.3 / 2026-08-10；ripgrep 15.2.0 / 2026-07-16；zoxide 0.9.9 / 2026-01-31；starship 1.26.0 / 2026-06-28）
- [x] 时间敏感表述巡检（第 75 天取一项）：**全库"相对时间"表述体检**。按「凡出现『最新/目前/当前版本』一律要带核对日期，或用可复核的判据替代」逐条筛查全库，命中 30 余处，其中 3 处确需修正——① [Spring Boot v3 概览] 原写「目前最强的 3.1 正式版会维护到 2025 年中旬」，这是 2023-08 的当时口径，事实早已反转：**Spring Boot 3.1 的 OSS 支持在 2024-06-30 就结束了**（商业支持 2025-06-30 到期），改为保留原文 + `:::warning` 时间敏感表述提醒 + 一份 2026-09 核对的五档版本状态表（4.1.x 主线 OSS 至 2027-07-31 / 4.0.x OSS 至 2026-12-31 / 3.5.x OSS 已于 2026-06-30 结束但商业支持至 2032-06-30 / 3.4.x 已结束 / 3.3 及更早已结束），并补 `:::danger` 说明「Spring Boot 不设 LTS，每个 minor 一律 12 个月 OSS + 12 个月商业支持，只能滚动升级」；② [Vue3 路由] 的「目前是 `4` 版本」补核对时间与「补丁号以 `npm view vue-router version` 为准，不要照抄本文写作时的数字」；③ 项目总览 [后端通用模板] 技术选型表补「测试」一行，写明 **Spring Boot 4.0 起默认 JUnit 6**（JUnit 5 写法继续可用）与 Testcontainers 2.0.x，并声明集成测试用真实容器而非 H2。旧写法一律保留、不删除、加标注，对照 Spring 5/6、Vue2/Vue3、Kafka 4.x/3.9.x、Elastic Stack 9.x/8.x/7.x、InfluxDB/TDengine、Ansible、Terraform/OpenTofu、安全基线工具、IDE 主版本的既有版本目录与状态标注策略保持统一约定
- [x] 存量文档更新（第 75 天配套，10 篇）：Others/Review/EfficiencyTools（顶部补 `:::info` 说明本页是「安利清单」、系统方法论见专题，相关文档补 3 条接效率工具专题）、Tools/IDE 目录页（相关专题首位补「IDE 管写代码时、效率工具管写代码之外」的分工说明）、Tools/VersionControl 目录页（新增「版本控制还能管什么」一节：dotfiles / AHK 脚本 / 笔记库 / 文档库四类资产的版本化与私有仓库提示，并补相关专题）、Ops/Linux 目录页（相关专题补终端四层结构与 `rg`/`fzf`/`bat`/`jq` 两条交叉链接）、Tools/Collaboration 目录页（相关专题补「统一规则、不统一工具」的取舍）、Others/AnnualReview/KnowledgeRefactor（相关专题补笔记库三层结构与「笔记库 vs 发布型文档库」的分工边界）、project/Base/BackendTemplate 总览（参考资料补效率工具与实战两条）、Backend/Python/Environment（新增「相关文档」四条，说明 `curl` 在 PowerShell 里是别名需写 `curl.exe` 这类跨平台差异）、AI/OpenClaw/Install（「以管理员身份打开 PowerShell」补 `:::tip` 说明 5.1 与 7.6 的 `pwsh.exe` / `powershell.exe` 区别与 profile 独立）、Backend/Java/Frame/SpringBoot/v3/Overview.md（见上一项巡检）
- [x] Project 存量补全：当月项目（周期 3「后端通用模板」，第 75 天）添加第 7 个可验证构建步骤，同时作为**第 3 周（联调与测试）第三阶段**——新增 [测试数据隔离与边界用例] 模块页与 2 张 SVG 示意图（`test-isolation.svg` 三档隔离方案 + 六维对比表、`boundary-matrix.svg` 九类输入 × 三值取法的边界矩阵 + 四步法），覆盖「不再用 H2 假装 MySQL」的完整论证（7 项方言差异对照表）、Testcontainers 2.0.x 接入（singleton container 模式 + `@DynamicPropertySource` 注入随机端口）与 **2.0 的三处破坏性变更**（模块统一加 `testcontainers-` 前缀、容器类迁到 `org.testcontainers.<模块名>` 包、移除 JUnit 4 支持，并给出留在 1.21.x 的选项）、隔离三档的速度/隔离度/跨线程可见性/自增序列四维对比与各自的失效场景（`@Transactional` 在三类场景下必失效）、`TRUNCATE` 的隐式提交语义与外键约束处理、按 `t_` 前缀动态清表的 `DatabaseCleaner`、**清库与 Redis `flushDb` 必须成对**（否则会出现「第二次跑就被锁」的玄学失败）、JUnit 并行执行配置（类内并行、类间 `same_thread`）与 `@ResourceLock` 的类间互斥写法、边界用例四步法与九类输入矩阵（`username`/`password` 长度、字符类、`id`、分页 `size`/`page`、排序字段白名单、令牌 `exp`、失败次数）、参数化测试用 `"a".repeat(n)` 规避手数字符串、注入 `Clock` 替代 `Thread.sleep` 消灭时间类 flaky、`RANDOM_PORT` + `CountDownLatch` 对齐起跑线的并发刷新用例（断言「恰好一次成功」）与 **Spring Boot 4 中 `TestRestTemplate` 已废弃改推 `RestTestClient`** 的说明；同步更新 [进展记录]（新增第 75 天段落：10 项产出 / 6 条验证命令 + 8 项待填实测 / 10 条问题与决策 / 下一步；并在第 74 天的「下一步」后加 `:::warning` 记录**顺序调整**——原计划第 75 天做 Docker 化，实际先收口第 3 周，Docker 化顺延到第 80 天，理由是「测试地基不牢就容器化，回头还要改测试，同一段路走两遍」），更新项目总览（进度表拆出第 75 天行与第 76-79 天行、交付内容补第 11 项并把进展记录改为第 12 项、技术选型补测试一行、`project.ts` 侧边栏补 1 个条目）
- [x] Project 存量补全：当月项目（周期 3「后端通用模板」，第 76 天）添加第 8 个可验证构建步骤，作为**「模板产品化」起点**（本日为项目侧插队日，见下方说明）——① 新增 [技术栈可插拔：模块边界与选择器脚本] 页 + 3 张 SVG 示意图（`pluggable-architecture.svg` 四层模块与依赖方向、`stack-matrix.svg` 三维组合矩阵与 5 预设、`selector-flow.svg` 选择器四步流程与六类产物），覆盖模块划分从直线结构（`application → web → security → data → common`）重构为四层 + 可替换实现层（`common → spi → web / 实现层 → application`）与四条依赖单向约定、**SPI 契约设计**（`AuthPort` / `TokenStatePort` / `CachePort` / `UserRepository`）及「**不统一 ORM 的 CRUD 接口**」的完整论证（四套 ORM 的 CRUD 取交集等于最弱能力集：分页模型、条件构造、多表 join 差异巨大的六维对照表）、`TokenStatePort.sharedAcrossInstances()` 让降级可被程序读到、两层可插拔（Maven profile 决定谁进 reactor / Spring 条件决定谁生效）及 **Spring Boot 4 中自动配置注册位置从 `spring.factories` 改为 `AutoConfiguration.imports`** 的坑、**能力降级门禁**（`cache != redis` 时令牌撤销 / 失败计数 / 账号锁定必须显式 `--allow-degraded-cache`，而 `login-log-enabled` 因写数据库不受影响）、`stack-select.py` 的三条设计性质（幂等 = 生成物是三维取值的纯函数且不含 preset 名、`--check` 非交互可当 CI 门禁、只写 marker 区间且区间外含缩进与换行风格一字节不动）与六类生成物、`selftest.py` 的 **57 项断言**（含 24 组合全生成、CRLF 保留、marker 区间内外行为区分）；② 新增 [模板 CLI：从 0 到 1 的设计评审与路线图] 页 + 2 张 SVG（`cli-layers.svg` 分层与数据流、`two-channels.svg` 生成器 vs 切换器双通道），覆盖**生成器（greenfield）与切换器（brownfield）是两个问题**的完整论证与变更成本三档（可增量 / 需重建装配 / **禁止**）、生成内核三方案对比（全自研 vs 复用 `initializr-generator` vs 混合）与 Initializr 扩展点对应表、模板组织与**文件级条件包含**（难点在「文件存不存在」而非插值）、Mustache vs FreeMarker 取舍、Picocli 选型与 GraalVM native image（490ms → 3ms，及**模板资源需 `-H:IncludeResources`** 的坑）、版本目录（`versions.toml` 含 Boot 线到 starter 坐标的映射）、支持矩阵收窄与「不支持必须报错并说明原因」、生成物配置与安全约定（环境变量占位 + **不给默认值即 fail fast 是特性**）、MVP 验收标准（唯一硬标准：`mvn -q clean verify` 退出码 0）与 7 项明确不做、四阶段路线图；③ 新增可执行交付物 `project/Base/BackendTemplate/stack-select/stack-select.py`（零第三方依赖，约 570 行）与 `selftest.py`（57 项断言）及 `fixture/` 骨架；④ 同步更新 [项目总览]（模块划分改为四层可插拔结构 + 四条约定 + 重构原因说明、技术选型表安全/数据/缓存三行改为「二选一 / 四选一 / 三选一」并写明降级约束、进度表拆出第 76 天行与第 77-79 天行、交付内容补第 13/14 项并把进展记录改为第 15 项、本地运行补选择器与自测命令、参考资料补两条）与 [进展记录]（新增第 76 天段落：六项产出 / 8 条验证命令 + 12 项实测记录（脚本部分 8 项 ✅ 已实跑）/ 12 条问题与决策 / 下一步；并在第 75 天的「下一步」加 `:::warning` 记录**顺序调整**——原计划第 76-79 天继续收口测试，实际第 76 天插队做模板产品化、第 77-79 天回到联调收口，理由是「这一步会决定后面所有交付物的形态，先定形态再做部署产物省一轮返工」），`project.ts` 侧边栏补 2 个条目，并修正 `pluggable-architecture.svg` 的 SPI 层术语（补 `TokenStatePort`，与正文一致）
- [x] 存量事实核对（第 76 天取一项）：**CLI 相关技术栈的「版本状态与坐标」核对**。按官方渠道逐条核对并据此修正了三处**时间敏感**表述——① **Java：方案原写「Java 21 是当前最新 LTS」，2026-09 已不成立**，实测 javaalmanac / Adoptium：JDK 25 LTS（2025-09-16 GA，支持至 2030-09，最新 25.0.4.1）为**当前 LTS**，JDK 26（2026-03-17，非 LTS）已于 2026-09 停止服务、JDK 27（2026-09-14）刚发布仍为非 LTS、JDK 21 LTS 支持至 2029-12、JDK 17 LTS 至 2027-10，并据此建立「最新版本 ≠ 最新 LTS（非 LTS 生命周期仅 6 个月）」的判定规则；② **Shiro：方案原写「传统项目之选、适合非 Spring 生态、老旧系统维护」，需更新**，实测 Shiro **3.0（2026-06-29 GA，最新 3.0.1 / 2026-08-23）明确支持 Spring 6/7+ 与 Spring Boot 3/4+**，1.x/2.x 已 EOL，3.0 基线为 JDK 17+ / Jakarta EE 9-11+ / 在 JDK 25+ 上用 Scoped Values 替代 ThreadLocal；社区动能确弱（ASF 董事会 2026-06 记录：状态 Ongoing with moderate activity、邮件列表流量低、16 committer / 12 PMC、**最近一位新增 PMC 成员为 2022-12-04**、安全漏洞报告显著增加，同期修 5 个安全问题发 4 个 CVE），据此把结论从「框架优劣」改为**「v1 不纳入支持矩阵，理由是可插拔成本」**（`Realm`/`Subject`/`SecurityManager` 领域模型与 Spring Security / Sa-Token 差别最大，第三个实现边际成本最高）；③ **Spring Boot 落点**：4.0.x（2025-11 GA）OSS 支持 2026-12 到期、**4.1.x（2026-06）OSS 支持至 2027-07** 为推荐落点、3.x 全部已于 2026-06 结束 OSS 支持，明确「判断该落在哪个版本要看支持窗口而不是版本号大小」；④ **starter 坐标随 Boot 线变化**（同主题内首次核对并落表）：Sa-Token `sa-token-spring-boot4-starter`（最新 1.46.0 / 2026-08-20）、MyBatis-Plus `mybatis-plus-spring-boot4-starter`（自 3.5.13 起，最新 3.5.17）、MyBatis-Flex `mybatis-flex-spring-boot4-starter`（最新 1.11.7），三家均提供 BOM 故版本可统一但 **artifactId 无法靠 BOM 解决、必须按 Boot 线映射**；⑤ **Boot 4 模块化的两个显式依赖**：MyBatis-Flex 因 starter 不再含 jdbc/datasource 自动配置须显式加 `spring-boot-starter-jdbc`，MyBatis-Plus 自 3.5.13 起 jsqlparser 被解耦（因 jsqlparser 5.0+ 不支持 JDK 8）须显式加 `mybatis-plus-jsqlparser`；⑥ **Jackson 2 → 3 包名迁移**（`com.fasterxml.jackson` → `tools.jackson`，仅 `jackson-annotations` 保留在 `com.fasterxml.jackson.annotation`；`Jackson2ObjectMapperBuilder` 已移除改用 `JsonMapper.builder()`）与测试侧 API 变更（`@MockBean` → `@MockitoBean`、`@SpringBootTest` 不再自动配置 MockMvc），照抄 Boot 3 教程的生成物会直接编译不过；⑦ **Picocli 4.7.7** 与 `picocli-codegen` 的 GraalVM 能力边界（只生成 picocli 自身反射配置，**模板资源需自行 `-H:IncludeResources`**；native image 启动约 3ms vs JVM 约 490ms）；⑧ **Spring Initializr 模块与扩展点**核对（`initializr-generator` / `-generator-spring` / `-metadata` / `-version-resolver` / `-web`；`ProjectDescription` + `ProjectGenerator` + `ProjectAssetGenerator` + `ProjectContributor` + `@ProjectGenerationConfiguration` + `spring.factories` 注册 + `ProjectDescriptionCustomizer` + `ProjectGenerationContext`；**上游仍为 pre-1.0、可能重构**，故策略为「当依赖用、不 fork 源码、版本锁在版本目录、升级跑 golden file 回归」），并以 Alibaba `start.aliyun.com` 为定制实例生产先例支撑「方案 C：骨架用 Initializr、技术栈装配用自研 marker 方案」的选型。以上核对结果全部写入新增两页并在相应位置标注版本与核对时间
- [x] 存量文档更新（第 76 天配套，4 篇 + 1 项资产修正）：project/Base/BackendTemplate/index.md（模块划分由五模块直线结构重写为四层 + 实现层，含四条依赖约定与「为什么重构而不是新增模块」的 `:::info` 说明；技术选型表安全/数据/缓存三行由单一选型改为「二选一 / 四选一 / 三选一」并写明版本基线与降级约束；进度跟踪表新增第 76 天行、原「第 76-79 天」行收窄为「第 77-79 天」；交付内容新增第 13/14 项、进展记录顺延为第 15 项；本地运行补充环境要求（Python 3.11+）、选择器四条命令与 57 项自测；参考资料补两条）、project/Base/BackendTemplate/Progress/index.md（新增第 76 天完整段落；第 75 天「下一步」加 `:::warning` 记录顺序调整并在其决策表补一行；里程碑对照表新增「模板产品化（第 76 天插入）」行并把第 3 周进度更新为 3/4 且注明顺延；参考资料补本日两条）、.vitepress/project.ts（BackendTemplate 子树补 2 个条目）、DOCS_PLAN.md（本页记录）；资产修正（3 项）：① `pluggable-architecture.svg` 的 SPI 契约层文案由「AuthPort / CachePort / 业务 Service 接口」改为「AuthPort / TokenStatePort / CachePort / UserRepository」，与正文契约设计一致；② **配图目录归位**——本次新增的 5 张 SVG 原落在 `StackSelect/assets/` 与 `TemplateCli/assets/` 两个新建子目录里，与本主题既有约定（子页统一引用主题级 `../assets/`，其余 12 个子页均如此）不一致，已全部并入 `project/Base/BackendTemplate/assets/`，并把 5 处引用由 `./assets/` 改为 `../assets/`，归并后本主题 assets 为 24 张 SVG + 1 张 Logo PNG；③ **补上首页 Logo 并补齐契约清单**——`backend-template-logo.png` / `.svg` 自第 69 天建项目时入库后从未被任何页面引用（孤儿资产），现按各专题首页惯例在项目总览 H1 下插入居中 Logo（`./assets/backend-template-logo.png`，75% 缩放），同时把「技术栈可插拔」条目里的 SPI 契约清单补上漏列的 `UserRepository`，与正文第 3 节的四个契约一致
- **备忘（第 76 天为项目侧插队日）**：本日先在项目侧插队做「模板产品化」（技术栈可插拔 + 选择器脚本 + 模板 CLI 设计），轮换表第 76 天主题（AI · LangChain）与本日「存量文档 5~10 篇」配额当时**未执行、顺延**。**同日稍后已补齐**：LangChain 专题 9 页 + 11 张配图 + 侧边栏/导航挂载，并以 **11 篇**存量交叉链接补足配额（见下方两条记录）。由此形成的约定：**项目侧插队日必须先说明「当日轮换主题与存量配额何时补」，且不得跨工作日结转**——「明天再补」在实际执行中会退化成「永远不补」
- [x] 全库相对链接巡检与**巡检工具盲区修正**（第 76 天取用项）：发现巡检脚本存在覆盖盲区——`linkcheck.py` 一直只遍历 `docs/` 目录，**整个 `project/` 树从未被检查过**，所以脚本此前报「broken = 0」时，`project/Base/BackendTemplate/StackSelect/index.md` 第 586 行的链接深度错误（`./TemplateCli/index.md` 应为 `../TemplateCli/index.md`）依然存在且不会被暴露。已把脚本扫描根由单一 `docs` 改为两个页面根 `docs` + `project`（并在输出里回显 `scanned roots`），新增覆盖 **233 条** project 侧相对链接（checked 2465 → **2698**），修正该处链接后 **broken = 0**；同一趟顺带做资产清点：`project/Base/BackendTemplate/assets/` 下 25 个资产**无「被引用但文件不存在」**，也**无有效孤儿**（仅 logo 的 `.svg` 源文件未被引用，与各专题 `xxx-logo.png` + `.svg` 成对入库、页面只引 PNG 的既有约定一致）；另校验 `docs/Tools/Efficiency/assets/` 12 个资产同样无孤儿、无缺失。结论：**「巡检通过」只对脚本实际扫过的范围成立**，范围本身要定期复核
- [x] AI 存量补全：LangChain 专题已建设（第 76 天轮换主题，本日先做项目插队、同日稍后补齐）——`docs/AI/LangChain` 9 个页面：目录页 + 生态概览与 v1 变更 + 环境与模型接入 + 从 Chain 到 Runnable + Agent 与中间件 + 记忆与上下文 + LangGraph 编排 + 实战：带人工审批的检索增强 Agent + 常见问题与最佳实践，以 **Python 侧 LangChain v1 为主线**，核心方法是**先把「LangChain（框架）/ LangGraph（运行时）/ LangSmith（平台）」三层边界分清再谈选型**（三者独立安装、独立授权，可以只用 LangGraph 不用 LangChain，也可以完全不用 LangSmith），并给出与 Java 侧 [LangChain4j] 的四维分工判据（团队主语言 / 生态新鲜度 / 部署形态 / 长流程编排）与混合架构的代价说明（多一次网络边界与一套部署，收益是模型侧迭代不被后端发版节奏拖住——需权衡、不是默认正确）；含 11 张 SVG 示意图与主题 Logo（PNG，75% 居中）；`AI.ts` 新增 `AI_LangChain` 子树，`sidebar.ts` import 并加入 `/docs/AI` 汇总与主题级挂载，`nav.ts` AI 分组与 `docs/AI/index.md` 补入口；**版本事实按包注册表逐一核对并落表**（Python：`langchain` 1.4.0 / 2026-09-03、`langchain-core` 1.6.3 / 2026-09-11、`langgraph` 1.2.11 / 2026-08-11、`deepagents` 0.7.14 / 2026-09-14；TypeScript：`langchain` 1.5.11 / 2026-09-09、`@langchain/core` 1.2.11 / 2026-09-12、`@langchain/langgraph` 1.4.15 / 2026-09-12），并按「主线 + 存量存档」标注代际分界——`langchain 1.0.0` 发布于 **2025-10-17**，v0.x 写法（`LLMChain` / `ConversationChain` / `AgentExecutor` / `create_react_agent`）**不删除**、统一标注为存量写法并给出迁移路径，同时说明 v0.3 线到 **2026-05** 仍在收补丁（`0.3.29` / 2026-05-05）故存档线短期不会消失
- [x] 存量事实核对（第 76 天轮换配套）：**LangChain 生态版本口径与两处失效文档域名**。① **版本表先写后核、修出两处落后**——初稿把 Python 侧写作「`langchain` 1.3.x / `langchain-core` 1.5.x」，按 PyPI 实际发布修正为 **1.4.x（1.4.0 / 2026-09-03）** 与 **1.6.x（1.6.3 / 2026-09-11）**，并把「当前线」列统一下沉到「大版本.次版本 + 首发日期」的写法（只写 `1.3.x` 这类次版本号会在一个 minor 周期内就过期）；`langgraph` 1.2.x、`deepagents` 0.7.x、TS 三行核对后无误；正文内联示例「Python 是 1.3、TS 是 1.5」同步改为 1.4。② **两处失效域名**——`docs/AI/Agent/Workflow` 与 `docs/AI/Agent/MultiAgent` 的参考资料仍指向已废弃的 `langchain-ai.github.io/langgraph/...`，官方文档已整体迁到 `docs.langchain.com`，逐条替换为现行地址（`https://docs.langchain.com/oss/python/langgraph/overview`、`https://docs.langchain.com/oss/python/langchain/multi-agent`，两条均实测可访问），并在原位置补本库 LangChain 专题的对应页链接。③ 确认 `langgraph-supervisor`（最后发布 0.0.31 / 2025-11-19）与 `langgraph-swarm`（0.1.0 / 2025-12-04，此后无发布）确已冻结，与新页「多智能体用子图与路由自行组织」的建议一致。旧写法一律保留、不删除、加标注，对照 Spring 5/6、Vue2/Vue3、Kafka、Elastic Stack、InfluxDB/TDengine、Ansible、Terraform/OpenTofu、安全基线工具、IDE、CLI 技术栈的既有版本状态标注策略保持统一约定
- [x] 存量文档更新（第 76 天轮换配套，11 篇）：AI/LLMApp 目录页（相关专题首位补 LangChain，写明「直接调 SDK」与「引入装配框架」两条路线的分工）、AI/RAG 目录页（接 LangChain · 实战的检索增强 Agent，说明「本页讲检索那一段、那里讲装配那一段」）、AI/Agent 目录页（接 LangChain 的 `create_agent` 与六个中间件钩子）、AI/PromptEngineering 目录页（接 LangChain · 记忆与上下文，把「上下文预算」落到框架里）、AI/LocalModel 目录页（接 LangChain · 环境与模型接入，与既有的 Langchain4j 模型集成并列）、AI/Java 占位页（在「待补充」提示下补 Java 侧可先看的 LangChain4j 与 Python 侧 LangChain，并转述四维分工判据，避免占位页成为死链终点）、AI/LLMApp/AgentIntegration（参考资料补 LangChain 的 Agent 与中间件、实战页，接上「写操作需人工确认」→ `interrupt` 的落点）、AI/Agent/Workflow（参考资料换掉失效域名并补 LangGraph 编排与本库多智能体页）、AI/Agent/MultiAgent（参考资料换域名 + 补 LangGraph 编排与生态概览，说明「用了 Agent 框架 ≠ 已有编排与可观测」）、Backend/Java/Frame/Langchain4j 目录页（新增「相关专题」段：LangChain / 大模型应用开发 / 本地模型部署，把 Java 与 Python 两条线互接）、Backend/Python/Environment（相关文档补 LangChain · 环境与模型接入，说明 `pip index versions` 判版本与写锁文件的场景）

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
同时为「每月项目轮换表」中的当月项目添加一个可验证的构建步骤：
项目以一个月为周期从 0 到 1 构建，广度与深度兼备，必须是完整项目，
当天产出可以是模块、接口、页面、配置或测试，必须能本地运行验证，
并在项目目录沉淀当日文档（当日做了什么、如何验证、下一步是什么），
按「需求设计 → 核心编码 → 联调测试 → 部署验收」的每周里程碑推进；
不安排复盘类主题，轮换表与章节中均不出现复盘内容；
更新侧边栏（必要时更新导航），
运行 pnpm docs:build 验证，最后按 Conventional Commits 规范提交并 push 到 GitHub 远程仓库。

补充要求：涉及大版本的主题按版本目录组织（如 Spring5/Spring6），旧版本保留并标注状态，不覆盖旧内容。
```
