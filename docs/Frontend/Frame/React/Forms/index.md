# React 表单与受控组件

表单是前端交互最密集的场景。本节从受控/非受控组件讲起，覆盖 React 19 的表单动作（Actions）、校验与文件上传，给出一套可落地的表单方案。

::: info 适用版本
本节基于 React 19.2.x。`useActionState`、`useFormStatus` 从 React 19 起稳定；复杂校验推荐配合 react-hook-form + zod。
:::

## 受控组件

受控组件的值由 React state 完全控制：

```tsx [src/LoginForm.tsx]
import { useState } from "react"

export default function LoginForm() {
  const [form, setForm] = useState({ email: "", password: "" })

  function update(field: keyof typeof form, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    console.log("提交：", form)
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={form.email}
        onChange={(e) => update("email", e.target.value)}
      />
      <input
        type="password"
        value={form.password}
        onChange={(e) => update("password", e.target.value)}
      />
      <button type="submit">登录</button>
    </form>
  )
}
```

优点：值唯一来源是 state，便于校验、联动、重置。

## 非受控组件

不需要实时响应时用非受控组件，值由 DOM 自己管理，提交时再读取：

```tsx
import { useRef } from "react"

export default function SimpleForm() {
  const nameRef = useRef<HTMLInputElement>(null)

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const data = new FormData(e.currentTarget)
    console.log("name:", data.get("name"))
    console.log("ref 值:", nameRef.current?.value)
  }

  return (
    <form onSubmit={handleSubmit}>
      <input name="name" ref={nameRef} />
      <button type="submit">提交</button>
    </form>
  )
}
```

给 `input` 加 `name` 属性后，`FormData` 会自动收集，是 React 19 表单动作的基础。

## React 19 表单动作

`<form action={fn}>` 让表单提交进入框架管理的状态：

```tsx [src/SignupForm.tsx]
import { useActionState } from "react"

async function signup(prevState: string, formData: FormData) {
  const name = String(formData.get("name") ?? "")
  if (!name) return "请输入用户名"
  await new Promise((r) => setTimeout(r, 500)) // 模拟接口
  return `注册成功：${name}`
}

export default function SignupForm() {
  const [message, formAction, isPending] = useActionState(signup, "")

  return (
    <form action={formAction}>
      <input name="name" placeholder="用户名" />
      <button type="submit" disabled={isPending}>
        {isPending ? "提交中..." : "注册"}
      </button>
      <p>{message}</p>
    </form>
  )
}
```

子组件里用 `useFormStatus` 读取父表单的 pending 状态：

```tsx [src/SubmitButton.tsx]
import { useFormStatus } from "react-dom"

export default function SubmitButton() {
  const { pending } = useFormStatus()
  return (
    <button type="submit" disabled={pending}>
      {pending ? "保存中..." : "保存"}
    </button>
  )
}
```

## 表单校验：react-hook-form + zod

简单校验可以手写；字段多、规则复杂时用 react-hook-form 管理状态与校验：

```shell
npm install react-hook-form zod @hookform/resolvers
```

```tsx [src/ProfileForm.tsx]
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"

const schema = z.object({
  email: z.string().email("邮箱格式不正确"),
  age: z.coerce.number().min(1, "年龄不能为空").max(120, "年龄超出范围"),
})

type FormValues = z.infer<typeof schema>

export default function ProfileForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
  })

  async function onSubmit(values: FormValues) {
    await fetch("/api/profile", {
      method: "POST",
      body: JSON.stringify(values),
    })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register("email")} />
      {errors.email && <p>{errors.email.message}</p>}

      <input type="number" {...register("age")} />
      {errors.age && <p>{errors.age.message}</p>}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "保存中..." : "保存"}
      </button>
    </form>
  )
}
```

## 文件上传

```tsx [src/UploadForm.tsx]
export default function UploadForm() {
  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const file = formData.get("file") as File
    console.log("文件名：", file?.name, "大小：", file?.size)
    // 交给后端：await fetch("/api/upload", { method: "POST", body: formData })
  }

  return (
    <form onSubmit={handleSubmit}>
      <input type="file" name="file" />
      <button type="submit">上传</button>
    </form>
  )
}
```

注意：`<input type="file">` 是只读的非受控输入，不要给它设置 `value`。

## 易错点

::: danger 常见错误
1. 受控 input 只写 `value` 不写 `onChange`，输入框不可编辑并报警告。
2. 用 `defaultValue` 想实现「受控 + 实时更新」，两者语义冲突。
3. `useActionState` 的 `prevState` 与「上一次表单值」混淆：它是上一次 action 的返回值，不是输入值。
4. 在 action 里 `await` 后仍尝试读取 `formData`，FormData 读取后内容仍在，但异步传输给后端时要先序列化。
5. 文件上传用 `JSON.stringify` 传 File 对象，实际丢失文件内容；应直接提交 FormData。
6. 校验只写前端不写后端，安全边界失效。
:::

## 验证方式

1. 受控输入框实时显示输入内容，提交后控制台打印最新值。
2. 非受控表单提交后 `FormData` 能取到所有带 `name` 的字段。
3. `useActionState` 表单：空用户名提交显示错误，有用户名提交显示成功，按钮在 pending 时禁用。
4. react-hook-form 表单：输入非法邮箱，提交被拦截并显示错误信息。
5. 文件上传选择文件后，控制台输出文件名和大小。

## 参考资料

- React 表单官方文档：https://zh-hans.react.dev/reference/react-dom/components/form
- useActionState：https://zh-hans.react.dev/reference/react/useActionState
- react-hook-form：https://react-hook-form.com/
- zod：https://zod.dev/
