# Less

Less（Leaner Style Sheets）是一个基于 JavaScript 的 CSS 预处理器，语法与原生 CSS 高度兼容，学习成本低。

- 官方文档：https://lesscss.org/
- GitHub：https://github.com/less/less.js

## 安装

```bash
# npm 安装
npm install -g less

# 项目本地安装
npm install --save-dev less

# 使用 lessc 编译
lessc styles.less styles.css

# 压缩输出
lessc styles.less styles.css --clean-css

# 监听模式
lessc styles.less styles.css --watch
```

## 变量

Less 允许使用变量存储可复用的值。

```less [variables.less]
// 定义变量
@primary-color: #1890ff;
@font-size-base: 14px;
@border-radius: 4px;
@spacing: 16px;

// 使用变量
.button {
  background-color: @primary-color;
  font-size: @font-size-base;
  border-radius: @border-radius;
  padding: @spacing;
}

// 变量名本身也可以是变量
@var: 'primary';
@primary-color: #1890ff;

.element {
  color: @@var; // 编译为 #1890ff
}
```

编译后：

```css [variables.css]
.button {
  background-color: #1890ff;
  font-size: 14px;
  border-radius: 4px;
  padding: 16px;
}

.element {
  color: #1890ff;
}
```

## 嵌套

Less 允许在 CSS 选择器中嵌套选择器，使代码更清晰。

```less [nesting.less]
// 基本嵌套
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

// 媒体查询嵌套
.container {
  width: 100%;

  @media (min-width: 768px) {
    width: 750px;
  }

  @media (min-width: 992px) {
    width: 970px;
  }

  @media (min-width: 1200px) {
    width: 1170px;
  }
}
```

## 混合（Mixins）

混合允许将一个类的所有属性引入到另一个类中。

```less [mixins.less]
// 基本混合
.border-radius {
  -webkit-border-radius: 4px;
  -moz-border-radius: 4px;
  border-radius: 4px;
}

.button {
  .border-radius;
}

// 带参数的混合
.border-radius(@radius) {
  -webkit-border-radius: @radius;
  -moz-border-radius: @radius;
  border-radius: @radius;
}

.card {
  .border-radius(8px);
}

// 带默认值的混合
.box-shadow(@x: 0, @y: 0, @blur: 4px, @color: rgba(0, 0, 0, 0.2)) {
  box-shadow: @x @y @blur @color;
}

.modal {
  .box-shadow();
  .box-shadow(2px, 2px, 10px, rgba(0, 0, 0, 0.3));
}

// 多个参数
.transition(@property: all, @duration: 0.3s, @timing: ease) {
  transition: @property @duration @timing;
}

.link {
  .transition(color, 0.2s, linear);
}

// 命名参数
.element {
  .box-shadow(@color: red, @blur: 8px);
}
```

## 运算

Less 支持在属性值上进行数学运算。

```less [operations.less]
@base-width: 100px;
@spacing: 10px;

.container {
  width: @base-width * 2;
  padding: @spacing + 5px;
  margin: @spacing / 2;
}

// 颜色运算
@base-color: #1890ff;

.element {
  background-color: @base-color + #111;
  color: @base-color - #222;
}

// 单位转换
@font-size: 14px;

.text {
  font-size: @font-size * 1.5; // 21px
  line-height: (@font-size * 1.5) + 4px; // 25px
}
```

## 函数

Less 提供了多种内置函数用于处理颜色和数值。

```less [functions.less]
// 颜色函数
@base: #1890ff;

.element {
  background-color: lighten(@base, 20%);
  color: darken(@base, 20%);
  border-color: saturate(@base, 10%);
  outline-color: desaturate(@base, 10%);
  box-shadow: 0 0 5px fade(@base, 50%);
}

// 数值函数
.size {
  width: round(10.5px); // 11px
  height: ceil(10.2px); // 11px
  min-height: floor(10.8px); // 10px
  margin: percentage(0.5); // 50%
}

// 字符串函数
.text::before {
  content: replace("Hello World", "World", "Less");
}
```

## 继承（Extend）

使用 `:extend()` 伪类实现选择器继承。

```less [extend.less]
// 基本继承
.btn {
  padding: 10px 20px;
  border: none;
  cursor: pointer;
}

.btn-primary {
  &:extend(.btn);
  background-color: #1890ff;
  color: #fff;
}

// 全部继承
.nav-item {
  display: inline-block;
  margin: 0 10px;
}

.nav-item a:extend(.nav-item all) {
  text-decoration: none;
}

// 多重继承
.alert {
  padding: 15px;
  border-radius: 4px;
}

.alert-success {
  &:extend(.alert);
  background-color: #52c41a;
}
```

## 命名空间和访问器

```less [namespaces.less]
// 命名空间
#bundle {
  .button() {
    display: block;
    padding: 10px 20px;
    border: 1px solid #1890ff;
  }

  .tab() {
    display: inline-block;
    margin-right: 10px;
  }
}

// 使用命名空间中的混合
.header {
  #bundle > .button;
}

.nav-item {
  #bundle > .tab;
}
```

## 作用域

Less 中的作用域与编程语言类似，变量先在局部查找，找不到则向父级作用域查找。

```less [scope.less]
@var: red;

.page {
  @var: white;

  .header {
    color: @var; // white
  }

  .footer {
    color: @var; // white
  }
}

.sidebar {
  color: @var; // red
}
```

## 导入

```less [import.less]
// 导入其他 less 文件
@import "variables.less";
@import "mixins.less";
@import "reset.less";

// 导入 CSS 文件（不会被处理）
@import (css) "library.css";

// 仅引用，不处理内容
@import (reference) "library.less";

// 内联导入
@import (inline) "library.css";

// 多次导入只处理一次
@import (once) "library.less";
```

## 条件表达式

```less [guards.less]
// 使用 when 关键字
.mixin(@a) when (@a > 10) {
  result: greater;
}

.mixin(@a) when (@a < 10) {
  result: smaller;
}

.mixin(@a) when (@a = 10) {
  result: equal;
}

.element {
  .mixin(15); // result: greater
}

// 类型检查函数
.mixin(@a) when (isnumber(@a)) {
  value: @a;
}

.mixin(@a) when (iscolor(@a)) {
  color: @a;
}

.mixin(@a) when (isstring(@a)) {
  content: @a;
}
```

## 循环

```less [loops.less]
// 使用递归实现循环
.generate-columns(@n, @i: 1) when (@i =< @n) {
  .col-@{i} {
    width: (@i * 100% / @n);
  }
  .generate-columns(@n, (@i + 1));
}

// 生成 12 列栅格
.generate-columns(12);

// 循环生成间距类
.loop-spacing(@n, @i: 1) when (@i =< @n) {
  .m-@{i} {
    margin: (@i * 4px);
  }
  .p-@{i} {
    padding: (@i * 4px);
  }
  .loop-spacing(@n, (@i + 1));
}

.loop-spacing(10);
```

## 映射（Maps）

Less 3.5+ 支持从混合和规则集中访问值。

```less [maps.less]
// 定义映射
@colors: {
  primary: #1890ff;
  success: #52c41a;
  warning: #faad14;
  error: #f5222d;
};

// 使用映射
.button-primary {
  background-color: @colors[primary];
}

.button-success {
  background-color: @colors[success];
}

// 从混合中获取值
.theme() {
  @primary: #1890ff;
  @secondary: #722ed1;
}

.element {
  color: .theme[@primary];
  border-color: .theme[@secondary];
}
```

## 实际项目示例

```less [example.less]
// 变量定义
@primary-color: #1890ff;
@text-color: #333;
@border-color: #d9d9d9;
@border-radius: 4px;
@spacing-unit: 8px;

// 混合定义
.flex-center() {
  display: flex;
  align-items: center;
  justify-content: center;
}

.clearfix() {
  &::after {
    content: '';
    display: table;
    clear: both;
  }
}

// 组件样式
.card {
  background: #fff;
  border-radius: @border-radius;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: @spacing-unit * 2;

  &-header {
    .flex-center();
    justify-content: space-between;
    border-bottom: 1px solid @border-color;
    padding-bottom: @spacing-unit;
    margin-bottom: @spacing-unit;
  }

  &-body {
    color: @text-color;
    line-height: 1.6;
  }

  &-footer {
    .clearfix();
    border-top: 1px solid @border-color;
    padding-top: @spacing-unit;
    margin-top: @spacing-unit;
  }
}

// 栅格系统
.row {
  .clearfix();
  margin: 0 -@spacing-unit;
}

.generate-grid(@n, @i: 1) when (@i =< @n) {
  .col-@{i} {
    float: left;
    width: (@i * 100% / @n);
    padding: 0 @spacing-unit;
    box-sizing: border-box;
  }
  .generate-grid(@n, (@i + 1));
}

.generate-grid(24);
```

::: tip 提示
- Less 完全兼容 CSS 语法
- 变量使用 `@` 符号
- 混合可以带参数和默认值
- 使用 `&` 引用父选择器
- Less 4.x 支持现代 JavaScript 环境
:::

::: danger 注意事项
- Less 变量没有块级作用域，只有函数作用域
- 循环使用递归实现，注意递归深度
- `:extend()` 默认只继承当前选择器，使用 `all` 关键字继承所有
- Less 函数不能直接定义在顶层，需要在混合或规则集中使用
:::
