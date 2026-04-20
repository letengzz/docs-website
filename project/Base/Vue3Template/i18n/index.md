# 配置国际化

在 Vue 中实现国际化，不假思索选择 **vue-i18n**，它是 Vue 官方推荐的国际化插件，支持 Vue3 组合式 API，提供了完整的类型定义。

官网地址：https://vue-i18n.intlify.dev

## 安装依赖

安装 vue-i18n：使用 `@11`标签安装支持 Vue3 的版本

```bash
pnpm add vue-i18n@11
```

## 国际化配置及语言包

在 `src`目录下创建 `i18n`目录，用于存放国际化相关的配置和语言包：

```
src/
|- i18n/
    |- index.ts        # 国际化配置文件
    |- locales/        # 语言包目录
       |- zh-CN.ts     # 中文语言包
       |- en-US.ts     # 英文语言包
```

1. 中文语言包：

   ```typescript [src/i18n/locales/zh-CN.ts]
   export default {
     common: {
       hello: '你好',
       welcome: '欢迎，{name}!',
     },
     home: {
       title: '欢迎使用 Vue3 通用模板',
       description: '这是一个功能完善、易于扩展的 Vue3 通用模板项目',
     },
   }
   ```

2. 英文语言包：

   ```typescript [src/i18n/locales/en-US.ts]
   export default {
     common: {
       welcome: 'Welcome, {name}!',
     },
     home: {
       title: 'Welcome to Vue3 Common Template',
       description: 'This is a feature-rich, easy-to-extend Vue3 common template project',
     },
   }
   ```

3. 实现国际化配置：

   ```typescript [src/i18n/index.ts]
   import type { App } from 'vue'
   import { createI18n } from 'vue-i18n'
   import zhCN from './locales/zh-CN'
   import enUS from './locales/en-US'
   
   // 创建 i18n 实例
   const i18n = createI18n({
     legacy: false, // 使用 Composition API
     locale: 'zh-CN',
     fallbackLocale: 'zh-CN', // fallback 语言
     messages: {
       'zh-CN': zhCN,
       'en-US': enUS,
     },
   })
   
   export const useI18n = (app: App) => {
     app.use(i18n)
   }
   ```

## 集成到应用

在 main.ts 中调用 useI18n函数：

```typescript
// ...
import { useI18n } from '@/i18n'

const app = createApp(App)
// ...
useI18n(app)
// ...
```

## 翻译文本与语言切换

在 pages/i18n.vue 进行测试国际化文本的翻译及语言的切换：

- 在界面上放了语言的按钮和国际化展示的文本。
- 在 template 中可以使用 **$t()**获取翻译文本；
- 在 TS 中使用 useI18n 组合式 API获取翻译文本。
- 动态设置 locale.value 修改全局使用的语言。

```vue
<template>
  <div class="flex gap-2">
    <button v-for="lang in languages" :key="lang.value" :class="{ active: currentLocale === lang.value }"
      @click="onChangeLanguage(lang.value)">
      {{ lang.label }}
    </button>
  </div>
  <div>{{ $t('common.welcome', { name: 'Hjc' }) }}</div>
  <div>{{ $t('home.title') }}</div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()
console.log(t('common.welcome', { name: 'Hjc' }))

const currentLocale = locale

// 支持的语言
const languages = [
  { label: '中文', value: 'zh-CN' },
  { label: 'English', value: 'en-US' },
]

const onChangeLanguage = async (lang: string) => {
  locale.value = lang
}
</script>
```

## 配置插件

`@intlify/unplugin-vue-i18n`是由 Vue I18n 官方团队开发的插件，使用它有两个原因：

- **省事**：它支持自动导入语言包，无需像上面那样手动导入语言文件，该插件会自动扫描并导入。
- **高效**：该插件在构建时预编译 message，减少运行时的开销。

### 安装依赖

安装开发依赖：

```bash
pnpm add @intlify/unplugin-vue-i18n -D
```

### 配置 vite 插件

在 `vite.config.ts`配置该插件：

```typescript [vite.config.ts]
// ...
import vueI18n from '@intlify/unplugin-vue-i18n/vite'
import path from 'node:path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  //...
  return {
    plugins: [
      // ...
      vueI18n({
        // 语言包目录
        include: path.resolve(__dirname, './src/i18n/locales/**'),
        // 开发模式下也启动编译时处理
        runtimeOnly: false,
        // 仅使用组合式 API
        compositionOnly: true,
        // 完整安装
        fullInstall: true,
      }),
    ],
    // ...
  }
})
```

### 主配置文件

在 src/i18n/index.ts 中，已经通过 createI18n 函数创建了 i18n 实例：

```typescript [src/i18n/index.ts]
// 创建 i18n 实例
const i18n = createI18n({
  legacy: false, // 使用 Composition API
  locale: 'zh-CN',
  fallbackLocale: 'zh-CN', // fallback 语言
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS,
  },
})
```

上面有两个地方需要修改：

1. 默认的 `locale`先从本地存储中获取，如果没有便默认使用浏览器的语言。
2. `messages`属性也不用指定，初始时为空，后面通过懒加载来填充。

因此，整个配置文件还需要添加两个函数：

1. 获取浏览器的语言；
2. 动态加载语言包；

完整代码：

```typescript [src/i18n/index.ts]
import type { App } from 'vue'
import { createI18n } from 'vue-i18n'

/**
 * 获取浏览器的语言
 */
const getBrowserLanguage = () => {
  const browserLang = navigator.language || (navigator as any).userLanguage
  return ['zh-CN', 'en-US'].includes(browserLang) ? browserLang : 'zh-CN'
}

const currentLang = localStorage.getItem('locale') || getBrowserLanguage()

// 创建 i18n 实例
const i18n = createI18n({
  legacy: false, // 使用 Composition API
  locale: currentLang,
  fallbackLocale: 'zh-CN', // fallback 语言
  messages: {},
})

/**
 * 动态加载语言包
 */
export async function loadLanguage(lang: string) {
  return import(`./locales/${lang}.ts`).then((messages) => {
    i18n.global.setLocaleMessage(lang, messages.default)
    localStorage.setItem('locale', lang)
    return lang
  })
}

loadLanguage(currentLang)

export const installI18n = (app: App) => {
  app.use(i18n)
}

export default i18n
```

### 切换语言

前文在 `pages/index.vue`中提供了语言切换的功能，点击按钮时会调用函数`onChangeLanguage`，由于现在懒加载语言包，需要修改该函数的视线：

```typescript
const onChangeLanguage = async (lang: string) => {
  // 加载语言包
  await loadLanguage(lang)
  // 设置当前语言
  locale.value = lang
}
```

到这一步，基本功能也算完事。但也还不够，对于大型应用，语言包会很庞大，因此需要实现路由级别的语言包懒加载。

## 路由级别的懒加载

实现路由级别的懒加载，就是**根据当前路由动态加载对应的语言模块**。

首先准备语言包和页面。目前 pages 中还有一个 demo.vue，就以 demo 为案例模块：当跳转 demo 页面时，动态加载这个页面的语言包。

### 语言包和页面

在 src/i18n/locales 中创建目录 `modules`，并在 `modules`中创建两个目录`zh-CN`、`en-US`，分别存放各模块的中文英文语言包，
现在的目录结构如下：

```
src/
|- i18n/
   |- index.ts        # 国际化配置文件
   |- locales/        # 语言包目录
      |- zh-CN.ts     # 通用中文语言包
      |- en-US.ts     # 通用英文语言包
      |- modules/      # 模块语言包
        |- en-US/     # 模块英文语言包
           |- demo.ts    # 测试模块
           |- ... 其他模块的英文
        |- zh-CN/     # 模块中文语言包
           |- demo.ts    # 测试模块
           |- ... 其他模块的中文
```

```typescript [src/i18n/locales/modules/zh-CN/demo.ts]
export default {
  title: '示例页面',
  info: '这是一个示例页面',
}
```

```typescript [src/i18n/locales/modules/zh-CN/demo.ts]
export default {
  title: 'Demo Page',
  info: 'This is a demo page',
}
```

```vue [src/pages/demo.vue]
<div>
  <div class="text-2xl text-danger">{{ $t('demo.title') }}</div>
  <div>{{ $t('demo.info') }}</div>
</div>
```

### 路由配置

在 demo 页面的路由配置中，通过 meta 信息指定需要加载的语言包模块。

在通用模板项目中，前面集成了基于文件系统的路由，没有原生的路由配置文件，可以在 demo.vue 的 `script`中通过 `definePage`来配置：

```vue
<template>
  <div>
    <div class="text-2xl text-danger">{{ $t('demo.title') }}</div>
    <div>{{ $t('demo.info') }}</div>
  </div>
</template>

<script setup lang="ts">
definePage({
  meta: {
    locales: ['demo'],
  },
})
</script>
```

一个页面可能需要加载多个模块的语言包，所以 locales 属性定义为一个字符串数组。

### 路由守卫中实现懒加载

在 `router/index.ts`添加路由守卫，在路由的前置守卫中根据 meta.locales 动态加载语言包：

```typescript
// ...
async function loadRouteLocales(to: RouteLocationNormalized) {
  const currentLang = localStorage.getItem('locale') || 'zh-CN'

  // 确保通用语言已加载
  await loadLanguage(currentLang)

  // 加载路由所需的语言模块
  if (to.meta.locales) {
    for (const locale of to.meta.locales as string[]) {
      try {
        await import(`@/i18n/locales/modules/${currentLang}/${locale}.ts`).then((messages) => {
          // 合并到当前语言的消息中
          i18n.global.mergeLocaleMessage(currentLang, {
              [locale]: messages.default,
          })
        })
      } catch (e) {
          console.warn(`Failed to load locale module: ${locale}`, e)
      }
    }
  }
}

// 路由前置守卫
router.beforeEach(async (to, from, next) => {
  await loadRouteLocales(to)
  next()
})
// ...
```

由于前置守卫可能还需要处理其他业务逻辑，因此将加载语言包抽取到独立的函数中。