# Sass

Sass（Syntactically Awesome Stylesheets）是世界上最成熟、最稳定、最强大的专业级 CSS 扩展语言。

- 官方文档：https://sass-lang.com/documentation/
- GitHub：https://github.com/sass/sass

## 两种语法

### SCSS（Sassy CSS）

使用 `.scss` 扩展名，完全兼容 CSS 语法，使用 `{}` 和 `;`。

```scss [styles.scss]
$primary-color: #1890ff;

.button {
  background-color: $primary-color;
  padding: 10px 20px;
}
```

### 缩进语法（Sass）

使用 `.sass` 扩展名，使用缩进代替 `{}`，换行代替 `;`。

```sass [styles.sass]
$primary-color: #1890ff

.button
  background-color: $primary-color
  padding: 10px 20px
```

::: tip 提示
- 推荐使用 SCSS 语法，与 CSS 完全兼容
- 本文档以 SCSS 语法为主
:::

## 安装

```bash
# npm 安装
npm install -g sass

# 项目本地安装
npm install --save-dev sass

# Dart Sass（推荐）
npm install sass

# 编译命令
sass input.scss output.css

# 监听模式
sass --watch input.scss:output.css

# 压缩输出
sass --style=compressed input.scss output.css

# 源码映射
sass --source-map input.scss output.css
```

## 变量

Sass 使用 `$` 符号定义变量。

```scss [variables.scss]
// 定义变量
$primary-color: #1890ff;
$font-size-base: 14px;
$border-radius: 4px;
$spacing: 16px;
$font-stack: 'Helvetica Neue', Arial, sans-serif;

// 使用变量
.button {
  background-color: $primary-color;
  font-size: $font-size-base;
  border-radius: $border-radius;
  padding: $spacing;
  font-family: $font-stack;
}

// 带 !default 的变量（默认值）
$theme-color: #1890ff !default;
$theme-color: #52c41a; // 不会覆盖上面的值

// 使用 !global 在局部作用域定义全局变量
.module {
  $width: 100px !global;
  width: $width;
}

.sidebar {
  width: $width; // 可以访问
}

// 使用变量命名
$primary: #1890ff;
$var: 'primary';

.element {
  color: var(--#{$var}); // CSS 自定义属性
}
```

## 嵌套

### 选择器嵌套

```scss [nesting.scss]
.nav {
  background: #fff;
  padding: 10px;

  .item {
    display: inline-block;
    margin-right: 10px;

    &:hover {
      color: #1890ff;
    }

    &.active {
      font-weight: bold;
    }

    a {
      text-decoration: none;
      color: inherit;
    }
  }
}
```

### 属性嵌套

```scss [property-nesting.scss]
.logo {
  border: {
    style: solid;
    width: 1px;
    color: #ccc;
    radius: 4px;
  }
}

// 编译后
.logo {
  border-style: solid;
  border-width: 1px;
  border-color: #ccc;
  border-radius: 4px;
}
```

### 媒体查询嵌套

```scss [media-nesting.scss]
.container {
  width: 100%;
  padding: 16px;

  @media (min-width: 768px) {
    width: 750px;
    padding: 24px;
  }

  @media (min-width: 992px) {
    width: 970px;
  }

  @media (min-width: 1200px) {
    width: 1170px;
  }
}
```

## 局部文件

以 `_` 开头的 Sass 文件不会被编译为 CSS，只能被其他文件导入。

```scss
// _variables.scss
$primary-color: #1890ff;

// _mixins.scss
@mixin flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

// main.scss
@use 'variables';
@use 'mixins';

.button {
  background-color: variables.$primary-color;
  @include mixins.flex-center;
}
```

## @use 规则

Sass 推荐使用 `@use` 代替 `@import` 加载模块。

```scss [use.scss]
// 加载模块
@use 'variables';

// 使用模块中的变量
.element {
  color: variables.$primary-color;
}

// 使用 as 设置命名空间
@use 'variables' as v;

.element {
  color: v.$primary-color;
}

// 使用 as * 取消命名空间
@use 'variables' as *;

.element {
  color: $primary-color;
}

// 加载多个模块
@use 'variables';
@use 'mixins';
@use 'functions';
```

## @forward 规则

`@forward` 用于将模块中的变量、混合、函数转发给其他模块。

```scss [forward.scss]
// _library.scss
@forward 'variables';
@forward 'mixins';
@forward 'functions';

// main.scss
@use 'library';

// 可以直接使用 library 中的所有内容
.element {
  color: library.$primary-color;
}
```

## 混合（Mixins）

```scss [mixins.scss]
// 定义混合
@mixin flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

// 使用混合
.header {
  @include flex-center;
}

// 带参数的混合
@mixin border-radius($radius) {
  -webkit-border-radius: $radius;
  -moz-border-radius: $radius;
  border-radius: $radius;
}

.card {
  @include border-radius(8px);
}

// 带默认值的混合
@mixin box-shadow($x: 0, $y: 0, $blur: 4px, $color: rgba(0, 0, 0, 0.2)) {
  box-shadow: $x $y $blur $color;
}

.modal {
  @include box-shadow;
  @include box-shadow(2px, 2px, 10px, rgba(0, 0, 0, 0.3));
}

// 内容块（@content）
@mixin media-mobile {
  @media (max-width: 768px) {
    @content;
  }
}

.container {
  width: 100%;

  @include media-mobile {
    width: 100%;
    padding: 16px;
  }
}

// 向内容块传递参数
@mixin theme($theme: dark) {
  [data-theme='#{$theme}'] {
    @content($theme);
  }
}

@include theme($theme: light) using ($theme) {
  background-color: #fff;
  color: if($theme == light, #333, #fff);
}
```

## 继承（@extend）

```scss [extend.scss]
// 占位符选择器
%message {
  padding: 16px;
  border-radius: 4px;
  font-size: 14px;
}

// 继承占位符
.message-success {
  @extend %message;
  background-color: #52c41a;
  color: #fff;
}

.message-error {
  @extend %message;
  background-color: #f5222d;
  color: #fff;
}

// 编译后
.message-success, .message-error {
  padding: 16px;
  border-radius: 4px;
  font-size: 14px;
}

.message-success {
  background-color: #52c41a;
  color: #fff;
}

.message-error {
  background-color: #f5222d;
  color: #fff;
}

// 继承已有类
.btn {
  padding: 10px 20px;
  border: none;
  cursor: pointer;
}

.btn-primary {
  @extend .btn;
  background-color: #1890ff;
  color: #fff;
}
```

## 运算

```scss [operations.scss]
// 数学运算
$base-width: 100px;
$spacing: 10px;

.container {
  width: $base-width * 2;
  padding: $spacing + 5px;
  margin: math.div($spacing, 2);
}

// 使用 math 模块
@use 'sass:math';

.element {
  width: math.div(100px, 3); // 33.33333px
  height: math.pow(2, 8); // 256
  margin: math.floor(10.8px); // 10px
}

// 颜色运算
$base-color: #1890ff;

.element {
  background-color: $base-color + #111;
  color: $base-color - #222;
}

// 字符串运算
$cursor: pointer;

.element {
  cursor: $cursor;
}
```

## 插值语句

```scss [interpolation.scss]
// 在选择器中使用
$className: 'button';

.#{$className} {
  background-color: #1890ff;
}

// 在属性名中使用
$property: 'margin';

.element {
  #{$property}-top: 10px;
  #{$property}-bottom: 10px;
}

// 在 URL 中使用
$assets-path: '/assets';

.logo {
  background-image: url('#{$assets-path}/logo.png');
}

// 在属性值中使用
$direction: left;

.element {
  border-#{$direction}-width: 2px;
}
```

## 控制指令

### @if 条件

```scss [if.scss]
@use 'sass:math';

@mixin theme($type) {
  @if $type == 'primary' {
    background-color: #1890ff;
    color: #fff;
  } @else if $type == 'success' {
    background-color: #52c41a;
    color: #fff;
  } @else if $type == 'warning' {
    background-color: #faad14;
    color: #333;
  } @else {
    background-color: #d9d9d9;
    color: #333;
  }
}

.button {
  @include theme('primary');
}

// 使用 if() 函数
.element {
  color: if(1 + 1 == 2, #1890ff, #f5222d);
}
```

### @each 循环

```scss [each.scss]
// 遍历列表
$sizes: 4px, 8px, 12px, 16px;

@each $size in $sizes {
  .icon-#{$size} {
    font-size: $size;
  }
}

// 遍历映射
$colors: (
  'primary': #1890ff,
  'success': #52c41a,
  'warning': #faad14,
  'error': #f5222d
);

@each $name, $color in $colors {
  .text-#{$name} {
    color: $color;
  }

  .bg-#{$name} {
    background-color: $color;
  }
}

// 多重赋值
@each $header, $size in (h1: 2rem, h2: 1.5rem, h3: 1.2rem) {
  #{$header} {
    font-size: $size;
  }
}
```

### @for 循环

```scss [for.scss]
// from X through Y（包含 Y）
@for $i from 1 through 3 {
  .col-#{$i} {
    width: math.div(100%, $i);
  }
}

// from X to Y（不包含 Y）
@for $i from 1 to 4 {
  .item-#{$i} {
    margin-left: 10px * $i;
  }
}

// 生成栅格系统
@for $i from 1 through 24 {
  .col-#{$i} {
    width: math.div($i, 24) * 100%;
  }
}
```

### @while 循环

```scss [while.scss]
$i: 6;

@while $i > 0 {
  .item-#{$i} {
    width: 20px * $i;
  }
  $i: $i - 2;
}
```

## 函数

### 内置函数

```scss [functions.scss]
@use 'sass:color';
@use 'sass:math';

// 颜色函数
$base: #1890ff;

.element {
  background-color: color.adjust($base, $lightness: 20%);
  color: color.adjust($base, $lightness: -20%);
  border-color: color.adjust($base, $saturation: 10%);
}

// 简写颜色函数
.element {
  background-color: lighten($base, 20%);
  color: darken($base, 20%);
  border-color: saturate($base, 10%);
}

// 数值函数
.size {
  width: math.round(10.5px); // 11px
  height: math.ceil(10.2px); // 11px
  min-height: math.floor(10.8px); // 10px
}

// 字符串函数
.text {
  content: str-insert('Hello', ' World', 6); // 'Hello World'
  content: str-index('Hello', 'e'); // 2
  content: to-upper-case('hello'); // 'HELLO'
  content: to-lower-case('HELLO'); // 'hello'
}

// 列表函数
$list: 10px, 20px, 30px;

.element {
  margin: nth($list, 1); // 10px
  padding: length($list); // 3
}

// 映射函数
$map: (key1: value1, key2: value2);

.element {
  content: map-get($map, key1); // value1
  content: map-keys($map); // key1, key2
  content: map-values($map); // value1, value2
}
```

### 自定义函数

```scss [custom-functions.scss]
@use 'sass:math';

// 计算 rem
@function px-to-rem($px, $base: 16px) {
  @return math.div($px, $base) * 1rem;
}

.element {
  font-size: px-to-rem(14px); // 0.875rem
  padding: px-to-rem(16px); // 1rem
}

// 计算百分比
@function percentage($value, $total) {
  @return math.div($value, $total) * 100%;
}

.col-6 {
  width: percentage(6, 24); // 25%
}

// 返回多个值
@function spacing($value) {
  @return ($value, $value * 2, $value * 4);
}

.element {
  margin: spacing(8px); // 8px 16px 32px
}
```

## 列表和映射

### 列表

```scss [lists.scss]
// 定义列表
$fonts: Tahoma, Geneva, 'Helvetica Neue', sans-serif;
$sizes: 10px 20px 30px;
$colors: (
  red,
  green,
  blue
);

// 使用列表
body {
  font-family: nth($fonts, 1);
}

// 遍历列表
@each $font in $fonts {
  .font-#{$font} {
    font-family: $font;
  }
}

// 列表函数
$list: 10px, 20px, 30px;

.element {
  length: length($list); // 3
  first: nth($list, 1); // 10px
  index: index($list, 20px); // 2
  join: join($list, 40px); // 10px, 20px, 30px, 40px
  append: append($list, 40px); // 10px, 20px, 30px, 40px
}
```

### 映射

```scss [maps.scss]
// 定义映射
$theme-colors: (
  'primary': #1890ff,
  'success': #52c41a,
  'warning': #faad14,
  'error': #f5222d,
  'info': #13c2c2
);

// 获取映射值
.button-primary {
  background-color: map-get($theme-colors, 'primary');
}

// 遍历映射
@each $name, $color in $theme-colors {
  .bg-#{$name} {
    background-color: $color;
  }

  .text-#{$name} {
    color: $color;
  }
}

// 映射函数
$merged: map-merge($theme-colors, ('dark': #000));
$removed: map-remove($theme-colors, 'info');
$keys: map-keys($theme-colors);
$values: map-values($theme-colors);
$has: map-has-key($theme-colors, 'primary'); // true
```

## 内置模块

Sass 提供了多个内置模块。

```scss [built-in-modules.scss]
// 颜色模块
@use 'sass:color';

.element {
  background: color.adjust(#1890ff, $lightness: 10%);
  color: color.scale(#1890ff, $lightness: 50%);
}

// 数学模块
@use 'sass:math';

.element {
  width: math.div(100px, 3);
  height: math.pow(2, 8);
}

// 字符串模块
@use 'sass:string';

.element::before {
  content: string.to-upper-case('hello');
}

// 列表模块
@use 'sass:list';

$list: 10px, 20px, 30px;
$first: list.nth($list, 1);

// 映射模块
@use 'sass:map';

$map: (key: value);
$value: map.get($map, key);

// 选择器模块
@use 'sass:selector';

// 检查模块
@use 'sass:meta';

@if meta.type-of($value) == 'number' {
  // ...
}
```

## 实际项目示例

```scss [example.scss]
@use 'sass:math';
@use 'sass:color';

// 变量定义
$primary-color: #1890ff;
$text-color: #333;
$border-color: #d9d9d9;
$border-radius: 4px;
$spacing-unit: 8px;

$theme-colors: (
  'primary': $primary-color,
  'success': #52c41a,
  'warning': #faad14,
  'error': #f5222d
);

// 混合定义
@mixin flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

@mixin clearfix {
  &::after {
    content: '';
    display: table;
    clear: both;
  }
}

@mixin text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

// 组件样式
.card {
  background: #fff;
  border-radius: $border-radius;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: $spacing-unit * 2;

  &-header {
    @include flex-center;
    justify-content: space-between;
    border-bottom: 1px solid $border-color;
    padding-bottom: $spacing-unit;
    margin-bottom: $spacing-unit;
  }

  &-body {
    color: $text-color;
    line-height: 1.6;
  }

  &-footer {
    @include clearfix;
    border-top: 1px solid $border-color;
    padding-top: $spacing-unit;
    margin-top: $spacing-unit;
  }
}

// 栅格系统
.row {
  @include clearfix;
  margin: 0 -$spacing-unit;
}

@for $i from 1 through 24 {
  .col-#{$i} {
    float: left;
    width: math.div($i, 24) * 100%;
    padding: 0 $spacing-unit;
    box-sizing: border-box;
  }
}

// 主题颜色类
@each $name, $color in $theme-colors {
  .bg-#{$name} {
    background-color: $color;
  }

  .text-#{$name} {
    color: $color;
  }

  .border-#{$name} {
    border-color: $color;
  }
}

// 响应式混合
@mixin respond-to($breakpoint) {
  @if $breakpoint == 'sm' {
    @media (min-width: 576px) { @content; }
  } @else if $breakpoint == 'md' {
    @media (min-width: 768px) { @content; }
  } @else if $breakpoint == 'lg' {
    @media (min-width: 992px) { @content; }
  } @else if $breakpoint == 'xl' {
    @media (min-width: 1200px) { @content; }
  }
}

.container {
  width: 100%;

  @include respond-to('sm') {
    max-width: 540px;
  }

  @include respond-to('md') {
    max-width: 720px;
  }

  @include respond-to('lg') {
    max-width: 960px;
  }

  @include respond-to('xl') {
    max-width: 1140px;
  }
}
```

::: tip 提示
- 推荐使用 Dart Sass（官方实现）
- 使用 `@use` 代替 `@import`
- 使用 `%placeholder` 定义可继承样式
- 使用 `@content` 向混合传递内容块
- Sass 模块系统提供更好的命名空间管理
:::

::: danger 注意事项
- `@import` 已被弃用，将在未来版本移除
- `math.div()` 代替 `/` 进行除法运算
- 占位符选择器 `%` 不会单独编译输出
- `@use` 每个模块只加载一次
- 变量和函数默认是私有的，使用 `!default` 或 `@forward` 公开
:::
