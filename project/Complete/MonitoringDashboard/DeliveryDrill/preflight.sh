#!/usr/bin/env bash
# 第 146 天交付演练 · 第 0 步：前置自检（**只读**）
#
# 为什么第 0 步必须是一个脚本，而不是文档里的一段「请先确认…」清单：
#   第 145 天写出的三份交付文档，第 0 步原文是 `bash scripts/preflight.sh` —— 而**这个
#   文件当时并不存在**，它所在的 `/tmp/monitoring-run/docs/` 与 `/tmp/monitoring-run/scripts/`
#   在第二天做演练时都已经不在了。于是那条判据（`DD-G`）当天得到的读数是「退出码 1」，
#   第二天复跑得到的却是 `No such file or directory` + rc=127。
#
#   这两件事**不是同一种失败**，这也是本脚本存在的原因：
#     · 检查不通过（rc=1）：环境不干净 —— 这是**结论**；
#     · 判据不可执行（rc=2）：连判失败的机会都没有 —— 这是**输入丢失**。
#   把两者混成一个「没通过」，就等于承认「判据的输入可以不交付」。
#
# 退出码（三态，刻意区分）：
#   0  前置齐备且检查全绿
#   1  前置齐备，但有检查项未通过（环境脏）
#   2  前置缺失到无法判定（沙盒目录 / docker / curl 不可用）——**不可执行**，不是失败
#
# 全部动作**只读**：不启停容器、不写任何文件（`MANIFEST.txt` 的校验也是只读的）。
# 唯一会写盘的动作被排除在外：本脚本不生成 MANIFEST，生成它是另一个动作（见当日文档第四节）。
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SANDBOX="${SANDBOX:-/tmp/monitoring-run}"
BASE="${BASE:-http://localhost:19090}"
AM="${AM:-http://localhost:9093}"
PY="${PY:-python3}"

pass=0; miss=0; skip=0; blocking=0
# 刻意**不做列对齐**：printf 的 `%-Ns` 按字节计数，中文标签每字 3 字节，
# 标签一长一短就会把「期望」列推得参差不齐——看起来像排版事故，实际是宽度口径不同。
# 交付脚本的输出第一要求是**能被 grep 稳定认出来**，不是好看，所以固定成 key=value 形态。
ok()   { printf '  [OK]    %s：期望=%s 实测=%s\n' "$1" "$2" "$3"; pass=$((pass+1)); }
no()   { printf '  [MISS]  %s：期望=%s 实测=%s\n' "$1" "$2" "$3"; miss=$((miss+1)); }
sk()   { printf '  [SKIP]  %s：原因=%s\n' "$1" "$2"; skip=$((skip+1)); }
blk()  { printf '  [BLOCK] %s：期望=%s 实测=%s\n' "$1" "$2" "$3"; blocking=$((blocking+1)); }

echo "=== 第 0 步：前置自检（只读）==="
echo "沙盒 SANDBOX=$SANDBOX"
echo "--- A. 前置工具与目录（决定「能不能判」）---"

# ---- A1/A2：沙盒目录。目录不存在时后面所有检查都无从谈起，直接判 2 ----
if [ -d "$SANDBOX" ]; then
  ok "沙盒目录" "存在" "$SANDBOX"
else
  blk "沙盒目录" "存在" "缺失：$SANDBOX"
fi

if command -v docker >/dev/null 2>&1; then
  if docker version --format '{{.Server.Version}}' >/dev/null 2>&1; then
    ok "docker CLI + daemon" "client 与 daemon 均可达" \
      "$(docker version --format '{{.Client.Version}}/{{.Server.Version}}')"
  else
    blk "docker CLI + daemon" "daemon 可达" "CLI 有，daemon 不可达"
  fi
else
  blk "docker CLI + daemon" "命令存在" "未安装 docker"
fi

if command -v curl >/dev/null 2>&1; then ok "curl" "命令存在" "$(curl --version | head -1 | cut -d' ' -f1-2)";
else blk "curl" "命令存在" "未安装 curl"; fi

if [ "$blocking" -gt 0 ]; then
  echo
  echo "前置：$pass 项通过，$blocking 项缺失 —— **不可执行**（rc=2）"
  echo "注意：这不是「检查未通过」，而是「没有输入可供检查」。两者必须分开处置。"
  exit 2
fi

echo "--- B. 交付件完整性（决定「交付的东西还是不是那一份」）---"
if [ -f "$HERE/MANIFEST.txt" ]; then
  if command -v shasum >/dev/null 2>&1; then
    sha_tool=(shasum -a 256)
  elif command -v sha256sum >/dev/null 2>&1; then
    sha_tool=(sha256sum)
  else
    sha_tool=()
  fi
  if [ "${#sha_tool[@]}" -eq 0 ]; then
    sk "本仓交付件指纹" "本机无 shasum / sha256sum"
  else
    # 数「有几条 OK」而不是「有几条不 OK」：`shasum -c` 在不一致时会**额外**打印一行
    # `WARNING: n computed checksum did NOT match`，用「非 OK 行数」当失败数会把这一行
    # 也算成一项失败（首轮实测：改一个字节报出「2 项不一致」，而清单里只有 2 项）。
    total_n=$(grep -c '^[0-9a-f]\{64\}  ' "$HERE/MANIFEST.txt" || true)
    ok_n=$( (cd "$HERE" && "${sha_tool[@]}" -c MANIFEST.txt) 2>/dev/null | grep -c ': OK$' || true)
    if [ "${ok_n:-0}" = "$total_n" ]; then
      ok "本仓交付件指纹" "${total_n} 项 sha256 全部一致" "OK ${ok_n}/${total_n}"
    else
      no "本仓交付件指纹" "${total_n} 项 sha256 全部一致" "仅 ${ok_n}/${total_n} 项一致"
    fi
  fi
else
  no "本仓交付件清单" "MANIFEST.txt 存在" "缺失"
fi

echo "--- C. 编排文件与「成对声明」判据（第 0 层，起栈之前就该查）---"
COMPOSE_FILE="$SANDBOX/compose.yaml"
if [ -f "$COMPOSE_FILE" ]; then
  ok "编排文件" "存在" "$COMPOSE_FILE"
  pairs=0; pair_bad=0
  while IFS= read -r f; do
    pairs=$((pairs+1))
    grep -q 'storage\.tsdb\.retention\.size' "$f" || pair_bad=$((pair_bad+1))
  done < <(grep -rl --include='*.yaml' --include='*.yml' 'storage\.tsdb\.retention\.time' "$SANDBOX" 2>/dev/null | sort)
  if [ "$pairs" = "0" ]; then
    no "保留上限成对声明" "≥1 份文件声明 time+size" "0 份文件声明 retention.time"
  elif [ "$pair_bad" = "0" ]; then
    ok "保留上限成对声明" "${pairs} 份都成对" "OK ${pairs}/${pairs}"
  else
    no "保留上限成对声明" "${pairs} 份都成对" "${pair_bad} 份只声明了 time"
  fi
else
  no "编排文件" "存在" "缺失：$COMPOSE_FILE"
fi

echo "--- D. 运行态（栈已在跑时才有意义）---"
running=$(cd "$SANDBOX" 2>/dev/null && docker compose ps --format '{{.State}}' 2>/dev/null | grep -c '^running$' || echo 0)
if [ "${running:-0}" = "3" ]; then ok "容器 running" "3 个" "3 个";
else no "容器 running" "3 个" "${running:-0} 个（未起栈时这是预期，起栈后不是）"; fi

http_code() { curl -s -o /dev/null -w '%{http_code}' --max-time 5 "$1" 2>/dev/null || echo 000; }

c=$(http_code "$BASE/-/ready")
if [ "$c" = "200" ]; then ok "Prometheus /-/ready" "200" "200"; else no "Prometheus /-/ready" "200" "$c"; fi
c=$(http_code "$AM/-/ready")
if [ "$c" = "200" ]; then ok "Alertmanager /-/ready" "200" "200"; else no "Alertmanager /-/ready" "200" "$c"; fi

if ! command -v "$PY" >/dev/null 2>&1; then
  sk "抓取目标与规则" "本机无 $PY，无法解析 JSON"
else
  t=$(curl -s --max-time 5 "$BASE/api/v1/targets?state=any" 2>/dev/null | "$PY" -c \
      "import sys,json
try:
    d=json.load(sys.stdin)['data']['activeTargets']
except Exception:
    print('-,-'); raise SystemExit
print('%d,%d' % (len(d), sum(1 for x in d if x['health']=='up')))" 2>/dev/null || echo "-,-")
  # 切分用 `##*,` 而**不是** `##*, `：后者把分隔符定义成「逗号+空格」，
  # 而 Python 端输出的是 `5,5`（无空格），于是永远切不开，两个值会一起进「实测」。
  tn=${t%%,*}; tu=${t##*,}
  if [ "$tu" = "$tn" ] && [ "$tn" != "-" ]; then ok "抓取目标 health=up" "全 up" "${tu}/${tn} up";
  else no "抓取目标 health=up" "全 up" "${tu}/${tn} up"; fi

  r=$(curl -s --max-time 5 "$BASE/api/v1/rules" 2>/dev/null | "$PY" -c \
      "import sys,json
try:
    g=json.load(sys.stdin)['data']['groups']
except Exception:
    print('-,-'); raise SystemExit
al=sum(1 for x in g for y in x['rules'] if y['type']=='alerting')
rc=sum(1 for x in g for y in x['rules'] if y['type']=='recording')
print('%d,%d' % (al, rc))" 2>/dev/null || echo "-,-")
  al=${r%%,*}; rc=${r##*,}
  if [ "$al" = "6" ]; then ok "告警规则条数" "6" "$al"; else no "告警规则条数" "6" "$al"; fi
  if [ "$rc" = "3" ]; then ok "记录规则条数" "3" "$rc"; else no "记录规则条数" "3" "$rc"; fi
fi

echo
if [ "$miss" = "0" ]; then
  echo "前置：$pass 项通过，0 项缺失，$skip 项跳过 —— 全绿（rc=0）"
  exit 0
fi
echo "前置：$pass 项通过，$miss 项缺失，$skip 项跳过 —— 环境未就绪（rc=1）"
echo "读法：rc=1 是**结论**（环境脏），rc=2 是**输入丢失**（不可执行）。两者不可合并。"
exit 1
