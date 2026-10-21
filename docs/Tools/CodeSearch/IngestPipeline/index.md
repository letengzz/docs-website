# 入库与解析：从文件到可检索的块

索引里的每一条记录都来自「某个文件的某一段字节」。这一层的工作是把「一个目录树」变成「一堆带坐标的块」，而它的每一个决定都会在查询侧以「搜不到」的形式出现——不是报错，是**少了一批本该命中的结果**。

本页按流水线顺序讲五个阶段，每个阶段都给出它在真实语料上的读数与失效形态。

::: tip 一句话理解
入库阶段的唯一目标：**让每一段可检索的文本都带上一组不会说谎的坐标**（文件 + 起止行 + 起止列 + 内容指纹）。坐标说谎，后面所有排序、跳转、增量都建立在假数据上。
:::

## 判据族声明

本页判据族 `CSG-A` ~ `CSG-H`，共 8 条。定义表在第六节。

## 本页不讲什么

- 不讲 n-gram 的粒度与体积换算，归[索引结构](../IndexStructure/index.md)。
- 不讲增量检测与删除后的孤儿 posting，归[增量更新](../IncrementalUpdate/index.md)。
- 不讲检索时的候选集与验真，归[查询规划](../QueryPlanning/index.md)。

## 一、五个阶段与它们各自的静默失效

![入库流水线的五个阶段与各自的失效点](../assets/cs-pipeline.svg)

| 阶段 | 输入 → 输出 | 关键决定 | 失效形态 | 判据 |
| --- | --- | --- | --- | --- |
| ① 枚举 | 目录树 → 文件列表 | 忽略规则、大小上限、二进制判定 | 少了一批文件（忽略规则写反） | `CSG-A` |
| ② 解码 | 字节 → 文本 | 编码、BOM、换行 | 整批中断，或静默丢字符 | `CSG-C` |
| ③ 分块 | 文本 → 块 + 坐标 | 按结构边界 / 按行 / 按固定窗口 | 边界切在标识符中间 | `CSG-D` |
| ④ 指纹 | 块 → 内容哈希 | sha1/sha256 vs `mtime+size` | 内容变了但指纹没变 | `CSG-E` |
| ⑤ 写入 | 块 → postings + 元数据 | 存原文还是存偏移 | 索引项无法还原原文 | `CSG-F` |

## 二、枚举：忽略规则是最容易写反的一行

枚举看起来只是 `os.walk`，但它决定了「语料是什么」。本仓实测的三条基线：

| 项 | 本仓读数 | 说明 |
| --- | --- | --- |
| Markdown 文件 | **2,406** | `docs/` + `project/` 下的 `*.md` |
| 总字节 | **15,679,054**（15.0 MiB） | 平均 6,517 B/篇 |
| 围栏代码块 | **约 16,841 个** | 按围栏标记计数后折半；占字节 **39.3%** |
| 行数 | **531,310** | 平均 221 行/篇 |
| 段落起点（空行后首个非缩进行） | **115,307** | 「按结构切块」时天然可用的边界 |

代码块占 **39.3%** 这件事很关键：代码搜索的语料里**四成是代码**，而代码块里的内容是**缩进敏感、换行敏感**的。任何「把连续空白折叠成一个空格」的归一化，都会让代码块里的缩进结构消失——所以归一化只能作用于**正文散文**，不能作用于代码块（判据 `CSG-G`）。

::: danger 忽略规则的三类经典错误
1. **把 `.gitignore` 当唯一真相**：`.gitignore` 的语义是「不追踪」，不是「不可检索」。构建产物目录（`dist/`）通常既被忽略、又确实不该搜；但 `node_modules` 被忽略后，你可能还是想搜依赖里的类型定义。**这两件事必须分两个列表**。
2. **忽略规则写成了「排除」而不是「跳过」**：`if "test" in path: continue` 会把 `latest/`、`contest/` 一起干掉。规则必须锚定路径段（`/test/`、`^\\.`），不能是子串。
3. **没有大小上限**：一个 800 MB 的 SQL dump 或 minified JS 进索引，会让构建时间与体积同时失控，而它在查询里几乎不可能被用到。实测本仓最大的单篇是 **87,340 B**——超过 1 MB 的文本文件就该单独决策（判据 `CSG-A`）。
:::

## 三、解码：失败要「记账」，不要「跳过」

本仓的实测结果很干净：**2,406 篇全部是合法 UTF-8，0 个 BOM，0 个 CRLF**。这不是普遍规律，而是因为仓库有 `.editorconfig` 与 CI 约束。读者自己的仓库几乎一定不是这样。

| 情形 | 常见处理 | 正确做法 |
| --- | --- | --- |
| 非 UTF-8（GBK / Latin-1） | `errors="ignore"` | `errors="replace"` **并记一条 `decode_failed` 计数**；忽略会让字静默消失 |
| 混合编码（一个文件里两种） | 整文件按一种解 | 按行试解，失败行降级为字节串并标记，不要整文件丢弃 |
| BOM | 当成内容 | 剥掉 BOM（否则第一行的第一个字符永远搜不到） |
| CRLF | 保留 | 归一为 `\n` 后再算坐标，否则列号在不同平台差 1 |
| 二进制伪装成 `.md` | 照常索引 | 前 8 KB 里出现 `\x00` 即判定二进制，跳过并计数 |

一个可执行的判据：**解码失败数必须出现在索引构建的摘要里**。构建日志只写「已索引 2,406 个文件」而不写「跳过 3 个、替换 12 个字符」，等于把这层失效藏起来了。

## 四、分块：边界决定前缀查询能不能用

「块」是可检索单元。三种切法在中文语料上的实测差异极大：

| 切法 | 块数（本仓） | 边界性质 | 前缀查询 | 备注 |
| --- | --- | --- | --- | --- |
| 固定窗口 500 字符 | **28,523** | **76.5% 的边界落在字/词中间** | 失效（`OutboxPub` 被切成两块） | 绝不能用于代码 |
| 固定窗口 1,000 字符 | 13,655 | 76.6% 落在中间 | 失效 | 同上 |
| 固定窗口 2,000 字符 | 6,258 | 76.5% 落在中间 | 失效 | 同上 |
| 按结构边界（标题 / 空行 / 围栏） | 约 **115,307** 个段落起点可用 | 全部落在结构边界上 | 正常 | 块偏小，需要合并 |
| 按符号（函数 / 类 / 标题） | 取决于语言解析器 | 全部落在符号边界 | 正常，且能做「符号内搜索」 | 需要 tree-sitter 级别的解析 |

::: warning 76.5% 这个数字不是巧合
中文没有空格，所以「固定窗口」的边界几乎必然落在某个词的内部——实测 500 / 1,000 / 2,000 三种窗口，切断率都是 **76.5%~76.6%**，几乎不随窗口大小变化。英文语料上这个比例会低得多（词间有空格），这也是「英文场景下固定窗口勉强能用」的原因。**在中文语料上，固定窗口切块是一个必然错误的默认值。**
:::

正确的做法是「结构边界优先 + 大小兜底」：

```python
# 结构边界切块（示意，只切到「段落 / 围栏 / 标题」这一层）
import re

BOUNDARY = re.compile(r"^(?:#{1,6} |```|\s*$)", re.M)

def chunk(text, max_chars=1200):
    """按结构边界切块；单块超过 max_chars 时退回按行切，绝不在行内切。"""
    cuts = [m.start() for m in BOUNDARY.finditer(text)] + [len(text)]
    blocks, start = [], 0
    for i in range(1, len(cuts)):
        if cuts[i] - start >= max_chars:
            blocks.append((start, cuts[i]))
            start = cuts[i]
    if start < len(text):
        blocks.append((start, len(text)))
    # 兜底：单块仍超长时按行切（行内不切，保证标识符完整）
    out = []
    for s, e in blocks:
        seg = text[s:e]
        if len(seg) <= max_chars * 2:
            out.append((s, e))
            continue
        pos = s
        for line in seg.splitlines(keepends=True):
            if pos - s >= max_chars:
                out.append((s, pos))
                s = pos
            pos += len(line)
        out.append((s, e))
    return out
```

这段代码的关键不在实现，在**它的失败方式**：它永远不在行内切，所以「前缀查询失效」这一类 bug 从结构上不可能发生。

## 五、中文与标识符：默认分词是一个静默的召回杀手

这是本页最重要的一组读数。同一份语料、同一个查询：

| 口径 | 查「幂等」的命中 | 说明 |
| --- | --- | --- |
| `text.split()`（空白分词） | **41** 篇 | 只有「幂等」恰好被空格/换行隔开时才命中 |
| 子串 / n-gram | **394** 篇 | 正确召回 |
| 差距 | **召回少 89.6%** | 而日志里没有任何错误 |

原因在词表本身：本仓 `split()` 得到 **515,711** 个不同的 token，其中含中文的有 **344,347** 个，**平均长度 16.8 字符、最长 512 字符**——也就是说，词表里绝大多数条目是「一整句话」，不是词。

所以代码搜索的正确默认是**「不分词」**：直接对归一化后的字符流建 n-gram，让「词」这个概念彻底消失。这也顺带解决了标识符问题——`OutboxPublisher` 在 n-gram 下就是一堆 3 字符片段，用户查 `boxPub` 照样命中。

| 语料类型 | 推荐 token 化 | 理由 |
| --- | --- | --- |
| 源码 / 配置 / 日志 | n-gram（n=3） | 标识符没有词边界，子串查询是常态 |
| 中文技术文档 | n-gram（n=2 与 3 双写） | 两字词占多数，3-gram 覆盖长串 |
| 纯英文自然语言 | 词项 + 前缀索引 | 体积最小，且 `ion` 这类高频词能靠 idf 压住 |
| 混合 | n-gram 为主，词项作辅助字段 | 兼顾召回与「词组匹配」的精确性 |

## 六、判据表

| 判据 | 断言 | 怎么验 |
| --- | --- | --- |
| `CSG-A` | 忽略规则锚定路径段而非子串，且有大小上限与二进制判定 | 造三个文件：`/test/a.md`（应跳过）、`/latest/b.md`（应索引）、`/big/c.md`（2 MB，应跳过并计数）；三条都符合 |
| `CSG-B` | 索引器的分词路径上不出现 `split()` / 空白分词 | `grep -rn "\.split()" src/index/` 无命中，或命中处有注释说明「这是按行切，不是分词」 |
| `CSG-C` | 解码失败与替换字符的数量出现在构建摘要里 | 构建日志有 `decode_failed=N replaced_chars=M skipped=K` 三个计数 |
| `CSG-D` | 分块边界只落在结构边界（标题/空行/围栏/行尾），不在行内 | 取任意块的首尾字符，都是 `\n` 或块首；随机抽 100 块检查，行内切断数为 0 |
| `CSG-E` | 内容指纹是内容哈希，不是 `mtime+size` | 把文件内容改一个字符但保持字节数不变、并用 `touch -r` 还原 mtime，索引应检测到变更 |
| `CSG-F` | 索引项能还原原文（存原文或 `(doc_id, offset, len)`），不需要回读全文件 | 从任意结果项取 20 字符上下文，与原文对应位置逐字节相同 |
| `CSG-G` | 归一化只作用于散文，不折叠代码块内的空白与缩进 | 取一个含缩进的代码块建索引，命中的片段里缩进仍然存在 |
| `CSG-H` | 入库有「总数对账」：枚举数 = 索引数 + 跳过数（且跳过原因分类计数） | 构建摘要满足 `enumerated == indexed + skipped`，且 `skipped` 按原因分桶 |

## 七、如何验证

```shell
# 1) 语料基线：文件数、字节、代码块占比（这三个数决定后面的所有预算）
python3 - <<'PY'
import os
docs = {}
for base in ("docs", "project"):
    for dp, _, fs in os.walk(base):
        for f in fs:
            if f.endswith(".md"):
                p = os.path.join(dp, f)
                docs[p] = open(p, encoding="utf-8", errors="replace").read()
total = sum(len(t) for t in docs.values())
incode = sum(len(part) for t in docs.values() for i, part in enumerate(t.split("```")) if i % 2)
print("files=%d bytes=%d code_ratio=%.1f%%" % (len(docs), total, 100 * incode / total))
PY
# 期望：files=2406 bytes=15679054 code_ratio=39.3%
# 判读：四成字节在围栏代码块里 —— 归一化不能折叠代码块空白（CSG-G）
```

```shell
# 2) 固定窗口切块的边界切断率：证明「窗口不是切块单位」
python3 - <<'PY'
import os
docs = {}
for base in ("docs", "project"):
    for dp, _, fs in os.walk(base):
        for f in fs:
            if f.endswith(".md"):
                p = os.path.join(dp, f)
                docs[p] = open(p, encoding="utf-8", errors="replace").read()
for W in (500, 1000, 2000):
    cut = tot = 0
    for t in docs.values():
        s = " ".join(t.split())
        for i in range(W, len(s), W):
            tot += 1
            if s[i - 1] not in " \n" and s[i] not in " \n":
                cut += 1
    print("window=%d chunks=%d cut_in_word=%d (%.1f%%)" % (W, tot, cut, 100 * cut / tot))
PY
# 期望：window=500  chunks=28523 cut≈21810 (76.5%)
#       window=1000 chunks=13655 cut≈10466 (76.6%)
#       window=2000 chunks=6258  cut≈4786  (76.5%)
# 判读：切断率不随窗口变化 —— 中文没有空格可对齐，窗口切块必然切在词内
```

```shell
# 3) 编码体检：三类「静默丢字符」的入口
python3 - <<'PY'
import os
bad = bom = crlf = big = 0
for base in ("docs", "project"):
    for dp, _, fs in os.walk(base):
        for f in fs:
            if not f.endswith(".md"):
                continue
            b = open(os.path.join(dp, f), "rb").read()
            try:
                b.decode("utf-8")
            except UnicodeDecodeError:
                bad += 1
            bom += b.startswith(b"\xef\xbb\xbf")
            crlf += b"\r\n" in b
            big += len(b) > 1 << 20
print("bad_utf8=%d bom=%d crlf=%d over_1MiB=%d" % (bad, bom, crlf, big))
PY
# 期望（本仓）：bad_utf8=0 bom=0 crlf=0 over_1MiB=0
# 判读：全 0 是仓库纪律的结果，不是普遍规律；读者仓库应把这三个数写进构建摘要（CSG-C）
```

## 参考资料

- Python `bytes.decode` 的 `errors` 策略（`strict` / `replace` / `ignore` 的差异）：<https://docs.python.org/3/library/codecs.html#error-handlers>
- `.gitignore` 模式语法（路径段锚定与子串的区别）：<https://git-scm.com/docs/gitignore#_pattern_format>
- tree-sitter（按符号切块的主流解析器）：<https://tree-sitter.github.io/tree-sitter/>
- Unicode 规范化形式（NFC/NFKC 对全角字符的处理）：<https://unicode.org/reports/tr15/>
- zoekt 的文档切分与行号维护：<https://github.com/sourcegraph/zoekt/blob/main/doc/design.md>
- 本仓相邻专题：[全文检索系统的索引更新](../../../DB/FullTextSearch/IndexUpdate/index.md) · [RAG 的切块策略](../../../AI/RAG/Chunking/index.md)
