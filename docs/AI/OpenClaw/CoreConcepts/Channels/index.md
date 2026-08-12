# 渠道（Channels）

渠道是 OpenClaw 接入各种消息平台的入口。用户通过渠道发消息，OpenClaw 通过渠道回消息，渠道与核心智能体之间由 Gateway 统一调度。

::: info 适用版本
本文基于 OpenClaw 当前文档体系，渠道配置以官方文档为准。
:::

## 渠道是什么

渠道（Channel）解决「用户在哪个平台和我对话」的问题：

- WhatsApp
- Telegram
- Discord
- 微信 / 微信公众号
- 飞书
- 网页聊天 / 命令行终端

每个渠道负责：

1. 接收用户消息并标准化为内部消息格式。
2. 把 Agent 的回复发送回对应平台。
3. 维护渠道内的会话上下文。

## 渠道与 Gateway 的关系

```text
WhatsApp ─┐
Telegram ─┤
Discord ──┼──▶ Gateway ──▶ Agent ──▶ LLM / 工具
飞书 ─────┘
```

渠道不直接调用模型，而是把消息交给 Gateway 统一路由；因此新增一个渠道不需要改动 Agent 逻辑。

## 渠道配置步骤

接入一个新渠道通常按以下步骤：

1. 在平台侧创建机器人/应用，获取 Token 或密钥。
2. 在 OpenClaw 配置中启用对应渠道并填入凭据。
3. 配置 Webhook/回调地址（公网可访问）。
4. 配置允许访问的会话白名单。
5. 重启或热加载配置，发送测试消息验证。

## 常见渠道对比

| 渠道 | 特点 | 典型用途 |
| --- | --- | --- |
| Telegram | API 开放、机器人生态成熟 | 个人助理、通知 |
| WhatsApp | 用户基数大 | 客服、业务沟通 |
| Discord | 社区属性强、支持多频道 | 社区机器人 |
| 微信/飞书 | 国内办公场景 | 企业内部助理 |
| 网页/终端 | 调试方便 | 开发测试 |

## 会话与会话 ID

每个渠道的每个会话（用户、群组）会对应一个会话 ID：

- 会话 ID 用于记忆检索和上下文管理。
- 同一用户跨渠道（如同时在 Telegram 和飞书）默认是不同会话。
- 需要跨渠道统一身份时，通过用户映射或统一账号体系实现。

示例（概念示意，具体字段以官方配置为准）：

```yaml
channels:
  telegram:
    enabled: true
    token: ${TELEGRAM_BOT_TOKEN}
    allowed_chats:
      - "123456789"
  discord:
    enabled: false
    token: ${DISCORD_BOT_TOKEN}
```

## 配置要点

不同渠道的配置项不同，但通常包含：

- 机器人 Token / App Secret。
- 回调地址或 Webhook。
- 渠道启用开关。
- 允许访问的会话/群组白名单。

示例（Telegram 风格，具体字段以官方配置为准）：

```yaml
channels:
  telegram:
    enabled: true
    token: ${TELEGRAM_BOT_TOKEN}
```

## 易错点

::: danger 常见错误
1. 只配置了渠道没有配置 Gateway 路由，消息进不来。
2. Token 写死在配置里并提交到 Git。
3. Webhook 地址填了内网地址，平台无法回调。
4. 生产渠道没有白名单，任何陌生人都能触发 Agent 执行工具。
5. 多个渠道共用一个会话 ID，上下文互相串扰。
6. Webhook 没有签名校验，攻击者伪造消息调用 Agent。
:::

## 验证方式

1. 在对应平台给机器人发一条消息，确认能收到回复。
2. 查看 Gateway 日志，确认消息从渠道进入并路由到 Agent。
3. 关闭渠道开关后，消息不再进入 Agent。
4. 用白名单外的账号发消息，确认被拒绝。
5. 重启后发送消息，确认会话上下文能通过记忆恢复。
6. 检查 Webhook 签名校验，用伪造请求测试是否被拒绝。

## 参考资料

- OpenClaw 官方文档：https://docs.openclaw.ai/
- Telegram Bot API：https://core.telegram.org/bots/api
