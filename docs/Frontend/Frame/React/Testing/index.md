# React 测试

::: info 版本现状
常用工具链：Vitest 3+、React Testing Library 16+、Playwright；具体版本以官方发布为准，安装时使用 `npm install -D` 引入。
:::

React 测试是确保应用质量的重要环节。本章介绍如何使用现代工具测试 React 组件。

## 测试工具链

| 工具 | 用途 | 说明 |
|------|------|------|
| Vitest | 测试运行器 | 替代 Jest，与 Vite 深度集成 |
| React Testing Library | 组件测试 | 以用户视角测试组件行为 |
| Playwright | E2E 测试 | 跨浏览器端到端测试 |
| MSW | API 模拟 | 模拟网络请求 |

## 安装

```bash [终端]
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

```typescript [vitest.config.ts]
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    include: ['src/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}']
  }
})
```

```typescript [src/test/setup.ts]
import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

afterEach(() => {
  cleanup()
})
```

## 组件测试基础

### 渲染测试

```tsx [src/components/Button.test.tsx]
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import Button from './Button'

describe('Button', () => {
  it('渲染按钮文本', () => {
    render(<Button>点击我</Button>)
    expect(screen.getByRole('button', { name: /点击我/i })).toBeInTheDocument()
  })

  it('渲染为指定类型', () => {
    render(<Button type="submit">提交</Button>)
    expect(screen.getByRole('button')).toHaveAttribute('type', 'submit')
  })

  it('应用自定义类名', () => {
    render(<Button className="custom-class">按钮</Button>)
    expect(screen.getByRole('button')).toHaveClass('custom-class')
  })
})
```

### 交互测试

```tsx [src/components/Counter.test.tsx]
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect } from 'vitest'
import Counter from './Counter'

describe('Counter', () => {
  it('点击按钮增加计数', async () => {
    const user = userEvent.setup()
    render(<Counter />)

    const count = screen.getByText(/计数:/i)
    const button = screen.getByRole('button', { name: /增加/i })

    expect(count).toHaveTextContent('计数: 0')

    await user.click(button)
    expect(count).toHaveTextContent('计数: 1')

    await user.click(button)
    expect(count).toHaveTextContent('计数: 2')
  })

  it('点击重置按钮归零', async () => {
    const user = userEvent.setup()
    render(<Counter />)

    const button = screen.getByRole('button', { name: /增加/i })
    const resetButton = screen.getByRole('button', { name: /重置/i })

    await user.click(button)
    await user.click(button)
    await user.click(resetButton)

    expect(screen.getByText(/计数:/i)).toHaveTextContent('计数: 0')
  })
})
```

## 异步测试

### 数据获取测试

```tsx [src/components/UserProfile.test.tsx]
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import UserProfile from './UserProfile'

vi.mock('@/api', () => ({
  fetchUser: vi.fn()
}))

import { fetchUser } from '@/api'

describe('UserProfile', () => {
  it('加载并显示用户信息', async () => {
    const mockUser = { id: 1, name: '张三', email: 'zhangsan@example.com' }
    vi.mocked(fetchUser).mockResolvedValue(mockUser)

    render(<UserProfile userId="1" />)

    expect(screen.getByText(/加载中/i)).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.getByText('张三')).toBeInTheDocument()
      expect(screen.getByText('zhangsan@example.com')).toBeInTheDocument()
    })
  })

  it('显示错误信息', async () => {
    vi.mocked(fetchUser).mockRejectedValue(new Error('网络错误'))

    render(<UserProfile userId="1" />)

    await waitFor(() => {
      expect(screen.getByText(/网络错误/i)).toBeInTheDocument()
    })
  })
})
```

## 表单测试

```tsx [src/components/LoginForm.test.tsx]
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import LoginForm from './LoginForm'

describe('LoginForm', () => {
  it('提交表单调用登录函数', async () => {
    const user = userEvent.setup()
    const onLogin = vi.fn()

    render(<LoginForm onLogin={onLogin} />)

    const emailInput = screen.getByLabelText(/邮箱/i)
    const passwordInput = screen.getByLabelText(/密码/i)
    const submitButton = screen.getByRole('button', { name: /登录/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'password123')
    await user.click(submitButton)

    expect(onLogin).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123'
    })
  })

  it('显示验证错误', async () => {
    const user = userEvent.setup()

    render(<LoginForm onLogin={() => {}} />)

    const submitButton = screen.getByRole('button', { name: /登录/i })
    await user.click(submitButton)

    expect(screen.getByText(/邮箱不能为空/i)).toBeInTheDocument()
    expect(screen.getByText(/密码不能为空/i)).toBeInTheDocument()
  })
})
```

## 自定义 Hook 测试

```tsx [src/hooks/useCounter.test.ts]
import { renderHook, act } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { useCounter } from './useCounter'

describe('useCounter', () => {
  it('初始化计数为 0', () => {
    const { result } = renderHook(() => useCounter())
    expect(result.current.count).toBe(0)
  })

  it('增加计数', () => {
    const { result } = renderHook(() => useCounter())

    act(() => {
      result.current.increment()
    })

    expect(result.current.count).toBe(1)
  })

  it('减少计数', () => {
    const { result } = renderHook(() => useCounter())

    act(() => {
      result.current.decrement()
    })

    expect(result.current.count).toBe(-1)
  })

  it('重置计数', () => {
    const { result } = renderHook(() => useCounter())

    act(() => {
      result.current.increment()
      result.current.increment()
      result.current.reset()
    })

    expect(result.current.count).toBe(0)
  })

  it('自定义初始值', () => {
    const { result } = renderHook(() => useCounter(10))
    expect(result.current.count).toBe(10)
  })
})
```

## Context 测试

```tsx [src/contexts/ThemeContext.test.tsx]
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { ThemeProvider, useTheme } from './ThemeContext'

function TestComponent() {
  const { theme, toggleTheme } = useTheme()
  return (
    <div>
      <span data-testid="theme">{theme}</span>
      <button onClick={toggleTheme}>切换</button>
    </div>
  )
}

describe('ThemeContext', () => {
  it('提供默认主题', () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    )

    expect(screen.getByTestId('theme')).toHaveTextContent('light')
  })

  it('切换主题', async () => {
    const user = userEvent.setup()

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    )

    const button = screen.getByRole('button', { name: /切换/i })
    await user.click(button)

    expect(screen.getByTestId('theme')).toHaveTextContent('dark')
  })
})
```

## Mock 测试

### 模拟模块

```tsx [src/components/ProductList.test.tsx]
import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import ProductList from './ProductList'

vi.mock('@/api/products', () => ({
  getProducts: vi.fn()
}))

import { getProducts } from '@/api/products'

describe('ProductList', () => {
  it('显示产品列表', async () => {
    const mockProducts = [
      { id: 1, name: '产品 A', price: 100 },
      { id: 2, name: '产品 B', price: 200 }
    ]

    vi.mocked(getProducts).mockResolvedValue(mockProducts)

    render(<ProductList />)

    await waitFor(() => {
      expect(screen.getByText('产品 A')).toBeInTheDocument()
      expect(screen.getByText('产品 B')).toBeInTheDocument()
    })
  })
})
```

### 模拟全局对象

```tsx [src/components/CopyButton.test.tsx]
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import CopyButton from './CopyButton'

describe('CopyButton', () => {
  it('复制文本到剪贴板', async () => {
    const user = userEvent.setup()
    const mockClipboard = { writeText: vi.fn() }
    Object.assign(navigator, { clipboard: mockClipboard })

    render(<CopyButton text="要复制的文本" />)

    const button = screen.getByRole('button', { name: /复制/i })
    await user.click(button)

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('要复制的文本')
    expect(screen.getByText(/已复制/i)).toBeInTheDocument()
  })
})
```

## 快照测试

```tsx [src/components/Header.test.tsx]
import { render } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import Header from './Header'

describe('Header', () => {
  it('匹配快照', () => {
    const { container } = render(<Header title="我的应用" />)
    expect(container).toMatchSnapshot()
  })
})
```

## E2E 测试

### Playwright 配置

```bash [终端]
npm install -D @playwright/test
npx playwright install
```

```typescript [playwright.config.ts]
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] }
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] }
    }
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI
  }
})
```

```typescript [e2e/todo.spec.ts]
import { test, expect } from '@playwright/test'

test.describe('Todo 应用', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('添加待办事项', async ({ page }) => {
    await page.getByPlaceholder('添加待办').fill('学习 React')
    await page.getByRole('button', { name: '添加' }).click()

    await expect(page.getByText('学习 React')).toBeVisible()
  })

  test('完成待办事项', async ({ page }) => {
    await page.getByPlaceholder('添加待办').fill('学习 React')
    await page.getByRole('button', { name: '添加' }).click()

    await page.getByRole('checkbox').check()
    await expect(page.getByText('学习 React')).toHaveClass(/completed/)
  })

  test('删除待办事项', async ({ page }) => {
    await page.getByPlaceholder('添加待办').fill('学习 React')
    await page.getByRole('button', { name: '添加' }).click()

    await page.getByRole('button', { name: '删除' }).click()
    await expect(page.getByText('学习 React')).not.toBeVisible()
  })
})
```

## 测试覆盖率

```bash [终端]
npx vitest run --coverage
```

```typescript [vitest.config.ts]
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80
      }
    }
  }
})
```

## 测试最佳实践

| 原则 | 说明 |
|------|------|
| 测试行为而非实现 | 关注用户能看到什么、能做什么 |
| 使用语义化查询 | 优先使用 getByRole、getByText |
| 避免测试库内部 | 不测试 React 内部实现 |
| 模拟外部依赖 | API、localStorage 等 |
| 保持测试独立 | 每个测试互不影响 |
| 测试边界情况 | 空数据、错误状态、加载状态 |

## 相关专题

- [前端工程化](../../../Others/FrontendEngineering/index.md)：Vitest + Testing Library 的完整测试体系
- [单元测试与组件测试](../../../Others/FrontendEngineering/Testing/index.md)：测试金字塔与覆盖率门禁
