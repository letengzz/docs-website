# Java（AI 专题）

::: tip 待补充
AI 方向的 Java 专题规划中，后续按计划补充。
:::

在补齐之前，Java 侧的大模型接入可先看既有内容：

- [LangChain4j](../../Backend/Java/Frame/Langchain4j/index.md)：Java 生态的同类装配框架（模型集成、Chain、记忆管理、平台接入）
- [LangChain](../LangChain/index.md)：同一问题的 Python 侧实现，第 3 节给出两套生态的分工判据

::: info 为什么两套都要看
选哪套**不取决于哪套更先进**。LangChain 专题第 3 节给了一张按「团队主语言、生态新鲜度、部署形态、长流程编排」四维取值的判据表，可以用来判断该落在 Java 还是 Python；混合架构（Java 管业务与权限、模型段抽成独立 Python 服务）也是常见落点，但要接受多一次网络边界与一套部署的代价。
:::
