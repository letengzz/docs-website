# 原子化 CSS (Atomic CSS) 框架

原子化 CSS 是一种 CSS 架构方式，通过将样式拆分为最小的、可复用的单元（原子类），在 HTML 中直接组合使用，从而提高开发效率和样式复用性。

## 什么是原子化 CSS

原子化 CSS 的核心理念是：

- **单一职责**：每个类只负责一个样式属性
- **组合使用**：通过多个原子类组合实现复杂样式
- **按需生成**：只生成实际使用的样式，减小 CSS 体积
- **避免命名冲突**：不需要为类名绞尽脑汁

```html
<!-- 传统 CSS -->
<div class="card">
  <h3 class="card-title">标题</h3>
  <p class="card-content">内容</p>
</div>

<!-- 原子化 CSS -->
<div class="bg-white rounded-lg shadow p-6">
  <h3 class="text-lg font-semibold text-gray-900">标题</h3>
  <p class="text-gray-500 mt-2">内容</p>
</div>
```

## 主流框架对比

| 特性 | Tailwind CSS | UnoCSS |
|------|--------------|--------|
| 类型 | 框架 | 引擎 |
| 编译速度 | 快 | 极快 |
| 灵活性 | 配置驱动 | 规则驱动 |
| 预设系统 | 插件系统 | 预设系统 |
| 兼容性 | 自有语法 | 兼容 Tailwind/Windi |
| 属性化模式 | 不支持 | 支持 |
| 图标集成 | 需要插件 | 内置支持 |
| 按需生成 | 支持 | 支持 |
| 生态 | 丰富 | 快速增长 |

## 框架介绍

### Tailwind CSS

Tailwind CSS 是最流行的原子化 CSS 框架，提供了丰富的工具类和完善的生态系统。

- **官网**：https://tailwindcss.com/
- **中文网**：https://www.tailwindcss.cn/
- **特点**：
  - 丰富的工具类库
  - 完善的响应式设计
  - 强大的自定义主题能力
  - 活跃的社区和生态
  - 官方 UI 组件库

### UnoCSS

UnoCSS 是一个高性能、高度可定制的原子化 CSS 引擎，具有灵活的预设系统和极快的编译速度。

- **官网**：https://unocss.dev/
- **中文网**：https://www.unocss.cn/
- **特点**：
  - 极快的编译速度
  - 灵活的预设系统
  - 兼容 Tailwind CSS 语法
  - 支持属性化模式
  - 内置图标支持
  - 动态规则和快捷方式

## 如何选择

### 选择 Tailwind CSS 的场景

- 需要完善的生态和组件库
- 团队已经熟悉 Tailwind CSS
- 需要官方支持和长期维护
- 项目较大，需要稳定的解决方案
- 需要丰富的第三方插件

### 选择 UnoCSS 的场景

- 追求极致的编译速度
- 需要高度自定义的规则
- 想要兼容 Tailwind CSS 语法
- 需要属性化模式
- 项目使用 Vite 构建
- 需要灵活的图标集成

## 学习建议

1. **先学 Tailwind CSS**：理解原子化 CSS 的核心概念和工具类
2. **再学 UnoCSS**：了解引擎级别的灵活性和性能优势
3. **掌握核心概念**：响应式设计、状态变体、自定义主题
4. **实践项目**：通过实际项目加深理解
5. **对比使用**：根据项目需求选择合适的框架

## 核心概念

### 工具类优先

直接在 HTML 中使用预定义的类名组合样式，无需编写自定义 CSS。

### 响应式设计

使用断点前缀实现不同屏幕尺寸的样式。

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <!-- 移动端 1 列，平板 2 列，桌面 3 列 -->
</div>
```

### 状态变体

使用状态前缀实现 hover、focus、active 等状态样式。

```html
<button class="bg-blue-500 hover:bg-blue-600 focus:ring-2 text-white">
  按钮
</button>
```

### 自定义主题

通过配置文件自定义颜色、字体、间距等主题变量。

```javascript
// Tailwind CSS
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: { 500: '#3b82f6' },
      },
    },
  },
}

// UnoCSS
export default defineConfig({
  theme: {
    colors: {
      primary: { 500: '#3b82f6' },
    },
  },
})
```

## 快速开始

### Tailwind CSS

```bash
# 安装
npm install -D tailwindcss postcss autoprefixer

# 初始化配置
npx tailwindcss init -p

# 使用
<div class="bg-blue-500 text-white p-4 rounded">Hello Tailwind!</div>
```

### UnoCSS

```bash
# 安装
npm install -D unocss

# Vite 配置
import UnoCSS from 'unocss/vite'

# 使用
<div class="bg-blue-500 text-white p-4 rounded">Hello UnoCSS!</div>
```

## 原子类与设计 token 的分工（第 189 天补充）

原子化 CSS 与设计 token 不是替代关系，而是**上下游**：token 决定「有哪些值」，原子类决定「这些值怎么被写成类名」。

| 问题 | 原子类回答 | 设计 token 回答 |
| --- | --- | --- |
| 这个间距是多少 | `p-3` 对应哪一个刻度 | `--space-12` 的取值与它属于哪一层 |
| 换主题时改什么 | 改配置里的主题映射 | 改语义层的引用关系 |
| 谁能改 | 任何写页面的人 | 设计系统维护者（受版本与影响面约束） |
| 跨端怎么复用 | 不能（原子类只在 CSS 里） | 能（同一份 token 编译到 CSS / 原生 / 小程序） |

Tailwind v4 把两者接在同一处：`@theme` 里声明的变量**既是 CSS 变量、又会生成工具类**。

```css [src/styles/theme.css]
@import "tailwindcss";

@theme {
  /* 语义 token 直接作为 @theme 变量：既生成 bg-surface，也可 var(--color-surface) */
  --color-surface: var(--bg-canvas);
  --color-accent: var(--accent-solid);
  --spacing-card: var(--space-12);
}
```

::: danger 不要把 token 直接写成原子类名
1. 写 `--color-surface: #f7f7f5` 是把**值**搬进 `@theme`，换主题时仍然要改这里，等于又多了一份源；
2. 正确写法是让 `@theme` 变量**引用**语义 token（如上例），主题切换只改语义层；
3. 反过来，页面里不要用 `bg-blue-500` 这种原始色阶类——它绕过了语义层，深色模式下不会跟着变。

token 的三层分工、双产物与影响面计算见 [设计系统与组件库工程 · Token](../../../DesignSystem/Tokens/index.md)；主题的两种实现（覆盖式 293 B vs 编译式 2,821 B）见 [主题与多品牌](../../../DesignSystem/Theming/index.md)。
:::

## 相关资源

- [Tailwind CSS 官方文档](https://tailwindcss.com/docs)
- [UnoCSS 官方文档](https://unocss.dev/guide/)
- [Tailwind CSS 中文网](https://www.tailwindcss.cn/)
- [UnoCSS 中文网](https://www.unocss.cn/)
- [Iconify 图标库](https://icon-sets.iconify.design/)

::: tip 进阶阅读
原子化 CSS 的工程化组合、主题定制与性能验证见 [原子化 CSS 实战](../Advanced/AtomicCSS/index.md)。
:::

## 子页导航

- [Tailwind CSS](TailwindCSS/index.md)
- [UnoCSS](UnoCSS/index.md)
