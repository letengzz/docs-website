# 常见问题与最佳实践

这一篇汇总 TypeScript 进阶最高频的 10 个问题和一套团队工程实践，覆盖类型设计、配置、迁移与性能。

## 常见问题

### 1. any 和 unknown 有什么区别

`any` 关闭一切检查；`unknown` 是“未知但必须收窄后才能使用”的安全类型。新代码禁止裸 any，外部数据用 `unknown` + 类型守卫。

### 2. interface 和 type 怎么选

接口优先：可扩展（declaration merging）、语义清晰；需要联合类型、交叉类型、映射类型时用 type。团队统一即可，不必迷信。

### 3. 泛型箭头函数为什么是 `<T,>`

在 `.tsx` 文件中 `<T>` 会被解析成 JSX 标签，所以泛型箭头函数要写成 `<T,>` 或 `<T extends unknown>`。

### 4. 怎么拿到函数的返回类型

```typescript
type R = ReturnType<typeof myFunction>;
type P = Parameters<typeof myFunction>;
```

配合 `typeof` 可以在不重复声明的情况下提取类型。

### 5. 条件类型为什么结果和预期不一样

大概率是分配律：裸类型参数会逐成员分发，用 `[T] extends [U]` 包裹可以关闭分发；也有可能是 infer 位置错误。

### 6. 第三方 JS 库没有类型怎么办

依次尝试：库自带类型 → `@types/xxx` → 自己写 `declare module`。不要用 `declare module "*"` 一刀切。

### 7. strictNullChecks 要不要开

必须开。它把 null/undefined 变成显式类型，是 TypeScript 最有价值的安全开关；关闭它等于放弃类型安全。

### 8. 装饰器要不要 experimentalDecorators

TypeScript 5.0+ 支持标准（Stage 3）装饰器，新项目优先用标准装饰器；老项目用 `experimentalDecorators` 保持兼容。团队内统一，不要混用。

### 9. 类型检查越来越慢怎么办

开启 `skipLibCheck`、项目引用（`tsc -b`）、避免巨型联合类型和过度递归条件类型；迁移 TypeScript 7.0（Go 原生编译器）可获得数量级提升。

### 10. 从 JS 迁移到 TS 怎么平滑

先开 `allowJs` + `checkJs: false` 逐步加入；新文件用 `.ts`，老文件分批迁移；用 `any` 暂缓但不新增；最后开启 strict 并纳入 CI 的 `tsc --noEmit`。

## 最佳实践清单

::: tip 可直接落地的清单
1. tsconfig 开启 `strict`，并在 CI 中执行 `tsc --noEmit` 强制检查。
2. 外部数据（API、localStorage、表单）先建模再使用，用类型守卫收窄。
3. 禁止裸 any；实在需要时用 `unknown` + 收窄或局部 `as` 并加注释。
4. 组件 props 全部显式声明，默认值用框架推荐写法。
5. 业务类型集中建模（api 目录），前后端契约用类型表达。
6. 泛型与工具类型（Partial、Pick、Record、ReturnType）优先于重复声明。
7. 使用路径别名 + 统一导入规范，避免相对路径地狱。
8. 声明文件纳入版本管理，不放在 node_modules。
9. 定期升级 TypeScript，关注 5.x → 6.0 → 7.0 的迁移说明。
10. 面试和复习时，用 tsc 实际验证每个类型结论，不要只背答案。
:::

## 验证方式

1. 把 `noImplicitAny` 关闭再打开，对比同一文件的报错差异。
2. 用 `ReturnType<typeof fn>` 写一个工具函数，确认提取类型正确。
3. 在 CI 脚本中加入 `tsc --noEmit`，故意提交一个类型错误，确认流水线失败。

## 参考资料

- TypeScript 官方文档：https://www.typescriptlang.org/docs/
- TypeScript 7.0 发布说明：https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/
- TypeScript 6.0 发布说明：https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/
