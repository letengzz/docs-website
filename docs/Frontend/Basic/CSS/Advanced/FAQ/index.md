# 常见问题与最佳实践

汇总 CSS 进阶开发中最高频的问题：布局选型、动画性能、响应式策略、原子化取舍与兼容性处理，方便快速查阅。

## 布局类

### Grid 和 Flex 到底怎么选？

| 场景 | 选型 |
| --- | --- |
| 页面骨架、二维网格、卡片墙 | Grid |
| 单行排列、导航、按钮组 | Flex |
| 组件内部一维排布 | Flex |
| 需要同时控制行和列 | Grid |

判断口诀：**先问「一行还是一张网？」**——一行用 Flex，整网用 Grid。

### 居中到底有几种写法？

```css
/* 现代首选：Flex */
.a { display: flex; align-items: center; justify-content: center; }

/* Grid 简洁版 */
.b { display: grid; place-items: center; }

/* 绝对定位 + transform */
.c { position: absolute; left: 50%; top: 50%;
     transform: translate(-50%, -50%); }
```

日常首选 Flex/Grid，绝对定位用于特殊场景。

## 动画类

### 动画卡顿怎么办？

排查顺序：

1. 确认动画只动 `transform` / `opacity`；
2. 用 DevTools Performance 录制，看是否触发 Layout/Paint；
3. 检查是否有大图、模糊滤镜（`filter: blur` 很贵）；
4. 减少同时动画的元素数量，必要时 `content-visibility` 跳过屏外渲染。

### `transition` 写在哪里？

写在**元素默认状态**：

```css
.btn {
  transition: transform 0.2s ease;   /* 正确 */
}
.btn:hover { transform: scale(1.05); }

/* 错误：只写在 hover，移出时无过渡 */
.btn:hover { transition: transform 0.2s ease; }
```

## 响应式类

### 媒体查询还是容器查询？

分工原则：

- **页面骨架**（侧边栏、主内容布局）→ 媒体查询（视口决定）；
- **可复用组件**（卡片、面板、导航条）→ 容器查询（容器决定）。

两者不是替代关系，而是**分层协作**。

### 图片在小屏溢出怎么办？

```css
img, video {
  max-width: 100%;
  height: auto;
}
```

再加响应式图片：`srcset` + `sizes` + WebP/AVIF + `loading="lazy"`。

### `vw` 单位有什么坑？

`100vw` 在部分环境包含滚动条宽度，导致横向溢出；页面级容器用 `max-width: 100%` 或 `100dvw`（动态视口单位）。字号用 `clamp()` 限制范围，避免超大屏失控。

## 架构类

### 怎么避免样式互相覆盖？

1. **BEM 命名**：单类选择器，低特异性；
2. **`@layer`**：显式声明 reset → base → components → utilities；
3. **框架作用域**：Vue Scoped / CSS Modules 隔离组件；
4. 全局规则只写设计令牌与基础排版。

### 原生 CSS 还需要 Sass/Less 吗？

2026 年原生 CSS 已具备：嵌套、变量、`@layer`、`color-mix()`、容器查询。多数新项目**不再需要预处理器**；仍需要的场景：老项目维护、复杂 mixin 复用、团队既有习惯。

## 原子化类

### Tailwind 和 UnoCSS 选哪个？

- 生态与文档成熟度：Tailwind（v4 已支持 Vite 插件）；
- 性能与可定制：UnoCSS（即时引擎、attributify 模式）；
- 两者工具类语法高度兼容，迁移成本低，按团队偏好选。

### 原子化类名太长怎么办？

把重复组合封装成组件：

```html
<!-- 封装前 -->
<button class="px-3 py-1 rounded bg-blue-500 text-white hover:bg-blue-600">
  按钮
</button>

<!-- 封装后（Vue） -->
<BaseButton>按钮</BaseButton>
```

## 兼容性类

### 新特性怎么判断能否用？

1. 查 [caniuse.com](https://caniuse.com/) 看三巨头支持；
2. 看 **Baseline** 状态（Widely Available = 可放心用）；
3. 用 `@supports` 提供降级；
4. 关键交互保留无动画/基础布局降级。

### 需要兼容 IE 吗？

2026 年 IE 已停止支持多年，**新项目不建议兼容**；存量项目用：`display: -ms-grid` 前缀或 Grid/Flex 双实现，配合 `@supports` 渐进增强。

## 最佳实践清单

::: tip CSS 进阶检查清单
1. 布局：一维用 Flex、二维用 Grid，是否选对？
2. 动画：是否只动 transform/opacity？是否尊重 `prefers-reduced-motion`？
3. 响应式：骨架用媒体查询、组件用容器查询，是否分工？
4. 尺寸：字号/间距是否流式（clamp/rem），图片是否 `max-width: 100%`？
5. 架构：是否 BEM + @layer + 设计令牌，无 `!important` 战争？
6. 原子化：动态类名是否避免拼接？暗色模式策略是否配置？
7. 兼容：新特性是否查过 Baseline，是否有 `@supports` 降级？
:::

## 参考资料

- [MDN：CSS 参考](https://developer.mozilla.org/zh-CN/docs/Web/CSS/Reference)
- [caniuse](https://caniuse.com/)
- [web.dev：Learn CSS](https://web.dev/learn/css)
