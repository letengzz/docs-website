# React 渲染与协调原理

理解 React 的「渲染（Render）→ 协调（Reconcile）→ 提交（Commit）」流程，才能真正读懂 `setState` 为什么是异步的、`key` 为什么重要、并发特性为什么能中断渲染。

::: info 适用版本
本节基于 React 19.2.x。React 18+ 默认启用并发渲染，React 19 继续基于 Fiber 架构。
:::

## 一次更新的完整流程

```text
触发更新（setState / useState 更新函数 / 外部 store）
  → Render 阶段：调用组件函数，计算新的 React 元素树（可中断）
  → 协调：对比新旧元素树，找出差异（Fiber 节点打上标记）
  → Commit 阶段：把差异应用到真实 DOM（不可中断）
  → 浏览器绘制
```

| 阶段 | 是否可以中断 | 是否操作 DOM | 副作用时机 |
| --- | --- | --- | --- |
| Render | 可以（并发） | 否 | 组件函数体执行 |
| Commit | 不可以 | 是 | `useEffect`、`useLayoutEffect` |

## 为什么叫 Fiber

Fiber 是 React 内部用来描述组件和 DOM 节点的数据结构，可以看作「可打断的调用栈」。每个组件对应一个 Fiber 节点，节点之间通过链表连接，React 可以在渲染过程中暂停、恢复、丢弃低优先级工作。

Fiber 节点主要保存：

- `type`：组件类型（函数组件、类组件、原生标签）。
- `key`：列表复用标识。
- `stateNode`：真实 DOM 或组件实例。
- `child` / `sibling` / `return`：树结构的链表指针。
- `lanes`：更新优先级。
- `alternate`：当前树与工作树互相指向，用于双缓冲。

## 协调（Reconciliation）

协调是 React 对比新旧元素、决定如何更新 DOM 的算法。核心规则：

1. **同类型元素复用**：`<div>` 换成 `<div>` 只更新属性；类型不同则整棵子树重建。
2. **key 决定列表复用**：同 key 的元素尽量复用并移动，而不是销毁重建。
3. **递归子节点**：从根向下逐层对比。

```tsx
// 列表对比：key 相同则复用 DOM
<ul>
  {items.map((item) => (
    <li key={item.id}>{item.name}</li>
  ))}
</ul>
```

如果不用 key 或用 index，插入/删除时 React 可能复用错误的 DOM，导致状态错乱（输入框内容串位是最常见的表现）。

## Render 阶段的 bailout

当父组件重渲染时，React 会检查子组件是否真的需要更新：

- props 引用相同且组件没有自己的 state 变化 → 跳过子组件（bailout）。
- 这也是 `React.memo` 和 `useMemo` 能生效的原因：它们让 React 在 props 没变时跳过函数组件执行。

```tsx
const MemoizedChild = memo(Child)
```

注意：`memo` 只做浅比较；props 传对象/函数时每次新建引用，memo 就会失效，需要配合 `useCallback`/`useMemo`。

## setState 为什么是异步的

在 React 事件处理函数中，多次 `setState` 会被合并（batching）：

```tsx
function handleClick() {
  setCount((c) => c + 1)
  setCount((c) => c + 1)
  setCount((c) => c + 1)
  // 最终 count 只 +3，组件只渲染一次
}
```

React 18+ 在 Promise、setTimeout、原生事件回调里也会自动批处理。如果想拿到最新值，用函数式更新或 `useEffect` 观察，而不是依赖 `setState` 后的同步读取。

## 并发特性原理

`useTransition` 和 `useDeferredValue` 让 React 可以「先响应紧急更新，再慢慢处理非紧急更新」：

```tsx
import { useDeferredValue, useState } from "react"

function Search() {
  const [keyword, setKeyword] = useState("")
  const deferredKeyword = useDeferredValue(keyword)

  // 输入框立即响应，列表用 deferred 值渲染，可以被打断
  return <List keyword={deferredKeyword} />
}
```

原理：React 把低优先级更新渲染到「工作树」，高优先级更新到来时丢弃低优先级的部分工作并重新开始。渲染结果直到 Commit 阶段才落到真实 DOM，因此用户不会看到中间状态。

## StrictMode 为什么执行两次

开发模式下 `StrictMode` 会故意让组件函数、state 初始化和 effect 多执行一轮，目的是暴露「非纯函数」和「未清理的副作用」：

- 组件函数必须是纯函数（同样的 props/state 返回同样的输出）。
- `useEffect` 必须能被重复 setup/cleanup。

这是特性不是 bug，生产构建不会双执行。

## React Compiler 简介

React Compiler 是 React 19 可选接入的编译期优化，自动对组件和 Hook 做记忆化，减少手写 `useMemo`/`useCallback`/`memo`。接入后：

- 代码更简洁，不需要到处思考引用稳定性。
- 必须满足 Rules of React（组件纯函数、Hooks 规则），否则编译器会告警或产生错误。

## 易错点

::: danger 常见错误
1. 在 `setState` 后立刻读取 state，拿到旧值；应使用函数式更新或在 effect 中读取。
2. 列表用 index 当 key，插入/删除后组件状态错乱。
3. 以为 `React.memo` 能解决一切，实际 props 每次传新对象/函数时 memo 无效。
4. 在 Render 阶段做副作用（修改全局变量、请求接口），并发渲染下可能执行多次或结果不一致。
5. 在 `useLayoutEffect` 里做耗时操作，阻塞浏览器绘制。
6. 把 StrictMode 的双执行当 bug，用「关掉 StrictMode」掩盖不纯函数问题。
:::

## 验证方式

1. 用 React DevTools Profiler 录制一次点击，观察 Render/Commit 时间线和组件执行次数。
2. 在列表中间插入一条数据，对比使用稳定 key 与 index key 时输入框内容是否串位。
3. 连续三次 `setCount((c) => c + 1)`，确认最终值 +3 且组件只渲染一次。
4. 输入框用 `useDeferredValue`，快速输入时 UI 不卡顿，列表落后于输入内容。
5. 开启 StrictMode，观察开发控制台对「清理副作用」的提示。

## 参考资料

- React 渲染机制：https://zh-hans.react.dev/learn/render-and-commit
- 协调：https://zh-hans.react.dev/learn/preserving-and-resetting-state
- React 并发特性：https://zh-hans.react.dev/reference/react/useDeferredValue
- React Compiler：https://react.dev/learn/react-compiler
