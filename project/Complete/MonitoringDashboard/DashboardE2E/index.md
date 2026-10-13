# 大盘数据接口端到端核对

第 129 天定稿了**契约五**（C6 → C7）：请求只带 `panel_id` 与时间范围，查询语句 / `step` / `unit` 全部由服务端推导，返回统一的六字段结构。今天是**第 2 周收官**：把这条接口从请求进到响应出**逐段走一遍**，核对它是不是真的按契约在干活。

一句话定位：**契约是两份文件写成的，接口是一次调用跑出来的——两者的距离只能靠「走一遍」来量。**

![大盘数据接口端到端核对：六段链路、判据修正与服务端显式不变量](../assets/dashboard-e2e.svg)

::: warning 本项目只有文档，没有代码
下面给出的核对脚本、代码骨架与判据，是**读者在自己的工程仓库里要执行的检查**。本仓库不存放任何源码、脚本与配置；「运行 `xxx`」一律指「先按本节创建好该文件，再执行」。
:::

## 一句话定位

第 132 天的收口（上）解决了**接缝**问题——`S1~S4` 是「配置与配置之间」的静态关系。今天解决的是另一种问题：**同一条约束在运行时是不是真的成立**。接缝对了，接口照样可以返错。

## 一、为什么「逐条读契约」不算核对

契约五是一份写得相当具体的文件，但它有一类内容**只有跑起来才知道对不对**：

| 契约里写下的 | 只有跑起来才知道的 |
| --- | --- |
| 返回是「统一的六字段结构」 | 六个要点是不是真的都填了；缺一个会不会**静默**变成空白图 |
| `step` 由服务端推导 | 推导出来的那个数字，是不是**采集间隔的整数倍** |
| 无数据必须给明确原因 | 实际返回的是原因，还是那个「看起来正常」的空数组 |
| `meta.from` / `meta.to` 存在 | 回显的是**请求原值**还是**实际查询区间**（两者在服务端对齐后并不相同） |

所以这一天的动作不是「再读一遍契约」，而是**把一条请求拆成六段，每一段问一句「这段的实际输出等于契约承诺的输出吗」**。

## 二、六要点 × 契约五 逐条对齐

契约五原文写的是「统一的六字段结构」，列出 5 个顶层键（`panel_id` / `title` / `unit` / `series[]` / `meta`）与 `meta` 内的 5 个子键，另加一条「无数据必须给明确原因」的硬要求。核对时按**可观测的 6 个要点**对齐——第 6 项落在 `meta.reason` 内（`check-dashboard.sh` 的 DA6 读的就是 `.meta.reason`）。

| # | 要点 | 契约五要求 | 取值来源 | 核对方式 | 错了会怎样 |
| --- | --- | --- | --- | --- | --- |
| 1 | `panel_id` | 原样回显请求值 | 请求 | 与 URL 末段逐字比对 | 回显成标题或规则名 → 前端把结果挂到**另一块面板**上 |
| 2 | `title` | 取自服务端白名单 | `panels.yaml` | 与白名单逐字比对 | 标题可被请求方影响 → 等于开放了任意文案写入 |
| 3 | `unit` | 由服务端下发，前端不换算 | `panels.yaml` | 与白名单逐字比对 | 回显请求方的 `unit` → 同一指标在两块面板上单位不同 |
| 4 | `series[]` | 只含标签与 `points`；标签集合 = 规则产出的标签 | `recording.yaml` | 取一条已知序列，比对**标签键集合** | 多出采集器注入的标签 → 图例炸开；少一个 → 实例分不清 |
| 5 | `meta` | `from` / `to` / `step` / `generated_at` / `truncated` | 服务端 | 五个子键逐个 `jq -e has()` | 缺 `truncated` → 值班人以为看到的是全量数据 |
| 6 | `meta.reason` | 无数据必须 `no_series` / `all_zero` / `out_of_retention` 三选一 | 服务端 | 用超出保留期的范围请求，读 `.meta.reason` | 返回空数组 → 值班人读成「一切正常」（第 129 天失败矩阵点名的正是这一行） |

::: tip 第 5 项里有个容易漏掉的点
`meta.from` / `meta.to` **不应该等于请求里的 `from` / `to`**。服务端为了对齐采样边界，通常会把区间向两侧取整到 `step` 的整数倍。所以正确行为是：**回显服务端实际用的那个区间**，而不是把请求原值抄回来。两者不一致时，图上时间轴的每一格都会偏，而**这是唯一一处「契约没写错、实现也没报错、但图是错的」的地方**。
:::

## 三、核对中发现的缺陷：W2-C 的判据写弱了

这是今天最有价值的产出——**第 132 天定的一条判据，经过今天的端到端核对，被证明拦不住它要拦的东西。**

### 第 129 天定稿的公式

```text
step = max( minStep, ceil((to − from) / max_points) )
```

### 第 132 天把它核成

> **W2-C**：`step ≥ scrape_interval` 且为整数倍。

### 问题出在哪

这两条单独看都没问题，**合起来是错的**：

- 原式的第二项 `ceil((to − from) / max_points)` **完全不受 `scrape_interval` 约束**；
- W2-C 的第一半只断言「不小于」，而 `44 ≥ 15` 成立 → **PASS**；
- W2-C 的后半「且为整数倍」在第 132 天的推演脚本里**根本没有实现**（脚本只比较了 `step < 15`）。

于是产生一整类缺陷：`ceil(...)` 一旦超过 `minStep`，`step` 就脱离采集间隔，得到 **44s / 173s / 1210s / 5184s / 1296s** 这样的步长。

### 实测（300 组合网格）

网格口径：范围 ∈ {1h, 6h, 1d, 7d, 30d} × `max_points` ∈ {100, 500, 1000, 2000, 5000} × `scrape_interval` ∈ {10, 15, 20, 30}s × `recording.interval` ∈ {30, 60, 120}s。

| 口径 | 非整数倍步长的组合数 |
| --- | --- |
| 原式（不对齐） | **160 / 300** |
| 先算再对齐（本章口径） | **0 / 300** |

> 这两行是**本机实跑**的结果，不是估计值。脚本见第九节。

### 为什么这类缺陷最危险

1. **不报错**。没有异常、没有日志、没有 5xx；接口返 200，`jq` 能正常解析。
2. **点数是够的，甚至更少**。步长变大反而更容易过 `DA5`（点数不超预算）——**门禁越松，缺陷越容易通过**。
3. **越「为了更精细」越容易踩中**。把 `max_points` 从 500 调到 2000 是为了让图更细，结果在 30 天范围上反而把 `step` 推到了 1296s 这种非整数倍上。
4. **误判方向是反的**。相位漂移在图上表现为「台阶」，看起来像**数据在周期性抖动**——值班人会去查业务，而问题在大盘参数里。

::: danger 一条纪律
**「大于等于」和「整数倍」不是同一个判据。** 前者是一个**不等式**，后者是一个**同余关系**。凡是「周期相关的两个数字必须相容」的约束，写成不等式都拦不住缺陷——因为不等式允许的取值集合里，绝大多数成员都会破坏同余关系。

这条纪律不只适用于 `step`：抓取间隔与规则窗口、规则窗口与保留期、缓存 TTL 与刷新间隔，全都是同一类关系。
:::

## 四、把约束落成服务端显式不变量

第 132 天的 `W2-H` 只说「`minStep` 的来源必须被显式注释」——那是**静态可判**的一条，属于文档纪律。今天的动作是把它**升级成运行期不变量**：不是「注释里写了」，而是「违反时进程起不来」。

### 三条不变量

| 编号 | 不变量 | 违反时 |
| --- | --- | --- |
| **INV-1** | `minStep` 同时读 `recording.interval` 与 `scrape_interval` 两处配置，取较大者，再向上对齐到 `scrape_interval` 的整数倍 | 拒绝启动 |
| **INV-2** | `step = snap( max(minStep, ceil((to − from) / max_points)), scrape_interval )` | 拒绝启动 |
| **INV-3** | 启动时对**面板声明的全部可选范围**逐个断言 `step % scrape_interval == 0` 且 `step ≥ minStep` | 拒绝启动 |

```java
/**
 * 步长策略。
 *
 * ⚠️ 本类的两个输入来自**别的契约**，改动前必须先读对方的契约文件：
 *    - scrapeInterval    ← 契约二（采集端 scrape_interval）
 *    - recordingInterval ← 契约三（recording 规则的 interval）
 *
 * 第 132 天 W2-H 要求「跨文件读配置必须显式声明来源」——
 * 也就是说上面这两行注释本身是判据的一部分，不是装饰。
 */
public final class StepPolicy {

    private final long scrapeSeconds;      // 契约二
    private final long recordingSeconds;   // 契约三
    private final int  maxPoints;
    private final long minStep;            // INV-1 的产物

    public StepPolicy(long scrapeSeconds, long recordingSeconds, int maxPoints) {
        if (scrapeSeconds <= 0)    throw new IllegalStateException("scrape_interval 未读到（契约二）");
        if (recordingSeconds <= 0) throw new IllegalStateException("recording.interval 未读到（契约三）");
        if (maxPoints <= 0)        throw new IllegalStateException("max_points 未配置");

        this.scrapeSeconds    = scrapeSeconds;
        this.recordingSeconds = recordingSeconds;
        this.maxPoints        = maxPoints;

        // INV-1：两处来源取较大者，再向上对齐到采集间隔的整数倍
        long base = Math.max(scrapeSeconds, recordingSeconds);
        this.minStep = ceilTo(base, scrapeSeconds);

        assertInvariants();   // INV-3：构造即断言，违反就拒绝启动
    }

    /** INV-2：先算再对齐——绝不返回未经对齐的值 */
    public long step(long rangeSeconds) {
        long raw = Math.max(minStep, ceilDiv(rangeSeconds, maxPoints));
        return ceilTo(raw, scrapeSeconds);
    }

    private void assertInvariants() {
        if (minStep % scrapeSeconds != 0)
            throw new IllegalStateException("INV-1 违反：minStep 不是 scrape_interval 的整数倍");
        if (minStep < recordingSeconds)
            throw new IllegalStateException("INV-1 违反：minStep 小于 recording.interval");

        // 对面板声明的全部可选范围逐个断言，把配置错误挡在启动期
        for (long range : new long[]{3600L, 21600L, 86400L, 604800L, 30L * 86400}) {
            long s = step(range);
            if (s % scrapeSeconds != 0)
                throw new IllegalStateException("INV-3 违反：范围 " + range + "s 的 step=" + s + " 不是整数倍");
            if (s < minStep)
                throw new IllegalStateException("INV-3 违反：范围 " + range + "s 的 step=" + s + " 小于 minStep=" + minStep);
        }
    }

    private static long ceilDiv(long a, long b) { return (a + b - 1) / b; }
    private static long ceilTo(long v, long base) { return ceilDiv(v, base) * base; }
}
```

### 为什么是「拒绝启动」而不是「运行期兜底」

兜底会让配置错误**永远不暴露**：大盘照常出图，只是图是错的。而大盘是**看图的工具**——一张看起来正常的错图，比一张空白图更危险，因为它会让人做出错误判断。

**宁可启动失败、让部署卡住，也不要一张看起来正常的错图。**

### 边界：`step` 大于整个查询范围时

当 `step > (to − from)`（例如范围 30s、`minStep` 60s），范围内**确实还有一个样本**。此时的正确行为是**照样返回该点**，而不是判定为 `no_series`：

- 返回空 → 值班人在「最近 30 秒」这个面板上看到「无数据」，误以为采集停了；
- 返回该点 → 一块面板上只有一个点，看图的人自然知道「区间太短」。

这条要连同 `INV-3` 一起断言，否则不变量会把自己的边界情况变成新缺陷。

## 五、消解第 129 天与第 132 天的口径差异

核对时发现两天的说法**并不一致**：

| 天 | 说法 |
| --- | --- |
| 第 129 天 | `minStep` 取自 **recording 规则的计算周期**（第 126 天定的 `interval`） |
| 第 132 天 | `minStep` 应从**采集侧的 `scrape_interval` 推导** |

这不是「谁写错了」，而是**两天各自只看到了一个面**。把两面合起来看：

| 只读一处 | 会在什么情况下出错 |
| --- | --- |
| **只读 `recording.interval`** | 若 `recording.interval = 60s`、`scrape_interval = 20s`：60 是 20 的整数倍，暂时安全。但某天把 `recording.interval` 调到 45s（或把 `scrape_interval` 调到 25s），`minStep` 立刻变成非整数倍 → 相位漂移。**它把一个「跨文件关系」写成了常数。** |
| **只读 `scrape_interval`** | 若 `scrape_interval = 15s`、`recording.interval = 60s`：`minStep` 会算成 15s，于是 `step` 可以小到 15s。而大盘画的是 **recording 指标**，它的产生周期是 60s——15s 的 `step` 会把同一个聚合点**取四次**，图上是四段一模一样的平台。**这比台阶更难读懂，且看起来不像缺陷。** |
| **两个都读（本章口径）** | 取较大者再对齐，同时满足「不重复采样规则结果」与「不产生相位漂移」。 |

::: tip 结论
`minStep` 不是「某一个配置项」，而是**两个配置项之间的一个约束**。凡是这类约束，都不应该被物化成一个常数写进代码——**它必须每次启动时从两处来源重新算出来**。

这也解释了为什么第 129 天写「取自 recording 的 `interval`」在当时是**正确且充分**的：那时的 `scrape_interval` 与 `recording.interval` 恰好是整数倍关系。**一个结论在某个配置下成立，不等于它在所有配置下成立。**
:::

## 六、六段链路的失败表现

端到端核对的顺序是固定的：**任一段不通过，后面的段不必再看**。这个顺序本身也有理由——它按「缺陷的隐蔽程度」从高到低排。

| 段 | 这一段的实际输出 | 失败表现 | 隐蔽程度 |
| --- | --- | --- | --- |
| ① 请求入参 | 只有 `panel_id` 与 `from` / `to` | 出现 `query=` → 契约五被单方面破坏，**服务端无法对结果做任何预算** | 低（一眼可见） |
| ② 面板白名单 | 未登记返回 **404** | 返回 500 或空数组 → 路径穿越可落到别的路由上 | 低 |
| ③ `step` 推导 | `step` 是采集间隔的整数倍 | 出现 44s / 173s 这类步长 → **台阶状假曲线，误判为业务抖动** | **高**（本节主题） |
| ④ 查询下发 | 查询只存在于服务端 `panels.yaml` | 查询可由请求方影响 → 一个面板就能扫全库 | 中 |
| ⑤ 结构组装 | 六要点齐全，`unit` 由服务端下发 | 缺 `truncated` → 看到的是降采样结果却以为全量 | 中 |
| ⑥ 空原因判定 | `no_series` / `all_zero` / `out_of_retention` 三选一 | 返回空数组 → **「没有异常」与「查不到」被合并成同一个现象** | **高** |

### 核对脚本 `check-dashboard-e2e.sh`

```bash
#!/usr/bin/env bash
# scripts/check-dashboard-e2e.sh —— 大盘数据接口的端到端核对（第 133 天）
#
# 纪律（与 check-dashboard.sh 的 DA3 同款）：
#   本脚本只允许用 panel_id 与时间范围发起请求，**不得引入任何查询参数**。
#   理由：这类接口最常见的退化方式就是「为了校验方便」在校验脚本里直接传一条
#   原始查询——那等于用门禁证明了一个不该存在的入口。
set -u
BASE=${BASE:-http://localhost:8081}
PANEL=${PANEL:-overview_error_rate}
SCRAPE=${SCRAPE:-15}          # 契约二的 scrape_interval，单位秒
fail=0

# E2E1 六要点齐全：顶层 5 键 + meta 内 5 子键
curl -s "$BASE/api/panels/$PANEL?from=-1h" | jq -e \
  'has("panel_id") and has("title") and has("unit") and has("series")
   and (.meta | has("from") and has("to") and has("step")
                  and has("generated_at") and has("truncated"))' \
  >/dev/null || { echo "E2E1 FAIL 返回结构缺键"; fail=1; }

# E2E2 panel_id 与 title 必须来自服务端白名单（请求方改不动）
body=$(curl -s "$BASE/api/panels/$PANEL?from=-1h")
got_id=$(printf '%s' "$body" | jq -r '.panel_id')
got_title=$(printf '%s' "$body" | jq -r '.title')
[ "$got_id" = "$PANEL" ] || { echo "E2E2 FAIL panel_id=$got_id"; fail=1; }
[ -n "$got_title" ] && [ "$got_title" != "null" ] || { echo "E2E2 FAIL title 为空"; fail=1; }

# E2E3 step 必须是 scrape_interval 的整数倍（本章修正后的 W2-C / E2E-A）
step=$(curl -s "$BASE/api/panels/$PANEL?from=-30d" | jq -r '.meta.step')
case "$step" in
  ''|null) echo "E2E3 FAIL 未取到 meta.step"; fail=1 ;;
  *[!0-9]*) echo "E2E3 FAIL step=\"$step\" 不是整数秒（契约五要求以秒为单位）"; fail=1 ;;
  *) [ $(( step % SCRAPE )) -eq 0 ] \
       || { echo "E2E3 FAIL step=${step}s 不是 ${SCRAPE}s 的整数倍"; fail=1; } ;;
esac

# E2E4 meta.from / meta.to 必须是实际查询区间，且长度是 step 的整数倍
align=$(curl -s "$BASE/api/panels/$PANEL?from=-1h" | jq -r '
  (.meta.from | fromdateiso8601) as $f
  | (.meta.to   | fromdateiso8601) as $t
  | (.meta.step) as $s
  | if (($t - $f) % $s) == 0 then "OK \($t - $f)s / step=\($s)s"
    else "FAIL 实际区间 \($t - $f)s 不是 step=\($s)s 的整数倍" end')
echo "E2E4 $align"
case "$align" in OK*) : ;; *) fail=1 ;; esac

# E2E5 空原因必须显式（超出保留期不许返回空数组）
reason=$(curl -s "$BASE/api/panels/$PANEL?from=2000-01-01T00:00:00Z&to=2000-01-01T01:00:00Z" \
         | jq -r '.meta.reason // "MISSING"')
case "$reason" in
  no_series|all_zero|out_of_retention) : ;;
  *) echo "E2E5 FAIL 超出保留期返回 reason=$reason"; fail=1 ;;
esac

# E2E6 truncated 与 step 的放大语义一致：只有点数确实超过预算时才允许 true
tr=$(curl -s "$BASE/api/panels/$PANEL?from=-30d" | jq -r '.meta.truncated')
n=$(curl -s "$BASE/api/panels/$PANEL?from=-30d" | jq '[.series[].points[]] | length')
[ "$n" -le 2000 ] || { echo "E2E6 FAIL 点数 $n 超过预算"; fail=1; }
echo "E2E6 INFO truncated=$tr points=$n step=${step}s（人工确认三者语义一致）"

exit $fail
```

> **`E2E3` 是本章新增的核心一条**，它把「步长是不是采集间隔的整数倍」从文档纪律变成了可执行断言。`E2E4` 用 `.meta.from` / `.meta.to` 的实际长度反查一致性——这是唯一一处能发现「`from`/`to` 回显了请求原值而不是实际区间」的检查。

## 七、判据表（E2E-A ~ E2E-H）

| 编号 | 判据 | 类型 | 本机结果 |
| --- | --- | --- | --- |
| **E2E-A** | `step` 是 `scrape_interval` 的整数倍（全部面板 × 全部可选范围） | 静态推演 + 运行期 | ✅ 本机可判（300 组合网格，0 缺陷，已跑） |
| **E2E-B** | 服务端启动期断言 INV-1 / INV-2 / INV-3，违反时**拒绝启动**并给出明确日志 | 动态 | `⏳ 未跑`（原因：本仓无工程代码，需服务启动才能观察启动失败行为） |
| **E2E-C** | `minStep` 同时 ≥ `recording.interval` 与 `scrape_interval`，且两个来源都在代码中显式声明 | 静态 | ✅ 本机可判（检查配置与来源注释） |
| **E2E-D** | `meta.from` / `meta.to` 回显**实际查询区间**（长度为 `step` 的整数倍），不是请求原值 | 动态 | `⏳ 未跑`（原因：需服务在监听） |
| **E2E-E** | `series[].labels` 的键集合等于对应 recording 规则产出的标签集合（不多不少） | 静态比对 + 运行期 | ✅ 静态可判（比对 `panels.yaml` 与 `recording.yaml` 的产出标签） |
| **E2E-F** | `meta.reason` 由**真实保留期**判定，且 `no_series` 与 `all_zero` 在全零序列下可区分 | 动态 | `⏳ 未跑`（原因：需服务与真实存储） |
| **E2E-G** | `meta.generated_at` 与本面板缓存 TTL 的关系被显式声明（前端不得另立新鲜度口径） | 静态 | ✅ 本机可判 |
| **E2E-H** | `check-dashboard-e2e.sh` 语法与参数正确，且**不引入任何查询参数**（与 `DA3` 同纪律） | 静态 | ✅ 本机可判（`bash -n` 语法检查已跑） |

::: tip 判据边界：`E2E-*` 与 `W2-*` 不重叠
按第 127 天的**判据唯一性纪律**，两个族的判据对象不同：

- **`W2-*`** 判的是**配置与配置之间**的静态关系（接缝是否成立、跨文件读配置是否声明）；
- **`E2E-*`** 判的是**一条真实请求**在链路上每一段的**运行期行为**（实际输出了什么）。

有一处需要显式说明：**`W2-C` 的判据表述由本章修正**——原表述「`step ≥ scrape_interval` 且为整数倍」中，前半句是必要但不充分的，且后半句未实现。修正后的完整口径就是 **`E2E-A`**。这是**替换而非新增**（不产生两条同名不同义的判据）；`W2-H` 保持「来源是否被声明」的原口径，`E2E-B` 补上它检查不到的那一半——**越界时会发生什么**。
:::

## 八、当日做了什么

1. 确立端到端核对的方法：**把一条请求拆成六段，逐段问「实际输出等于契约承诺吗」**，而不是重读一遍契约；
2. 产出**六要点 × 契约五**的逐条对齐表（含每一条的「取值来源 / 核对方式 / 错了会怎样」），并点出 `meta.from` / `meta.to` 应回显**实际查询区间**这个最容易漏的点；
3. 通过核对**发现 `W2-C` 判据写弱了**：原式 `ceil((to−from)/max_points)` 不受 `scrape_interval` 约束，而不等式判据拦不住非整数倍步长；
4. 给出**本机实跑**的量化证据：300 组合网格下，原式 **160/300** 非整数倍、先算再对齐 **0/300**；
5. 把约束从「注释」升级为「**启动期不变量**」——INV-1 / INV-2 / INV-3 三条，违反即拒绝启动，并给出「为什么宁可启动失败也不要一张看起来正常的错图」的理由；
6. **消解第 129 天与第 132 天的口径差异**：`minStep` 不是某一个配置项，而是两个配置项之间的约束，必须每次启动时从两处重算；并写清「只读一处」各自会在什么情况下出错；
7. 补上边界情形：`step` 大于整个查询范围时仍须返回该点，而不是判定为 `no_series`；
8. 产出 `E2E-A ~ E2E-H` 判据表，并**显式写清与 `W2-*` 的边界**（`W2-C` 替换为 `E2E-A`，`W2-H` 保留、由 `E2E-B` 补运行期行为），遵守判据唯一性纪律。

## 九、如何验证

```shell
# 1) 结构完整性：本章要核对的三样东西都在仓库里
ls project/Complete/MonitoringDashboard/DashboardE2E/index.md
grep -c 'E2E-' project/Complete/MonitoringDashboard/DashboardE2E/index.md
grep -n 'INV-1\|INV-2\|INV-3' project/Complete/MonitoringDashboard/DashboardE2E/index.md | head -6

# 2) step 的整数倍推演（E2E-A，本机可跑，纯算术，不需要服务）
python3 - <<'PY'
import math
def snap(v, b): return math.ceil(v / b) * b

RANGES = [3600, 21600, 86400, 604800, 30*86400]
MPS, SCRAPES, RECS = [100, 500, 1000, 2000, 5000], [10, 15, 20, 30], [30, 60, 120]

bad_new = bad_old = total = 0
for sc in SCRAPES:
    for rec in RECS:
        minstep = snap(max(rec, sc), sc)              # INV-1
        for mp in MPS:
            for r in RANGES:
                total += 1
                if max(minstep, math.ceil(r / mp)) % sc != 0:   # 原式（不对齐）
                    bad_old += 1
                if snap(max(minstep, math.ceil(r / mp)), sc) % sc != 0:  # INV-2
                    bad_new += 1

print(f"组合总数={total}  原式非整数倍={bad_old}  对齐后非整数倍={bad_new}")
print("E2E-A", "PASS" if bad_new == 0 else "FAIL")
PY
#    期望：组合总数=300  原式非整数倍=160  对齐后非整数倍=0

# 3) 核对脚本的语法与「不引查询参数」纪律（E2E-H，与 DA3 同款检查）
bash -n scripts/check-dashboard-e2e.sh && echo "语法 OK"
grep -q 'query=' scripts/check-dashboard-e2e.sh && echo "E2E-H FAIL 脚本引入了查询参数" || echo "E2E-H PASS"

# 4) 起链路后逐条跑（需服务在监听，否则按纪律标 ⏳）
bash scripts/check-dashboard-e2e.sh; echo "exit=$?"
#    期望：exit=0；且 E2E3 报出的 step 是 ${SCRAPE}s 的整数倍

# 5) project/ 下只允许文档与配图（提交前自查，输出必须为空）
find project -type f ! -name "*.md" ! -name "*.png" ! -name "*.svg" ! -name "*.jpg"
```

## 十、下一步

- **第 134 天**：**第 2 周收口（终）**——输出「服务可启动、接口可调用、页面可访问」三条验收判据的**可执行步骤与阻塞项**，为第 3 周联调铺路；同时把 `W2-C → E2E-A` 的判据修正回写到 [第 2 周收口（上）](../Week2Close/index.md) 页（**追加说明、不删除原表述**）。
- **第 3 周（135-141）**：端到端联调 + **L3 告警实测触发** + **L4 容量与保留策略压测**。
- **动态判据回填**：`E2E-B / D / F` 与上一章遗留的 `L1`（`DA-A` / `DA-D` / `DA-H`）、`L2` 五条静态对账，在工程仓库与容器运行时具备后**逐条回填**；回填前一律保持 `⏳ 未跑` 标注。

::: warning 一条纪律（沿用上一章）
上面这些未跑项**都有明确的前置条件**。第 3 周的任务是**先补齐前置条件**，而不是直接去做它们。**如果前置条件仍不满足，正确做法是继续如实标注，而不是把期望值填进实测列。**
:::

## 参考资料

- 上一章：[第 2 周收口：四组件 × 五契约对账](../Week2Close/index.md)
- 契约五原文与实现决定：[看板数据服务（C6）](../DashboardAPI/index.md)
- 契约三的 `recording.interval`：[查询与规则设计](../Rules/index.md)
- 契约二与 `scrape_interval`：[采集任务配置](../ScrapeConfig/index.md)
- 契约文件与配置三层划分：[接口契约与工程骨架](../Contracts/index.md)
- 理论基座：[监控告警专题](/docs/Ops/Monitoring/index.md)
- 项目方法论：[完整项目交付](/docs/Others/ProjectDelivery/index.md)
