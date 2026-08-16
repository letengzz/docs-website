# 模板字面量类型

模板字面量类型（Template Literal Types）用反引号把字符串“模板化”，配合联合类型和 `infer`，可以把字符串变成类型系统里的可解析结构，常用于事件名、路由参数、CSS 类名等场景。

## 基本语法

```typescript [TemplateLiteralTypes/BasicDemo.ts]
type Size = "small" | "medium" | "large";
type Color = "red" | "blue";

type ButtonClass = `btn-${Size}-${Color}`;
// "btn-small-red" | "btn-small-blue" | ... 共 6 种

const ok: ButtonClass = "btn-large-blue";
// const bad: ButtonClass = "btn-huge-red";  // 报错
```

模板中的占位符是联合类型时，结果会自动做**笛卡尔积展开**。

## 模式匹配与 infer 提取

```typescript [TemplateLiteralTypes/ExtractDemo.ts]
type ExtractId<T extends string> =
  T extends `/user/${infer Id}` ? Id : never;

type A = ExtractId<"/user/1001">;   // "1001"
type B = ExtractId<"/order/abc">;   // never
```

## 实战：类型安全的路由参数

```typescript [TemplateLiteralTypes/RouteParams.ts]
type Route = "/user/:id" | "/user/:id/order/:orderId";

type ParamsOf<T extends string> =
  T extends `${infer _A}/:${infer Param}/${infer Rest}`
    ? { [K in Param]: string } & ParamsOf<`/:${Rest}`>
    : T extends `${infer _A}/:${infer Param}`
      ? { [K in Param]: string }
      : {};

type Params = ParamsOf<Route>;
// { id: string } & { orderId: string }

function buildPath<T extends string>(
  route: T,
  params: ParamsOf<T>,
) {
  return route.replace(/:(\w+)/g, (_, key: keyof typeof params) =>
    String(params[key]));
}
```

调用时参数会被强制校验：

```typescript
// buildPath("/user/:id", {});              // 报错：缺 id
const path = buildPath("/user/:id/order/:orderId", {
  id: "1",
  orderId: "2",
});
```

## 内置字符串工具

| 工具 | 作用 | 示例 |
| --- | --- | --- |
| `Uppercase<S>` | 全大写 | `Uppercase<"abc">` → `"ABC"` |
| `Lowercase<S>` | 全小写 | `Lowercase<"ABC">` → `"abc"` |
| `Capitalize<S>` | 首字母大写 | `Capitalize<"abc">` → `"Abc"` |
| `Uncapitalize<S>` | 首字母小写 | `Uncapitalize<"Abc">` → `"abc"` |

```typescript [TemplateLiteralTypes/CaseDemo.ts]
type EventName = `on${Capitalize<"click" | "input">}`;
// "onClick" | "onInput"
```

## 实战：事件映射表

```typescript [TemplateLiteralTypes/EventMap.ts]
type ElementEvents = {
  click: MouseEvent;
  input: InputEvent;
  keydown: KeyboardEvent;
};

type ListenerMap<T> = {
  [K in keyof T as `on${Capitalize<string & K>}`]: (e: T[K]) => void;
};

type Listeners = ListenerMap<ElementEvents>;
// { onClick: (e: MouseEvent) => void; onInput: ...; onKeydown: ... }
```

`as` 重映射键可以把类型键转换成事件监听器名。

## 易错点

::: danger 常见错误
1. 占位符里放非字面量联合：`${string}` 会退化成普通 string，失去精确匹配。
2. 忘记联合展开会产生“爆炸”：多个多成员占位符会生成大量组合，保持占位符成员数量可控。
3. 递归模板解析不收敛：每次递归必须消费 `/${Rest}` 等片段，否则类型实例化过深。
4. `Capitalize` 等工具只处理首字母：需要逐词转换时要自己写递归类型。
5. 把模板字面量类型用在运行时字符串拼接：它是编译期类型，运行时仍用普通模板字符串。
:::

## 验证方式

1. 运行 `npx tsc --noEmit TemplateLiteralTypes/*.ts`，确认类型成立。
2. 把 `buildPath("/user/:id", {})` 取消注释，确认编译器提示缺少 `id`。
3. 在 IDE 悬停 `ListenerMap<ElementEvents>` 展开结果，对照事件名转换。

## 参考资料

- 模板字面量类型手册：https://www.typescriptlang.org/docs/handbook/2/template-literal-types.html
- 键重映射：https://www.typescriptlang.org/docs/handbook/2/mapped-types.html#key-remapping-via-as
- 字符串工具类型：https://www.typescriptlang.org/docs/handbook/2/template-literal-types.html#intrinsic-string-manipulation-types
