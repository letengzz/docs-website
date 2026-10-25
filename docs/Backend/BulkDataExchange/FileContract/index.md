# 文件契约：模板、列定义与版本

批量导入的第一次事故，几乎都发生在**「我以为的列」和「他填的列」不是同一列**的时候。文件契约就是把这件事写死：哪一列、什么类型、能不能空、单位是什么、日期怎么写、表头长什么样、版本怎么判定。它不是「文件格式说明」，而是**双方都要遵守的接口**——和 REST 的接口契约一样，改它要走评审。

这一页给一套可以直接抄进项目的契约结构，并说明每一处「看起来无所谓」的约定会在哪里爆掉。

![文件契约的三个版本与四条列定义](../assets/bdx-contract.svg)

本页判据族 `BDF-A` ~ `BDF-H`，共 8 条。定义表在第八节。

## 一、契约的五个组成部分

| 组成 | 回答什么 | 缺了会怎样 |
| --- | --- | --- |
| **版本标识** | 这份文件按哪一版规则解释 | 新模板的列被旧代码按位置读，字段整体错位 |
| **列定义** | 每列的名称、类型、必填、归一化规则 | 「12元」这种值被当数字解析失败，或更糟：被截成 12 |
| **表头形式** | 第几行是表头、是否允许别名、是否允许乱序 | 用户删了一列备注，后面所有列前移一位 |
| **行号语义** | 「第几行」指文件行还是记录序号 | 回执让用户改「第 58 行」，他去改了第 58 条记录 |
| **拒绝规则** | 哪些情况整份文件不收 | 半份错文件被收下，产生一批半正确数据 |

::: tip 一句话理解
契约的作用不是「让文件能被读进来」，而是**让「读不进来」这件事有明确、可解释、可批量执行的理由**。
:::

## 二、版本：靠标记判定，不靠文件名

文件名里的 `v2`、`final`、`最终版`、`最终版(1)` 都不是版本。版本必须写在**文件内容里**，且能被机器一眼判定：

```csv [orders_20261025.csv]
# template_version=3
sku,name,price,currency,on_sale,effective_date
SKU-0001,保温杯,89.00,CNY,true,2026-11-01
```

三条硬规矩：

1. **版本标记必须是文件的第一行**（注释行或专用列 `__version`），且**不允许**出现在表头之后——表头之后的标记会被当成数据。
2. **没有标记 = v1**，按 v1 处理；v1 已停用时**直接拒绝**并给出迁移指引，不要「尽力兼容」。
3. **未知版本拒绝**，不允许「按最新版猜着读」——猜对了没人感谢，猜错了是一批脏数据。

| 版本状态 | 处理方式 | 用户看到的 |
| --- | --- | --- |
| 当前版（v3） | 正常导入 | 无提示 |
| 存量版（v2） | 接受，批次上标 `template=v2`，回执里提示「建议升级模板」 | 黄色提示 |
| 停用版（v1） | **拒绝**，整份不收 | 错误码 `E_TEMPLATE_RETIRED` + 下载新模板链接 |
| 未知版本 | **拒绝** | 错误码 `E_TEMPLATE_UNKNOWN` |

## 三、列定义的八个要素

一列的定义必须能回答八个问题，少一个就会在某次数据里翻车：

| 要素 | 示例 | 不写会怎样 |
| --- | --- | --- |
| 名称（`name`） | `price` | 只能按位置读，插一列就全错位 |
| 中文名（`label`） | 单价 | 回执只能报 `price`，业务看不懂 |
| 类型（`type`） | `decimal(12,2)` | 「待定」「暂无」被塞进金额列 |
| 必填（`required`） | `true` | 空值一路流到下游，在报表里变成 0 |
| 唯一（`unique`） | `true`（`sku`） | 同一 SKU 两行，谁生效取决于写入顺序 |
| 归一化（`normalize`） | `trim`、全角转半角、去千分位 | `1,299.00` 与 `1299` 被当成两个值 |
| 单位（`unit`） | `CNY` / `cent` / `kg` | v1 用「分」、v3 用「元」，差 100 倍 |
| 枚举（`enum`） | `on_sale ∈ {true,false,1,0,是,否}` | 「是/否」被写成字符串存进布尔列 |

一份可直接落地的契约（YAML 形式，存在代码库里、随版本走）：

```yaml [contracts/product_price.v3.yaml]
version: 3
template: 商品价目表
header_row: 2                # 第 1 行是版本注释，第 2 行是表头
allow_extra_columns: false   # 多出的列 -> 拒绝（默认），见第五节
columns:
  - name: sku
    label: 商品编码
    type: string
    required: true
    unique: true
    normalize: [trim, upper]
  - name: name
    label: 商品名称
    type: string
    required: true
    max_length: 120
    normalize: [trim, fullwidth_to_halfwidth]
  - name: price
    label: 单价
    type: decimal(12,2)
    required: true
    unit: CNY
    min: 0
    normalize: [trim, strip_thousands_sep]
  - name: currency
    label: 币种
    type: string
    required: true
    enum: [CNY, USD, HKD]
  - name: on_sale
    label: 是否在售
    type: boolean
    required: false
    default: true
    enum_map: { "是": true, "否": false, "1": true, "0": false }
  - name: effective_date
    label: 生效日期
    type: date
    required: true
    format: "%Y-%m-%d"       # 只认 ISO 8601，见第四节
```

## 四、三个最容易含糊的类型

### 4.1 金额：单位与精度必须写在列定义里

「单价」这三个字不含信息。必须写清三件事：**币种、最小单位、小数位**。

| 写法 | 存储值 | 读出来 | 结论 |
| --- | --- | --- | --- |
| `unit: CNY, type: decimal(12,2)` | `8900`（分）或 `89.00`（元） | 依赖实现 | 必须把「存分还是存元」写进契约 |
| `unit: cent` | `8900` | 89.00 元 | 明确，但要求导出时也按分 |
| `type: float` | `89.0` | 可能 `88.99999999999999` | **禁止**：浮点不能表示 0.1 |

::: danger 注意
1. **不要用 `float` 接金额**。`0.1 + 0.2 != 0.3` 不是理论问题：批量导入几万行后做汇总，差额会稳定出现，且每次都差在不同的行上，极难排查。
2. **不要让「元/分」混在一列里**。v1 模板用「分」、v3 用「元」，如果代码里靠 `if version >= 3` 临时换算，那么任何一次版本判断失误都会产生 100 倍误差，而且**看起来完全正常**（数字都是整数）。
3. **不要在导入时四舍五入**。`1.005` 按 `HALF_UP` 是 `1.01`、按 `HALF_EVEN` 是 `1.00`；导入阶段只做「解析」，舍入属于业务计算，应在同一处统一处理。
:::

### 4.2 日期：只认 ISO 8601，其余全部拒绝

本机枚举 `日/月` 的 1..12 × 1..12 共 144 种组合，其中 **132 种（91.7%）** 在「月/日」和「日/月」两种解释下都合法。也就是说：`03/04/2026` 到底是 3 月 4 日还是 4 月 3 日，**文件本身无法回答**。

所以契约里只留一种写法：

```text
effective_date: 2026-11-01     ✅
2026/11/01                     ❌ 拒绝（E_DATE_FORMAT）
01/11/2026                     ❌ 拒绝（歧义，不给「猜」的机会）
2026-11-01T00:00:00+08:00      ⚠️ 允许，但截断为日期并记录原始值
```

拒绝 > 猜测。猜错一个日期，代价是一整批价格提前或推迟一个月生效。

### 4.3 布尔与枚举：把「人的写法」映射进来，但只映射已知的

`是/否`、`Y/N`、`1/0`、`true/false`、`√/×` 都会出现。做法是**在契约里显式列 `enum_map`**，而不是在代码里 `if v in ("是","Y","1")` 硬编码——后者迟早会漏掉一个方言，然后那一列整批变成 `false`。

```python [app/contract/enum_map.py]
BOOL_MAP = {
    "true": True, "false": False,
    "1": True, "0": False,
    "是": True, "否": False,
    "y": True, "n": False,
    "√": True, "×": False,
}

def to_bool(raw: str) -> bool | None:
    """未知写法返回 None（由校验层报 E_ENUM），不要默认 False。"""
    return BOOL_MAP.get(raw.strip().lower())
```

返回 `None` 而不是 `False` 是关键：`False` 是一个**合法业务值**，用它表示「解析失败」会让「用户填了不认识的值」和「用户填了否」永远分不开。

## 五、表头匹配：三种策略与各自的代价

| 策略 | 规则 | 优点 | 代价 |
| --- | --- | --- | --- |
| **严格按名** | 表头必须与契约完全一致（顺序可变） | 最安全，插列不影响 | 用户改一个字（`单价` → `商品单价`）就整份拒绝 |
| **别名映射** | 契约里为每列配别名列表 | 容错好 | 别名表会无限膨胀，且两个别名指向同一列时结果取决于遍历顺序 |
| **按位置** | 第 N 列就是第 N 个字段 | 实现最简单 | 用户删一列，后面全部错位——**这是最危险的一种** |

推荐组合：**严格按名为主 + 少量别名 + 明确拒绝未知列**。

```python [app/contract/header.py]
def match_header(header: list[str], contract) -> dict[str, int]:
    norm = [h.strip().lstrip("\ufeff").lower() for h in header]
    idx: dict[str, int] = {}
    unknown: list[str] = []
    for i, h in enumerate(norm):
        hit = contract.by_name_or_alias(h)
        if hit is None:
            unknown.append(header[i])
            continue
        if hit.name in idx:
            raise ContractError("E_HEADER_DUP", f"列 {hit.label} 重复出现")
        idx[hit.name] = i
    missing = [c.label for c in contract.required if c.name not in idx]
    if missing:
        raise ContractError("E_HEADER_MISSING", f"缺少必填列：{missing}")
    if unknown and not contract.allow_extra_columns:
        raise ContractError("E_HEADER_UNKNOWN", f"存在未知列：{unknown}")
    return idx
```

注意 `lstrip("\ufeff")`：这一行看起来多余，实际上是**唯一能救 BOM 文件的地方**。带 BOM 的 UTF-8 文件，第一个表头是 `'\ufeffsku'`，不剥离就永远匹配不上，而报错信息里显示的是 `sku`——排查时会怀疑人生。见[解析与编码](../ParsingAndEncoding/index.md)。

## 六、行号语义：一份回执能不能用，全看这一条

「第 58 行有错」这句话有两种解释，而它们经常不是同一行：

| 口径 | 定义 | 用户在 Excel 里看到的位置 |
| --- | --- | --- |
| **文件行号**（`line_no`） | 从文件第 1 行（含注释与表头）算起 | 与 Excel 左侧行号一致 ✅ |
| **记录序号**（`row_no`） | 只数数据行，从 1 开始 | 需要加 2（注释 + 表头）才能对上 |
| **字段内换行导致的物理行** | 一条记录可能占多个物理行 | 直接对不上 ❌ |

**约定：回执一律用 `line_no`（文件行号）**，并在回执表头写清「本行号与 Excel 左侧行号一致；若单元格内含换行，以该记录**起始行**为准」。这一句注释能省掉大量「我第 58 行是空的啊」的工单。

## 七、拒绝规则的三种情况

| 情况 | 错误码 | 为什么必须整份拒绝 |
| --- | --- | --- |
| 版本未知 / 已停用 | `E_TEMPLATE_UNKNOWN` / `E_TEMPLATE_RETIRED` | 列语义可能完全不同，逐行校验也救不回来 |
| 列数不符 / 缺必填列 | `E_HEADER_MISSING` | 缺失列会让后面所有行都缺同一个值，逐行报错等于刷屏 |
| 存在未知列 | `E_HEADER_UNKNOWN` | 用户以为「备注3」会被导入，实际被丢弃；默默丢列比报错更危险 |

其余情况（类型错、枚举错、引用不存在）**一律按行处理**，进回执，不整份拒绝——见[行级校验](../RowValidation/index.md)。

## 八、本页判据

| 编号 | 看什么现象 | 判成什么 | 不满足时改哪里 |
| --- | --- | --- | --- |
| `BDF-A` | 文件内是否有可被机器判定的版本标记 | 只靠文件名/靠人工确认即失败 | 首行加 `# template_version=N` |
| `BDF-B` | 未知版本是否被拒绝 | 「按最新版猜着读」即失败 | 加白名单，未知即 `E_TEMPLATE_UNKNOWN` |
| `BDF-C` | 每一列是否声明类型、必填、归一化、单位 | 缺任一要素即失败 | 补 YAML 契约，代码从契约生成校验器 |
| `BDF-D` | 金额列是否明确「分/元」与小数位，且未使用浮点 | 使用 `float`/`double` 即失败 | 改 `decimal` 或整数分 |
| `BDF-E` | 日期列是否只接受 ISO 8601 | 接受 `MM/DD/YYYY` 即失败 | 只放行 `%Y-%m-%d`，其余报 `E_DATE_FORMAT` |
| `BDF-F` | 表头匹配是否按名（而非按位置），且剥离 BOM | 按位置读取即失败 | 改为按名 + 别名，`lstrip("\ufeff")` |
| `BDF-G` | 未知列是否被拒绝（或至少被显式忽略并在回执说明） | 静默丢弃即失败 | `allow_extra_columns: false`，报 `E_HEADER_UNKNOWN` |
| `BDF-H` | 回执行号是否与 Excel 行号一致，且注明「起始行」口径 | 用记录序号即失败 | 解析器保留物理行号，回执写口径说明 |

## 参考资料

- RFC 4180《Common Format and MIME Type for CSV Files》（引号、逗号、换行与表头约定）：<https://www.rfc-editor.org/rfc/rfc4180>
- ISO 8601-1:2019《Date and time — Representations for information interchange》：<https://www.iso.org/standard/70907.html>
- ISO 4217 货币代码与最小单位（minor unit）：<https://www.iso.org/iso-4217-currency-codes.html>
- Microsoft《Excel specifications and limits》（单元格 32,767 字符、253 个换行）：<https://support.microsoft.com/en-us/office/excel-specifications-and-limits-1672b34d-7043-467e-8e27-269d656771c3>
- [解析与编码：编码嗅探、引号与注入面](../ParsingAndEncoding/index.md)（BOM 与编码在这一页展开）
- [行级校验与错误回执](../RowValidation/index.md)（行号语义在回执里的落地）
