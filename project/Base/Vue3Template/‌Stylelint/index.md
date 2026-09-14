# 配置CSS代码检查工具

## 配置VSCode

在.vscode中添加并修改：

```json [extensions.json]
{
  "recommendations": [
    "Vue.vue-official",
    "vitest.explorer",
    "ms-playwright.playwright",
    "dbaeumer.vscode-eslint",
    "EditorConfig.EditorConfig",
    "esbenp.prettier-vscode",
    "stylelint.vscode-stylelint" // [!code focus] [!code highlight]
  ]
}
```

::: danger 扩展 ID 写错会静默失效
`extensions.json` 里的 ID 只要格式合法就不会报错，**但写错发布者时「推荐安装」会找不到扩展，且不留任何提示**。下面是三个最容易写错的 ID：

| 容易写错 | 正确 ID | 说明 |
| --- | --- | --- |
| `prettier.prettier-vscode` | `esbenp.prettier-vscode` | Prettier 的发布者是个人账号 `esbenp`，不是 `prettier` |
| `stylelint.vstylelint` | `stylelint.vscode-stylelint` | 中间是 `vscode-`，不是 `v` |
| `Vue.volar` | `Vue.vue-official` | 官方 Vue 扩展已更名（旧 ID `Vue.volar`，若失效请用新 ID） |

判断方法：把 ID 拼进市场地址 `https://marketplace.visualstudio.com/items?itemName=<ID>`，能打开才说明 ID 正确。
:::

```json [settings.json]
{
  "editor.formatOnSave": false,
  "editor.codeActionsOnSave": {
    "source.fixAll.stylelint": "explicit",
    "source.fixAll": "explicit"
  },
  "stylelint.validate": [
    "css",
    "scss",
    "sass",
    "less",
    "postcss",
    "vue",
    "html",
    "markdown",
    "xml",
    "jsx",
    "tsx",
    "svelte"
  ],
  "stylelint.snippet": ["css", "scss", "vue"],
  "files.associations": {
    "*.vue": "vue",
    "*.scss": "scss"
  }
}
```

## 安装

::: code-group

```shell [sass]
pnpm add sass postcss postcss-html postcss-scss stylelint stylelint-config-recess-order stylelint-config-standard -D
```

```shell [less]
pnpm add less postcss postcss-html postcss-less stylelint stylelint-config-recess-order stylelint-config-standard -D
```

:::

## 配置文件

```js [stylelint.config.mjs]
/** @type {import('stylelint').Config} */
export default {
  // stylelint-config-standard 基础配置
  // stylelint-config-recess-order 样式顺序
  extends: ['stylelint-config-standard', 'stylelint-config-recess-order'],
  // 不同文件类型用不同解析器
  overrides: [
    {
      files: ['**/*.(css|html|vue)'],
      customSyntax: 'postcss-html',
    },
    // 选less可以注释scss
    {
      files: ['*.less', '**/*.less'],
      customSyntax: 'postcss-less',
    },
    // 选sass可以注释上面的less
    {
      files: ['*.scss', '**/*.scss'],
      customSyntax: 'postcss-scss',
      rule: {
        'scss/percent-placeholder-pattern': null,
        'scss/at-mixin-pattern': null,
      },
    },
  ],
  rules: {
    // 'prettier/prettier': true,
    'media-feature-range-notation': null,
    'selector-not-notation': null,
    'import-notation': null,
    'function-no-unknown': null,
    'selector-class-pattern': null,
    'selector-pseudo-class-no-unknown': [
      true,
      {
        ignorePseudoClasses: ['global', 'deep'],
      },
    ],
    'selector-pseudo-element-no-unknown': [
      true,
      {
        ignorePseudoElements: ['v-deep', ':deep'],
      },
    ],
    'at-rule-no-unknown': [
      true,
      {
        ignoreAtRules: [
          'tailwind',
          'apply',
          'variants',
          'responsive',
          'screen',
          'function',
          'if',
          'each',
          'include',
          'mixin',
          'extend',
          'use',
        ],
      },
    ],
    'no-empty-source': null,
    'named-grid-areas-no-invalid': null,
    'no-descending-specificity': null,
    'font-family-no-missing-generic-family-keyword': null,
    'rule-empty-line-before': [
      'always',
      {
        ignore: ['after-comment', 'first-nested'],
      },
    ],
    'unit-no-unknown': [true, { ignoreUnits: ['rpx'] }],
    'order/order': [
      [
        'dollar-variables',
        'custom-properties',
        'at-rules',
        'declarations',
        {
          type: 'at-rule',
          name: 'supports',
        },
        {
          type: 'at-rule',
          name: 'media',
        },
        'rules',
      ],
      { severity: 'error' },
    ],
  },
  ignoreFiles: ['**/*.js', '**/*.jsx', '**/*.tsx', '**/*.ts'],
}
```

## 新增脚本

```json [package.json]
{
    "scripts": {
        // ...
        "lint:stylelint": "stylelint  \"**/*.{css,scss,less,vue,html}\" --fix"
    }
}
```

## 忽略文件

```tex [.stylelintignore]
/dist/*
/public/*
```

