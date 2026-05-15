# Vue3 搭建基础环境

由于vite脚手架要禁止\*.cjs 和 eslint版本升级废弃rc配置文件， 故重新搭建。

核心采用antfu大神预设配置 替代prettier和eslint设置，保留stylelint原因是暂时antfu不支持。

## 前置条件

### node版本

node 最好>20 因为eslint9的需要 本次项目node为20.10.0

![image-20250107150058871](../assets/image-20250107150058871.png)

### vscode 插件

vscode 插件 eslint prettier stylelint unocss vue-official postcss

![image-20240828103527225](../assets/image-20240828103527225.png)

![image-20240828103542672](../assets/image-20240828103542672.png)

![image-20240828103556492](../assets/image-20240828103556492.png)

![image-20240828103620621](../assets/image-20240828103620621.png)

![image-20240828103706879](../assets/image-20240828103706879.png)

![image-20240828140147090](../assets/image-20240828140147090.png)

### git

安装官方git 用代码仓库管理

```shell
git init
```

## 创建项目

使用官方命令创建项目，然后清空项目

```shell
npm create vue
```

![image-20250107154112524](../assets/image-20250107154112524.png)

## .vscode 配置文件

> 用于保存带代码格式化

生成.vscode/settings.json 修改：

```json
{
  "typescript.tsdk": "./node_modules/typescript/lib",
  // "npm.packageManager": "pnpm",
  // "editor.formatOnSave": true,
  "editor.tabSize": 2,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  // 保存文件缓慢时，可以考虑开启以下 3 行配置。
  "vue.server.maxOldSpaceSize": 4096,
  "vue.server.hybridMode": true,
  "typescript.tsserver.maxTsServerMemory": 4096,
  "files.eol": "\n",
  "editor.guides.bracketPairs": true,
  "editor.bracketPairColorization.enabled": true,
  "vue.inlayHints.missingProps": true,
  "vue.autoInsert.dotValue": true,
  "explorer.copyRelativePathSeparator": "/",
  "search.exclude": {
    "**/node_modules": true,
    "**/*.log": true,
    "**/*.log*": true,
    "**/bower_components": true,
    "**/dist": true,
    "**/elehukouben": true,
    "**/.git": true,
    "**/.gitignore": true,
    "**/.svn": true,
    "**/.DS_Store": true,
    "**/.idea": true,
    "**/.vscode": false,
    "**/pnpm i.lock": true,
    "**/tmp": true,
    "out": true,
    "dist": true,
    "node_modules": true,
    "CHANGELOG.md": true,
    "examples": true,
    "res": true,
    "screenshots": true,
    "pnpm i-error.log": true,
    "**/.pnpm i": true
  },
  "files.exclude": {
    "**/.cache": true,
    "**/.editorconfig": true,
    "**/.eslintcache": true,
    "**/bower_components": true,
    "**/.idea": true,
    "**/tmp": true,
    "**/.git": true,
    "**/.svn": true,
    "**/.hg": true,
    "**/CVS": true,
    "**/.DS_Store": true
  },
  "files.watcherExclude": {
    "**/.git/objects/**": true,
    "**/.git/subtree-cache/**": true,
    "**/.vscode/**": true,
    "**/node_modules/**": true,
    "**/tmp/**": true,
    "**/bower_components/**": true,
    "**/dist/**": true,
    "**/pnpm i.lock": true
  },
  "eslint.useFlatConfig": true,
  "stylelint.enable": true,
  "stylelint.validate": ["css", "less", "postcss", "scss", "vue", "sass"],
  "path-intellisense.mappings": {
    "@/": "${workspaceRoot}/src"
  },
  "i18n-ally.localesPaths": ["src/locales/lang"],
  "i18n-ally.keystyle": "nested",
  "i18n-ally.sortKeys": true,
  "i18n-ally.namespace": true,
  "i18n-ally.pathMatcher": "{locale}/{namespaces}.{ext}",
  "i18n-ally.enabledParsers": ["json"],
  "i18n-ally.sourceLanguage": "en",
  "i18n-ally.displayLanguage": "zh-CN",
  "i18n-ally.enabledFrameworks": ["vue", "react"],
  // Disable the default formatter, use eslint instead
  "prettier.enable": false,
  "editor.formatOnSave": false,

  // Auto fix
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit",
    "source.organizeImports": "never",
    "source.fixAll.stylelint": "explicit"
  },

  // Silent the stylistic rules in you IDE, but still auto fix them
  "eslint.rules.customizations": [
    { "rule": "style/*", "severity": "off", "fixable": true },
    { "rule": "format/*", "severity": "off", "fixable": true },
    { "rule": "*-indent", "severity": "off", "fixable": true },
    { "rule": "*-spacing", "severity": "off", "fixable": true },
    { "rule": "*-spaces", "severity": "off", "fixable": true },
    { "rule": "*-order", "severity": "off", "fixable": true },
    { "rule": "*-dangle", "severity": "off", "fixable": true },
    { "rule": "*-newline", "severity": "off", "fixable": true },
    { "rule": "*quotes", "severity": "off", "fixable": true },
    { "rule": "*semi", "severity": "off", "fixable": true }
  ],
  "css.validate": false,
  "less.validate": false,
  "scss.validate": false,
  // Enable eslint for all supported languages
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "typescript",
    "typescriptreact",
    "vue",
    "html",
    "markdown",
    "json",
    "jsonc",
    "yaml",
    "toml",
    "xml",
    "gql",
    "graphql",
    "astro",
    "css",
    "less",
    "scss",
    "pcss",
    "postcss"
  ]
}
```

## 调整项目

typescript 不能识别 .vue 文件

解决方法：可以在env.d.ts 文件中添加以下代码，如果没有 vite-env.d.ts ，可以自己新建一个 xxx.d.ts 类型的文件即可

```typescript
/// <reference types="vite/client" />
declare module '*.vue' {
  import { ComponentOptions } from 'vue'
  const componentOptions: ComponentOptions
  export default componentOptions
}
```



## UnoCSS

添加依赖：

```shell
npm install -D unocss @iconify-json/ep @unocss/preset-rem-to-px @unocss/transformer-directives
```

引入UnoCSS：

> vite.config.ts

```typescript
//unocss vite插件
import UnoCSS from 'unocss/vite'

// https://vite.dev/config/
export default defineConfig({
  // ...
  plugins: [
    // ...
    UnoCSS(),
  ],
})
```

配置UnoCSS：

> uno.config.ts

```typescript
//uno.config.ts

//预设rem转px
import presetRemToPx from '@unocss/preset-rem-to-px'
//transformerDirectives 可以使用 @apply @screen theme函数
import transformerDirective from '@unocss/transformer-directives'
import {
  defineConfig,
  presetAttributify,
  presetUno,
  transformerVariantGroup,
  presetIcons,
} from 'unocss'

export default defineConfig({
  presets: [
    presetAttributify(),
    presetUno(),
    // 现在mt-1会转换为 margin-top: 1px
    presetRemToPx({
      baseFontSize: 4,
    }),
    //自动引入图标配置
    presetIcons({
      scale: 1.2,
      warn: true,
    }),
  ],
  transformers: [transformerDirective(), transformerVariantGroup()],
  //自定义配置
  rules: [
    //自定义配置
    //以下官网规则可自定义转换
    // [/^m-(\d+)$/, ([, d]) => ({ margin: `${d / 4}rem` })],
    // [/^p-(\d+)$/, match => ({ padding: `${match[1] / 4}rem` })],
  ],
  //自定义属性 一个属性可以对应多个unocss类值
  shortcuts: {
    //垂直水平居中
    'flex-center': 'flex justify-center items-center',
    //放在最后
    'flex-col-end': 'flex justify-end items-center',
    //垂直居中
    'flex-middle': 'flex items-center',
    //分开两边
    'flex-between': 'flex justify-between items-center',
    //竖直居中
    'flex-col-center': 'flex flex-col justify-center',
  },
})
```

全局配置：

> main.ts

```typescript
//eslint-disable-next-line import/no-unresolved
import 'virtual:uno.css' // 引入 uno.css
```

使用：

> 使用图标时：`i前缀-ep图库名:lock图标名称`

```vue
<template>
  <div>
    <h1>UnoCSS</h1>
    <div class="box"></div>
    <hr />
    <div class="h-100 w-100 bg-red-800 text-30 text-blue hover:text-black">小猫米</div>
    <hr />
    <div class="box2">小猫咪</div>
    <hr />
    <div h100 w100 bg-blueGray text-fuchsia mt10 py20>小猫咪</div>
    <hr />
    <div class="wrap" w200 h100 flex-center gap10>
      <div w20 h20 bg-blue></div>
      <div w20 h20 bg-blue></div>
      <div w20 h20 bg-blue></div>
    </div>
    <hr />
    <div i-ep:dish></div>
    <i w100 h100 block i-ep:switch-button></i>
  </div>
</template>

<script setup></script>

<style lang="scss" scoped>
.box {
  width: 100px;
  height: 100px;
  background-color: salmon;
}
.box2 {
  @apply h-100 w-100 bg-red-800 text-30 text-blue hover:text-black;
}
.wrap {
  border: 1px solid #ddd;
}
</style>
```

## 采用antfu 组合prettier&eslint

配置网站：https://github.com/antfu/eslint-config/tree/feat/support-eslint-9?tab=readme-ov-file

先选一个unocss 免得后续再去安装unocss的@unocss/eslint-plugin

### 命令行界面 (CLI) 安装

空格选择 回车下一步

```js
npx @antfu/eslint-config@latest
```

![image-20250107173615864](../assets/image-20250107173615864.png)

### 安装依赖包

> "@antfu/eslint-config": "^2.27.3",
>
> "eslint": "^9.9.1",
>
> "eslint-plugin-format": "^0.1.2",
>
> "@unocss/eslint-plugin": "^0.62.3",

```js
npm i
```

### 配置文件

修改生成配置文件eslint.config.js为eslint.config.mjs 用于eslint规则校验

> eslint.config.mjs

```js
import antfu from '@antfu/eslint-config'

export default antfu({
  // @stylistic/eslint-plugin-plus
  stylistic: true,
  // eslint-plugin-format
  formatters: true,
  // unocss 检测&格式化 暂时注释 等配置了unocss再开放为true
  unocss: true,
  // vue的eslint配置
  vue: true,
  // 保存删除未引入的代码
  // isInEditor: false,
  // 9x版本 忽略文件这种配置方式 废弃掉eslintignore
  ignores: [
    '*.sh',
    'node_modules',
    '*.md',
    '*.woff',
    '*.ttf',
    '.idea',
    '/public',
    '/docs',
    '.husky',
    '.local',
    '/bin',
    'Dockerfile',
  ],
})
```

### 新增脚本

> package.json

```js
{
    "scripts": {
       // ...
      "lint": "eslint .",
      "lint:fix": "eslint . --fix"
    }
}
```

## 代码提交检查

Husky + Lint-staged + Commitlint + Commitizen + cz-git 来配置 Git 提交代码规范。

> 核心内容是配置 Husky 的 pre-commit 和 commit-msg 两个钩子:
>
> pre-commit：Husky + Lint-staged 整合实现 Git 提交前代码规范检测/格式化 (前提：ESlint + Prettier + Stylelint 代码统一规范)；
>
> commit-msg: Husky + Commitlint + Commitizen + cz-git 整合实现生成规范化且高度自定义的 Git commit message。

### husky

Husky 是 Git 钩子工具，可以设置在 git 各个阶段（`pre-commit`、`commit-msg` 等）触发。

官网https://typicode.github.io/husky 推荐安装指令

1. 前提条件 项目有.git 如果没有需要生成 有git的话不需要这一步

```shell
git init
```

2. 自动配置husky

```shell
npx husky-init
```

![image-20250107210102300](../assets/image-20250107210102300.png)

3. 安装husky 执行 `npm i`

```js
npm i
```

![image-20250107210141221](../assets/image-20250107210141221.png)

### Lint-staged 增量检测提交代码

lint-staged 是一个在 git add 到暂存区的文件运行 linters (ESLint/Prettier/StyleLint) 的工具，避免在 git commit 提交时在整个项目执行。

1. 安装：

```js
npm i lint-staged -D
```

2. 新建lint-staged.config.mjs 配置文件

> lint-staged.config.mjs

```js
/**  @type {import('lint-staged').Config} */
export default {
  '*.{js,jsx,ts,tsx}': ['eslint --fix'],
  '*.json': ['eslint --fix'],
  '*.vue': ['eslint --fix'],
  '*.{scss,less,styl,html}': ['stylelint --fix --allow-empty-input'],
  '*.md': ['prettier --write'],
}
```

3. 添加指令

> package.json

```json
"scripts": {
  // ...
  "lint:lint-staged": "lint-staged"
},
```

4. 文件`.husky/pre-commit`**修改提交前钩子命令**

npx命令会自动执行安装过的 lint-staged插件，从而执行lint-staged.config.mjs配置文件

```js
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npm run lint:lint-staged --allow-empty
```

![image-20240207143016869](../assets/image-20240207143016869.png)

### Commitlint

Commitlint 检查您的提交消息是否符合 Conventional commit format。

Commitlint 官网：https://commitlint.js.org/)

1. 安装：

```js
npm i @commitlint/cli @commitlint/config-conventional -D
```

2. 根目录创建 `commitlint.config.mjs` 配置文件：

> commitlint.config.mjs

```js
/** @type {import("@commitlint/types").UserConfig} */
export default {
  ignores: [(commit) => commit.includes('init')],
  extends: ['@commitlint/config-conventional'],
  rules: {
    'body-leading-blank': [2, 'always'],
    'footer-leading-blank': [1, 'always'],
    'header-max-length': [2, 'always', 108],
    'subject-empty': [2, 'never'],
    'type-empty': [2, 'never'],
    'subject-case': [0],
    'type-enum': [
      2,
      'always',
      [
        'feat', // 新增功能
        'fix', // 修复缺陷
        'docs', // 文档变更
        'style', // 代码格式（不影响功能，例如空格、分号等格式修正）
        'refactor', // 代码重构（不包括 bug 修复、功能新增）
        'perf', // 性能优化
        'test', // 添加疏漏测试或已有测试改动
        'build', // 构建流程、外部依赖变更（如升级 npm 包、修改 webpack 配置等）
        'ci', // 修改 CI 配置、脚本
        'revert', // 回滚 commit
        'chore', // 对构建过程或辅助工具和库的更改（不影响源文件、测试用例）
      ],
    ],
  },
}
```

3. 执行下面命令生成 `commint-msg` 钩子用于 git 提交信息校验

```js
npx husky add .husky/commit-msg "npx --no -- commitlint --edit $1"
```

![image-20240207142542813](../assets/image-20240207142542813.png)

### Commitizen

安装：

```shell
npm install --dev commitizen cz-vinyl
```

添加 `.czvinylrc` 文件：

```json
{
  "headerFormat": "{type}: {subject}",
  "commitTypes": [
    {
      "description": "一个新的功能",
      "value": "feat"
    },
    {
      "description": "一个BUG修复",
      "value": "fix"
    },
    {
      "description": "辅助工具更改或者无法分类的提交",
      "value": "chore"
    },
    {
      "description": "提高性能的代码更改",
      "value": "perf"
    },
    {
      "description": "不修复错误也不增加功能的重构代码",
      "value": "refactor"
    },
    {
      "description": "更新代码格式",
      "value": "style"
    },
    {
      "description": "添加测试用例",
      "value": "test"
    },
    {
      "description": "更新文档",
      "value": "docs"
    },
    {
      "description": "更新CI发版代码",
      "value": "ci"
    },
    {
      "description": "更新构建依赖等模块",
      "value": "build"
    }
  ],
  "skipScope": true,
  "skipTicketId": true,
  "subjectMaxLength": 70,
  "subjectMinLength": 3,
  "typeQuestion": "请选择一个提交类型：",
  "subjectQuestion": "请输入一个提交信息：",
  "bodyQuestion": "请输入一个提交详细内容（可跳过）："
}
```

在scripts中添加：

```shell
"scripts": {
   // ...
   "cz": "git-cz"
 },
 "config": {
   "commitizen": {
     "path": "cz-vinyl"
   }
 },
```

使用 `npm run cz` 运行：

![image-20250316110304316](../assets/image-20250316110304316.png)

## 调整Sass

注意：将自带的css文件删除。

引入样式：

> src/main.ts

```typescript
// 引入全局样式
import '@/styles/index.scss'
```

添加全局样式：

> src/styles/index.scss

```scss
// 全局样式
html,
body {
  padding: 0;
  margin: 0;
}

#app {
  height: 100vh;
}
```

添加全局scss函数：

> src/styles/mixin.scss

```scss
// 全局scss函数

@mixin wh($w, $h) {
  width: $w + px;
  height: $h + px;
}
```

添加全局变量样式：

> src/styles/variables.scss

```scss
// 全局变量样式
$blue: rgb(53 53 109);
$red: rgb(172 37 37);
```

调整vite：

> vite.config.ts

```typescript
export default defineConfig({
  // ...
  css: {
    // 预加载
    preprocessorOptions: {
      // 全局样式变量预注入
      scss: {
        additionalData: `
          @use "@/styles/variables.scss" as *;
          @use "@/styles/mixin.scss" as *;
        `,
      },
    },
  },
})
```

使用：

```vue
<script setup></script>

<template>
  <div>
    <h1 class="num">This is an about page {{ counter.count }}</h1>
  </div>
</template>

<style scoped lang="scss">
.num {
  @include wh(500, 500);

  color: $red;
}
</style>
```

## gzip压缩

安装：

```shell
npm i vite-plugin-compression -D
```

vite.config.ts配置：

```typescript
// gzip压缩
import viteCompression from 'vite-plugin-compression'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    // ...
    viteCompression({
      verbose: true, // 默认即可
      disable: false, // 开启压缩(不禁用)，默认即可
      deleteOriginFile: false, // 删除源文件
      threshold: 10240, // 压缩阈值，以字节为单位。如果一个资源比这个值小，它就不会被压缩。默认是 10240
      algorithm: 'gzip', // 压缩算法，默认是 gzip
      ext: '.gz', // 文件类型，默认是 .gz
    }),
  ],
})
```

## 打包进度

插件网站：https://www.npmjs.com/package/vite-plugin-progress

安装：

```shell
npm i vite-plugin-progress -D
```

vite.config.ts配置：

```typescript
// 打包进度
import progress from 'vite-plugin-progress'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    // ...
    progress(),
  ],
})
```

## 自动重启

插件网站：https://www.npmjs.com/package/vite-plugin-restart

安装：

```shell
npm i vite-plugin-restart -D
```

vite.config.ts配置：

```typescript
// 自动重启
import viteRestart from 'vite-plugin-restart'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    // ...
    viteRestart({
      restart: ['./*.config.[jt]s', './**/config/*.[jt]s', './*.config.mjs'],
    }),
  ],
})
```

## Svg配置

插件网站：https://www.npmjs.com/package/vite-svg-loader

安装：

```shell
npm i vite-svg-loader -D
```

vite.config.ts配置：

```typescript
// svg加载
import svgLoader from 'vite-svg-loader'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    // ...
    svgLoader({
      defaultImport: 'url', // default 'file' or 'url'
      svgo: true,
    }),
  ],
})
```

## 分析插件

官网：https://www.npmjs.com/package/rollup-plugin-visualizer

安装：

```shell
npm i rollup-plugin-visualizer -D
```

vite.config.ts配置：

```typescript
import { visualizer } from 'rollup-plugin-visualizer'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    // ...
    visualizer({
      open: true, //注意设置true
      gzipSize: true,
      brotliSize: true,
    }),
  ],
})
```

## rem转换

官网：https://www.npmjs.com/package/vite-plugin-px2rem#vite-plugin-px2rem

安装：

```shell
npm i vite-plugin-px2rem -D
```

> vite-plugin-px2rem rem转px插件

vite.config.ts配置：

```typescript
import { px2rem } from 'vite-plugin-px2rem'
// https://vite.dev/config/
export default defineConfig({
  plugins: [
    //.
    px2rem({
      width: 750, //设计稿宽度
      rootFontSize: 16, //根字体大小
    }),
  ],
})
```

## 图片压缩

官网：https://www.npmjs.com/package/vite-plugin-image-optimizer

安装：

```shell
npm add sharp svgo -D
npm add vite-plugin-image-optimizer -D
```

vite.config.ts配置：

```typescript
// 图片压缩
import { ViteImageOptimizer } from 'vite-plugin-image-optimizer'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    // ...
    ViteImageOptimizer({
      png: {
        // https://sharp.pixelplumbing.com/api-output#png
        quality: 60,
      },
      jpeg: {
        // https://sharp.pixelplumbing.com/api-output#jpeg
        quality: 60,
      },
      jpg: {
        // https://sharp.pixelplumbing.com/api-output#jpeg
        quality: 60,
      },
    }),
  ],
})
```

## 打包拆分 & 小图片转base64

官网：https://cn.vitejs.dev/config/build-options.html#build-assetsinlinelimit

vite.config.ts配置：

```typescript
// https://vite.dev/config/
export default defineConfig({
  build: {
    // 10kb以下 转Base64
    assetsInlineLimit: 1024 * 10,
    // chunkSizeWarningLimit:1500, //配置文件大小提醒限制 默认为500
    rollupOptions: {
      output: {
        // 每个node_modules下的文件单独打包
        manualChunks(id: string) {
          if (id.includes('node_modules')) {
            // return 'vendor' //第三方依赖合并在一起
            // 抽离第三方依赖
            // return id.toString().split('node_modules/.pnpm/')[1].split('/')[0].toString()
            return id.toString().split('node_modules/')[1].split('/')[0].toString()
          }
          return undefined
        },
        // 用于从入口点创建的块的打包输出格式[name]表示文件名，[hash]表示该文件hash值
        entryFileNames: '../assets/js/[name].[hash].js', // 用于命名代码拆分时创建的共享的输出命名
        chunkFileNames: '../assets/js/[name].[hash].js', // 用于输出静态资源的命名，[ext]表示文件拓展名
        assetFileNames: '../assets/[ext]/[name].[hash].[ext]',
      },
    },
  },
  // ...
})
```

## 配置环境变量

官网：https://cn.vitejs.dev/guide/env-and-mode.html#intellisense

在根目录下新建.env开头的文件：

- .env：所有环境默认加载
- .env.development：开发环境默认加载
- .env.production：生产环境默认加载
- .env.check：自定义环境

![image-20250113174344475](../assets/image-20250113174344475.png)

修改package.json命令：

```json
"scripts": {
    // ...
    "build:check": "vite build --mode check",
    // ...
},
```

新建 `build/utils.ts`文件处理环境文件变量：

```typescript
/* eslint-disable node/prefer-global/process */
// Read all environment variable configuration files to process.env
export function wrapperEnv(envConf: any) {
  const ret: any = {}

  for (const envName of Object.keys(envConf)) {
    let realName = envConf[envName].replace(/\\n/g, '\n')
    realName = realName === 'true' ? true : realName === 'false' ? false : realName

    if (envName === 'VITE_PORT') {
      realName = Number(realName)
    }
    if (envName === 'VITE_PROXY' && realName) {
      try {
        realName = JSON.parse(realName.replace(/'/g, '"'))
      } catch (error) {
        realName = ''
        console.error(error)
      }
    }
    ret[envName] = realName
    if (typeof realName === 'string') {
      process.env[envName] = realName
    } else if (typeof realName === 'object') {
      process.env[envName] = JSON.stringify(realName)
    }
  }
  return ret
}
```

vite.config.ts配置：

```typescript
/* eslint-disable node/prefer-global/process */
import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'

// 自动引入样式
import { useBuild } from './build/build'
import { usePlugins } from './build/plugins'
import { useServer } from './build/server'
import { wrapperEnv } from './build/utils'

// https://vite.dev/config/
export default defineConfig(({ command, mode }) => {
  // 模式
  const isBuild = command === 'build'
  console.log('isBuild', isBuild)
  // 获取当前文件夹地址 current working directory
  const root = process.cwd()
  // 读取包含VITE_开头的环境变量
  const env = loadEnv(mode, root)
  // 环境变量值转换
  const viteEnv = wrapperEnv(env)
  return {
    // ...
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    css: {
      // 预加载
      preprocessorOptions: {
        // 全局样式变量预注入
        scss: {
          additionalData: `
            @use "@/styles/variables.scss" as *;
            @use "@/styles/mixin.scss" as *;
          `,
        },
      },
    },
  }
})
```

> tsconfig.app.json

```json
{
  "extends": "@vue/tsconfig/tsconfig.dom.json",
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.app.tsbuildinfo",

    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["types", "src/**/*", "src/**/*.vue"],
  "exclude": ["src/**/__tests__/*"]
}
```

> tsconfig.node.json

```json
{
  "extends": "@tsconfig/node22/tsconfig.json",
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.node.tsbuildinfo",

    "module": "ESNext",
    "moduleResolution": "Bundler",
    "types": ["node"],
    "noEmit": true
  },
  "include": [
    "vite.config.*",
    "vitest.config.*",
    "cypress.config.*",
    "nightwatch.conf.*",
    "playwright.config.*",
    "build",
    "types"
  ]
}
```

将env.d.ts移动到types

```typescript
/// <reference types="vite/client" />
declare module '*.vue' {
  import type { ComponentOptions } from 'vue'

  const componentOptions: ComponentOptions
  export default componentOptions
}

interface ImportMetaEnv {
  readonly VITE_APP_TITLE: string
  // 更多环境变量...
  readonly VITE_CHECK: boolean
  readonly VITE_BASE_URL: string
  readonly VITE_IS_PORXY: boolean
  readonly VITE_OPEN_GIZP: boolean
  readonly VITE_OPEN_VISUALIZER: boolean
  readonly VITE_PORT: number
  readonly VITE_OPEN_MOCK: boolean
  readonly VITE_MOCK_ALL: boolean
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

interface ViteEnv extends ImportMetaEnv {}
```

## 根据不同环境使用不同插件

官网：https://cn.vitejs.dev/config/#conditional-config

vite.config.ts 抽离出插件，打包配置server配置等复杂配置：

> vite.config.ts

```typescript
/* eslint-disable node/prefer-global/process */
import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'

// 自动引入样式
import { useBuild } from './build/build'
import { usePlugins } from './build/plugins'
import { useServer } from './build/server'
import { wrapperEnv } from './build/utils'

// https://vite.dev/config/
export default defineConfig(({ command, mode }) => {
  // 模式
  const isBuild = command === 'build'
  console.log('isBuild', isBuild)
  // 获取当前文件夹地址 current working directory
  const root = process.cwd()
  // 读取包含VITE_开头的环境变量
  const env = loadEnv(mode, root)
  // 环境变量值转换
  const viteEnv = wrapperEnv(env)
  return {
    plugins: usePlugins(isBuild, viteEnv),
    build: useBuild(viteEnv),
    server: useServer(viteEnv),
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    css: {
      // 预加载
      preprocessorOptions: {
        // 全局样式变量预注入
        scss: {
          additionalData: `
            @use "@/styles/variables.scss" as *;
            @use "@/styles/mixin.scss" as *;
          `,
        },
      },
    },
  }
})
```

> build/server.ts

```typescript
// 服务器选项

export function useServer(viteEnv: ViteEnv) {
  return {
    // 监听所有公共ip
    // host: '0.0.0.0',
    cors: true,
    port: viteEnv.VITE_PORT,
    proxy: {
      // 前缀
      '/dev': {
        target: 'http://www.example.com',
        changeOrigin: true,
        // 前缀重写
        rewrite: (path: string) => path.replace(/^\/api/, '/api'),
      },
    },
  }
}
```

> build/build.ts

```typescript
// 打包选项

export function useBuild(viteEnv: ViteEnv) {
  const { VITE_CHECK } = viteEnv
  return {
    // 10kb以下，转Base64
    assetsInlineLimit: 1024 * 10,
    // chunkSizeWarningLimit: 1500,//配置文件大小提醒限制，默认500
    rollupOptions: {
      output: {
        // 每个node_modules模块分成一个js文件
        manualChunks(id: string) {
          if (id.includes('node_modules')) {
            return VITE_CHECK
              ? id.toString().split('node_modules/.pnpm/')[1].split('/')[0].toString()
              : 'vendor'
          }
          return undefined
        },
        // 用于从入口点创建的块的打包输出格式[name]表示文件名,[hash]表示该文件内容hash值
        entryFileNames: '../assets/js/[name].[hash].js', // 用于命名代码拆分时创建的共享块的输出命名
        chunkFileNames: '../assets/js/[name].[hash].js', // 用于输出静态资源的命名，[ext]表示文件扩展名
        assetFileNames: '../assets/[ext]/[name].[hash].[ext]',
      },
    },
  }
}
```

> build/plugins/index.ts

```typescript
// 插件配置 总入口
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'

import { px2remPlugin } from './px2rem'
import { svgLoaderPlugin } from './svgLoader'
import { UnoCSSPlugin } from './UnoCSS'
import { visualizerPlugin } from './visualizer'
import { viteCompressionPlugin } from './viteCompression'
import { ViteImageOptimizerPlugin } from './ViteImageOptimizer'
import { ViteRestartPlugin } from './ViteRestart'
import { VueDevToolsPlugin } from './VueDevTools'

export function usePlugins(isBuild: boolean, viteEnv: ViteEnv) {
  const { VITE_OPEN_GIZP, VITE_OPEN_VISUALIZER } = viteEnv

  const plugins = [vue(), vueJsx()]

  // 开发环境&生产环境加载的插件
  plugins.push(px2remPlugin())
  plugins.push(svgLoaderPlugin())
  plugins.push(UnoCSSPlugin())

  // 开发需要
  if (!isBuild) {
    plugins.push(VueDevToolsPlugin())
    plugins.push(ViteRestartPlugin())
  }

  // 生产环境需要
  if (isBuild) {
    // 图片压缩
    plugins.push(ViteImageOptimizerPlugin())

    VITE_OPEN_GIZP && plugins.push(viteCompressionPlugin())
    VITE_OPEN_VISUALIZER && plugins.push(visualizerPlugin())
  }

  return plugins
}
```

> build/plugins/px2rem.ts

```typescript
// px2rem
import { px2rem } from 'vite-plugin-px2rem'

export function px2remPlugin() {
  return px2rem({
    width: 750, // 设计稿宽度 核心
    rootFontSize: 16, // 根字体大小
  })
}
```

> build/plugins/svgLoader.ts

```typescript
// svg
import svgLoader from 'vite-svg-loader'

export function svgLoaderPlugin() {
  return svgLoader({
    defaultImport: 'url', // or 'raw'
    svgo: true,
  })
}
```

> build/plugins/UnoCSS.ts

```typescript
// unocss

import UnoCSS from 'unocss/vite'

export const UnoCSSPlugin: any = () => UnoCSS()
```

> build/plugins/visualizer.ts

```typescript
// 代码分析
import { visualizer } from 'rollup-plugin-visualizer'

export function visualizerPlugin() {
  return visualizer({
    open: true, // 注意这里要设置为true，否则无效
    gzipSize: true,
    brotliSize: true,
  })
}
```

> build/plugins/viteCompression.ts

```typescript
// giz 压缩
// 压缩gzip
import viteCompression from 'vite-plugin-compression'

export function viteCompressionPlugin() {
  return viteCompression({
    verbose: true, // 默认即可
    disable: false, // 开启压缩(不禁用)，默认即可
    deleteOriginFile: false, // 删除源文件
    threshold: 10240, // 压缩前最小文件大小
    algorithm: 'gzip', // 压缩算法
    ext: '.gz', // 文件类型
  })
}
```

> build/plugins/ViteImageOptimizer.ts

```typescript
// 图片压缩
import { ViteImageOptimizer } from 'vite-plugin-image-optimizer'

export function ViteImageOptimizerPlugin() {
  return ViteImageOptimizer({
    png: {
      // https://sharp.pixelplumbing.com/api-output#png
      quality: 60,
    },
    jpeg: {
      // https://sharp.pixelplumbing.com/api-output#jpeg
      quality: 60,
    },
    jpg: {
      // https://sharp.pixelplumbing.com/api-output#jpeg
      quality: 60,
    },
  })
}
```

> build/plugins/ViteRestart.ts

```typescript
// 自动重启
import ViteRestart from 'vite-plugin-restart'

export function ViteRestartPlugin() {
  return ViteRestart({
    restart: ['*.config.[jt]s', '**/config/*.[jt]s', '*.config.cjs', './.eslintrc.cjs'],
  })
}
```

> build/plugins/VueDevTools.ts

```typescript
// devTools
import VueDevTools from 'vite-plugin-vue-devtools'

export const VueDevToolsPlugin: any = () => VueDevTools()
```

## 按需引入Element plus

安装：

- element-plus：核心依赖包
- @element-plus/icons-vue：图标
- unplugin-vue-components：自动注册全局组件
- unplugin-auto-import：自动引入全局api
- vite-plugin-style-import：解决Element-plus api样式不引入问题 consola附带依赖
- unplugin-icons 官网使用按钮按需注册

```shell
# 核心依赖
npm i element-plus @element-plus/icons-vue

#按需加载
npm i unplugin-vue-components unplugin-auto-import vite-plugin-style-import consola unplugin-icons -D
```

vite.config.ts配置：

```typescript
import { fileURLToPath, URL } from 'node:url'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
// 自动引入注册
import AutoImport from 'unplugin-auto-import/vite'

// 自动引入element plus 组件 自动识别全局组件并点亮属性提示

import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import Components from 'unplugin-vue-components/vite'
import { defineConfig } from 'vite'
import { createStyleImportPlugin, ElementPlusResolve } from 'vite-plugin-style-import'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    // ...
    AutoImport({
      resolvers: [ElementPlusResolver()],
      imports: ['vue', 'vue-router', 'pinia'],
      dts: './types/auto-imports.d.ts',
      // eslint 报错解决：'ref' is not defined
      eslintrc: {
        // 默认 false, true 启用生成。生成一次就可以，避免每次工程启动都生成，一旦生成配置文件之后，最好把 enable 关掉，即改成 false。结合文档1
        // enabled: true,
        // 否则这个文件每次会在重新加载的时候重新生成，这会导致 eslint 有时会找不到这个文件。当需要更新配置文件的时候，再重新打开
        // filepath: './.eslintrc-auto-import.json' // 默认就是 ./.eslintrc-auto-import.json
        // globalsPropValue: true // 默认 true
      },
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: './types/components.d.ts',
    }),
    createStyleImportPlugin({
      resolves: [ElementPlusResolve()],
      libs: [
        {
          libraryName: 'element-plus',
          esModule: true,
          resolveStyle: (name: string) => {
            return `element-plus/theme-chalk/${name}.css`
          },
        },
      ],
    }),
  ],
})
```

> tsconfig.app.json

```json
{
  // ...
  "compilerOptions": {
    // ..
    "types": ["element-plus/global"]
  }
}
```
