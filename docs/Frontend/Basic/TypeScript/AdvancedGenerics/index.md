# 泛型进阶

泛型（Generics）让类型“像参数一样”复用。进阶要点是：**约束（extends）、默认参数、keyof 联动、泛型工具与泛型组件**。

## 泛型约束

```typescript [AdvancedGenerics/ConstraintDemo.ts]
interface HasLength {
  length: number;
}

function longest<T extends HasLength>(a: T, b: T): T {
  return a.length >= b.length ? a : b;
}

longest("abc", "de");            // string 有 length
longest([1, 2], [3]);            // number[] 有 length
// longest(1, 2);                // 报错：number 没有 length
```

## keyof 约束

```typescript [AdvancedGenerics/KeyofDemo.ts]
function getValue<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const user = { name: "张三", age: 25 };
const name = getValue(user, "name");   // string
// getValue(user, "email");            // 报错：email 不是 user 的键
```

`K extends keyof T` 保证传入的键一定存在，返回值类型跟随键变化。

## 默认类型参数

```typescript [AdvancedGenerics/DefaultParam.ts]
function createList<T = string>(): T[] {
  return [];
}

const strings = createList();          // string[]
const numbers = createList<number>();  // number[]
```

默认参数要放在类型参数列表末尾。

## 泛型类与工厂函数

```typescript [AdvancedGenerics/FactoryDemo.ts]
class Box<T> {
  constructor(public value: T) {}

  map<U>(fn: (value: T) => U): Box<U> {
    return new Box(fn(this.value));
  }
}

const box = new Box(10);
const text = box.map(String);          // Box<string>
```

## 泛型与联合类型联动

```typescript [AdvancedGenerics/UnionDemo.ts]
type Result<T> = { ok: true; value: T } | { ok: false; error: string };

function parse<T>(input: string, parseFn: (raw: string) => T): Result<T> {
  try {
    return { ok: true, value: parseFn(input) };
  } catch (e) {
    return { ok: false, error: (e as Error).message };
  }
}

const result = parse("42", Number);
if (result.ok) {
  console.log(result.value);   // number
}
```

## 实战：类型安全的事件发射器

```typescript [AdvancedGenerics/EventEmitter.ts]
type Events = {
  click: { x: number; y: number };
  keydown: { key: string };
};

class Emitter<T extends Record<string, unknown>> {
  private handlers = new Map<keyof T, Array<(payload: any) => void>>();

  on<K extends keyof T>(event: K, handler: (payload: T[K]) => void) {
    const list = this.handlers.get(event) ?? [];
    list.push(handler as (payload: any) => void);
    this.handlers.set(event, list);
  }

  emit<K extends keyof T>(event: K, payload: T[K]) {
    this.handlers.get(event)?.forEach((fn) => fn(payload));
  }
}

const emitter = new Emitter<Events>();
emitter.on("click", (p) => console.log(p.x, p.y));   // p 自动推断
emitter.emit("click", { x: 1, y: 2 });
```

## 易错点

::: danger 常见错误
1. 泛型不加约束就访问属性：`T.length` 报错，先 `T extends HasLength`。
2. 类型参数顺序混乱：带默认值的参数必须放最后。
3. 用 `any` 代替泛型：丢失类型联动，泛型的价值就没了。
4. `keyof T` 与索引访问混用：`T[K]` 才能拿到键对应值的类型。
5. 泛型组件里把类型参数当运行值：类型参数只存在于编译期，运行时不可用。
:::

## 验证方式

1. 运行 `npx tsc --noEmit AdvancedGenerics/*.ts`，确认无报错。
2. 把 `getValue(user, "email")` 取消注释，确认编译器报错。
3. 在 IDE 中把鼠标悬停在 `emitter.on("click", p => ...)` 的 `p` 上，确认类型为 `{ x: number; y: number }`。

## 参考资料

- 泛型手册：https://www.typescriptlang.org/docs/handbook/2/generics.html
- keyof 类型操作符：https://www.typescriptlang.org/docs/handbook/2/keyof-types.html
- 索引访问类型：https://www.typescriptlang.org/docs/handbook/2/indexed-access-types.html
