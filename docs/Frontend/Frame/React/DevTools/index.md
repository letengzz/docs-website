# React DevTools

React DevTools 是 React 官方提供的浏览器扩展，用于调试 React 应用。它提供了组件树查看、性能分析、Hooks 检查等功能。

## 安装

### Chrome 扩展

在 Chrome 网上应用店搜索 "React Developer Tools" 并安装。

### Firefox 扩展

在 Firefox 附加组件市场搜索 "React Developer Tools" 并安装。

### 独立版本

```bash [终端]
npm install -g react-devtools
```

## 组件树

### 查看组件结构

打开浏览器开发者工具，切换到 "Components" 标签页：

- 左侧显示组件树结构
- 右侧显示选中组件的 props 和 state
- 可以搜索组件名称快速定位

### 组件过滤

```tsx
// 在组件中设置显示名称
function MyComponent() {
  return <div>内容</div>
}
MyComponent.displayName = 'CustomDisplayName'

// 或使用 displayName 静态属性
const MyComponent = () => <div>内容</div>
MyComponent.displayName = 'CustomDisplayName'
```

### 组件高亮

在 DevTools 设置中启用 "Highlight updates when components render"，可以在页面上高亮显示正在重新渲染的组件。

## Props 和 State 检查

### 查看 Props

选中组件后，右侧面板显示：

- **Props**：组件接收的属性
- **State**：组件内部状态
- **Hooks**：使用的 Hooks 及其值
- **Context**：订阅的 Context 值

### 编辑 Props 和 State

在 DevTools 中可以直接编辑 props 和 state 来测试不同状态下的组件表现：

1. 选中组件
2. 在右侧面板找到要编辑的值
3. 双击值进行修改
4. 按 Enter 确认

::: tip 提示
在 DevTools 中修改 state 仅用于调试，不会保存到代码中。刷新页面后恢复原始状态。
:::

## Hooks 调试

### 查看 Hooks 值

```tsx [components/UserProfile.tsx]
import { useState, useEffect, useRef } from 'react'

function UserProfile() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const inputRef = useRef(null)

  useEffect(() => {
    fetchUser().then(data => {
      setUser(data)
      setLoading(false)
    })
  }, [])

  return <div>{user?.name}</div>
}

export default UserProfile
```

在 DevTools 的 Hooks 面板中可以看到：

- Hook 0: `useState` - user: null, setUser: ƒ
- Hook 1: `useState` - loading: true, setLoading: ƒ
- Hook 2: `useRef` - current: null
- Hook 3: `useEffect` - 依赖: []

### 自定义 Hook 显示

```tsx [hooks/useCounter.ts]
import { useState, useCallback } from 'react'

function useCounter(initialValue = 0) {
  const [count, setCount] = useState(initialValue)

  const increment = useCallback(() => setCount(c => c + 1), [])
  const decrement = useCallback(() => setCount(c => c - 1), [])
  const reset = useCallback(() => setCount(initialValue), [initialValue])

  return { count, increment, decrement, reset }
}

export default useCounter
```

DevTools 会显示自定义 Hook 及其内部状态。

## Profiler 性能分析

### 录制性能

1. 切换到 "Profiler" 标签
2. 点击录制按钮（蓝色圆点）
3. 与应用交互
4. 点击停止按钮

### 分析结果

- **火焰图**：显示每个组件的渲染时间
- **排名图**：按渲染时间排序的组件列表
- **为什么渲染**：显示组件重新渲染的原因

### 识别性能问题

```tsx [components/ExpensiveList.tsx]
import { memo } from 'react'

const ExpensiveList = memo(function ExpensiveList({ items }: { items: Item[] }) {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  )
})

export default ExpensiveList
```

在 Profiler 中，如果看到 ExpensiveList 频繁渲染但 props 未变化，说明需要添加 memo 优化。

## 组件树搜索

在 DevTools 顶部搜索框中输入组件名称，可以快速定位到该组件。

支持：
- 组件名称搜索
- 正则表达式搜索
- 过滤显示/隐藏组件

## 设置选项

### 组件过滤

在设置中可以配置：

- **Hide components where...**：隐藏匹配正则的组件
- **Show component stacks in warnings**：在警告中显示组件堆栈

### 主题

支持浅色和深色主题，跟随系统或手动设置。

## 独立 DevTools

### 启动独立版本

```bash [终端]
react-devtools
```

### 连接应用

```typescript [src/main.tsx]
import { createRoot } from 'react-dom/client'
import App from './App'

// 连接独立 DevTools
if (process.env.NODE_ENV === 'development') {
  require('react-devtools')
}

createRoot(document.getElementById('root')!).render(<App />)
```

## React Native DevTools

### 安装

```bash [终端]
npx react-devtools
```

### 使用

在 React Native 应用中启用 DevTools：

```javascript [App.js]
if (__DEV__) {
  require('react-devtools')
}
```

## 调试技巧

### 1. 使用 $r 访问选中组件

在控制台中，`$r` 指向当前在 Components 面板中选中的组件实例：

```javascript
// 在控制台中
$r // 当前选中的组件实例
$r.props // 组件的 props
$r.state // 组件的 state
```

### 2. 使用 $x 执行 XPath 查询

```javascript
// 在控制台中
$x('//div[@class="user-card"]') // 查找所有 user-card 元素
```

### 3. 组件渲染计数

在组件中添加渲染计数：

```tsx [components/DebugCounter.tsx]
import { useEffect, useRef } from 'react'

function DebugCounter({ name }: { name: string }) {
  const renderCount = useRef(0)

  useEffect(() => {
    renderCount.current += 1
    console.log(`${name} 渲染次数: ${renderCount.current}`)
  })

  return null
}

export default DebugCounter
```

### 4. 使用 React 调试构建

```bash [终端]
# 使用 React 调试构建（包含额外警告和提示）
npm install react@canary react-dom@canary
```

## DevTools API

### 编程式访问

```typescript [src/devtools.ts]
if (process.env.NODE_ENV === 'development') {
  window.__REACT_DEVTOOLS_GLOBAL_HOOK__ = {
    renderers: new Map(),
    supportsFiber: true,
    inject: (renderer) => {},
    onCommitFiberRoot: (rendererID, root) => {},
    onCommitFiberUnmount: (rendererID, fiber) => {}
  }
}
```

## 常见问题

### DevTools 不显示

- 确保使用的是开发构建
- 确保 React 版本与 DevTools 兼容
- 尝试刷新页面或重启浏览器

### 组件名称显示为 "Anonymous"

为组件添加 displayName：

```tsx
function MyComponent() {
  return <div>内容</div>
}
MyComponent.displayName = 'MyComponent'
```

### Hooks 不显示

- 确保使用的是 React 16.8+
- 确保 Hooks 在组件顶层调用
- 检查是否有多个 React 版本
