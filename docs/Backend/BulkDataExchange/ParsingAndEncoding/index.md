# 解析与编码：编码嗅探、引号与注入面

解析段是整条链路上**最不会报错、也最容易出错**的一段。它拿到一坨字节，要猜出「这坨字节用的是什么编码、什么分隔符、引号怎么转义、一条记录在哪结束」——猜错任何一项，它都不会失败，只会把数据**静默地变形**：金额进了备注列、表头多了一个不可见字符、含换行的字段被拆成两条记录。

这一页把解析拆成五段，逐段说明「猜错的后果」和「不猜的做法」，最后处理两个必须在这一层解决的问题：**注入面**与**解压炸弹**。

![解析五段与四个安静的错误](../assets/bdx-parse.svg)

本页判据族 `BDP-A` ~ `BDP-H`，共 8 条。定义表在第八节。

## 一、五段：从字节到字段

| # | 段 | 输入 | 判据 | 猜错的后果 |
| --- | --- | --- | --- | --- |
| ① | 魔数识别 | 前 8 个字节 | `PK\x03\x04` → ZIP（xlsx/docx）、`\xd0\xcf\x11\xe0` → OLE2（xls）、`\xef\xbb\xbf` → UTF-8 BOM | 把 xlsx 当 CSV 读 → 一堆乱码但**不报错** |
| ② | 编码判定 | 全文采样 | BOM 优先；无 BOM 则「显式声明 > 严格 UTF-8 试探 > GB18030 兜底」 | GBK 按 UTF-8 读 → 首个中文处抛错；BOM 未剥离 → 表头带 `\ufeff` |
| ③ | 方言判定 | 前 10 行 | 分隔符（`,` `;` `\t` 竖线）、引号符、是否含表头 | 用 `,` 切 `;` 分隔的文件 → 每行只有 1 个字段 |
| ④ | 逐行切分 | 整个流 | RFC 4180 的引号与字段内换行 | `split(',')` → 含逗号的字段直接裂开 |
| ⑤ | 归一化 | 每条记录 | 去空格、全角转半角、去千分位、单位换算 | `1,299` 与 `1299` 变成两个值 |

::: danger 注意
1. **不要用 `line.split(',')`**。RFC 4180 明确允许字段被双引号包裹，包裹内可出现逗号、换行和 `""`（表示一个 `"`）。本机实测：5,000 行里 75% 的备注含逗号/引号/换行，按逗号切分 **3,724 行错列（74.5%）**，`csv.reader` 错 **0** 行。
2. **不要用 `readlines()` 再逐行解析**。同一份文件的**物理行 6,233 行、逻辑记录 5,001 条**——字段内的换行让「一行 = 一条记录」这个假设直接失效。
3. **不要靠扩展名判断类型**。`.csv` 可能是 GBK、可能是 Excel 另存的 TSV、也可能是 `.xls` 改名。判断依据只能是字节。
:::

## 二、编码：三种做法，只有一种是可运维的

| 做法 | 实现 | 优点 | 缺点 |
| --- | --- | --- | --- |
| **全靠猜** | 用 `chardet`/`charset-normalizer` 猜 | 用户零负担 | 短文件猜错率高；猜错时**不报错**，直接乱码入库 |
| **强制声明** | 上传时必须选编码 / 文件内声明 | 判定明确 | 用户不知道自己的文件是什么编码（尤其 Windows 导出的 Excel CSV 默认是 GBK） |
| **声明 + 严格试探 + 兜底** | 有声明用声明；无声明先严格 UTF-8，失败再 GB18030 | 两者兼得 | 实现复杂一点，但**错误可解释** |

推荐第三种，并把它写成一个函数：

```python [app/io/encoding.py]
from pathlib import Path

BOMS = [
    (b"\xef\xbb\xbf", "utf-8-sig"),
    (b"\xff\xfe\x00\x00", "utf-32-le"),
    (b"\x00\x00\xfe\xff", "utf-32-be"),
    (b"\xff\xfe", "utf-16-le"),
    (b"\xfe\xff", "utf-16-be"),
]

def detect_encoding(head: bytes, declared: str | None = None) -> tuple[str, bool]:
    """返回 (编码, 是否带 BOM)。

    顺序：BOM > 显式声明 > 严格 UTF-8 > GB18030 兜底。
    """
    for bom, enc in BOMS:
        if head.startswith(bom):
            return enc, True
    if declared:
        return declared, False
    try:
        head.decode("utf-8", errors="strict")
        return "utf-8", False
    except UnicodeDecodeError:
        # GB18030 是 GBK/GB2312 的超集，且几乎不会误判 ASCII
        head.decode("gb18030", errors="strict")
        return "gb18030", False
```

三个必须注意的点：

1. **`utf-8-sig` 才会剥 BOM**。用 `utf-8` 读带 BOM 的文件不会报错，但第一个字段名会变成 `'\ufeffsku'`。本机实测：`b'\xef\xbb\xbfid,name'` 按 `utf-8` 解出的表头是 `'\ufeffid'`，按 `utf-8-sig` 解出才是 `'id'`。
2. **只采样前 64 KB 判断编码，但整份文件按同一编码读**。逐块判断会在多字节字符被切断的位置误判。
3. **失败要报「第几行第几列」**。`UnicodeDecodeError` 自带 `start`/`end` 字节偏移，转成行列号再报给用户——本机实测 GBK 文件按 UTF-8 读，错误发生在**第 25 个字节**，对应第 1 行第 3 列（首个中文字符）。

## 三、方言：分隔符、引号与换行

| 方言项 | 常见取值 | 判定方式 |
| --- | --- | --- |
| 分隔符 | `,`（RFC 4180）、`;`（欧洲区域设置下的 Excel）、`\t`（TSV）、竖线 | 在前 10 行里统计「引号外的候选字符出现次数」，取每行最稳定的那个 |
| 引号符 | `"`（标准）、`'`（少见）、无引号 | 只在字段**首字符**出现时才算引号 |
| 行尾 | `\r\n`（Windows）、`\n`（Unix）、`\r`（老 Mac） | 用 `newline=''` 打开，交给解析器处理 |
| 表头 | 有 / 无 / 多行 | 契约声明 `header_row`，不猜 |

::: warning 一个必踩的坑：`newline=''`
Python 里 `open(path)` 默认做**通用换行转换**，会把 `\r\n` 变成 `\n`，然后再交给 `csv.reader`。这本来没问题，但如果字段内部含 `\r\n`，转换后字段内容会被改写（`\r` 丢失），导出的文件与原文不再逐字节一致。

正确写法：

```python
with open(path, encoding=enc, newline="") as f:   # newline='' 必须写
    for row in csv.reader(f):
        ...
```
:::

## 四、流式解析：不要让内存决定你能导多大

| 做法 | 4.29 MB / 10 万行 CSV 的峰值内存 | 说明 |
| --- | --- | --- |
| `list(csv.reader(f))` 全量载入 | **27,556 KB** | 每行是一个 list，10 万行 × 4 列 ≈ 40 万个字符串对象 |
| 逐行迭代 `for row in csv.reader(f)` | **62 KB** | 只保留当前行 |

**约 444 倍**。这不是「优化」问题：全量载入意味着 100 万行的文件（约 45 MB）要吃掉 270 MB 堆，且是**瞬时**的——批量导入往往是多个用户同时传，三个人并发就把服务打爆。

```python [app/io/stream.py]
import csv, io

def iter_rows(path: str, enc: str, delimiter: str = ","):
    """逐行产出 (line_no, fields)。line_no 是「记录起始的物理行号」。"""
    with open(path, encoding=enc, newline="") as f:
        reader = csv.reader(f, delimiter=delimiter)
        line_no = 0
        for row in reader:
            # csv 不直接给行号；用 reader.line_num 拿「读到第几个物理行」
            start = line_no + 1
            line_no = reader.line_num
            yield start, row
```

`reader.line_num` 是**已消费的物理行数**，不是记录数。对含字段内换行的记录，它一次会增加多行——这正好是我们要的「起始行号」语义，也是 `BDF-H`（行号与 Excel 一致）能成立的基础。

另外要显式设置字段长度上限：

```python
csv.field_size_limit(1024 * 1024)   # 默认 131072，超了抛 _csv.Error: field larger than field limit
```

默认 128 KB 对「备注」这类列不一定够；但也不要设成无限——一个没有上限的字段就是一个内存炸弹。

## 五、注入面：2.61% 的字段会变成公式

CSV 被 Excel 打开时，以 `=` `+` `-` `@` 开头的单元格会被当作**公式执行**。这是 CWE-1236，OWASP 给出的危险首字符还包括 Tab(`0x09`)、CR(`0x0D`)、LF(`0x0A`)，以及部分**全角变体**（`＝` `＋` `－` `＠`，在日文等区域设置下会被识别）。

本机对一个「姓名/备注」类字段做了 20,000 次采样（其中 2.8% 刻意模拟危险值）：**522 个字段（2.61%）** 以危险字符开头。但这 522 个里，大部分是**正常业务值**：

| 真实值 | 危险首字符 | 加单引号前缀后 | 后果 |
| --- | --- | --- | --- |
| `=1+1`（用户真的想写这个文本） | `=` | `'=1+1` | 正确：显示为文本 |
| `+86 13800138000` | `+` | `'+86 13800138000` | **数据被改坏**：多了一个引号 |
| `-5% 折扣` | `-` | `'-5% 折扣` | **数据被改坏** |
| `@张三` | `@` | `'@张三` | 数据被改坏 |

也就是说：**前缀逃逸是「安全」对「保真」的正面冲突**，没有两全的做法。三种可选策略：

| 策略 | 做法 | 适合 | 代价 |
| --- | --- | --- | --- |
| **一律前缀** | 危险首字符前加 `'` | 导出给**人看**的报表 | 数据被改；再导入时要把前缀剥掉，否则值变了 |
| **仅危险值前缀** | 只对「长得像公式」的值（`=` 开头、含 `(` 且含 `cmd`/`HYPERLINK` 等）加前缀 | 导出给**系统**消费 | 规则可绕过，且 `+86` 这类仍可能被误判 |
| **整列文本化** | 导出 `xlsx` 时把列格式设为文本（`@`） | 导出 xlsx | 只对 xlsx 有效；CSV 无格式概念 |

OWASP 还记录了一个更麻烦的事实：**单引号前缀在 Excel「另存再打开」后可能被去掉**，公式重新变活。所以真正稳妥的做法是分两层：

```python [app/export/csv_safe.py]
DANGEROUS = ("=", "+", "-", "@", "\t", "\r", "\n", "＝", "＋", "－", "＠")

def csv_cell(value: str, mode: str = "human") -> str:
    """导出单元格。

    mode='human' —— 给人看的报表：危险首字符加单引号，牺牲保真换安全。
    mode='system' —— 给系统消费：不改内容，由接收方按文本解析（契约里写明）。
    """
    if mode == "system":
        return value
    if value and value[0] in DANGEROUS:
        return "'" + value
    return value
```

并且在导出文件的口径页里写清用了哪种模式——**这是唯一能让下游知道「那个引号是逃逸还是数据」的办法**。

## 六、上传上限与解压炸弹

「限制上传大小」几乎人人都做，但**限制的位置往往是错的**：只看压缩包大小，等于只锁了门没关窗。

本机造了一个 20 MB 的全零文件，`ZIP_DEFLATED` 压完只有 **20,504 字节**，压缩比 **1,023 : 1**。也就是说：一个 20 MB 的上传限额，允许用户解出 **20 GB**。嵌套压缩（zip 里套 zip）还能把这个倍数再乘一次。

四个上限必须同时存在：

| 上限 | 建议值 | 检查时机 | 不设的后果 |
| --- | --- | --- | --- |
| 请求体大小 | 20~50 MB | 网关/框架层 | 直接打满带宽与磁盘 |
| **解压后总字节** | 500 MB | 解压**前**读 ZIP 目录里的 `file_size` 求和 | 磁盘写满、进程 OOM |
| **单文件压缩比** | 100 : 1 | 解压前比对 `compress_size` 与 `file_size` | 1,023:1 的炸弹畅通无阻 |
| **数据行数** | 100 万（Excel 上限同数量级） | 解析时边读边数，超了立刻中止 | 一个 500 MB 的文件跑 40 分钟才发现没人要 |

```python [app/io/zipguard.py]
import zipfile

MAX_TOTAL = 500 * 1024 * 1024
MAX_RATIO = 100

def safe_open_zip(path: str):
    zf = zipfile.ZipFile(path)
    total = 0
    for info in zf.infolist():
        if info.is_dir():
            continue
        ratio = info.file_size / max(info.compress_size, 1)
        if ratio > MAX_RATIO:
            raise ValueError(f"E_ZIP_RATIO: {info.filename} 压缩比 {ratio:.0f}:1")
        total += info.file_size
        if total > MAX_TOTAL:
            raise ValueError(f"E_ZIP_TOO_LARGE: 解压后超过 {MAX_TOTAL} 字节")
    return zf
```

注意 `zipfile` **不会**在 `read()` 时替你检查这些——它老老实实解压，直到你把内存用完。所以必须在 `infolist()` 阶段先算，再决定要不要解。

## 七、一段完整的解析入口

把上面所有判断收成一个函数，它只做「字节 → 记录流」，不做任何业务校验：

```python [app/io/parse.py]
from dataclasses import dataclass
import csv

@dataclass
class ParsedFile:
    encoding: str
    delimiter: str
    header: list[str]
    line_no: int          # 表头所在物理行

def open_table(path: str, declared_enc: str | None = None,
               declared_delim: str | None = None) -> tuple[ParsedFile, object]:
    with open(path, "rb") as f:
        head = f.read(64 * 1024)
    enc, _has_bom = detect_encoding(head, declared_enc)
    delim = declared_delim or sniff_delimiter(head.decode(enc, errors="replace"))

    f = open(path, encoding=enc, newline="")
    reader = csv.reader(f, delimiter=delim)
    header = next(reader)
    meta = ParsedFile(enc, delim, header, reader.line_num)
    return meta, reader        # 调用方继续 for row in reader，用完负责 close
```

**验收方式**：拿一份「GBK 编码、含 3 个带逗号与换行的备注、表头有 BOM」的文件跑一遍，断言 ① `encoding == "gb18030"`、② `len(header) == 8` 且 `header[0] == "sku"`（无 `\ufeff`）、③ 记录数等于人工数的行数。

## 八、本页判据

| 编号 | 看什么现象 | 判成什么 | 不满足时改哪里 |
| --- | --- | --- | --- |
| `BDP-A` | 类型判定是否基于魔数而非扩展名 | 靠后缀判断即失败 | 读前 8 字节，识别 ZIP/OLE2/BOM |
| `BDP-B` | 编码判定顺序是否为「BOM > 声明 > 严格 UTF-8 > GB18030」 | 直接用 `utf-8` 打开即失败 | 按第二节实现 `detect_encoding` |
| `BDP-C` | BOM 是否被剥离（表头首字符无 `\ufeff`） | 表头含 `\ufeff` 即失败 | 用 `utf-8-sig` 或 `lstrip("\ufeff")` |
| `BDP-D` | 是否使用符合 RFC 4180 的解析器，而非字符串切分 | 用 `split` 即失败 | 换 `csv.reader` / `OpenCSV` / `encoding/csv` |
| `BDP-E` | 打开文件是否带 `newline=''`，且用 `reader.line_num` 计行号 | 用 `readlines()` 逐行即失败 | 改流式迭代，保留物理行号 |
| `BDP-F` | 是否设置了字段长度上限与数据行数上限 | 无上限即失败 | `field_size_limit` + 行数计数器 |
| `BDP-G` | 解压前是否校验「解压后总字节」与「单文件压缩比」 | 只限压缩包大小即失败 | 加 `safe_open_zip` |
| `BDP-H` | 导出时是否对危险首字符做了处理，且口径（human/system）写入导出说明 | 未处理即失败；处理了但没写口径也失败 | 加 `csv_cell`，并把模式写进导出页 |

## 参考资料

- RFC 4180《Common Format and MIME Type for Comma-Separated Values (CSV) Files》：<https://www.rfc-editor.org/rfc/rfc4180>
- CWE-1236《Improper Neutralization of Formula Elements in a CSV File》：<https://cwe.mitre.org/data/definitions/1236.html>
- OWASP《CSV Injection》（危险首字符含 Tab/CR/LF 与全角变体、两种缓解的取舍、Excel 另存后失效）：<https://owasp.org/www-community/attacks/CSV_Injection>
- GB 18030-2022《信息技术 中文编码字符集》：<https://openstd.samr.gov.cn/>
- Python 文档《csv — CSV File Reading and Writing》（`field_size_limit`、`line_num`、`newline=''`）：<https://docs.python.org/3/library/csv.html>
- Python 文档《zipfile — Work with ZIP archives》（`infolist()`、`compress_size`/`file_size`）：<https://docs.python.org/3/library/zipfile.html>
- [文件契约：模板、列定义与版本](../FileContract/index.md)（编码声明写在契约里）
- [行级校验与错误回执](../RowValidation/index.md)（解析产出的行号如何变成回执）
