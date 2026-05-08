# 模板引擎

模板引擎是用于将数据与 HTML 模板结合生成动态网页的工具。

## 常用模板引擎

### 1. EJS

- 官网: https://ejs.co/
- 特点：使用 JavaScript 语法，学习成本低

```js [ejs-setup.js]
app.set('view engine', 'ejs')
```

### 2. Pug (Jade)

- 官网: https://pugjs.org/
- 特点：缩进语法，简洁优雅

```js [pug-setup.js]
app.set('view engine', 'pug')
```

### 3. Handlebars

- 官网: https://handlebarsjs.com/
- 特点：逻辑less 模板，安全性高

```js [handlebars-setup.js]
const exphbs = require('express-handlebars')
app.engine('handlebars', exphbs())
app.set('view engine', 'handlebars')
```

## 模板引擎对比

| 特性 | EJS | Pug | Handlebars |
|------|-----|-----|------------|
| 语法 | JavaScript | 缩进 | 自定义标签 |
| 学习曲线 | 低 | 中 | 中 |
| 性能 | 良好 | 良好 | 优秀 |
| 灵活性 | 高 | 中 | 低 |

## 选择建议

- **EJS**：适合熟悉 HTML 的开发者
- **Pug**：适合追求简洁的开发者
- **Handlebars**：适合需要严格分离逻辑的项目

::: tip 提示
Express 支持多种模板引擎，可以根据项目需求选择
:::
