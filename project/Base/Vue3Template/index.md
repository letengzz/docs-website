# Vue3模板

一个可直接用于中后台项目的 **Vue 3 + Vite + TypeScript** 工程模板：从初始化、规范、请求封装，到权限、主题、组件库、构建优化与发布回滚，形成完整闭环。本文档按模块逐步完成，每个模块都给出**完整文件内容 + 完整命令 + 可验证收尾**。

## 目录结构

### 工程初始化

- [初始化项目](InitProject/index.md)
- [配置环境变量](Env/index.md)
- [拆分配置](SplitConfig/index.md)
- [配置打包构建优化](Build/index.md)

### 基础设施

- [封装 Pinia](Pinia/index.md)
- [配置自动路由](Router/index.md)
- [配置自动导入](AutoImport/index.md)
- [配置组件自动注册](AutoComponent/index.md)
- [配置VueUse工具集](VueUse/index.md)
- [配置VueRequest](VueRequest/index.md)
- [配置国际化](i18n/index.md)
- [自定义配置网络请求](Http/index.md)

### 业务增强

- [权限模块](Permission/index.md)
- [主题模块](Theme/index.md)
- [组件库集成](ComponentLibrary/index.md)

### 样式体系

- [配置CSS代码检查工具](‌Stylelint/index.md)
- [配置SCSS](SCSS/index.md)
- [配置UnoCSS](UnoCSS/index.md)

### 发布与运维

- [发布模块](Release/index.md)
- [常见问题与最佳实践](FAQ/index.md)

::: info 当前使用的版本
Node 20.x / pnpm 10.x / Vue 3.5.x / Vite 6.x / TypeScript 5.x / Element Plus 2.x（以项目 `package.json` 实际锁定版本为准）。
:::

## 迭代记录

| 日期 | 迭代内容 |
| --- | --- |
| 首版 | 初始化项目、Pinia、自动路由、自动导入、组件自动注册、VueUse、环境变量、i18n、请求封装、构建优化、拆分配置、样式体系 |
| 本次 | **新增权限模块**（路由/菜单/按钮三层权限）、**主题模块**（设计令牌 + 明暗主题 + 组件库联动）、**组件库集成**（按需引入 + 二次封装分层）、**发布模块**（多环境构建 + 版本化发布 + 回滚）、**常见问题与最佳实践**；补齐 VueRequest 页面，环境变量补充多环境章节 |

## 使用方式

```shell
# 1. 安装依赖
pnpm install

# 2. 启动开发
pnpm dev

# 3. 构建生产产物
pnpm build:prod
```

预期结果：开发服务启动后访问终端提示的地址（默认 `http://localhost:5173`），页面正常渲染且控制台无报错；构建成功后在 `dist/` 生成产物。

## 推荐阅读顺序

1. 先按「工程初始化」把项目跑起来，理解环境变量与构建配置。
2. 再读「基础设施」，掌握状态管理、路由、请求封装。
3. 接着看「业务增强」，接入权限、主题与组件库。
4. 最后看「发布与运维」，把项目安全地发出去。

## 相关专题

- [前端工程化专题](../../../docs/Frontend/Others/FrontendEngineering/index.md)：代码规范、测试、CI 集成
- [Vue 3 框架文档](../../../docs/Frontend/Frame/Vue/index.md)：响应式、组件与路由原理
- [跨端开发](../../../docs/Frontend/Frame/CrossPlatform/index.md)：需要多端时的方案选型

## 参考资料

- Vue 3 官方文档：https://cn.vuejs.org/
- Vite 官方文档：https://cn.vitejs.dev/
- Pinia 官方文档：https://pinia.vuejs.org/zh/
- Element Plus 官方文档：https://element-plus.org/zh-CN/
