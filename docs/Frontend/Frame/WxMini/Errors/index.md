# 微信小程序 常见错误

小程序的报错大体分五类：**配置类、编译类、运行时报错、接口与域类、平台与审核类**。本页按类别给出高频错误、成因与处理方式，可作为排障速查表使用；调试方法见 [调试工具链](../Debug/index.md)。

## 一、配置类

| 现象 | 常见原因 | 处理 |
| --- | --- | --- |
| 启动即白屏，控制台提示找不到页面 | `app.json` 中 `pages` 路径写错或缺少该页面目录 | 路径不带 `.wxml` 后缀，且需与目录结构一致 |
| 编译报 `app.json` 语法错误 | 多写逗号、引号不匹配、注释残留 | JSON 不允许注释，用工具格式化检查 |
| tabBar 不显示 | 未配置 `tabBar.list`，或 `pagePath` 不在 `pages` 中 | `list` 至少 2 项，路径必须在 `pages` 中注册 |
| 找不到 `sitemap.json` | 文件缺失或被删除 | 补回文件，或在 `app.json` 中关闭索引配置 |
| 分包报错 | 分包路径与主包冲突、分包大小超限 | 检查分包目录归属与体积 |

::: danger 配置类错误的特点
**报错位置和真实原因常常不在同一处**：例如 `pages` 里少注册一个页面，报错却出现在跳转时。遇到"莫名奇妙的错误"，先完整核对一次 `app.json`。
:::

## 二、编译与语法类

| 报错关键词 | 原因 | 处理 |
| --- | --- | --- |
| `Unexpected token` | JS 语法错误（多余括号、缺少分号、模板字符串未闭合） | 用编辑器定位到具体行 |
| `Cannot find module` | 路径拼错，或使用了未构建的 npm 包 | 检查路径；npm 包需先「构建 npm」（见 [npm 使用](../npm/index.md)） |
| `WXML 编译错误` | 标签未闭合、属性写法错误、<span v-pre>`{{ }}`</span> 表达式不合法 | 检查对应 WXML 文件 |
| `wxss 编译错误` | 使用了不支持的 CSS 选择器或语法 | 改用小程序支持的写法（见 [样式](../Style/index.md)） |

## 三、运行时报错

| 报错 | 原因 | 处理 |
| --- | --- | --- |
| `xxx is not a function` | 调用了不存在的 API（常为基础库版本过低） | 用 `wx.canIUse` 或存在性判断做兼容（见 [基础库版本与兼容](../Version/index.md)） |
| `Cannot read property 'x' of undefined` | 数据未加载完就渲染 / 接口返回结构不符 | 加默认值与可选链，渲染前判空 |
| `setData` 后界面没变化 | 更新的是普通变量而不是 `data`，或遗漏 `setData` | 统一通过 `setData` 更新渲染数据 |
| `this` 指向错误 | 回调中直接使用 `this` | 用箭头函数或在外部保存 `that = this` |
| 定时器仍在下发请求 | 页面销毁未清理定时器 | 在 `onUnload` 中 `clearInterval` |

```js [两个高频修复示例]
Page({
  data: { list: [] },

  onLoad() {
    // 1) 接口返回前的默认值，避免 undefined 渲染
    this.setData({ list: this.data.list || [] })

    // 2) 回调中 this 的正确用法
    wx.request({
      url: 'https://api.example.com/list',
      success: (res) => {                      // 箭头函数继承外层 this
        this.setData({ list: res.data.list || [] })
      },
    })
  },

  onUnload() {
    if (this.timer) clearInterval(this.timer)  // 页面销毁时清理
  },
})
```

## 四、网络与域名类

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `request:fail url not in domain list` | 服务器域名未在后台配置 | 后台配置合法域名（HTTPS），或开发时勾选「不校验合法域名」 |
| 真机请求失败、模拟器正常 | 真机未配置域名或证书不被信任 | 配置正式域名与有效证书 |
| 401 / 403 | 登录态过期或权限不足 | 重新登录刷新 token；检查接口权限 |
| 请求超时 | 服务端慢或网络差 | 设置 timeout，加失败重试与降级提示 |
| 上传大文件失败 | 体积超限或超时 | 压缩后再传，或分片上传 |

::: warning 开发时不要长期依赖「不校验合法域名」
该选项仅是开发便利。上线前必须在**未勾选**的状态下完整验证一次，否则很容易出现"开发全好、上线全挂"。
:::

## 五、平台与审核类

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 审核驳回：类目不符 | 实际功能与所选类目不一致 | 按实际业务选择类目，必要时补资质 |
| 审核驳回：功能不完整 | 存在空白页、无法使用的入口 | 提交前完整走查（含异常路径） |
| 审核驳回：诱导分享/关注 | 使用了平台不允许的诱导文案 | 修改文案与交互 |
| 体验版正常、线上异常 | 线上未配置域名/未开通能力 | 对照线上配置逐项核对 |
| 发布后部分用户白屏 | 基础库版本过低 | 设置最低基础库版本或补兼容分支（见 [基础库版本与兼容](../Version/index.md)） |

## 六、进阶能力相关

启用新渲染引擎、多线程与自动化后，会出现一批特有的报错：

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 页面开启 Skyline 后无法滚动 | Skyline 下页面默认不滚动 | 改用 `scroll-view` 并设 `height: 100vh`（见 [Skyline](../Skyline/index.md)） |
| 开启 Skyline 后布局错位 | `defaultDisplayBlock` / `defaultContentBox` 改变了默认盒模型 | 逐页对比样式，按需调整 |
| 开启 Skyline 后某个组件不渲染 | 该组件尚未被 Skyline 支持 | 该页保持 WebView，或替换组件 |
| `wx.createWorker is not a function` | 基础库过低，或 `app.json` 未配 `workers` | 核对版本与配置（见 [Worker](../Worker/index.md)） |
| Worker 内报 `wx is not defined` | 在 Worker 中使用了界面类 API | 把界面操作移回主线程 |
| Worker 返回空对象 | `postMessage` 传了不可结构化克隆的数据 | 只传普通 JSON 可表达的数据 |
| CI 上传报「密钥/白名单」错误 | 密钥未注入或 IP 不在白名单 | 在后台加入流水线出口 IP（见 [自动化与 CI](../Automation/index.md)） |
| 自动化脚本连接开发者工具失败 | 未开启开发者工具「服务端口」 | 设置 → 安全设置中开启 |

```js [Worker 数据传递的正确姿势]
// 错误：传整个页面 data（体积大，且可能含不可克隆内容）
// worker.postMessage({ rows: this.data.rows, cb: () => {} })

// 正确：只传计算需要的字段
worker.postMessage({ type: 'sum', values: this.data.rows.map((r) => r.amount) })
```

::: danger 注意
**不要用「开启 Skyline / 关闭校验」这类开关来掩盖报错**。例如把 `renderer` 开开关关来「解决」滚动问题，只会让问题在不同页面反复出现。找到根因（组件是否支持、滚动结构是否正确）再改。
:::

## 排障顺序（建议固定下来）

1. **看配置**：`app.json` / 页面路径 / 域名配置。
2. **看报错**：开发者工具 Console 的第一条红色错误。
3. **看数据**：AppData 面板确认 `data` 是否符合预期。
4. **看网络**：Network 面板确认请求是否发出、状态码与返回体。
5. **上真机**：模拟器正常但真机异常时，优先怀疑权限、版本与性能。

::: tip 把错误变成资产
每解决一个问题，就把「现象 → 根因 → 解决方式」补到本页表格里。三个月后，这份清单会比任何教程都更贴合你们的项目。
:::

## 验证方式

1. 故意写错一个页面路径，确认能从报错信息定位到 `app.json` 的哪一行。
2. 在 `onLoad` 中调用一个不存在的 API，观察报错文案，并用 `wx.canIUse` 修复。
3. 取消勾选「不校验合法域名」，确认请求失败并出现明确的域名提示。
4. 把本页表格中的 3 条错误在项目中复现并记录解决过程，形成团队速查表。

## 相关专题

- [调试工具链](../Debug/index.md)：Console / Network / AppData 面板用法
- [基础库版本与兼容](../Version/index.md)：版本导致的 API 不存在问题
- [Skyline 渲染引擎](../Skyline/index.md)：新渲染引擎的兼容问题
- [Worker 多线程](../Worker/index.md)：多线程使用中的报错
- [自动化与 CI](../Automation/index.md)：流水线上传失败的原因
- [原生 API](../API/index.md)：网络请求与域名配置
- [上线发布](../Release/index.md)：审核驳回与发布流程

## 参考资料

- 微信小程序官方文档 · 错误码：https://developers.weixin.qq.com/miniprogram/dev/framework/usability/errorcode.html
- 微信小程序官方文档 · 调试：https://developers.weixin.qq.com/miniprogram/dev/devtools/debug.html
