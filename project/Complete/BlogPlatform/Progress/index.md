# 进展记录

每个条目记录三件事：**做了什么、如何验证、下一步是什么**。格式沿用 [后端通用模板 · 进展记录](../../../Base/BackendTemplate/Progress/index.md)。

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
