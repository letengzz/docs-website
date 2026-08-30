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

## 相关资源

- [Tailwind CSS 官方文档](https://tailwindcss.com/docs)
- [UnoCSS 官方文档](https://unocss.dev/guide/)
- [Tailwind CSS 中文网](https://www.tailwindcss.cn/)
- [UnoCSS 中文网](https://www.unocss.cn/)
- [Iconify 图标库](https://icon-sets.iconify.design/)

::: tip 进阶阅读
原子化 CSS 的工程化组合、主题定制与性能验证见 [原子化 CSS 实战](Advanced/AtomicCSS/index.md)。
:::
