# Tailwind CSS

Tailwind CSS 是一个功能类优先（utility-first）的 CSS 框架，它提供了丰富的工具类，可以直接在 HTML 中组合出各种样式，无需编写自定义 CSS。

- 官网：https://tailwindcss.com/
- 中文网：https://www.tailwindcss.cn/

## 安装与配置

### Vite 项目安装

```bash
# 安装依赖
npm install -D tailwindcss @tailwindcss/vite
```

配置 Vite 插件：

```typescript [vite.config.ts]
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    tailwindcss(),
  ],
})
```

在 CSS 中引入 Tailwind：

```css [src/style.css]
@import "tailwindcss";
```

在入口文件中引入：

```typescript [main.ts]
import './style.css'
```

### PostCSS 方式安装（传统方式）

```bash
# 安装依赖
npm install -D tailwindcss postcss autoprefixer

# 初始化配置文件
npx tailwindcss init -p
```

配置文件：

```javascript [tailwind.config.js]
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

```javascript [postcss.config.js]
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

在 CSS 中引入：

```css [src/style.css]
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## 核心概念

### 工具类优先

Tailwind 采用工具类优先的方式，通过组合多个小粒度的类名来实现样式。

```html
<div class="flex items-center justify-center h-screen bg-gray-100">
  <p class="text-2xl font-bold text-gray-800">Hello Tailwind</p>
</div>
```

### 响应式设计

Tailwind 使用断点前缀来实现响应式设计。

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

### 状态变体

Tailwind 提供了丰富的状态变体来处理交互效果。

```html
<!-- hover 状态 -->
<button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
  按钮
</button>

<!-- focus 状态 -->
<input class="border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none px-3 py-2 rounded">

<!-- active 状态 -->
<button class="bg-blue-500 active:bg-blue-800 text-white py-2 px-4 rounded">
  按下按钮
</button>

<!-- 组合状态 -->
<button class="bg-blue-500 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 text-white py-2 px-4 rounded">
  完整状态
</button>
```

### 伪元素

```html
<!-- before 伪元素 -->
<div class="before:content-['★'] before:text-yellow-500 before:mr-1">
  收藏
</div>

<!-- after 伪元素 -->
<div class="after:content-['→'] after:ml-1 after:text-blue-500">
  了解更多
</div>

<!-- first-letter 伪元素 -->
<p class="first-letter:text-4xl first-letter:font-bold first-letter:text-blue-500 first-letter:float-left first-letter:mr-2">
  首字下沉效果
</p>
```

## 常用工具类

### 布局

#### Flexbox

```html
<!-- 基础布局 -->
<div class="flex">flex 容器</div>
<div class="inline-flex">行内 flex 容器</div>

<!-- 方向 -->
<div class="flex-row">水平方向</div>
<div class="flex-col">垂直方向</div>
<div class="flex-row-reverse">反向水平</div>
<div class="flex-col-reverse">反向垂直</div>

<!-- 换行 -->
<div class="flex-wrap">允许换行</div>
<div class="flex-nowrap">不换行</div>

<!-- 主轴对齐 -->
<div class="justify-start">起点</div>
<div class="justify-end">终点</div>
<div class="justify-center">居中</div>
<div class="justify-between">两端对齐</div>
<div class="justify-around">均匀分布</div>
<div class="justify-evenly">等距分布</div>

<!-- 交叉轴对齐 -->
<div class="items-start">起点</div>
<div class="items-end">终点</div>
<div class="items-center">居中</div>
<div class="items-baseline">基线对齐</div>
<div class="items-stretch">拉伸</div>

<!-- 项目属性 -->
<div class="flex-1">flex: 1 1 0%</div>
<div class="flex-auto">flex: 1 1 auto</div>
<div class="flex-none">flex: none</div>
<div class="flex-grow">flex-grow: 1</div>
<div class="flex-shrink">flex-shrink: 1</div>
```

#### Grid

```html
<!-- 基础布局 -->
<div class="grid">grid 容器</div>
<div class="inline-grid">行内 grid 容器</div>

<!-- 列 -->
<div class="grid-cols-1">1 列</div>
<div class="grid-cols-2">2 列</div>
<div class="grid-cols-3">3 列</div>
<div class="grid-cols-4">4 列</div>
<div class="grid-cols-12">12 列</div>
<div class="grid-cols-[100px_1fr_2fr]">自定义列宽</div>

<!-- 行 -->
<div class="grid-rows-2">2 行</div>
<div class="grid-rows-3">3 行</div>
<div class="grid-rows-[100px_auto]">自定义行高</div>

<!-- 间距 -->
<div class="gap-4">行列间距 4px</div>
<div class="gap-x-4">列间距 4px</div>
<div class="gap-y-4">行间距 4px</div>

<!-- 跨越 -->
<div class="col-span-2">跨越 2 列</div>
<div class="row-span-2">跨越 2 行</div>
<div class="col-start-2">从第 2 列开始</div>
<div class="col-end-5">在第 5 列结束</div>
```

### 尺寸

#### 宽度

```html
<!-- 固定宽度 -->
<div class="w-0">0px</div>
<div class="w-1">4px</div>
<div class="w-2">8px</div>
<div class="w-4">16px</div>
<div class="w-8">32px</div>
<div class="w-16">64px</div>
<div class="w-32">128px</div>
<div class="w-64">256px</div>

<!-- 百分比宽度 -->
<div class="w-1/2">50%</div>
<div class="w-1/3">33.333%</div>
<div class="w-2/3">66.666%</div>
<div class="w-1/4">25%</div>
<div class="w-3/4">75%</div>
<div class="w-full">100%</div>

<!-- 特殊宽度 -->
<div class="w-screen">100vw</div>
<div class="w-min">min-content</div>
<div class="w-max">max-content</div>
<div class="w-fit">fit-content</div>

<!-- 自定义宽度 -->
<div class="w-[200px]">200px</div>
<div class="w-[50%]">50%</div>
<div class="w-[calc(100%-2rem)]">calc(100%-2rem)</div>

<!-- 最小/最大宽度 -->
<div class="min-w-0">0px</div>
<div class="min-w-full">100%</div>
<div class="max-w-xs">20rem (320px)</div>
<div class="max-w-sm">24rem (384px)</div>
<div class="max-w-md">28rem (448px)</div>
<div class="max-w-lg">32rem (512px)</div>
<div class="max-w-xl">36rem (576px)</div>
<div class="max-w-2xl">42rem (672px)</div>
<div class="max-w-screen-xl">1280px</div>
```

#### 高度

```html
<!-- 固定高度 -->
<div class="h-0">0px</div>
<div class="h-4">16px</div>
<div class="h-8">32px</div>
<div class="h-16">64px</div>
<div class="h-32">128px</div>
<div class="h-64">256px</div>

<!-- 百分比高度 -->
<div class="h-1/2">50%</div>
<div class="h-1/3">33.333%</div>
<div class="h-full">100%</div>

<!-- 特殊高度 -->
<div class="h-screen">100vh</div>
<div class="h-svh">100svh</div>
<div class="h-lvh">100lvh</div>
<div class="h-dvh">100dvh</div>
<div class="h-min">min-content</div>
<div class="h-max">max-content</div>
<div class="h-fit">fit-content</div>

<!-- 自定义高度 -->
<div class="h-[200px]">200px</div>
<div class="h-[50vh]">50vh</div>

<!-- 最小/最大高度 -->
<div class="min-h-0">0px</div>
<div class="min-h-full">100%</div>
<div class="min-h-screen">100vh</div>
<div class="max-h-full">100%</div>
<div class="max-h-screen">100vh</div>
```

### 间距

#### 外边距（Margin）

```html
<!-- 全方向 -->
<div class="m-0">0px</div>
<div class="m-1">4px</div>
<div class="m-2">8px</div>
<div class="m-4">16px</div>
<div class="m-8">32px</div>
<div class="m-auto">auto</div>

<!-- 水平方向 -->
<div class="mx-4">左右 16px</div>
<div class="mx-auto">水平居中</div>

<!-- 垂直方向 -->
<div class="my-4">上下 16px</div>

<!-- 单方向 -->
<div class="mt-4">上 16px</div>
<div class="mr-4">右 16px</div>
<div class="mb-4">下 16px</div>
<div class="ml-4">左 16px</div>

<!-- 负边距 -->
<div class="-m-4">-16px</div>
<div class="-mt-4">上 -16px</div>
```

#### 内边距（Padding）

```html
<!-- 全方向 -->
<div class="p-0">0px</div>
<div class="p-1">4px</div>
<div class="p-2">8px</div>
<div class="p-4">16px</div>
<div class="p-8">32px</div>

<!-- 水平方向 -->
<div class="px-4">左右 16px</div>

<!-- 垂直方向 -->
<div class="py-4">上下 16px</div>

<!-- 单方向 -->
<div class="pt-4">上 16px</div>
<div class="pr-4">右 16px</div>
<div class="pb-4">下 16px</div>
<div class="pl-4">左 16px</div>
```

### 排版

#### 字体

```html
<!-- 字体大小 -->
<p class="text-xs">12px</p>
<p class="text-sm">14px</p>
<p class="text-base">16px</p>
<p class="text-lg">18px</p>
<p class="text-xl">20px</p>
<p class="text-2xl">24px</p>
<p class="text-3xl">30px</p>
<p class="text-4xl">36px</p>
<p class="text-5xl">48px</p>
<p class="text-6xl">60px</p>

<!-- 自定义字体大小 -->
<p class="text-[14px]">14px</p>
<p class="text-[2rem]">2rem</p>

<!-- 字重 -->
<p class="font-thin">100</p>
<p class="font-extralight">200</p>
<p class="font-light">300</p>
<p class="font-normal">400</p>
<p class="font-medium">500</p>
<p class="font-semibold">600</p>
<p class="font-bold">700</p>
<p class="font-extrabold">800</p>
<p class="font-black">900</p>

<!-- 字间距 -->
<p class="tracking-tighter">-0.05em</p>
<p class="tracking-tight">-0.025em</p>
<p class="tracking-normal">0em</p>
<p class="tracking-wide">0.025em</p>
<p class="tracking-wider">0.05em</p>
<p class="tracking-widest">0.1em</p>

<!-- 行高 -->
<p class="leading-3">12px</p>
<p class="leading-4">16px</p>
<p class="leading-6">24px</p>
<p class="leading-8">32px</p>
<p class="leading-none">1</p>
<p class="leading-tight">1.25</p>
<p class="leading-snug">1.375</p>
<p class="leading-normal">1.5</p>
<p class="leading-relaxed">1.625</p>
<p class="leading-loose">2</p>

<!-- 文本对齐 -->
<p class="text-left">左对齐</p>
<p class="text-center">居中</p>
<p class="text-right">右对齐</p>
<p class="text-justify">两端对齐</p>

<!-- 文本装饰 -->
<p class="underline">下划线</p>
<p class="line-through">删除线</p>
<p class="no-underline">无装饰</p>
<p class="overline">上划线</p>

<!-- 文本转换 -->
<p class="uppercase">大写</p>
<p class="lowercase">小写</p>
<p class="capitalize">首字母大写</p>
<p class="normal-case">正常</p>

<!-- 溢出处理 -->
<p class="truncate">单行截断...</p>
<p class="overflow-ellipsis">省略号</p>
<p class="overflow-clip">裁剪</p>
```

#### 颜色

```html
<!-- 文本颜色 -->
<p class="text-slate-500">石板色</p>
<p class="text-gray-500">灰色</p>
<p class="text-zinc-500">锌色</p>
<p class="text-neutral-500">中性色</p>
<p class="text-stone-500">石头色</p>
<p class="text-red-500">红色</p>
<p class="text-orange-500">橙色</p>
<p class="text-amber-500">琥珀色</p>
<p class="text-yellow-500">黄色</p>
<p class="text-lime-500">酸橙色</p>
<p class="text-green-500">绿色</p>
<p class="text-emerald-500">翡翠色</p>
<p class="text-teal-500">青色</p>
<p class="text-cyan-500">蓝绿色</p>
<p class="text-sky-500">天蓝色</p>
<p class="text-blue-500">蓝色</p>
<p class="text-indigo-500">靛蓝色</p>
<p class="text-violet-500">紫罗兰色</p>
<p class="text-purple-500">紫色</p>
<p class="text-fuchsia-500">紫红色</p>
<p class="text-pink-500">粉色</p>
<p class="text-rose-500">玫瑰色</p>

<!-- 自定义颜色 -->
<p class="text-[#ff0000]">自定义红色</p>
<p class="text-[rgb(255,0,0)]">RGB 红色</p>
<p class="text-[rgba(255,0,0,0.5)]">带透明度红色</p>

<!-- 背景颜色 -->
<div class="bg-blue-500">蓝色背景</div>
<div class="bg-gradient-to-r from-blue-500 to-purple-500">渐变背景</div>
```

### 边框

```html
<!-- 边框宽度 -->
<div class="border">1px</div>
<div class="border-0">0px</div>
<div class="border-2">2px</div>
<div class="border-4">4px</div>
<div class="border-8">8px</div>

<!-- 单边边框 -->
<div class="border-t-2">上边框</div>
<div class="border-r-2">右边框</div>
<div class="border-b-2">下边框</div>
<div class="border-l-2">左边框</div>

<!-- 边框颜色 -->
<div class="border-gray-200">灰色边框</div>
<div class="border-blue-500">蓝色边框</div>

<!-- 圆角 -->
<div class="rounded-none">0px</div>
<div class="rounded-sm">2px</div>
<div class="rounded">4px</div>
<div class="rounded-md">6px</div>
<div class="rounded-lg">8px</div>
<div class="rounded-xl">12px</div>
<div class="rounded-2xl">16px</div>
<div class="rounded-3xl">24px</div>
<div class="rounded-full">完全圆角</div>

<!-- 单边圆角 -->
<div class="rounded-t-lg">顶部圆角</div>
<div class="rounded-b-lg">底部圆角</div>
<div class="rounded-l-lg">左侧圆角</div>
<div class="rounded-r-lg">右侧圆角</div>
```

### 效果

#### 阴影

```html
<!-- 阴影 -->
<div class="shadow-sm">小阴影</div>
<div class="shadow">默认阴影</div>
<div class="shadow-md">中等阴影</div>
<div class="shadow-lg">大阴影</div>
<div class="shadow-xl">超大阴影</div>
<div class="shadow-2xl">巨大阴影</div>
<div class="shadow-inner">内阴影</div>
<div class="shadow-none">无阴影</div>

<!-- 阴影颜色 -->
<div class="shadow-blue-500/50">蓝色阴影</div>
```

#### 透明度

```html
<!-- 元素透明度 -->
<div class="opacity-0">完全透明</div>
<div class="opacity-25">25% 不透明</div>
<div class="opacity-50">50% 不透明</div>
<div class="opacity-75">75% 不透明</div>
<div class="opacity-100">完全不透明</div>

<!-- 背景透明度 -->
<div class="bg-blue-500/50">半透明蓝色背景</div>

<!-- 文本透明度 -->
<p class="text-blue-500/50">半透明蓝色文本</p>
```

### 变换

```html
<!-- 缩放 -->
<div class="scale-0">缩小到 0</div>
<div class="scale-50">缩小 50%</div>
<div class="scale-75">缩小 75%</div>
<div class="scale-90">缩小 90%</div>
<div class="scale-95">缩小 95%</div>
<div class="scale-100">原始大小</div>
<div class="scale-105">放大 5%</div>
<div class="scale-110">放大 10%</div>
<div class="scale-125">放大 25%</div>
<div class="scale-150">放大 50%</div>

<!-- 旋转 -->
<div class="rotate-0">0°</div>
<div class="rotate-1">1°</div>
<div class="rotate-2">2°</div>
<div class="rotate-3">3°</div>
<div class="rotate-6">6°</div>
<div class="rotate-12">12°</div>
<div class="rotate-45">45°</div>
<div class="rotate-90">90°</div>
<div class="rotate-180">180°</div>

<!-- 平移 -->
<div class="translate-x-0">X 轴不移动</div>
<div class="translate-x-1">X 轴移动 4px</div>
<div class="translate-x-4">X 轴移动 16px</div>
<div class="translate-x-full">X 轴移动 100%</div>
<div class="-translate-x-full">X 轴移动 -100%</div>
<div class="translate-y-4">Y 轴移动 16px</div>

<!-- 倾斜 -->
<div class="skew-x-0">0°</div>
<div class="skew-x-1">1°</div>
<div class="skew-x-2">2°</div>
<div class="skew-x-3">3°</div>
<div class="skew-x-6">6°</div>
<div class="skew-x-12">12°</div>

<!-- 变换原点 -->
<div class="origin-center">中心</div>
<div class="origin-top">顶部</div>
<div class="origin-top-right">右上</div>
<div class="origin-right">右侧</div>
<div class="origin-bottom-right">右下</div>
<div class="origin-bottom">底部</div>
<div class="origin-bottom-left">左下</div>
<div class="origin-left">左侧</div>
<div class="origin-top-left">左上</div>
```

### 过渡和动画

#### 过渡

```html
<!-- 过渡属性 -->
<button class="transition">默认过渡</button>
<button class="transition-all">所有属性过渡</button>
<button class="transition-colors">颜色过渡</button>
<button class="transition-opacity">透明度过渡</button>
<button class="transition-shadow">阴影过渡</button>
<button class="transition-transform">变换过渡</button>

<!-- 过渡时长 -->
<button class="duration-75">75ms</button>
<button class="duration-100">100ms</button>
<button class="duration-150">150ms</button>
<button class="duration-200">200ms</button>
<button class="duration-300">300ms</button>
<button class="duration-500">500ms</button>
<button class="duration-700">700ms</button>
<button class="duration-1000">1000ms</button>

<!-- 过渡函数 -->
<button class="ease-linear">线性</button>
<button class="ease-in">加速</button>
<button class="ease-out">减速</button>
<button class="ease-in-out">加速减速</button>

<!-- 延迟 -->
<button class="delay-75">75ms 延迟</button>
<button class="delay-100">100ms 延迟</button>
<button class="delay-150">150ms 延迟</button>
<button class="delay-200">200ms 延迟</button>
<button class="delay-300">300ms 延迟</button>
<button class="delay-500">500ms 延迟</button>
```

#### 动画

```html
<!-- 内置动画 -->
<div class="animate-spin">旋转</div>
<div class="animate-ping">脉冲扩散</div>
<div class="animate-pulse">脉冲</div>
<div class="animate-bounce">弹跳</div>

<!-- 自定义动画 -->
<!-- 在 tailwind.config.js 中配置 -->
```

### 定位

```html
<!-- 定位类型 -->
<div class="static">默认定位</div>
<div class="fixed">固定定位</div>
<div class="absolute">绝对定位</div>
<div class="relative">相对定位</div>
<div class="sticky">粘性定位</div>

<!-- 位置 -->
<div class="top-0">顶部 0</div>
<div class="right-0">右侧 0</div>
<div class="bottom-0">底部 0</div>
<div class="left-0">左侧 0</div>
<div class="inset-0">全方向 0</div>
<div class="inset-x-0">水平方向 0</div>
<div class="inset-y-0">垂直方向 0</div>

<!-- z-index -->
<div class="z-0">z-index: 0</div>
<div class="z-10">z-index: 10</div>
<div class="z-20">z-index: 20</div>
<div class="z-30">z-index: 30</div>
<div class="z-40">z-index: 40</div>
<div class="z-50">z-index: 50</div>
<div class="z-auto">z-index: auto</div>
```

### 显示和可见性

```html
<!-- 显示 -->
<div class="block">块级</div>
<div class="inline">行内</div>
<div class="inline-block">行内块级</div>
<div class="flex">flex</div>
<div class="inline-flex">行内 flex</div>
<div class="grid">grid</div>
<div class="inline-grid">行内 grid</div>
<div class="table">表格</div>
<div class="hidden">隐藏</div>

<!-- 可见性 -->
<div class="visible">可见</div>
<div class="invisible">不可见（占位）</div>

<!-- 溢出 -->
<div class="overflow-auto">自动</div>
<div class="overflow-hidden">隐藏</div>
<div class="overflow-clip">裁剪</div>
<div class="overflow-visible">可见</div>
<div class="overflow-scroll">滚动</div>
<div class="overflow-x-auto">水平自动</div>
<div class="overflow-y-auto">垂直自动</div>
```

## 自定义配置

### 扩展主题

```javascript [tailwind.config.js]
/** @type {import('tailwindcss').Config} */
export default {
  theme: {
    extend: {
      // 扩展颜色
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
      // 扩展字体
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
      // 扩展间距
      spacing: {
        '18': '72px',
        '88': '352px',
      },
      // 扩展断点
      screens: {
        '3xl': '1920px',
      },
      // 扩展圆角
      borderRadius: {
        '4xl': '2rem',
      },
    },
  },
}
```

### 添加自定义工具类

```javascript [tailwind.config.js]
/** @type {import('tailwindcss').Config} */
export default {
  plugins: [
    function ({ addUtilities }) {
      const newUtilities = {
        '.scrollbar-thin': {
          scrollbarWidth: 'thin',
          '&::-webkit-scrollbar': {
            width: '4px',
          },
        },
        '.text-shadow': {
          textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)',
        },
      }
      addUtilities(newUtilities)
    },
  ],
}
```

### 添加自定义组件

```javascript [tailwind.config.js]
/** @type {import('tailwindcss').Config} */
export default {
  plugins: [
    function ({ addComponents }) {
      const newComponents = {
        '.btn': {
          padding: '0.5rem 1rem',
          borderRadius: '0.375rem',
          fontWeight: '600',
          '&:hover': {
            opacity: '0.9',
          },
        },
        '.btn-primary': {
          backgroundColor: '#3b82f6',
          color: '#fff',
        },
        '.card': {
          borderRadius: '0.5rem',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          padding: '1.5rem',
        },
      }
      addComponents(newComponents)
    },
  ],
}
```

## @layer 指令

Tailwind 提供了 `@layer` 指令来组织自定义样式。

```css [style.css]
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  h1 {
    @apply text-2xl font-bold;
  }
  h2 {
    @apply text-xl font-bold;
  }
  body {
    @apply bg-gray-50 text-gray-900;
  }
}

@layer components {
  .btn {
    @apply px-4 py-2 rounded font-semibold transition-colors;
  }
  .btn-primary {
    @apply bg-blue-500 text-white hover:bg-blue-600;
  }
  .btn-secondary {
    @apply bg-gray-200 text-gray-800 hover:bg-gray-300;
  }
  .card {
    @apply bg-white rounded-lg shadow p-6;
  }
}

@layer utilities {
  .text-shadow {
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  }
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
    &::-webkit-scrollbar {
      display: none;
    }
  }
}
```

## @apply 指令

使用 `@apply` 可以在 CSS 中组合工具类。

```css [style.css]
.btn {
  @apply px-4 py-2 rounded font-semibold transition-colors duration-200;
}

.btn-primary {
  @apply bg-blue-500 text-white hover:bg-blue-600 active:bg-blue-700;
}

.card {
  @apply bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow;
}

.input {
  @apply px-3 py-2 border border-gray-300 rounded-md focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-colors;
}
```

## theme() 函数

使用 `theme()` 函数在 CSS 中访问主题配置。

```css [style.css]
.card {
  background-color: theme('colors.blue.500');
  border-radius: theme('borderRadius.lg');
  box-shadow: 0 1px 3px theme('colors.black / 0.1');
}

.title {
  font-size: theme('fontSize.2xl');
  font-weight: theme('fontWeight.bold');
  color: theme('colors.gray.900');
}
```

## 实际项目示例

### 卡片组件

```html
<div class="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden md:max-w-2xl hover:shadow-lg transition-shadow duration-300">
  <div class="md:flex">
    <div class="md:shrink-0">
      <img class="h-48 w-full object-cover md:h-full md:w-48" src="/img/card.jpg" alt="卡片图片">
    </div>
    <div class="p-8">
      <div class="uppercase tracking-wide text-sm text-indigo-500 font-semibold">标签</div>
      <a href="#" class="block mt-1 text-lg leading-tight font-medium text-black hover:underline">卡片标题</a>
      <p class="mt-2 text-slate-500">这是一段卡片描述文字，可以包含一些简短的内容介绍。</p>
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
          <span class="text-xl font-bold text-blue-600">Logo</span>
        </div>
        <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
          <a href="#" class="border-blue-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">首页</a>
          <a href="#" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">产品</a>
          <a href="#" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">关于</a>
        </div>
      </div>
      <div class="flex items-center">
        <button class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
          登录
        </button>
      </div>
    </div>
  </div>
</nav>
```

### 响应式表单

```html
<form class="max-w-lg mx-auto p-6 bg-white rounded-lg shadow">
  <div class="space-y-6">
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">姓名</label>
      <input type="text" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-colors" placeholder="请输入姓名">
    </div>
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
      <input type="email" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-colors" placeholder="请输入邮箱">
    </div>
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">消息</label>
      <textarea rows="4" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-colors" placeholder="请输入消息"></textarea>
    </div>
    <div>
      <button type="submit" class="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-md font-medium transition-colors">
        提交
      </button>
    </div>
  </div>
</form>
```

### 网格布局

```html
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 p-6">
  <div class="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
    <div class="text-3xl font-bold text-blue-500">1,234</div>
    <div class="text-sm text-gray-500 mt-1">总用户数</div>
  </div>
  <div class="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
    <div class="text-3xl font-bold text-green-500">567</div>
    <div class="text-sm text-gray-500 mt-1">活跃用户</div>
  </div>
  <div class="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
    <div class="text-3xl font-bold text-yellow-500">89</div>
    <div class="text-sm text-gray-500 mt-1">待处理</div>
  </div>
  <div class="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
    <div class="text-3xl font-bold text-red-500">12</div>
    <div class="text-sm text-gray-500 mt-1">错误数</div>
  </div>
</div>
```

::: tip 提示
- Tailwind CSS v4 使用 `@import "tailwindcss"` 代替 v3 的 `@tailwind` 指令
- 推荐使用 JIT（即时编译）模式，按需生成样式
- 使用 `@apply` 组合常用样式为组件类
- 使用 `theme()` 函数访问主题配置
- 配置文件中 `extend` 用于扩展默认主题，直接设置会覆盖默认值
:::

::: danger 注意事项
- 避免在 HTML 中使用过多工具类导致代码冗长，可使用 `@apply` 提取组件类
- 自定义颜色时注意使用 Tailwind 的颜色格式（支持 `/` 分隔透明度）
- 响应式设计使用移动优先策略，先写移动端样式再添加断点
- 不要混用 Tailwind v3 和 v4 的配置方式
- 生产环境务必启用 PurgeCSS（Tailwind 内置）来移除未使用的样式
:::
