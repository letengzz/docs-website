# 声明文件与 .d.ts

声明文件（`.d.ts`）是“只有类型、没有实现”的文件，用来描述 JavaScript 模块或全局变量的形状。它是让 TypeScript 项目安全使用纯 JS 库的关键。

## 什么时候需要声明文件

1. 第三方 JS 库没有自带类型，也没有 `@types` 包。
2. 全局变量（如 `window.XXX`、CDN 注入的对象）。
3. 自己写的 JS 模块想被 TS 项目使用。

## 基本语法

```typescript [DeclarationFiles/global.d.ts]
declare const VERSION: string;

declare function formatMoney(amount: number, symbol?: string): string;

declare class ApiClient {
  constructor(baseUrl: string);
  get<T>(path: string): Promise<T>;
}

declare namespace MyLib {
  function init(options: { debug?: boolean }): void;
}
```

这些声明只描述类型，不产生任何运行时代码。

## 模块声明

为没有类型的 npm 包写声明：

```typescript [DeclarationFiles/legacy-utils.d.ts]
declare module "legacy-utils" {
  export function parse(text: string): Record<string, string>;
  export const version: string;
}
```

之后就可以正常导入：

```typescript
import { parse } from "legacy-utils";
```

## 泛型与重载

```typescript [DeclarationFiles/request.d.ts]
declare module "tiny-request" {
  export function request<T>(url: string): Promise<T>;
  export function request(
    url: string,
    options: { method: string; body?: unknown },
  ): Promise<unknown>;
}
```

## 全局类型与 window 扩展

```typescript [DeclarationFiles/window.d.ts]
export {};

declare global {
  interface Window {
    gtag?: (event: string, params: Record<string, unknown>) => void;
  }
}
```

注意：文件内有 `import`/`export` 时是模块声明文件，必须用 `declare global` 扩展全局。

## @types 与 DefinitelyTyped

大多数流行库在 [DefinitelyTyped](https://github.com/DefinitelyTyped/DefinitelyTyped) 有社区类型：

```shell
npm install -D @types/lodash
npm install -D @types/node
```

规则：

1. 库自带类型（`types` 字段或 `.d.ts`）→ 直接使用，不装 @types。
2. 库没有类型且社区有 @types → 安装对应 @types。
3. 两者都没有 → 自己写 `declare module` 或创建 `.d.ts`。

## 发布自己的类型

在 `package.json` 中声明类型入口：

```json [package.json]
{
  "name": "my-utils",
  "main": "dist/index.js",
  "types": "dist/index.d.ts"
}
```

构建时让 tsc 同时产出声明文件：

```shell
tsc --declaration --emitDeclarationOnly --outDir dist
```

## 易错点

::: danger 常见错误
1. 声明文件里写实现：`.d.ts` 只允许类型和 `declare`，写实现会报错。
2. 全局声明文件里有 `import`：文件会变成模块，全局声明失效；需要时用 `declare global`。
3. 装 @types 时版本与库不匹配：如 `@types/react@18` 配 React 19，类型行为不一致。
4. 用 `declare module "*"` 一刀切：所有模块变成 any，失去类型安全。
5. 忘记把 `.d.ts` 纳入 tsconfig 的 include：声明不生效。
:::

## 验证方式

1. 运行 `npx tsc --noEmit`，确认自定义声明文件生效。
2. 故意写一个错误类型（如 `declare const VERSION: number` 却赋字符串），确认报错位置在声明处。
3. 安装 `@types/lodash` 后 `import _ from "lodash"`，确认智能提示出现。

## 参考资料

- 声明文件手册：https://www.typescriptlang.org/docs/handbook/declaration-files/introduction.html
- .d.ts 模板库：https://www.typescriptlang.org/docs/handbook/declaration-files/by-example.html
- DefinitelyTyped：https://github.com/DefinitelyTyped/DefinitelyTyped
