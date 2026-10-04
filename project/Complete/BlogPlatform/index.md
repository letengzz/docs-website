# 全栈博客平台

周期 4（第 91-120 天）的从 0 到 1 完整项目：**前后台 + 评论 + 全文搜索 + 一键部署**。它不是又一个「博客教程」——前三个周期分别沉淀了前端模板（Vue3Template）、全栈方法论（FullStackProject）、后端模板（BackendTemplate），这个项目把这些资产**全部当成现成积木**，在真实业务里组装一遍，验证「模板复用」这条路到底通不通、哪里卡。

::: warning 本项目只有文档，没有代码
`project/` 是**纯文档目录**：下面所有章节讲的都是「这个项目怎么做出来」——目录结构、配置内容、代码片段、命令与判据全部写在正文里，但**仓库不存放源码、脚本、SQL 与构建文件**。
正文里出现「运行 `xxx`」时，指的是**先在你的工程里按本节内容创建好该文件**，再执行。
:::

## 一句话定位

一个可直接上线的个人/小团队博客系统：前台面向读者（SEO 优先），后台面向作者（写作与管理），核心链路是**写文章 → 发布 → 被搜到 → 被评论**。月末交付判据：一键部署成功、上线验收清单全部通过、按文档能从零复现。

## 为什么是博客

| 备选项目 | 为什么不选 / 为什么选博客 |
| --- | --- |
| 待办 / 记事本类 | 业务太薄，撑不起「评论、搜索、渲染管线」三个有深度的子系统 |
| 电商类 | 第 80 天已在 `docs/Backend/Ecommerce` 完整讲过领域建模，重复 |
| **博客** | 业务人人熟悉（不用花篇幅解释需求），但**一个都不少**：SSR 与 SEO、富文本/Markdown 渲染管线、两级评论嵌套、全文检索、缓存与热点、审核与安全——广度够；且每个子系统都有真实的技术决策点，深度也够 |

## 与既有资产的关系

| 既有资产 | 在本项目中的用法 |
| --- | --- |
| [后端通用模板](../../Base/BackendTemplate/index.md) | **后端基座**：认证、统一响应、异常、TraceId、数据访问、门禁全套直接复用，本项目只写业务层 |
| [Vue3 模板](../../Base/Vue3Template/index.md) | 后台管理端的工程约定来源（目录结构、权限、组件库集成） |
| [全栈项目实战](../FullStackProject/index.md) | 流程模板：四周里程碑、联调、验收的走法照搬，遇到分歧点单独说明 |
| [Nuxt 专题](../../../docs/Frontend/Frame/Nuxt/index.md) | 前台选型的依据：博客是 SEO 密集型业务，纯 CSR 不合格，Nuxt 的渲染模式与 Server Routes 正面回应这一点 |
| [完整项目交付](../../../docs/Others/ProjectDelivery/index.md) | 方法论：验收条件写法、契约先行、迁移六步法在需求/设计页直接引用 |

## 技术选型

| 层 | 选型 | 一句话理由 |
| --- | --- | --- |
| 前台（读者端） | **Nuxt（Vue3 SSR）** | SEO 是博客的生命线；首屏与 TTFB 由 SSR 兜底 |
| 后台（作者端） | **Vue3 + Element Plus** | 管理端无 SEO 需求，SPA 够用；复用 Vue3Template |
| 后端 | **Spring Boot 4.1 + Java 25** | 以 BackendTemplate 为基座，业务代码只写领域层 |
| 主库 | **MySQL 8.4** | 内容关系性强；沿用模板的双方言能力，PG 作为部署期可选项 |
| 全文搜索 | **MySQL ngram FULLTEXT 起步** | 中文搜索先用内置方案把链路打通，预留 ES 升级路径（见数据库设计页的取舍论证） |
| 缓存 | **Redis 8** | 文章详情与列表热点缓存、点赞计数 |
| 部署 | **Docker Compose + CI 门禁** | 一键部署；门禁复用模板的 `gates.json` 机制 |

:::tip 提示
选型的完整论证（含「为什么前台不用 SPA」「为什么搜索不直接上 ES」）在 [架构设计与技术选型](./Architecture/index.md)，这里只放结论。
:::

## 四周里程碑

| 周 | 天数 | 内容 | 验收判据 |
| --- | --- | --- | --- |
| 第 1 周 | 91-97 | 需求拆分、技术选型、架构设计、数据库设计 | 需求含 Given/When/Then 验收条件；ER 图 + 建表 SQL 可执行 |
| 第 2 周 | 98-104 | 核心编码：文章 CRUD、Markdown 渲染管线、分类标签、后台管理 | 服务可启动、接口可调用、后台页面可访问 |
| 第 3 周 | 105-111 | 评论、全文搜索、前台 SSR、联调与测试 | 评论链路通、中文搜索可用、自动化测试全绿 |
| 第 4 周 | 112-120 | 一键部署、监控接入、上线验收、文档沉淀 | Compose 一键起、验收清单通过、能按文档从零复现 |

## 进度跟踪

| 日期 | 产出 | 状态 |
| --- | --- | --- |
| 第 91 天 | 立项：需求拆分 + 技术选型 + 架构 + 数据库设计（7 表 DDL + ER 图） | ✅ |
| 第 92 天 | 接口契约先行（OpenAPI 3.1，4 链路 12 路径）+ 双方言 DDL + parity/contract 两个本地门禁 | ✅ |
| 第 93 天 | Maven 多模块骨架 + 两条运行路径（local / prod+flyway）+ 结构门禁与行为冒烟（27 断言 / 9 用例） | ✅ |
| 第 94-97 天 | 第 1 周收尾：仓储接真库 + 契约测试上移 `mvn test` | ⏳ 待办（管理端写接口已在第 98 天提前落地） |
| 第 98 天 | 文章写入链路：管理端 CRUD + 发布状态机 + 分类标签字典 + 第三道门禁 `admin_smoke`（37 步，可重复） | ✅ |
| 第 99 天 | 管理端认证与角色：Bearer 令牌签发与校验、PBKDF2 口令哈希、默认拒绝的鉴权规则、401 先于 403 | ✅ |
| 第 100 天 | 文章下线动作：四态状态机（DRAFT / PUBLISHED / OFFLINE / DELETED）+ 时间戳语义 + 第二道写链路门禁 `lifecycle_smoke`（24 步） | ✅ |
| 第 101 天 | Markdown 渲染能力补齐：写时渲染（与发布同事务）+ 表格/引用块 + TOC 中文锚点 + 高亮分工（服务端透传、客户端着色） | ✅ |
| 第 102 天 | 可见性收敛：读者端列表/详情对非 PUBLISHED 一律 404（存在性不泄漏）+ 缓存失效时序（提交后失效 + TTL 兜底）+ 读侧门禁 `visibility_smoke`（22 步） | ✅ |
| 第 103 天 | 测试分层收口：断言按「依赖什么」分流，渲染器/状态矩阵/401 先于 403/分页边界上移 `mvn test`；分类与标签计数对齐 PUBLISHED 口径 | ✅ |
| 第 104 天 | 判据收口与分类标签联调：smoke 中已上移断言下线 + `assertion_audit.py` 判据唯一性核查；`withCount` 服务端单一口径 + L1-L6 六条两端联调动作 | ✅ |
| 第 105 天 | 评论写入链路：两级楼层模型定稿（`root_id = 自身 id`、`floor` 写时分配 + 唯一索引）+ 写入三约束（PUBLISHED 才可评 / 父评论同文章 / 已删不可回）+ `comment_smoke` 断言清单先行，门禁扩到八道 | ✅ |
| 第 106 天 | 评论读侧：楼层 keyset 分页（游标 = floor，禁 offset）+ 楼内回复全量返回 + 已删楼层「占位保留」口径（修订 S2）+ 契约 401/403 分支穷举评论路径（C1~C10）+ 审核状态读侧生效，`comment_smoke` 扩到 28 步 | ✅ |
| 第 107 天 | 全文搜索：`search_text` 与渲染同事务 + 两处服务端配置（`ngram_token_size` 只读、`innodb_ft_enable_stopword=OFF`）+ 查询串净化与布尔模式短语匹配 + `EXPLAIN` 走索引断言 + `search_smoke`（9 步），门禁扩到九道 | ✅ |
| 第 108 天 | 前台 SSR：`useAsyncData` 四纪律 + hydration 三红线 + SEO 元信息（TDK/canonical/og:）+ SSR 缓存头与失效时序 + 搜索页 400 转友好提示 + `ssr_smoke`（R1~R10，10 步），门禁扩到十道 | ✅ |
| 第 109 天 | 读者账号与权限：账号生命周期五状态 + `users` 扩列与 `user_tokens` 新表 + 令牌轮换与复用检测 + 数据归属（只能动自己的）+ 三处口径收敛；`account_smoke`（22 步），门禁扩到十一道 | ✅ |
| 第 110 天 | 核心业务流收口：三个聚合与事务边界 + 转移 × 副作用矩阵 + 字段依赖清单 D1~D10 + 五段时序走查 + 一条龙回归 CF1~CF14（`coreflow_smoke`），门禁扩到十二道 | ✅ |
| 第 111 天 | 第 3 周正式收口：回归报告实测回填四步清单定稿 + 两项欠账显式处置（Docker DDL 实测移至第 112 天 Compose 首验；压测顺延第 119 天）+ 第 4 周交接 | ✅ 本日 |
| 第 112-120 天 | 第 4 周：部署 / 监控 / 验收 | ⏳ |

## 各章节

1. [需求拆分与验收条件](./Requirements/index.md)：用户故事、INVEST、Given/When/Then、非功能需求
2. [架构设计与技术选型](./Architecture/index.md)：分层架构、渲染模式、搜索方案取舍、缓存策略
3. [数据库设计](./DatabaseDesign/index.md)：ER 图、7 张表完整 DDL、索引设计、搜索字段设计
4. [接口契约](./Contract/index.md)：OpenAPI 3.1 四条链路定稿、双方言 DDL 与 parity 门禁
5. [工程骨架与验收门禁](./Skeleton/index.md)：四模块分层、两条运行路径、结构门禁与行为冒烟
6. [文章写入链路](./WritePath/index.md)：管理端 CRUD、发布状态机与软删除、Markdown 消毒、第三道门禁
7. [管理端认证与角色](./AuthRoles/index.md)：Bearer 令牌、PBKDF2 口令哈希、角色模型与默认拒绝的鉴权规则
8. [文章下线动作](./Lifecycle/index.md)：四态状态机、四个动作的迁移矩阵、非法路径 409 与时间戳语义
9. [Markdown 渲染能力补齐](./Rendering/index.md)：写时渲染、表格/引用块、TOC 中文锚点、高亮分工与明确不做
10. [可见性收敛](./Visibility/index.md)：读者端只看得到 PUBLISHED、404 一致性判据、缓存失效时序与读侧门禁
11. [测试分层收口](./TestLayers/index.md)：断言按依赖分流、上移与保留清单、`mvn test` 门禁与六道门禁顺序
12. [判据收口与分类标签联调](./Consolidation/index.md)：判据唯一性自动核查、分类与标签的服务端单一口径、L1-L6 六条两端联调动作
13. [评论链路：两级楼层的建模与写入](./Comments/index.md)：楼层模型与写时楼层号、写入三约束、`comment_smoke` 断言清单的分层定稿
14. [评论读侧：楼层分页、占位渲染与契约穷举](./CommentRead/index.md)：keyset 分页与楼内回复全量、已删楼层占位口径、401/403 分支穷举、审核状态读侧生效
15. [全文搜索：MySQL ngram 先行](./Search/index.md)：`search_text` 写入时机、两处服务端配置、布尔模式短语匹配与净化、`EXPLAIN` 走索引断言
16. [前台 SSR：服务端取数、hydration 一致与 SEO 元信息](./FrontendSSR/index.md)：`useAsyncData` 四纪律、软 404 透传、TDK/canonical/og:、SSR 缓存头与失效、搜索页服务端渲染
17. [读者账号与权限](./ReaderAccount/index.md)：账号生命周期、`users` 扩列与 `user_tokens`、令牌轮换与复用检测、数据归属矩阵、SSR 下的登录态与缓存切分
18. [核心业务流收口](./CoreFlow/index.md)：三个聚合、转移 × 副作用矩阵、字段依赖清单、五段时序走查、一条龙回归 CF1~CF14 与第 3 周验收结论
19. [第 3 周收口](./Week3Close/index.md)：回归报告实测回填四步清单、Docker DDL 与压测两项欠账的显式处置、第 4 周交接
19. [进展记录](./Progress/index.md)：每天做了什么、如何验证、下一步

## 在你自己的工程里跑起来

本仓**不含可直接运行的工程**。按下表把对应章节的内容落到你的工程后，验证顺序与判据如下（`your-project/` 指你自己建的工程目录）：

```shell
cd your-project/service
mvn install -DskipTests                         # 首次需联网（本地仓库缺来源元数据，-o 会失败）
mvn test                                        # ② 单元测试：秒级，不起服务、不连数据库
cd blog-application && export SERVER_PORT=18080
mvn spring-boot:run                             # 默认 profile=local：内存仓储，不需要数据库
```

```shell
# 另开终端：十二道行为门禁（结构 / 只读行为 / 写链路行为 / 状态迁移 / 读侧可见性 / 评论链路 / 全文搜索 / 读者账号 / 前台 SSR / 核心业务流一条龙 / 判据唯一性）
cd your-project/service
python skeleton_check.py                            # 期望 checks = 27  failed = 0
python api_smoke.py       --base http://127.0.0.1:18080 # 期望 cases = 9   passed = 9
python admin_smoke.py     --base http://127.0.0.1:18080 # 期望 steps = 37  passed = 37（会写数据，只对本地环境跑）
python lifecycle_smoke.py --base http://127.0.0.1:18080 # 期望 steps = 24  passed = 24（状态迁移矩阵）
python visibility_smoke.py --base http://127.0.0.1:18080 # 期望 steps = 22 passed = 22（读侧可见性）
python comment_smoke.py   --base http://127.0.0.1:18080 # 期望 steps = 28 passed = 28（评论读写链路，第 105 天起、第 106 天扩）
python search_smoke.py    --base http://127.0.0.1:18080 # 期望 steps = 9  passed = 9（全文搜索，第 107 天起；需 MySQL 已按第 107 天配好 ngram 参数）
python account_smoke.py   --base http://127.0.0.1:18080 # 期望 steps = 22 passed = 22（读者账号，第 109 天起；需先执行 V2 增量 DDL）
python ssr_smoke.py --base http://127.0.0.1:3000 --api http://127.0.0.1:18080 # 期望 steps = 10 passed = 10（前台 SSR，第 108 天起；需前台已按第 108 天构建并启动）
python coreflow_smoke.py  --base http://127.0.0.1:18080 # 期望 steps = 14 passed = 14（核心业务流一条龙，第 110 天起；覆盖五段时序与三个接缝）
python lifecycle_smoke.py --selftest                    # 期望 selftest: 24/24 通过（证明断言不是恒真）
python search_smoke.py    --selftest                    # 期望 selftest: 9/9 通过
python account_smoke.py   --selftest                    # 期望 selftest: 22/22 通过
python ssr_smoke.py       --selftest                    # 期望 selftest: 10/10 通过
```

```shell
# 判据唯一性与分类标签两端一致（第 104 天新增）
python assertion_audit.py                   # 期望 PASS：每条判据只有一个归属（退出码 0）
curl -s 'http://127.0.0.1:18080/api/v1/categories?withCount=true'
                                            # 期望：每个分类都带 postCount；空分类返回 0 而非消失
```

各门禁脚本的完整设计、断言清单，以及「哪条断言该放单元测试、哪条必须留在冒烟脚本」的分层判据，见[测试分层收口](./TestLayers/index.md)、[工程骨架与验收门禁](./Skeleton/index.md)、[文章写入链路](./WritePath/index.md)与[文章下线动作](./Lifecycle/index.md)；判据唯一性核查与分类标签两端一致见[判据收口与分类标签联调](./Consolidation/index.md)；评论链路见[评论链路：两级楼层的建模与写入](./Comments/index.md)与[评论读侧](./CommentRead/index.md)；全文搜索的两处服务端配置与 `EXPLAIN` 断言见[全文搜索：MySQL ngram 先行](./Search/index.md)；前台 SSR 的 `useAsyncData` 纪律、软 404 透传与 SEO 元信息见[前台 SSR](./FrontendSSR/index.md)；读者账号的生命周期、令牌轮换与数据归属矩阵见[读者账号与权限](./ReaderAccount/index.md)；三个聚合、状态机副作用矩阵、字段依赖清单与一条龙回归 CF1~CF14 见[核心业务流收口](./CoreFlow/index.md)。

## 参考资料

- 项目方法论：[完整项目交付](../../../docs/Others/ProjectDelivery/index.md)
- 后端基座：[后端通用模板](../../Base/BackendTemplate/index.md)
- 前台框架：[Nuxt 全栈开发](../../../docs/Frontend/Frame/Nuxt/index.md)
- 搜索升级路径：[Elasticsearch 专题](../../../docs/DB/NoRelational/Elasticsearch/index.md)
- 账号与权限：[认证与授权专题](../../../docs/Backend/Auth/index.md)（会话 / JWT / 权限模型 / 服务端落地）｜ [Spring Security 6](../../../docs/Backend/Java/Frame/SpringSecurity/index.md)
- MySQL ngram 全文解析器（官方，含空格/停用词/词元搜索的确切行为）：[dev.mysql.com/doc/refman/8.4/en/fulltext-search-ngram.html](https://dev.mysql.com/doc/refman/8.4/en/fulltext-search-ngram.html)
- 账号安全规范：[RFC 9700 OAuth 2.0 Security BCP](https://www.rfc-editor.org/rfc/rfc9700)（刷新令牌轮换与撤销）｜ [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
