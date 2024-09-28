# OpenTiny

OpenTiny 是一个由华为开源的轻量级 Vue 组件库，同时支持 Vue 2.0 和 Vue 3.0。专为现代 web 应用设计，提供了一系列精心设计的组件和工具，包含布局、导航、菜单、表格、日历、图表等 70+ 组件。旨在为开发者提供一套完整的前端解决方案，以快速构建高质量的企业级应用。

官方网站：https://opentiny.design/

部分组件预览：

![图片](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202409281730261.png)

![图片](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202409281730296.webp)

![图片](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202409281730052.webp)

![图片](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202409281730428.webp)

![图片](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202409281730340.webp)

![图片](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202409281730614.webp)

使用组件：

```shell
// 安装
npm install @opentiny/vue@2 // vue2
npm install @opentiny/vue@3 // vue3
// vite.config.js 配置
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import autoImportPlugin from '@opentiny/unplugin-tiny-vue'
export default defineConfig({
  plugins: [vue(), autoImportPlugin('vite')],
  define: {
    'process.env': { ...process.env }
  }
})
```

功能和特性：

- 组件丰富：提供了一系列预制的 UI 组件，覆盖了表单、数据展示、导航、布局、反馈等多种场景。
- 支持主流浏览器：Chrome、Edge、Firefox、Opera、Safari 。
- 组件导入方式：支持自动导入、多组件引入、单组件引入以及完整引入四种方式。
- 主题定制：支持主题定制，允许开发者根据品牌风格调整组件的样式和颜色。
- 响应式设计：组件支持响应式布局，确保在不同设备和屏幕尺寸上都能提供良好的用户体验。
- 国际化支持：支持多语言，方便在全球范围内使用。
- 无障碍性：遵循无障碍设计原则，确保所有用户都能方便地使用应用。
- 文档和示例：提供详细的文档和丰富的示例代码，帮助开发者快速上手。