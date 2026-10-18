# 评论与 @ 提及的写入接口

第 2 周第 5 步：把「评论」做成一条**可幂等重放、提及范围可控、通知不会重复也不会丢**的写入链路。

## 当日做了什么

| 项 | 产出 |
| --- | --- |
| 数据模型 | `comment`（评论主体）、`comment_mention`（提及关系）、`notification_outbox`（待投递通知）三张表的完整 DDL 与四条约束 |
| 接口 | `POST /api/v1/cards/{cardId}/comments`、`GET .../comments`、`PATCH .../comments/{id}`、`DELETE .../comments/{id}` 四个契约 |
| 提及解析 | 解析规则、边界条件、三种「看起来能 @ 其实不该 @」的情形 |
| 幂等 | `Idempotency-Key` + 客户端 `tempId` 双保险，重复提交返回同一 `commentId` |
| 通知扇出 | 同事务写 outbox（至少一次投递），消费侧按 `(recipient, comment_id)` 去重 |
| 可见性 | 提及对象必须是**本工作区成员**，否则整条请求拒绝——防止「@ 到无权用户」造成信息泄漏 |
| 判据 | `CM-A` ~ `CM-H` 八条，每条都给出可执行验收 |

::: tip 本步的位置
第 159 天（`BoardCardApi`）解决了「卡片本身怎么读写」。这一步解决的是**挂在卡片上的第二类写入**：它比卡片更麻烦，因为一条评论会**派生出别的写入**（提及关系、通知），而这些派生写入必须和评论在同一个事务里成立，否则就会出现「评论成功但通知丢了」这个协作系统最常被投诉的不一致。
:::

## 一、为什么这一步不是「加一个 POST」

一条评论的写入涉及五次变化：

| # | 变化 | 失败的后果 |
| --- | --- | --- |
| 1 | `comment` 插入一行 | 评论没发出去 |
| 2 | `comment_mention` 插入 N 行 | 被 @ 的人收不到通知，且无法反查「谁被提过」 |
| 3 | `notification_outbox` 插入 N 行 | 通知丢失（且没有任何补偿线索） |
| 4 | `card.comment_count` 递增 | 列表页评论数不对（第 159 天用 `LEFT JOIN` 聚合，可不用这一列；若用冗余列就必须同事务） |
| 5 | `board_events` 插入一条事件 | 其他人的屏幕上看不到这条评论 |

**1~3 必须在同一个事务里**（它们描述同一件事）；4 若采用冗余列也在同一事务；5 走第 140 天定的 outbox 模式（提交后广播），不能和 1~3 混在一个事务里等待推送。

## 二、数据模型

```sql
-- V6__comment_mention.sql

CREATE TABLE comment (
  id           uuid        NOT NULL DEFAULT uuidv7(),
  tenant_id    bigint      NOT NULL,
  board_id     uuid        NOT NULL,
  card_id      uuid        NOT NULL,
  author_id    bigint      NOT NULL,
  body         text        NOT NULL,
  body_html    text        NOT NULL,
  edited_at    timestamptz,
  deleted_at   timestamptz,
  created_at   timestamptz NOT NULL DEFAULT now(),
  version      integer     NOT NULL DEFAULT 0,
  CONSTRAINT comment_pk PRIMARY KEY (id),
  CONSTRAINT comment_body_ck CHECK (length(body) BETWEEN 1 AND 8000),
  CONSTRAINT comment_board_fk FOREIGN KEY (board_id, tenant_id)
      REFERENCES board (id, tenant_id) ON DELETE CASCADE,
  CONSTRAINT comment_card_fk FOREIGN KEY (card_id, board_id, tenant_id)
      REFERENCES card (id, board_id, tenant_id) ON DELETE CASCADE
);
CREATE INDEX comment_card_idx ON comment (card_id, created_at DESC, id DESC)
  WHERE deleted_at IS NULL;
```

```sql
CREATE TABLE comment_mention (
  comment_id   uuid   NOT NULL,
  tenant_id    bigint NOT NULL,
  mentioned_id bigint NOT NULL,
  kind         text   NOT NULL DEFAULT 'user',
  CONSTRAINT comment_mention_pk PRIMARY KEY (comment_id, mentioned_id),
  CONSTRAINT comment_mention_kind_ck CHECK (kind IN ('user','group')),
  CONSTRAINT comment_mention_fk FOREIGN KEY (comment_id)
      REFERENCES comment (id) ON DELETE CASCADE
);
CREATE INDEX comment_mention_user_idx ON comment_mention (mentioned_id, comment_id);
```

```sql
CREATE TABLE notification_outbox (
  id           bigint      GENERATED ALWAYS AS IDENTITY,
  tenant_id    bigint      NOT NULL,
  topic        text        NOT NULL,
  payload      jsonb       NOT NULL,
  dedup_key    text        NOT NULL,
  created_at   timestamptz NOT NULL DEFAULT now(),
  published_at timestamptz,
  attempts     integer     NOT NULL DEFAULT 0,
  CONSTRAINT notification_outbox_uk UNIQUE (tenant_id, dedup_key)
);
CREATE INDEX notification_outbox_pending_idx ON notification_outbox (id)
  WHERE published_at IS NULL;
```

四条设计理由：

1. **`comment_mention` 用复合主键 `(comment_id, mentioned_id)`**：同一条评论里 @ 同一个人两次只留一行——这是「去重」的第一道闸，在数据库层解决，不依赖应用。
2. **`dedup_key` 唯一约束**：形如 `mention:{comment_id}:{user_id}`。重复解析、重复提交、重试都不会产生第二条通知。
3. **`comment` 用 `uuidv7()`**：时间有序，索引写入局部性好（详见 [数据库内核 · B+ 树](/docs/DB/DatabaseInternals/BPlusTree/index.md)），且客户端可以先生成 `tempId` 做乐观展示。
4. **`deleted_at` 软删 + 部分索引**：列表只查未删的；软删的评论仍保留 `comment_mention`（审计需要「这条评论提过谁」），但不再产生新通知。

## 三、提及解析：三条规则与三种假阳性

### 解析规则

```text
@ 后紧跟 显示名 或 用户名
结束条件：空白、标点（，。！？、；：""''（）【】）、换行、字符串结束
最长匹配：优先匹配最长合法用户名（@张三丰 不应解析成 @张三）
大小写：用户名不区分大小写；显示名区分（同名时以用户名为准）
```

解析结果必须落到 `user_id`，而不是保留字符串——**通知要发给 ID，不是发给一段文本**。

### 三种「看起来能 @ 其实不该 @」

| 情形 | 例子 | 正确处置 |
| --- | --- | --- |
| **代码块 / 引用里的 @** | `` `user@example.com` `` | 解析前先剥离代码块与行内代码，否则会把邮箱当成提及 |
| **@ 后面是邮箱或 URL** | `support@company.com` | 正则要求 `@` 前是**行首或空白**，且后面只允许用户名字符集 |
| **@ 到一个不存在的用户** | `@张三丰`（已离职） | **不报错**，但也不产生提及与通知；在响应里返回 `unresolvedMentions` 供前端提示 |

第三条最容易做错：如果「@ 不存在的人」直接返回 400，那么用户离职后所有历史评论在编辑时都会失败。正确做法是**静默降级为纯文本**，并把未解析项返回给前端做提示。

::: danger 最容易造成事故的一种：@ 到非本工作区成员
「@ 一个不在这个看板里的人」如果被允许，会出现两种后果：① 通知发给了不该看到这块看板的人（信息泄漏）；② 那个人点进来发现 404（体验断裂）。

**正确做法是整条请求拒绝**（`422 MENTION_NOT_MEMBER`），而不是静默过滤——静默过滤会让用户以为「我 @ 了他」，实际没发出去。
:::

## 四、幂等：两道保险

客户端在弱网下重试是常态。评论的重复提交比卡片更明显，因为用户会「以为没发出去」再点一次。

| 保险 | 机制 | 解决什么 |
| --- | --- | --- |
| **客户端 `tempId`** | 前端生成 UUID，随请求带上；服务端以 `(author_id, temp_id)` 做唯一约束 | 同一用户同一条草稿的重复提交 |
| **`Idempotency-Key` 头** | 客户端为每次「发送动作」生成一个 key；服务端存 `key → 响应体` 24 小时 | 网络重试、客户端重放、SDK 自动重试 |

```sql
-- 去重表（与评论同事务写入）
CREATE TABLE idempotency_record (
  tenant_id  bigint      NOT NULL,
  scope      text        NOT NULL,          -- 'comment.create'
  key        text        NOT NULL,
  response   jsonb       NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT idempotency_record_pk PRIMARY KEY (tenant_id, scope, key)
);
```

三次重复提交的预期行为：

| 场景 | 期望 |
| --- | --- |
| 同一 `Idempotency-Key` 第二次提交 | 返回**第一次的响应体**（含同一 `commentId`），HTTP 200 |
| 同一 `tempId` 但不同 key | 命中 `(author_id, temp_id)` 唯一约束 → 返回已存在的评论（200，不是 409） |
| 不同 key、不同 `tempId`、内容相同 | **视为两条评论**（用户确实可能发两遍），不合并 |

第三行是刻意的：**幂等只能靠客户端给的标识，不能靠「内容相同」猜**。按内容去重会把「我就是要发两遍」误判成重复。

## 五、通知扇出：同事务写 outbox

```sql
-- 与评论插入同一事务
WITH new_comment AS (
  INSERT INTO comment (tenant_id, board_id, card_id, author_id, body, body_html, temp_id)
  VALUES (:tenant, :board, :card, :author, :body, :html, :temp_id)
  RETURNING id
), mentions AS (
  INSERT INTO comment_mention (comment_id, tenant_id, mentioned_id)
  SELECT nc.id, :tenant, m.user_id
    FROM new_comment nc, unnest(:mentioned_ids::bigint[]) AS m(user_id)
  ON CONFLICT DO NOTHING
  RETURNING comment_id, mentioned_id
)
INSERT INTO notification_outbox (tenant_id, topic, payload, dedup_key)
SELECT :tenant,
       'comment.mention',
       jsonb_build_object('commentId', mention.comment_id, 'cardId', :card, 'userId', mention.mentioned_id),
       'mention:' || mention.comment_id || ':' || mention.mentioned_id
  FROM mentions mention
ON CONFLICT (tenant_id, dedup_key) DO NOTHING;
```

三个要点：

1. **用 CTE 把三步串成一条语句**：避免「先查再插」的竞态，也避免 `nextval()` 被调用两次（第 159 天记过的坑）。
2. **`ON CONFLICT DO NOTHING` 两处都要有**：提及去重（同一个人被 @ 两次）与通知去重（重试时）。
3. **不要在这里直接调用推送**：事务提交前推送 = 可能推送了一条最终回滚的评论。投递由消费者按 `published_at IS NULL` 拉取。

### 折叠：一次 @ 五个人不产生五条通知

```sql
-- 消费侧按 (recipient, card_id, 5 分钟窗口) 折叠
SELECT recipient_id, card_id,
       count(*) AS mentions,
       min(created_at) AS first_at
  FROM notification_outbox
 WHERE topic = 'comment.mention' AND published_at IS NULL
 GROUP BY recipient_id, card_id, date_trunc('5 minutes', created_at);
```

折叠规则：同一收件人、同一卡片、5 分钟内的多条提及合并成一条「张三等 3 人在卡片《…》中提到了你」。**折叠只影响展示，不影响 `comment_mention` 的完整记录**——审计要的是「谁被提过」，不是「发了几条通知」。

## 六、接口契约

| 方法 | 路径 | 成功 | 主要错误 |
| --- | --- | --- | --- |
| `POST` | `/api/v1/cards/{cardId}/comments` | `201` + `{commentId, createdAt, mentions[]}` | `404 CARD_NOT_FOUND`、`403 NOT_BOARD_MEMBER`、`422 MENTION_NOT_MEMBER`、`409 IDEMPOTENT_REPLAY`（同 key 不同体） |
| `GET` | `/api/v1/cards/{cardId}/comments` | `200` + 游标分页 | `404`、`403` |
| `PATCH` | `/api/v1/cards/{commentId}` | `200` + 新 `version` | `409 VERSION_CONFLICT`、`403 NOT_AUTHOR` |
| `DELETE` | `/api/v1/cards/{commentId}` | `204` | `403 NOT_AUTHOR_OR_ADMIN` |

四条契约纪律：

1. **`POST` 必须返回 `mentions[]`**（`userId` + `displayName`），前端用它渲染高亮；不返回的话前端要二次解析，解析规则两份必然漂移。
2. **`PATCH` 必须带 `version`**（乐观锁，与第 159 天的卡片一致），并**重新解析提及**：编辑后新增的提及要补通知，删掉的提及要撤回（见下）。
3. **`DELETE` 是软删**：`deleted_at` 置位，`comment_mention` 保留，`notification_outbox` 里未投递的提及通知**标记为作废**（`published_at` 置为 `now()` 且 `payload` 加 `revoked:true`）。
4. **编辑不重发全部通知**：只对「新增的被提及者」发通知，已有提及者不重复打扰。

## 七、如何验证

```shell
# ① 三张表与四条约束是否就位
psql "$DB" -tAc "SELECT conname FROM pg_constraint
  WHERE conrelid IN ('comment'::regclass,'comment_mention'::regclass,'notification_outbox'::regclass)
  ORDER BY 1"
```

**预期输出**：至少包含 `comment_body_ck`、`comment_mention_pk`、`notification_outbox_uk`、`comment_card_fk`。

```shell
# ② 同一 Idempotency-Key 提交两次，返回同一 commentId
KEY=$(uuidgen)
for i in 1 2; do
  curl -s -X POST "http://localhost:8080/api/v1/cards/$CARD/comments" \
    -H "Authorization: Bearer $TOKEN" -H "Idempotency-Key: $KEY" \
    -H 'Content-Type: application/json' \
    -d '{"body":"@alice 看一下这个","tempId":"'$(uuidgen)'"}' | jq -r .commentId
done
```

**预期输出**：两行**完全相同**的 UUID。

```shell
# ③ 提及关系与通知条数一致（去重生效）
psql "$DB" -tAc "SELECT
  (SELECT count(*) FROM comment_mention WHERE comment_id = '$CID') AS mentions,
  (SELECT count(*) FROM notification_outbox WHERE dedup_key LIKE 'mention:$CID:%') AS notices"
```

**预期输出**：两个数字相等。通知数大于提及数说明去重没生效。

```shell
# ④ @ 非本工作区成员必须整条拒绝
curl -s -o /dev/null -w '%{http_code}\n' -X POST "http://localhost:8080/api/v1/cards/$CARD/comments" \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"body":"@outsider 你好","tempId":"'$(uuidgen)'"}'
```

**预期输出**：`422`。返回 `201` 说明越权提及没有被拦住。

```shell
# ⑤ 代码块里的 @ 不应被解析
psql "$DB" -tAc "SELECT count(*) FROM comment_mention WHERE comment_id = '$CID_CODE'"
```

**预期输出**：`0`。大于 0 说明解析前没有剥离代码块。

```shell
# ⑥ 编辑后新增提及只发一条新通知
psql "$DB" -tAc "SELECT count(*) FROM notification_outbox WHERE dedup_key LIKE 'mention:$CID:%'"
```

**预期输出**：编辑前 N 条，编辑后 N+1 条（只多出新增的那一位），不是 2N。

```shell
# ⑦ 删除评论后未投递通知作废、已投递不回滚
psql "$DB" -tAc "SELECT payload->>'revoked', published_at IS NOT NULL
  FROM notification_outbox WHERE dedup_key LIKE 'mention:$CID:%'"
```

**预期输出**：待投递的那些显示 `revoked = true`；已投递的保持原样（不撤回已送达的通知，只在展示层标注「评论已删除」）。

```shell
# ⑧ 并发 20 次同版本编辑，只有 1 次成功
seq 20 | xargs -P20 -I{} curl -s -o /dev/null -w '%{http_code}\n' \
  -X PATCH "http://localhost:8080/api/v1/cards/$CID" \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"body":"edit","version":0}' | sort | uniq -c
```

**预期输出**：`1 200` + `19 409`。

::: warning 这八条命令需要真实运行的服务
本页的验证命令依赖**读者自己的工程**（Java 25 + Spring Boot 4.1 + PostgreSQL 18）已按前面章节启动。`project/` 只有文档、没有代码，因此这里给的是**契约与判据**，不给可执行副本。若尚未实现接口，命令 ②~⑧ 会连接失败——这是正常状态，按「下一步」继续做完再回来验。
:::

## 八、判据族 `CM-A` ~ `CM-H`

| 判据 | 规则 | 违反时的样子 | 验证方式 |
| --- | --- | --- | --- |
| `CM-A` | 评论、提及、通知三张表必须在同一事务内写入 | 评论成功但通知丢失，无补偿线索 | 命令 ③ |
| `CM-B` | 提及去重由复合主键保证，不依赖应用层 `if` | 同一人被 @ 两次产生两条通知 | 命令 ③ |
| `CM-C` | 通知去重由 `dedup_key` 唯一约束保证 | 重试或重放产生重复通知 | 命令 ③⑥ |
| `CM-D` | 提及对象必须是本工作区成员，否则整条请求 `422` | 通知发给无权用户（信息泄漏）或静默不发 | 命令 ④ |
| `CM-E` | 解析前必须剥离代码块与行内代码 | 邮箱、代码片段被当成提及 | 命令 ⑤ |
| `CM-F` | 未解析的提及静默降级为纯文本，并在响应中返回 | 离职用户导致历史评论无法编辑 | 见第三节 |
| `CM-G` | 编辑只对新增提及发通知，删除提及要作废未投递通知 | 编辑一次打扰所有人一遍 | 命令 ⑥⑦ |
| `CM-H` | `PATCH` 必须带 `version` 乐观锁 | 两人同时编辑，后写覆盖前写 | 命令 ⑧ |

## 九、下一步

| 顺序 | 内容 | 为什么是下一步 |
| --- | --- | --- |
| 1 | **附件直传（预签名 URL）** | 评论的下一类内容就是图片/文件；它与评论共用「先建记录、后补资源」的模式 |
| 2 | **通知中心的读接口**（未读数、已读游标） | 通知已经进了 outbox，但还没有「收件箱」；读模型与写模型要分开设计 |
| 3 | **实时推送接线**（STOMP + Redis 广播） | 评论的 `board_events` 已经写入，但还没有推到其他人屏幕上（第 140 天定了协议，未接线） |
| 4 | **跨租户用例矩阵补三行** | 新增的「提及越权」是第 155 天 18 格矩阵之外的第 19 格，要回填 |

::: info 版本与边界
本步基于项目基线：Java **25（LTS）**、Spring Boot **4.1**、PostgreSQL **18**（`uuidv7()` 原生可用）、Flyway 迁移。`uuidv7()` 需要 PG 18+，若读者的环境是 17 及以下，改用 `gen_random_uuid()` 并接受索引局部性变差（见 [B+ 树](/docs/DB/DatabaseInternals/BPlusTree/index.md) 的写入局部性一节）。
:::

## 参考资料

- 本站 [分区分表与冷热分离](/docs/DB/PartitionArchival/index.md)——评论与通知表未来也会面临「历史怎么删」，分区与归档的判据在那里
- 本站 [幂等键设计](/docs/Backend/IdempotencyStateMachine/IdempotencyKey/index.md)——`Idempotency-Key` 的完整口径与 409 分支
- 本站 [实时协作与冲突解决](/docs/Backend/RealtimeCollaboration/index.md)——评论的协同编辑与顺序问题
- 本站 [数据建模](/docs/DB/DataModeling/index.md)——复合外键与冗余列的取舍
- 相邻章节：[看板与卡片读写接口](../BoardCardApi/index.md) · [拖动写入路径](../DragWritePath/index.md) · [事件表与顺序字段](../EventSequence/index.md)
