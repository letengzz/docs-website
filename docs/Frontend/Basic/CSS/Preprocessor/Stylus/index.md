# Stylus

Stylus 是一个富有表现力的 CSS 预处理器，语法灵活，支持多种写法。它由 Node.js 编写，可以方便地与 Node.js 项目集成。

- 官方文档：https://stylus-lang.com/
- GitHub：https://github.com/stylus/stylus

## 安装

```bash
# npm 安装
npm install -g stylus

# 项目本地安装
npm install --save-dev stylus

# 编译命令
stylus input.styl -o output.css

# 监听模式
stylus input.styl -o output.css -w

# 压缩输出
stylus input.styl -o output.css -c

# 输出压缩格式
stylus input.styl -o output.css --compress
```

## 语法特点

Stylus 支持多种语法格式：

```stylus [styles.styl]
// 完整语法（带大括号和分号）
body {
  color: #333;
  font-size: 14px;
}

// 缩进语法（无大括号和分号）
body
  color #333
  font-size 14px

// 混合语法（无冒号）
body
  color: #333
  font-size: 14px

// 甚至可以省略选择器的大括号
body
  color #333
  a
    color blue
    &:hover
      color red
```

::: tip 提示
- Stylus 语法非常灵活，可以根据个人喜好选择
- 推荐使用缩进语法，更简洁
- 本文档以缩进语法为主
:::

## 变量

Stylus 变量定义非常灵活，可以使用 `=` 或直接赋值。

```stylus [variables.styl]
// 定义变量
primary-color = #1890ff
font-size-base = 14px
border-radius = 4px
spacing = 16px

// 使用变量
.button
  background-color primary-color
  font-size font-size-base
  border-radius border-radius
  padding spacing

// 使用 $ 符号（可选）
$primary = #1890ff

.element
  color $primary

// 变量可以引用其他变量
base-color = #1890ff
light-color = lighten(base-color, 20%)

.header
  background-color light-color

// 属性引用
.logo
  margin-left @margin-left // 引用自身的 margin-left
  margin-left 10px
```

## 嵌套

### 选择器嵌套

```stylus [nesting.styl]
.nav
  background #fff
  padding 10px

  .item
    display inline-block
    margin-right 10px

    &:hover
      color #1890ff

    &.active
      font-weight bold

    a
      text-decoration none
      color inherit

// 父选择器引用
.button
  background #1890ff

  &:hover
    background darken(#1890ff, 10%)

  &-primary
    background #1890ff

  &-success
    background #52c41a
```

### 属性嵌套

```stylus [property-nesting.styl]
.logo
  border
    style solid
    width 1px
    color #ccc
    radius 4px

// 编译后
.logo
  border-style solid
  border-width 1px
  border-color #ccc
  border-radius 4px
```

### 媒体查询嵌套

```stylus [media-nesting.styl]
.container
  width 100%
  padding 16px

  @media (min-width 768px)
    width 750px
    padding 24px

  @media (min-width 992px)
    width 970px

  @media (min-width 1200px)
    width 1170px
```

## 混合（Mixins）

```stylus [mixins.styl]
// 基本混合
border-radius()
  -webkit-border-radius arguments
  -moz-border-radius arguments
  border-radius arguments

.button
  border-radius(4px)

// 带参数的混合
box-shadow(x = 0, y = 0, blur = 4px, color = rgba(0, 0, 0, 0.2))
  box-shadow x y blur color

.modal
  box-shadow()
  box-shadow(2px, 2px, 10px, rgba(0, 0, 0, 0.3))

// 使用 arguments 获取所有参数
transition()
  -webkit-transition arguments
  -moz-transition arguments
  transition arguments

.link
  transition(color 0.2s linear)

// 可变参数
box-shadows()
  box-shadow arguments

.element
  box-shadows(0 0 5px rgba(0,0,0,0.2), inset 0 0 10px rgba(0,0,0,0.1))

// 内容块
media-mobile()
  @media (max-width 768px)
    {block}

.container
  width 100%
  +media-mobile()
    width 100%
    padding 16px
```

## 函数

### 内置函数

```stylus [functions.styl]
// 颜色函数
base = #1890ff

.element
  background-color lighten(base, 20%)
  color darken(base, 20%)
  border-color saturate(base, 10%)
  outline-color desaturate(base, 10%)
  box-shadow 0 0 5px alpha(base, 0.5)

// 数值函数
.size
  width round(10.5px) // 11px
  height ceil(10.2px) // 11px
  min-height floor(10.8px) // 10px
  margin unit(0.5, '%') // 50%

// 字符串函数
.text::before
  content 'Hello' + ' Stylus'

// 类型检查
.element
  if typeof(base) == 'color'
    color base
```

### 自定义函数

```stylus [custom-functions.styl]
// px 转 rem
px-to-rem(px, base = 16px)
  unit(px / base, 'rem')

.element
  font-size px-to-rem(14px) // 0.875rem
  padding px-to-rem(16px) // 1rem

// 计算百分比
percentage(value, total)
  (value / total) * 100%

.col-6
  width percentage(6, 24) // 25%

// 返回多个值
spacing(value)
  value value * 2 value * 4

.element
  margin spacing(8px) // 8px 16px 32px

// 条件函数
theme-color(type)
  if type == 'primary'
    #1890ff
  else if type == 'success'
    #52c41a
  else if type == 'warning'
    #faad14
  else
    #d9d9d9

.button
  background-color theme-color('primary')
```

## 运算

```stylus [operations.styl]
// 数学运算
base-width = 100px
spacing = 10px

.container
  width base-width * 2
  padding spacing + 5px
  margin spacing / 2

// 颜色运算
base-color = #1890ff

.element
  background-color base-color + #111
  color base-color - #222

// 单位转换
font-size = 14px

.text
  font-size font-size * 1.5 // 21px
  line-height (font-size * 1.5) + 4px // 25px

// 字符串连接
icon-url(name)
  '../icons/' + name + '.png'

.logo
  background-image url(icon-url('logo'))
```

## 继承

```stylus [extend.styl]
// 使用 @extend
.message
  padding 16px
  border-radius 4px
  font-size 14px

.message-success
  @extend .message
  background-color #52c41a
  color #fff

.message-error
  @extend .message
  background-color #f5222d
  color #fff

// 编译后
.message, .message-success, .message-error
  padding 16px
  border-radius 4px
  font-size 14px

.message-success
  background-color #52c41a
  color #fff

.message-error
  background-color #f5222d
  color #fff

// 占位符选择器
%button
  padding 10px 20px
  border none
  cursor pointer

.btn-primary
  @extend %button
  background-color #1890ff
  color #fff
```

## 插值

```stylus [interpolation.styl]
// 在选择器中使用
className = 'button'

.{className}
  background-color #1890ff

// 在属性名中使用
property = 'margin'

.element
  {property}-top 10px
  {property}-bottom 10px

// 在 URL 中使用
assets-path = '/assets'

.logo
  background-image url('%s/logo.png' % assets-path)

// 字符串格式化
direction = 'left'

.element
  border-%s-width % direction 2px
```

## 条件表达式

```stylus [conditionals.styl]
// if/else
theme(type)
  if type == 'primary'
    background-color #1890ff
    color #fff
  else if type == 'success'
    background-color #52c41a
    color #fff
  else if type == 'warning'
    background-color #faad14
    color #333
  else
    background-color #d9d9d9
    color #333

.button
  theme('primary')

// 三元表达式
type = 'primary'

.element
  color type == 'primary' ? #1890ff : #333

// unless（相当于 if not）
debug = false

.element
  unless debug
    display none
```

## 循环

### each 循环

```stylus [each.styl]
// 遍历列表
sizes = 4px, 8px, 12px, 16px

for size in sizes
  .icon-{size}
    font-size size

// 遍历映射
colors = {
  primary: #1890ff,
  success: #52c41a,
  warning: #faad14,
  error: #f5222d
}

for name, color in colors
  .text-{name}
    color color

  .bg-{name}
    background-color color

// 带索引
items = 'a', 'b', 'c'

for item, i in items
  .item-{i}
    content item
```

### for 循环

```stylus [for.styl]
// 范围循环
for i in 1..3
  .col-{i}
    width (100% / i)

// 不包含结束值
for i in 1..4
  .item-{i}
    margin-left 10px * i

// 生成栅格系统
for i in 1..24
  .col-{i}
    width (i / 24) * 100%

// 循环生成间距类
for i in 1..10
  .m-{i}
    margin i * 4px

  .p-{i}
    padding i * 4px
```

### while 循环

```stylus [while.styl]
i = 6

while i > 0
  .item-{i}
    width 20px * i
  i = i - 2
```

## 导入

```stylus [import.styl]
// 导入其他 stylus 文件
@import 'variables'
@import 'mixins'
@import 'reset'

// 导入 CSS 文件（不会被处理）
@import 'library.css'

// 条件导入
@import 'ie' if ie

// 多次导入只处理一次
@import 'variables'
```

## 内置函数

```stylus [built-in-functions.styl]
// 颜色函数
base = #1890ff

.element
  // 调整颜色
  background-color lighten(base, 20%)
  color darken(base, 20%)
  border-color saturate(base, 10%)
  outline-color desaturate(base, 10%)

  // 透明度
  box-shadow 0 0 5px alpha(base, 0.5)
  background-color rgba(base, 0.8)

  // 颜色信息
  hue(base) // 色相
  saturation(base) // 饱和度
  lightness(base) // 亮度

// 数值函数
.size
  width round(10.5px) // 11px
  height ceil(10.2px) // 11px
  min-height floor(10.8px) // 10px
  margin abs(-10px) // 10px

// 字符串函数
.text
  content unquote("'Hello'")
  content s('Hello %s', 'World') // 'Hello World'

// 列表函数
list = 10px, 20px, 30px

.element
  length(list) // 3
  first(list) // 10px
  last(list) // 30px
  push(list, 40px) // 10px, 20px, 30px, 40px
  pop(list) // 30px

// 类型检查
.value
  if typeof(base) == 'color'
    color base
  if typeof(10px) == 'unit'
    width 10px
```

## 实际项目示例

```stylus [example.styl]
// 变量定义
primary-color = #1890ff
text-color = #333
border-color = #d9d9d9
border-radius = 4px
spacing-unit = 8px

theme-colors = {
  primary: primary-color,
  success: #52c41a,
  warning: #faad14,
  error: #f5222d
}

// 混合定义
flex-center()
  display flex
  align-items center
  justify-content center

clearfix()
  &::after
    content ''
    display table
    clear both

text-ellipsis()
  overflow hidden
  text-overflow ellipsis
  white-space nowrap

// 组件样式
.card
  background #fff
  border-radius border-radius
  box-shadow 0 2px 8px rgba(0, 0, 0, 0.1)
  padding spacing-unit * 2

  &-header
    flex-center()
    justify-content space-between
    border-bottom 1px solid border-color
    padding-bottom spacing-unit
    margin-bottom spacing-unit

  &-body
    color text-color
    line-height 1.6

  &-footer
    clearfix()
    border-top 1px solid border-color
    padding-top spacing-unit
    margin-top spacing-unit

// 栅格系统
.row
  clearfix()
  margin 0 -spacing-unit

for i in 1..24
  .col-{i}
    float left
    width (i / 24) * 100%
    padding 0 spacing-unit
    box-sizing border-box

// 主题颜色类
for name, color in theme-colors
  .bg-{name}
    background-color color

  .text-{name}
    color color

  .border-{name}
    border-color color

// 响应式混合
respond-to(breakpoint)
  if breakpoint == 'sm'
    @media (min-width 576px)
      {block}
  else if breakpoint == 'md'
    @media (min-width 768px)
      {block}
  else if breakpoint == 'lg'
    @media (min-width 992px)
      {block}
  else if breakpoint == 'xl'
    @media (min-width 1200px)
      {block}

.container
  width 100%

  +respond-to('sm')
    max-width 540px

  +respond-to('md')
    max-width 720px

  +respond-to('lg')
    max-width 960px

  +respond-to('xl')
    max-width 1140px
```

::: tip 提示
- Stylus 语法非常灵活，支持多种写法
- 变量定义可以省略 `var` 或 `$`
- 使用 `arguments` 获取混合的所有参数
- 使用 `{block}` 在混合中传递内容块
- 支持字符串格式化 `%s`
:::

::: danger 注意事项
- Stylus 社区活跃度相对较低
- 语法过于灵活可能导致团队代码风格不统一
- 部分 IDE 对 Stylus 语法支持不如 Sass/Less 完善
- 建议使用 `.styl` 扩展名
- 缩进语法中注意保持一致的缩进（推荐 2 空格）
:::
