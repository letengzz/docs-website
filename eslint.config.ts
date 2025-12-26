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
    files: ['**/*.config.*', 'eslint.config.*'],
    rules: {
      '@typescript-eslint/no-require-imports': 'off',
    },
  },
);
