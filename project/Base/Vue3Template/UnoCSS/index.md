# 配置UnoCSS

UnoCSS 是一个高性能、可定制的原子化 CSS 框架。

## 安装依赖

安装 UnoCSS 及其相关依赖：

```bash
pnpm add unocss -D
```

## 配置 Vite 插件

在 `vite.config.ts`文件中添加 UnoCSS 插件：

```typescript [vite.config.ts]
// ...
import UnoCSS from 'unocss/vite'// 导入 UnoCSS 插件  // [!code focus] [!code highlight]


export default defineConfig({
   plugins:[
     // ...
     UnoCSS()   // [!code focus] [!code highlight]
   ],
   // ...
})
```

## 配置 UnoCSS

在根目录下创建 `uno.config.ts`文件，配置 UnoCSS，主要配置如下内容：

1. 预设配置：使用 Tailwind 预设
2. 转换器配置：支持 @apply、分组 
3. 主题配置：前面定义的 CSS 变量映射到 UnoCSS 
4. 规则：为 primary, success 等颜色生成工具类 
5. 快捷类：定义了两个样式快捷类名

```typescript
import {
  defineConfig,
  presetWind4,
  transformerDirectives,
  transformerVariantGroup,
  presetIcons,
} from 'unocss'

export default defineConfig({
  presets: [
    presetWind4({
      preflights: { reset: true },
    }),
    presetIcons({
      prefix: 'i-',
      extraProperties: {
        display: 'inline-block',
        'vertical-align': 'middle',
      },
    }),
  ],

  transformers: [
    // 启用 @apply 指令支持
    transformerDirectives(),
    // 启用 `hover:(bg-gray-400 text-white)` 类写法
    transformerVariantGroup(),
  ],

  theme: {
    colors: {
      // 品牌与状态色
      primary: 'var(--wm-color-primary)',
      success: 'var(--wm-color-success)',
      warning: 'var(--wm-color-warning)',
      danger: 'var(--wm-color-danger)',
      info: 'var(--wm-color-info)',
      // 文字色
      'text-primary': 'var(--wm-color-text-primary)',
      'text-regular': 'var(--wm-color-text-regular)',
      'text-secondary': 'var(--wm-color-text-secondary)',
      // 背景色
      'bg-page': 'var(--wm-bg-color-page)',
      'bg-base': 'var(--wm-bg-color-base)',
    },
    spacing: {
      xs: 'var(--wm-spacing-xs)',
      sm: 'var(--wm-spacing-sm)',
      md: 'var(--wm-spacing-md)',
      lg: 'var(--wm-spacing-lg)',
      xl: 'var(--wm-spacing-xl)',
      '2xl': 'var(--wm-spacing-2xl)',
    },
    fontSize: {
      xs: 'var(--wm-font-size-xs)',
      sm: 'var(--wm-font-size-sm)',
      base: 'var(--wm-font-size-base)',
      lg: 'var(--wm-font-size-lg)',
      xl: 'var(--wm-font-size-xl)',
      '2xl': 'var(--wm-font-size-2xl)',
      '3xl': 'var(--wm-font-size-3xl)',
    },
    borderRadius: {
      sm: 'var(--wm-border-radius-sm)',
      base: 'var(--wm-border-radius-base)',
      lg: 'var(--wm-border-radius-lg)',
      full: 'var(--wm-border-radius-full)',
    },
  },

  rules: [
    ...['primary', 'success', 'warning', 'danger', 'info'].flatMap((color) => [
      [`bg-${color}-light-3`, { 'background-color': `var(--wm-color-${color}-light-3)` }],
      [`bg-${color}-light-5`, { 'background-color': `var(--wm-color-${color}-light-5)` }],
      [`bg-${color}-light-7`, { 'background-color': `var(--wm-color-${color}-light-7)` }],
      [`bg-${color}-light-9`, { 'background-color': `var(--wm-color-${color}-light-9)` }],
      [`text-${color}-dark-2`, { color: `var(--wm-color-${color}-dark-2)` }],
    ]),
  ],
  //自定义属性 一个属性可以对应多个unocss类值
  shortcuts: {
    //垂直水平居中
    'flex-center': 'flex justify-center items-center',
    //放在最后
    'flex-col-end': 'flex justify-end items-center',
    //垂直居中
    'flex-middle': 'flex items-center',
    //分开两边
    'flex-between': 'flex justify-between items-center',
    //竖直居中
    'flex-col-center': 'flex flex-col justify-center',
  },
})
```

在以前的版本中，还需要手动添加样式重置 (安装 @unocss/reset, 并引入需要的样式重置文件)，但使用了 Tailwind 4 作为预设，可以通过配置 `preflights: { reset: true }`来开启样式重置，故这里无需安装其他依赖了。

**引入 UnoCSS**： 在 `src/plugins/assets.ts`文件中添加 UnoCSS 的引入：

```typescript
import 'virtual:uno.css' // 引入 UnoCSS
```

测试：

```vue
<template>
<div>
  <divclass="demo">Hello world</div>
  <divclass="text-xs text-primary">测试文字</div>
  <divclass="text-sm text-success">测试文字</div>
  <divclass="text-md text-info">测试文字</div>
  <divclass="text-base text-warning">测试文字</div>
  <divclass="text-lg text-danger">测试文字</div>
  <divclass="text-xl text-text-primary">测试文字</div>
  <divclass="text-2xl text-text-regular">测试文字</div>
  <divclass="text-3xl text-text-secondary">测试文字</div>

  <buttonclass="mt-xl px-md py-sm border rounded-base"@click="toggleTheme">
      切换深色/浅色模式
  </button>
</div>
</template>

<script setup lang="ts">
const toggleTheme= () => {
const html = document.documentElement
const currentTheme = html.getAttribute('data-theme')
  html.setAttribute('data-theme', currentTheme ==='dark'?'light':'dark')
}
</script>
<style scoped lang="scss">
.demo{
@apply text-xl text-primary bg-success-light-7;
}
</style>
```

## 配置图标

UnoCSS 的图标依赖于 `@iconify/json`，iconify 有很多图标集合，这些图标集合包含了 Element Plus、Ant Design 等，每个图标集合又有很多图标。

iconify 官网：https://icon-sets.iconify.design/

网站右上角的搜索框可以搜索想要的图标，左侧的搜索框可以过滤图标集。

使用 UnoCSS 图标预设，可以安装全量的图标集合，也可以指定安装具体的某个集合。安装全量作为开发依赖即可：

```bash
pnpm add @iconify/json -D
```

### 添加预设

在 `uno.config.ts`的 `presets`数组中配置图标预设：

```typescript [uno.config.ts]
import {
  // ...
  presetIcons,
} from 'unocss'

export default defineConfig({
  presets: [
    // ...
    presetIcons({
      prefix: 'i-',
      extraProperties: {
        display: 'inline-block',
        'vertical-align': 'middle',
      },
    }),
  ],
  // ...
})
```

### 测试使用图标

在 demo.vue 中测试使用图标：

```vue
<template>
  <div>
    <!-- A basic anchor icon from Phosphor icons -->
    <div class="i-ph-anchor-simple-thin" />
    <!-- An orange alarm from Material Design Icons -->
    <i class="i-mdi-alarm text-orange-400" />
    <!-- A large Vue logo -->
    <div class="i-logos-vue text-3xl" />
    <!-- Sun in light mode, Moon in dark mode, from Carbon -->
    <button class="i-carbon-sun dark:i-carbon-moon" />
    <!-- Twemoji of laugh, turns to tear on hovering -->
    <div class="i-twemoji-grinning-face-with-smiling-eyes hover:i-twemoji-face-with-tears-of-joy" />
    </div>
</template>
```

启动服务进行测试，看看在浏览器中是否会出现图标。

## 本地 SVG 图标

虽然 Iconify 提供了丰富的图标库，但项目开发中常常需要使用 UI 设计师提供的自定义 SVG 图标。因此，我们需要为模板项目添加本地 SVG 图标的支持。

### 安装依赖

安装 Vite SVG 图标插件：

```
pnpm add vite-plugin-svg-icons -D
```

### 配置 Vite 插件

1. 在 `vite.config.ts`中添加 SVG 图标插件配置：

   ```typescript [vite.config.ts]
   import { defineConfig } from 'vite'
   import vue from '@vitejs/plugin-vue'
   import UnoCSS from 'unocss/vite'
   import { createSvgIconsPlugin } from 'vite-plugin-svg-icons'
   import { fileURLToPath, URL } from 'node:url'
   
   export default defineConfig({
     plugins: [
       vue(),
       UnoCSS(),
       // 配置 SVG 图标插件
       createSvgIconsPlugin({
         // SVG 图标目录
         iconDirs: [fileURLToPath(new URL('./src/assets/icons', import.meta.url))],
         // 生成的 symbol ID 格式
         symbolId: 'icon-[dir]-[name]'
       })
     ],
   })
   ```

2. 创建 SVG 图标目录：在 `src/assets`目录中创建 `icons`目录，用于存放本地 SVG 图标。

3. 在 `src/plugins/assets.ts`中引入 SVG 图标：

   ```typescript [src/plugins/assets.ts]
   // ...
   import 'virtual:svg-icons-register'
   
   // ...
   ```

### 测试本地 SVG 图标

1. 准备 SVG 图标：在 `assets/icons`目录下添加一个 SVG 图标文件，例如 `demo.svg`

2. 在 `demo.vue`中测试 SVG 图标：

   ```vue
   <svg aria-hidden="true" class="svg">
     <use href="#icon-demo" fill="red" />
   </svg>
   ```

:::danger
在 vite.config.ts 中配置插件时定义了 symbolId：

1. svg 文件的存放位置要与 symbolId 一致。
2. href 图标的引用格式也要与 symbolId 一致。

:::

## 实现强大的图标组件

在真实开发过程中，除了会遇到 SVG 图标，还有可能遇到 iconfont 图标；另外，Iconify 也提供了 Vue 组件。

封装一个强大的图标组件，支持四种使用方式：

1. Iconify Icon
2. UnoCSS Icon (本质上也是 Iconify Icon)
3. 本地 svg 图标
4. 本地或在线的 Iconfont

### 创建组件

按照如下目录文件结构，创建图标组件：

```
src/
|- components/
    |- icon/
       |- icon.vue
```

初始化组件代码：

```vue [src/components/icon/icon.vue]
<template>
</template>

<script setup lang="ts">
defineOptions({ name: 'Icon' })
</script>

<style scoped lang="scss"></style>
```

### 定义属性 props

按照需求，组件的属性定义：

```vue [src/components/icon/icon.vue]
const props = withDefaults(
  defineProps<{
    /**
     * Icon 图标类型：
     * - uno：UnoCSS Icon，对应的 icon 属性：https://icones.js.org/
     * - iconify: Iconify 图标，对应的 icon 属性： https://icon-sets.iconify.design/
     * - svg：本地 SVG 图标
     * - iconfont：IconFont 图标
     */
    type?: 'uno' | 'svg' | 'iconify' | 'iconfont'
    icon: string
    prefix?: string
    fontFamily?: string
    fontUrl?: string
  }>(),
  {
    type: 'iconify',
    prefix: 'icon',
    fontFamily: 'iconfont',
  },
)
```

`type`：指定该组件的四种使用方式：

1. type 为 `uno`时，可以从如下地址搜索图标，并获取图标的 `name`：https://icones.js.org/collection/all
2. type 为 `iconfiy`时，可以从如下地址搜索图标，并获取图标的 `name`：https://icon-sets.iconify.design/
3. type 为 `svg`时，使用本地的 SVG 图标，SVG 图标的位置和前缀在 `vite.config.ts`中指定。如果配置的前缀不是字符串 `icon`，需要设置 `prefix`属性；

4. type 为 `iconfont`时，如果字体图标文件没有在 index.html 使用 link 标签引入，则需要设置 `fontUrl`属性；另外要注意字体图标的 prefix 和 font-family 是否与默认值一致，如果不一致也需要手动指定。

### 安装依赖

当 type 为 `iconfiy`时，使用 Iconify Icon Vue 组件，安装该组件：

```bash
pnpm add @iconify/vue
```

如果不需要使用 iconify，也可以不用安装，因为 UnoCSS 图标的方式，本质上也是 Iconify Icon 的图标。

### 实现组件

根据 type 的值，实现不同类型的使用：

```vue [src/components/icon/icon.vue]
<template>
  <div v-if="type === 'uno'" :class="icon" />

  <iconify-icon v-else-if="type === 'iconify'" :icon="icon" class="icon" :aria-hidden="false" />

  <svg v-else-if="type === 'svg'" class="svg">
    <use :href="svgSymbolId" fill="currentColor" />
  </svg>

  <i v-else-if="type === 'iconfont'" :class="iconfontClassName" />

  <span v-else>Unsupported type: {{ type }}</span>
</template>
<script setup lang="ts">
import { onBeforeMount, computed, withDefaults, defineProps } from 'vue'
import { Icon as IconifyIcon } from '@iconify/vue'

defineOptions({ name: 'Icon' })

const props = withDefaults(
  defineProps<{
    type?: 'uno' | 'svg' | 'iconify' | 'iconfont'
    icon: string
    prefix?: string
    fontFamily?: string
    fontUrl?: string
  }>(),
  {
    type: 'iconify',
    prefix: 'icon',
    fontFamily: 'iconfont',
  },
)

onBeforeMount(() => {
  if (props.type === 'iconfont' && props.fontUrl) {
    const existingLink = document.querySelector(`link[href="${props.fontUrl}"]`)
    if (!existingLink) {
      const link = document.createElement('link')
      link.rel = 'stylesheet'
      link.href = props.fontUrl
      document.head.appendChild(link)
    }
  }
})

const svgSymbolId = computed(() => `#${props.prefix}-${props.icon}`)

const iconfontClassName = computed(() => `${props.fontFamily} ${props.prefix}-${props.icon}`)
</script>

<style scoped lang="scss">
.icon {
  @apply inline-block align-mid text-xl;
}
.svg {
  @apply inline-block align-mid;
  width: 1rem;
  height: 1rem;
}
</style>
```

### 测试组件

在 demo.vue 中测试四种使用方式：

```vue [demo.vue]
<div>
  <icon type="iconify" icon="mdi:user" class="size-8 text-primary" />
  <icon type="uno" icon="i-mdi:user" class="size-8 text-primary" />
  <icon type="svg" icon="demo" class="text-primary size-8!" />
  <icon
    type="iconfont"
    font-url="//at.alicdn.com/t/c/font_3457715_h47rhjpli3n.css"
    icon="mobile-alt"
    class="text-primary text-2xl!"
  />
</div>
```

