# UnoCSS

官网：https://unocss.dev/

中文网：http://www.unocss.cn

## 安装UnoCSS

安装UnoCSS：

- unocss：UnoCSS核心库
- @unocss/preset-rem-to-px：UnoCSS自带的rem转为px
- @unocss/transformer-directives：使用`@apply` `@screen` theme函数
- @unocss/eslint-config：eslint 格式化UnoCSS

```shell
npm install -D unocss @unocss/preset-rem-to-px @unocss/transformer-directives @unocss/eslint-config
```

## 引入UnoCSS

> vite.config.ts

```typescript
//unocss vite插件
import UnoCSS from 'unocss/vite'

// https://vite.dev/config/
export default defineConfig({
  // ...
  plugins: [
    // ...
    UnoCSS(),
  ],
})
```

## 配置UnoCSS

> uno.config.ts

```typescript
// uno.config.ts
import fs from 'node:fs'
import path from 'node:path'
// 预设rem转px
import presetRemToPx from '@unocss/preset-rem-to-px'
// transformerDirectives 可以使用 @apply @screen theme函数
import transformerDirective from '@unocss/transformer-directives'
import {
  defineConfig,
  presetAttributify,
  presetIcons,
  presetUno,
  transformerVariantGroup,
} from 'unocss'

// import { FileSystemIconLoader } from '@iconify/utils/lib/loader/node-loaders'
// loader helpers -- pnpm i @iconify/utils -D 官网的不晓得为啥 jenkins 打包总会出点问题
// TODO: 上面失效用下面替代 pnpm i unplugin-icons -D
import { FileSystemIconLoader } from 'unplugin-icons/loaders'

// SVG图标基础目录
const SVG_BASE_DIR = './src/assets/svg'

export default defineConfig({
  presets: [
    presetAttributify(),
    // {
    // 忽略的属性
    // ignoreAttributes: ['container', 'table'],
    // }
    presetUno(),
    // 现在mt-1会转换为 margin-top: 1px
    presetRemToPx({
      baseFontSize: 4,
    }),
    // 自动引入图标配置
    presetIcons({
      scale: 1.2,
      // warn: true,
      // 全局自定义图标转换
      customizations: {
        transform(svg, collection) {
          // 如果是menu图标，则添加fill="currentColor"
          if (collection === 'menu') {
            return svg.replace(/^<svg /, '<svg fill="currentColor" ')
          }
          return svg
        },
      },
      collections: {
        // 本地SVG图标集合 自动读取SVG_BASE_DIR下面文件夹里面的图标 使用方式为 i-文件夹名称-图标名称
        ...loadLocalSvgCollections(),
        // 按需加载的图标集合 非必须
        // 'ant-design': () => import('@iconify-json/ant-design/icons.json').then(i => i.default),
        ep: () => import('@iconify-json/ep/icons.json').then((i) => i.default),
      },
    }),
  ],
  // 安全列表 动态图标需要 例如：<div i-menu-home /> 菜单图标是后端返回的需要动态处理
  safelist: generateSafeList(['menu']), // 传入数组参数
  transformers: [transformerDirective(), transformerVariantGroup()],
  // 自定义配置
  rules: [
    // 自定义配置
    // 以下官网规则可自定义转换
    // [/^m-(\d+)$/, ([, d]) => ({ margin: `${d / 4}rem` })],
    // [/^p-(\d+)$/, match => ({ padding: `${match[1] / 4}rem` })],
    /** 以下官网规则可自定义转换 */
    /* 例如 m-1 转换为 margin:0.25rem */
    // [/^m-(\d+)$/, ([, d]) => ({margin: `${d / 4}rem`})],
    // [/^p-(\d+)$/, match => ({padding: `${match[1] / 4}rem`})],
    [
      /^bg-img-\[(.+)\]$/,
      ([, value]) => {
        // 替换下划线为正常的路径分隔符
        const path = value.replace(/_/g, '/')
        return {
          'background-image': `url(${path})`,
          'background-repeat': 'no-repeat',
          'background-size': '100% 100%',
        }
      },
    ],
  ],
  // 自定义属性 一个属性可以对应多个unocss类值
  shortcuts: [
    // 动态快捷方式
    /**
     *   t+字号+透明度+加粗
     *   t14 就变成 text-14 color=rgba(37,51,71,1)
     *   t145 就变成 text-14 color=rgba(37,51,71,0.55)
     *   t14b5 就变成 text-14 color=rgba(37,51,71,1) font-weight: 500
     *   t145b5 就变成 text-14 color=rgba(37,51,71,0.55) font-weight: 500
     */
    [
      /^t(\d{2})(\d)?(b\d+)?$/,
      ([, size, opacity, weight]) => {
        const fontSize = `text-${size}`
        const fontWeight = weight ? `font-${weight.slice(1)}00` : ''
        const opacityValue = opacity ? (Number(opacity) * 0.1 + 0.05).toFixed(2) : '1'
        const color = `text-[rgba(37,51,71,${opacityValue})]`
        return `${fontSize} ${fontWeight} ${color}`
      },
    ],
    {
      // 垂直水平居中
      'flex-center': 'flex justify-center items-center',
      // 放在最后
      'flex-col-end': 'flex justify-end items-center',
      // 垂直居中
      'flex-middle': 'flex items-center',
      // 分开两边
      'flex-between': 'flex justify-between items-center',
      // 竖直居中
      'flex-col-center': 'flex flex-col justify-center',
      // 字体基线对其
      'flex-baseline': 'flex items-baseline',
    },
  ],
  theme: {
    breakpoints: {
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
    },
  },
})
// 本地 SVG 图标存放目录 用于动态渲染图标 例如：菜单按钮
function generateSafeList(collections: string[]) {
  const safeList: string[] = []
  collections.forEach((collection) => {
    try {
      const dirPath = path.resolve(SVG_BASE_DIR, collection)
      if (fs.existsSync(dirPath) && fs.statSync(dirPath).isDirectory()) {
        const files = fs.readdirSync(dirPath)
        const icons = files
          .filter((file) => file.endsWith('.svg'))
          .map((file) => `i-${collection}-${path.basename(file, '.svg')}`)
        safeList.push(...icons)
      }
    } catch (error) {
      console.error(`无法读取图标集合 ${collection}:`, error)
    }
  })

  return safeList
}

// 加载本地SVG图标集合
function loadLocalSvgCollections() {
  const result: Record<string, ReturnType<typeof FileSystemIconLoader>> = {}

  try {
    // 读取SVG_BASE_DIR目录下的所有内容
    const items = fs.readdirSync(SVG_BASE_DIR)

    // 筛选出文件夹
    const collections = items.filter((item) => {
      const itemPath = path.join(SVG_BASE_DIR, item)
      return fs.existsSync(itemPath) && fs.statSync(itemPath).isDirectory()
    })

    // 为每个文件夹创建FileSystemIconLoader
    collections.forEach((collection) => {
      result[collection] = FileSystemIconLoader(path.join(SVG_BASE_DIR, collection))
    })
  } catch (error) {
    console.error(`无法读取SVG图标目录 ${SVG_BASE_DIR}:`, error)
  }
  return result
}
```

全局配置：

> main.ts

```typescript
//eslint-disable-next-line import/no-unresolved
import 'virtual:uno.css' // 引入 uno.css
```

使用：

> 使用图标时：`i前缀-ep图库名:lock图标名称`

```vue
<template>
  <div>
    <h1>UnoCSS</h1>
    <div class="box"></div>
    <hr />
    <div class="h-100 w-100 bg-red-800 text-30 text-blue hover:text-black">小猫米</div>
    <hr />
    <div class="box2">小猫咪</div>
    <hr />
    <div h100 w100 bg-blueGray text-fuchsia mt10 py20>小猫咪</div>
    <hr />
    <div class="wrap" w200 h100 flex-center gap10>
      <div w20 h20 bg-blue></div>
      <div w20 h20 bg-blue></div>
      <div w20 h20 bg-blue></div>
    </div>
    <hr />
    <div i-ep:dish></div>
    <i w100 h100 block i-ep:switch-button></i>
  </div>
</template>

<script setup></script>

<style lang="scss" scoped>
.box {
  width: 100px;
  height: 100px;
  background-color: salmon;
}
.box2 {
  @apply h-100 w-100 bg-red-800 text-30 text-blue hover:text-black;
}
.wrap {
  border: 1px solid #ddd;
}
</style>
```

## 常用属性

### 宽度

- `w-10`：宽度为 10px
- `w-[200px]`：自定义宽度为 200px
- `w-full`：宽度为 100%
- `w-screen`：宽度为视窗宽度
- `min-w-10`：最小宽度为 10px
- `max-w-100`：最大宽度为 100px

### 高度

- `h-10`：高度为 10px
- `h-[200px]`：自定义高度为 200px
- `h-full`：高度为 100%
- `h-screen`：高度为视窗高度
- `min-h-10`：最小高度为 10px
- `max-h-100`：最大高度为 100px

### 间距

- `m-4`：外边距为 4px
- `mx-4`：水平外边距为 4px
- `mx-a`：水平外边距为 auto
- `my-4`：垂直外边距为 4px
- `my-a`：垂直外边距为 auto
- `mt-4`：上外边距为 4px
- `mt-a`：上外边距为 auto
- `mr-4`：右外边距为 4px
- `mb-4`：下外边距为 4px
- `ml-4`：左外边距为 4px
- `p-4`：内边距为 4px
- `px-4`：水平内边距为 4px
- `py-4`：垂直内边距为 4px
- `pt-4`：上内边距为 4px
- `pr-4`：右内边距为 4px
- `pb-4`：下内边距为 4px
- `pl-4`：左内边距为 4px

### 颜色和背景

- `text-red`：文本颜色为红色
- `text-[#ff0000]`：自定义文本颜色
- `bg-blue-500`：背景颜色为蓝色
- `bg-[#0000ff]`：自定义背景颜色

### 边框

- `border`：添加边框
- `border-2`：2px 宽度的边框
- `border-red`：红色边框
- `rounded-md`：中等圆角
- `rounded-full`：完全圆形的圆角
- `b-rd-2`：2px圆角
- `border="10 solid bule"`：蓝色边框
- `border="10 solid [rgba(0,0,0,.5)]"`：使用rgba设置颜色

## flex

### 基础布局

- `flex`：启用 flex 布局
- `flex="~"`：启用 flex 布局
- `inline-flex`：启用行内 flex 布局
- `flex-row`：水平方向布局（默认）
- `flex-col`：垂直方向布局
- `flex-row-reverse`：反向水平布局
- `flex-col-reverse`：反向垂直布局

### 换行

- `flex-wrap`：允许换行
- `flex-nowrap`：不换行（默认）
- `flex-wrap-reverse`：反向换行

### 主轴对齐

- `justify-start`：主轴起点对齐
- `justify-end`：主轴终点对齐
- `justify-center`：主轴居中对齐
- `justify-between`：主轴两端对齐，中间等间距
- `justify-around`：主轴均匀分布
- `justify-evenly`：主轴等距分布

### 交叉轴对齐

- `items-start`：交叉轴起点对齐
- `items-end`：交叉轴终点对齐
- `items-center`：交叉轴居中对齐
- `items-baseline`：交叉轴基线对齐
- `items-stretch`：交叉轴拉伸对齐

### 项目属性

- `flex-1`：flex: 1
- `flex-auto`：flex: auto
- `flex-none`：flex: none
- `flex-initial`：flex: initial

### 实用组合（从项目配置中）

- `flex-center`：垂直水平居中 (`flex items-center justify-center`)
- `flex-end`：放在最后 (`flex items-center justify-end`)
- `flex-middle`：垂直居中 (`flex items-center`)
- `flex-between`：分开两边 (`flex items-center justify-between`)
- `flex-col-center`：垂直 (`flex flex-col items-center`)
- `flex-baseline`：字体基线对齐 (`flex items-baseline`)

## gird

### 基础布局

- `grid`：启用 grid 布局
- `inline-grid`：启用行内 grid 布局

### 网格模板

- `grid-cols-3`：创建 3 列网格
- `grid-cols-[100px_1fr_2fr]`：自定义列宽
- `grid="~ cols-[100px_1fr_2fr]"`：自定义列宽
- `grid-rows-3`：创建 3 行网格
- `grid-rows-[100px_1fr_2fr]`：自定义行高
- `grid="~ cols-[100px_1fr_2fr] 768px:cols-[100px_1fr_1fr]"`：自定义列宽

### 间距

- `gap-4`：行列间距为 4px
- `gap-x-4`：列间距为 4px
- `gap-y-4`：行间距为 4px

### 项目位置和跨度

- `col-span-2`：跨越 2 列
- `row-span-2`：跨越 2 行
- `col-start-2`：从第 2 列开始
- `col-end-5`：在第 5 列结束
- `row-start-2`：从第 2 行开始
- `row-end-5`：在第 5 行结束

### 对齐

- `justify-items-start`：水平起点对齐
- `justify-items-end`：水平终点对齐
- `justify-items-center`：水平居中对齐
- `justify-items-stretch`：水平拉伸对齐
- `content-start`：垂直起点对齐
- `content-end`：垂直终点对齐
- `content-center`：垂直居中对齐
- `content-between`：垂直两端对齐
- `content-around`：垂直均匀分布

## 图标

官网：http://www.unocss.cn/presets/icons.html

引入图标库：

```shell
pnpm add -D @unocss/preset-icons @iconify-json/[the-collection-you-want]
```

- [the-collection-you-want]：在 https://icon-sets.iconify.design/ 搜索

- ep代表element plus

- @iconfiy-json/ep：Element Plus的图标库

  ```shell
  pnpm install -D @iconify-json/ep
  ```

- @iconfiy-json/ant-design：ant-degsin的图标库

  ```shell
  pnpm install -D @iconify-json/ant-design
  ```

使用：

```
<!-- 网络图标 -->
<div i-库-图标名></div>

<div i-库:图标名></div>

<div class="i-ant-design:linux-outlined"></div>

<div class="i-ant-design-linux-outlined"></div>

<!-- 本地图标 -->
<div i-本地文件夹-图标名></div>

<div class="i-momo-a"></div>
```
