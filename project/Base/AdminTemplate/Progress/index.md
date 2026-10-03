# 进展记录

## 一、本次产出（2026-10-03）

| 步骤 | 页面 | 内容 | 配图 |
| --- | --- | --- | --- |
| — | [`index.md`](../index.md)（专题入口） | 定位、与 NuxtTemplate 的分工、快速上手 | `admin-topic-map.svg` |
| 0 | [`Requirement/`](../Requirement/index.md) 需求与方案定位 | 分层定位、三条硬约束、三路线对照、明确不做 | `admin-layering.svg` |
| 1 | [`Bootstrap/`](../Bootstrap/index.md) 初始化基线 | 五步流程、基线验收、`template.config.json` 读取纪律、admin 区间 | `admin-init-flow.svg` |
| 2 | [`StackAdapter/`](../StackAdapter/index.md) 技术栈适配层 | 构建期查表、目录约定、共享 props 契约、实现示例 | `admin-adapter.svg` |
| 3 | [`Skeleton/`](../Skeleton/index.md) 后台骨架 | 双布局、菜单单一来源、页面组织、404 | `admin-layout.svg` |
| 4 | [`Login/`](../Login/index.md) 登录与路由守卫 | 演示接口、useAuth、全局守卫、登录页、退出闭环 | `admin-auth-flow.svg` |

合计 **6 页 + 本篇**，配 6 张 SVG。

## 二、方案上的关键取舍

1. **适配层走构建期查表，不走运行时切换**。`nuxt.config.ts` 在构建时读 `template.config.json`，把 `Ui*` 适配名注册为所选框架目录下的唯一实现。运行时 `<component :is>` 方案被否决：五套实现全部进产物、props 类型推导失效、SSR 多一拍 hydration 抖动。
2. **实现文件放 `app/ui-impl/` 而非 `app/components/` 下**。`components/` 下的同名实现会被 Nuxt 自动导入互相打架，且五份全部进产物；放外面用 `components` 配置项按目录注册，产物里永远只有一份。
3. **登录判据只认服务端**。令牌走 HttpOnly Cookie，`useAuth.fetchUser()` 问 `/api/auth/me` 是唯一可信判据；前端不缓存「是否登录」的本地结论，避免与 SSR 双端事实相反。
4. **演示接口只有三个**（login / me / logout），内存令牌表明确标注「演示品，生产替换」；接真实后端时只动 `server/api/auth/` 一处。

## 三、如何验证（本轮的判据）

- 结构自检：H1 唯一、容器配对、无裸插值、图片引用路径为 `../assets/`（子页）/ `./assets/`（目录页），全库巡检脚本全绿。
- 约束可执行化：三条硬约束各给了 grep/命令判据（`pnpm verify` 仍 12/12；框架 import 只出现在 `app/ui-impl/`；无框架组合全流程走通）。
- 诚实标注：与 NuxtTemplate 同口径，本文按官方文档逐处核对编写，**未实际跑过初始化与登录流程**，读者按各页「验证方式」本地执行。

## 四、下一步

| # | 方向 | 说明 |
| --- | --- | --- |
| 1 | 权限模块 | 「登录/未登录」二值判断升级为角色与按钮级权限；参考 [Vue3 模板 · 权限模块](../../Vue3Template/Permission/index.md) 的思路，落在骨架的守卫与菜单过滤上 |
| 2 | 五框架实现补全 | `ui-impl/` 目前给了契约与两个示例实现（element-plus / plain），其余三个框架实现按契约表逐个补齐 |
| 3 | 接真实后端 | 用 [后端通用模板](../../BackendTemplate/index.md) 的认证接口替换演示接口，验证「只动 server/api/auth 一处」的承诺 |
| 4 | 部署形态 | 沿用 NuxtTemplate 的[部署文档](../../NuxtTemplate/Deployment/index.md)，补后台模板特有的环境变量清单与验收项 |
