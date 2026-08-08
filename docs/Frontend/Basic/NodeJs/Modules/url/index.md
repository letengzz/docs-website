# url 模块

url 模块用于解析和拼接 URL 地址。

## 获取 URL 路径

```javascript
const url = require('url')

const myUrl = 'https://www.example.com/path?name=zhangsan&age=18'

// 传统方式：url.parse
const parsed = url.parse(myUrl, true)
console.log(parsed.pathname)   // /path
console.log(parsed.query)      // { name: 'zhangsan', age: '18' }

// 现代方式：URL 类（推荐）
const u = new URL(myUrl)
console.log(u.pathname)                              // /path
console.log(u.searchParams.get('name'))              // zhangsan
```

## 查询字符串

传统方式：

```javascript
const parsed = url.parse('https://www.example.com/path?name=zhangsan', true)
console.log(parsed.query.name) // zhangsan
```

另一种方式（URLSearchParams）：

```javascript
const u = new URL('https://www.example.com/path?name=zhangsan&age=18')
console.log(u.searchParams.get('name')) // zhangsan
console.log(u.searchParams.get('age'))  // 18
```

::: tip
新代码推荐使用全局 `URL` 和 `URLSearchParams`，`url.parse` 属于历史 API，部分场景已标记弃用。
:::

