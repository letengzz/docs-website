# React Context 深入

Context 是 React 内置的「跨层级传值」机制，解决 props 层层透传问题。本节讲透 `createContext`、`useContext`、Provider 重渲染陷阱和与 `useReducer` 的组合用法。

::: info 适用版本
本节基于 React 19.2.x。React 19 中 `<Context>` 本身可以直接作为 Provider 使用，写法更简洁。
:::

## Context 是什么

Context 让组件树中的任意后代组件直接读取「就近 Provider」提供的值，不需要每一层都通过 props 传递：

```ts [src/theme.ts]
import { createContext } from "react"

export type Theme = "light" | "dark"

export const ThemeContext = createContext<Theme>("light")
```

```tsx [src/App.tsx]
import { ThemeContext } from "./theme"

export default function App() {
  return (
    <ThemeContext value="dark">
      <Toolbar />
    </ThemeContext>
  )
}
```

React 19 中 `<ThemeContext value="dark">` 等价于旧写法 `<ThemeContext.Provider value="dark">`。

## 读取 Context

```tsx [src/Toolbar.tsx]
import { useContext } from "react"
import { ThemeContext } from "./theme"

export default function Toolbar() {
  const theme = useContext(ThemeContext)
  return <div className={theme === "dark" ? "dark" : "light"}>工具栏</div>
}
```

## 什么时候该用 Context

适合：

- 主题、语言、登录用户等「全局但变化不频繁」的数据。
- 跨多层的配置（如组件库的主题 token）。
- 与 `useReducer` 组合实现局部状态共享。

不适合：

- 高频变化的数据（如输入框的每个字符、实时坐标）。
- 只想给一两个子组件传值（直接用 props 更清晰）。
- 全局复杂状态（优先考虑 Zustand、Redux 等专门方案）。

## Provider 重渲染陷阱

Provider 的值只要变化，所有消费该 Context 的组件都会重渲染，无论子组件是否真的用到变化的部分。

```tsx
// 错误：每次渲染都创建新对象，导致所有消费者重渲染
<UserContext value={{ name, age }}>
  <App />
</UserContext>
```

```tsx
// 正确：用 useMemo 稳定引用，只有数据真正变化才重渲染
import { useMemo } from "react"

const value = useMemo(() => ({ name, age }), [name, age])
<UserContext value={value}>
  <App />
</UserContext>
```

## 拆分 Context

把变化频率不同的数据拆成多个 Context，避免「改一个字段，全部消费者重渲染」：

```ts [src/user-contexts.ts]
import { createContext } from "react"

export const UserInfoContext = createContext<{ name: string; avatar: string } | null>(null)
export const UserActionsContext = createContext<{
  login: (name: string) => void
  logout: () => void
} | null>(null)
```

```tsx [src/UserProvider.tsx]
import { useCallback, useState } from "react"
import { UserActionsContext, UserInfoContext } from "./user-contexts"

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [name, setName] = useState("")

  const login = useCallback((n: string) => setName(n), [])
  const logout = useCallback(() => setName(""), [])

  return (
    <UserActionsContext value={{ login, logout }}>
      <UserInfoContext value={{ name, avatar: name ? "/avatar.png" : "" }}>
        {children}
      </UserInfoContext>
    </UserActionsContext>
  )
}
```

头像组件只订阅 `UserInfoContext`，登录/登出组件只订阅 `UserActionsContext`，互不干扰。

## Context + useReducer

小型应用可以用 Context 分发全局状态，不必引入 Redux：

```ts [src/cart-reducer.ts]
export interface CartItem {
  id: number
  name: string
  count: number
}

export type CartAction =
  | { type: "add"; item: CartItem }
  | { type: "remove"; id: number }
  | { type: "clear" }

export function cartReducer(state: CartItem[], action: CartAction): CartItem[] {
  switch (action.type) {
    case "add":
      return state.some((i) => i.id === action.item.id)
        ? state.map((i) =>
            i.id === action.item.id ? { ...i, count: i.count + 1 } : i,
          )
        : [...state, action.item]
    case "remove":
      return state.filter((i) => i.id !== action.id)
    case "clear":
      return []
    default:
      return state
  }
}
```

```tsx [src/CartProvider.tsx]
import { createContext, useReducer } from "react"
import { cartReducer, type CartItem } from "./cart-reducer"

export const CartStateContext = createContext<CartItem[]>([])
export const CartDispatchContext = createContext<React.Dispatch<CartAction>>(
  () => {},
)

export function CartProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(cartReducer, [])

  return (
    <CartDispatchContext value={dispatch}>
      <CartStateContext value={state}>{children}</CartStateContext>
    </CartDispatchContext>
  )
}
```

拆成「状态 Context」和「dispatch Context」两个，避免只读组件因 dispatch 引用变化而重渲染。

## React Compiler 与 Context

React Compiler（React 19 起可选接入）会自动记忆组件和值，减少手写 `useMemo`/`useCallback` 的必要。接入后 Context 值仍建议按「数据 vs 动作」拆分，编译器不是万能药。

## 易错点

::: danger 常见错误
1. 直接在 JSX 里写内联对象字面量作为 value，每次渲染都新建对象引用，所有消费者跟着重渲染。
2. 整个应用只放一个巨型 Context，任何字段变化都让全局组件刷新。
3. 忘了默认值：组件在 Provider 之外使用时拿到默认值，出现「读不到最新值」的困惑；重要场景用 `null` 并在消费端判空。
4. 在 Context 里放「高频变化」的数据（拖拽坐标、输入值），性能急剧下降。
5. React 19 中把 `<Context value>` 和 `<Context.Provider value>` 混写，风格不一致容易出 bug。
6. 用 Context 管理所有状态，组件树深了以后调试困难；规模变大时迁移到专门状态库。
:::

## 验证方式

1. 切换主题后，只有消费主题 Context 的组件重渲染（React DevTools Profiler 查看）。
2. 修改用户名，头像组件不重渲染（拆分 Context 生效）。
3. 用 `useReducer` 的购物车加减商品，列表和合计正确更新。
4. 移除 Provider 后组件能显示默认值或友好提示，而不是报错。
5. React DevTools 的 Components 面板能看到 Provider 层级和 value。

## 参考资料

- React Context 官方文档：https://zh-hans.react.dev/learn/passing-data-deeply-with-context
- useContext API：https://zh-hans.react.dev/reference/react/useContext
- useReducer：https://zh-hans.react.dev/reference/react/useReducer
- React 19 发布说明：https://react.dev/blog/2024/12/05/react-19
