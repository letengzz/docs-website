# 代码规范

代码规范让团队写出的代码“像一个人写的”：风格统一、命名清晰、低级错误被尽早拦截。前端代码规范由四件套组成：**EditorConfig（编辑器统一）→ Prettier（格式化）→ ESLint（质量规则）→ stylelint（样式规则）**。

## 规范四件套

| 工具 | 职责 | 配置位置 |
| --- | --- | --- |
| EditorConfig | 缩进、换行、编码统一 | `.editorconfig` |
| Prettier | 代码格式化（引号、分号、宽度） | `.prettierrc` + `.prettierignore` |
| ESLint | 代码质量规则（未用变量、危险语法） | `eslint.config.js`（flat config） |
| stylelint | CSS/SCSS 规范（顺序、单位、命名） | `stylelint.config.js` |

## EditorConfig

```ini [.editorconfig]
root = true

[*]
charset = utf-8
indent_style = space
indent_size = 2
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
```

## Prettier

```json [.prettierrc]
{
  "semi": false,
  "singleQuote": true,
  "printWidth": 100,
  "trailingComma": "all"
}
```

```shell
pnpm add -D prettier
pnpm exec prettier --write "src/**/*.{js,ts,vue,css}"
```

::: tip 格式化交给工具
不要手写格式！让 Prettier 在保存时自动格式化（VS Code 配置 `editor.formatOnSave`），并配合 lint-staged 在提交时兜底。
:::

## ESLint（flat config，v9+/v10）

ESLint 10 起 **flat config（`eslint.config.js`）是唯一配置方式**，旧 `.eslintrc` 已彻底移除。

```shell
pnpm add -D eslint eslint-plugin-vue typescript-eslint @vue/eslint-config-typescript
```

```js [eslint.config.js]
import eslintPluginVue from 'eslint-plugin-vue'
import tseslint from 'typescript-eslint'

export default tseslint.config(
  { ignores: ['dist/**', 'node_modules/**'] },
  ...tseslint.configs.recommended,
  ...eslintPluginVue.configs['flat/recommended'],
  {
    files: ['**/*.vue'],
    languageOptions: {
      parserOptions: { parser: tseslint.parser },
    },
  },
  {
    rules: {
      'no-unused-vars': 'error',
      'vue/multi-word-component-names': 'off',
      'vue/no-unused-components': 'warn',
    },
  },
)
```

```json [package.json]
{
  "scripts": {
    "lint": "eslint .",
    "lint:fix": "eslint . --fix"
  }
}
```

## stylelint

```shell
pnpm add -D stylelint stylelint-config-standard
```

```js [stylelint.config.js]
export default {
  extends: ['stylelint-config-standard'],
  rules: {
    'declaration-block-no-redundant-longhand-properties': null,
    'no-descending-specificity': null,
  },
}
```

## 常用规则建议

| 类别 | 规则 | 说明 |
| --- | --- | --- |
| 变量 | `no-unused-vars` | 未使用变量直接报错 |
| 危险操作 | `no-eval` | 禁止 eval |
| 相等判断 | `eqeqeq` | 强制 `===` |
| 未处理异步 | `no-floating-promises` | Promise 必须处理 |
| 命名 | `camelcase` | 变量驼峰命名 |
| Vue | `vue/multi-word-component-names` | 组件名 ≥ 2 个词 |
| 类型 | `@typescript-eslint/no-explicit-any` | 避免滥用 any |

::: danger 常见错误
1. **ESLint 与 Prettier 规则冲突**：格式化结果被 lint 报错；用 `eslint-config-prettier` 关掉冲突规则。
2. **只装不跑**：CI 里不执行 lint，规范形同虚设。
3. **`--fix` 不检查剩余问题**：fix 后要再跑一次确认无 error。
4. **全局禁用规则**：`/* eslint-disable */` 滥用会让门禁失去意义；局部豁免要写理由。
5. **忽略文件不全**：`dist`、`node_modules`、lockfile 要进 ignore，否则 lint 巨慢。
:::

## 验证方式

1. 运行 `pnpm lint`，确认 0 error、0 warning。
2. 故意写 `var x = 1` + 未使用变量，确认 lint 报错并可 `--fix` 自动修复。
3. 运行 `pnpm exec prettier --check .`，确认格式全部符合。
4. 保存文件时触发自动格式化，确认格式化结果与 CI 一致。

## 参考资料

- ESLint 文档：https://eslint.org/docs/latest/
- Prettier 文档：https://prettier.io/docs/en/
- stylelint 文档：https://stylelint.io/
- EditorConfig：https://editorconfig.org/
- typescript-eslint：https://typescript-eslint.io/
