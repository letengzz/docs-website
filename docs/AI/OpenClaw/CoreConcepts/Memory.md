# 记忆系统（Memory）

OpenClaw 的记忆系统通过 **纯文本 Markdown 文件** 实现持久化。模型只能在当前窗口内"看到"信息，真正的持久化记忆依赖于写入文件的机制。

## 记忆层次

OpenClaw 的记忆分为三个层次：

| 层次 | 文件 | 内容特点 | 加载方式 |
|------|------|---------|---------|
| **会话记忆** | JSONL 会话文件 | 当前会话的完整对话历史 | 自动加载（上下文窗口内） |
| **每日笔记** | `memory/YYYY-MM-DD.md` | 每日发生的事情、决策、上下文 | 今天 + 昨天自动加载 |
| **长期记忆** | `MEMORY.md` | 策划后的重要事实、偏好、决策 | 主会话（DM）启动时注入 |

### 会话记忆

会话记忆是 Agent 在**当前会话**中的对话历史，存储在：

```
~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl
```

- 对话历史以 JSONL 格式逐行存储
- 会话 ID 由 OpenClaw 确定，保持稳定
- 会话记忆受模型**上下文窗口限制**，超长对话会自动触发压缩（Compaction）

### 每日笔记（Daily Notes）

每日笔记是 Agent 在 `memory/YYYY-MM-DD.md` 中记录的工作日志：

- **自动加载**：会话启动时自动加载今天和昨天的笔记
- **原始记录**：包含当天的对话要点、决策、事件
- **不受上下文注入限制**：不触发截断警告（使用 `memory_get` / `memory_search` 工具按需访问）

### 长期记忆（MEMORY.md）

`MEMORY.md` 是经过筛选的"策划记忆"：

- **仅在主会话加载**：不会注入到群聊、子 Agent 等共享环境中
- **策划式维护**：只保留重要信息，而非原始日志
- **定期更新**：通过心跳检查，Agent 可以审查每日笔记并将重要内容提升到 `MEMORY.md`

::: warning 安全提示
`MEMORY.md` 包含个人上下文，仅在直接对话（DM）中加载。不要在群聊、共享频道中暴露此文件的内容。
:::

## 记忆工具

OpenClaw 提供两个核心记忆工具：

### memory_search — 语义搜索

```bash
# 在记忆中搜索相关内容
openclaw memory search "上次讨论的部署方案"
```

- 支持**混合搜索**（向量相似度 + 关键词匹配）
- 即使措辞不同也能找到相关内容
- 自动检测可用的 Embedding 提供商（OpenAI、Gemini、Voyage、Mistral）

### memory_get — 精确读取

```bash
# 读取特定日期或范围的记忆
openclaw memory search "2026-04-29" --exact
```

- 读取特定记忆文件或行范围
- 支持精确文件和行号定位

## 记忆后端

OpenClaw 支持多种记忆存储后端：

| 后端 | 特点 | 适用场景 |
|------|------|---------|
| **Builtin（默认）** | 基于 SQLite，开箱即用，支持混合搜索 | 标准使用 |
| **QMD** | 本地优先，支持重排序、查询扩展、索引外部目录 | 大规模记忆管理 |
| **Honcho** | AI 原生跨会话记忆，用户建模 | 需要深度记忆理解 |

## 记忆更新策略

### 自动记忆刷新（Memory Flush）

在会话压缩（Compaction）之前，OpenClaw 会自动运行一个静默轮次：

1. 提醒 Agent 将重要上下文保存到记忆文件
2. 默认启用，无需额外配置
3. 确保压缩过程不丢失关键信息

::: tip 工作原理
记忆刷新在压缩触发前运行。如果对话中有尚未写入文件的重要事实，它们会被自动保存后才会进行摘要压缩。
:::

### 梦境机制（Dreaming）

Dreaming 是可选的后台记忆整合过程：

- **默认关闭**：需要显式启用
- **定时运行**：通过 Cron 作业自动调度
- **阈值过滤**：只有通过评分、召回频率、查询多样性门槛的内容才会被提升
- **人类可审查**：提升摘要写入 `DREAMS.md` 供人工审查

### 手动维护

你也可以直接告诉 Agent 记住某事：

> "记住，我更喜欢 TypeScript"

Agent 会自动将这条信息写入 `MEMORY.md` 或相关的 `memory/` 文件。

## 记忆搜索配置

### 启用记忆搜索

记忆搜索需要配置 Embedding 提供商：

```json5
// ~/.openclaw/openclaw.json
{
  agents: {
    defaults: {
      memorySearch: {
        enabled: true,
      },
    },
  },
}
```

如果已配置 OpenAI、Gemini、Voyage 或 Mistral 的 API Key，记忆搜索会自动启用。

### 记忆后端切换

```json5
{
  memory: {
    backend: "qmd", // builtin | qmd | honcho
    qmd: {
      includeDefaultMemory: true,
    },
  },
}
```

## 记忆 CLI 命令

```bash
# 查看索引状态和提供商
openclaw memory status

# 执行语义搜索
openclaw memory search "项目部署方案"

# 强制重建索引
openclaw memory index --force

# 执行梦境回填（将历史笔记重新评分）
openclaw memory rem-backfill --path ./memory --stage-short-term

# 回滚梦境回填
openclaw memory rem-backfill --rollback
```

## 最佳实践

### 应该记录的内容

- 重要的用户偏好和决策
- 项目的关键上下文（Git 仓库、配置路径等）
- 反复出现的问题和解决方案
- Agent 自身学到的经验教训

### 不应该记录的内容

- API Keys、密码等敏感凭证
- 私密对话的原文转储
- 过大的文件（会导致上下文膨胀）
- 纯临时性的一次性信息

### 工作空间备份

建议将工作空间纳入 **私有 Git 仓库** 进行备份：

```bash
cd ~/.openclaw/workspace
git init
git add AGENTS.md SOUL.md TOOLS.md MEMORY.md memory/
git commit -m "备份 Agent 工作空间和记忆"
```

::: danger 安全警告
即使在私有仓库中，也绝对不要提交：
- API 密钥、OAuth 令牌、密码
- `~/.openclaw/` 下的任何文件
- 敏感附件的原始数据

:::

