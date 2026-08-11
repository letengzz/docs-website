# React 合成事件与事件处理

React 的事件系统把浏览器原生事件包装成**合成事件（SyntheticEvent）**，统一跨浏览器行为，并在根节点统一委托处理。本节讲清原理、常用模式和与原生事件混用的注意事项。

::: info 适用版本
本节基于 React 19.2.x。React 17+ 的事件委托挂载点从 `document` 改到了应用根容器（root container）。
:::

## 合成事件是什么

合成事件是 React 对原生事件的一层封装，拥有与原生事件一致的接口（`preventDefault`、`stopPropagation`、`target` 等），但解决了浏览器差异并优化了性能：

```tsx
import type { ChangeEvent } from "react"

function handleChange(e: ChangeEvent<HTMLInputElement>) {
  console.log(e.target.value) // 原生目标
  e.preventDefault()
}

<input onChange={handleChange} />
```

事件对象在 React 17+ 中**不再复用**，可以安全地异步读取（旧版的事件池 pooling 已移除）。

## 事件委托原理

React 不会把监听器挂到每个元素上，而是在根容器统一监听：

```text
React 17 之前：document 上委托
React 17+：应用根容器（如 #root）上委托
  → 事件冒泡到根容器
  → React 根据 fiber 树找到对应组件
  → 按组件树的顺序执行合成事件处理器
```

好处：

- 动态插入的组件不需要重新绑定事件。
- 减少内存占用（不用每个元素一个监听器）。
- 统一的冒泡/捕获语义。

## 常用事件写法

```tsx
// 事件类型通过泛型标注，参数自动推导
const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {}

// 传参数 + 事件对象
<button onClick={(e) => handleDelete(e, item.id)}>删除</button>

// 阻止默认行为
<form onSubmit={(e) => e.preventDefault()}>...</form>

// 键盘事件
<input onKeyDown={(e) => {
  if (e.key === "Enter") submit()
}} />
```

## onChange 与受控输入

React 的 `onChange` 语义与原生 `change` 不同：它等价于「每次输入变化都触发」（原生 `input` 事件），因此受控输入框是标准写法：

```tsx
function SearchBox() {
  const [value, setValue] = useState("")
  return (
    <input
      value={value}
      onChange={(e) => setValue(e.target.value)}
    />
  )
}
```

如果只写了 `value` 没写 `onChange`，React 会报警告且输入框不可编辑。

## 合成事件与原生事件混用

原生监听器（如 `addEventListener`）不受 React 合成事件系统管理：

```tsx
useEffect(() => {
  const el = document.getElementById("box")
  const handler = () => console.log("原生事件")
  el?.addEventListener("click", handler)
  return () => el?.removeEventListener("click", handler)
}, [])
```

注意事项：

1. 原生监听器需要手动清理，否则卸载后泄漏。
2. 合成事件里的 `stopPropagation()` 只能阻止 React 合成事件的传播，不能阻止原生监听器；反过来原生 `stopPropagation()` 会阻止事件到达根容器，React 处理器也可能收不到。
3. 不要在原生监听器里调用 `e.stopPropagation()` 后还指望 React onClick 触发。

## 被动事件与性能

某些浏览器事件（`touchstart`、`wheel`）默认是 passive 的，无法在监听器中 `preventDefault()`。React 对滚动类事件也做了优化；需要阻止滚动默认行为时，考虑：

- 用 `onWheel` 无法可靠阻止，改用原生非 passive 监听器（React 不直接支持 passive 配置）。
- 或通过 CSS（如 `overscroll-behavior`）解决。

## 事件处理最佳实践

1. 事件处理器保持轻量，不要在回调里做重计算。
2. 高频事件（滚动、拖拽、输入联想）用防抖/节流，或 `useDeferredValue` 降低渲染压力。
3. 需要访问最新 state 时用函数式更新或 `useRef` 镜像，避免闭包过期。
4. 列表项事件用 `data-*` 或参数传递 id，避免为每项创建过多内联函数（可接受时内联函数也 OK，React 19 + Compiler 下开销很小）。

## 易错点

::: danger 常见错误
1. 在原生 `addEventListener` 回调里使用组件 state，闭包拿到旧值；应把依赖写进 effect 或用 ref。
2. 在合成事件里 `stopPropagation()` 后以为原生事件也停了，混用场景行为不一致。
3. 忘记给受控 input 写 `onChange`，控制台报「value without onChange」且无法输入。
4. 在事件回调里直接读取 `setState` 后的值，拿到旧状态。
5. 在 `useEffect` 里注册原生监听但不清理，组件卸载后事件泄漏。
6. 用 `onChange` 做防抖输入时把 `e.target` 存进异步闭包，React 17+ 虽不会复用事件对象，但跨线程/跨事件仍建议先取出 `value`。
:::

## 验证方式

1. 打开浏览器 DevTools Event Listeners 面板，确认监听器挂在 `#root` 而不是每个按钮上。
2. 输入框输入文字，`onChange` 每次都触发且 `value` 同步。
3. 同时挂原生监听和 React onClick，测试 `stopPropagation` 的实际传播范围。
4. 卸载组件后用 `getEventListeners` 或控制台确认原生监听已移除。
5. 快速输入搜索框，UI 不卡顿（防抖/`useDeferredValue` 生效）。

## 参考资料

- React 事件处理：https://zh-hans.react.dev/learn/responding-to-events
- 合成事件参考：https://zh-hans.react.dev/reference/react-dom/components/common
- React 17 事件委托变更：https://legacy.reactjs.org/blog/2020/10/20/react-v17.html
