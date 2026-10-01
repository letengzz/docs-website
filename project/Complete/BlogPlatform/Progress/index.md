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
