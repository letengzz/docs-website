# 批量数据交换工程

一次性接口传一条数据，出错时调用方立刻知道；批量导入传一个文件，出错时**只有用户知道**——他打开自己的 Excel 数了一遍，发现少了 13 行。批量数据交换的全部工程量，就是为了让「少了的那 13 行」在**用户发现之前**就已经被记录下来、能指回原文的某一行、并且能解释为什么被拒。

本专题讲**一个文件从上传到入账、再到导出对账的完整链路**：文件契约怎么定、编码与格式怎么解析、行级校验怎么做、重跑怎么不重复、导出怎么保证是一份静止画面、异步作业的状态怎么表达。它不讲具体某个库的 API（那是[工具 · 数据操作](../../Tools/DatabaseClients/DataOps/index.md)的事），只讲**这一整条链路上，哪些地方一定会安静地丢数据**。

<p style="text-align:center;"><img src="./assets/bulkdataexchange-logo.png" style="zoom:75%;" alt="批量数据交换工程 Logo" /></p>

::: tip 一句话理解
批量导入的失败**几乎不报错**：作业 `exit 0`、日志写着 `import done`、库里确实多了 9,987 行——差的 13 行被一次「业务校验不通过」轻轻带过，而回执没生成、行号没记、用户也无从复核。
:::

::: info 本专题与相邻专题的分工
- **单条记录的幂等键与状态机** → [幂等与状态机工程](../IdempotencyStateMachine/IdempotencyKey/index.md)：那边讲「一次请求重复到达怎么办」，本专题讲「**一个文件**重复上传、以及一个文件内部**几万行**的幂等怎么做」——单位从「请求」变成「批次 + 行」。
- **对象存储、上传与预签名** → [对象存储工程](../ObjectStorage/index.md)：那是**字节怎么存**（分片上传、生命周期、签名 URL），本专题的[导出快照](ExportSnapshot/index.md)只借用它做「下载凭证」，不重复讲存储选型。
- **定时任务与延迟调度** → [分布式调度工程](../DistributedScheduling/index.md)：那边管「什么时候跑」，本专题的[异步作业](AsyncJob/index.md)管「跑起来之后状态怎么表达、进度怎么报、取消怎么落」。
- **消息投递与重试** → [消息通知与触达工程](../NotificationDelivery/index.md)：那边的重试目标是「让用户收到」，本专题的重试目标是「让同一批数据**不重复入账**」——重试的语义完全不同。
- **CSV 与 Excel 的操作级用法** → [工具 · 数据库客户端数据操作](../../Tools/DatabaseClients/DataOps/index.md)：那边是「怎么点、怎么导」，本专题是「导出来的东西凭什么可信」。
- **数据入仓与分层** → [数据仓库](../../DB/DataWarehouse/index.md) 与 [CDC](../../DB/CDC/index.md)：那是**持续同步**，本专题是**人工触发的一次性文件交换**；前者追求低延迟，后者追求可解释与可重跑。
- **对账本身** → [账务与清结算 · 对账](../Ledger/Reconciliation/index.md)：本专题只做到「把行数与金额交出去」，谁跟谁对、差异怎么归口在那边。
:::

## 目录

- [总览：七段交换链与三个成功定义](Overview/index.md)
- [文件契约：模板、列定义与版本](FileContract/index.md)
- [解析与编码：编码嗅探、引号与注入面](ParsingAndEncoding/index.md)
- [行级校验与错误回执](RowValidation/index.md)
- [幂等重跑、批次状态机与断点](IdempotentRerun/index.md)
- [导出：快照一致性、分页与流式下载](ExportSnapshot/index.md)
- [异步作业：进度、取消与并发](AsyncJob/index.md)
- [实战：一个能跑起来的最小交换链路](Practice/index.md)
- [常见问题与分诊](FAQ/index.md)

## 专题地图

![批量数据交换专题地图](./assets/bdx-topic-map.svg)

## 判据纪律

沿用全库写法：**每页 8 条，编号形如 `BDO-A`**，逐页前缀唯一，可被 `utils/audit` 下的判据类巡检机械核对。每条判据回答四件事：**看什么现象、判成什么、不满足时改哪里**。

| 页 | 判据族 | 这一族管什么 | 条数 |
| --- | --- | --- | --- |
| 总览 | `BDO-A` ~ `BDO-H` | 七段链、三个成功定义、七个必失点、接缝归属 | 8 |
| 文件契约 | `BDF-A` ~ `BDF-H` | 模板版本、列定义、表头匹配、单位与日期、行号语义 | 8 |
| 解析与编码 | `BDP-A` ~ `BDP-H` | 编码嗅探、BOM、引号与换行、注入面、大小与解压上限、流式 | 8 |
| 校验与回执 | `BDR-A` ~ `BDR-H` | 校验分层、错误码、行内多错、回执文件、部分成功、阈值 | 8 |
| 幂等重跑 | `BDI-A` ~ `BDI-H` | 业务键、文件指纹、批次状态机、断点、覆盖语义、互斥 | 8 |
| 导出快照 | `BDX-A` ~ `BDX-H` | 快照时点、keyset 分页、稳定排序、流式写、凭证、口径页 | 8 |
| 异步作业 | `BDJ-A` ~ `BDJ-H` | 作业表、进度口径、取消、并发与优先级、重试、可观测 | 8 |
| 实战 | `BDE-A` ~ `BDE-H` | 表结构、五步流水、负向验收、可重跑、验收 SQL | 8 |
| 常见问题 | `BDQ-A` ~ `BDQ-H` | 分诊表、误判、止血顺序、上线自查 | 8 |

合计 **9 族 72 条**。

## 事实与规格速览（2026-10 口径）

这类工程的实现细节几乎全被**外部规格**决定，写清楚以免被旧经验误导：

| 事项 | 现状 | 对交换链路的影响 |
| --- | --- | --- |
| Excel 工作表上限 | **1,048,576 行 × 16,384 列**；单元格最多 **32,767 字符**；单元格内最多 **253 个换行**（Microsoft 官方规格） | 「导出全量给业务看」在百万行以上必然失败，且**不会报错**——Excel 只会静默丢弃超出部分。超过 100 万行就要分片，且分片依据必须是**稳定排序键**，见[导出快照](ExportSnapshot/index.md) |
| CSV 标准 | RFC 4180（2005）：逗号分隔、双引号包裹、引号内 `""` 转义、字段内可含换行 | 这是「为什么不能用 `split(',')`」的规范依据。本机实测：含引号与换行的 5,000 行数据，按逗号切分错 **3,724 行（74.5%）**，`csv.reader` 错 0 行 |
| 公式注入 | CWE-1236 `Improper Neutralization of Formula Elements in a CSV File`；OWASP 列出的危险首字符是 `=` `+` `-` `@` **以及 Tab(0x09)、CR(0x0D)、LF(0x0A)**，还包括部分**全角变体** | 导出的每一格都要过一遍前缀检查；但见下面的「两个都不能全信」 |
| 公式注入的两种修法 | ① 单引号前缀 `'`（OWASP 传统建议）；② 引号包裹 + 制表符前缀（**Excel-resistant**，但制表符会成为数据的一部分） | 两者都有代价：单引号在 Excel「另存再打开」后**可能被去掉**；制表符会污染下程序解析。本机实测：20,000 个字段里 **522 个（2.61%）** 以危险字符开头，其中包含「+86 手机号」与「-5% 折扣」——**逃逸会改坏正常数据** |
| 中文编码 | GB 18030-2022 为强制性国家标准，向下兼容 GBK/GB2312；UTF-8 无 BOM 是跨系统交换的事实默认 | 上传来的中文 CSV 有很大比例是 GBK。本机实测：GBK 字节流按 UTF-8 硬读，在**第 25 个字节**就抛 `UnicodeDecodeError`；带 BOM 的文件按 UTF-8 读，表头会变成 `'\ufeffid'`，按列名取值直接 `KeyError` |
| 数据库批量写 | PostgreSQL 的 `COPY`、MySQL 的 `LOAD DATA`、SQLite 的 `executemany` 都是「批越大越快、但事务越大回滚越贵」 | 实测 5 万行：批 100 / 1,000 / 10,000 → **289 / 89 / 62 ms**。批从 1,000 加到 10,000 只再快 1.4 倍，但一个坏行毁掉的行数从 1,000 变成 10,000 |
| 时间与日期 | ISO 8601 的 `YYYY-MM-DD` 无歧义；`MM/DD/YYYY` 与 `DD/MM/YYYY` 有歧义 | 本机枚举 1..12 月 × 1..12 日共 144 种写法，其中 **132 种（91.7%）** 两种解释都合法——同一个 `03/04/2026` 在不同地区差一个月 |

::: warning 两个「不能全信」
1. **不能全信文件的扩展名**：`.csv` 可能是 GBK、可能是 Excel 另存的 TSV、可能是带 BOM 的 UTF-8、也可能根本是 `.xls` 改了后缀。判断依据只能是**字节**（BOM、NUL 字节、ZIP 魔数 `PK\x03\x04`）。
2. **不能全信「成功」的返回值**：解析库返回 10,000 行不代表这 10,000 行都合法；数据库返回 10,000 行也不代表它们都是这次写进去的。判据必须落在**行数守恒**上，见[总览](Overview/index.md)的第七段。
:::

## 七个必失点（本专题的全部理由）

这七条不是「注意一下」，而是**结构性的**：只要实现里缺少对应的一条，数据就会安静地少下去。

1. **用 `split(',')` 解析**——含引号、逗号、换行的字段全部错列，本机 5,000 行错 3,724 行，且错列后**不报错**，只是金额进了备注列。见[解析与编码](ParsingAndEncoding/index.md)。
2. **编码按 UTF-8 硬读**——GBK 文件首行即崩（可修复），带 BOM 的文件则**不崩**，只是每一列的名字都多一个不可见字符，取值为空却一路写进库。见[解析与编码](ParsingAndEncoding/index.md)。
3. **整个文件一个事务**——1 条坏行让 5,000 行全部回滚（本机：入账 **0 行**）；反过来「逐行提交 + 回执说成功」则更糟。见[行级校验](RowValidation/index.md)。
4. **没有业务唯一键**——同一份 10,000 行导入两次，库里 **20,000 行**；有 `on conflict` 时仍是 10,000 行。见[幂等重跑](IdempotentRerun/index.md)。
5. **导出用 offset 分页 + 并发有写**——20,000 行导出期间删 20 条，**漏 20 行（0.1%）**且多读 20 条新行；按可变键排序则反过来**重复 20 行**。见[导出快照](ExportSnapshot/index.md)。
6. **全量载入内存 + 不设上传上限**——同一个 4.29 MB 文件，全量载入峰值 **27,556 KB**，流式只有 **62 KB**（约 444 倍）；而 20 MB 的全零文件压成 20,504 字节（**1,023:1**），一个 20 MB 的上传就能解出 20 GB。见[解析与编码](ParsingAndEncoding/index.md)。
7. **导出直接拼 CSV、不做前缀处理**——2.61% 的字段以 `=` `+` `-` `@` 开头；而简单加单引号会把 `+86 13800138000` 变成 `'+86...`。见[解析与编码](ParsingAndEncoding/index.md)。

## 为什么这里没有版本目录

本专题**不建 `v1/` `v2/` 这类版本目录**，理由三条：

1. **换代的是文件格式，不是判据**。从 CSV 到 Excel 到「JSON Lines 分片上传」，变的是承载容器；而「行号要能指回原文」「重跑不能翻倍」「导出必须是一份静止画面」这三类判据一字未变。
2. **并存差异是渠道，不是代际**。同一时期里，财务走 Excel、运营走 CSV、系统对系统走 SFTP 落地文件——它们是**三种渠道**，不是新旧版本。按版本建目录会把「渠道对照」拆成历史存档。
3. **可验证的差异已收敛进表格**。凡是有「两种做法」的地方（offset vs keyset、单引号 vs 制表符、整批 vs 分批事务），都用同一张表写清「什么时候用哪个、差多少」，并附本机读数。

作为对照，本库确实存在需要版本目录的主题：[Spring 5 / Spring 6](../Java/Frame/Spring/index.md)、[Vue 2 / Vue 3](../../Frontend/Frame/Vue/index.md)、[MySQL 5.7 / 8.4](../../DB/SchemaEvolution/index.md)——它们的共同点是**同一个产品的两代 API 不兼容且旧版仍在跑**，与本题不同。

## 三条底线

::: danger 三条不可让步的底线
1. **行数必须守恒**：`文件数据行数 = 成功入账行数 + 失败行数`，且失败行必须逐行出现在回执里。任何「大致导进来了」的说法都不算验收。本机实测：整批一个事务时一条坏行让入账变成 **0 行**，而作业状态仍然是成功——守恒式是唯一能抓住它的东西。见[行级校验](RowValidation/index.md)。
2. **重跑必须幂等，且幂等键落在业务键上**：`batch_no` 只保证「同一批不被建两次」，真正的「不重复入账」靠 `(业务唯一键)` 的 upsert。本机实测：无唯一键时 10,000 行导两次变 **20,000 行**。见[幂等重跑](IdempotentRerun/index.md)。
3. **导出必须能解释自己**：文件里要有快照时点、过滤条件、行数、生成人；否则对账时没人能区分「业务变了」和「导出时正在写」。本机实测：分页导出期间 20 条写入就足以造成 **0.1%** 的漏行或重复。见[导出快照](ExportSnapshot/index.md)。
:::

## 阅读顺序

先读[总览](Overview/index.md)拿到七段链与三个成功定义，然后按手上的问题选主线：

- **用户说「少了几行」** → [常见问题与分诊](FAQ/index.md) 的五行分诊表，再按指向跳
- **要设计导入模板、和业务对齐列** → [文件契约](FileContract/index.md)
- **文件一上传就报编码错 / 中文乱码** → [解析与编码](ParsingAndEncoding/index.md)
- **要决定「部分成功」还是「全成或全败」** → [行级校验](RowValidation/index.md)
- **重跑之后数据翻倍了** → [幂等重跑](IdempotentRerun/index.md)
- **导出的报表和系统里对不上** → [导出快照](ExportSnapshot/index.md)
- **作业卡在 99%、或者取消后还在写** → [异步作业](AsyncJob/index.md)
- **要从零搭一套能验收的最小链路** → [实战](Practice/index.md)，按 S1~S6 走

## 参考资料

- Microsoft《Excel specifications and limits》（1,048,576 行 × 16,384 列、单元格 32,767 字符、253 个换行）：<https://support.microsoft.com/en-us/office/excel-specifications-and-limits-1672b34d-7043-467e-8e27-269d656771c3>
- RFC 4180《Common Format and MIME Type for Comma-Separated Values (CSV) Files》：<https://www.rfc-editor.org/rfc/rfc4180>
- CWE-1236《Improper Neutralization of Formula Elements in a CSV File》：<https://cwe.mitre.org/data/definitions/1236.html>
- OWASP《CSV Injection》（危险首字符清单、两种缓解的取舍、Excel 另存后失效的行为）：<https://owasp.org/www-community/attacks/CSV_Injection>
- OWASP WSTG《Testing for CSV Injection》：<https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Injection/21-CSV_Injection>
- GB 18030-2022《信息技术 中文编码字符集》（强制性国家标准，向下兼容 GBK）：<https://openstd.samr.gov.cn/>
- PostgreSQL 18 文档《COPY》（服务端批量导入与服务端文件权限）：<https://www.postgresql.org/docs/18/sql-copy.html>
- MySQL 8.4 文档《LOAD DATA Statement》（`LOCAL`、`secure_file_priv`、字符集参数）：<https://dev.mysql.com/doc/refman/8.4/en/load-data.html>
- Python 文档《csv — CSV File Reading and Writing》（`field_size_limit`、`QUOTE_*`、`newline=''` 的作用）：<https://docs.python.org/3/library/csv.html>
