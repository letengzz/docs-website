# React 国际化

国际化（i18n）让应用支持多语言，适应不同地区用户。本章介绍如何在 React 应用中实现国际化。

## react-i18next

### 安装

```bash [终端]
npm install i18next react-i18next i18next-browser-languagedetector
```

### 配置

```typescript [src/i18n/index.ts]
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

import zhCN from './locales/zh-CN.json'
import enUS from './locales/en-US.json'
import jaJP from './locales/ja-JP.json'

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      'zh-CN': { translation: zhCN },
      'en-US': { translation: enUS },
      'ja-JP': { translation: jaJP }
    },
    fallbackLng: 'zh-CN',
    debug: process.env.NODE_ENV === 'development',
    interpolation: {
      escapeValue: false
    }
  })

export default i18n
```

```json [src/i18n/locales/zh-CN.json]
{
  "common": {
    "welcome": "欢迎",
    "login": "登录",
    "logout": "退出登录",
    "save": "保存",
    "cancel": "取消",
    "delete": "删除",
    "edit": "编辑",
    "search": "搜索",
    "loading": "加载中...",
    "error": "出错了"
  },
  "home": {
    "title": "首页",
    "description": "这是首页描述"
  },
  "user": {
    "profile": "个人资料",
    "name": "姓名",
    "email": "邮箱",
    "age": "年龄",
    "greeting": "你好，{{name}}！",
    "unreadCount": "你有 {{count}} 条未读消息"
  }
}
```

```json [src/i18n/locales/en-US.json]
{
  "common": {
    "welcome": "Welcome",
    "login": "Login",
    "logout": "Logout",
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit",
    "search": "Search",
    "loading": "Loading...",
    "error": "Error"
  },
  "home": {
    "title": "Home",
    "description": "This is the home page description"
  },
  "user": {
    "profile": "Profile",
    "name": "Name",
    "email": "Email",
    "age": "Age",
    "greeting": "Hello, {{name}}!",
    "unreadCount": "You have {{count}} unread messages"
  }
}
```

### 使用

```tsx [src/main.tsx]
import { createRoot } from 'react-dom/client'
import App from './App'
import './i18n'

createRoot(document.getElementById('root')!).render(<App />)
```

```tsx [src/components/Header.tsx]
import { useTranslation } from 'react-i18next'

function Header() {
  const { t, i18n } = useTranslation()

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng)
  }

  return (
    <header>
      <h1>{t('home.title')}</h1>
      <nav>
        <button onClick={() => changeLanguage('zh-CN')}>中文</button>
        <button onClick={() => changeLanguage('en-US')}>English</button>
        <button onClick={() => changeLanguage('ja-JP')}>日本語</button>
      </nav>
    </header>
  )
}

export default Header
```

### 带变量的翻译

```tsx [src/components/UserGreeting.tsx]
import { useTranslation } from 'react-i18next'

function UserGreeting({ name }: { name: string }) {
  const { t } = useTranslation()

  return <h2>{t('user.greeting', { name })}</h2>
}

export default UserGreeting
```

### 复数处理

```tsx [src/components/Notification.tsx]
import { useTranslation } from 'react-i18next'

function Notification({ count }: { count: number }) {
  const { t } = useTranslation()

  return <p>{t('user.unreadCount', { count })}</p>
}

export default Notification
```

```json [src/i18n/locales/en-US.json]
{
  "user": {
    "unreadCount_one": "You have {{count}} unread message",
    "unreadCount_other": "You have {{count}} unread messages"
  }
}
```

## 日期和时间格式化

### 使用 Intl API

```tsx [src/components/FormattedDate.tsx]
interface FormattedDateProps {
  date: Date | string
  locale?: string
}

function FormattedDate({ date, locale = 'zh-CN' }: FormattedDateProps) {
  const formattedDate = new Intl.DateTimeFormat(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(new Date(date))

  return <span>{formattedDate}</span>
}

export default FormattedDate
```

### 数字格式化

```tsx [src/components/FormattedNumber.tsx]
interface FormattedNumberProps {
  value: number
  style?: 'decimal' | 'currency' | 'percent'
  currency?: string
  locale?: string
}

function FormattedNumber({
  value,
  style = 'decimal',
  currency = 'CNY',
  locale = 'zh-CN'
}: FormattedNumberProps) {
  const formattedNumber = new Intl.NumberFormat(locale, {
    style,
    currency
  }).format(value)

  return <span>{formattedNumber}</span>
}

export default FormattedNumber
```

## 语言切换组件

```tsx [src/components/LanguageSwitcher.tsx]
import { useTranslation } from 'react-i18next'

const languages = [
  { code: 'zh-CN', name: '中文', flag: '🇨🇳' },
  { code: 'en-US', name: 'English', flag: '🇺🇸' },
  { code: 'ja-JP', name: '日本語', flag: '🇯🇵' }
]

function LanguageSwitcher() {
  const { i18n } = useTranslation()

  return (
    <div className="language-switcher">
      {languages.map(lang => (
        <button
          key={lang.code}
          onClick={() => i18n.changeLanguage(lang.code)}
          className={i18n.language === lang.code ? 'active' : ''}
        >
          {lang.flag} {lang.name}
        </button>
      ))}
    </div>
  )
}

export default LanguageSwitcher
```

## 动态加载翻译文件

```typescript [src/i18n/index.ts]
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import Backend from 'i18next-http-backend'

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'zh-CN',
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json'
    },
    interpolation: {
      escapeValue: false
    }
  })

export default i18n
```

## RTL 支持

```tsx [src/components/App.tsx]
import { useEffect } from 'react'
import { useTranslation } from 'react-i18next'

function App() {
  const { i18n } = useTranslation()

  useEffect(() => {
    const isRTL = ['ar', 'he', 'fa', 'ur'].includes(i18n.language)
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr'
  }, [i18n.language])

  return <div>{/* 应用内容 */}</div>
}

export default App
```

## 国际化最佳实践

| 实践 | 说明 |
|------|------|
| 使用 key 而非原文 | 翻译文件中使用 key 而非英文原文 |
| 避免字符串拼接 | 使用变量替换而非字符串拼接 |
| 处理复数形式 | 不同语言复数规则不同 |
| 日期时间本地化 | 使用 Intl API 格式化 |
| 数字本地化 | 货币、百分比等格式化 |
| 文本方向 | 支持 RTL 语言 |
| 字体选择 | 不同语言可能需要不同字体 |
| 测试多语言 | 测试所有支持的语言 |
