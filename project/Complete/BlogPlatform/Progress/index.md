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
