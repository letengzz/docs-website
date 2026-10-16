# 环境交付件落盘：9 份台账与 3 份脚本的内容入仓

这一页是第 4 周（部署 + 文档沉淀）的**第 9 步**：把第 147 天《交付包》台账里标 `⏳` 的**环境交付件**从「只有指纹和命令」推进到「内容可拷贝」。它回答三件事——**哪几份已经落在库里、哪几份没有、今天补了哪几份**；它**不重复**[交付包](../DeliveryPackage/index.md)的台账口径，也**不重复**[交付演练](../DeliveryDrill/index.md)的只读自检。

![实时监控大盘：9 份环境交付件的落盘台账、库内覆盖率与三步复算路径](../assets/env-artifacts.svg)

## 一、这一步在周期里的位置

第 147 天把交付包拆成两部分：**本仓交付件**（三份文档 + `preflight.sh`）与**环境交付件**（9 份配置与脚本）。前者当天被 `PK-A` 判出越界形态、今天已换形态结清；后者当时**只记了指纹**，台账逐行写着 `⏳`——因为「记录不等于交付」。

今天做的就是把 `⏳` 逐行变成 `✅` 或**如实仍然 `⏳`**：

| 项 | 第 147 天的状态 | 第 148 天的处置 |
| --- | --- | --- |
| 三份文档（复现指南 / 验收清单 / 故障索引） | ✅ 已落成独立页面 | 不动 |
| `preflight.sh`（本仓交付件） | ❌ 形态越界（`PK-1`） | 内容搬进[交付演练](../DeliveryDrill/index.md)第十节，文件移出 |
| **环境交付件 9 份** | ⏳ 仅指纹与命令 | **本页：先量覆盖率，再补真缺的那几份** |

**先量，再补。** 直接「把 9 份全部贴进仓库」是最省事的做法，也是错的：其中若干份的内容**早已在别的页里落着**（例如 alertmanager 的配置在验收三页里逐行完整），再贴一遍就是**同内容两处维护**——本库有一条硬纪律专门防它：*已有内容不做重复章节*。所以今晚的第一步是量一次「库内覆盖率」。

## 二、9 份交付件的落盘台账（实测）

量法是：把每份文件里**长度大于 12 且非注释**的行取出来当语料，逐行到 `project/` 与 `docs/` 的全部 Markdown 里做**精确子串匹配**，报「命中行数 / 有效行数」。这是一个**偏保守**的读数：格式化差异（缩进、换行）都会算成未命中，因此真实覆盖只会更高。

| # | 交付件 | 字节 / 行 | 库内命中 | 覆盖率 | 最佳落点页 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `compose.yaml` | 910 B / 28 | 11 / 21 | **52.4%** | [架构设计](../Architecture/index.md)（9 行）、[部署前置](../DeployPrep/index.md)（4 行） | ⏳ 结构与片段在，逐行不全 |
| 2 | `compose.singlefile.yaml` | 910 B / 28 | 同第 1 行 | —— | 同上（`cmp` 实测与第 1 行**完全相同**） | ⏳ 同上 |
| 3 | `prometheus/prometheus.yml` | 2017 B / 74 | 59 / 66 | **89.4%** | [采集任务配置](../ScrapeConfig/index.md)（44 行） | ✅ 基本落盘 |
| 4 | `prometheus/alerting.yaml` | 5661 B / 98 | 26 / 40 | **65.0%** | [部署前置](../DeployPrep/index.md)（25 行）、[查询与规则设计](../Rules/index.md)（20 行） | ⏳ 规则体在，逐行不全 |
| 5 | `prometheus/recording.yaml` | 431 B / 13 | 8 / 9 | **88.9%** | [查询与规则设计](../Rules/index.md)（6 行） | ✅ 基本落盘 |
| 6 | `alertmanager/alertmanager.yaml` | 480 B / 16 | 13 / 13 | **100.0%** | [验收三](../Acceptance3/index.md)（13 行） | ✅ **逐行完整** |
| 7 | `bin/one-click-up.sh` | 7614 B / 134 | 9 / 62 | **14.5%** | 最高命中仅 4 行（[交付演练](../DeliveryDrill/index.md)） | ❌ **内容未落盘** |
| 8 | `scripts/check-panels.sh` | 8095 B / 156 | 2 / 72 | **2.8%** | 最高命中仅 2 行 | ❌ **内容未落盘** |
| 9 | `scripts/check-alerts.py` | 12278 B / 268 | 6 / 175 | **3.4%** | 最高命中仅 1 行 | ❌ **内容未落盘** |

**读数给出的结论很清楚**：6 份配置类交付件的内容**已经在库里**（其中 3 份接近逐行完整）；真正空着的只有**三份脚本**——它们各自只有 3%~15% 的行能在库里找到，而库里出现的往往是**命令名**（`bash bin/one-click-up.sh`），不是内容。

::: tip 为什么「命令名出现」不等于「交付件存在」
读者看到 `bash bin/one-click-up.sh` 时，**他手上并没有这个文件**。这正是第 146 天演练抓到的那件事的另一种形态：文档里写着「运行 `xxx`」，而 `xxx` 不存在——读者只能停在那里。**判据必须是「内容可 grep 到」，不是「文件名被提到过」。**
:::

## 三、三份脚本的完整内容

三份脚本落在本页**第九节**（附录），这是本节要说明的三条取舍：

1. **为什么是「页面里的围栏代码块」而不是「仓库里的文件」**：`project/` 只允许 `*.md` 与配图（`AGENTS.md` 第 9 节）。第 146 天把 `preflight.sh` 落成文件、第 147 天被 `PK-A` 当场判 `FAIL`、第 148 天换形态结清——**同一条边界不会因为换了一份脚本就允许放行**。
2. **为什么三份放同一页而不是三页**：它们**同属一个交付单元**（一键起 → 看板自查 → 告警自查），任何一份单独看都无法复算出结论；而项目页的粒度是「一个可验证的构建步骤」，今天这一步就是「把这一组脚本的输入补齐」。
3. **为什么连注释一起落**：三份脚本里有 **8 处注释是踩坑记录**（例如 `${t##*, }` 多写一个空格导致永远切不开；数「非 OK 行」会把 `shasum` 的告警行也算成一项）。**注释是这三份脚本技术含量最高的部分**——删掉注释的版本能跑，但读者会用同样的方式再踩一次。

## 四、复算：从页面内容重建这 9 份交付件

读者按下面四步，可以把本页与各落点页的内容**还原成一份能跑的沙盒**。全程只依赖网页内容，不依赖任何仓库文件（这正是「落盘」的含义）。

```shell
# 步骤 ①② 建目录骨架与配置类交付件（内容见各落点页的对应小节）
WORK=~/monitoring-run && mkdir -p "$WORK"/{prometheus,alertmanager,bin,scripts,docs}
cd "$WORK"
#   ① compose.yaml       ← ../Architecture/index.md + ../DeployPrep/index.md
#   ② prometheus/*.yaml  ← ../ScrapeConfig/index.md + ../Rules/index.md
#   ③ alertmanager.yaml  ← ../Acceptance3/index.md（逐行完整，可整段复制）
#   以上 6 份的校验命令（语法正确性）：
docker compose config -q                      # 期望：无输出、rc=0
promtool check config prometheus/prometheus.yml   # 期望：SUCCESS: 3 rule files found
amtool check-config alertmanager/alertmanager.yaml # 期望：SUCCESS

# 步骤 ③ 三份脚本（内容见本页第九节）
#   ④ bin/one-click-up.sh   ← 第九节 9.1
#   ⑤ scripts/check-panels.sh ← 第九节 9.2
#   ⑥ scripts/check-alerts.py ← 第九节 9.3
chmod +x bin/one-click-up.sh scripts/check-panels.sh
python3 -m py_compile scripts/check-alerts.py  # 期望：无输出、rc=0

# 步骤 ④ 三条自查一次跑完（只读；三态退出码见 ../DeliveryDrill/index.md）
bash "$WORK/bin/one-click-up.sh"               # 期望：三级就绪信号，最后 rc=0
bash "$WORK/scripts/check-panels.sh"; echo "rc=$?"   # 期望：三张大盘各一行结论
python3 "$WORK/scripts/check-alerts.py"; echo "rc=$?" # 期望：告警链路逐项 OK
```

::: danger 复算里最容易跳过的一步：语法校验
`docker compose config -q` 与 `promtool check config` 都只做**静态校验**，不需要起栈。跳过它们直接起栈的后果是：**错误会被推迟到「栈已经起了一半」的时刻**，而这时容器已经占了端口、写了一半的卷——排查成本高出一个量级。**第 0 层的东西必须在第 0 层查**（这条口径与第 144 天的「成对声明判据放在起栈之前」是同一条）。
:::

## 五、判据表：`EA-A` ~ `EA-H`

| 判据 | 内容 | 怎么验证 | 状态 |
| --- | --- | --- | --- |
| `EA-A` | 9 份环境交付件**逐份**给出字节 / 行数 / 库内命中 / 覆盖率四个读数 | 本页第二节表格 9 行，四列非空 | ✅ 本机已判 |
| `EA-B` | 覆盖率是**量出来的**，不是估的：量法与「偏保守」的理由写死 | 页面含「长度大于 12 且非注释」与「格式差异算未命中」两句 | ✅ 本机已判 |
| `EA-C` | 三份未落盘的脚本，其**完整内容**在本页可 `grep` 到 | 对三份脚本各取一条代表性行，在页面内命中 | ✅ 本机已判 |
| `EA-D` | 脚本内容带**注释**（踩坑记录不删），且围栏带文件名标题语法 | 三个围栏均为 ` ```shell [路径] ` / ` ```python [路径] ` 形态 | ✅ 本机已判 |
| `EA-E` | 6 份配置类交付件都在**已存在的页面**里有落点，且未新建重复章节 | 第二节「最佳落点页」列的 6 个链接均可解析 | ✅ 本机已判 |
| `EA-F` | 复算路径**不依赖仓库文件**：每条命令的输入都有「去哪里取」 | 第四节四条步骤各自标注内容来源页 | ✅ 本机已判 |
| `EA-G` | 语法校验被放在起栈之前，且给出「跳过它会发生什么」 | 页面含 `docker compose config -q` 与「推迟到栈起了一半」的后果句 | ✅ 本机已判 |
| `EA-H` | 三份脚本在真环境里各跑过一次，读数非空 | 起沙盒后逐条执行第四节步骤 ④ | ⏳ 未跑（原因：**本仓库只有文档，没有可执行的工程与沙盒**；容器运行时本机可用，复验见 [第 3 周验收结论](../../TeamBoard/Week3Acceptance/index.md) 第三节） |

## 六、当日做了什么

1. **先量再补**：把「9 份环境交付件」逐份做了一次**库内覆盖率实测**（有效行定义、匹配口径、偏保守的理由都写死在页面里），得到 6 份已落盘、3 份空着这个结论——**避免了把 6 份已有内容再贴一遍**（那会变成同内容两处维护）。
2. 记录**一份形式特殊的情况**：`compose.singlefile.yaml` 与 `compose.yaml` 的 `cmp` 实测完全相同，因此不单独计数，只在台账里注明——这是第 144 天「两份 sha256 相同的编排文件看着像互相备份」那条结论的延续。
3. **补上三份真正空着的脚本内容**（`one-click-up.sh` 134 行 / `check-panels.sh` 156 行 / `check-alerts.py` 268 行，**连 8 处踩坑注释一起**），落在本页第九节，围栏带文件名标题语法。
4. 给出**四步复算路径**：从各落点页取 6 份配置 → 从本页取 3 份脚本 → 先做两条**静态语法校验** → 再跑三条自查。每一步都标注「内容去哪里取」，**不依赖任何仓库文件**。
5. 写死**「命令名出现 ≠ 交付件存在」**这条口径，并把它作为本节的存在理由：库里 3 份脚本的命中行大多只是脚本名的调用点。
6. 产出 **`EA-A` ~ `EA-H` 八条判据**：七条文档级、本机可判，一条运行期如实标 `⏳`；`⏳` 的原因只写**本仓库无工程与沙盒**（口径更正见第四天的[第 3 周验收结论](../../TeamBoard/Week3Acceptance/index.md)）。

## 七、如何验证

```shell
cd project/Complete/MonitoringDashboard/EnvArtifacts

# EA-A：台账 9 行 + 四列
grep -cE '^\| [0-9] \| `' index.md                        # 期望 9

# EA-B：量法与保守口径写死
grep -c '长度大于 12 且非注释' index.md                     # 期望 3
grep -c '因此真实覆盖只会更高' index.md                     # 期望 2

# EA-C：三份脚本的代表性行都在页内（各取一条只在脚本里出现的行）
grep -c '三级就绪信号' index.md                            # 期望 3
grep -c 'check-panels.sh' index.md                        # 期望 10
grep -c 'check-alerts.py' index.md                        # 期望 12

# EA-D：三个围栏带文件名标题语法
grep -cE '^```(shell|python) \[(bin/one-click-up\.sh|scripts/check-panels\.sh|scripts/check-alerts\.py)\]' index.md  # 期望 3

# EA-E：6 个落点页链接可解析（linkcheck 覆盖，此处只数链接条数）
grep -c '最佳落点页\|\.\./[A-Za-z0-9]*/index\.md' index.md  # 期望 19

# EA-F：复算路径四条步骤 + 内容来源标注
grep -c '^# 步骤 [①②③④]' index.md                        # 期望 3
grep -c '不依赖任何仓库文件' index.md                       # 期望 3

# EA-G：语法校验在起栈之前
grep -c 'docker compose config -q' index.md               # 期望 4
grep -c '栈已经起了一半' index.md                          # 期望 2

# 配图与判据条数
grep -c 'assets/env-artifacts.sv[g]' index.md             # 期望 1
grep -cE '^\| `EA-[A-H]`' index.md                        # 期望 8
```

## 八、下一步

| 待办 | 内容 | 归属 |
| --- | --- | --- |
| **干净机器复现** | 一台干净机器上按《从零复现指南》完整执行，把 `DD-G` 的读数从 **1** 变成 **0**；本页第四节是它的输入清单 | 第 143 天登记、第 147 天再次登记，**今天仍未解**（但输入已经齐备） |
| **`compose.yaml` 逐行落盘** | 覆盖率 52.4%，是 6 份配置里最低的一份；差的那 10 行需要逐行补到[架构设计](../Architecture/index.md)或[部署前置](../DeployPrep/index.md) | **今天新登记**（量出来才发现） |
| **`alerting.yaml` 逐行落盘** | 覆盖率 65.0%；规则体在、边界与注释不全 | **今天新登记** |
| `L3` | 真实通知渠道四项前置（凭据 / 模板 / 限流重试 / `resolved`） | 第 140 天登记，仍未解 |
| 周期 5 收口 | 第 4 周收口：交付包 + 交付件落盘 + 干净机器复现 + 结项结论 | 本目录 |

## 九、附录：三份脚本完整内容

下面三份内容按**第 146~147 天沙盒里的实测版本**落盘。把它们存成同名文件、`chmod +x`（Python 那份不需要）即可复跑第四节步骤 ④。

```shell [bin/one-click-up.sh]
#!/usr/bin/env bash
# 一键起全栈 + 三级就绪等待 + 验收
#
# 为什么需要一个脚本，而不是「docker compose up -d 然后手动 curl」：
#   `up -d` 的返回值只保证**容器已被创建并启动**，它不保证：
#     · Prometheus 的 HTTP 端口能应答（第 2 级）
#     · 所有 target 完成过至少一次抓取（第 3 级）
#   第 3 级的等待上界不是拍脑袋的 30s，而是配置里**最大的 scrape_interval** ——
#   因为最慢的那个 job 决定了「大盘能画出全部曲线」的最早时刻。
#   本沙盒里它是 `edge-services / 60s`，所以 `up -d` 返回后最多要等 60s 才算就绪。
#
# 退出码：0 就绪 / 1 超时或验收有红项
set -uo pipefail
cd "$(dirname "$0")/.."

BASE="${BASE:-http://localhost:19090}"
COMPOSE="${COMPOSE:-docker compose}"
PY="${PY:-python3}"

log() { printf '  %s\n' "$*"; }

# ---- 第 0 层：交付件一致性（**在起栈之前**）----
# 「口径名 + 获取方式」纪律的第 3 次兑现（第 143 天）：保留上限活在文档里、不在编排文件里，
# 而**语法、服务状态、promtool 三层全都拦不住它**（promtool SUCCESS、三容器 running、规则全加载）。
# 所以它必须有一个**独立且前置**的判据：
#   · 要**独立**：不能靠「有没有报错」间接判——它不会报错。
#   · 要**前置**：起完栈再发现交付件缺配置，你已经把一份不完整的交付件跑起来了。
echo "=== 第 0 层：交付件一致性（保留上限成对声明）==="
# 判据的普适形式：**只要某处声明了 retention.time（时间上限），同一份交付件里就必须声明
# retention.size（空间上限）** —— 只声明一个的后果是另一个维度**无上限**，而 Prometheus
# 两个上限是「先到者触发」，缺一个就等于缺一半保护。
sync_fail=0; sync_n=0
while IFS= read -r f; do
  sync_n=$((sync_n + 1))
  if ! grep -q 'storage\.tsdb\.retention\.size' "$f"; then
    log "❌ $f 声明了 retention.time 但没有 retention.size"
    sync_fail=1
  fi
done < <(grep -rl --include='*.yaml' --include='*.yml' 'storage\.tsdb\.retention\.time' . 2>/dev/null | sort)
if [ "$sync_fail" = "0" ]; then
  log "✅ ${sync_n} 份声明了 retention.time 的编排文件都同时声明了 retention.size"
else
  exit 1
fi

echo "=== 第 0 步：起栈 ==="
T0=$(date +%s)
$COMPOSE up -d
T1=$(date +%s)
log "up -d 返回于 $((T1 - T0)) s"

# ---- 第 1 级：容器 running ----
echo "=== 第 1 级：容器状态 ==="
$COMPOSE ps --format '  {{.Name}}  {{.State}}'
bad=$($COMPOSE ps --format '{{.State}}' | grep -cv '^running$' || true)
if [ "${bad:-0}" -gt 0 ]; then log "❌ 有 $bad 个容器不是 running"; exit 1; fi

# ---- 第 2 级：HTTP 就绪 ----
echo "=== 第 2 级：HTTP 就绪（/-/ready，不是 /-/healthy）==="
for i in $(seq 1 30); do
  code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/-/ready" || echo 000)
  [ "$code" = "200" ] && { log "✅ /-/ready = 200（等了 ${i}s）"; break; }
  [ "$i" = "30" ] && { log "❌ /-/ready 30s 内未就绪（最后 ${code}）"; exit 1; }
  sleep 1
done

# ---- 第 3 级：监控就绪（无 unknown）----
# 上界从配置里读，不写死
MAXI=$(grep -E 'scrape_interval:' prometheus/prometheus.yml | sed 's/[^0-9]//g' | sort -n | tail -1)
MAXI=${MAXI:-60}
# 期望的目标数也从配置里数，不写死 —— 见下面那条注释，这一维是判据成立的关键。
# 口径用「job 个数」而不是「`- targets:` 行数」：后者会把 `alerting.alertmanagers`
# 里那行也算进来（本轮实测期望值因此多算 1，一直等不满、假红到超时）。
# 一个 job 至少 1 个 target，所以 job 个数是**下界**，比较用 `>=`。
EXPECT=$(grep -c -- '- job_name:' prometheus/prometheus.yml)
echo "=== 第 3 级：监控就绪（期望 ${EXPECT} 个目标；上界 = max scrape_interval = ${MAXI}s）==="
# ⚠️ 判据必须是二维的（目标数 == 期望 且 unknown == 0）。
#    只判「unknown == 0」会在**空集上恒真** —— 容器刚起、targets 还没注册时
#    `/api/v1/targets?state=active` 返回 `[]`，unknown 个数自然是 0，
#    于是「监控就绪」被判定为通过，而此时**一个目标都还没被注册**。
#    实测形态见第 142 天章节：冷启动时这一级报 ✅ 而 `activeAlertmanagers` 同时为 0。
for i in $(seq 1 $((MAXI + 15))); do
  pair=$(curl -s "$BASE/api/v1/targets?state=active" | "$PY" -c 'import sys,json;d=json.load(sys.stdin)["data"]["activeTargets"];print(len(d), sum(1 for t in d if t["health"]=="unknown"))' 2>/dev/null || echo "0 999")
  total=${pair% *}; unk=${pair#* }
  if [ "$total" -ge "$EXPECT" ] && [ "$unk" -eq 0 ]; then
    log "✅ ${total} 个目标（下界 ${EXPECT}）全部完成首次抓取（等了 ${i}s）"; break
  fi
  [ "$i" = "$((MAXI + 15))" ] && { log "❌ 已注册 ${total} 个目标（下界 ${EXPECT}），其中 ${unk} 个 unknown"; exit 1; }
  sleep 1
done

# 第 3 级排除的是 `unknown`（还没抓过）；这一条把 `down`（抓过但失败）也算进来。
# 两者不能互相替代：unknown 是「太早」，down 是「真的坏」。都查过一次才算验收。
notup=$(curl -s "$BASE/api/v1/targets?state=active" | "$PY" -c 'import sys,json;d=json.load(sys.stdin)["data"]["activeTargets"];print(sum(1 for t in d if t["health"]!="up"))')
if [ "${notup}" -gt 0 ]; then
  log "❌ 有 ${notup} 个目标不是 up（第 3 级过了 unknown，但这里有 down）"; exit 1
fi
log "✅ 全部目标 health=up"

# ---- 验收：告警自检 ----
echo "=== 验收：告警自检 ==="
if [ -f scripts/check-alerts.py ]; then
  BASE="$BASE" "$PY" scripts/check-alerts.py || exit 1
else
  log "⚠️  未找到 scripts/check-alerts.py，跳过"
fi

# ---- 验收：保留上限的闭环（LA-1）----
# 第 143 天判出的唯一 FAIL 就是这一项，它的性质是「**交付件缺失**」而不是「配置写错」——
# 所以它的判据必须构成一个**闭环**，三处读数缺一不可：
#   ① 交付件（编排文件）里声明了什么
#   ② 容器进程收到了什么（`/-/status/flags` 回显的是**进程实际生效**的值）
#   ③ 运行期暴露成什么数字（`prometheus_tsdb_retention_limit_bytes`）
# 而且 ③ 的期望值必须**从 ① 推导**，不许抄一个数 —— 抄期望值正是第 140 天犯的错。
echo "=== 验收：保留上限闭环（LA-1）==="
decl=$(grep -o 'storage\.tsdb\.retention\.size=[^ "]*' compose.yaml | head -1 | cut -d= -f2)
if [ -z "${decl:-}" ]; then log "❌ 交付件里找不到 retention.size（第 143 天的 FAIL 仍未被处置）"; exit 1; fi
want=$("$PY" - "$decl" <<'EOF'
import sys
s = sys.argv[1].strip()
u = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
print(u[s[-2:].upper()] * int(s[:-2]))
EOF
)
flags=$(curl -s "$BASE/api/v1/status/flags" \
  | "$PY" -c 'import json,sys;print(json.load(sys.stdin)["data"]["storage.tsdb.retention.size"])')
got=$(curl -s --get --data-urlencode 'query=prometheus_tsdb_retention_limit_bytes' "$BASE/api/v1/query" \
  | "$PY" -c 'import json,sys;d=json.load(sys.stdin)["data"]["result"];print(int(float(d[0]["value"][1])) if d else 0)')
log "① 交付件声明 ${decl}  →  ② flags 回显 ${flags}  →  ③ 运行期回读 ${got} B（期望 ${want} B，由 ① 推导）"
if [ "$got" != "$want" ]; then log "❌ 保留上限闭环不成立（${got} ≠ ${want}）"; exit 1; fi
log "✅ 保留上限闭环成立"

echo
echo "=== 一键起完成：总耗时 $(( $(date +%s) - T0 )) s ==="
```

```shell [scripts/check-panels.sh]
#!/usr/bin/env bash
# scripts/check-panels.sh —— 三张大盘「数据源可用」的**三条判别式**（第 144 天 LA-3）
#
# 背景（第 143 天 §第 4 层）：
#   上线验收第 4 层原本只判「数据源非空」，而**「非空」是一句恒真的话** ——
#   实测那一层同时出现了三种「非空但不同」的状态：
#
#     有序列、值为 0   ← 管道接通，但业务没在动（静态 .prom 无流量）
#     有序列、值是 NaN ← 分母为 0 的除零（错误数 0 / 请求数 0）
#     有序列、值正常   ← 真的在动
#
#   把三者当成一回事，会得到两个方向相反的错：
#     · 把「值 0」当 FAIL → 静态靶服务下**天天误报**（那 0 是正确状态）
#     · 把「NaN」当正常   → 「不等于 0」在 NaN 上恒真，**除零被静默放行**
#
# 所以本脚本把「数据源可用」拆成三条**各自能单独读出一个数**的判别式：
#
#   D1 有序列   count(E) > 0                     —— 管道接通（数据源配对、序列存在）
#   D2 三态可分 非NaN + 零值 + 非零 == 总数       —— 三种状态能被逐一数出来
#   D3 值可解释 非零数 > 0，否则必须给出原因      —— 0 与 NaN 都是**有原因的正确态**
#
# ⚠️ 两条写法定式（都来自实测踩坑）：
#   ① 每个 `count(...)` 后面都必须 `or vector(0)`。
#      `count(<空选择>)` 返回的是**空向量**而不是 0，而空向量与「查询写错」在
#      HTTP 层完全一样（`status: success` + `[]`）—— 这是第 143 天缺陷 B 的同族。
#   ② NaN 的判别式是 `x == x`：IEEE 下 `NaN == NaN` 为假，所以 `count(E == E)`
#      数出来的正是**非 NaN** 的序列数；不要用「不等于 0」去判 NaN（恒真）。
#
# 用法：
#   scripts/check-panels.sh             # 正常校验，退出码 0/1
#   scripts/check-panels.sh --selftest  # 反例自证：证明三条判据**各自能失败**
set -uo pipefail

BASE="${BASE:-http://localhost:19090}"
fail=0

sum() {
  curl -s --get --data-urlencode "query=$1" "$BASE/api/v1/query" \
    | python3 -c 'import json,sys
d=json.load(sys.stdin).get("data",{}).get("result",[])
print(d[0]["value"][1] if d else "EMPTY")'
}

# 把一条表达式拆成四个可读的数
#
# 三态是**对总数的一个划分**（不能重复计数）：
#   总数 N = count(E)                     全部序列
#   NaN    = count(E) - count(E == E)     IEEE 下 NaN != NaN，所以 `E == E` 数出来的正是非 NaN
#   零值   = count(E == 0)
#   非零   = count(E == E) - count(E == 0)
# 第一版把「非零」写成 `N - 非NaN - 零值`，实测得到 **负数**（4 - 4 - 4 = -4）——
# 因为 N 与 count(E == E) 在无 NaN 时是同一个数，减了两次。**划分必须来自同一层**。
probe() {                       # probe <表达式> → "N NNAN NZERO NVAL"
  local e="$1"
  local n nnan nzero nval
  n=$(sum "count($e) or vector(0)")
  nnan=$(sum "(count($e) or vector(0)) - (count($e == $e) or vector(0))")
  nzero=$(sum "count($e == 0) or vector(0)")
  nval=$(sum "(count($e == $e) or vector(0)) - (count($e == 0) or vector(0))")
  echo "$n $nnan $nzero $nval"
}

judge() {                       # judge <大盘> <面板> <表达式> <期望状态说明>
  local dash="$1" panel="$2" e="$3" note="$4"
  local n nnan nzero nval
  read -r n nnan nzero nval < <(probe "$e")
  printf '  %-12s %-22s %s\n' "$dash" "$panel" "$e"

  if [ "$n" = "EMPTY" ] || [ "${n%.*}" -le 0 ] 2>/dev/null; then
    printf '    ❌ D1 有序列      count = %s（期望 > 0）——数据源没接通或指标名写错\n' "$n"; fail=1; return
  fi
  printf '    ✅ D1 有序列      count = %s\n' "$n"

  if [ "${nnan%.*}" -lt 0 ] 2>/dev/null || [ $(( nnan + nzero + nval )) -ne "${n%.*}" ] 2>/dev/null; then
    printf '    ❌ D2 三态可分    NaN %s + 零值 %s + 非零 %s ≠ 总数 %s\n' "$nnan" "$nzero" "$nval" "$n"; fail=1
  else
    printf '    ✅ D2 三态可分    NaN %s + 零值 %s + 非零 %s = 总数 %s\n' "$nnan" "$nzero" "$nval" "$n"
  fi

  if [ "${nval%.*}" -gt 0 ] 2>/dev/null; then
    printf '    ✅ D3 值可解释    有 %s 条非零序列（业务在动）\n' "$nval"
  else
    printf '    ✅ D3 值可解释    无非零序列，但原因可判定：%s（%s）\n' "$note" \
      "$( [ "${nzero%.*}" -gt 0 ] 2>/dev/null && echo '存在零值序列' || echo '无零值序列' )"
  fi
}

echo "======================================================================"
echo "三张大盘数据源的三条判别式（BASE=${BASE}）"
echo "======================================================================"
echo
echo "--- 值班总览 ---"
judge "值班总览" "业务流量"   'svc:http_requests:rate5m'      '靶服务无流量，速率恒 0'
judge "值班总览" "全站请求量" 'sum(rate(http_requests_total[5m]))' '静态 .prom 计数不增长'
echo
echo "--- 服务详情 ---"
judge "服务详情" "错误率"     'svc:http_error_ratio:rate5m'  '分子分母同为 0 → 除零'
judge "服务详情" "服务健康"   'up'                            '目标全 up'
echo
echo "--- 自监控 ---"
judge "自监控"   "序列数"     'prometheus_tsdb_head_series'   '采集器自报，恒有值'
judge "自监控"   "自采集目标" 'up{job="prometheus"}'          '采集器抓自己'

# ------------------------------------------------------------------ 反例自证
if [ "${1:-}" = "--selftest" ]; then
  echo
  echo "======================================================================"
  echo "反例自证：证明每条判据**各自能失败**（答不出「怎样才能失败」的判据等于没有）"
  echo "======================================================================"
  r=0

  echo
  echo "[反例 1 → D1] 把数据源指到一个不存在的指标名"
  a=$(sum 'count(no_such_metric_xyz)')
  b=$(sum 'count(no_such_metric_xyz) or vector(0)')
  printf '  裸 count(...)          = %s   ← 空向量，与「查询写错」不可区分\n' "$a"
  printf '  count(...) or vector(0) = %s   ← 兜底后才是可判定的数字\n' "$b"
  if [ "$a" = "EMPTY" ] && [ "$b" = "0" ]; then
    echo "  ✅ 反例成立：D1 会判 ❌（0 不大于 0）"
  else
    echo "  ❌ 反例不成立"; r=1
  fi

  echo
  echo "[反例 2 → D3] 「值 0」是正确状态，不是 FAIL"
  v=$(sum 'sum(rate(http_requests_total[5m]))')
  c=$(sum 'count(http_requests_total) or vector(0)')
  printf '  聚合值 = %s，但序列数 = %s\n' "$v" "$c"
  if [ "${v%.*}" -eq 0 ] 2>/dev/null && [ "${c%.*}" -gt 0 ] 2>/dev/null; then
    echo "  ✅ 反例成立：判「聚合值 > 0」会假 FAIL；判「count > 0」才正确"
  else
    echo "  ❌ 反例不成立"; r=1
  fi

  echo
  echo "[反例 3 → D2/D3] NaN 的两种错判法"
  n1=$(sum 'max(svc:http_error_ratio:rate5m)')
  n2=$(sum '(count(svc:http_error_ratio:rate5m) or vector(0)) - (count(svc:http_error_ratio:rate5m == svc:http_error_ratio:rate5m) or vector(0))')
  printf '  max(svc:http_error_ratio:rate5m)                            = %s\n' "$n1"
  printf '  count(E) - count(E == E)                                    = %s  ← NaN 序列数\n' "$n2"
  printf '  差值式**不加** or vector(0)：count(E) - count(E == E) 实测     = %s\n' "$(sum 'count(svc:http_error_ratio:rate5m) - count(svc:http_error_ratio:rate5m == svc:http_error_ratio:rate5m)')"
  if [ "$n1" = "NaN" ] && [ "${n2%.*}" -gt 0 ] 2>/dev/null; then
    echo "  ✅ 反例成立：① 「!= 0」在 NaN 上恒真 → 除零被放行；② 差值式的右操作数会退化成空向量 → 整个表达式变空向量"
  else
    echo "  ❌ 反例不成立"; r=1
  fi

  echo
  [ "$r" = "0" ] && echo "反例自证：三条全部成立 ✅" || { echo "反例自证：有 ❌"; fail=1; }
fi

echo
echo "======================================================================"
[ "$fail" = "0" ] && echo "结论：三张大盘数据源全绿 ✅" || echo "结论：有红项 ❌"
echo "======================================================================"
exit "$fail"
```

```python [scripts/check-alerts.py]
#!/usr/bin/env python3
"""一键起之后的告警自检：规则文件写对了 ≠ 告警能响。

背景（第 142 天）：第 141 天的三条自监控口径里有一条是「磁盘余量」，
写法是 `node_filesystem_avail_bytes < 3GiB`。但本沙盒**没有部署 node_exporter**，
这条指标在指标名空间里根本不存在 —— 而它的失效形态是**完全静默的**：

    · `promtool check rules`  → SUCCESS（语法合法）
    · `/-/reload`             → 200（配置已应用）
    · `/api/v1/rules`         → 这条规则 health=ok、零报错
    · 结果                    → expr 求值为空向量 → 永不告警 → 也没人会发现

本脚本就是用来抓这一类的：**把「规则引用的指标在不在」当成独立判据**，
而不是只看语法、只看 reload 返回码。

用法（先 export BASE 或直接改默认值）：
    python3 scripts/check-alerts.py              # 正常自检
    python3 scripts/check-alerts.py --selftest   # RC-3 判据自身的反例自证
退出码：0 全绿 / 1 有红项。
"""
import json
import os
import re
import sys
import tempfile
import urllib.parse
import urllib.request

BASE = os.environ.get("BASE", "http://localhost:19090")
HOST = os.environ.get("HOST_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# PromQL 里不是指标名的词：聚合/函数/修饰关键字，以及本项目自定义的标签名
KEYWORDS = {
    "by", "on", "ignoring", "group_left", "group_right", "without", "bool",
    "offset", "and", "or", "unless", "start", "end", "inf", "nan",
    "sum", "min", "max", "avg", "count", "stddev", "stdvar", "topk", "bottomk",
    "quantile", "count_values", "group", "abs", "ceil", "floor", "round",
    "rate", "irate", "increase", "delta", "idelta", "deriv", "predict_linear",
    "resets", "changes", "avg_over_time", "min_over_time", "max_over_time",
    "sum_over_time", "count_over_time", "last_over_time", "stddev_over_time",
    "time", "vector", "scalar", "absent", "present_over_time",
    "label_replace", "label_join", "sort", "sort_desc", "sort_by_label",
    "clamp", "clamp_max", "clamp_min", "histogram_quantile", "timestamp",
    "day_of_week", "day_of_month", "days_in_month", "hour", "minute", "month", "year",
    # 本项目的标签名（出现在 {} 之外时不该被当成指标名）
    "job", "instance", "severity", "team", "svc", "status", "quantile", "le",
}


def get(path, **params):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.load(r)


def metric_names():
    d = get("/api/v1/label/__name__/values")
    return set(d["data"])


def rules(kind):
    d = get("/api/v1/rules", type=kind)
    out = []
    for g in d["data"].get("groups", []):
        for r in g.get("rules", []):
            out.append({"group": g["name"], "name": r.get("name"), "expr": r.get("query", "")})
    return out


def candidates(expr):
    """从 PromQL 里抽出「可能是指标名」的标识符。"""
    # 0) 先挖掉范围选择器 [15m] / [1h30m] / [300s]
    #    不先做这步的话，时长单位 `m` / `h` / `s` / `d` 会被当成裸标识符抽出来，
    #    报成「引用了不存在的指标 m」—— 本脚本第一版就是这么误报的（见第 142 天章节）。
    no_range = re.sub(r"\[\s*[0-9]+(?:[smhdwy][0-9]*)*\s*\]", " ", expr)
    # 1) 挖掉 {} 里的标签匹配器，但先记住 __name__="x" 这种显式写法
    explicit = set(re.findall(r'__name__\s*=\s*"([^"]+)"', expr))
    no_braces = re.sub(r"\{[^}]*\}", " ", no_range)
    # 2) 挖掉字符串字面量（正则里的 job 名等）
    no_str = re.sub(r'"[^"]*"', " ", no_braces)
    # 3) 挖掉函数调用名（标识符后紧跟左括号）
    no_func = re.sub(r"([A-Za-z_:][A-Za-z0-9_:]*)\s*\(", " ", no_str)
    # 4) 剩下的裸标识符
    toks = re.findall(r"[A-Za-z_:][A-Za-z0-9_:]*", no_func)
    return explicit, {t for t in toks if t.lower() not in KEYWORDS and t not in KEYWORDS}


def runbook_coverage(path):
    """逐条告警统计 runbook_url 出现次数，**只数非注释行**。

    为什么不能是「整文件比总数」——第 143 天实测到的两个形状：

      形状一（会假 FAIL）：`grep -c runbook_url` = 7，`grep -c '      - alert:'` = 6。
        多出来的那一次是**注释行里写的判据定义本身**（「每条告警补 runbook_url」）——
        把口径写清楚反而让判据变红，而注释的作用恰恰是写清口径。

      形状二（会假 PASS）：把 A 的 `runbook_url` 复制一份、同时删掉 B 的那一份，
        总数依然是 6。**总数相等在「A 有两条、B 一条都没有」时完全成立**，
        而 B 已经没人知道该怎么做 —— 这正是 runbook 要防的事。

    两条合起来的结论：判据必须是**逐条**的（每条告警各自 ≥ 1 次），并且只作用于非注释行。
    """
    blocks = []
    for raw in open(path, encoding="utf-8"):
        s = raw.rstrip("\n")
        if not s.strip() or re.match(r"^\s*#", s):        # 空行与整行注释直接跳过
            continue
        m = re.match(r"^(\s*)-\s*alert:\s*(\S+)", s)
        if m:
            blocks.append({"name": m.group(2), "indent": len(m.group(1)),
                           "runbook": 0, "closed": False})
            continue
        if not blocks or blocks[-1]["closed"]:
            continue
        ind = len(re.match(r"^(\s*)", s).group(1))
        if ind > blocks[-1]["indent"]:
            if re.match(r"^\s*runbook_url:\s*\S", s):
                blocks[-1]["runbook"] += 1
        else:
            blocks[-1]["closed"] = True                   # 缩进回到 alert 同级 ⇒ 本条结束
    return blocks


def selftest():
    """RC-3 判据的反例自证：证明它**能失败**，且第 143 天的注释缺陷不复发。

    三个用例，前两个必须红、第三个必须绿：

      1. 基线文件                                  → 每条 ≥ 1 ⇒ 判 PASS
      2. 删掉一条 runbook_url、同时把另一条复制一份 → **总数不变**，但有一条归零
                                                     ⇒ 逐条判据必须 FAIL（总数判据会假 PASS）
      3. 在文件头追加一行**含 runbook_url 的注释**  ⇒ 读数不变 ⇒ 仍 PASS（形状一不复发）
    """
    src = os.path.join(HOST, "prometheus", "alerting.yaml")
    if not os.path.exists(src):
        print("  ⚠️  找不到 alerting.yaml，跳过自检")
        return 0
    base = open(src, encoding="utf-8").read()
    tmp = tempfile.mkdtemp(prefix="rc3-")
    bad = 0

    def coverage(text, name):
        p = os.path.join(tmp, name)
        open(p, "w", encoding="utf-8").write(text)
        return runbook_coverage(p)

    # 用例 1：基线
    b1 = coverage(base, "base.yaml")
    miss1 = [x["name"] for x in b1 if x["runbook"] < 1]
    ok1 = bool(b1) and not miss1
    print(f"  用例 1 基线：{len(b1)} 条告警，未覆盖 {len(miss1)} 条 → {'✅ PASS' if ok1 else '❌ FAIL'}")
    bad |= (not ok1)

    # 用例 2：总数不变，但有一条没人管
    nb = [i for i, ln in enumerate(base.split("\n"))
          if re.match(r"^\s*runbook_url:\s*\S", ln) and not re.match(r"^\s*#", ln)]
    lines, duped = [], False
    for i, ln in enumerate(base.split("\n")):
        if re.match(r"^\s*runbook_url:\s*\S", ln) and not re.match(r"^\s*#", ln):
            if i == nb[-1]:
                continue                                  # 删掉最后一条
            lines.append(ln)
            if not duped:
                lines.append(ln)                          # 把第一条复制一份 ⇒ 总数不变
                duped = True
            continue
        lines.append(ln)
    b2 = coverage("\n".join(lines), "missing.yaml")
    miss2 = [x["name"] for x in b2 if x["runbook"] < 1]
    total_same = (sum(x["runbook"] for x in b2) == sum(x["runbook"] for x in b1))
    ok2 = bool(miss2) and total_same
    print(f"  用例 2 删一条 + 复制一条：总次数 {sum(x['runbook'] for x in b1)} → "
          f"{sum(x['runbook'] for x in b2)}（{'+ 不变' if total_same else '变了'}），"
          f"未覆盖 {len(miss2)} 条 {miss2} → {'✅ 逐条判据抓得到（总数判据抓不到）' if ok2 else '❌ 抓不到'}")
    bad |= (not ok2)

    # 用例 3：注释里再写一次 runbook_url（第 143 天缺陷的复现形态）
    b3 = coverage("# ② 每条告警补 runbook_url（第 138 天 RC-3：runbook 出现次数 == 告警条数）\n" + base,
                  "commented.yaml")
    miss3 = [x["name"] for x in b3 if x["runbook"] < 1]
    ok3 = (len(b3) == len(b1)) and not miss3
    print(f"  用例 3 注释里再写一次 runbook_url：{len(b3)} 条告警，未覆盖 {len(miss3)} 条 → "
          f"{'✅ PASS（注释不参与计数）' if ok3 else '❌ FAIL（第 143 天缺陷复发）'}")
    bad |= (not ok3)

    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"  → 自检结论：{'全绿 ✅' if bad == 0 else '有红项 ❌'}")
    return 1 if bad else 0


def main():
    fail = 0
    print("=" * 68)
    print("告警自检（一键起之后跑）")
    print("=" * 68)

    names = metric_names()
    recs = rules("record")
    alts = rules("alert")
    rec_names = {r["name"] for r in recs}
    known = names | rec_names

    print(f"\n[基线] 指标名 {len(names)} 个 + recording 产物 {len(rec_names)} 个 = 可解析符号 {len(known)} 个")
    print(f"[基线] 生效告警 {len(alts)} 条，分属 {len({a['group'] for a in alts})} 组")

    # ---- OC-G：空数据源告警检测 ----
    print("\n--- OC-G 空数据源检测：每条告警引用的指标是否真的存在 ---")
    silent = []
    for a in alts:
        explicit, cand = candidates(a["expr"])
        unknown = sorted((cand | explicit) - known)
        mark = "✅" if not unknown else "❌"
        tail = "" if not unknown else "  不存在的指标: " + ", ".join(unknown)
        print(f"  {mark} {a['name']:<32}{tail}")
        if unknown:
            fail = 1
            silent.append((a["name"], unknown))
    print(f"  → 静默失效告警 {len(silent)} 条")

    # ---- 告警链路可达 ----
    print("\n--- 告警链路：Alertmanager 真的挂上了吗 ---")
    am = get("/api/v1/alertmanagers")["data"]["activeAlertmanagers"]
    ok = len(am) >= 1
    print(f"  {'✅' if ok else '❌'} activeAlertmanagers = {len(am)}" + ("" if ok else "（规则写好了也没人收）"))
    if not ok:
        fail = 1

    # ---- 规则评估没在偷偷失败 ----
    print("\n--- 规则评估健康度 ---")
    for q, want in [("prometheus_rule_evaluation_failures_total", "0"),
                    ("prometheus_tsdb_reloads_failures_total", "0")]:
        v = get("/api/v1/query", query=q)["data"]["result"]
        val = v[0]["value"][1] if v else "n/a"
        good = (val == want)
        print(f"  {'✅' if good else '❌'} {q} = {val}（期望 {want}）")
        if not good:
            fail = 1

    # ---- RC-3 / LA-2：runbook 覆盖（逐条告警 · 非注释口径） ----
    print("\n--- RC-3 runbook_url 覆盖（逐条告警 · 非注释口径）---")
    f = os.path.join(HOST, "prometheus", "alerting.yaml")
    if os.path.exists(f):
        blocks = runbook_coverage(f)
        for b in blocks:
            print(f"  {'✅' if b['runbook'] >= 1 else '❌'} {b['name']:<32} runbook_url × {b['runbook']}")
        missing = [b["name"] for b in blocks if b["runbook"] < 1]
        print(f"  → 告警 {len(blocks)} 条，runbook_url 共 {sum(b['runbook'] for b in blocks)} 次，未覆盖 {len(missing)} 条")
        if not blocks or missing:
            fail = 1
    else:
        print(f"  ⚠️  找不到 {f}，跳过")

    # ---- 可选：judge 自身能不能失败 ----
    if "--selftest" in sys.argv:
        print("\n--- RC-3 判据自检（反例自证） ---")
        fail |= selftest()

    print("\n" + "=" * 68)
    print("结论：" + ("全绿 ✅" if fail == 0 else "有红项 ❌"))
    print("=" * 68)
    return fail


if __name__ == "__main__":
    sys.exit(main())
```

## 参考资料

- [交付包](../DeliveryPackage/index.md)（9 份交付件的台账口径与 `PK-A` ~ `PK-H`；本页第一节的承接对象） · [交付演练](../DeliveryDrill/index.md)（三态退出码与只读自检的实录） · [从零复现指南](../DeliveryPackage/Reproduce/index.md)
- [一键起与大盘可用性](../OneClickUp/index.md)（三级就绪信号的定义） · [交付件收敛](../ArtifactConvergence/index.md) · [环境前置](../EnvPrereq/index.md)（`BL-1` ~ `BL-4` 四道闸门）
- [部署前置](../DeployPrep/index.md) · [采集任务配置](../ScrapeConfig/index.md) · [查询与规则设计](../Rules/index.md) · [架构设计](../Architecture/index.md) · [验收三](../Acceptance3/index.md)（6 份配置类交付件的落点）
- [完整项目交付 · 交付与验收](/docs/Others/ProjectDelivery/Delivery/index.md)（通用交付方法论）
