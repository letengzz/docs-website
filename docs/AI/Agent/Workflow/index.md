# 工作流编排

复杂任务需要把 Agent 的步骤**编排成工作流**：定义状态、条件分支、循环与终止条件。从手写循环到框架（LangGraph、Coze、Dify、n8n），按复杂度选择。

## 从代码到工作流

```text
简单：单 Agent 循环（max_steps）
中等：顺序步骤 + 条件分支
复杂：图编排（节点 + 边 + 状态）
```

## 工作流核心元素

| 元素 | 说明 |
| --- | --- |
| 节点（Node） | 一个处理步骤（LLM 调用/工具/判断） |
| 边（Edge） | 节点间流转 |
| 状态（State） | 共享的上下文与中间结果 |
| 条件分支 | 根据状态决定下一步 |
| 循环/终止 | 重试、最大步数、完成条件 |

## 顺序工作流示例

```text
输入 → 提取意图 → 查数据库 → 生成回答 → 格式校验 → 输出
                          ↓ 查询失败
                      重试 / 兜底回答
```

## 条件分支

```text
意图 = 查询天气 → 调用天气工具
意图 = 订票     → 调用订票流程（需确认）
其他           → 转人工 / 通用回答
```

## 图编排（LangGraph 示例）

```python [workflow.py]
from langgraph.graph import StateGraph

builder = StateGraph(dict)
builder.add_node("classify", classify)
builder.add_node("query", query_tool)
builder.add_node("answer", generate)
builder.add_edge("__start__", "classify")
builder.add_conditional_edges(
    "classify",
    route,
    {"weather": "query", "default": "answer"},
)
builder.add_edge("query", "answer")
builder.add_edge("answer", "__end__")
graph = builder.compile()
```

## 低代码平台

| 平台 | 特点 |
| --- | --- |
| Coze | 拖拽编排，插件丰富，适合快速原型 |
| Dify | 开源，RAG + 工作流一体 |
| n8n | 通用自动化，AI 节点扩展 |
| LangGraph | 代码化，灵活可控，适合深度定制 |

## 工作流设计原则

1. **显式状态**：中间结果存入 state，避免靠模型记忆。
2. **失败兜底**：每个工具/节点定义重试与降级。
3. **可观测**：记录每步输入输出，便于排查。
4. **人工确认点**：写操作、高影响动作插入确认节点。
5. **尽早退出**：意图明确时不要跑完整图。

## 易错点

::: danger 常见错误
1. 把工作流写成“不可变管道”：真实任务需要条件分支与循环。
2. 状态管理混乱：节点之间通过隐式上下文传数据，出错难查。
3. 没有超时/步数上限：卡死或无限循环。
4. 每步都调大模型：能用规则判断的分支用规则，省成本降延迟。
5. 忽略中间结果校验：错误数据流入后续节点。
6. 一上来就用重型框架：简单任务先手写循环，复杂再上 LangGraph。
:::

## 验证方式

1. 用一个三节点顺序工作流跑通端到端。
2. 给“查询失败”分支加兜底，模拟故障验证。
3. 记录每步耗时与 Token，评估成本。

## 参考资料

- LangGraph：https://langchain-ai.github.io/langgraph/
- Coze：https://www.coze.cn/
- Dify：https://dify.ai/
- n8n：https://n8n.io/
