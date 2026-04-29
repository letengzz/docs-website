# 智能体（Agent）

Agent 是 OpenClaw 中的核心执行单元 —— 一个拥有记忆、个性和工具能力的 AI 实体。它不仅仅是一个 LLM 对话接口，而是一个能读取文件、执行命令、搜索网络、调用 API 的自主任务执行系统。

## Agent 是什么

在 OpenClaw 中，每个 Agent 拥有完整独立的"大脑"：

- **独立的记忆系统**：通过工作空间文件（`MEMORY.md`、`memory/`）维持长期记忆
- **独立的个性配置**：通过 `SOUL.md`、`IDENTITY.md`、`USER.md` 定义其行为风格
- **独立的工作空间**：每个 Agent 有自己的工作目录、文件集合和配置
- **独立的模型配置**：每个 Agent 可以绑定不同的 LLM 提供商和模型参数
- **独立的会话存储**：`~/.openclaw/agents/<agentId>/sessions/` 下的独立会话历史

### 单 Agent vs 多 Agent

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| **单 Agent（默认）** | 一个 `main` Agent 处理所有消息 | 个人使用、单用户体验 |
| **多 Agent** | 多个隔离的 Agent，各自独立运行 | 多人共享一台服务器、不同工作场景需要不同 Agent |

::: tip 默认行为
如果不做任何配置，OpenClaw 自动运行一个 ID 为 `main` 的 Agent，工作空间位于 `~/.openclaw/workspace`，会话以 `agent:main:<mainKey>` 标识。
:::

## 工作空间（Workspace）

工作空间是 Agent 的"家" —— 它是 Agent 操作文件的默认工作目录，包含定义 Agent 行为的所有配置文件。

### 工作空间文件结构

```
~/.openclaw/workspace/
├── AGENTS.md          # Agent 操作指令和规则
├── SOUL.md            # 个性、语调和行为边界
├── USER.md            # 用户画像和偏好
├── IDENTITY.md        # Agent 的名称、风格、表情符号
├── TOOLS.md           # 本地工具使用约定和备注
├── MEMORY.md          # 长期记忆（策划式，非原始日志）
├── HEARTBEAT.md       # 心跳检查清单（可选）
├── BOOTSTRAP.md       # 首次运行仪式文件（仅新工作空间）
├── memory/            # 每日记忆日志目录
│   └── YYYY-MM-DD.md  # 每日笔记（如 2026-04-29.md）
└── skills/            # 工作空间级技能（可选）
```

### 各文件职责详解

| 文件 | 作用 | 加载时机 |
|------|------|---------|
| **AGENTS.md** | Agent 的操作指南：规则、优先级、行为准则 | 每次会话启动时自动注入 |
| **SOUL.md** | Agent 的个性：语调、边界、幽默感、价值观 | 每次会话启动时自动注入 |
| **USER.md** | 用户信息：称呼、时区、偏好 | 每次会话启动时自动注入 |
| **IDENTITY.md** | Agent 的自我认知：名称、物种、风格、Emoji | 每次会话启动时自动注入 |
| **TOOLS.md** | 本地工具备注：设备昵称、SSH 别名、TTS 语音偏好 | 每次会话启动时自动注入 |
| **MEMORY.md** | 长期策划记忆：重要事实、决策、偏好 | 仅在主会话（DM）中加载 |
| **HEARTBEAT.md** | 心跳检查清单 | 心跳运行时加载 |
| **BOOTSTRAP.md** | 一次性首次运行仪式 | 仅新工作空间创建时存在 |

::: warning 注意
工作空间文件会在每次会话启动时被**注入到上下文窗口**中。请保持文件简洁，尤其是 `MEMORY.md`（可能随时间增长）。过大的文件会被截断并标记。
:::

### 工作空间注入限制

- 单文件最大字符数：`agents.defaults.bootstrapMaxChars`（默认 12000）
- 总注入字符数上限：`agents.defaults.bootstrapTotalMaxChars`（默认 60000）
- 缺失的文件会注入一个简短标记，不阻止启动
- 子 Agent 会话只注入 `AGENTS.md` 和 `TOOLS.md`

## Agent 执行循环

Agent 的一次完整运行（Agent Loop）遵循以下生命周期：

```
┌─────────────────────────────────────────────────────┐
│                   Agent 执行循环                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. 接收消息（来自 Channel）                          │
│         │                                           │
│         ▼                                           │
│  2. 准备上下文                                       │
│     ├── 加载工作空间文件                              │
│     ├── 加载会话历史（JSONL）                         │
│     ├── 加载技能列表                                  │
│     └── 构建系统提示词                                │
│         │                                           │
│         ▼                                           │
│  3. 调用 LLM 推理                                    │
│     ├── 解析模型响应                                  │
│     ├── 如果 LLM 请求工具调用 → 步骤 4               │
│     └── 如果 LLM 直接回复 → 步骤 5                   │
│         │                                           │
│         ▼                                           │
│  4. 执行工具调用                                      │
│     ├── 验证工具权限（策略检查）                       │
│     ├── 执行工具（read / exec / search ...）         │
│     ├── 收集工具结果                                  │
│     └── 返回步骤 3（将结果注入 LLM 上下文）            │
│         │                                           │
│         ▼                                           │
│  5. 生成最终回复                                      │
│     ├── 组装文本 + 推理内容                           │
│     ├── 过滤静默令牌（NO_REPLY）                      │
│     └── 通过 Gateway 返回 Channel                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 消息队列模式

Agent 的消息处理支持三种队列模式：

| 模式 | 行为 | 适用场景 |
|------|------|---------|
| **steer** | 新消息注入当前运行（在工具调用完成后） | 需要中断当前任务进行调整 |
| **followup** | 新消息排队，等待当前运行结束后处理 | 标准对话模式 |
| **collect** | 多条消息合并，在一个 Agent 轮次中处理 | 批量消息处理 |

## 子智能体（Sub-agent）

当任务复杂、需要隔离执行时，Agent 可以创建**子智能体**：

- **隔离执行**：子 Agent 拥有独立的上下文和工具集
- **任务聚焦**：只接收特定的任务描述，不被主会话干扰
- **自动汇报**：任务完成后自动将结果推回父 Agent
- **轻量提示词**：子 Agent 使用 `minimal` 模式的提示词，不包含心跳、回复标签等无关内容

::: tip 使用建议
对于多步骤复杂任务，优先使用 `sessions_spawn` 创建子 Agent，而不是在单个消息中反复调用工具。
:::

## 技能（Skills）

Skills 是 Agent 可加载的专业知识包。每个 Skill 包含一个 `SKILL.md` 文件，定义了特定领域的操作指南。

### 技能加载顺序（优先级从高到低）

1. 工作空间级：`<workspace>/skills`
2. 项目级：`<workspace>/.agents/skills`
3. 个人级：`~/.agents/skills`
4. 托管级：`~/.openclaw/skills`
5. 内置技能（随安装包发布）
6. 额外目录：`skills.load.extraDirs`

### 技能的工作方式

```xml
<available_skills>
  <skill>
    <name>weather</name>
    <description>获取天气、降水、温度和预报信息</description>
    <location>/path/to/skills/weather/SKILL.md</location>
  </skill>
  <skill>
    <name>healthcheck</name>
    <description>审计和加固运行 OpenClaw 的主机安全</description>
    <location>/path/to/skills/healthcheck/SKILL.md</location>
  </skill>
</available_skills>
```

Agent 在提示词中看到可用技能列表，需要时通过 `read` 工具加载对应的 `SKILL.md` 获取详细操作指南。

## 系统提示词（System Prompt）

OpenClaw 为每次 Agent 运行构建自定义的系统提示词。提示词结构是 OpenClaw 拥有的（不依赖模型默认提示词），包含以下核心模块：

| 模块 | 内容 |
|------|------|
| **Tooling** | 可用工具列表、使用规则、长期运行的工作指引 |
| **Safety** | 安全护栏提醒，防止绕过监管 |
| **Skills** | 可用技能列表（若存在） |
| **Workspace** | 工作目录路径 |
| **Current Date & Time** | 用户时区和时间 |
| **Runtime** | 主机、操作系统、Node 版本、模型、推理级别 |
| **Workspace Files** | 注入的配置文件内容（AGENTS.md 等） |
| **Heartbeats** | 心跳提示词和行为配置 |
| **Sandbox** | 沙箱模式（若启用） |

### 提示词模式

| 模式 | 内容 | 用于 |
|------|------|------|
| `full`（默认） | 包含所有模块 | 常规 Agent 运行 |
| `minimal` | 移除 Skills、心跳、回复标签等 | 子 Agent 运行 |
| `none` | 仅返回基本身份信息 | 特殊场景 |
