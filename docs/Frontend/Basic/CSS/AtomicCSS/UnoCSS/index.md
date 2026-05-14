# UnoCSS

UnoCSS 是一个高性能、高度可定制的原子化 CSS 引擎，具有灵活的预设系统和极快的编译速度。

- 官网：https://unocss.dev/
- 中文网：https://www.unocss.cn/

## 特点

- **极快**：基于正则匹配，编译速度极快
- **灵活**：支持多种预设和自定义规则
- **兼容**：兼容 Tailwind CSS 和 Windi CSS 的语法
- **按需生成**：只生成实际使用的样式
- **框架无关**：支持 Vue、React、Svelte 等框架

## 安装

```bash
# npm 安装
npm install -D unocss

# 常用插件
npm install -D @unocss/preset-rem-to-px @unocss/transformer-directives @unocss/eslint-config
```

## 配置

### Vite 配置

```typescript [vite.config.ts]
import { defineConfig } from 'vite'
import UnoCSS from 'unocss/vite'

export default defineConfig({
  plugins: [
    UnoCSS(),
  ],
})
```

### UnoCSS 配置

```typescript [uno.config.ts]
import {
  defineConfig,
  presetAttributify,
  presetIcons,
  presetUno,
  presetWind3,
  transformerDirectives,
  transformerVariantGroup,
} from 'unocss'

// rem 转 px 预设
import presetRemToPx from '@unocss/preset-rem-to-px'

export default defineConfig({
  presets: [
    // 属性化模式
    presetAttributify(),
    // 默认预设
    presetUno(),
    // 或 Windi CSS 预设
    // presetWind3(),
    // rem 转 px
    presetRemToPx({
      baseFontSize: 4,
    }),
    // 图标预设
    presetIcons({
      scale: 1.2,
      collections: {
        // Element Plus 图标
        ep: () => import('@iconify-json/ep/icons.json').then(i => i.default),
        // Ant Design 图标
        antd: () => import('@iconify-json/ant-design/icons.json').then(i => i.default),
      },
    }),
  ],
  transformers: [
    // 支持 @apply、@screen、theme()
    transformerDirectives(),
    // 支持变体组语法
    transformerVariantGroup(),
  ],
  // 自定义规则
  rules: [
    // 自定义背景图片规则
    [
      /^bg-img-\[(.+)\]$/,
      ([, value]) => {
        const path = value.replace(/_/g, '/')
        return {
          'background-image': `url(${path})`,
          'background-repeat': 'no-repeat',
          'background-size': '100% 100%',
        }
      },
    ],
  ],
  // 快捷方式
  shortcuts: {
    // 垂直水平居中
    'flex-center': 'flex justify-center items-center',
    // 垂直居中
    'flex-middle': 'flex items-center',
    // 两端对齐
    'flex-between': 'flex justify-between items-center',
    // 放在最后
    'flex-col-end': 'flex justify-end items-center',
    // 竖直居中
    'flex-col-center': 'flex flex-col justify-center',
    // 字体基线对齐
    'flex-baseline': 'flex items-baseline',
  },
  // 主题配置
  theme: {
    breakpoints: {
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
    },
    colors: {
      primary: {
        50: '#f0f9ff',
        100: '#e0f2fe',
        200: '#bae6fd',
        300: '#7dd3fc',
        400: '#38bdf8',
        500: '#0ea5e9',
        600: '#0284c7',
        700: '#0369a1',
        800: '#075985',
        900: '#0c4a6e',
      },
    },
  },
  // 安全列表（动态生成的类名需要在此声明）
  safelist: [
    'i-menu-home',
    'i-menu-setting',
  ],
})
```

### 全局引入

```typescript [main.ts]
import 'virtual:uno.css'
```

## 使用方式

### 类名模式

```html
<div class="h-100 w-100 bg-red-800 text-30 text-blue hover:text-black">
  小猫米
</div>
```

### 属性模式

```html
<div h-100 w-100 bg="blue-800" text="30 blue hover:black">
  小猫米
</div>
```

### 变体组

```html
<!-- 原始写法 -->
<div class="hover:bg-red-500 hover:text-white focus:bg-red-500 focus:text-white">
  按钮
</div>

<!-- 变体组写法 -->
<div class="hover:(bg-red-500 text-white) focus:(bg-red-500 text-white)">
  按钮
</div>
```

## 常用工具类

### 尺寸

#### 宽度

- `w-10`：宽度 10px
- `w-[200px]`：自定义宽度
- `w-full`：100%
- `w-screen`：视窗宽度
- `min-w-10`：最小宽度
- `max-w-100`：最大宽度

#### 高度

- `h-10`：高度 10px
- `h-[200px]`：自定义高度
- `h-full`：100%
- `h-screen`：视窗高度
- `min-h-10`：最小高度
- `max-h-100`：最大高度

### 间距

#### 外边距

- `m-4`：全方向 16px
- `mx-4`：水平方向 16px
- `mx-a`：水平居中
- `my-4`：垂直方向 16px
- `my-a`：垂直居中
- `mt-4`：上 16px
- `mt-a`：上自动
- `mr-4`：右 16px
- `mb-4`：下 16px
- `ml-4`：左 16px

#### 内边距

- `p-4`：全方向 16px
- `px-4`：水平方向 16px
- `py-4`：垂直方向 16px
- `pt-4`：上 16px
- `pr-4`：右 16px
- `pb-4`：下 16px
- `pl-4`：左 16px

### 颜色和背景

- `text-red`：文本颜色
- `text-[#ff0000]`：自定义颜色
- `bg-blue-500`：背景颜色
- `bg-[#0000ff]`：自定义背景
- `bg-gradient-to-r from-blue-500 to-purple-500`：渐变背景

### 边框

- `border`：1px 边框
- `border-2`：2px 边框
- `border-red`：红色边框
- `rounded-md`：中等圆角
- `rounded-full`：完全圆角
- `b-rd-2`：2px 圆角

### Flex 布局

#### 基础

- `flex`：启用 flex
- `inline-flex`：行内 flex
- `flex-row`：水平方向
- `flex-col`：垂直方向
- `flex-row-reverse`：反向水平
- `flex-col-reverse`：反向垂直

#### 换行

- `flex-wrap`：允许换行
- `flex-nowrap`：不换行
- `flex-wrap-reverse`：反向换行

#### 主轴对齐

- `justify-start`：起点
- `justify-end`：终点
- `justify-center`：居中
- `justify-between`：两端对齐
- `justify-around`：均匀分布
- `justify-evenly`：等距分布

#### 交叉轴对齐

- `items-start`：起点
- `items-end`：终点
- `items-center`：居中
- `items-baseline`：基线
- `items-stretch`：拉伸

#### 项目属性

- `flex-1`：flex: 1
- `flex-auto`：flex: auto
- `flex-none`：flex: none
- `flex-initial`：flex: initial

#### 实用组合

- `flex-center`：垂直水平居中
- `flex-end`：放在最后
- `flex-middle`：垂直居中
- `flex-between`：分开两边
- `flex-col-center`：竖直居中
- `flex-baseline`：字体基线对齐

### Grid 布局

#### 基础

- `grid`：启用 grid
- `inline-grid`：行内 grid

#### 网格模板

- `grid-cols-3`：3 列
- `grid-cols-[100px_1fr_2fr]`：自定义列宽
- `grid-rows-3`：3 行
- `grid-rows-[100px_1fr_2fr]`：自定义行高

#### 间距

- `gap-4`：行列间距 4px
- `gap-x-4`：列间距
- `gap-y-4`：行间距

#### 项目位置和跨度

- `col-span-2`：跨越 2 列
- `row-span-2`：跨越 2 行
- `col-start-2`：从第 2 列开始
- `col-end-5`：在第 5 列结束
- `row-start-2`：从第 2 行开始
- `row-end-5`：在第 5 行结束

#### 对齐

- `justify-items-start`：水平起点
- `justify-items-end`：水平终点
- `justify-items-center`：水平居中
- `justify-items-stretch`：水平拉伸
- `content-start`：垂直起点
- `content-end`：垂直终点
- `content-center`：垂直居中
- `content-between`：垂直两端对齐
- `content-around`：垂直均匀分布

## @apply 指令

在 CSS 中使用 `@apply` 组合工具类：

```vue
<style lang="scss" scoped>
.box2 {
  @apply h-100 w-100 bg-red-800 text-30 text-blue hover:text-black;
}
</style>
```

## @screen 指令

使用 `@screen` 创建媒体查询：

```css
@media (--sm) {
  /* 640px 以上 */
}

/* 或使用 @screen */
@screen sm {
  .container {
    width: 640px;
  }
}
```

## theme() 函数

在 CSS 中访问主题配置：

```css
.card {
  background-color: theme('colors.primary.500');
  border-radius: theme('borderRadius.lg');
}
```

## 图标

### 安装图标库

```bash
# 安装图标预设
pnpm add -D @unocss/preset-icons

# 安装具体图标库（在 https://icon-sets.iconify.design/ 搜索）
pnpm install -D @iconify-json/ep        # Element Plus
pnpm install -D @iconify-json/ant-design # Ant Design
```

### 使用方式

```html
<!-- 网络图标（使用 - 或 : 分隔） -->
<div i-ep-dish></div>
<div i-ep:switch-button></div>
<div class="i-ant-design-linux-outlined"></div>

<!-- 本地图标 -->
<div i-local-folder></div>
```

### 配置本地图标

```typescript [uno.config.ts]
import { FileSystemIconLoader } from 'unplugin-icons/loaders'

presetIcons({
  collections: {
    // 本地 SVG 图标
    menu: FileSystemIconLoader('./src/assets/svg/menu'),
    // 在线图标
    ep: () => import('@iconify-json/ep/icons.json').then(i => i.default),
  },
})
```

## 预设

### presetUno

默认预设，兼容 Tailwind CSS 和 Windi CSS。

```typescript
import { presetUno } from 'unocss'

export default defineConfig({
  presets: [presetUno()],
})
```

### presetWind3

Windi CSS 预设，与 Windi CSS 完全兼容。

```typescript
import { presetWind3 } from 'unocss'

export default defineConfig({
  presets: [presetWind3()],
})
```

### presetAttributify

属性化模式，允许使用属性代替 class。

```typescript
import { presetAttributify } from 'unocss'

export default defineConfig({
  presets: [
    presetAttributify({
      // 忽略的属性
      ignoreAttributes: ['container', 'table'],
    }),
  ],
})
```

```html
<!-- 属性化模式 -->
<div bg="blue-500 hover:blue-600" text="white sm" p="4" m="2">
  内容
</div>
```

### presetIcons

图标预设。

```typescript
import { presetIcons } from 'unocss'

export default defineConfig({
  presets: [
    presetIcons({
      scale: 1.2,
      warn: true,
      collections: {
        ep: () => import('@iconify-json/ep/icons.json').then(i => i.default),
      },
    }),
  ],
})
```

### presetRemToPx

将 rem 单位转换为 px。

```typescript
import presetRemToPx from '@unocss/preset-rem-to-px'

export default defineConfig({
  presets: [
    presetRemToPx({
      baseFontSize: 4, // mt-1 转换为 margin-top: 1px
    }),
  ],
})
```

## 转换器

### transformerDirectives

支持 `@apply`、`@screen`、`theme()` 指令。

```typescript
import { transformerDirectives } from 'unocss'

export default defineConfig({
  transformers: [transformerDirectives()],
})
```

### transformerVariantGroup

支持变体组语法。

```typescript
import { transformerVariantGroup } from 'unocss'

export default defineConfig({
  transformers: [transformerVariantGroup()],
})
```

```html
<!-- 变体组 -->
<div class="hover:(bg-red-500 text-white) focus:(bg-red-500 text-white)">
  按钮
</div>
```

## 自定义规则

### 动态规则

```typescript
export default defineConfig({
  rules: [
    // m-1 转换为 margin: 0.25rem
    [/^m-(\d+)$/, ([, d]) => ({ margin: `${d / 4}rem` })],
    // p-1 转换为 padding: 0.25rem
    [/^p-(\d+)$/, ([, d]) => ({ padding: `${d / 4}rem` })],
  ],
})
```

### 静态规则

```typescript
export default defineConfig({
  rules: [
    ['custom-shadow', { 'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)' }],
  ],
})
```

## 快捷方式

### 静态快捷方式

```typescript
export default defineConfig({
  shortcuts: {
    'btn': 'px-4 py-2 rounded font-semibold',
    'btn-primary': 'bg-blue-500 text-white hover:bg-blue-600',
    'card': 'bg-white rounded-lg shadow p-6',
  },
})
```

### 动态快捷方式

```typescript
export default defineConfig({
  shortcuts: [
    // t14 转换为 text-14 color=rgba(37,51,71,1)
    // t145 转换为 text-14 color=rgba(37,51,71,0.55)
    // t14b5 转换为 text-14 color=rgba(37,51,71,1) font-weight: 500
    [/^t(\d{2})(\d)?(b\d+)?$/, ([, size, opacity, weight]) => {
      const fontSize = `text-${size}`
      const fontWeight = weight ? `font-${weight.slice(1)}00` : ''
      const opacityValue = opacity ? (Number(opacity) * 0.1 + 0.05).toFixed(2) : '1'
      const color = `text-[rgba(37,51,71,${opacityValue})]`
      return `${fontSize} ${fontWeight} ${color}`
    }],
  ],
})
```

## 响应式

UnoCSS 使用移动优先的响应式设计。

```html
<!-- 移动端单列，平板两列，桌面三列 -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div class="bg-white p-4 rounded shadow">卡片 1</div>
  <div class="bg-white p-4 rounded shadow">卡片 2</div>
  <div class="bg-white p-4 rounded shadow">卡片 3</div>
</div>
```

默认断点：

| 断点 | 前缀 | 最小宽度 |
|------|------|----------|
| sm | sm | 640px |
| md | md | 768px |
| lg | lg | 1024px |
| xl | xl | 1280px |
| 2xl | 2xl | 1536px |

## 实际项目示例

### 卡片组件

```html
<div class="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow">
  <div class="p-6">
    <div class="text-sm text-primary-500 font-semibold">标签</div>
    <h3 class="mt-1 text-lg font-medium text-gray-900">卡片标题</h3>
    <p class="mt-2 text-gray-500">这是一段卡片描述文字。</p>
    <div class="mt-4 flex-center gap-4">
      <button class="btn btn-primary">操作</button>
      <button class="btn">取消</button>
    </div>
  </div>
</div>
```

### 导航栏

```html
<nav class="bg-white shadow-sm">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between h-16">
      <div class="flex">
        <div class="flex-shrink-0 flex items-center">
          <span class="text-xl font-bold text-primary-500">Logo</span>
        </div>
        <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
          <a href="#" class="border-primary-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">首页</a>
          <a href="#" class="border-transparent text-gray-500 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">产品</a>
          <a href="#" class="border-transparent text-gray-500 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">关于</a>
        </div>
      </div>
      <div class="flex items-center">
        <button class="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded text-sm font-medium">
          登录
        </button>
      </div>
    </div>
  </div>
</nav>
```

### 仪表盘

```html
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 p-6">
  <div class="bg-white rounded-lg shadow p-6">
    <div class="text-3xl font-bold text-blue-500">1,234</div>
    <div class="text-sm text-gray-500 mt-1">总用户数</div>
  </div>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="text-3xl font-bold text-green-500">567</div>
    <div class="text-sm text-gray-500 mt-1">活跃用户</div>
  </div>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="text-3xl font-bold text-yellow-500">89</div>
    <div class="text-sm text-gray-500 mt-1">待处理</div>
  </div>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="text-3xl font-bold text-red-500">12</div>
    <div class="text-sm text-gray-500 mt-1">错误数</div>
  </div>
</div>
```

::: tip 提示
- UnoCSS 兼容 Tailwind CSS 和 Windi CSS 语法
- 使用属性化模式可以让代码更简洁
- 使用变体组可以减少重复的前缀
- 动态生成的类名需要添加到 safelist
- 使用 transformerDirectives 可以在 CSS 中使用 @apply
:::

::: danger 注意事项
- UnoCSS 默认不会生成未使用的样式，动态类名需要配置 safelist
- 本地图标需要正确配置路径和 loader
- 属性化模式可能与某些框架的属性冲突
- 自定义规则时注意正则表达式的性能
- 生产环境确保正确配置 content 扫描路径
:::
