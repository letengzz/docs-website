# 配置CSS代码检查工具

## 配置VSCode

在.vscode中添加并修改：

```json [extensions.json]
{
  "recommendations": [
    "Vue.volar",
    "vitest.explorer",
    "ms-playwright.playwright",
    "dbaeumer.vscode-eslint",
    "EditorConfig.EditorConfig",
    "prettier.prettier-vscode",
    "stylelint.vstylelint" // [!code focus] [!code highlight]
  ]
}
```

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

