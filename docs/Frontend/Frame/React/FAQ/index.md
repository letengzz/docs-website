# React 常见问题与最佳实践

汇总 React 开发中最高频的坑与解法，并给出一份可以直接对照的生产自查清单。

::: info 适用版本
本文基于 React 19.2.x；涉及旧版本差异时会在条目中说明。
:::

## 生产自查清单

发布前逐项核对：

- [ ] 组件是纯函数，没有在渲染期间修改外部状态
- [ ] 列表渲染使用稳定且唯一的 `key`
- [ ] `useEffect` 的副作用都有清理逻辑
- [ ] 受控输入都有 `value` + `onChange`
- [ ] 请求有错误处理与重试，loading 状态齐全
- [ ] 大列表、高频更新做了性能优化（memo、虚拟列表、并发特性）
- [ ] 用户输入渲染前做了转义（React 默认转义文本，`dangerouslySetInnerHTML` 已审查）
- [ ] 敏感信息没有写进客户端代码
- [ ] `npm run build` 与类型检查通过

## 常见问题

### 1. 调用 setState 后立刻读取，值还是旧的

`setState` 是异步的，事件处理中多次调用还会批处理。不要依赖调用后的同步读取：

```tsx
// 错误
setCount(count + 1)
console.log(count) // 旧值

// 正确
setCount((c) => c + 1)
```

需要基于最新值做后续逻辑时，使用函数式更新或在 `useEffect` 中观察。

### 2. 组件不更新，界面停留在旧数据

常见原因：

1. 直接修改了对象/数组（`state.items.push(x)`），React 没有检测到引用变化。
2. 父组件每次渲染都传入新建的对象/内联值，子组件 memo 的浅比较失效。
3. 更新逻辑写在 Render 阶段之外但依赖了过期闭包。

```tsx
// 错误：原地修改
setState((prev) => {
  prev.items.push(item)
  return prev
})

// 正确：返回新引用
setState((prev) => ({ ...prev, items: [...prev.items, item] }))
```

### 3. Hooks 报错：Rules of Hooks

```text
Rendered more hooks than during the previous render
```

Hooks 必须在组件顶层、顺序固定地调用，不能放在 `if`、`for`、普通函数里：

```tsx
// 错误
if (visible) {
  useEffect(() => {})
}

// 正确：条件逻辑放进 Hook 内部
useEffect(() => {
  if (visible) doSomething()
}, [visible])
```

### 4. key 用 index 导致列表状态错乱

插入、删除、排序时，index 会变化，React 复用错误的 DOM，输入框内容串位、勾选状态错乱。使用稳定 id：

```tsx
{items.map((item) => (
  <Item key={item.id} item={item} />
))}
```

### 5. 输入框报 warning：value without onChange

受控组件必须同时提供 `value` 和 `onChange`；只读展示用 `readOnly` 明确意图：

```tsx
<input value={value} readOnly />
```

### 6. StrictMode 下 effect 执行两次

这是开发模式的故意行为，用于暴露副作用未清理的问题，不是 bug。正确做法是让 effect 可重复 setup/cleanup：

```tsx
useEffect(() => {
  const timer = setInterval(tick, 1000)
  return () => clearInterval(timer)
}, [])
```

生产构建不会双执行。

### 7. React.memo 没生效

`memo` 只做浅比较，每次渲染都新建的 props（对象、数组、函数）会让 memo 失效：

```tsx
// 错误
<Child data={{ name }} />

// 正确
const data = useMemo(() => ({ name }), [name])
const handleClick = useCallback(() => {}, [])
<Child data={data} onClick={handleClick} />
```

接入 React Compiler 后，这部分记忆化大多可以交给编译器。

### 8. useEffect 里请求接口造成重复请求

检查依赖数组：

- 依赖了每次渲染都变化的函数/对象 → 用 `useCallback`/`useMemo` 稳定引用。
- 严格模式开发环境双执行 → 用 AbortController 清理或改用数据获取库。
- 真正需要缓存和去重 → 用 TanStack Query / SWR。

### 9. 从 React 18 升到 19 后组件行为变化

主要检查点：

- 移除 `defaultProps` 对函数组件的支持（改用参数默认值）。
- `forwardRef` 不再必需，ref 可以直接作为 prop。
- `useEffect` 清理时机更严格，未清理的副作用更容易暴露。
- `react-dom/test-utils` 的 `act` 已迁移到 `react` 包。

升级前先跑一遍类型检查和测试，再逐步验证页面行为。

## 最佳实践

1. **状态最小化**：能从 props 或已有 state 推导的值不要重复存储（`derived state`）。
2. **数据获取交给专门库**：TanStack Query / SWR 负责缓存、重试、失效，组件只关注 UI。
3. **组件边界清晰**：容器组件管数据，展示组件管 UI。
4. **错误边界兜底**：生产环境用错误边界 + 全局错误上报，避免白屏。
5. **性能先测量再优化**：用 React DevTools Profiler 找热点，不要盲目 memo。
6. **安全默认**：文本自动转义，`dangerouslySetInnerHTML` 内容必须可信。

## 验证方式

1. 对照自查清单逐项确认。
2. 用 `npm run build` + 类型检查确认无警告。
3. 打开 React DevTools Profiler，录制主要交互，确认没有意外的全树重渲染。
4. 在 StrictMode 下跑一遍开发环境，修复所有「副作用未清理」提示。
5. 用 Lighthouse 跑一次性能与最佳实践检查。

## 参考资料

- React 官方 FAQ：https://zh-hans.react.dev/learn
- 状态管理哲学：https://zh-hans.react.dev/learn/managing-state
- 保持组件纯粹：https://zh-hans.react.dev/learn/keeping-components-pure
- React 19 升级指南：https://react.dev/blog/2024/04/25/react-19
