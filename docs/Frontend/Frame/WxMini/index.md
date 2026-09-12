# 微信小程序

<p style="text-align:center;"><img src="./assets/wxmini-logo.png" alt="微信小程序" style="zoom:75%;" /></p>

微信小程序（WeChat Mini Program）是运行在微信客户端内的**轻量级应用形态**：无需下载安装，扫码或搜索即可打开，具备独立的页面栈、渲染层与网络层，并通过平台开放能力（登录、支付、分享、订阅消息等）与微信生态打通。本专题覆盖从项目结构、模板语法、组件、API、路由、性能到发布审核的完整链路。

## 目录

### 入门与基础

- [微信小程序 概述](Overview/index.md)
- [微信小程序 基础](Basic/index.md)
- [微信小程序 配置文件](Settings/index.md)
- [微信小程序 调试工具链](Debug/index.md)
- [微信小程序 基础库版本与兼容](Version/index.md)

### 视图与交互

- [微信小程序 模板语法](Template/index.md)
- [微信小程序 组件](Component/index.md)
- [微信小程序 样式](Style/index.md)
- [微信小程序 事件](Event/index.md)
- [微信小程序 生命周期](Lifecycle/index.md)

### 能力与数据

- [微信小程序 原生 API](API/index.md)
- [微信小程序 路由与页面栈](Router/index.md)
- [微信小程序 页面间通信](PageCommunication/index.md)
- [微信小程序 全局数据共享（getApp）](getApp/index.md)
- [微信小程序 开放能力](OpenAbility/index.md)

### 进阶与工程化

- [微信小程序 自定义组件](CustomComponent/index.md)
- [微信小程序 npm 使用](npm/index.md)
- [微信小程序 分包加载](Subpackage/index.md)
- [微信小程序 性能优化](Performance/index.md)
- [微信小程序 云开发](Cloud/index.md)

### 发布与排障

- [微信小程序 上线发布](Release/index.md)
- [微信小程序 常见错误](Errors/index.md)

::: info 版本约定
本专题以**当前稳定基础库**为主线：涉及新 API、新组件与新配置项的写法默认按其最低基础库版本要求使用；旧版本兼容写法与已废弃能力的说明**保留并标注「仅存量项目使用」**，不删除、不覆盖。具体版本门槛以官方文档对应页面为准，版本策略与兼容判断见 [基础库版本与兼容](Version/index.md)。
:::

::: tip 学习路径建议
先按「概述 → 基础 → 配置文件 → 模板语法 → 组件 → 事件 → 生命周期 → API」跑通一个最小项目，再补「路由 → 页面通信 → 全局数据」，最后做「分包 → 性能 → 发布审核」。每一步都用真机验证一次，比在模拟器里反复调试更省时间。
:::

**拓展**：

- [IDE 工具](../../../Tools/IDE/index.md)
- [前端性能优化专题](../../Others/PerformanceOptimization/index.md)
