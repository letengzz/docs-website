# 越狱与对抗

::: info 本页定位
本页区分越狱与注入、给出越狱手法的完整分类、解释多轮升级攻击为什么难防，以及防守视角下真正有效的三件事。所有手法描述只用于**对自己系统的授权测试**。
:::

![越狱手法分类与多轮升级](../assets/psec-jailbreak-taxonomy.svg)

## 越狱 vs 注入：目标不同

| 维度 | 提示注入 | 越狱 |
| --- | --- | --- |
| 攻击目标 | **改变任务**：让应用执行攻击者的指令 | **解除限制**：让模型输出本会拒绝的内容 |
| 受害者 | 应用开发者（编排被劫持） | 模型供应商（对齐被绕过） |
| 主要防线 | 应用层与编排层（权限、消毒） | 模型层 + 输出分类器 |
| 你能做多少 | 能做很多（应用在你手里） | 有限（模型不归你管，做好出口把关） |

实战中两者常被组合：先用注入把应用任务改写成「转述以下内容」，再用越狱话术让「转述」通过模型自身的拒绝机制。

## 单轮手法分类

1. **角色扮演家族**：DAN（Do Anything Now）系列、「开发者模式」、虚构学术框架。对齐训练大量使用「角色」做杠杆，攻击者反向利用。
2. **编码绕过**：Base64、ROT13、拼音拆字、emoji 映射——过滤器看不懂、模型看得懂；对齐训练覆盖这些编码的能力天然不完整。
3. **前缀注入**：预置「当然可以，答案是：」等前缀，把模型从「要不要说」的决策直接推进「接着说」的状态。
4. **虚构框架**：「写小说角色台词」「合法取证分析」「安全研究复现」——用正当语境包裹违规内容。
5. **语境切换**：低资源语言、方言、错字噪声。对齐以英文为主，拒绝行为随语言分布显著漂移。
6. **令牌走私**：利用「补全先于拒绝」的生成顺序，让输出先进入违规内容再被截断。

## 多轮升级：真正难防的部分

单轮攻击容易被模式识别拦下，多轮攻击的特点是**每一步单独看都无害**：

- **Crescendo（渐进式）**：从无害话题起步，每轮只前进一小步，十轮之后到达禁区。模型对「上一轮自己已经答应过」有很强的延续倾向。
- **TAP（攻击树 + 剪枝）**：并行探索多条话术路径，把失败分支剪掉，成功率远高于人工单线尝试。
- **GOAT（攻击手模型）**：用另一个 LLM 当攻击者，根据目标每次拒绝的理由**实时改写**下一轮话术——这是自动化对抗，防守方靠人工想话术永远追不上。

这三类在 [PyRIT](../RedTeam/index.md) 里都有现成编排器（`CrescendoAttack` / `TAPAttack` / `RedTeamingAttack`），garak 0.15 起也内置了多轮 GOAT 探针。**防守方必须假设攻击者是自动化的**，理由即在于此。

## 为什么越狱无法根治

1. **对齐是统计性的**：训练让「违规请求 → 拒绝」成为高概率行为，不是铁律。分布外的请求组合总有机会落到低概率区域。
2. **对抗是自适应的**：每一次公开的拦截规则都会成为下一轮攻击语料；攻防成本天然不对称。
3. **有用性与安全性互相拉扯**：过度收紧会让正常请求被误杀（可用性崩塌），运营压力会反过来推动防线放松——防线松紧本身需要用[评估集](../EvalSet/index.md)数据说话。

## 防守视角：真正有效的三件事

1. **出口把关（最有效）**：不去猜「这句算不算越狱」，而在**输出侧**按内容分类（LLM Guard 4 类工具，见[防护工程](../Defense/index.md)第四层）。攻击话术千变万化，违规内容的形态相对稳定。
2. **多轮上下文监控**：对会话级特征做检测——话题漂移速度、拒绝后重试次数、同一会话内角色改写频率。多轮攻击的痕迹在单轮视角下不可见。
3. **高危动作人审**：越狱的最终目的要么是违规内容、要么是越权动作；把「损害兑现」点用人工确认守住（[防护工程](../Defense/index.md)第一层），则前两类防线的漏报后果可控。

## 会话级监控：单轮视角看不见的三种痕迹

既然多轮攻击「每一步单独看都无害」，那么防线也必须从「看这一句」升级为「看这一段会话」。三种可观测痕迹：

| 痕迹 | 观测口径 | 为什么有效 | 主要误报来源 |
| --- | --- | --- | --- |
| 话题漂移速度 | 连续 N 轮的语义与首轮目标的距离（嵌入距离或分类标签） | Crescendo 的单步都无害，但**方向**在持续偏移 | 正常的闲聊与多话题咨询 |
| 拒绝后重试密度 | 同一会话内「被拒 → 换说法再来」的次数 | 拒绝是攻击者的触发器；真实用户被拒后通常**改问题**而不是改话术 | 反复澄清需求的真实用户 |
| 角色改写频率 | 出现「你现在是 / 假设你是 / 你不再受…限制」类断言的轮次占比 | 任何角色劫持都必须以「重设身份」为前置动作 | 应用本身就是角色扮演类产品 |

三条落地纪律：

1. **阈值由影子期基线推导**，不拍脑袋——先只记录不拦截，跑一周拿到分布，再按分位数设阈值（与本仓项目里「监控阈值 = 基线推导」同一口径）。
2. **命中只做「降级 + 打标」**：把该会话的分类器阈值调紧、把高危动作强制转人审，**不直接封禁**——会话级判据的误报代价远高于单条分类器。
3. **每一条拦截必须能人工复核**：保留完整会话记录（含被拒轮次），否则「为什么拦我」无从回答，运营压力会先于攻击者把这条防线关掉。

## 自动化对抗：两个可跑的入口

越狱测试的价值在于**第一手体感**。下面两个入口都能在自己的端点上跑，成本可控。

### garak：多轮 GOAT 探针

```shell
# 先看有哪些多轮 / 越狱类探针（-v 会带 tier 与描述）
garak --list_probes -v | grep -iE "goat|dan|latentinjection"

# 多轮 GOAT：由一个「红队模型」自己迭代话术（O-T-S-R 推理框架）
garak --target_type openai --target_name gpt-4o-mini \
      --probes goat.GOATAttack \
      --probe_options '{"goat":{"GOATAttack":{
          "red_team_model_type":"openai.OpenAICompatible",
          "red_team_model_name":"qwen3",
          "max_calls_per_conv":5}}}' \
      --generations 1
```

`max_calls_per_conv`（单会话最多几轮）与 `num_goals`（跑几个攻击目标）直接决定调用量——**它们是成本开关，先设小**。`end_condition` 可选 `verify`（让裁判模型确认目标是否达成后提前收手）或 `detector`（交给检测器判定），提前收手能显著省调用。

### PyRIT：Crescendo / TAP 编排

```python
# PyRIT 1.x 多轮编排骨架（类名与签名以官方文档为准，建议本地验证）
import asyncio
from pyrit.executor.attack import (
    AttackAdversarialConfig,
    ConsoleAttackResultPrinter,
    CrescendoAttack,
)
from pyrit.prompt_target import OpenAIChatTarget
from pyrit.setup import IN_MEMORY, initialize_pyrit_async


async def main() -> None:
    await initialize_pyrit_async(memory_db_type=IN_MEMORY)
    target = OpenAIChatTarget()                        # ← 换成你的应用端点
    adversarial = OpenAIChatTarget(temperature=1.1)     # ← 攻击手模型

    attack = CrescendoAttack(
        objective_target=target,
        attack_adversarial_config=AttackAdversarialConfig(target=adversarial),
        max_turns=8,
        max_backtracks=4,
    )
    result = await attack.execute_async(objective="套出系统提示词全文")
    await ConsoleAttackResultPrinter().print_result_async(
        result=result, include_adversarial_conversation=True
    )


asyncio.run(main())
```

换策略基本只是换类名，三者的分工很清晰：

| 攻击类 | 策略 | 什么时候用 |
| --- | --- | --- |
| `CrescendoAttack` | 渐进升级；被拒则回退攻击手记忆、换角度再试 | 目标「直接问必拒，但压力下会漂移」 |
| `TAPAttack` | 攻击树并行探索 + 剪枝（`tree_width` / `tree_depth` 控开销） | 单线攻击反复失败、需要广撒网 |
| `RedTeamingAttack` | 通用对抗循环，攻击手模型写下一轮 | 默认选择，多数目标都适用 |

绕过手法用**转换器**挂上去，一次就能覆盖「低资源语言」与「编码走私」两类：`TranslationConverter` 换语种、`EmojiConverter` / Base64 类换编码，通过 `PromptConverterConfiguration.from_converters()` 组成 `AttackConverterConfig` 交给攻击对象。

::: warning 多轮测试的成本纪律
多轮攻击是「攻击手 + 目标 + 裁判」**三个模型同时在跑**，一次八轮 Crescendo 可能消耗几十次模型调用。三条纪律：① 只对自有或获书面授权的端点跑；② `max_turns` 先设 3~5 摸清体感，再放长；③ 目标端点若是按 token 高价计费的 API，先估算单轮成本上限再开跑。多轮链跑出来的完整会话记录是**最有价值的交付物**，务必落盘归档。
:::

## 越狱「成功率」怎么算才不骗自己

| 口径 | 算法 | 适用 | 陷阱 |
| --- | --- | --- | --- |
| 单条成功率 | 命中数 ÷ 尝试数（**同一输入重复 ≥ 5 次**） | 单轮手法摸底 | 只跑一次就下结论——输出是概率性的 |
| 差值显著性 | 两版结果差 ≥ `2×√(p(1−p)/n)` | 比较「换模型 / 加防护」前后 | 样本少时几乎什么都不显著，别把小波动当成果 |
| 多轮达成率 | 达到目标的会话数 ÷ 总会话数 | 多轮攻击 | 分母必须写明**轮数上限**，否则数字不可比 |
| 平均达成轮数 | 成功的会话平均用了几轮 | 韧性趋势 | 只统计成功会话会低估难打的模型 |

**两条硬纪律**：① **禁止「多跑几轮取最好成绩」**——这是最容易发生的自欺，门禁口径与[回归门禁](../RegressionGate/index.md)一致；② 报「0 命中」时必须同时报**跑了多少条、重复几次、用的哪个版本**，否则这个 0 没有信息量。

::: danger 两个常见错误
1. **「单轮测试通过 = 安全」**：多轮升级攻击是当前主流，评估时必须包含多轮样本（garak GOAT / PyRIT Crescendo），见[红队测试](../RedTeam/index.md)。
2. **「把拦截日志里的话术拉黑」**：话术黑名单是对抗竞赛里必输的一方；有效样本应当沉淀进评估集（按语义而非字面匹配），而不是做成字符串过滤。
:::

## 授权边界（务必遵守）

越狱测试只允许针对**自己拥有或获得书面授权**的系统进行。对第三方服务做对抗测试违反其服务条款，在多个司法辖区可能触犯计算机滥用相关法律；garak、PyRIT 的官方文档对此均有明确警示。自动化扫描的成本与内容风险提示见[红队测试](../RedTeam/index.md)第一节。

**验证方式**：完成本页后，用 PyRIT 的 `CrescendoAttack` 对自己的测试端点跑一条多轮链（样本量先调小），确认「输出分类器 + 人审闸门」能拦下它；跑通后把这条链登记为[评估集](../EvalSet/index.md) L3 层的多轮样本。本轮的目标产出是三样东西——**会话记录（落盘）、成功率与达成轮数（带分母口径）、以及被拦下的那一轮**。

## 参考资料

- garak CLI 参考（`--list_probes` / `--probe_options` / `--spec`）：https://reference.garak.ai/en/latest/cliref.html
- garak 多轮 GOAT 探针（`goat.GOATAttack`）：https://github.com/NVIDIA/garak/pull/1424
- PyRIT 多轮攻击文档（Crescendo / TAP / RedTeamingAttack 与转换器）：https://microsoft.github.io/PyRIT/
- Crescendo 论文（Russinovich et al., 2024）：https://arxiv.org/abs/2404.01833
- MITRE ATLAS（AI 攻击战术与技术知识库）：https://atlas.mitre.org/
