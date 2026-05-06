# React 可访问性

可访问性（Accessibility，简称 a11y）确保所有用户，包括残障用户，都能正常使用应用。React 提供了多种方式来提升应用的可访问性。

## WAI-ARIA 属性

### 基本 ARIA 属性

```tsx [components/AccessibleButton.tsx]
function AccessibleButton() {
  return (
    <button
      aria-label="关闭对话框"
      aria-describedby="close-button-description"
      aria-pressed={false}
      aria-disabled={false}
    >
      ×
    </button>
  )
}

export default AccessibleButton
```

### 常用 ARIA 属性

| 属性 | 说明 | 示例 |
|------|------|------|
| `aria-label` | 为元素提供可访问的标签 | `aria-label="搜索"` |
| `aria-labelledby` | 引用作为标签的元素 ID | `aria-labelledby="title-id"` |
| `aria-describedby` | 引用描述元素 ID | `aria-describedby="desc-id"` |
| `aria-hidden` | 隐藏元素对辅助技术 | `aria-hidden="true"` |
| `aria-live` | 声明动态内容区域 | `aria-live="polite"` |
| `aria-expanded` | 指示展开/折叠状态 | `aria-expanded={isOpen}` |
| `aria-selected` | 指示选中状态 | `aria-selected={isSelected}` |
| `aria-required` | 指示必填字段 | `aria-required={true}` |
| `aria-invalid` | 指示无效状态 | `aria-invalid={hasError}` |

## 语义化 HTML

### 使用正确的 HTML 元素

```tsx [components/SemanticPage.tsx]
function SemanticPage() {
  return (
    <div>
      <header>
        <nav aria-label="主导航">
          <ul>
            <li><a href="/">首页</a></li>
            <li><a href="/about">关于</a></li>
          </ul>
        </nav>
      </header>

      <main>
        <article>
          <h1>文章标题</h1>
          <p>文章内容...</p>
        </article>

        <aside>
          <h2>侧边栏</h2>
          <p>相关信息...</p>
        </aside>
      </main>

      <footer>
        <p>© 2026 我的网站</p>
      </footer>
    </div>
  )
}

export default SemanticPage
```

### 避免使用 div 代替按钮

```tsx
// ❌ 错误：使用 div 模拟按钮
<div onClick={handleClick} className="button">
  点击我
</div>

// ✅ 正确：使用原生 button
<button onClick={handleClick}>
  点击我
</button>

// ✅ 如果必须使用 div，添加 role 和 tabIndex
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={e => e.key === 'Enter' && handleClick()}
  className="button"
>
  点击我
</div>
```

## 键盘导航

### 焦点管理

```tsx [components/Modal.tsx]
import { useEffect, useRef } from 'react'

function Modal({ isOpen, onClose, children }: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null)
  const previousFocusRef = useRef<HTMLElement | null>(null)

  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement as HTMLElement
      modalRef.current?.focus()
    }

    return () => {
      previousFocusRef.current?.focus()
    }
  }, [isOpen])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <div
      ref={modalRef}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      tabIndex={-1}
    >
      <h2 id="modal-title">对话框标题</h2>
      {children}
      <button onClick={onClose}>关闭</button>
    </div>
  )
}

export default Modal
```

### 焦点陷阱

```tsx [components/FocusTrap.tsx]
import { useEffect, useRef, type ReactNode } from 'react'

interface FocusTrapProps {
  children: ReactNode
  isActive: boolean
}

function FocusTrap({ children, isActive }: FocusTrapProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!isActive || !containerRef.current) return

    const container = containerRef.current
    const focusableElements = container.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    const firstElement = focusableElements[0]
    const lastElement = focusableElements[focusableElements.length - 1]

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault()
          lastElement.focus()
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault()
          firstElement.focus()
        }
      }
    }

    container.addEventListener('keydown', handleTabKey)
    firstElement?.focus()

    return () => container.removeEventListener('keydown', handleTabKey)
  }, [isActive])

  return <div ref={containerRef}>{children}</div>
}

export default FocusTrap
```

## 表单可访问性

```tsx [components/AccessibleForm.tsx]
function AccessibleForm() {
  return (
    <form>
      <div>
        <label htmlFor="email">邮箱</label>
        <input
          id="email"
          type="email"
          aria-required="true"
          aria-describedby="email-error"
          aria-invalid={!!emailError}
        />
        {emailError && (
          <span id="email-error" role="alert">
            {emailError}
          </span>
        )}
      </div>

      <div>
        <label htmlFor="password">密码</label>
        <input
          id="password"
          type="password"
          aria-required="true"
          aria-describedby="password-hint"
        />
        <span id="password-hint">至少 8 个字符</span>
      </div>

      <button type="submit">提交</button>
    </form>
  )
}

export default AccessibleForm
```

## 动态内容

### Live Regions

```tsx [components/Notification.tsx]
function Notification({ message }: { message: string }) {
  return (
    <div role="status" aria-live="polite">
      {message}
    </div>
  )
}

export default Notification
```

### 加载状态

```tsx [components/LoadingState.tsx]
function LoadingState() {
  return (
    <div role="status" aria-live="polite">
      <span className="sr-only">加载中...</span>
      <div className="spinner" aria-hidden="true" />
    </div>
  )
}

export default LoadingState
```

## 屏幕阅读器隐藏

```css [styles/accessibility.css]
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

## 颜色对比度

```tsx [components/AccessibleText.tsx]
function AccessibleText() {
  return (
    <div>
      <p style={{ color: '#333', backgroundColor: '#fff' }}>
        正常文本，对比度 12.6:1
      </p>
      <p style={{ color: '#767676', backgroundColor: '#fff' }}>
        次要文本，对比度 4.6:1
      </p>
    </div>
  )
}

export default AccessibleText
```

::: tip 提示
WCAG 2.1 要求：
- 正常文本：对比度至少 4.5:1
- 大文本（18pt 或 14pt 粗体）：对比度至少 3:1
:::

## 测试可访问性

### axe-core

```bash [终端]
npm install -D @axe-core/react
```

```typescript [src/main.tsx]
if (process.env.NODE_ENV === 'development') {
  import('@axe-core/react').then(axe => {
    axe.default(React, ReactDOM, 1000)
  })
}
```

### React Testing Library 可访问性查询

```tsx [src/components/Button.test.tsx]
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import Button from './Button'

describe('Button', () => {
  it('有可访问的标签', () => {
    render(<Button aria-label="提交表单">提交</Button>)
    expect(screen.getByRole('button', { name: /提交表单/i })).toBeInTheDocument()
  })
})
```

## 可访问性检查清单

| 检查项 | 说明 |
|--------|------|
| 语义化 HTML | 使用正确的 HTML 元素 |
| 键盘导航 | 所有功能可通过键盘访问 |
| 焦点管理 | 焦点顺序合理，可见 |
| 颜色对比度 | 满足 WCAG 2.1 要求 |
| 替代文本 | 图片有 alt 属性 |
| 表单标签 | 所有表单字段有 label |
| 错误提示 | 错误信息清晰且可访问 |
| 动态内容 | 使用 aria-live 通知变化 |
| 屏幕阅读器 | 测试屏幕阅读器兼容性 |
| 缩放 | 支持 200% 缩放 |
