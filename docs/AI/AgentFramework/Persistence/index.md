# 持久化与记忆

LangGraph 的持久化分两层，解决的问题不同：**Checkpointer（检查点）** 让一次运行「随时暂停、随时恢复、随时回放」，服务的是**流程连续性**；**Store（记忆库）** 让数据「跨线程、跨会话」还在，服务的是**长期记忆**。混着设计会导致要么什么都存、存储爆炸，要么关键状态根本没落库。

![检查点与 Store 的分工](../assets/afw-persistence.svg)

## 1. 三个概念：thread、checkpointer、store

| 概念 | 是什么 | 生命周期 | 典型用法 |
| --- | --- | --- | --- |
| **thread** | 一次运行的身份标识（`thread_id`） | 一个会话 / 一个工单 | 同一 `thread_id` 再 `invoke` 即恢复 |
| **Checkpointer** | 每个超步后把**整份状态**快照落库 | 跟随 thread | 断点续跑、`interrupt` 暂停、时间旅行 |
| **Store** | 跨 thread 的键值 / 向量存储 | 跟随用户 / 应用 | 用户偏好、长期画像、跨会话事实 |

::: tip 一句话理解
**Checkpointer 记「这一次跑到哪了」，Store 记「这个用户是谁」。** 崩溃恢复、人工审批靠前者；「上次聊过他偏好简洁回答」靠后者。
:::

## 2. Checkpointer 后端选型

```python
from langgraph.checkpoint.memory import InMemorySaver        # 测试
from langgraph.checkpoint.sqlite import SqliteSaver          # 单机
from langgraph.checkpoint.postgres import PostgresSaver      # 生产
```

| 后端 | 场景 | 注意 |
| --- | --- | --- |
| `InMemorySaver` | 本地开发、单测 | 进程退出即失；**多 worker 不共享** |
| `SqliteSaver` | 单机脚本、原型 | 并发写受限；不适合 Web 多进程部署 |
| `PostgresSaver` | **生产默认选择** | 需执行 `setup()` 建表；支持连接池 |
| 社区后端（Redis / MongoDB 等） | 已有基础设施复用 | 版本与 `langgraph` 主版本要兼容，先跑通恢复用例再上生产 |

```python
import psycopg
from langgraph.checkpoint.postgres import PostgresSaver

DB_URI = "postgresql://user:pass@localhost:5432/agents"
with psycopg.connect(DB_URI, autocommit=True) as conn:
    checkpointer = PostgresSaver(conn)
    checkpointer.setup()                       # 首次运行建表，幂等
    graph = builder.compile(checkpointer=checkpointer)

    cfg = {"configurable": {"thread_id": "order-2026-1001"}}
    graph.invoke(inputs, cfg)                  # 崩溃后同 cfg 再 invoke 即恢复
```

::: danger 多 worker 部署的三条硬要求
1. **所有 worker 连同一个检查点库**——用内存检查点部署两个副本，等于每个副本各活各的，恢复必然丢状态。
2. **`thread_id` 必须全局唯一且可路由**——同一 thread 的两次请求可能落在不同 worker，靠库共享状态。
3. **状态里不要放不可序列化对象**（连接句柄、文件句柄）——检查点要序列化整份状态，放了就在恢复时炸。
:::

## 3. 检查点的四个能力

```python
cfg = {"configurable": {"thread_id": "t-1"}}

# ① 看当前状态（values 是状态，next 是即将执行的节点）
snap = graph.get_state(cfg)
print(snap.values, snap.next)

# ② 列出全部历史检查点（时间旅行的目录）
for s in graph.get_state_history(cfg):
    print(s.config["configurable"]["checkpoint_id"], s.next)

# ③ 从任意检查点重放（换一条路试试）
old = next(s for s in graph.get_state_history(cfg) if ...)
graph.invoke(None, s.config)          # 传 None 即从该检查点继续

# ④ 人工修改状态后继续（修数据、补字段）
graph.update_state(cfg, {"draft": "人工修正后的草稿"})
```

| 能力 | 生产用途 | 滥用后果 |
| --- | --- | --- |
| 恢复 | 进程重启 / 部署发布后流程继续 | 用内存检查点则全失效 |
| 暂停（配合 `interrupt`） | 人工审批可以隔天甚至隔周回来 | 无检查点的暂停只能进程挂着 |
| 时间旅行 | 排障：回到出事前一步，换个输入重放 | 全量历史永久保留 → 存储爆炸 |
| `update_state` | 修正数据后继续，不重跑前置节点 | 绕过节点逻辑乱改状态 → 状态与业务不一致 |

## 4. 保留策略：检查点必须会过期

每步都落库意味着**写放大**。一个 50 步流程跑完产生 50 份快照，状态里再放大对象，几天就能把库撑爆。生产三件事：

1. **按时间或条数清理**：终态 thread 的历史检查点只保留 N 天 / 最近 M 条；进行中的 thread 至少保留最近一份。
2. **状态瘦身**：大对象存 URI，用时取；把「可推导数据」从状态里剔出去（两份真相必然漂移）。
3. **监控两件事**：检查点表体积增速、单次检查点写入延迟——劣化最先出现在这两处。

## 5. Store：跨线程的长期记忆

```python
from langgraph.store.memory import InMemoryStore
from langgraph.store.postgres import PostgresStore

store = PostgresStore(conn)                 # 与 checkpointer 同库也可
graph = builder.compile(checkpointer=checkpointer, store=store)

# 节点内部通过 get_store() 读写，按 (namespace, key) 组织
def remember(state):
    store.put(("users", state["user_id"]), "prefs", {"style": "concise"})

def greet(state):
    prefs = store.get(("users", state["user_id"]), "prefs")
    ...
```

| 需求 | 用哪个 | 原因 |
| --- | --- | --- |
| 「本次会话」的上下文与恢复 | Checkpointer | 随 thread 生命周期 |
| 「这个用户」的偏好 / 画像 | Store | 跨 thread 存活 |
| 「上次检索过的文档」缓存 | Store 或外部缓存 | 与流程状态无关，别混进检查点 |

::: warning 别把 Store 当数据库用
Store 是给「Agent 记忆」设计的键值 / 向量接口，不是业务数据库。业务事实（订单、权限）留在业务库里，Agent 通过工具查询——把业务数据复制进 Store 会造成两份真相。
:::

## 6. 易错点清单

1. **忘了 `compile(checkpointer=...)`**：`interrupt` 与恢复全部静默失效（不报错，就是不停）。
2. **每次请求换 `thread_id`**：恢复无从谈起——thread_id 要在会话 / 工单维度稳定。
3. **内存检查点上生产多副本**：见第 2 节三条硬要求。
4. **状态里放大对象**：检查点膨胀、变慢——存 URI。
5. **历史检查点永不过期**：存储爆炸——按第 4 节定保留策略。
6. **把业务数据复制进 Store**：两份真相——业务事实留业务库。

## 7. 验证方式

1. **恢复生效**：`invoke` 到一半 `kill -9` 进程，重启后同 `thread_id` 再 `invoke`，确认从断点继续（用 `stream_mode="updates"` 看节点从中间开始）。
2. **时间旅行可用**：`get_state_history` 列出 ≥ 3 条检查点，指定其中一条 `invoke(None, ...)` 能重放。
3. **多 worker 共享**：起两个进程连同一 Postgres，A 进程 `invoke` 后 B 进程 `get_state` 能看到状态。
4. **清理生效**：插入超过保留期的假检查点，跑清理任务后确认被删、进行中 thread 的最新检查点还在。
5. **Store 隔离**：换一个 `user_id` 确认读不到前一个用户的 `prefs`。

## 相关文档

- [LangGraph 状态机深入](../StateGraph/index.md)：状态设计直接决定检查点体积
- [人工介入工程化](../HumanLoop/index.md)：`interrupt` 依赖检查点才能「暂停一周再继续」
- [LangChain · 记忆与上下文](../../LangChain/Memory/index.md)：四层记忆模型与本页 checkpointer/store 的对应
- [Agent 应用 · 记忆与上下文](../../Agent/MemoryContext/index.md)：记忆分层的框架无关方法论

## 参考资料

- LangGraph 持久化（官方）：https://docs.langchain.com/oss/python/langgraph/persistence
- PostgresSaver / Deepdive（官方）：https://langchain-ai.github.io/langgraph/reference/checkpoints/
- Store（官方）：https://docs.langchain.com/oss/python/langgraph/memory
