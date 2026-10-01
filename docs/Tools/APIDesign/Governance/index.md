# 治理机制：Lint 门禁与破坏性变更拦截

**一句话定位**：前一页讲了「什么算破坏性变更」，这一页讲**怎么让它真的被拦住**——规则集怎么写、门禁在哪几层跑、失败怎么处理、例外怎么申请，以及**怎么证明门禁不是摆设**。

![治理四层门禁](../assets/apidesign-governance.svg)

::: info 版本口径（2026-10 核对）
| 工具 | 当前状态 | 定位 |
| --- | --- | --- |
| **Spectral**（`@stoplight/spectral-cli`） | 持续迭代，Apache-2.0 | 规则集**完全可自定义**，是「把团队规范写成可执行检查」的标准答案；支持 OpenAPI 3.x、AsyncAPI、Arazzo |
| **Redocly CLI** | **v2.46.x** 线（2026-08-07） | lint / bundle / 预览一体；`generate-client` 仍为实验特性；内置规则偏向「让文档渲染得好」 |
| **Vacuum** | Go 单二进制，**兼容 Spectral 规则集** | 速度快，适合大仓 / monorepo 的 CI 加速；生态比 Spectral 年轻 |
| **oasdiff** | Go 单二进制，Apache-2.0 | 专做**两份契约的差异与破坏性变更判定**，Lint 工具替代不了 |
| **openapi-spec-validator** | Python 包 | 只做**结构合法性**校验，不做风格 |
| **Swagger Editor / swagger-cli** | 只做合法性校验 | 会放行一份「每个属性命名风格都不同」的契约——**合法性是地板，不是天花板** |

**注意分工**：合法性校验（validator）与风格校验（linter）是两件事，必须都跑。前者保证工具能解析，后者保证人能读懂、生成器能产出可用的名字。
:::

## 1. 规则集：治理的地基

「门禁」这个词容易让人以为只要接一个 CI 步骤。但如果规则集是空的（只有工具内置默认规则），门禁实际检查的只是「文档合法不合法」——**它拦不住任何风格问题**。

团队规范必须落成**可执行的规则**。下面是可直接使用的起点：

```yaml [.spectral.yaml]
# 继承 Spectral 官方 oas 规则集（结构、示例、description 的基础检查）
extends: ["spectral:oas"]

rules:
  # ── 命名与标识 ──
  operation-operationId: error          # 每个 operation 必须有 operationId
  operation-operationId-unique: error   # 全局唯一，客户端生成器依赖它
  path-kebab-case:
    description: 路径段使用 kebab-case（小写字母、数字、连字符）
    severity: error
    given: $.paths
    then:
      function: pattern
      functionOptions:
        match: '^(\/([a-z0-9]+(-\w+)*|\{[a-zA-Z0-9_]+\}))+$'

  # ── 契约完整性 ──
  operation-4xx-response: error         # 每个 operation 至少声明一个 4xx
  operation-success-response: error     # 至少声明一个成功响应
  response-content-defined:
    description: 2xx 响应必须声明 content（只写 description 等于空壳）
    severity: error
    given: $.paths[*][get,post,put,patch,delete].responses[?(@property.match(/^2/))]
    then:
      field: content
      function: truthy

  # ── 分页与安全 ──
  page-size-upper-bound:
    description: size 参数必须声明上限（防止一次拖垮数据库）
    severity: error
    given: $.paths[*][get].parameters[?(@.name=='size')]
    then:
      field: schema.maximum
      function: truthy

  # ── 团队约定 ──
  tag-defined: warn                     # 每个 operation 应带 tags
  description-required: warn            # info.description 与 operation.description
```

::: danger 规则集的三个实现要点
1. **`severity` 要分清 error 与 warn**。全是 error 会让人一开始就绕过门禁（改完要 20 分钟）；全是 warn 等于没门禁。经验值：**命名、完整性这类「写错了就没法用」的判 error；文档质量、可读性判 warn**。
2. **正则必须真的测过**。上面 `path-kebab-case` 的 `given: $.paths` 是把 `match` 作用在**键名**上的写法，不同工具的 `given` 语义有差异——**写完一定要用一份「故意写坏的」契约验证它会报错**（见第 5 节）。
3. **`extends` 里的官方规则集不要整体关闭**。要停用某条内置规则时，用 `off` 精确关闭并**在规则旁写清为什么**，否则半年后没人知道这条为什么关着。
:::

## 2. 四层门禁的落点

### 2.1 第 ① 层：编辑器

装上 Spectral 或 Redocly 的编辑器扩展，仓库根放规则集文件，扩展自动加载。**这是投入产出比最高的一层**——问题在产生的瞬间就被指出来，成本接近零。

### 2.2 第 ② 层：pre-commit

```yaml [.pre-commit-config.yaml]
repos:
  - repo: local
    hooks:
      - id: openapi-lint
        name: OpenAPI 契约 lint（error 级失败即阻断）
        entry: npx @stoplight/spectral-cli lint
        args: ["--fail-severity=error"]
        language: system
        files: '^docs/api/.*\.ya?ml$'
```

::: tip `--fail-severity=error` 是必须的
默认情况下 Spectral **即使发现问题也返回 0**（它把结果当作"报告"）。不加这个参数，hook 永远"通过"——**这是最常见的一处「门禁看起来在跑，实际什么也没拦」**。
:::

### 2.3 第 ③ 层：PR 门禁

```yaml [.github/workflows/api-contract.yml]
name: API 契约门禁
on:
  pull_request:
    paths: ['docs/api/**']

jobs:
  contract:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }

      - name: ① 结构合法
        run: |
          python3 -m pip install --quiet openapi-spec-validator pyyaml
          python3 -m openapi_spec_validator docs/api/openapi.yaml

      - name: ② 规则集（error 即失败）
        run: npx --yes @stoplight/spectral-cli lint docs/api/openapi.yaml --fail-severity=error

      - name: ③ 多文件可打包
        run: npx --yes @redocly/cli@latest bundle docs/api/openapi.yaml -o /tmp/bundle.yaml

      - name: ④ 破坏性变更检测（与上一个基线比）
        run: |
          BASE=$(git show origin/main:docs/api/openapi.baseline.yaml > /tmp/baseline.yaml && echo /tmp/baseline.yaml)
          go install github.com/oasdiff/oasdiff@latest
          oasdiff breaking "$BASE" docs/api/openapi.yaml
```

::: warning 基线从哪来
基线必须是**「上一次真正发布出去的契约」**，而不是「上一次提交的契约」。做法：在发布流水线里把当时的契约复制到 `docs/api/openapi.baseline.yaml` 并提交（或打 tag）。

如果基线取 `origin/main` 的当前值，那么**同一个 PR 里连续改两次契约**时，第二次的对比对象已经包含了第一次的改动——破坏性变更会被"自己人"掩盖。
:::

### 2.4 第 ④ 层：发布后对账

前三层管不住「线上多出来的东西」。第 ④ 层做两件事：

| 检查 | 做法 | 能发现什么 |
| --- | --- | --- |
| **契约 ↔ 实现导出** | 测试环境用 springdoc / FastAPI 导出 `impl.json`，与契约做 `oasdiff diff` | 实现偷偷多出的参数、少掉的错误分支 |
| **契约 ↔ 真实流量** | 从网关 / 访问日志抽取实际被调用的路径与方法，与契约的 `paths` 求差集 | **影子接口**（契约里没有但线上在被调用） |

```shell
# 契约 ↔ 实现：差异即缺陷
oasdiff diff docs/api/openapi.yaml impl.json

# 契约 ↔ 流量：找出契约里没有的路径（影子接口）
python3 - <<'PY'
import yaml, re, subprocess
doc = yaml.safe_load(open('docs/api/openapi.yaml', encoding='utf-8'))
declared = {p.rstrip('/') for p in doc.get('paths', {})}
# 从真实访问日志里抽取路径（示例：nginx access log，第二列是 request 行）
log = subprocess.run(['cat', 'access.log'], capture_output=True, text=True).stdout
observed = set()
for line in log.splitlines():
    m = re.search(r'"(?:GET|POST|PUT|PATCH|DELETE) ([^ ]+)', line)
    if m:
        observed.add(re.sub(r'/\d+', '/{id}', m.group(1).split('?')[0]))
shadow = observed - declared
print('契约已声明:', len(declared), ' 线上实际:', len(observed))
print('影子接口:', sorted(shadow) or '无')
assert len(observed) > 0, '日志里没抽到任何请求——先确认日志格式与文件路径'
PY
```

::: danger 「活性判据」是这类脚本的生命线
上面每个脚本都带一条 `assert len(...) > 0`。原因不是形式主义：**契约治理脚本最常见的失效方式是「扫到了空集合，于是报告一切正常」**——路径写错、日志格式变了、YAML 解析失败后静默返回 `{}`，都会得到一份漂亮的绿色报告。

**凡是以「有没有问题」为结论的脚本，都必须先证明「确实扫到了东西」。**
:::

## 3. 例外怎么申请

治理最容易被推翻的方式是「这次的例外先放过」。**不给例外通道，就会有人绕过整个机制**。所以要做的是**让例外可见、有时效、有负责人**：

```yaml [docs/api/waivers.yaml]
# 契约治理例外登记表
waivers:
  - rule: operation-4xx-response
    path: /health
    reason: 健康检查是基础设施探针，不存在业务错误分支
    owner: "@platform-team"
    expires: 2026-12-31        # 过期后自动重新变红
  - rule: path-kebab-case
    path: /legacy/GetUserList
    reason: 已对外发布且无法迁移，计划在 2027-Q1 随 v1 一起 Sunset
    owner: "@user-team"
    expires: 2027-03-31
```

三个字段缺一不可：

| 字段 | 作用 | 缺了会怎样 |
| --- | --- | --- |
| `reason` | 说明为什么这次是合理的 | 后面的人无法判断能否沿用 |
| `owner` | 谁负责在 `expires` 前消掉它 | 例外变成永久豁免 |
| `expires` | **过期自动变红** | 例外永久化，规则名存实亡 |

## 4. 常见反模式

| 反模式 | 表现 | 修法 |
| --- | --- | --- |
| **门禁无规则集** | 只跑工具默认规则，命名风格千奇百怪却全绿 | 把团队规范写成 `.spectral.yaml` |
| **到处 `warn`** | CI 永远成功，输出几百条黄色日志没人看 | 命名与完整性类判 `error`，并逐步把存量问题清零 |
| **`--fail-severity` 没设** | Spectral 报告问题但退出码 0 | 必须显式加参数 |
| **基线跟着 HEAD 走** | 破坏性变更被自己掩盖 | 基线取「上一次发布的契约」 |
| **例外无 expires** | 例外永久化 | 加 `expires` 并按周扫描过期项 |
| **只查契约不查实现** | 实现偷偷多出参数，契约变成一厢情愿 | 第 ④ 层做契约 ↔ 实现 diff |
| **门禁挡住发布却没人能改** | 团队绕过门禁（`--no-verify`） | 保证修复成本低于绕过成本：先补齐工具链、再扩大规则范围 |

## 5. 验证方式：证明门禁有牙齿

这是本页最重要的一节。**没有做过变异测试的门禁，其绿色结论不可信。**

```shell
# ① 规则集生效性：故意写坏一份契约，确认报 error
cp docs/api/openapi.yaml /tmp/broken.yaml
python3 - <<'PY'
import yaml
d = yaml.safe_load(open('/tmp/broken.yaml', encoding='utf-8'))
p = next(iter(d['paths']))                       # 取第一个路径
d['paths']['/Bad_Path_UPPER'] = d['paths'].pop(p) # 换成违反 kebab-case 的路径
yaml.safe_dump(d, open('/tmp/broken.yaml', 'w', encoding='utf-8'), allow_unicode=True)
PY
npx @stoplight/spectral-cli lint /tmp/broken.yaml --fail-severity=error
echo "退出码应为非 0；若为 0，说明规则没生效"

# ② 删掉 operationId，确认报 error
python3 - <<'PY'
import yaml
d = yaml.safe_load(open('/tmp/broken.yaml', encoding='utf-8'))
for path, item in d['paths'].items():
    for m, op in item.items():
        op.pop('operationId', None)
yaml.safe_dump(d, open('/tmp/broken.yaml', 'w', encoding='utf-8'), allow_unicode=True)
PY
npx @stoplight/spectral-cli lint /tmp/broken.yaml --fail-severity=error   # 期望非 0

# ③ 破坏性变更门禁：删一个响应字段，确认 oasdiff 报错
cp docs/api/openapi.yaml /tmp/new.yaml
python3 - <<'PY'
import yaml
d = yaml.safe_load(open('/tmp/new.yaml', encoding='utf-8'))
s = d['components']['schemas']
target = next(k for k, v in s.items() if v.get('type') == 'object' and v.get('properties'))
del s[target]['properties'][next(iter(s[target]['properties']))]   # 删掉一个字段
yaml.safe_dump(d, open('/tmp/new.yaml', 'w', encoding='utf-8'), allow_unicode=True)
PY
oasdiff breaking docs/api/openapi.yaml /tmp/new.yaml    # 期望退出码非 0
```

::: tip 三步都跑过一遍，再宣布「门禁已上线」
这三步分别验证了**风格规则、完整性规则、破坏性变更检测**三类门禁的有效性。任何一步的退出码是 0，说明那一道门禁实际上没在工作——此时它带来的是**虚假的安全感**，比没有门禁更糟。
:::

## 6. 参考资料

- [Spectral 文档 · 自定义规则集](https://docs.stoplight.io/docs/spectral/)：`rules` / `given` / `then` 的完整语义
- [Spectral 内置 OAS 规则集](https://docs.stoplight.io/docs/spectral/docs/reference/openapi-rules)：开箱可用的规则清单
- [Redocly CLI · 配置与规则](https://redocly.com/docs/cli/configuration/)：`redocly.yaml` 与自带规则
- [oasdiff](https://github.com/Tufin/oasdiff)：`breaking` / `diff` / `changelog` 三个子命令
- [Vacuum](https://github.com/daveshanley/vacuum)：兼容 Spectral 规则集的快速实现
- [openapi-spec-validator](https://github.com/python-openapi/openapi-spec-validator)：结构合法性校验
- [OWASP API Security Top 10](https://owasp.org/API-Security/)：API9:2023 不当资产清单管理（影子接口）
- 相邻页：[OpenAPI 契约工程化](../OpenAPI/index.md)、[版本策略与兼容性演进](../Versioning/index.md)、[实战](../Practice/index.md)
