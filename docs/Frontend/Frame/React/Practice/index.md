# React 实战案例

用一个可运行的「商品搜索 + 购物车」项目，把 React 19、TypeScript、React Router、Zustand、TanStack Query 串起来。项目约 10 个文件，可直接在 `Vite + React + TS` 模板上运行。

::: info 运行环境
React 19.2.x、Vite、TypeScript、React Router 8.x、Zustand 5.x、TanStack Query 5.x。Node 建议 22+（LTS）。
:::

## 功能设计

| 页面 | 功能 |
| --- | --- |
| 首页 `/` | 商品列表、关键词搜索、加入购物车 |
| 商品详情 `/product/:id` | 展示单个商品 |
| 购物车 `/cart` | 数量加减、清空、合计 |

数据先用本地 mock 模拟，方便验证；把 mock 换成 API 即接入真实后端。

## 1. 创建项目

```shell
npm create vite@latest react-shop -- --template react-ts
cd react-shop
npm install
npm install react-router zustand @tanstack/react-query
```

## 2. 类型与 mock 数据

```ts [src/types.ts]
export interface Product {
  id: number
  name: string
  price: number
  category: string
}

export interface CartItem extends Product {
  count: number
}
```

```ts [src/mock.ts]
import type { Product } from "./types"

export const products: Product[] = [
  { id: 1, name: "机械键盘", price: 299, category: "外设" },
  { id: 2, name: "无线鼠标", price: 129, category: "外设" },
  { id: 3, name: "27 寸显示器", price: 1299, category: "显示" },
  { id: 4, name: "人体工学椅", price: 899, category: "家具" },
]

export function fetchProducts(keyword: string): Promise<Product[]> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const kw = keyword.trim()
      resolve(products.filter((p) => p.name.includes(kw)))
    }, 300)
  })
}
```

## 3. 购物车 Store（Zustand）

```ts [src/stores/cart.ts]
import { create } from "zustand"
import type { CartItem, Product } from "../types"

interface CartState {
  items: CartItem[]
  add: (product: Product) => void
  changeCount: (id: number, delta: number) => void
  clear: () => void
}

export const useCartStore = create<CartState>((set) => ({
  items: [],
  add: (product) =>
    set((state) => {
      const exist = state.items.find((item) => item.id === product.id)
      if (exist) {
        return {
          items: state.items.map((item) =>
            item.id === product.id ? { ...item, count: item.count + 1 } : item,
          ),
        }
      }
      return { items: [...state.items, { ...product, count: 1 }] }
    }),
  changeCount: (id, delta) =>
    set((state) => ({
      items: state.items
        .map((item) =>
          item.id === id ? { ...item, count: item.count + delta } : item,
        )
        .filter((item) => item.count > 0),
    })),
  clear: () => set({ items: [] }),
}))
```

组件里只订阅用到的切片，避免整个 store 变化都触发重渲染：

```ts
import { useCartStore } from "../stores/cart"

const items = useCartStore((state) => state.items)
const add = useCartStore((state) => state.add)
```

## 4. TanStack Query 数据获取

```ts [src/api/useProducts.ts]
import { useQuery } from "@tanstack/react-query"
import { fetchProducts } from "../mock"

export function useProducts(keyword: string) {
  return useQuery({
    queryKey: ["products", keyword],
    queryFn: () => fetchProducts(keyword),
    placeholderData: (prev) => prev, // 搜索时保留旧数据，避免闪烁
  })
}
```

## 5. 首页组件

```tsx [src/pages/Home.tsx]
import { useState } from "react"
import { Link } from "react-router"
import { useProducts } from "../api/useProducts"
import { useCartStore } from "../stores/cart"

export default function Home() {
  const [keyword, setKeyword] = useState("")
  const { data, isPending } = useProducts(keyword)
  const add = useCartStore((state) => state.add)

  return (
    <div>
      <h2>商品列表</h2>
      <input
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
        placeholder="搜索商品名称"
      />
      {isPending ? (
        <p>加载中...</p>
      ) : (
        <ul>
          {data?.map((product) => (
            <li key={product.id}>
              <Link to={`/product/${product.id}`}>{product.name}</Link>
              <span> ¥{product.price} </span>
              <button onClick={() => add(product)}>加入购物车</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
```

## 6. 购物车组件

```tsx [src/pages/Cart.tsx]
import { useCartStore } from "../stores/cart"

export default function Cart() {
  const items = useCartStore((state) => state.items)
  const changeCount = useCartStore((state) => state.changeCount)
  const clear = useCartStore((state) => state.clear)

  const totalCount = items.reduce((sum, item) => sum + item.count, 0)
  const totalPrice = items.reduce(
    (sum, item) => sum + item.price * item.count,
    0,
  )

  return (
    <div>
      <h2>购物车（{totalCount} 件）</h2>
      {items.length === 0 ? (
        <p>购物车是空的</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>名称</th>
              <th>单价</th>
              <th>数量</th>
              <th>小计</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td>{item.name}</td>
                <td>¥{item.price}</td>
                <td>
                  <button onClick={() => changeCount(item.id, -1)}>-</button>
                  {item.count}
                  <button onClick={() => changeCount(item.id, 1)}>+</button>
                </td>
                <td>¥{item.price * item.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <p>合计：¥{totalPrice}</p>
      <button onClick={clear}>清空</button>
    </div>
  )
}
```

## 7. 路由与入口

```tsx [src/main.tsx]
import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { BrowserRouter } from "react-router"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import App from "./App"

const queryClient = new QueryClient()

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
)
```

```tsx [src/App.tsx]
import { NavLink, Route, Routes } from "react-router"
import Home from "./pages/Home"
import Cart from "./pages/Cart"
import ProductDetail from "./pages/ProductDetail"
import { useCartStore } from "./stores/cart"

export default function App() {
  const totalCount = useCartStore((state) =>
    state.items.reduce((sum, item) => sum + item.count, 0),
  )

  return (
    <div>
      <nav>
        <NavLink to="/">首页</NavLink>
        <NavLink to="/cart">购物车（{totalCount}）</NavLink>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/product/:id" element={<ProductDetail />} />
        <Route path="/cart" element={<Cart />} />
      </Routes>
    </div>
  )
}
```

商品详情页：

```tsx [src/pages/ProductDetail.tsx]
import { useParams, Link } from "react-router"
import { products } from "../mock"

export default function ProductDetail() {
  const { id } = useParams()
  const product = products.find((p) => p.id === Number(id))

  if (!product) {
    return <p>商品不存在，<Link to="/">返回首页</Link></p>
  }

  return (
    <div>
      <h2>{product.name}</h2>
      <p>分类：{product.category}，价格：¥{product.price}</p>
    </div>
  )
}
```

## 验证方式

1. `npm run dev` 启动，访问 http://localhost:5173/。
2. 搜索「键盘」，列表只剩机械键盘；清空搜索后恢复全部商品。
3. 点击「加入购物车」，导航栏数量 +1；重复加入只增加数量。
4. 进入购物车页，加减数量、小计和合计实时更新；减到 0 自动移除。
5. 点击商品名进入详情页，刷新后页面正常。
6. `npm run build` 构建成功，`npm run preview` 预览正常。

## 扩展思路

- 把 mock 换成真实 API：`fetchProducts` 改为 `fetch("/api/products")`。
- 购物车用 `zustand/middleware/persist` 持久化到 localStorage。
- 用 `lazy()` 懒加载购物车页和详情页。
- 用 react-hook-form + zod 给结算表单加校验。
- 补一组 Vitest + Testing Library 组件测试。

## 参考资料

- React 官方文档：https://zh-hans.react.dev/
- React Router：https://reactrouter.com/
- Zustand：https://zustand.docs.pmnd.rs/
- TanStack Query：https://tanstack.com/query/latest
