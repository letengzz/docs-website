# 进展记录

每个条目记录三件事：**做了什么、如何验证、下一步是什么**。格式沿用 [后端通用模板 · 进展记录](../../../Base/BackendTemplate/Progress/index.md)。

::: warning 本页命令里的路径指「你自己的工程」
本仓是**文档库**，不存放代码：`service/`、`api/`、`db/`、`ops/` 等路径指的是**你按对应章节搭起来的工程目录**，`python xxx.py` 指的是**你按该章节实现出来的脚本**。
第 91~98 天的条目记录的是当时的做法与实测输出，用来对照判据；**不能直接在本仓复现**。
:::

## 2026-09-27（第 91 天）：立项 —— 需求、选型、架构、数据库一次成型

**做了什么**：

1. **立项与定位**：确定「全栈博客平台」为周期 4（第 91-120 天）项目，核心主张是**把前三个周期的资产当积木**——后端以 [后端通用模板](../../../Base/BackendTemplate/index.md) 为基座、后台管理沿用 [Vue3 模板](../../../Base/Vue3Template/index.md) 约定、前台选型依据 [Nuxt 专题](../../../../docs/Frontend/Frame/Nuxt/index.md)；
2. **需求拆分**（[需求页](../Requirements/index.md)）：三角色四链路，6 个核心用户故事全部写 Given/When/Then；非功能需求给出可验收判据（P95、限流阈值、SEO 的 curl 断言）；明确四项**不做**（多媒体上传、私信、ES 集群、主题系统）并归档理由；
3. **技术选型与架构**（[架构页](../Architecture/index.md)）：前台 Nuxt SSR（本项目第一个不可逆决策，含三方案对比）；搜索方案定为 MySQL ngram FULLTEXT 起步 + 三条升级硬约定（SearchService 单接口、检索字段独立、升级触发条件写死）；缓存与计数按数据形态分四档；
4. **数据库设计**（[数据库页](../DatabaseDesign/index.md)）：6 张业务表 + 1 张回写表的完整可执行 DDL（MySQL 8.4），ER 图，六项设计决策表（slug 暴露、正文双列、评论两级冗余 root_id、软删除范围等），索引与三个高频查询一一对应；
5. **侧边栏与目录**：项目挂载进 `project.ts` 与 [完整项目目录](../../index.md)。

**如何验证**：

```shell
# ① DDL 可执行性（需 Docker；本机暂无则标注待验证，第 92 天工程骨架初始化时补跑）
docker run --rm -i mysql:8.4 mysql -uroot -proot -e "
  CREATE DATABASE IF NOT EXISTS blog DEFAULT CHARSET utf8mb4;
  USE blog; SOURCE /dev/stdin;" < db/mysql/V1__blog_init.sql
# 期望：无报错；SHOW TABLES 列出 7 张表

# ② 设计自检
#  - 需求页 6 个 US 每个都能在 ER 图上找到落位表
#  - 架构图上四条主链路都有落点
#  - DDL 中每个高频查询有对应索引（后续 EXPLAIN 复验）
```

**问题与决策**：

| 问题 | 决策 |
| --- | --- |
| 后端选 Spring Boot 还是 Go？ | Spring Boot。理由不是语言偏好，而是**基座复用**：模板的认证/门禁/双方言能力直接继承，Go 侧虽已有入门与微服务专题但没有等价模板，等于全部重写 |
| 搜索要不要直接上 ES？ | 不上。个人博客量级远未到 ES 的舒适区，「预留升级路径」落成三条硬约定（见架构页），比提前引入一套集群更符合「可逆决策从快」 |
| 评论层级做两级还是无限级？ | 物理两级 + 楼层内平铺。无限级的产品价值存疑、查询与展示成本陡增；`root_id` 冗余让整层回复一个索引取完 |
| 草稿对匿名返回 404 还是 403？ | 404。403 等于承认「这个 slug 存在」，未发布内容的存在性本身就是泄露 |

**下一步（第 92 天）**：① 接口契约先行——四条链路的 OpenAPI 契约定稿并入库（可 diff）；② 工程骨架初始化（多模块结构 + Flyway + PostgreSQL 版 DDL 过 parity 门禁）；③ 补跑本日 DDL 的 Docker 验证。

:::info 状态回填（第 92 天）
上面三项已完成 ①②，③ 因**本机无 Docker** 仍标注待验证（验证命令已写进 [契约页](../Contract/index.md)，进入部署周前补跑）。详见下方第 92 天段落。
:::

## 2026-09-29（第 92 天）：契约先行 + 双方言 DDL + 两个本地门禁

**做了什么**：

1. **OpenAPI 3.1 契约定稿**（[契约页](../Contract/index.md)）：四条链路 12 条路径 / 14 个操作入库 `api/openapi.json`——文章（读者端只暴露 slug、未发布 404）、分类标签（name/slug 双唯一 409）、评论（两级楼层 + 软删除）、搜索（**SearchService 单接口**，升级 ES 不改契约）；统一响应 `Result<T>` + Bearer JWT 口径显式声明；
2. **双方言 DDL**：`db/mysql/V1__blog_init.sql`（第 91 天定稿入库）+ `db/postgres/V1__blog_init.sql`（七条翻译规则：DATETIME→TIMESTAMP、MEDIUMTEXT/TEXT→TEXT、行内 COMMENT→COMMENT ON、内联索引→CREATE INDEX、FULLTEXT(ngram)→GIN(to_tsvector)、`ON UPDATE CURRENT_TIMESTAMP` 移交应用层）；
3. **两个零依赖门禁**：`db/parity_check.py`（类型归一化逐列比对 + 主键/唯一/普通索引一致 + 检索索引「名称对齐、列形态豁免」注册表）与 `api/contract_check.py`（版本、$ref 可解析、每个操作有响应结构、四条链路齐全）；
4. **契约页沉淀**当日文档（做了什么 / 如何验证 / 问题与决策 / 下一步），`project.ts` 侧边栏补「接口契约」条目。

**如何验证**：

```shell
cd project/Complete/BlogPlatform
python db/parity_check.py       # ✅ 实测：OK: 7 张表 / 42 列 双方言结构一致
python api/contract_check.py    # ✅ 实测：OK: 12 条路径 / 14 个操作，$ref 全部可解析，四条链路齐全

# 变异法确认门禁有效（不是摆设）：
#  - PG 版一列类型改 INTEGER → parity 报「类型不一致」退出码 1
#  - 删一个 200 响应的 content → contract_check 报「缺少 content」退出码 1
# Docker 验证 DDL：本机无 Docker，待部署周前补跑（命令见契约页）
```

**问题与决策**：

| 问题 | 决策 |
| --- | --- |
| FULLTEXT(ngram) 与 GIN(to_tsvector) 列形态不同，parity 会误报 | 检索索引进注册表：名称两侧必须对齐，列形态豁免——强行对齐方言特性没有意义 |
| PG 没有 `ON UPDATE CURRENT_TIMESTAMP` | 移交应用层显式写 `updated_at`；不加触发器，保持两侧 DDL 逐列可对照 |
| 契约用 YAML 还是 JSON？ | JSON：标准库可校验、零新依赖；需要 YAML 时 `yq` 互转 |
| 写接口 200 要不要声明响应结构？ | 要。首轮 contract_check 抓出 8 处「200 缺 content」——契约的价值恰恰在把这类含糊提前暴露 |

**下一步（第 93 天）**：Maven 多模块工程骨架初始化（以 BackendTemplate 裁剪 common/web/data + Flyway 装载 `db/mysql/V1__blog_init.sql`），第 2 周第一个服务 `PostService` 按**已定稿契约**实现——先跑通「契约 → 实现 → 契约测试」的最小闭环（`GET /api/v1/posts` 返回真实数据）。

:::info 状态回填（第 93 天）
本项已完成，落地为四模块骨架（多出一个 `blog-application`：可启动模块单独隔开）+ 两道门禁，「契约 → 实现 → 验收」最小闭环已跑通。详见下方第 93 天段落与 [工程骨架页](../Skeleton/index.md)。
:::

## 2026-09-29（第 93 天，接第 92 天同日推进）：Maven 四模块骨架 + 结构/行为两道门禁

**做了什么**：

1. **四模块 Maven 骨架**（`service/`，[工程骨架页](../Skeleton/index.md)）：聚合 POM `blog-parent` + `blog-common`（零依赖）→ `blog-data` → `blog-web` → `blog-application`（唯一可启动），依赖方向单向且由门禁强制；
2. **两条运行路径**：`local` 走内存仓储（无数据库即可跑完整链路）、`prod + flyway` 走真实迁移脚本；SQL 的唯一来源是仓库根 `db/<vendor>/`，构建期用 `maven-resources-plugin` 复制进 classpath，切方言只改 `-Dblog.db.vendor=`；
3. **契约落成实现**：`PostController` 实现读者端 `GET /api/v1/posts` 与 `/{slug}`，`MAX_PAGE_SIZE=50` 与契约一致；`GlobalExceptionHandler` 把 `ErrorCode` 映射到 400/404/401/403/500；
4. **两个零依赖门禁**：`skeleton_check.py`（**结构**，27 条断言：模块名单/依赖方向/版本来源/生产配置/迁移命名与双方言对齐）与 `api_smoke.py`（**行为**，9 个用例含草稿 404、越界分页 400 等错误路径）；两者都内置 `--selftest` 变异测试；
5. **修复两个「编译通过、运行才炸」的坑**并留痕：漏 `-parameters` 导致参数绑定全 500；缺 `spring.profiles.default` 导致裸跑启动失败。

**如何验证**：

```shell
cd project/Complete/BlogPlatform/service

# ① 结构门禁（不需要数据库、不需要起服务）
python skeleton_check.py                # ✅ 实测：checks = 27  failed = 0  → PASS
python skeleton_check.py --selftest      # ✅ 实测：selftest: 8/8 通过（8 条规则各改坏一次都能报红）

# ② 行为门禁（起服务后另开终端）
mvn install -DskipTests                  # ✅ 实测：BUILD SUCCESS，四模块全绿；迁移脚本被复制进 classpath
cd blog-application && export SERVER_PORT=18080 && mvn spring-boot:run
# ✅ 实测：8 秒后端口监听成功，Started BlogApplication
cd .. && python api_smoke.py --base http://127.0.0.1:18080
# ✅ 实测：cases = 9  passed = 9  failed = 0  → PASS
python api_smoke.py --selftest           # ✅ 实测：selftest: 9/9（每条断言都对空响应报错，不是恒真门禁）
```

**问题与决策**：

| 问题 | 决策 |
| --- | --- |
| 六个接口用例全返回 500，且日志无异常 | 根因是自建 parent 漏了 `-parameters`（Spring 反射拿不到参数名）→ 父 POM 显式开启并注释来源；同时给兜底异常处理器补 `log.error`——兜底不打日志等于把证据一起吞了 |
| 裸跑 `mvn spring-boot:run` 报「找不到 PostRepository Bean」 | 加 `spring.profiles.default: local`：「不带参数」的语义应当是「本地跑」，不能要求记住 `-Plocal` |
| `mvn -o` 离线构建失败（构件在但缺来源元数据） | 首次构建联网；离线能力留到 CI 镜像预热阶段解决，不在项目期硬凑 |
| 门禁把插件 `<version>` 误判为「子模块自带版本」 | **两边都改**：工程侧把插件版本收进父 POM 的 `pluginManagement`（符合 Maven 纪律），门禁侧把输出细化为区分「依赖版本 / 插件版本」并补一条变异用例 |
| 门禁 OK 的行打印的是失败措辞 | `Result.add` 增加独立的成功/失败措辞——「OK 生产配置缺少占位符」这种输出会让人把通过读成不通过 |

**下一步（第 94 天）**：① 仓储换成真库（JDBC 实现 + `-Pflyway` 装载 `db/mysql/V1__blog_init.sql`，验证真能建出 7 张表）；② 把 `api_smoke.py` 的用例上移成 MockMvc 集成测试，让契约断言进 `mvn test`；③ 实现管理端 `POST /api/v1/admin/posts`，跑通「写 → 渲染 → 读」链路。

## 2026-09-30（第 98 天）：文章写入链路 —— 管理端 CRUD + 发布状态机 + 第三道门禁

:::info 信息
第 94-97 天的「第 1 周收尾」三项中，**管理端写接口**提前到本日落地；「仓储接真库」与「契约测试上移 `mvn test`」仍在待办中，见文末下一步。这样安排的依据是：写接口是第 2 周核心编码的入口，先把「写 → 渲染 → 读」打通，真库接入才有真实的读写路径可换。
:::

**做了什么**：

1. **管理端写接口**（[文章写入链路](../WritePath/index.md)）：`POST /api/v1/admin/posts`（建草稿）、`PUT /{id}`（改标题/slug/归属/正文）、`DELETE /{id}`（软删除）、`POST /{id}/publish`（发布）；契约里声明的 400/404/409 分支**首次有了实现**；
2. **状态只能由动作改变**：`PostUpsert` 入参**没有 `status` 字段**，发布是唯一的"转 PUBLISHED"入口；状态机 `DRAFT → PUBLISHED`，重复发布返回 **409 而不是幂等 200**——假幂等会掩盖调用方手里的过期状态；
3. **软删除语义**：新增内部终态 `DELETED`（**不在对外契约枚举里**），对外一律表现为 404；软删除同时清空 `publishedAt`，让「有人绕过状态判断」也放不出已删文章；
4. **分类与标签字典**：新增 `TaxonomyRepository` + 内存实现，读者端 `GET /api/v1/categories|tags`，后台端 `POST /api/v1/admin/{categories|tags}`；**id → slug 的翻译只发生在数据层一处**（写入用 id、读出用 slug 是契约的刻意设计）；
5. **Markdown 渲染管线**（`MarkdownRenderer`）：**先全量转义、再拼自己产出的标签**；链接只放行 `http/https` 与站内 `/` 路径，`javascript:` 等协议整段降级为纯文本，不做"看起来像但不安全"的降级；
6. **统一响应补 `detail`**：`BizException` 新增 `(ErrorCode, String detail)`，`message` 变成「错误码文案：定位信息」，让后台表单能直接定位到哪一格错了（如 `参数不合法：categoryId 不存在：999999`）；
7. **第三道门禁 `admin_smoke.py`**：37 个顺序步骤覆盖写链路全分支，内置 `--selftest` 变异测试；与只读的 `api_smoke.py` **结构性地分开**（只读脚本因此可以安全指向任何环境）。

**如何验证**：

```shell
cd project/Complete/BlogPlatform/service

# ① 结构门禁
python skeleton_check.py                  # ✅ 实测：checks = 27  failed = 0  → PASS

# ② 先停服务再安装：运行中的 JVM 会锁住本地仓库里的 jar，顺序反了会报 ...tmp -> ....jar
mvn -o install -DskipTests                # ✅ 实测：BUILD SUCCESS，四模块全绿

# ③ 两条运行路径都保留，本日用 local（内存仓储，无数据库）
cd blog-application && SERVER_PORT=18080 mvn -o spring-boot:run
# ✅ 实测：Started BlogApplication in 7.92s，Tomcat 监听 18080

# ④ 行为门禁（另开终端）
cd .. && python api_smoke.py --base http://127.0.0.1:18080
# ✅ 实测：cases = 9  passed = 9  failed = 0  → PASS（只读，不写任何数据）
python admin_smoke.py --base http://127.0.0.1:18080
# ✅ 实测：steps = 37  passed = 37  failed = 0  → PASS
python admin_smoke.py --base http://127.0.0.1:18080
# ✅ 实测：连跑第二遍仍 37/37 —— 不重启服务即可重复执行
python admin_smoke.py --selftest
# ✅ 实测：selftest: 37/37 通过（37 步在空响应下都至少有一条断言报错）
```

**问题与决策**：

| 问题 | 决策 |
| --- | --- |
| 已发布文章改了正文，读者端仍显示旧内容 | `update` 沿用了旧 `contentHtml`。它是 `contentMd` 的**派生物**：已发布时必须重算，草稿保持 `null`（发布时才渲染）。门禁里专门加了「更新后读者端读到新正文」这一步，第二遍跑才暴露 |
| `BizException` 报「需要 ErrorCode / 找到 ErrorCode,String」 | 异常类补 `(ErrorCode, String detail)` 构造器，并把 `detail` 一路带到统一响应——**只回「参数不合法」，后台表单无法自修** |
| 门禁写了「检查 id 是正数」却发现它对空响应也通过 | `--selftest` 当场抓出：该步只读上下文、与 HTTP 响应无关，**永远不可能失败**。改为对响应断言 `field_gt("id", 9000)`（用「> 下界」而非「存在」，因为 `null`/`0` 都能骗过存在性判断） |
| 门禁第一版只能跑一遍 | `total=3` / `list_len(3)` 写死了绝对值，第二遍必然误报。改为「开跑先抓基线、断言 `基线+delta`」 |
| 连跑两遍时 19 步级联失败，报错指向接口 | 真因是 `RUN_TAG` 只精确到秒，同一秒内两遍撞 slug → 创建拿到 409。修法是给 slug 加随机位（`uuid.uuid4().hex[:4]`）；**这类假失败最耗时间，要在数据生成源头消掉** |
| 改了 `blog-data` 但 `spring-boot:run` 跑的是旧 jar | `spring-boot:run` 在子模块目录下只编译该模块，其余从本地仓库取。纪律：**改过 `blog-data`/`blog-web` 必须先回 `service/` 跑一次 `mvn install`** |
| 双脚本重复覆盖同一批断言 | 把 `api_smoke.py` 恢复为纯只读、写链路全部归 `admin_smoke.py`：合成一个文件用 `--readonly` 开关区分，等于把安全边界交给人的记忆 |

**下一步（第 99 天）**：① 仓储接真库（`blog-data` 加 JDBC 实现 + `-Pflyway` 装载 `db/mysql/V1__blog_init.sql`，验证真能建出 7 张表）；② 把 `admin_smoke.py` 的写链路步骤上移成 MockMvc 集成测试，契约断言进 `mvn test`；③ 补契约里已声明但尚未实现的 `401 / 403` 分支（认证与角色）。

:::info 状态回填（第 99 天）
本项 ③ 已完成，落地为 [管理端认证与角色](../AuthRoles/index.md)：令牌签发与校验、PBKDF2 口令哈希、三级角色与默认拒绝的鉴权规则、401 先于 403。①② 仍在待办。
:::

## 2026-10-01（第 99 天）：管理端认证与角色 —— 令牌、口令与默认拒绝

:::info 本日的口径变化：仓库从此只写文档，不写项目代码
从本日起，`project/` **只沉淀文档**：不再提交源码、脚本、SQL 与构建文件（规则见 [AGENTS.md · 第 9 节](../../../../AGENTS.md)）。因此本日的产出是**认证与角色的设计文档**（[管理端认证与角色](../AuthRoles/index.md)），而不是一份可运行的实现。

**诚实说明**：本日的验收清单**未在编写环境实际运行过**——设计定稿时代码草稿尚未完成构建。所以下面的命令是「按该设计实现后应当得到的结果」，不是实测输出；等你按页面实现出来，用 `--selftest` 先证断言能被证伪，再看主流程。
:::

**做了什么**：

1. **令牌格式与校验顺序**（[认证与角色页](../AuthRoles/index.md)）：自签三段式 `header.payload.signature`，HS256（HMAC-SHA256）+ Base64URL 无填充；`exp` 必带；**先验签、再解析 payload、最后判过期**——顺序反了，伪造令牌的 payload 会被当合法数据读出来；
2. **口令存储**：PBKDF2-HMAC-SHA256 十二万次迭代，存储格式 `pbkdf2-sha256$迭代数$盐$摘要`（自描述，将来换算法能识别旧格式），比对用 `MessageDigest.isEqual` 做**恒定时间**比较，避免按字节短路带来的时间侧信道；
3. **三级角色**：`VIEWER(1) < EDITOR(2) < ADMIN(3)`，用数值大小做「至少达到某级别」判断，避免把「文章可写」和「分类可写」写成两套互不相干的判定；
4. **默认拒绝的鉴权规则**：规则表按「方法 + 路径前缀」声明所需角色，**没被规则命中的管理端路径一律按 `VIEWER` 兜底**——新增接口忘记登记时表现为「能读、不能写」，而不是「全放开」；分类与标签的写操作要 `ADMIN`，文章写操作要 `EDITOR`；
5. **401 与 403 的顺序**：无令牌 / 令牌格式错 / 验签失败 / 已过期 → **401**；令牌合法但角色不足 → **403**。反过来先判权限，等于对未认证的人承认「这个路径是存在的」；`OPTIONS` 预检直接放行，否则跨域预检会被 401 挡在门外；
6. **配置在两种 profile 下语义不同**：`prod` 只接受 `password-hash`，出现明文口令直接启动失败（fail-fast）；`local` 允许明文并打印告警、启动时派生哈希，方便本机起服务。`prod` 里所有凭据项保持 `${X}` 占位符、**不允许给默认值**——给了默认值等于把凭据写进了仓库；
7. **契约补齐 401 / 403 分支**：`api/openapi.json` 里管理端各操作补上 `401 未登录` 与 `403 权限不足`，并新增 `/api/v1/admin/auth/login`、`/api/v1/admin/auth/me` 两条路径与 `LoginRequest` / `LoginView` / `MeView` 三个 schema；契约校验器新增「认证链路」一组前缀检查。

**如何验证**（按设计实现后应当得到）：

```shell
cd your-project/service

# ① 先证断言能被证伪（这一步失败，后面全绿也不算数）
python auth_smoke.py --selftest     # 期望：各步断言在空响应 / 错响应下都至少报错一次

# ② 起服务（profile=local，内存仓储）
cd blog-application && SERVER_PORT=18080 mvn spring-boot:run

# ③ 主流程（另开终端）
cd .. && python auth_smoke.py --base http://127.0.0.1:18080
# 期望覆盖：无令牌 401 / 格式错 401 / 验签失败 401 / 已过期 401 / 口令错 401
#          VIEWER 写文章 403 / EDITOR 写文章 200 / EDITOR 改分类 403 / ADMIN 全通
#          GET /auth/me 返回的身份与登录时一致

# ④ 契约仍自洽
python api/contract_check.py        # 期望：路径、$ref、认证链路前缀全部齐全
```

**问题与决策**：

| 问题 | 决策 |
| --- | --- |
| 要不要引第三方 JWT 库？ | **先不引**。当前只需要「签发 / 验签 / 判过期」三件事，用 JDK 自带的 `Mac` 就能做对；引入依赖的代价是版本对齐、CVE 跟进与构建期风险。等到需要 RS256、JWKS 轮转、多受众校验时再换——属于**可逆决策从快** |
| 鉴权规则默认放行还是默认拒绝？ | **默认拒绝**（管理端未命中规则的路径按最低角色处理）。默认放行的失效方式是「新接口忘了登记 = 全开放」，且没人会发现；默认拒绝的失效方式是「新接口没人能写」，会在第一次联调时被发现 |
| 口令明文能不能进配置？ | 只在 `local` 允许，且**启动即告警**；`prod` 见到明文直接启动失败。理由是把「本地方便」和「生产安全」做成同一份配置，最后一定是生产配置里躺着明文 |
| 401 还是 403？ | 认证问题 401、授权问题 403，且**必须先认证后授权**。把两者混用会让排障者分不清「我没登录」还是「我权限不够」 |
| 令牌有效期多长？ | 两小时起步，且不引入 refresh token。个人博客的管理端场景里，长有效期的风险大于频繁登录的成本 |

**下一步（第 100 天）**：① 文章下线动作（`PUBLISHED → OFFLINE → DRAFT` 合法路径与非法路径的 409）；② Markdown 渲染能力补齐（代码块高亮、目录、图片本地化）；③ 把 `auth_smoke.py` 的 401/403 用例上移成 MockMvc 集成测试，让鉴权断言进 `mvn test`。

:::info 状态回填（第 100 天）
本项 ① 已完成，落地为 [文章下线动作](../Lifecycle/index.md)（四态状态机 + 时间戳语义 + `lifecycle_smoke.py` 24 步门禁）。②③ 仍在待办，见下方第 100 天段落的「下一步」。
:::

## 2026-10-02（第 100 天）：文章下线动作 —— 四态状态机与第二道写链路门禁

:::info 本日为文档产出
沿用第 99 天起生效的口径：`project/` **只沉淀文档**，不提交源码与脚本。本页记录的是**设计、迁移矩阵与验收判据**，命令需在你自己的工程里按本页实现后执行。
:::

**做了什么**：

1. **四态状态机**（[文章下线动作](../Lifecycle/index.md)）：在第 98 天 `DRAFT → PUBLISHED` 的单边上，补齐 `OFFLINE`（已下线）与 `DELETED`（软删除终态），把「发布之后又想撤下来」这条高频路径补上——它在第 98 天的设计里没有落点；
2. **两个正交维度**：把「对外可见性」与「生命周期位置」分开。`DRAFT` 与 `OFFLINE` 对外表现相同（匿名 404），差别在于**前者从未发布过、后者曾经发布过**——由此推出「`DRAFT` 不能 `unpublish`」「`OFFLINE` 可以 `revoke` 回草稿」这两条判据；
3. **四个动作的迁移矩阵**：`publish`（DRAFT/OFFLINE → PUBLISHED）、`unpublish`（PUBLISHED → OFFLINE）、`revoke`（OFFLINE → DRAFT）、`delete`（任意非终态 → DELETED）；非法路径一律 **409 + `STATE_CONFLICT`**，并带上「当前状态 → 目标状态」；
4. **`PUBLISHED → DRAFT` 强制两步**（先 `unpublish` 再 `revoke`）：一步到位会抹掉「曾于某时刻对外可见」这段事实，而后台审计需要它；
5. **时间戳语义**：`publishedAt` 在**重新发布时刷新**（读者侧排序与「最近更新」依赖它）、不下线时保留；新增 `offlineAt`，在 `unpublish` 时写入、**`publish` 时必须清空**；
6. **契约补齐**：`api/openapi.json` 新增 `/api/v1/admin/posts/{id}/unpublish` 与 `/revoke` 两条路径、补齐 401/403/404/**409** 分支；并明确 `OFFLINE` / `DELETED` **不进对外枚举**（对外只有 `draft` / `published`），读者端对未发布内容一律 404、不区分原因；
7. **第二道写链路门禁 `lifecycle_smoke.py`（24 步）**：与 `admin_smoke.py` **结构性分开**（写链路冒烟 vs 状态迁移矩阵），并沿用三条纪律——断言相对基线、测试数据带随机位、`--selftest` 用空上下文做变异测试。

**如何验证**：

```shell
cd your-project/service

python lifecycle_smoke.py --selftest        # 期望：24/24（每步在空响应下都至少报错一次）
python skeleton_check.py                    # 期望：checks = 27  failed = 0

# 停服务后再 install（运行中的 JVM 锁着本地仓库的 jar）
mvn -o install -DskipTests                  # 期望：BUILD SUCCESS，四模块全绿
cd blog-application && SERVER_PORT=18080 mvn -o spring-boot:run

# 另开终端：四道门禁
cd .. && python api_smoke.py       --base http://127.0.0.1:18080   # 期望 cases = 9   passed = 9
python admin_smoke.py              --base http://127.0.0.1:18080   # 期望 steps = 37  passed = 37
python lifecycle_smoke.py          --base http://127.0.0.1:18080   # 期望 steps = 24  passed = 24
python lifecycle_smoke.py          --base http://127.0.0.1:18080   # 连跑第二遍仍 24/24（证明断言相对基线）
python api/contract_check.py                                       # 期望：新增路径与 409 分支齐全
```

**问题与决策**：

| 问题 | 决策 |
| --- | --- |
| `PUBLISHED → DRAFT` 一步还是两步？ | **两步**（先下线再撤回）。一步会抹掉「曾对外可见」的事实，审计需要它 |
| 重新发布时 `publishedAt` 刷新还是保留？ | **刷新**。读者侧排序与「最近更新」依赖它；首次发布时刻由 `createdAt` 承担 |
| `OFFLINE` 要不要进对外契约枚举？ | **不进**。进枚举会让「增减内部状态」变成破坏性变更；对外统一只暴露 `draft` / `published` |
| 状态迁移门禁并进 `admin_smoke.py` 吗？ | **不并**。合成一个文件用开关区分，等于把「只读脚本可安全指向任何环境」这条安全边界交给人的记忆 |
| 为什么非法迁移必须在**正确的起点**上测？ | 在 `PUBLISHED` 上测 `unpublish` 会得到 200；只有把用例摆到 `DRAFT` 上，那个 409 才是有效的——**起点错了，409 用例会假通过** |
| `offlineAt` 忘清空会怎样？ | 接口全部 200、状态也对，只有后台列表排序悄悄错。**这是本轮唯一一处「肉眼不可见」的错误**，只能靠门禁断言兜住（第 15 步） |

**下一步（第 101 天）**：① 文章列表的可见性收敛——确认下线后的文章不会因缓存残留继续出现在读者端（缓存失效与状态迁移的先后顺序）；② Markdown 渲染能力补齐（代码块高亮、目录、图片本地化）；③ 把 `lifecycle_smoke.py` 与 `auth_smoke.py` 的用例上移成 MockMvc 集成测试，让状态机与鉴权断言进 `mvn test`。

## 2026-10-02（第 101 天）：Markdown 渲染能力补齐 —— 写时渲染、表格/引用、TOC 与高亮分工

:::info 本日为文档产出
沿用「只沉淀文档」口径。本页记录 [渲染管线补齐](../Rendering/index.md) 的设计决策、用例表与验收判据，代码在你自己的工程里实现后验证。
:::

**做了什么**：

1. **渲染时机收敛为「写时渲染」**：渲染管线挂在状态机 `PUBLISHED` 转移上、与发布同一事务；`contentHtml` + `toc` 随发布落库，读路径只读不渲染，重发布时重渲——渲染结果与发布时刻的渲染器版本绑定，渲染器升级不会悄悄改变已发布文章；
2. **块级解析补齐**：表格（列数不齐**整块降级**为段落，禁止「尽力修复」出坏版式）与引用块（嵌套上限 3 层），单元格内容复用既有 `inline()` 的「先转义后拼标签」顺序，安全模型不变；
3. **TOC 与锚点**：H2/H3 渲染副产品登记为 `toc` JSON 列；`slugify` 保留中文（纯 `a-z0-9` 会把全中文标题变成空 id）、冲突追加 `-2/-3`，纯函数进单测；
4. **代码高亮分工**：服务端只透传语言标记（白名单 `[a-z0-9+#-]`，非法丢弃 class），着色交客户端高亮库——服务端高亮会让 HTML 膨胀 3~5 倍且引入词表依赖；
5. **明确不做归档**：图片上传（需求页非目标）、HTML 混排（与先转义模型冲突）、公式/Mermaid（最小攻击面原则）。

**如何验证**：

```shell
mvn test -Dtest=MarkdownRendererTest     # 期望：合法表格产出 <table>、坏表格整体为段落、
                                         #       重复标题 id="a"/"a-2"、javascript: 降级、<script> 转义

# 链路级断言（你的工程里，沿用 WritePath 页冒烟步骤拿 token、建文、发布）
curl -s $B/api/v1/posts/my-post | python3 -c "
import json,sys; d=json.load(sys.stdin)['data']
assert d['contentHtml'] and '<table>' in d['contentHtml'] and 'id=' in d['contentHtml']
assert d['toc'] and d['toc'][0]['anchor']
print('渲染管线断言全部通过')"
# 追加：连续 GET 两次，响应逐字节一致（读路径零渲染的证据）
```

**问题与决策**：

| 问题 | 决策 |
| --- | --- |
| 渲染在读时还是写时？ | **写时**。读路径成本恒定；代价双倍存储 + 重渲染批任务，均已在设计页归档 |
| 高亮在服务端还是客户端？ | **客户端**。服务端只透传语言标记并白名单校验 |
| 中文标题 slug 怎么生成？ | 保留中文、去标点空白、冲突追加序号 |
| 表格解析失败怎么办？ | **整块降级**。残缺 `<table>` 比纯文本更糟——坏版式没人发现 |

**下一步（第 102 天）**：① 可见性收敛——读者端列表/详情对 DRAFT / OFFLINE / DELETED 一律 404（第 100 天状态机的读侧收口），补第四道门禁 `visibility_smoke`；② 渲染器用例表与可见性用例一起评估上移 `mvn test`（第 101-104 天周收口目标）；③ 之后进入第 3 周评论链路。

本项 ① 已完成，落地为 [可见性收敛](../Visibility/index.md)（404 一致性判据 + 缓存失效时序 + `visibility_smoke` 22 步）；② 已在本日给出统一评估口径（按断言对象分流，见可见性页第三节），余下上移清单见下方第 102 天段落的「下一步」。

## 2026-10-02（第 102 天）：可见性收敛 —— 读者端只看得到 PUBLISHED 与读侧门禁

:::info 本日为文档产出
沿用「只沉淀文档」口径。本页记录 [可见性收敛](../Visibility/index.md) 的设计决策、22 步用例与验收判据，代码在你自己的工程里实现后验证。
:::

**做了什么**：

1. **读侧收口一条规则**：读者端能看到的文章当且仅当 `status = PUBLISHED`——列表过滤条件进 SQL（内存过滤会算错分页 total）、详情非 PUBLISHED 走 404；
2. **404 一致性硬判据**：`DRAFT` / `OFFLINE` / `DELETED` 与不存在的 slug 四种来源的 404 响应**逐字节一致**（统一 `ARTICLE_NOT_FOUND`），存在性不泄漏——否决 403（可枚举探测）与 410（确认曾经存在）；
3. **缓存失效时序**（接第 101 天待办）：`publish` / `unpublish` / `delete` 三动作在**事务提交后**删详情 + 列表缓存，先删后提交存在旧值回填窗口；短 TTL（60s）兜底；管理端直读数据库不走读者缓存；
4. **读侧门禁 `visibility_smoke`（22 步）**：含「unpublish 后立刻连续 GET 两次必须都 404」的缓存收敛用例与「过滤前后 total 差值」的分页语义用例；`--selftest` 变异测试同规交付；
5. **用例上移统一口径**（周收口目标）：断言纯函数与 HTTP 语义的上移 `mvn test`（渲染器、slugify、状态机、401/403、可见性 404），断言跨进程时序与端到端编排的留在 smoke——上移不是消灭冒烟脚本；
6. **勘误**：第 101 天计划把本门禁写作「第四道」，按完整清单（含 `auth_smoke`）实为第五道行为门禁、第一道读侧门禁，以可见性页门禁表为准。

**如何验证**：

```shell
python visibility_smoke.py --selftest                        # 期望：22/22
python visibility_smoke.py --base http://127.0.0.1:18080     # 期望：22/22 通过

# 404 一致性抽检：四个来源逐字节一致
for slug in draft-slug offline-slug deleted-slug never-exist; do
  curl -s -w "%{http_code}\n" http://127.0.0.1:18080/api/v1/posts/$slug -o /tmp/r
done

# 上移后的测试入口（第 103-104 天完成全部清单）
mvn test -Dtest='MarkdownRendererTest,SlugifyTest,PostStatusTest,PostVisibilityTest'
```

**问题与决策**：

| 问题 | 决策 |
| --- | --- |
| 非 PUBLISHED 返回 403 / 410 / 404？ | 404。另两者都向读者确认了存在性 |
| 缓存失效放事务前还是提交后？ | 提交后。先删后提交会被并发读回填旧值 |
| 下线后 `contentHtml` 清不清？ | 不清。重新发布覆盖，保留即保留审计线索 |
| 用例去 `mvn test` 还是留 smoke？ | 按断言对象分流（见可见性页第三节表） |

**下一步（第 103 天）**：① 完成上移清单（渲染器、状态机、契约 401/403 分支 → MockMvc），`mvn test` 全绿后确认第 2 周验收；② 分类/标签的文章计数同步收口（下线文章不计数）；③ 进入第 3 周评论链路。

本项 ① ② 已在本日落地，见下方第 103 天段落；③ 顺延至第 105 天。

## 2026-10-02（第 103 天）：测试分层收口 —— 把用例搬进 `mvn test`

:::info 本日为文档产出
沿用「只沉淀文档」口径。本页记录 [测试分层收口](../TestLayers/index.md) 的分层判据、上移清单与六道门禁顺序，代码在你自己的工程里实现后验证。
:::

**做了什么**：

1. **给分层定一条判据**：**这条断言依赖什么？** 依赖越少就放得越靠上。纯函数（渲染、slugify、状态迁移矩阵）与 HTTP 语义（401 先于 403、方法与状态码、分页边界）上移 `mvn test`；**跨进程时序**（缓存失效窗口、连跑两遍、重启后状态）与**端到端编排**（建文→发布→读到→下线→404）留在 smoke——上移不是消灭冒烟脚本；
2. **上移清单按「风险」而不是按「难度」排**：状态迁移矩阵由 `lifecycle_smoke` 抽检 9 格改为 **`@CsvSource` 穷举 16 格**；`auth_smoke` 里的四类 401 与「VIEWER 403 / EDITOR 200」搬进 `AuthFilterTest`；渲染器边界（转义、表格列数不齐降级、引用块层级）改为参数化用例；分页边界独立成 `PaginationTest`；`slugify` 从覆盖盲区补上；
3. **401 先于 403 必须在快门禁里钉死**：它一旦被改反，攻击者能用 403 与 401 的差别枚举路径存在性——这是安全缺陷，不该等到十秒级的 smoke 才发现，而且很容易被一次「统一异常处理」的重构顺手改坏；
4. **三条纪律原样带进 JUnit**：测试数据带随机位（同秒撞 slug 的坑第 98 天踩过）、断言相对基线（分页断言「差值等于被过滤条数」而不是 `total == 7`）、**断言必须能被证伪**（改坏一格必须报红，否则删掉）；
5. **顺手收口分类与标签计数**（第 102 天待办 ②）：计数口径**仅统计 PUBLISHED**，与读者端列表用同一条件；计数进 SQL 的 `GROUP BY` 而不是内存过滤（内存过滤会把分页 `total` 算错）；**不做冗余计数列**，改为只读时实时统计——冗余列要靠状态迁移维护，漏减一处就永久错；用例落在 MockMvc 层，且必须包含「`unpublish` 后计数减回去」这一条；
6. **六道门禁定序**：按「越靠左越便宜」排为 静态编译 → 单元测试 → 结构 → 契约 → 行为冒烟 → 迁移矩阵；并补一条纪律：**同一断言只在一个门禁里存在**，上移后要删掉 smoke 里的对应抽检，否则两种失败信号指向同一处代码。

**如何验证**：

```shell
# ① 先证门禁能被证伪（这一步失败，后面全绿也不算数）
#    把 PostStatusTest 中 "DRAFT, unpublish, DRAFT, STATE_CONFLICT" 的期望改成 ok
mvn test -Dtest=PostStatusTest
# ✅ 期望：FAIL，且失败信息指向 DRAFT --unpublish--> 那一格（不是整类报错）

# ② 还原后全绿：秒级，不起服务、不连数据库
mvn test
# ✅ 期望：Tests run: NN, Failures: 0, Errors: 0, Skipped: 0 → BUILD SUCCESS

# ③ 第 2 周验收：五道既有门禁仍全绿（先停服务 → 再 install → 后启动）
cd your-project/service && mvn install -DskipTests
cd blog-application && export SERVER_PORT=18080 && mvn spring-boot:run
# 另开终端：
python skeleton_check.py                             # 期望 checks = 27  failed = 0
python api_smoke.py        --base http://127.0.0.1:18080   # 期望 cases = 9   passed = 9
python admin_smoke.py      --base http://127.0.0.1:18080   # 期望 steps = 37  passed = 37
python lifecycle_smoke.py  --base http://127.0.0.1:18080   # 期望 steps = 24  passed = 24
python visibility_smoke.py --base http://127.0.0.1:18080   # 期望 steps = 22  passed = 22
```

**问题与决策**：

| 问题 | 决策 |
| --- | --- |
| 单元测试要不要起真库？ | 不起，用 `local` profile 的内存仓储；真库路径由 flyway 迁移与双方言 parity 门禁覆盖 |
| 要不要引入 Testcontainers？ | 第 4 周部署阶段再评估。现在没有依赖数据库方言的断言，先别为用不到的隔离付启动成本 |
| 时间相关断言怎么做？ | 注入 `Clock`，测试传固定时钟。直接读 `System.currentTimeMillis()` 的代码无法稳定断言「保留 `publishedAt`、清空 `offlineAt`」 |
| 计数用冗余列还是实时统计？ | 实时 `GROUP BY`。冗余列要多一个失效入口，当前数据量下收益不成比例 |
| 上移后 smoke 里的重复用例怎么办？ | **删掉**。同一断言只在那一层存在，否则两边都会漂 |

**下一步（第 104 天）**：① 把契约里 401/403 分支与分页边界**穷举**（本日建了骨架，缺的是分支覆盖），`CategoryCountTest` 扩到标签维度；② 第 2 周完全收口后出「第 2 周验收小结」对照判据逐条勾选；③ 第 105 天进入第 3 周：评论两级嵌套与审核状态，测试策略继续沿用本日的分层判据（评论树构建是纯函数 → 上移 `mvn test`；防刷限流是时序 → 留 smoke）。

**本日落地情况（第 104 天）**：① 契约 401/403 与分页边界的**穷举**顺延至第 105 天（分类与标签的计数口径已在本日收口并扩到标签维度）；② 第 2 周收口以「八项验收判据」形式落地（见下方段落）；③ 与第 105 天评论链路的判据一致。

## 2026-10-02（第 104 天，同日第五轮）：判据收口与分类标签联调 —— 第 2 周收尾

:::info 本日为文档产出
沿用「只沉淀文档」口径。本页记录 [判据收口与分类标签联调](../Consolidation/index.md) 的收口顺序、删除/保留判据清单、单一口径的计数实现与六条两端联调动作，代码在你自己的工程里实现后验证。
:::

**做了什么**：

1. **给第 103 天的上移补上「下线」这一半**：上移是**搬迁不是复制**。收口顺序写成四步——先确认新处全绿 → 只删一组 → **故意把实现改坏验证新处会红**（证明「删掉的不是唯一哨兵」）→ 改回提交。第三步最容易被跳过，也最值钱；
2. **删除/保留判据清单**：五组上移项（渲染器 R1-R8、状态机 S1-S12、契约 A1-A6、可见性 V1-V4、计数 C1-C2）逐项给出 smoke 侧处置；**三类绝对不能删**——跨请求时序（`unpublish` 后连续两次 GET 的缓存收敛）、端到端编排（注册→登录→发文→读者可见）、失败路径编排（注销→失效→列表消失）；
3. **分类与标签从三处口径收成一处**：管理端列表页「全部状态都算」、读者端筛选页「取数组长度」、详情侧栏「另一次查询」，三处分叉导致「同分类管理端 12 篇、读者端 8 篇」。收为服务端 `countPublishedByCategory()`——**只计 PUBLISHED**，`GROUP BY` 一次算全量（避免 N+1），空分类返回 `count = 0` 而非过滤，**隐藏交由各端自行决定**（读者端隐藏避免死链，管理端保留否则没法加文章）；
4. **方法名承载口径**：`countPublishedByCategory` 而不是 `countByCategory`——口径写进名字，下一个人看到「下线后计数掉了」就不会当 bug 去"修"；同理 SQL 里 `p.status = 'PUBLISHED' AND p.deleted = 0` 写死在 JOIN 条件里，不在 Java 层过滤；
5. **六条两端联调动作 L1-L6**：新建草稿（计数不变）→ 发布（+1）→ 下线（-1）→ **恢复并重新发布（+1 不是 +2）** → 删除（不变）→ 空分类（管理端显示 0，读者端不出现）。**L4 是计数器最经典的 bug**，且不会让任何单接口测试失败——只能靠串联用例抓住，所以它必须留在 smoke；
6. **第 7 条验收判据：判据唯一性**：新增 `assertion_audit.py`，给每条判据一个稳定标识（`R/S/A/V/C` + 序号），检查同一标识是否同时出现在 Java 测试方法与 smoke 脚本里，重复即失败。脚本本身也要求可证伪（把 `R5` 写进两层必须报红）；
7. **门禁全景定格为七道**：结构门禁（每次提交）/ `mvn test`（PR 门禁）/ 四道 smoke（部署前）/ 判据唯一性（每次提交），职责互不重叠。

**如何验证**：

```shell
cd your-project/service

mvn test                       # 期望 BUILD SUCCESS；Tests run >= 120, Failures 0（删断言后不得变红）
python assertion_audit.py      # 期望 PASS：每条判据只有一个归属（退出码 0）
python lifecycle_smoke.py --base http://127.0.0.1:18080   # 期望 L4 计数 +1 不 +2
python lifecycle_smoke.py --selftest                       # 期望 24/24（断言可证伪）
python visibility_smoke.py --base http://127.0.0.1:18080   # 期望 22/22

curl -s 'http://127.0.0.1:18080/api/v1/categories?withCount=true'
# 期望：每个分类都带 postCount；新建的空分类返回 0 而非消失
```

**问题与决策**：

| 问题 | 决策 |
| --- | --- |
| smoke 里的旧断言留不留注释？ | 删干净。留注释等于留第二份口径 |
| 计数用 `COUNT` 现算还是冗余字段？ | 现算。当前量级开销可忽略，冗余字段要维护一致性，收益为负 |
| 空分类谁负责隐藏？ | 前端隐藏，服务端返回。服务端过滤会让「分类被删」与「分类为空」表现一致 |
| 标签这种多对多怎么数？ | 同一口径 + `COUNT(DISTINCT post_id)`，漏 `DISTINCT` 会多算 |
| 联调要不要真起两个前端？ | 不需要。`curl` 验服务端出参即可——前端零逻辑正是本日想达到的状态 |
| 判据唯一性只查 `RSAVC` 前缀够吗？ | 够。脚本能抓「重复」，抓不了「漏标」，后者由 code review 兜 |

**下一步（第 105 天）**：进入第 3 周（里程碑：评论、全文搜索、前台 SSR、联调与测试）。第 105 天做**评论链路第一块——两级楼层的建模与写入**：① `comment` 表加 `root_id` 与 `floor`，读者端永远只渲染两层，深层第 N 层挂到第 2 层并标注「回复 @某人」；② 写入三约束——只能评论 `PUBLISHED` 文章、`parent_id` 必须属于同一篇文章、软删除的评论不可再被回复；③ **先定 `comment_smoke.py` 的断言清单**，仍按「语义进 `mvn test`、时序留 smoke」分层——本日刚收口，别在第 3 周又破一次。

**本日落地情况（第 105 天）**：①②③ 全部完成（见下方第 105 天段落）；审核状态（先发后审/先审后发的开关）判断定不在写入侧，顺延到读侧与后台管理一起设计。


## 2026-10-03（第 105 天）：评论链路 —— 两级楼层的建模与写入（第 3 周起点）

:::info 本日为文档产出
沿用「只沉淀文档」口径。本页记录 [评论链路：两级楼层的建模与写入](../Comments/index.md) 的楼层模型、写入三约束、楼层号分配策略与 `comment_smoke` 断言清单，代码在你自己的工程里实现后验证。
:::

**做了什么**：

1. **楼层模型定稿**：物理两级、展示永远两层。楼层根 `parent_id IS NULL` 且 **`root_id = 自身 id`**（`root_id IS NULL` 定义为脏数据信号），楼内回复 `root_id = 楼层根 id`——「取整层」= `WHERE post_id=? AND root_id=?` 一条索引走完，深层回复物理上仍是一层；
2. **楼层号写时分配**：新增 `floor` 列（楼层根才有，回复为 NULL）+ `uk_comments_post_floor` 唯一索引，号源为「文章内最大 floor + 1」（`FOR UPDATE` 锁文章行，冲突重试一次）；**删除不回收楼层号**——「#12 楼」是用户引用锚点，读时 `row_number()` 会随删除漂移；
3. **被回复人冗余**：`reply_to_user_id = 父评论 user_id`，扁平化后的楼内回复靠它渲染「回复 @某人」；
4. **写入三约束**：① 只能评论 PUBLISHED（四来源 404 逐字节一致，复用可见性判据 V1）；② 父评论必须同文章（409 `2003`——契约错误码第一次在写链路之外有真实用例）；③ 已软删评论不可回复（404，与不存在不可区分）；
5. **断言清单先行**：`comment_smoke.py` 24 步先于实现定稿——语义类 T1~T7（树构建纯函数、三约束、floor 单调、500 字边界、401 先于 403）上移 `mvn test`；时序类 S1~S4（缓存可见、删层编排、连跑两遍、5 线程并发抢楼层号）留 smoke；
6. **门禁全景扩到八道**：结构门禁 / `mvn test` / 五道 smoke（api / admin / lifecycle / visibility / **comment**）/ `assertion_audit.py`（`T*/S*` 前缀纳入唯一性核查）；
7. **审核状态顺延**：先发后审 / 先审后发的开关判定不在写入侧，第 106 天与后台管理一起设计。

**如何验证**：

```shell
cd your-project/service
mvn test                            # 期望 BUILD SUCCESS；T1~T7 全绿（CommentTreeTest / CommentWriteTest）
python comment_smoke.py --base http://127.0.0.1:18080   # 期望 steps = 24  passed = 24
python comment_smoke.py --selftest                      # 期望 selftest: 24/24（断言可证伪）
python assertion_audit.py                               # 期望 PASS：T*/S* 各只出现一次

curl -s -o /dev/null -w '%{http_code}\n' -X POST http://127.0.0.1:18080/api/v1/posts/no-such-post/comments -H 'Content-Type: application/json' -d '{"content":"hi"}'
# 期望 404（约束① 的不存在来源）
```

**问题与决策**：

| 问题 | 决策 |
| --- | --- |
| 楼层号写时分配还是读时计算？ | 写时分配。引用稳定性优先于编号连续性 |
| 楼层根的 `root_id` 留 NULL 还是等于自身 id？ | 等于自身 id，NULL 定义为脏数据信号——判据要能一句 SQL 抓住异常 |
| 父评论跨文章 404 还是 409？ | 409。评论存在、只是挂错文章，是调用方状态错乱 |
| 父评论已删除 404 还是 409？ | 404。与不存在不可区分，删除不留存在性痕迹 |
| 深层回复为什么不上三级树？ | 无限嵌套的 UI 与分页是灾难，「回复 @某人」是验证过的产品答案 |
| 并发抢楼层号锁什么？ | 锁文章行，不锁全局序列——不同文章互不影响 |
| 断言为什么先于实现定稿？ | 后补断言会朝着「实现长什么样」写而不是「语义该是什么」 |

**下一步（第 106 天）**：① 评论读侧——楼层 keyset 分页（按 `floor`，禁 offset 深翻页）、楼层内回复全量返回、楼层根被删后的「已删除」占位渲染口径；② 承接第 104 天顺延项：契约 401/403 分支穷举补上评论路径；③ 全文搜索进入议程（MySQL ngram 先行）。

**里程碑对照**：第 3 周（105-111 天）进行中 1/4。


## 2026-10-03（第 106 天，同日第二轮）：评论读侧 —— 楼层分页、占位渲染与契约穷举

:::info 本日为文档产出
沿用「只沉淀文档」口径。本页记录 [评论读侧：楼层分页、占位渲染与契约穷举](../CommentRead/index.md) 的 keyset 分页设计、占位渲染口径与 401/403 分支穷举矩阵，代码在你自己的工程里实现后验证。
:::

**做了什么**：

1. **楼层 keyset 分页定稿**：游标 = 楼层根的 `floor`（第 105 天「写时分配 + 唯一索引 + 删除不回收」的读侧兑现），`WHERE floor > ? ORDER BY floor ASC LIMIT size+1` 探边，取不满则 `nextCursor = null`；`size` 封顶 50；**offset 禁用**（删除导致页内元素重复/漏读 + 深翻页 O(n) 扫描）；
2. **楼内回复全量返回**：不翻页、按 `created_at ASC`（对话顺序），与楼层的时间倒序相反——「楼层找最新、楼内找过程」；超大楼层不做分页防护，用监控阈值（单楼 > 200 告警）发现；
3. **已删楼层根改「占位保留」口径并修订 S2**：原位置渲染「该评论已删除」，不返回内容与作者 id，**楼内回复保留展示**（删除作者的评论 ≠ 删除别人的讨论），占位不可回复；`comment_smoke` 的 S2 由「整层消失」修订为此口径，断言标识不变、清单记 28 步；
4. **审核状态读侧落定**：`review_status`（VISIBLE / PENDING_REVIEW），读者端只渲染 VISIBLE；先发后审/先审后发是后台开关，**读侧只认状态不认开关**——读写两侧解耦；
5. **契约 401/403 分支穷举补齐评论路径（C1~C10）**：判据「401 先判 → 404 管不可达 → 403 管无权限」，删除接口**先 404 后 403**（防「403 先行」变成存在性预言机）；过期令牌一律 401（过期即匿名，不留双解中间态）；
6. **断言清单 v2**：T8（分页切片纯函数 + size 钳制）/ T9（占位渲染纯函数）/ T10（审核状态可见性）上移 `mvn test`（CommentReadTest）；S2 修订、S5（分页遍历到底不重不漏 + 中途删除仍不重不漏）、S6（认证矩阵六分支外部可观测面）留 smoke；`assertion_audit.py` 前缀唯一性核查通过。

**如何验证**：

```shell
cd your-project/service
mvn test                            # 期望 BUILD SUCCESS；T1~T10 全绿（新增 CommentReadTest）
python comment_smoke.py --base http://127.0.0.1:18080   # 期望 steps = 28  passed = 28
python comment_smoke.py --selftest                      # 期望 selftest: 28/28（断言可证伪）
python assertion_audit.py                               # 期望 PASS：T1~T10 / S1~S6 各只出现一次

# keyset 分页手工抽查：nextCursor 严格递增、翻到底 nextCursor = null
curl -s 'http://127.0.0.1:18080/api/v1/posts/hello-world/comments?size=2'
# 401/403 矩阵抽查
curl -s -o /dev/null -w '%{http_code}\n' -X DELETE http://127.0.0.1:18080/api/v1/comments/1
# 期望 401（C6：匿名删除）
```

**问题与决策**：

| 问题 | 决策 |
| --- | --- |
| 游标用 floor 还是 created_at？ | floor。写时分配 + 唯一索引 + 不回收，稳定性在第 105 天已付清 |
| 楼内回复翻不翻页？ | 不翻。回复量级是产品设计约束的事，超大楼层用监控阈值发现 |
| 删除楼层根整层消失还是占位保留？ | 占位保留（修订 S2）。删除不扩散：别人的回复不陪葬 |
| 先 404 还是先 403？ | 先 404。403 先行是存在性预言机 |
| 过期令牌怎么处理？ | 一律 401。过期即匿名，不留「过期但放行」的双解中间态 |
| 审核开关为什么读侧不感知？ | 开关决定写入初值，读侧只认状态——读写解耦 |

**下一步（第 107 天）**：全文搜索（MySQL ngram 全文索引先行：`ngram_token_size`、`FULLTEXT(title, content)`、`MATCH...AGAINST` 出参与相关度排序、空查询 400），ES 作为中文召回不达标时的后备。里程碑对照：第 3 周（105-111 天）进行中 2/4。

## 2026-10-04（第 107 天）：全文搜索 —— MySQL ngram 先行

:::info 本日为文档产出
沿用「只沉淀文档」口径。本页记录 [全文搜索：MySQL ngram 先行](../Search/index.md) 的写入侧时机、两处服务端配置、查询净化与短语匹配、`EXPLAIN` 走索引断言，代码与配置在你自己的工程里落地后验证。
:::

**做了什么**：

1. **`search_text` 与渲染同事务**：复用第 101 天写时渲染机制，发布/编辑/重渲染时一起写；内容取「渲染后纯文本（标题 + 正文）」，**剥离围栏代码块**（大段代码会把相关度拉高）、保留行内代码（`ngram_token_size` 这类术语要能搜）；草稿照写（MySQL 无部分索引），可见性留给查询期 `WHERE status='PUBLISHED'`；
2. **两处服务端配置（都不是代码问题）**：① `ngram_token_size = 2` 是**只读变量**，只能写 `my.cnf` / 启动参数，改后需重启 **且重建 FULLTEXT 索引**；② `innodb_ft_enable_stopword = OFF`——**ngram 剔除的是「包含停用词的词元」**，默认英文停用词表会让 `java` 被切成 `ja`/`av`/`va`（都含 `a`）而整片剔除、搜不到；它是动态变量但**光改不重建索引无效**；
3. **索引「建了不用」的口径变断言**：FULLTEXT 建在 `(title, search_text)`，`MATCH()` 的列集合必须与索引定义逐字一致才能吃掉索引；反例 `MATCH(search_text)` **语法合法、结果看着也对，只是全表扫**——唯一能发现它的是 `EXPLAIN` 的 `key` 列，故写成 Q7 门禁；
4. **查询模式定为布尔模式**：ngram 下 `IN NATURAL LANGUAGE MODE` 是 ngram 词的**并集（OR）**（搜「数据库设计」会命中只含「数据」的文章），`IN BOOLEAN MODE` 是 ngram **短语**匹配（只命中含完整词的文档），后者与「找这个词」的意图一致；代价是必须净化布尔元字符（`+ - * " ( ) ~ @ > <`）+ 最小长度 2（不足 2 字不成 ngram，必然命中 0，直接 400 而不是静默空结果）；
5. **排序与分页**：排序键写全三级 `score DESC, published_at DESC, id DESC`（同分是常态，少一级就会在页边界重复/漏读）；分页**退回 offset**——游标分页要求排序键是稳定列，而 `score` 是随查询串变化的计算值，keyset 无从下手，改用「`size` 封顶 50 + `page×size` 封顶 500」；只返回 `hasMore`、不精算 `total`（精算要给全文索引再跑一次 `COUNT(*)`），`hasMore` 用多取一条探边；
6. **摘要片段为服务端纯函数**：命中处 ±40 字、HTML 转义、命中词包 `<mark>`；无命中取前 80 字（不做「直接截前 80 字」，那样用户看不出为什么命中）；
7. **断言清单 T11~T14 / Q1~Q9**：T11（净化纯函数）/ T12（摘要纯函数）/ T13（三级排序稳定）/ T14（分页边界钳制）上移 `mvn test`（`SearchQueryTest` / `SearchServiceTest`）；Q1~Q9 留在 `search_smoke.py`，其中 **Q7 断言 `EXPLAIN` 的 `key = ft_posts_search`**、**Q9 是停用词回归（搜 `java` 必须命中）**；门禁全集从八道扩到**九道**，`assertion_audit.py` 前缀核查扩展到 `T11~T14` 与 `Q1~Q9`。

**如何验证**：

```shell
# 前提：MySQL 已配好 ngram_token_size=2 与 innodb_ft_enable_stopword=OFF 并重启，且已重建索引
cd your-project/service
mvn test                            # 期望 BUILD SUCCESS；T1~T14 全绿（新增 SearchQueryTest / SearchServiceTest）
python search_smoke.py --base http://127.0.0.1:18080   # 期望 steps = 9  passed = 9
python search_smoke.py --selftest                      # 期望 selftest: 9/9（断言可证伪）
python assertion_audit.py                              # 期望 PASS：T1~T14 / S1~S6 / Q1~Q9 各只出现一次

# 手工抽查
curl -s 'http://127.0.0.1:18080/api/v1/search?q=全文搜索'      # 期望命中标题含该词的文章、首条 score 最高
curl -s -o /dev/null -w '%{http_code}\n' 'http://127.0.0.1:18080/api/v1/search?q='        # 期望 400（空查询）
curl -s -o /dev/null -w '%{http_code}\n' 'http://127.0.0.1:18080/api/v1/search?q=%E6%90%9C' # 期望 400（单字）
curl -s 'http://127.0.0.1:18080/api/v1/search?q=java'          # 期望非空（Q9：停用词表已关）
```

```sql
-- Q7 执行计划：key 必须是 ft_posts_search，为 NULL 则说明 MATCH 列集合与索引定义不一致
EXPLAIN SELECT id FROM posts
 WHERE MATCH(title, search_text) AGAINST('全文搜索' IN BOOLEAN MODE) AND status='PUBLISHED';
```

**问题与决策**：

| 问题 | 决策 |
| --- | --- |
| `search_text` 什么时候生成？ | 与渲染同事务。不留「渲染了但搜不到 / 搜到了但页面没内容」的半边窗口 |
| 围栏代码块进不进索引？ | 不进。大段代码会拉高相关度；行内代码保留 |
| `ngram_token_size` 要不要调？ | 保持默认 2。只读变量、改它要重启 + 重建索引，代价与收益不成比例；真正要改的是停用词表 |
| 为什么必须关停用词表？ | ngram 剔除「**包含**停用词的词元」，默认英文表会让 `java` 整片消失——「搜不到却查不出原因」的典型 |
| 自然语言模式还是布尔模式？ | 布尔模式。NL 在 ngram 下是 OR 并集（噪声大），布尔是短语匹配（与意图一致） |
| 搜索分页为什么能退回 offset？ | 游标分页要稳定排序键，`score` 是计算值——**这里用不了 keyset**，用上限封顶代替；与评论区的 keyset 是两种不同的正确解 |
| 为什么断言 `EXPLAIN` 而不只看结果？ | 「建了不用」两条路都通、无报错，只有执行计划能证明索引在起作用 |
| 单字查询为什么 400 而不是返回空？ | 返回空是静默无结果，用户会以为站内没有；400 让前台能提示「至少输入 2 个字」 |

**下一步（第 108 天）**：前台 SSR——Nuxt 服务端取数与 hydration（`useAsyncData` 与首屏 HTML 一致）、文章列表与详情的 SSR 缓存头、搜索页在服务端渲染时把 Q4 的 400 转成友好提示、SEO 元信息（`title` / `description` / `og:`）由服务端渲进 HTML。判据：查看源代码能看到正文与 TDK；禁用 JavaScript 后页面仍可读。里程碑对照：第 3 周（105-111 天）进行中 3/4。

## 2026-10-04（第 108 天）：前台 SSR —— 服务端取数、hydration 一致与 SEO 元信息

:::info 本日为文档产出
本页记录 [前台 SSR](../FrontendSSR/index.md) 的实现口径：`useAsyncData` 四纪律、软 404 透传、TDK/canonical/og: 由服务端渲进 HTML、SSR 缓存头与失效时序、搜索页 400 转友好提示，代码与配置在你自己的工程里落地后验证。
:::

**做了什么**：

1. **服务端取数四纪律**：key 全局唯一（`post:` + slug）、不传 `server: false`（关掉即退化 CSR、SEO 失效）、结果进 payload（客户端 hydration 不重复请求）、错误用 `createError` 抛真状态码——**软 404 是本日最贵的错误**：后端 404 被前台吞成「漂亮的 404 组件 + 200」，第 102 天的存在性不泄漏就白做了，故 R3 断言打在前台 HTTP 状态码上；
2. **hydration 三条红线**：setup 顶层不碰 `window`/`document`/`localStorage`（放 `onMounted` 或 `<ClientOnly>`）、不用每次都变的值参与渲染（`Date.now()`/`Math.random()`/本地时区——时间在服务端格式化成字符串再下发）、列表 key 与顺序稳定（两端吃同一份 payload）；
3. **SEO 元信息一处写全**：详情页 title=文章标题、description=摘要（**服务端已有纯文本，前台只取不加工**，两端各截一遍必然不一致）、`og:` 全套、canonical=`{SITE_URL}/posts/{slug}`；**搜索页反向操作**——`noindex` 且不设 canonical（同一 URL 对应无限多内容，收录只会稀释权重），但搜索页本体仍要 SSR；
4. **SSR 缓存头与失效**：详情 `public, max-age=60, stale-while-revalidate=300`、列表 30 秒、带 hash 的静态资源 `immutable`、搜索 `no-store`；失效口径与第 102 天同一条原则——版本号（`updated_at`）进后端缓存键、提交后失效、TTL 只兜底，R9 验证「发布新版后下一次请求源码立即更新」；
5. **搜索页服务端渲染**：`q` 缺失或 < 2 字**不发请求**直接渲染「至少输入 2 个字」（HTTP 200）；上游 500 渲染页内错误态而非裸抛（搜索是站内增强功能，5xx 会让爬虫把整站降权）；R5 断言「提示出现在服务端渲染的 HTML 里」，不等客户端 JS 起来；
6. **断言分层**：T15（摘要取值纯函数）/T16（缓存头计算纯函数）上移 `mvn test`；R1~R10 留 `ssr_smoke.py`（要起前台、要 curl 源码），其中 **R1/R2 的判据是「看源码能看到正文与 TDK」而非看开发者工具的 DOM**——后者在任何页面都会显示，没有判别力；门禁从九道扩到**十道**，`assertion_audit.py` 前缀核查扩展到 `R1~R10`。

**如何验证**：

```shell
cd your-project/web
npx nuxt build                                # 期望：构建成功，产物含 SSR 服务端入口（R10）
node .output/server/index.mjs &               # 期望：监听 3000

python ssr_smoke.py --base http://127.0.0.1:3000 --api http://127.0.0.1:18080
# 期望 steps = 10  passed = 10
python ssr_smoke.py --selftest                # 期望 selftest: 10/10（断言可证伪）
python assertion_audit.py                     # 期望 PASS：T1~T16 / S1~S6 / Q1~Q9 / C1~C10 / R1~R10 各只出现一次

# 手工抽查：SEO 的最终判据是看源码
curl -s http://127.0.0.1:3000/posts/hello-world | grep -o '<title>[^<]*</title>'   # 期望文章标题
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3000/posts/draft-slug    # 期望 404（R3）
curl -sI http://127.0.0.1:3000/posts/hello-world | grep -i cache-control           # 期望 max-age=60 前缀（R4）
curl -s 'http://127.0.0.1:3000/search?q=' | grep -c '至少输入 2 个字'               # 期望 ≥ 1（R5）
```

**问题与决策**：

| 问题 | 决策 |
| --- | --- |
| 详情页要不要 SSG？ | 不做。文章随时发布/下线，ISR 失效复杂度大于收益；SSR + 60 秒缓存头已平衡 TTFB 与新鲜度 |
| 软 404 谁负责？ | 前台。后端 404 是对的，前台吞成 200 就错了——断言打在前台状态码上 |
| 搜索出错返回什么？ | 200 + 页内错误态 + `noindex`；不裸抛 5xx（避免整站被降权） |
| mismatch 怎么发现？ | 构建期警告不忽略 + R7「禁 JS 语义」兜底 |
| 缓存失效放哪？ | 版本号在后端缓存键，前台只读响应头——不另起炉灶 |
| description 谁截？ | 服务端（写时渲染产物已是纯文本），前台只取 |

**下一步（第 109 天）**：第 3 周收尾——① 十道门禁全绿并记录实测输出；② 跨链路一条龙回归（发布 → 进列表 → 被搜到 → 可评论 → SSR 源码同步）；③ 第 1 周遗留的 Docker 验证 DDL 补跑（部署周前最后窗口）。里程碑对照：第 3 周（105-111 天）4/4。

## 2026-10-05（第 109 天）：读者账号与权限 —— 给评论链路补上它一直假定的那个身份

:::info 本日为文档产出
本页记录 [读者账号与权限](../ReaderAccount/index.md) 六页的设计与实施口径：账号生命周期、`users` 扩列与 `user_tokens`、令牌轮换与复用检测、数据归属矩阵、SSR 下的登录态与缓存切分。代码、DDL 与冒烟脚本都在你自己的工程里落地后再验证。
:::

**为什么是这一天做这件事**：第 99 天只做了**管理端**认证（配置驱动的后台账号），而[评论链路](../Comments/index.md)的断言 `T7` 早就写着「匿名发评论 `401` 先于 `403`」，`comments.user_id` 与 `reply_to_user_id` 也早在第 1 周就是 `NOT NULL` 与强引用。也就是说：**结构上一直假定读者有账号，只是没人把它建出来**——第 105~108 天的评论测试用的那个「登录读者」在此之前只存在于测试脚本的假设里。

**做了什么**：

1. **账号生命周期定稿（五状态六迁移）**：`PENDING` / `ACTIVE` / `FROZEN` / `CLOSED`；`PENDING` **能登录但不能写**（否则用户没法在登录态下点「重发验证邮件」，链路会断在一个自相矛盾的设计上）；`FROZEN` 只能管理员解冻（自助解冻等于把封禁变成一次口令重置）；`CLOSED` 是终态，登录 `401` 且与「用户名不存在」逐字节一致；
2. **`users` 扩列 + `user_tokens` 新表**：增量脚本 `V2__reader_account.sql` 给 `users` 补 6 列（`email` / `admin_role` / `status` / `email_verified_at` / `last_login_at` / `closed_at`）、新增第 7 张业务表 `user_tokens`（刷新令牌，**只存 SHA-256 哈希**、`family_id` 支持整族撤销、`replaced_by` 区分「用错」与「用旧」）。**迁移顺序写死在页面上**：`ADD COLUMN ... DEFAULT` 会把存量行一并写成默认值，所以必须「按存量语义加列 → 回填 → 再改默认值」三步走，否则第 99 天建的、本来正常的管理端账号会全部变成「待验证」；
3. **令牌设计：access 不落库、refresh 必须落库**。access 15 分钟靠 HS256 验签换取零 IO；refresh 30 天需要「能反悔」——登出、改密、冻结、泄漏检测四件事都要求它**能即时作废**，这正是无状态令牌做不到的。刷新走**轮换 + 复用检测**（RFC 9700 的口径）：一个 refresh 只能换一次，旧票再次出现即判定该族泄漏，**整族撤销**，且命中后仍返回普通 `401`（不告诉攻击者「你被发现了」）；
4. **数据归属（本日真正的技术内容）**：把「不存在性不泄漏」从**文章**推广到**账号**——登录失败、账号已注销、账号不存在三种情形响应逐字节一致（错误码 `3001` 四合一，精确原因只写审计日志）；同时定死**归属判据在服务端**：`comments.user_id == token.sub`，前端隐藏按钮只是体验。越权矩阵 6 类动作 × 3 种身份 = 18 格，每格唯一期望，**全部用 `curl` 打、不走前端**；
5. **SSR 下的登录态与缓存切分**：令牌放 **httpOnly Cookie**（前台是 SSR，服务端拿不到 `localStorage`，否则首屏只能渲染成未登录），`refresh_token` 的 `Path` 收窄到只剩刷新接口一条；公共页的**身份片段不进 SSR 输出**（顶栏与评论框走客户端渲染），因此文章页的 `public, max-age=60, stale-while-revalidate=300` **口径不变**，而 `/me` 与 `/me/comments` 一律 `private, no-store`——**两个身份进同一个缓存键就是串号事故**；
6. **断言分层与门禁扩到第十一道**：`A1~A10` 语义类上移 `mvn test`（哈希自描述与升级、口令上限、注册唯一性、口令强度、登录失败不可区分、状态门禁、轮换、复用检测、归属矩阵、`aud` 边界）；`B1~B6` 时序类留 `account_smoke.py`（22 步：端到端编排、登出即失效、并发刷新恰好一成一败、改密影响面、频控窗口、两账号不串号 + 连跑两遍幂等）。同时把项目总览里「十道门禁」这处**数字与列表对不上**的口径定格成十一道的完整清单；
7. **三处悬空口径收敛**（都是文档与实现各说各话、不会报错但会误导下一个人）：① `password_hash` 列注释「BCrypt 哈希」与实际的自描述 PBKDF2 串不符，列宽 100 → 120，并把迭代参数从 `120_000` 对齐到 OWASP 现行基线 **`600_000`**（PBKDF2-HMAC-SHA256）；② 业务身份 `READER`/`AUTHOR` 收进 `role`、运维角色收进 `admin_role`（`NULL` = 无后台权限，与第 99 天「默认拒绝」的兜底方向一致）；③ 管理端账号来源由配置文件收敛进 `users` 表，配置只保留**引导用的首个 ADMIN**，且该通道在「表里已有管理员」时**自动跳过**；
8. **一处顺带修的旧账**：`Requirements` 页早期写的接口路径是 `/api/admin/posts` 形态，第 92 天的契约早已统一为 `/api/v1/...`，本日把该页全部路径改正。

**如何验证**：

```shell
cd your-project/service

# ① 先证断言可被证伪（不报红 = 断言恒真，后面全绿无意义）
python account_smoke.py --selftest                    # 期望 selftest: 22/22 通过

# ② A1~A10 随单元测试跑：秒级，不起服务、不连数据库
mvn test                                              # 期望 BUILD SUCCESS
python assertion_audit.py                             # 期望 PASS：A*/B* 各只出现一次

# ③ 增量 DDL（连续执行，结掉第 1 周的 Docker 欠账）
docker run --rm -i mysql:8.4 mysql -uroot -proot -e "
  CREATE DATABASE IF NOT EXISTS blog DEFAULT CHARSET utf8mb4;
  USE blog; SOURCE /dev/stdin;" < db/mysql/V1__blog_init.sql
docker run --rm -i mysql:8.4 mysql -uroot -proot blog -e "SOURCE /dev/stdin" \
  < db/mysql/V2__reader_account.sql
# 期望：两条都无报错；此后 SHOW TABLES 列出 8 张表
python api/parity_check.py                            # 期望 PASS

# ④ 主流程与越权矩阵（另开终端）
export SERVER_PORT=18080 && cd blog-application && mvn spring-boot:run
cd .. && python account_smoke.py --base http://127.0.0.1:18080
# 期望 steps = 22  passed = 22

# ⑤ 手工抽查：枚举防护与 aud 边界
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:18080/api/v1/admin/posts \
  -H "Authorization: Bearer $READER_TOKEN"            # 期望 401（不是 403）
curl -sI http://127.0.0.1:3000/posts/hello-world | grep -i cache-control
# 期望 public, max-age=60, stale-while-revalidate=300（公共页口径不变）
```

**问题与决策**：

| 问题 | 决策 |
| --- | --- |
| 读者与管理端账号存不存一张表 | **一张表，两个角色列**（`role` / `admin_role`）。拆两张表会让「同一个人既是作者又是编辑」变成两行，账号治理立刻分叉 |
| 注册接口要不要告诉你邮箱已被占用 | **不告诉，一律 `202`**（邮箱是找回口令的凭据，泄漏面比用户名大）；用户名是公开标识，占用就 `409`。代价是「其实注册过却忘了」的用户会被卡住，因此必须配「文案与成功时一致 + 重发入口同样 `202` + 审计计数」三件补偿 |
| 「我的评论」是权限还是过滤 | **过滤**。它不是「能不能看」而是「看哪些」，判据是内容（每条 `userId == token.sub`）而非状态码；**写操作才是权限** |
| 注销是删行还是置状态位 | **置状态位 + 打散用户名与邮箱**。`users` 第 1 周已定「不删行」，而 `posts.author_id`、`comments.user_id`、`comments.reply_to_user_id` 三处都是强引用 |
| 注销后原用户名可否被别人注册 | **不允许**，进保留名单——允许复用会让新的「张三」继承旧张三的历史评论，等于身份混淆；邮箱则允许复用（私有凭据，锁住等于永久占用） |
| 复用检测命中后返回什么 | 普通 `401`。回「检测到令牌复用」等于通知攻击者，而正确处置是让他继续以为一切正常、同时整族已被作废——**检测的价值在争取时间，不在通知对方** |
| 读者令牌打管理端返回 `401` 还是 `403` | **`401`**。令牌里带 `aud=reader\|admin`，拿错门票属于「身份未被证实」；判成 `403` 等于承认该身份在这个入口有效 |
| 身份片段要不要进 SSR 输出 | **不进**。否则公共页要么失去 CDN 缓存、要么加 `Vary: Cookie` 并把命中率打崩，且任一层 CDN 忽略 `Vary` 就会把 A 的页面发给 B |
| CSRF 要不要上双提交 token | 本模块**不做**，前提是「所有写操作都是 `POST` 且 `SameSite=Lax`」；三条前提（跨站携带凭据 / `GET` 触发副作用 / `SameSite=None`）写在页面上，任一出现就必须回来补 |

**下一步（第 110 天）**：① **核心业务流收口**——把「发文 → 发布 → 被搜到 → 被评论 → 作者可见反馈」串成一条端到端链路，读者账号就是这条链路的身份主语；② 第 3 周收尾剩余：一条龙回归报告落档、Docker 验证 DDL 的实测输出回填（三段清单与命令已在本日[验收页](../ReaderAccount/Acceptance/index.md)定稿）；③ 已知顺延项登记在案：**压测**按轮换表第 119 行与联调合并，不提前压——没有稳定部署形态时压出来的数字既不可比也不可复用。里程碑对照：第 3 周（105-111 天）第 4/4 步，收尾待回填。

## 2026-10-05（第 110 天）：核心业务流收口 —— 一条链路串起全部模块（第 3 周收尾）

:::info 本日为文档产出
本页记录 [核心业务流收口](../CoreFlow/index.md) 七页（章节入口 + 领域建模 + 状态机驱动 + 接口联调 + 端到端走查 + 一条龙回归 + 第 3 周验收结论）：三个聚合、转移 × 副作用矩阵、字段依赖清单 D1~D10、五段时序与一条龙回归 CF1~CF14。实现与脚本都在你自己的工程里落地后再验证。
:::

**为什么是这一天做这件事**：第 98~109 天的十二个章节全是**模块级**验收——`admin_smoke` 证明写链路对、`search_smoke` 证明搜索对、`account_smoke` 证明账号对，但**模块级全绿推不出链路级正确**。链路上真正的风险全在接缝：缓存回填窗口（第 102 天第 ⑤ 步只能守一段）、渲染与 `search_text` 的同事务半边（第 107 天口径没有链路级断言）、「读者发评论 → 作者看得到」这条反馈回路**从始至终没有一道门禁**（两个「读侧」各测各的，谁都覆盖不了对方）。

**做了什么**：

1. **领域建模收口（三个聚合）**：Post（内容 + 三个渲染产物同生共死）、Comment（两级楼层 + 只评已发布 + 楼层不回收）、User（行只增不删 + 族内单活跃）三个聚合与各自的不变量表；事务边界按「谁的不变量被破坏」划——发布只动 Post 聚合内三列、注销**什么都不做**（不做昵称快照让「已注销用户」显示零代码跨聚合）；通用语言表把 `PUBLISHED`、楼层、占位保留、登录族等术语钉死唯一出处（与 `assertion_audit` 的判据唯一性是同一原则的两个层面）；
2. **转移 × 副作用矩阵（本日最有复用价值的一张表）**：四个动作各自牵动的「同事务 / 提交后 / 读者端效果」三列收拢成一张矩阵，其中最反直觉的一格是 `publish` **没有「写入搜索索引」副作用**——ngram FULLTEXT 就建在 `posts` 表上、`search_text` 与渲染同事务，发布后天然可搜；这格同时是将来升 ES 时的**检查单入口**（升级即把它换成「提交后同步 + 对账 + 下线删文档」三件套）；「要不要领域事件」的决策写死：单体阶段不引入，按格判断哪条副作用装不下事务再挪；
3. **接口联调：字段依赖清单 D1~D10**：把「A 的响应字段喂 B 的请求」显式成清单（`slug` → 前台 URL、`contentHtml` → v-html 信任边界、Cookie access → 评论接口、`authorName` 实时联表、`me/comments.postSlug` → 跳回原文、管理端评论列表 → 反馈回路）；漂移分三类各有抓手——结构漂移归 `contract_check`、语义漂移归 smoke 字段断言、时序漂移归跨进程 smoke（并写明**语义漂移是唯一没有编译器帮忙的一类**，这正是断言要打到字段值的原因）；
4. **端到端五段时序走查**：发文与发布 → 可见与可搜 → 读者身份 → 被评论 → 反馈回路，每段标注身份、入口、动作、出口与守门禁；重点盯三个接缝（缓存回填窗口、同事务半边、SSR 身份片段），并给走查纪律：**读者段全部用无痕窗口或 curl**——同浏览器登着后台测前台是全链路走查最常见的假绿来源；
5. **一条龙回归定稿（`coreflow_smoke.py`，CF1~CF14）**：把第 109 天的 9 步读者轨迹扩展为覆盖五段 + 三接缝的 14 步（新增 CF10 反馈回路可见、CF11 下线后双 GET 404、CF12 重新发布恢复命中、CF14 traceId 串链）；`CF` 前缀登记进 `assertion_audit` 唯一性核查；回归报告固定五节（环境与版本 / 门禁矩阵输出 / 步骤表 / DDL 回填 / 结论与遗留），**实测列纪律**：只填真跑出来的输出，无 Docker 就写「未跑 + 原因」，禁止把期望抄进实测；
6. **第 3 周验收结论（全项目维度）**：里程碑七项对照（六项判据齐备、压测明确顺延第 119 天）；风险与顺延登记表 7 项（压测、邮件发送 = 上线阻塞项、DDL 欠账、ES 路径、MFA/第三方登录、邮箱枚举、监控起点）逐项写去向；第 4 周交接三件事（一键部署——**ngram 两项配置必须进镜像**、监控接入、上线清单合并收敛）。门禁全景**十一道 → 十二道**（`coreflow_smoke` 为第十二道）。

**如何验证**：

```shell
cd your-project/service

# ① 先证断言可被证伪
python coreflow_smoke.py --selftest          # 期望 selftest: 14/14 通过

# ② 判据唯一性（CF 前缀加入后）
python assertion_audit.py                    # 期望 PASS

# ③ 起服务后跑一条龙（另开终端）
export SERVER_PORT=18080 && cd blog-application && mvn spring-boot:run
cd .. && python coreflow_smoke.py --base http://127.0.0.1:18080
# 期望 steps = 14  passed = 14；连跑第二遍仍 14/14（相对基线 + 随机位纪律）

# ④ 手工抽查：反馈回路（单段门禁测不到的那条）
# 以读者身份发一条评论后，用管理端令牌拉后台评论列表
curl -s http://127.0.0.1:18080/api/v1/admin/comments \
  -H "Authorization: Bearer $ADMIN_TOKEN" | grep -c "$READER_COMMENT_ID"
# 期望：1（CF10 的手工复现）
```

**问题与决策**：

| 问题 | 决策 |
| --- | --- |
| 聚合间要不要领域事件 | 单体阶段**不引入**。同事务直调 + 提交后钩子，副作用清单集中在一处、`lifecycle_smoke` 逐格可断言；事件的前提（多团队 / 多部署单元 / 某条副作用装不下事务）按格判断，不按系统一刀切 |
| `publish` 的副作用里为什么没有「写搜索索引」 | FULLTEXT 建在 `posts` 表上、`search_text` 同事务写入，**没有第二个事实来源**；升 ES 时这格换成「提交后同步 + 对账 + 下线删文档」三件套 |
| 注销要不要级联处理文章与评论 | **什么都不做**。显示名实时联表，`CLOSED` 自然显示「已注销用户」；大事务 + 快照列是反面教材（破坏占位保留承诺、让 Post 聚合理解「注销」） |
| CF10（读者评论作者可见）归哪道门禁 | **只能归一条龙**。它横跨读者写与管理端读，塞进 `comment_smoke` 会让评论门禁依赖管理端登录态，破坏「一段一门禁」 |
| 回归报告实测列怎么填 | **只填真跑出来的输出**；跑不了写「未跑 + 原因」。把期望抄进实测 = 伪造记录，比不做更糟 |
| 压测放第 3 周还是第 119 天 | **第 119 天**（与联调合并成「压 → 定位 → 优化 → 复压」闭环）。结论页 / 第 109 天验收页 / 本页**三处口径一致**，顺延不靠「反正以后会做」 |
| 走查用什么身份打读者段 | 无痕窗口或 curl。同浏览器登着后台测前台，Cookie 同源共享，测的根本不是游客视角 |

**下一步（第 111 天）**：① 第 3 周正式收口——按 [Regression 页](../CoreFlow/Regression/index.md)五节结构把一条龙回归报告落档：十一道既有门禁 + `coreflow_smoke` 的实测输出、Docker 验证 DDL 的实测回填（`SHOW TABLES = 8`、`parity_check` PASS），**跑不了的项写明原因保持 ⏳**；② 进入第 4 周准备：一键部署的 Compose 设计（四服务 + `my.cnf` 挂载，ngram 配置进镜像）、监控指标口径（traceId 已串链，补 QPS / P95 / 缓存命中率）、上线清单合并（账号十项 + 全项目风险表 7 项收敛为一张）；③ 里程碑对照：第 3 周（105-111 天）**收尾完成**，第 4 周（112-120 天）从部署起步。

## 2026-10-05（第 111 天）：第 3 周正式收口 —— 回归报告回填清单定稿与欠账显式处置

:::info 本日为文档产出
本日不新增门禁与代码口径，产出为[第 3 周收口页](../Week3Close/index.md)：收口原则、回归报告实测回填四步清单、两项欠账的显式处置决定与第 4 周交接。
:::

**做了什么**：

1. **回归报告实测回填收敛为四步**：启动依赖 → 逐项跑十二道门禁 → 实测列只填真跑输出 → 四条合格判据自检；每条命令与[项目总览](../index.md)的期望值逐一对齐（`checks = 27` / `steps = 14` 等数字两处一致）。
2. **Docker DDL 欠账（第 1 周遗留）显式处置**：按「实测列纪律」如实记录「未跑 + 原因」（文档侧无读者工程运行环境，且该验证依赖第 4 周部署形态才有意义）；判据不变，作为**第 112 天 Compose 首验的第一个动作**执行。判据定稿不等于实测完成，该项保持 ⏳。
3. **压测顺延口径收口**：与轮换表 119 行、[验收结论](../CoreFlow/Acceptance/index.md)三处一致——压测依赖稳定部署形态，顺延第 119 天合并成闭环。
4. **第 4 周交接**：一键部署（ngram 两配置进镜像为红线，`search_smoke` Q9 为部署后首验）、监控接入（CF14 traceId 串链之上补指标与告警）、上线验收清单（从零复现为出口判据）。

**如何验证**：

- 全项目搜索「⏳」：每处待办可追溯到归属周与判据入口，无悬空项。
- 回归报告四步清单与总览页命令、期望值两处一致。

**下一步**：第 112 天进入第 4 周——Compose 四服务搭建 + `my.cnf` 挂载，完成后第一个动作执行 V1+V2 DDL 实测并回填回归报告第二节。

## 2026-10-05（第 112 天）：一键部署 —— Compose 五服务与首次 DDL 实测（第 4 周起点）

:::info 本日为文档产出
产出为[一键部署](../Deployment/index.md)页 + 部署配置约定（Compose 结构、`.env` 矩阵、`my.cnf` 挂载）。**本日不新增业务代码、不新增门禁**——门禁数量仍是十二道，本日做的是给它们换一个**稳定部署形态**，并兑现第 3 周登记的欠账 1。
:::

**做了什么**：

1. **五个角色定形**：`nginx`（唯一对外端口）、`blog-web`（前台 SSR，3000）、`blog-server`（18080）、`mysql`（8.4，带卷）、`redis`（7，带卷）。除 nginx 外全部只在内网可达。
2. **启动顺序靠健康检查**：MySQL 与 Redis 用 `healthcheck` + `depends_on: condition: service_healthy`，后端等数据库真的能连上再起。**上一版 `depends_on: [mysql]` 的写法会留下「首次启动必失败」的窗口**，本日改掉。
3. **`my.cnf` 挂载（红线）**：`ngram_token_size = 2` 与 `innodb_ft_enable_stopword = OFF` 随容器启动生效，并顺带把字符集钉成 `utf8mb4`。漏配的后果是**搜索接口不报错、只是永远搜不到中文词**，所以把 `search_smoke` 的 Q9 定为部署后的第一道验证。
4. **依赖注入矩阵**：一份 `.env` 是唯一事实来源，必填四项（库口令、库名、应用账号、令牌密钥）不给默认值；服务里一律用 `${VAR}` 引用，不在多个 `environment` 块里重复写。
5. **首次部署六步闭环**：准备环境 → 起依赖 → 跑迁移 → 起服务 → 冒烟验收 → 记录版本与回滚演练，每一步都配命令与期望输出。
6. **欠账 1 结清口径**：V1 + V2 连跑 + `tables_ = 8` + `parity_check` PASS 的判据不变，**实测列按真实输出回填**，不在文档里预先填好。

**如何验证**：

```shell
# ① 配置自检：有未定义变量会在这里报错
cd deploy && docker compose config >/dev/null

# ② 依赖先起，等 healthy（MySQL 首启要几十秒）
docker compose up -d mysql redis
docker compose ps --format 'table {{.Service}}\t{{.Status}}'
# 期望：两行都出现 (healthy)

# ③ 迁移连跑 + 表数量核对（欠账 1 的实测动作）
docker compose exec -T mysql mysql -uroot -p"$DB_ROOT_PASSWORD" "$DB_NAME" < ../blog-server/db/migration/V1__init.sql
docker compose exec -T mysql mysql -uroot -p"$DB_ROOT_PASSWORD" "$DB_NAME" < ../blog-server/db/migration/V2__reader_account.sql
docker compose exec -T mysql mysql -uroot -p"$DB_ROOT_PASSWORD" "$DB_NAME" \
  -e "SELECT COUNT(*) AS tables_ FROM information_schema.tables WHERE table_schema='$DB_NAME' AND table_type='BASE TABLE';"
# 期望：tables_ = 8

# ④ ngram 两项看运行时实际生效值（不看配置文件）
docker compose exec mysql mysql -uroot -p"$DB_ROOT_PASSWORD" -e "
  SHOW VARIABLES LIKE 'ngram_token_size';
  SHOW VARIABLES LIKE 'innodb_ft_enable_stopword';"
# 期望：2 / OFF

# ⑤ 起业务服务并对外验收
docker compose up -d blog-server blog-web nginx
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1/api/v1/posts    # 期望 200
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1/               # 期望 200

# ⑥ 部署后第一道专项验证 + 十二道门禁（把输出原样贴进回归报告实测列）
python search_smoke.py --base http://127.0.0.1    # 期望 steps = 9 passed = 9（Q9 中文词元）
python skeleton_check.py --base http://127.0.0.1  # 期望 checks = 27 failed = 0
python coreflow_smoke.py --base http://127.0.0.1  # 期望 steps = 14 passed = 14
```

**问题与决策**：

| 问题 | 决策 |
| --- | --- |
| 迁移脚本自动跑还是手工跑 | **手工跑**。自动迁移在多副本编排下有竞态；单副本阶段手工执行更可控、可回滚 |
| 前台与后端合不合一个镜像 | **不合成**。Node 产物与 JVM 产物构建目标不同，合成后体积翻倍且缓存互相干扰 |
| 数据库端口要不要对外 | **不暴露**。调试走 `docker compose exec`，长期暴露 3306 是常见事故入口 |
| `my.cnf` 挂载还是写进自定义镜像 | **本阶段挂载**。可审计、改配置不重建镜像；「配置即代码进镜像」留到需要分发镜像时 |
| 健康检查为什么给 40 秒 `start_period` | MySQL 首次初始化数据目录很慢；`start_period` 内的失败不计入 `retries`，避免提前判死 |
| 前端 SSR 的 `PUBLIC_BASE_URL` 从哪来 | 从 `.env` 注入，不写死——同一份镜像要能跑在 localhost 与正式域名上 |

**下一步**：第 113 天做第 4 周第二件事——**监控接入**。CF14 已断言 `traceId` 能串起一条链路，在其之上补三项指标口径（QPS / P95 延迟 / 缓存命中率）与告警阈值，并明确「谁来看、什么时候看」。压测仍顺延第 119 天，归属口径与[第 3 周收口页](../Week3Close/index.md)、[验收结论](../CoreFlow/Acceptance/index.md)三处一致。

## 2026-10-05（第 113 天）：监控接入 —— 指标口径、告警阈值与 traceId 串链（第 4 周第二步）

> 第 112 天「下一步」声明的监控接入已在本日落地：[监控接入](../Monitoring/index.md)。

**当日做了什么**：

1. **三层信号落点定稿**：指标走 Micrometer → Prometheus 拉取（Boot Actuator 内建，零自建采集器）；日志走结构化 + `traceId` 字段、`docker logs` 可 grep；**链路追踪系统刻意不做**，升级时机（拆出第二个服务时）写进决策表。
2. **六项指标口径**：QPS、P95/P99、错误率、缓存命中率、DB 连接池 pending、JVM（只观察不告警）——每项写明 Micrometer 指标名与聚合维度；三条标签纪律（`uri` 用路由模板、缓存名有限集合、401/403/404 不计错误率）。
3. **阈值 = 基线推导**：起点值表（P95 > 基线 × 3、错误率 > 1%、命中率 < 60% 等）+ 影子期测基线的流程；「谁来看」与「每条告警必须带两条处置入口」写进页面。
4. **traceId 串链三条判据**：透传（含响应头）、落日志、可验证——用 CF14 的走查方式任取一条请求三段日志各能 grep 到。
5. **最小面板**：Grafana 六格，每格一条 PromQL。
6. **决策表六行**：拉 vs 推、Compose 可选 profile、不上 ELK、追踪升级时机、401 不计错误率、JVM 不设阈值。

**验证判据**（文档产出，验收是判据不是实测）：指标可拉（`/actuator/prometheus` 含 `http_server_requests` 行）、口径正确（连续请求后 QPS 与命中率有对应变化）、告警链路实测触达一次、traceId 三段日志闭环；**监控检查定位为部署验收项，不新增行为门禁**——十二道门禁数量与职责不变。

**下一步**：第 114 天做**备份恢复演练**（`mysqldump` 全量 + binlog 增量恢复到指定时间点，恢复目标用临时容器）与上线验收清单定稿；第 4 周收口与[一键部署](../Deployment/index.md)判据合并。压测仍顺延第 119 天。

## 2026-10-06（第 114 天）：备份恢复演练 —— 临时容器恢复四步、R1~R6 对账判据与上线验收清单定稿（第 4 周第三步）

> 第 113 天「下一步」声明的备份恢复演练已在本日落地：[备份恢复演练与上线验收清单](../BackupDrill/index.md)。

**当日做了什么**：

1. **备份策略定稿**：每日 `mysqldump --single-transaction` 全量 + binlog 持续留存（MySQL 8.4 默认开启），各保留 7 天；备份目录独立于 `mysql-data` 卷（数据卷损坏不连带备份）。
2. **恢复演练四步**：造场景（记录删除前计数 → 删一篇文章 → 记录时间点）→ 临时容器恢复全量（同款 `my.cnf`，ngram 一致性为红线）→ `mysqlbinlog --stop-datetime` 重放至目标时间点 → 对账。
3. **R1~R6 对账判据**：表数 8 / 文章数回删除前 / 被删文章回归 / 读者表一致 / 字符集一致 / 恢复耗时留实测值。
4. **三条红线**：恢复只在临时容器做、备份与数据卷分卷、`my.cnf` 不得漂移。
5. **上线验收清单九项合并定稿**：一键部署（1~3）+ 监控接入（4~6）+ 备份演练（7~8）+ 从零复现（9），每项标注出处页面——清单只做合并，不新增判据。

**验证判据**（文档产出，验收是判据不是实测）：R1~R6 逐条给出实测输出形态、演练全程耗时记录、临时容器清理后 `docker ps -a | grep mysql-restore` 为空；恢复演练属部署验收项，不新增行为门禁——十二道门禁数量与职责不变。

**下一步**：第 115 天做**第 4 周收口**——对照[上线验收清单](../BackupDrill/index.md)九项逐条实测回填（实测列纪律与回归报告一致：只填真跑出来的输出），第 4 周里程碑四项对照定稿。压测仍顺延第 119 天，归属口径三处不变（[第 3 周收口](../Week3Close/index.md) / [验收结论](../CoreFlow/Acceptance/index.md) / 本页）。

## 2026-10-06（第 115 天）：第 4 周收口 —— 上线验收清单九项实测回填与里程碑对照定稿

> 第 114 天「下一步」声明的第 4 周收口已在本日落地：[第 4 周收口](../Week4Close/index.md)。

**当日做了什么**：

1. **九项验收清单逐条回填**：每项标注判据出处（部署 1~3 / 监控 4~6 / 备份 7~8 / 从零复现 9）与实测状态——按实测列纪律，本机无 Docker 环境，九项全部标 **⏳ 未跑 + 原因**，不把期望值抄进实测列。
2. **欠账收敛**：九项 ⏳ 归并为单一前置条件（一台有 Docker 的机器），兑现路径写成[一键部署](../Deployment/index.md)首次部署六步之后的六步回填清单（含告警触达、恢复演练、从零复现）。
3. **第 4 周里程碑对照定稿**：一键部署 / 监控接入 / 备份演练（三项均为「判据定稿」）/ 第 4 周收口（本页）。
4. **口径不变**：压测仍顺延第 119 天，三处口径（[第 3 周收口](../Week3Close/index.md) / [验收结论](../CoreFlow/Acceptance/index.md) / 项目总览）一致；本日不新增判据与门禁。

**验证判据**（文档产出）：每行 ⏳ 均附原因、判据可回溯出处页面；九项对应命令在各自页面可复制执行——拿到 Docker 环境后按回填清单逐项跑通并回填实测列。

**下一步**：第 119 天做**压测**；Docker 环境到位后按[第 4 周收口](../Week4Close/index.md)第三节六步完成九项实测回填，产出追加进回归报告实测列与[进展记录](./index.md)。

## 2026-10-06（第 116 天）：评论 AI 预审与文章摘要 —— 给已上线的写链路接上第一个 LLM 能力

> 第 115 天「下一步」声明的压测仍按口径顺延第 119 天；本日按第 4 周「文档沉淀 + 欠账兑现」节奏，落地一个此前显式悬置的模块：[评论 AI 预审与文章摘要](../AiModeration/index.md)。

**当日做了什么**：

1. **模块契约定稿**：`comments` 增 `ai_verdict` / `ai_verdict_at` 两列（一条 V 迁移）+ 两个内部接口（评论预审 / 文章摘要）+ 一个后台人审动作 `POST /api/v1/admin/comments/{id}/moderate`——**补齐第 106 天显式顺延的「审核动作留给第 4 周」悬置项**，写入侧定初值 → AI 打标 → 人审定终值 → 读侧只认状态。
2. **三条红线**：不给模型任何工具调用；输出只进白名单字段；AI 不改可见性（fail-safe，AI 失效时退回纯人审）。
3. **L2 安全评估集 30 条**（12 reject + 10 review + 8 pass），期望值由人写定、不由模型自评。
4. **本地桩 + 评估运行器 + 四场景实测**（本机真跑，Python 3.13，无外部 API key、无 Docker 依赖）。

**验证判据**（四条均为实测输出，非期望值）：

| 场景 | 命令要点 | 实测 | 退出码 |
| --- | --- | --- | --- |
| A 正常 | 桩 `compliant` 模式 | `RESULT: PASS  30/30` | 0 |
| B 防护失效 | 桩 `unsafe` 模式（一律 pass） | `RESULT: FAIL  8/30`（22 条 reject/review 全部报出） | 1 |
| C 空评估集 | `empty.jsonl` | `RESULT: FAIL (activity check: empty suite)` | 1 |
| D 端点不可达 | 指向未监听端口 | `RESULT: FAIL  0/30`（30 条调用异常） | 1 |

A 证明能过、B 证明能拦、C/D 证明不会自己骗自己——**门禁必须四条都过才算接通**。断言清单 M1~M10 已在[模块页](../AiModeration/index.md)逐条标注实测状态：M3/M4/M5/M6 ✅（本日实测）、M8 ✅（第 108 天已收口）、其余 ⏳ 待 Docker + 真实模型端点。**实测边界**：桩验证的是契约解析、判据执行与门禁接线；换真实模型后这 30 条能否 30/30 未知，那才是 L2 红线的真正含义。

**下一步**：第 119 天做**压测**（口径三处不变）；拿到 Docker + 真实模型端点后先重跑 L2 得到真实模型基线，再回填 M1/M2/M7/M9/M10 与[第 4 周收口](../Week4Close/index.md)九项的实测列。

## 2026-10-07（第 117 天）：交付文档包与运维手册 —— 把 24 章的交付物收敛成可交接的一套

> 第 116 天「下一步」声明的压测仍按口径顺延第 119 天；本日按第 4 周「文档沉淀」节奏落地第 25 章：[交付文档包与运维手册](../Delivery/index.md)。

**当日做了什么**：

1. **交付物清单收敛（11 行）**：每行标注「所在章节 + 验证方式 + 判据」，并写明**本章不新增判据**——部署细节归 [一键部署](../Deployment/index.md)、指标口径归 [监控接入](../Monitoring/index.md)、恢复判据归 [备份恢复演练](../BackupDrill/index.md)、验收项归 [第 4 周收口](../Week4Close/index.md)。理由是判据唯一性：同一条判据两份实现必然分叉。
2. **配置对账做成可执行判据**：给出 `.env.example` 键名提取 + 双向 `diff` 的命令（期望无输出），并列出 14 个关键配置项的「缺失后果」表。其中两项标注为**「不报错但错」**：`TZ`（容器时区不一致 → 超时与定时整体偏移 8 小时，无异常无日志）与 `AI_TIMEOUT_MS`（设成 30 秒 → 每个评论请求最多占用线程 30 秒，正确做法是短超时 + fail-safe 回人审）。
3. **新增 Runbook 四条 SOP**（本页唯一的全新内容）：文章页 502 / 接口大面积超时 / Redis 不可达 / 磁盘写满与日志暴涨，每条按**五段式**（症状 → 5 分钟确认 → 处置 → 回滚 → 判据）写清。此前 24 章讲的都是「正常怎么跑起来」，没有一章回答「坏了先看哪一行」。
4. **SOP 头号纪律**：SOP-4 是四条里唯一**不可回滚**的，处置顺序必须是「**先确认最近一次全量备份可恢复 → 再删**」，判据沿用第 114 天的 R1~R6。
5. **交接清单 D1~D10**：D1/D5 本日核对 ✅、D8 第 114 天已收口 ✅、D10 第 116 天已收口 ✅；D2/D3/D4/D6/D7/D9 ⏳ 待 Docker 与工程环境（原因逐条写明）。

**验证判据**（文档产出，验收是判据不是实测；本节四条命令均可在读者自己的工程里执行）：

| 判据 | 命令要点 | 期望 |
| --- | --- | --- |
| 交付物齐全（D1） | 遍历 11 个章节目录判断 `index.md` 存在 | 11 行全为 `OK` |
| Runbook 五段式完整（D5） | `grep -c` 统计五段标记行数 | 20（4 条 SOP × 5 段） |
| 配置对账（D2） | 提取键名后 `diff` | 无输出（完全一致） |
| SOP-1 可定位（D6） | `docker compose ps` + 健康端点 | 五服务 running；健康端点 200 |

**实测列纪律**（与第 4 周收口、回归报告完全一致）：本机无 Docker 与工程环境，D2/D3/D4/D6/D7/D9 一律标 **⏳ + 原因**，不把期望值抄进实测列。前置条件与第 115 天收敛出的那条完全同源：**一台有 Docker 的机器 + 一个可运行的工程仓库**。

**下一步**：第 118-120 天收口第 4 周。文档沉淀已在本日落地，剩余动作是等 Docker 环境到位后回填九项验收与本章 D3/D4/D6/D7；第 119 天做**压测**，口径三处不变（[第 3 周收口](../Week3Close/index.md) / [验收结论](../CoreFlow/Acceptance/index.md) / 项目总览）。

## 2026-10-07（第 118 天）：前台 PWA 与离线可读 —— 补上「断网时读者看到什么」这个整项目都没回答的问题

> 第 117 天「下一步」声明的第 4 周收尾动作没有变，压测仍按口径顺延第 119 天；本日按第 4 周「广度补齐」节奏落地第 26 章：[前台 PWA 与离线可读](../PwaOffline/index.md)。

**为什么这一章值得单独占一天**：前 25 章回答的都是「**有网时**这个博客怎么跑」——需求、架构、库表、契约、写入、可见性、SSR、账号、部署、监控、备份、AI 预审、交付。**没有一章回答「读者在地铁里点开这个博客，看到的是什么」**。而第 108 天已经把前台做成 SSR，离线兜底的边际成本已经很低——这是一块**投入小、缺口大**的短板。

**当日做了什么**：

1. **四项能力先取舍，再动手**：PWA 的四项能力（可安装 / 可离线 / 可推送 / 可后台）不是打包出售的。本项目按业务价值筛出三件，另一件**明确不做并写明理由**——

   | 能力 | 决策 | 理由（本项目的，不是通用的） |
   | --- | --- | --- |
   | 可离线 | ✅ 做（本章主体） | 博客是读密集型业务；第 108 天已 SSR，兜底成本低 |
   | 可安装 | ✅ 顺带做 | Manifest 是纯声明，**不需要 Service Worker 也能安装**，成本近零 |
   | 可后台 | ✅ 只做评论 | 评论是唯一的读者写入动作，「以为成功其实没有」是信任事故 |
   | 可推送 | ❌ **不做** | 博客更新频率低；VAPID 私钥要进密钥管理，而第 117 天的配置对账里根本没有这一项 |

2. **三层落位（本章唯一需要设计的地方）**：壳（`_nuxt/*`、字体、图标 → 预缓存 + Cache First）/ 内容快照（访问过的文章详情页 HTML → Network First + 3s 超时，`maxEntries: 30`）/ 兜底（`offline.html` → 预缓存 + `navigateFallback`）。关键判断：**SSR 输出的 HTML 不进预缓存**——它是每次请求现渲染的，预缓存一份等于给自己造了一个永远过期的副本。

3. **三条硬红线（都属「不报错但错」，只能靠判据拦）**：
   - `/api/` 必须进 `navigateFallbackDenylist`，否则断网时接口请求会拿到 `offline.html` 的 HTML，`res.json()` 抛出的错误会指向完全无关的位置（第 108 天「搜索页 400 转友好提示」踩过同类）；
   - `/api/v1/me`、`/api/v1/admin/*`、评论写接口**绝不进缓存**——承接第 109 天的数据归属矩阵，个人化数据被缓存后**换账号会串号，这是安全事故不是体验问题**；
   - 接口响应必须限 `statuses: [200]`——第 102 天定死「读者端对非 PUBLISHED 一律 404」，如果 404 也被缓存，读者会**长期**看到「文章不存在」且不会有任何日志。

4. **更新提示按「waiting → 用户点击 → skipWaiting → 刷新」的固定顺序**：本项目前台是 SSR + 按路由懒加载的 chunk，新 SW 在旧页面还在运行时接管并删旧缓存，**正停留在页面上的读者可能立刻拿到 404 的资源**。所以绝不能在 `install` 里直接 `skipWaiting()`。

5. **安装引导按平台分叉**：Chromium 走 `beforeinstallprompt`（`event` 一次性，用完必须置空）；iOS 无程序化 API，只能图文引导，且必须补 `apple-touch-icon`——**只配 manifest 会导致主屏图标是网页截图**。

6. **离线评论队列（复用第 110 天评论链路）**：`IndexedDB` 落盘 + **客户端 UUID 幂等键**（`Idempotency-Key` 随请求发）+ 三个补发触发点（`online` 事件 / `sync` 事件 / **每次应用启动**）。第三点是唯一跨平台的可靠兜底——iOS 与 Firefox 都没有 Background Sync。同时补齐两条接缝：**换账号不补发**（承接第 109 天数据归属矩阵）、**令牌失效标为「需重新登录后重试」**而非带着过期令牌反复重试。

7. **F1~F10 十条验收断言定稿**：形态与第 110 天的 `CF1~CF14`、第 116 天的 `M1~M10` 完全一致（每条都有可执行操作 + 明确期望）。其中 **F10 是本章与第 108 天的守门断言**：`curl` 拿到的必须是完整 SSR HTML，**离线能力绝不能把 SEO 换掉**（抓取工具不执行 Service Worker）。

**验证判据**（本页是文档产出，以下是读者在自己工程里可执行的命令与期望）：

| 判据 | 命令要点 | 期望 |
| --- | --- | --- |
| F1 Manifest 合法 | `curl -sI .../manifest.webmanifest` | 200 且 `Content-Type: application/manifest+json` |
| F3 预缓存只含静态资源 | 控制台列出 precache URL | 全是 `_nuxt/*`、`/icons/*`、`/offline.html`；**无 `.html`、无 `/api/`** |
| F5 读过的文章离线可读 | 访问一篇文章 → 勾 Offline → 刷新 | 正文完整（仅 PUBLISHED 会进缓存） |
| F8 更新提示可走通 | 改 `offline.html` → 重新构建 → 刷新 | 出现提示，点击后加载新文案且旧缓存名被删 |
| F9 离线评论不丢不重 | 勾 Offline 提交 → 恢复网络 | UI 翻成「已发送」，服务端**只有一条**记录 |
| F10 SEO 未被牺牲 | `curl -s http://127.0.0.1:3000/posts/hello \| grep -c '<title>'` | `1`（正文出现在源码里，不依赖 JS） |

**实测列纪律**（与第 4 周收口、回归报告、第 117 天完全一致）：本机没有 Docker、没有可运行的工程仓库，F2/F3/F8/F9 的浏览器侧实测一律标 **⏳ 未跑 + 原因**，F1/F10 的 `curl` 判据也需先起服务。**本章交付的是判据，不把期望值抄进实测列**——兑现前置条件与第 115 天收敛出的那条同源：**一台能跑 Node 构建的机器 + 一个按文档搭起来的工程**。

**一条前置纪律已登记给第 119 天**：压测前必须在 DevTools 里勾上 **Application → Service Workers → Bypass for network**。本章新增的 Service Worker 会显著降低服务端实际压力（缓存命中根本不回源），不排除这个旁路变量，压测得到的 QPS 与服务端负载**没有可比性**。

**下一步**：第 119 天做**压测**（口径三处不变：[第 3 周收口](../Week3Close/index.md)、[验收结论](../CoreFlow/Acceptance/index.md)、[项目总览](../index.md)），压测前置清单里已加上「Bypass for network」这一条；随后第 120 天随 Docker 环境兑现回填九项验收与本章 D3/D4/D6/D7 的实测列。通用原理与工具链（五种缓存策略矩阵、Workbox 7 / `vite-plugin-pwa` 2.0 配置形态、iOS Web Push 六条限制、Background Sync 真实支持面）见 [PWA 与离线应用](../../../../docs/Frontend/PWA/index.md)，本章不重复。

## 2026-10-07（第 119 天）：联调与压测 —— 兑现第 3 周登记的「压测达标」欠账

> 第 118 天「下一步」声明的压测口径没有变，本章**沿用三处口径**（[第 3 周收口](../Week3Close/index.md)、[验收结论](../CoreFlow/Acceptance/index.md)、[项目总览](../index.md)）：不重新排期、不并入第 120 天。本日落地第 27 章：[联调与压测](../LoadTesting/index.md)。

**当日做了什么**：

1. **先补联调复核，再压测**。理由是链路不同：前 20 天的联调跑在**开发机三个直连进程**上，nginx 不在链路里，于是「路径前缀改写 / `X-Forwarded-For` 与真实 IP 限流 / 软 404 的最终呈现」这三段从未被覆盖。复核落成四条 + 一张 I1~I8 清单：

   | 复核项 | 为什么它只在单入口下才暴露 |
   | --- | --- |
   | 契约一致性 | 契约是「写的」，响应是「跑的」，`@JsonIgnore` 会让字段静默消失 |
   | 错误语义 | 401 必须先于 403；404 要**带页面**且不泄漏存在性（第 102 天口径） |
   | 字段对齐 | **雪花 ID 超 2^53 被抹低位**、空集合返 `null` 而非 `[]`、时间戳缺时区 —— 三个都不报错 |
   | 登录态与缓存 | SSR 页面缓存与用户态相互作用；**这条只有两账号交替请求才会暴露** |

2. **压测前置把五个变量钉死**（Pr1~Pr8）：量什么（三项主指标 + 两项诊断）、在什么环境量（**本项目是同机压测 → 结论只能作环比，不能当容量上界**）、用多少数据量（posts ≥ 10000、热文 200、comments ≥ 5000）、排除了哪些**旁路变量（八项）**、从第几秒开始算数（预热 60s 丢弃 / 稳态 180s / 收尾 30s）。其中第 118 天登记的「SW Bypass」正式成为 Pr6。

3. **压测脚本定稿（k6）**，并把压测里最经典的方法论错误单独拆出来讲：**闭模型 → 协调遗漏**。系统卡 2s 时，闭模型的 VU 全卡在等响应上，本该排队的 199 个请求「消失」了，于是 P99 看起来只有几百毫秒——因此**容量验证一律用 `constant-arrival-rate`（开模型）**，并把模型类型写进报告。另附一条**许可证红线**：k6 是 AGPL-3.0，当工具跑自己的系统没问题，嵌进要交付或托管的平台需先过法务。

4. **瓶颈定位固化为四层顺序表**：入口 nginx → 应用（blog-server / blog-server 之外的 **blog-web SSR 单线程**）→ Redis → MySQL；**从连接池 `pending` 开始看**，因为它是「在等服务端资源」的直接证据，而不是推算。配一段完整的五段式走查（症状 → 5 分钟确认 → 定位 → 结论 → 判据），根因是列表查询在万级数据量下退化为 `type=ALL` + `filesort`——**这在只有 12 篇的开发库上永远发现不了**，正好印证「数据量级」为何被列进前置。

5. **优化落地改为单变量流水线**：改前快照 → 只改一处 → **复跑十二道门禁** → 同参数复压 → 环比 P95 与错误率。头号危险区是缓存类改动（延长 TTL 换命中率会直接破坏第 102 天的可见性时序）。记录三项优化（联合索引 / 列表投影裁剪 / 容器内存与 JVM 堆对齐），逐项给出期望与复压判据。

6. **验收三段编号定稿**：`I1~I8`（联调）、`Pr1~Pr8`（前置）、`L1~L14`（验收），与既有 `CF1~CF14`、`M1~M10`、`F1~F10`、`R1~R6`、`D1~D10` **互补而不重叠**（判据唯一性）。其中 **L12 要求根因有「结构性」判据**（`EXPLAIN` 的 `type` 非 `ALL`、无 `Using filesort`）——只写「P95 ≤ 360ms」的话，下次索引被误删会整条链路重走一遍。

**验证判据**（本页是文档产出，以下是读者在自己工程里可执行的命令与期望）：

| 判据 | 命令要点 | 期望 |
| --- | --- | --- |
| I1 单入口三探活 | `curl -o /dev/null -w '%{http_code}'` 打 `/`、`/api/v1/posts`、`/api/v1/nope` | 200 / 200 / 404 |
| I3 大整数为字符串 | `jq -r '.data[0].id \| type'` | `string` |
| I7 软 404 不泄漏 | 草稿 slug 与不存在 slug 的状态码对比 | 两者相同（404） |
| I8 两账号不串号 | 交替请求 `/me` | 各返回自己的邮箱 |
| Pr4 数据量达标 | 三表 `COUNT(*)` | ≥ 10000 / 5000 / 200 |
| L5/L6 基线→目标 | `summary-export` 中 `p(95)` | 目标档 ≤ 基线 × 2 |
| L9 压测机未成瓶颈 | 摘要中 `dropped_iterations` | = 0 |
| L12 根因有结构判据 | `EXPLAIN` 输出 | `type` 非 `ALL`、无 filesort |
| L13 功能未回归 | `mvn test` + 十二道冒烟 | 零失败 |

**实测列纪律**（与第 111/115/117 天完全一致）：本机没有 Docker、没有可运行的工程仓库，**L1~L13 一律记 ⏳ 阻塞 + 原因**（解除条件 = 一台有 Docker 的机器 + 按文档搭起来的工程），**不把期望值抄进实测列**；只有 L14（报告四要素模板）本日 ✅——它是文档产出，不依赖环境。

**顺带登记一条合并建议**：第 118 天遗留的 F2/F3/F8/F9、第 117 天遗留的 D3/D4/D6/D7 与本章 L1~L13 **共享同一个前置条件（Docker 环境）**，第 120 天应一次性兑现，不要分三次开环境。

**下一步**：第 120 天「部署与验收」——把本章 I1~I8 与 L1~L14 并入上线验收清单，随 Docker 环境一次性兑现全部遗留实测回填；本章新增待办只有一条：k6 脚本随环境跑一次，回填 L5~L12。

## 2026-10-07（第 120 天）：上线发布与结项验收 —— 周期 4 收口

**做了什么**：

1. **新建章节 [上线发布与结项验收](../ReleaseAcceptance/index.md)（8 页）**，并为全项目定下四条不动原则：不新增判据、不改口径、不抄期望值、不做复盘。前 27 章回答「怎么做出来」，本章只回答「这些已定稿的判据兑现了多少」。

2. **发布方案（[ReleasePlan](../ReleaseAcceptance/ReleasePlan/index.md)，GL1~GL6）**：把「发布做完了」变成可证伪的定义——四个前置（提交与镜像 tag 一致 / 预发布十二道冒烟 / **回滚包已真拉取** / 备份非空）、一个时序（**迁移必须早于应用替换**）、一个后置（15 分钟观察窗口内四项指标在基线内）。给出发布窗口的三条选择标准与四条可复制命令；定 L1/L2/L3 三级处置，并写死**「L3 命中 Rb1~Rb3 即回滚，不需审批」**——把「要不要回滚」从需要判断力的问题，转化为只需查表的问题。

3. **回滚预案（[Rollback](../ReleaseAcceptance/Rollback/index.md)，Rb1~Rb8）**：三条硬判据全部围绕「用户还能不能用」（写链路 5xx / 文章详情 404 / 登录链路），并把 **Rb2 单独列一条**——404 既不计入错误率也不写日志，但内容对读者消失与宕机等价。三类回滚按代价排序（应用 → 配置 → 数据），给出铁律「能只回应用就绝不回数据」；补 RB5 配置回滚的隐藏陷阱（`restart` **不重读** `environment`，必须 `up -d`）与 **RB7/RB8**（回滚后必须重跑冒烟、必须补 revert，否则下次发布原样复发）。新增「**不可回滚点**」判定法：一条自查问题——「切回上一版本后，数据库还能不能服务它？」

4. **欠账合并兑现（[EnvFulfill](../ReleaseAcceptance/EnvFulfill/index.md)，S1~S8）**：把第 115/116/117/118/119 天各自登记的 `⏳` 合并成**一条执行序列**，并给出「欠账 → 编号 → 出处 → 兑现段」完整映射。核心理由：五批欠账**共享同一个前置条件**（一台有 Docker 的机器），分五次开环境 = 五次返工。序列：S1 骨架与迁移 → S2 十二道冒烟 → S3 观测（含告警**真触发**验证）→ S4 第 13 道 AI 评估 → S5 浏览器侧与回滚演练 → S6 压测 → S7 备份恢复 → S8 从零复现。附四条执行纪律与兑现记录表模板。

5. **上线验收终版（[GoLiveCheck](../ReleaseAcceptance/GoLiveCheck/index.md)）**：把五个编号族（九项 / `L` / `F` / `D` / `M`，并入 `GL`/`Rb`/`H`）**按验收对象**重排成四组——A 系统可用 / B 可观测 / C 抗压与可恢复 / D 可交接与可复现——形成全项目唯一的验收入口。**只归类不重写**：判据正文只有一处，摘要与原文冲突以出处为准。落点的一条设计是：把 `D6`/`D7` 从「交接组」挪进「B 可观测组」，因为**分组按它验证的对象，而不是按它由哪一天产出**。

6. **结项与交接（[Handover](../ReleaseAcceptance/Handover/index.md)，H1~H8）**：写清「验收答能不能上（对象是系统）、交接答换人接不接得住（对象是人）」为什么必须是两张表（判据稳定性不同）。`H6~H8` 要求知识转移**被验证**而非被宣称——「他操作，我只看不说」并记录卡点。建立遗留登记表，四条遗留的共同根因被显式暴露：**它们全部指向同一个解除条件**（Docker 环境），这层信息在「待补充」式记录里永远看不见。澄清结项标准是「零**无主**遗留」而非「零遗留」。

7. **文档沉淀与从零复现（[DocsRepro](../ReleaseAcceptance/DocsRepro/index.md)）**：给出八段复现最短路径（每段附「做完的标志」）、五条「顺序不对就必然失败」的依赖陷阱（先评论后文章、先搜索后渲染、先 SSR 后账号、先压测后功能、迁移与应用倒序），并把 **17 项巡检明确定位为「文档门禁」**——`pnpm docs:build` 只证明语法没错，不证明文档能用（`H4` 的证据来源）。

8. **FAQ（[FAQ](../ReleaseAcceptance/FAQ/index.md)）**：六行分诊表（第一问固定为「损害兑现了吗」）、12 个高频问答、发布前十条自查清单、十二条纪律、13 条术语表。

**验证判据**（本页是文档产出，以下是读者在自己工程里可执行的命令与期望）：

| 判据 | 命令要点 | 期望 |
| --- | --- | --- |
| GL1 冻结版本一致 | `git rev-parse HEAD` 与镜像 tag 比对 | 同一 SHA |
| GL3 回滚包可拉取 | `docker pull <repo>:<previous-tag>` | 拉取成功 |
| GL5 迁移早于应用 | `docker compose logs` 两段时间戳比对 | 迁移时刻更早 |
| GL6 观察窗口四项达标 | 错误率 < 1%、P95 ≤ 基线×2、命中率 ≥ 90%、pending = 0 | 四项全达标 |
| Rb4 应用回滚耗时 | `time docker compose up -d --no-deps blog-server` | ≤ 5 分钟 |
| Rb7 回滚后冒烟 | 十二道 `*_smoke.py` | 全绿 |
| H4 文档门禁 | 17 项巡检脚本 | 全部退出码 0 |
| H5 从零复现 | 新目录重建 + `k6 run --vus 1 --duration 30s` | checks 100% |

**实测列纪律**（与第 111/115/117/119 天完全一致，本页是第五次落点）：本机没有 Docker、没有可运行的工程仓库，**A/B/C/D 四组的运行时条目一律记 ⏳ 阻塞 + 原因 + 解除条件**，不把期望值抄进实测列。本日实测 ✅ 的只有两项：`L14`（压测报告四要素模板，已在第 119 天定稿）与终表本身的**文档层判据**（四组分类互斥完备、每条可回溯唯一出处、三态定义与既有页面一致）。

**顺带结清一条**：第 119 天登记的合并建议在本页被正式采纳——F2/F3/F8/F9、D3/D4/D6/D7、L1~L13、M10 全部并入 `S1~S8`，前置条件满足一次即可全部兑现。

**下一步**：**本项目到此结束**——周期 4（第 91-120 天，全栈博客平台）累计 **28 章 + 8 页收口章节**，全部交付物索引见[结项与交接](../ReleaseAcceptance/Handover/index.md)。周期 5（第 121-150 天）起为「实时监控大盘」，从需求与架构重新开始。
