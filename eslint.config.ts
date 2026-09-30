import tseslint from 'typescript-eslint';
import pluginJs from '@eslint/js';
import globals from 'globals';

export default tseslint.config(
  {
    ignores: [
      '**/node_modules/**',
      '**/.vitepress/dist/**',
      '**/.vitepress/cache/**',
      '**/*.md',
    ],
  },
  pluginJs.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ['**/*.ts', '**/*.mts', '**/*.cts'],
    languageOptions: {
      globals: {
        ...globals.node,
      },
    },
    rules: {
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
      '@typescript-eslint/consistent-type-imports': 'error',
      '@typescript-eslint/no-namespace': 'off',
      '@typescript-eslint/triple-slash-reference': 'off',
    },
  },
  {
    // utils/ 下的 Node 脚本（.mjs）也需要 node 全局变量（console、process 等）
    files: ['**/*.mjs', '**/*.js', '**/*.cjs'],
    languageOptions: {
      globals: {
        ...globals.node,
      },
    },
  },
  {
    // 收窄到代码扩展名：`**/*.config.*` 会把 `ui.config.json` 这类 JSON 配置也扫进来，
    // 而 JSON 不是 JS 语法，解析必报错（project/Base/NuxtTemplate/scripts/fixture/ui.config.json 即为此例）。
    files: ['**/*.config.{js,mjs,cjs,ts,mts,cts}', 'eslint.config.*'],
    rules: {
      '@typescript-eslint/no-require-imports': 'off',
    },
  },
);
