# React 数据获取模式

「组件挂载后请求接口」只是数据获取的起点。本节覆盖请求竞态、loading/error 状态、SWR 与 TanStack Query 的缓存方案，以及服务端组件的取舍。

::: info 适用版本
本节基于 React 19.2.x。示例使用 TanStack Query 5.x（当前稳定版）；`use` Hook 与 Server Components 需要 React 19 + 支持 SSR 的框架（如 Next.js）。
:::

## 基础模式：useEffect + fetch

```tsx [src/useUser.ts]
import { useEffect, useState } from "react"

interface User {
  id: number
  name: string
}

export function useUser(userId: number) {
  const [user, setUser] = useState<User | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const [isPending, setIsPending] = useState(true)

  useEffect(() => {
    let cancelled = false
    setIsPending(true)

    fetch(`/api/users/${userId}`)
      .then((res) => {
        if (!res.ok) throw new Error("请求失败")
        return res.json()
      })
      .then((data) => {
        if (!cancelled) setUser(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err)
      })
      .finally(() => {
        if (!cancelled) setIsPending(false)
      })

    return () => {
      cancelled = true
    }
  }, [userId])

  return { user, error, isPending }
}
```

关键点：

- `cancelled` 标记防止组件卸载后 setState（React 18+ 不再警告，但仍会产生无效更新）。
- 依赖数组包含 `userId`，切换用户时重新请求。
- 错误需要 `try/catch` 或 `.catch` 处理，不能只写成功分支。

## 竞态问题

快速切换 `userId` 时，先发出的慢请求可能后返回，覆盖新数据。除了 `cancelled` 标记，更严谨的做法是记录最新请求序号：

```ts
useEffect(() => {
  let active = true
  const seq = ++requestSeq.current

  fetch(`/api/users/${userId}`)
    .then((r) => r.json())
    .then((data) => {
      if (active && seq === requestSeq.current) setUser(data)
    })

  return () => {
    active = false
  }
}, [userId])
```

如果接口支持，直接用 `AbortController` 取消旧请求更省资源：

```ts
useEffect(() => {
  const controller = new AbortController()
  fetch(`/api/users/${userId}`, { signal: controller.signal })
    .then((r) => r.json())
    .then(setUser)
    .catch((err) => {
      if (err.name !== "AbortError") setError(err)
    })
  return () => controller.abort()
}, [userId])
```

## 缓存与状态：TanStack Query

手写 fetch 每次进入页面都会重新请求，且没有缓存、重试、失效机制。TanStack Query 把「服务端状态」从组件 state 中分离：

```tsx [src/api/useUsers.ts]
import { useQuery } from "@tanstack/react-query"

export function useUser(userId: number) {
  return useQuery({
    queryKey: ["user", userId],
    queryFn: async () => {
      const res = await fetch(`/api/users/${userId}`)
      if (!res.ok) throw new Error("加载失败")
      return res.json()
    },
    staleTime: 60_000,   // 1 分钟内认为数据新鲜，不重复请求
    gcTime: 5 * 60_000,  // 5 分钟后清理缓存
  })
}
```

组件里统一使用 `isPending` / `isError` / `data`：

```tsx
function UserCard({ userId }: { userId: number }) {
  const { data, isPending, isError, refetch } = useUser(userId)

  if (isPending) return <p>加载中...</p>
  if (isError) return <button onClick={() => refetch()}>重试</button>
  return <p>{data.name}</p>
}
```

修改数据用 Mutation，成功后主动失效缓存：

```tsx
import { useMutation, useQueryClient } from "@tanstack/react-query"

function RenameButton({ userId }: { userId: number }) {
  const queryClient = useQueryClient()
  const mutation = useMutation({
    mutationFn: (name: string) =>
      fetch(`/api/users/${userId}`, {
        method: "PATCH",
        body: JSON.stringify({ name }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user", userId] })
    },
  })

  return <button onClick={() => mutation.mutate("新名字")}>改名</button>
}
```

## SWR 方案

SWR（stale-while-revalidate）是另一类轻量缓存方案，写法与 TanStack Query 类似：

```shell
npm install swr
```

```tsx
import useSWR from "swr"

const fetcher = (url: string) => fetch(url).then((r) => r.json())

function Profile({ userId }: { userId: number }) {
  const { data, error, isLoading } = useSWR(`/api/users/${userId}`, fetcher)
  if (isLoading) return <p>加载中...</p>
  if (error) return <p>出错了</p>
  return <p>{data.name}</p>
}
```

## Server Components 与 use

在支持 RSC 的框架（Next.js 等）中，服务端组件可以直接 `await` 数据，不需要客户端请求状态：

```tsx [app/users/[id]/page.tsx]
export default async function UserPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const res = await fetch(`https://api.example.com/users/${id}`)
  const user = await res.json()
  return <p>{user.name}</p>
}
```

客户端组件中，React 19 的 `use` 可以读取 Promise：

```tsx
import { use } from "react"

function UserName({ userPromise }: { userPromise: Promise<User> }) {
  const user = use(userPromise)
  return <p>{user.name}</p>
}
```

选择建议：服务端能拿到的数据优先服务端取；需要实时刷新、客户端交互、缓存失效的数据用 TanStack Query。

## 易错点

::: danger 常见错误
1. `useEffect` 请求不写清理逻辑，组件卸载后仍 setState（内存泄漏/无效更新）。
2. 竞态：慢请求覆盖新数据，切换参数后显示旧内容。
3. 所有接口都走 useEffect，没有缓存，切页就重新加载、重复请求。
4. TanStack Query 的 `queryKey` 不包含参数，切换用户后拿到上一个用户的数据。
5. mutation 成功后不 `invalidateQueries`，界面停留旧数据。
6. 在 Server Components 里把数据库密码等敏感逻辑写进客户端 bundle。
:::

## 验证方式

1. 快速切换用户，确认最终显示的是最后选择的用户（无竞态）。
2. Network 面板：同一数据在 `staleTime` 内切换回来不重复请求。
3. 修改用户名称后列表自动刷新（mutation 失效缓存生效）。
4. 断网重试按钮能重新请求并恢复界面。
5. `npm run build` 通过，服务端组件与客户端组件数据流正常。

## 参考资料

- TanStack Query：https://tanstack.com/query/latest
- SWR：https://swr.vercel.app/zh-CN
- React use Hook：https://zh-hans.react.dev/reference/react/use
- 服务端组件：https://react.dev/learn/start-a-new-react-project
