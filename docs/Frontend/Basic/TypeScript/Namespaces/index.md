# TypeScript 命名空间

## 命名空间基础

命名空间用于组织代码，避免全局命名冲突。

```typescript [namespace-basic.ts]
// 基础命名空间
namespace Validation {
  export interface StringValidator {
    isAcceptable(s: string): boolean
  }

  const lettersRegexp = /^[A-Za-z]+$/
  const numberRegexp = /^[0-9]+$/

  export class LettersOnlyValidator implements StringValidator {
    isAcceptable(s: string) {
      return lettersRegexp.test(s)
    }
  }

  export class ZipCodeValidator implements StringValidator {
    isAcceptable(s: string) {
      return s.length === 5 && numberRegexp.test(s)
    }
  }
}

// 使用
const validator = new Validation.LettersOnlyValidator()
console.log(validator.isAcceptable('Hello'))  // true
```

## 命名空间拆分

```typescript [namespace-split.ts]
// Validation.ts
namespace Validation {
  export interface StringValidator {
    isAcceptable(s: string): boolean
  }
}

// LettersOnlyValidator.ts
/// <reference path="Validation.ts" />
namespace Validation {
  const lettersRegexp = /^[A-Za-z]+$/

  export class LettersOnlyValidator implements StringValidator {
    isAcceptable(s: string) {
      return lettersRegexp.test(s)
    }
  }
}

// ZipCodeValidator.ts
/// <reference path="Validation.ts" />
namespace Validation {
  const numberRegexp = /^[0-9]+$/

  export class ZipCodeValidator implements StringValidator {
    isAcceptable(s: string) {
      return s.length === 5 && numberRegexp.test(s)
    }
  }
}
```

## 别名

```typescript [namespace-alias.ts]
namespace Shapes {
  export namespace Polygons {
    export class Triangle {}
    export class Square {}
    export class Pentagon {}
  }
}

// 使用别名
import Polygon = Shapes.Polygons

const triangle = new Polygon.Triangle()
const square = new Polygon.Square()

// 函数别名
namespace MathUtils {
  export function add(a: number, b: number) {
    return a + b
  }

  export function multiply(a: number, b: number) {
    return a * b
  }
}

import calc = MathUtils

console.log(calc.add(1, 2))  // 3
console.log(calc.multiply(3, 4))  // 12
```

## 命名空间与模块

```typescript [namespace-vs-module.ts]
// 命名空间（不推荐用于新项目）
namespace MyLib {
  export class User {
    constructor(public name: string) {}
  }

  export function createUser(name: string) {
    return new User(name)
  }
}

// 模块（推荐）
export class User {
  constructor(public name: string) {}
}

export function createUser(name: string) {
  return new User(name)
}

// 使用模块
import { User, createUser } from './MyLib'
```

## 第三方库命名空间

```typescript [third-party-namespace.ts]
// 声明第三方库命名空间
declare namespace jQuery {
  interface AjaxSettings {
    method?: 'GET' | 'POST'
    url: string
    data?: any
  }

  function ajax(settings: AjaxSettings): Promise<any>
  function get(url: string): Promise<any>
  function post(url: string, data: any): Promise<any>
}

// 使用
jQuery.ajax({
  method: 'GET',
  url: '/api/users'
})

jQuery.get('/api/users')
jQuery.post('/api/users', { name: '张三' })
```

## 命名空间合并

```typescript [namespace-merge.ts]
// 声明合并
namespace Animals {
  export class Dog {
    bark() {
      console.log('汪汪')
    }
  }
}

namespace Animals {
  export class Cat {
    meow() {
      console.log('喵喵')
    }
  }
}

// 使用
const dog = new Animals.Dog()
const cat = new Animals.Cat()

dog.bark()
cat.meow()

// 函数与命名空间合并
function buildLabel(name: string): string {
  return buildLabel.prefix + name + buildLabel.suffix
}

namespace buildLabel {
  export let prefix = 'Hello, '
  export let suffix = '!'
}

console.log(buildLabel('张三'))  // Hello, 张三!
```

## 枚举与命名空间

```typescript [enum-namespace.ts]
// 枚举与命名空间合并
enum Color {
  Red,
  Green,
  Blue
}

namespace Color {
  export function mix(c1: Color, c2: Color): Color {
    return ((c1 + c2) % 3) as Color
  }

  export function toString(c: Color): string {
    return Color[c]
  }
}

console.log(Color.mix(Color.Red, Color.Green))  // 1 (Green)
console.log(Color.toString(Color.Blue))  // 'Blue'
```

::: danger 注意
- 命名空间在 ES 模块中不推荐使用
- 新项目优先使用 ES 模块
- 命名空间主要用于组织全局代码
- 第三方库类型声明可能使用命名空间
:::
