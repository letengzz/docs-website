# React 错误边界

错误边界是 React 中用于捕获子组件树中 JavaScript 错误的组件。它可以防止整个应用崩溃，并提供友好的错误提示。

## 创建错误边界

### 类组件方式

错误边界必须使用类组件实现，因为只有类组件支持 `componentDidCatch` 和 `getDerivedStateFromError`：

```tsx [components/ErrorBoundary.tsx]
import { Component, type ErrorInfo, type ReactNode } from 'react'

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode | ((error: Error, reset: () => void) => ReactNode)
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('错误边界捕获:', error)
    console.error('组件栈:', errorInfo.componentStack)

    this.props.onError?.(error, errorInfo)
  }

  reset = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError) {
      if (typeof this.props.fallback === 'function') {
        return this.props.fallback(this.state.error!, this.reset)
      }
      return (
        this.props.fallback || (
          <div className="error-boundary">
            <h2>出错了</h2>
            <p>{this.state.error?.message}</p>
            <button onClick={this.reset}>重试</button>
          </div>
        )
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
```

### 使用错误边界

```tsx [App.tsx]
import ErrorBoundary from './components/ErrorBoundary'
import UserProfile from './components/UserProfile'
import Dashboard from './components/Dashboard'

function App() {
  return (
    <ErrorBoundary>
      <div className="app">
        <header>应用标题</header>
        <main>
          <ErrorBoundary fallback={<div>用户信息加载失败</div>}>
            <UserProfile />
          </ErrorBoundary>

          <ErrorBoundary
            fallback={(error, reset) => (
              <div>
                <h3>仪表盘错误</h3>
                <p>{error.message}</p>
                <button onClick={reset}>重试</button>
              </div>
            )}
          >
            <Dashboard />
          </ErrorBoundary>
        </main>
      </div>
    </ErrorBoundary>
  )
}

export default App
```

## 错误边界不能捕获的错误

::: danger 注意
错误边界不能捕获以下类型的错误：

- 事件处理器中的错误（如 onClick）
- 异步代码中的错误（如 setTimeout、Promise）
- 服务端渲染中的错误
- 错误边界自身内部的错误
:::

### 事件处理器错误处理

```tsx [components/EventHandler.tsx]
function EventHandler() {
  const handleClick = () => {
    try {
      throw new Error('事件处理器错误')
    } catch (error) {
      console.error('捕获事件错误:', error)
    }
  }

  return <button onClick={handleClick}>点击</button>
}

export default EventHandler
```

### 异步错误处理

```tsx [components/AsyncComponent.tsx]
import { useState, useEffect } from 'react'

function AsyncComponent() {
  const [error, setError] = useState<Error | null>(null)
  const [data, setData] = useState(null)

  useEffect(() => {
    fetchData()
      .then(setData)
      .catch(setError)
  }, [])

  if (error) {
    return <div>加载失败：{error.message}</div>
  }

  return <div>{data}</div>
}

export default AsyncComponent
```

## React 19 错误处理改进

### 更好的错误信息

React 19 改进了错误报告，特别是 SSR 和服务端组件的错误信息更清晰：

```tsx [components/ServerErrorHandler.tsx]
'use client'

import { useEffect } from 'react'

export default function Error({
  error,
  reset
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('错误摘要:', error.digest)
    console.error('错误详情:', error.message)
  }, [error])

  return (
    <div className="error-container">
      <h2>页面加载失败</h2>
      <p>{error.message}</p>
      {error.digest && <p>错误代码：{error.digest}</p>}
      <button onClick={() => reset()}>重试</button>
    </div>
  )
}
```

## 全局错误处理

### 使用 window.onerror

```typescript [src/error-handler.ts]
window.onerror = function(message, source, lineno, colno, error) {
  console.error('全局错误:', {
    message,
    source,
    line: lineno,
    column: colno,
    error: error?.stack
  })

  // 发送错误到监控服务
  reportError({
    type: 'window_error',
    message: String(message),
    stack: error?.stack
  })
}

window.onunhandledrejection = function(event: PromiseRejectionEvent) {
  console.error('未处理的 Promise 拒绝:', event.reason)

  reportError({
    type: 'unhandled_rejection',
    message: String(event.reason),
    stack: event.reason?.stack
  })
}

function reportError(error: Record<string, unknown>) {
  // 发送到错误监控服务
  fetch('/api/errors', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(error)
  })
}
```

## 错误边界最佳实践

### 分层错误边界

```tsx [App.tsx]
import ErrorBoundary from './components/ErrorBoundary'

function App() {
  return (
    <ErrorBoundary fallback={<AppError />}>
      <Header />
      <ErrorBoundary fallback={<SidebarError />}>
        <Sidebar />
      </ErrorBoundary>
      <ErrorBoundary fallback={<ContentError />}>
        <MainContent />
      </ErrorBoundary>
      <Footer />
    </ErrorBoundary>
  )
}

export default App
```

### 错误报告

```tsx [components/ErrorReporter.tsx]
import { Component, type ErrorInfo, type ReactNode } from 'react'

interface ErrorReporterProps {
  children: ReactNode
}

interface ErrorReporterState {
  error: Error | null
}

class ErrorReporter extends Component<ErrorReporterProps, ErrorReporterState> {
  state: ErrorReporterState = { error: null }

  static getDerivedStateFromError(error: Error) {
    return { error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.reportError(error, errorInfo)
  }

  reportError(error: Error, errorInfo: ErrorInfo) {
    const errorData = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent
    }

    // 发送到错误监控服务
    fetch('/api/errors', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(errorData)
    }).catch(console.error)
  }

  render() {
    if (this.state.error) {
      return (
        <div className="error-reporter">
          <h2>应用遇到错误</h2>
          <p>我们已记录此错误，请稍后重试</p>
          <button onClick={() => window.location.reload()}>刷新页面</button>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorReporter
```

## 开发环境错误覆盖

```tsx [components/DevErrorOverlay.tsx]
import { Component, type ErrorInfo, type ReactNode } from 'react'

interface DevErrorOverlayProps {
  children: ReactNode
}

interface DevErrorOverlayState {
  error: Error | null
  errorInfo: ErrorInfo | null
}

class DevErrorOverlay extends Component<DevErrorOverlayProps, DevErrorOverlayState> {
  state: DevErrorOverlayState = { error: null, errorInfo: null }

  static getDerivedStateFromError(error: Error) {
    return { error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ errorInfo })
  }

  render() {
    if (this.state.error && process.env.NODE_ENV === 'development') {
      return (
        <div style={{
          padding: '20px',
          backgroundColor: '#ffebee',
          border: '1px solid #f44336',
          borderRadius: '4px',
          margin: '10px'
        }}>
          <h3 style={{ color: '#c62828' }}>开发环境错误</h3>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px' }}>
            {this.state.error.message}
            {this.state.errorInfo?.componentStack}
          </pre>
        </div>
      )
    }

    return this.props.children
  }
}

export default DevErrorOverlay
```
