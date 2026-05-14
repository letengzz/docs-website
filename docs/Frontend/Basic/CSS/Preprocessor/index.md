# 预处理器

CSS 预处理器是一种脚本语言，它扩展了 CSS 的功能，使 CSS 更易于编写和维护。预处理器代码最终会被编译为标准的 CSS 代码。

## 为什么使用预处理器

- **变量**：定义可复用的值（颜色、字体、间距等）
- **嵌套**：更清晰地表达选择器之间的层级关系
- **混合（Mixins）**：复用样式代码块
- **函数**：处理颜色、数值等
- **运算**：在样式中进行数学计算
- **继承**：共享样式规则
- **模块化**：将样式拆分为多个文件

## 主流预处理器对比

| 特性 | Less | Sass (SCSS) | Stylus |
|------|------|-------------|--------|
| 语法 | CSS 兼容 | CSS 兼容 | 灵活 |
| 变量符号 | `@` | `$` | 无符号或 `$` |
| 混合调用 | `.mixin()` | `@include mixin` | `mixin()` |
| 继承 | `:extend()` | `@extend` | `@extend` |
| 条件语句 | `when` | `@if` | `if/else` |
| 循环 | 递归 | `@for/@each/@while` | `for/each/while` |
| 运行环境 | Node.js/浏览器 | Ruby/Dart/Node.js | Node.js |
| 社区活跃度 | 中 | 高 | 低 |

## 选择建议

- **Less**：适合 React 项目（Ant Design 使用），语法与 CSS 高度兼容
- **Sass**：最流行，生态最完善，适合大多数项目
- **Stylus**：语法最灵活，适合喜欢简洁语法的开发者

## 学习路径

- [Less](Less/index.md) - JavaScript 编写的 CSS 预处理器，语法与 CSS 高度兼容
- [Sass](Sass/index.md) - 最成熟、最强大的 CSS 扩展语言
- [Stylus](Stylus/index.md) - 富有表现力的 CSS 预处理器，语法灵活

::: tip 提示
- 如果项目已有技术栈，建议使用与框架匹配的预处理器
- Vue 项目推荐使用 Sass
- React + Ant Design 项目推荐使用 Less
- 新项目可以自由选择，推荐 Sass
:::
