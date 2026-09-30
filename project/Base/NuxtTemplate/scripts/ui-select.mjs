#!/usr/bin/env node
/**
 * ui-select.mjs —— Nuxt 通用模板的 UI 组件库选择器。
 *
 * 设计目标（与文档「第 5 步：切换工具链」一一对应）：
 *   1. 幂等   ：产物是 (ui, render) 两个取值的纯函数，不含时间戳 / 用户名 / 预设名
 *   2. 可校验 ：--check 重新计算并与磁盘逐字节比对，不一致即以非 0 退出，可当 CI 门禁
 *   3. 可回溯 ：取值落在 ui.config.json（入库），谁在什么时候换过库一眼可见
 *   4. 零依赖 ：只用 Node 内置模块，不需要 npm install
 *   5. 只写生成物 + 一个 marker 区间：手写业务文件永不覆盖
 *
 * 用法：
 *   node scripts/ui-select.mjs --ui element --render ssr
 *   node scripts/ui-select.mjs --preset element-admin
 *   node scripts/ui-select.mjs --list
 *   node scripts/ui-select.mjs --check
 *   node scripts/ui-select.mjs --dry-run --ui antd --render ssr
 *   node scripts/ui-select.mjs --print        # 只打印当前取值对应的命令，不写文件
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import process from 'node:process'
import { fileURLToPath } from 'node:url'

// --------------------------------------------------------------------------
// 目录约定（工程根目录下的相对路径）
// --------------------------------------------------------------------------
const CONFIG_FILE = 'ui.config.json'
const NUXT_CONFIG = 'nuxt.config.ts'
const GEN_DIR = 'app/ui/generated'
const FILES = {
  manifest: `${GEN_DIR}/manifest.ts`,
  adapter: `${GEN_DIR}/adapter.ts`,
  deps: `${GEN_DIR}/deps.json`,
  fragment: `${GEN_DIR}/nuxt-ui.config.mjs`,
  tokens: 'app/assets/styles/generated-tokens.css',
  summary: 'UI.md',
}
const MARKER_BEGIN = '// ui:modules:begin'
const MARKER_END = '// ui:modules:end'
const IMPORT_LINE
  = "import { uiModules } from './app/ui/generated/nuxt-ui.config.mjs'"
const IMPORT_MODULE = "'./app/ui/generated/nuxt-ui.config.mjs'"

// --------------------------------------------------------------------------
// 目录表：每个 UI 实现层的元数据（版本口径 2026-09-30，以官方发布页为准）
// --------------------------------------------------------------------------
const CATALOG = {
  element: {
    label: 'Element Plus',
    version: '2.14.x',
    module: '@element-plus/nuxt',
    moduleVersion: '1.1.x',
    impl: '@app/ui-element',
    experimental: false,
    deps: { 'element-plus': '^2.14.0', '@element-plus/icons-vue': '^2.3.0' },
    devDeps: { '@element-plus/nuxt': '^1.1.0' },
    css: [],
    transpile: ['element-plus'],
    prefix: 'el',
    vars: {
      '--el-color-primary': 'var(--ui-color-primary)',
      '--el-color-danger': 'var(--ui-color-danger)',
      '--el-border-radius-base': 'var(--ui-radius-control)',
      '--el-font-size-base': 'var(--ui-font-body)',
    },
    hydration: [
      '官方模块已内置 SSR 的 ID 与 z-index 注入，无需手工 provide',
      'Teleport 类组件（Dialog / Drawer / Tooltip）用 <ClientOnly> 包一层',
      'pnpm 环境需保证 dayjs 可被解析（提升依赖或显式安装）',
    ],
    fit: '表单密集的中后台',
  },
  antd: {
    label: 'Ant Design Vue',
    version: '4.x',
    module: '@ant-design-vue/nuxt',
    moduleVersion: '1.4.x',
    impl: '@app/ui-antd',
    experimental: false,
    deps: { 'ant-design-vue': '^4.2.0', '@ant-design/icons-vue': '^7.0.0' },
    devDeps: { '@ant-design-vue/nuxt': '^1.4.0' },
    css: [],
    transpile: ['ant-design-vue'],
    prefix: 'a',
    vars: {
      '--ant-color-primary': 'var(--ui-color-primary)',
      '--ant-color-error': 'var(--ui-color-danger)',
      '--ant-border-radius': 'var(--ui-radius-control)',
      '--ant-font-size': 'var(--ui-font-body)',
    },
    hydration: [
      '打开样式提取（extractStyle），避免首屏样式闪烁与顺序不一致',
      '图标包需单独注册，否则渲染期找不到图标组件',
      '按需导入由官方模块完成，不要手工再配 unplugin',
    ],
    fit: '复杂表格与企业管理台',
  },
  nuxtui: {
    label: 'Nuxt UI',
    version: '4.11.x',
    module: '@nuxt/ui',
    moduleVersion: '4.11.x',
    impl: '@app/ui-nuxtui',
    experimental: false,
    deps: { '@nuxt/ui': '^4.11.0', tailwindcss: '^4.3.0' },
    devDeps: {},
    css: ['~/assets/styles/main.css'],
    transpile: [],
    prefix: 'u',
    vars: {
      '--ui-primary': 'var(--ui-color-primary)',
      '--ui-error': 'var(--ui-color-danger)',
    },
    hydration: [
      '根组件必须用 <UApp> 包裹，否则 Toast / Tooltip / Overlay 不工作',
      'Tailwind 4 走 CSS-first：main.css 里 @import "tailwindcss" 与 "@nuxt/ui"',
      '要求 Nuxt 4.1 及以上；本模板基线为 Nuxt 4.5',
    ],
    fit: '内容站、追求与框架原生融合',
  },
  vuetify: {
    label: 'Vuetify',
    version: '3.x',
    module: 'vuetify-nuxt-module',
    moduleVersion: '1.0.0-rc.5',
    impl: '@app/ui-vuetify',
    experimental: true,
    deps: { vuetify: '^3.9.0' },
    devDeps: { 'vuetify-nuxt-module': '1.0.0-rc.5' },
    css: [],
    transpile: [],
    prefix: 'v',
    vars: {
      '--v-theme-primary': 'var(--ui-color-primary)',
      '--v-theme-error': 'var(--ui-color-danger)',
    },
    hydration: [
      '官方模块目前仍处于 rc 阶段，生产使用必须锁死精确版本',
      'SASS 变量需要在构建期注入，运行时改主题只能改 CSS 变量那部分',
      '使用前请确认模块的 SSR 行为在你的 Nuxt 小版本上已验证',
    ],
    fit: 'Material 风格产品',
  },
}

const UI_KEYS = ['element', 'antd', 'nuxtui', 'vuetify']
const RENDER_KEYS = ['ssr', 'ssg']

// 预设只是「怎么选」的便捷入口，不写进任何生成物
const PRESETS = {
  'element-admin': { ui: 'element', render: 'ssr', note: '国内中后台最主流的一套' },
  'antd-enterprise': { ui: 'antd', render: 'ssr', note: '复杂表格与企业级表单' },
  'nuxtui-content': { ui: 'nuxtui', render: 'ssg', note: '内容站，全静态预渲染' },
  'vuetify-material': { ui: 'vuetify', render: 'ssr', note: 'Material 风格（实验性）' },
  'static-demo': { ui: 'element', render: 'ssg', note: '纯静态演示壳' },
}

const EXIT_OK = 0
const EXIT_REJECT = 1
const EXIT_USAGE = 2

class Reject extends Error {}

// --------------------------------------------------------------------------
// 工具
// --------------------------------------------------------------------------
const normalize = text => text.replace(/\r\n/g, '\n').replace(/\r/g, '\n')

const readText = path => normalize(readFileSync(path, 'utf8'))

const writeText = (path, text) => {
  mkdirSync(dirname(path), { recursive: true })
  writeFileSync(path, normalize(text), 'utf8')
}

const j = value => JSON.stringify(value)
const jPretty = value => `${JSON.stringify(value, null, 2)}\n`

/** 个性化能力由渲染模式派生：SSG 在构建期把 HTML 定死，没有「按这次请求」的机会。 */
const personalizeOf = render => render === 'ssr'

// --------------------------------------------------------------------------
// 产物计算：纯函数 (ui, render) -> { 相对路径: 内容 }
// --------------------------------------------------------------------------
function buildArtifacts(ui, render) {
  const meta = CATALOG[ui]
  const personalize = personalizeOf(render)
  const degraded = personalize ? [] : ['personalize']

  const manifest = `// 本文件由 scripts/ui-select.mjs 生成，请勿手工修改。
// 取值来源：${CONFIG_FILE}（唯一事实来源）
export const uiManifest = {
  ui: ${j(ui)},
  uiLabel: ${j(meta.label)},
  uiVersion: ${j(meta.version)},
  impl: ${j(meta.impl)},
  module: ${j(meta.module)},
  moduleVersion: ${j(meta.moduleVersion)},
  render: ${j(render)},
  experimental: ${meta.experimental},
  degraded: ${j(degraded)},
} as const

export type UiKey = ${UI_KEYS.map(j).join(' | ')}
export type RenderMode = ${RENDER_KEYS.map(j).join(' | ')}
`

  const adapter = `// 本文件由 scripts/ui-select.mjs 生成，请勿手工修改。
// 业务层只 import 这里，永远不 import 具体的组件库。
export { default as UiProvider } from ${j(meta.impl)}
export const uiPrefix = ${j(meta.prefix)}
import type { UiKey } from './manifest'
export const uiKey: UiKey = ${j(ui)}
`

  const deps = jPretty({
    ui,
    render,
    personalize,
    dependencies: meta.deps,
    devDependencies: meta.devDeps,
    note: '本文件由 ui-select.mjs 生成，用于驱动依赖安装命令，不直接写入 package.json。',
  })

  const fragment = `// 本文件由 scripts/ui-select.mjs 生成，请勿手工修改。
// nuxt.config.ts 的 marker 区间会读取本文件导出的值。
export const uiModules = ${j([meta.module])}
export const uiCss = ${j(meta.css)}
export const uiBuild = ${j({ transpile: meta.transpile })}
export const uiNitroPreset = ${j(personalize ? 'node-server' : 'static')}
export const uiRouteRules = ${j(personalize ? {} : { '/**': { prerender: true } })}
export const uiRuntimeConfigPublic = ${j({ ui, render, personalize })}
// 契约组件通过 #ui-impl 找到当前实现：换库只改这一行，业务与契约层都不动。
// 用 # 前缀是为了与 npm 包名区分，避免构建器去 node_modules 里找它。
export const uiAlias = ${j({ '#ui-impl': `./app/ui/impl/${ui}` })}
`

  const varLines = Object.entries(meta.vars).map(([k, v]) => `  ${k}: ${v};`).join('\n')
  const tokens = `/* 本文件由 scripts/ui-select.mjs 生成，请勿手工修改。
 * 第 ③ 层：把语义令牌映射到 ${meta.label} 的变量命名体系。
 * 业务与组件只使用第 ② 层（--ui-*），换库时只替换本文件。 */
:root {
  /* ---- 第 ② 层：语义令牌（由第 ① 层品牌令牌派生） ---- */
  --ui-color-primary: var(--brand-500);
  --ui-color-danger: var(--brand-danger);
  --ui-radius-control: var(--radius-md);
  --ui-font-body: var(--font-size-base);

  /* ---- 第 ③ 层：${meta.label} 变量映射 ---- */
${varLines}
}
`

  const hydration = meta.hydration.map((s, i) => `${i + 1}. ${s}`).join('\n')
  const summary = `# UI 实现层：${meta.label}（${render}）

本文件由 \`scripts/ui-select.mjs\` 生成，是当前取值的**人可读摘要**。
取值来源只有一处：\`${CONFIG_FILE}\`。

| 项 | 值 |
| --- | --- |
| UI 实现层 | \`${meta.impl}\` |
| 组件库 | ${meta.label} ${meta.version} |
| Nuxt 模块 | \`${meta.module}\` ${meta.moduleVersion} |
| 渲染模式 | ${render} |
| Nitro preset | ${personalize ? 'node-server' : 'static'} |
| 实验性 | ${meta.experimental ? '是（生产使用需锁死版本）' : '否'} |
| 降级项 | ${degraded.length ? degraded.join('、') : '无'} |
| 适配场景 | ${meta.fit} |

## SSR / 水合注意事项

${hydration}

## 需要执行的命令

\`\`\`shell
node scripts/ui-select.mjs --ui ${ui} --render ${render}
node scripts/ui-select.mjs --check
pnpm install
pnpm dev
\`\`\`
`

  return {
    files: {
      [FILES.manifest]: manifest,
      [FILES.adapter]: adapter,
      [FILES.deps]: deps,
      [FILES.fragment]: fragment,
      [FILES.tokens]: tokens,
      [FILES.summary]: summary,
    },
    degraded,
  }
}

/** marker 区间的内容刻意与取值无关：区间内容对所有 ui 取值完全相同。 */
const markerBlock = () => `  ${MARKER_BEGIN}\n  modules: [...baseModules, ...uiModules],\n  ${MARKER_END}`

/** 把 marker 区间替换为规范内容；区间或 import 缺失时拒绝执行（不猜位置）。 */
function applyMarker(existing) {
  const text = normalize(existing)
  const b = text.indexOf(MARKER_BEGIN)
  const e = text.indexOf(MARKER_END)
  if (b < 0 || e < 0 || e < b) {
    throw new Reject(
      `${NUXT_CONFIG} 里找不到 marker 区间，脚本不会猜位置自己去创建。\n`
      + `请手工补回这两行后重试：\n  ${MARKER_BEGIN}\n  ${MARKER_END}`,
    )
  }
  if (!text.includes(IMPORT_MODULE)) {
    throw new Reject(
      `${NUXT_CONFIG} 顶部缺少生成物的 import，脚本不会替你插入 import 语句。\n`
      + `请在文件顶部补上（import 语句可以换行书写）：\n  ${IMPORT_LINE}`,
    )
  }
  // 从「含前置缩进的行首」开始替换、从 MARKER_END 行的行尾之后接回。
  // 否则区间前的缩进会被不断累加：每跑一次多缩进一层，--check 立刻报红。
  const lineStart = text.lastIndexOf('\n', b) + 1
  const lineEnd = text.indexOf('\n', e)
  const head = text.slice(0, lineStart)
  const tail = lineEnd >= 0 ? text.slice(lineEnd) : ''
  return head + markerBlock() + tail
}

/** 返回 { targets, degraded }：全部应当落盘的文件内容。 */
function fullTargets(ui, render, existingNuxt) {
  const { files, degraded } = buildArtifacts(ui, render)
  return {
    targets: {
      ...files,
      [CONFIG_FILE]: jPretty({ ui, render, personalize: personalizeOf(render) }),
      [NUXT_CONFIG]: applyMarker(existingNuxt),
    },
    degraded,
  }
}

// --------------------------------------------------------------------------
// 门禁
// --------------------------------------------------------------------------
function gate(ui, render, args) {
  const meta = CATALOG[ui]
  let ok = true

  if (meta.experimental && !args.allowExperimental) {
    console.error(
      `ERROR 组合 ui=${ui} 依赖实验性模块，脚本默认拒绝：\n`
      + `  - ${meta.module} 当前版本 ${meta.moduleVersion}（仍是 rc，未发正式版）\n\n`
      + `原因：rc 阶段的 Nuxt 模块在小版本之间可能改变 SSR 行为，\n`
      + `      而 UI 库恰恰是「换掉就要全站回归」的那一层，不适合承担这个风险。\n\n`
      + `处理方式二选一：\n`
      + `  a) 换一个稳定模块：  --ui element / --ui antd / --ui nuxtui\n`
      + `  b) 明确接受风险：    --allow-experimental（生成物里 experimental=true，并在 UI.md 写清）`,
    )
    ok = false
  }

  if (render === 'ssg' && !args.allowDegraded) {
    console.error(
      'ERROR 组合 render=ssg 会让以下能力降级，脚本默认拒绝：\n'
      + '  - 按请求个性化（按登录态 / 时区 / 地理位置决定首屏内容）\n\n'
      + '原因：SSG 在构建期就把 HTML 定死，服务端没有「按这次请求」的机会。\n'
      + '      单机演示能跑通，但一旦真的要求「同一 URL 不同人看到不同内容」就会失效。\n\n'
      + '处理方式二选一：\n'
      + '  a) 改用 SSR：        --render ssr\n'
      + '  b) 明确接受降级：    --allow-degraded-personalize（生成物里 personalize=false）',
    )
    ok = false
  }
  return ok
}

// --------------------------------------------------------------------------
// 子命令
// --------------------------------------------------------------------------
function cmdList() {
  console.log('可选 UI 实现层：')
  for (const key of UI_KEYS) {
    const m = CATALOG[key]
    console.log(`  ${key.padEnd(9)} ${m.label.padEnd(16)} ${m.version.padEnd(10)} ${m.impl}${m.experimental ? '  [实验性]' : ''}`)
  }
  console.log(`\n可选渲染模式：${RENDER_KEYS.join(' / ')}\n`)
  console.log('预设：')
  for (const [name, p] of Object.entries(PRESETS)) {
    console.log(`  ${name.padEnd(18)} ui=${p.ui.padEnd(9)} render=${p.render.padEnd(5)} ${p.note}`)
  }
  return EXIT_OK
}

function resolvePick(args) {
  if (args.preset) {
    const p = PRESETS[args.preset]
    if (!p) {
      console.error(`ERROR 未知预设：${args.preset}`)
      return null
    }
    return [p.ui, p.render]
  }
  if (!args.ui || !args.render) {
    console.error('ERROR 需要同时给出 --ui 与 --render（或用 --preset）')
    return null
  }
  if (!UI_KEYS.includes(args.ui)) {
    console.error(`ERROR --ui 取值非法：${args.ui}，可选 ${UI_KEYS.join(' / ')}`)
    return null
  }
  if (!RENDER_KEYS.includes(args.render)) {
    console.error(`ERROR --render 取值非法：${args.render}，可选 ${RENDER_KEYS.join(' / ')}`)
    return null
  }
  return [args.ui, args.render]
}

function cmdApply(args, ui, render) {
  const dir = args.dir
  const nuxtPath = join(dir, NUXT_CONFIG)
  const cfgPath = join(dir, CONFIG_FILE)

  if (!existsSync(nuxtPath)) {
    console.error(`ERROR 在 ${nuxtPath} 找不到 ${NUXT_CONFIG}`)
    return EXIT_REJECT
  }
  if (!existsSync(cfgPath) && !args.dryRun) {
    console.error(`ERROR 在 ${cfgPath} 找不到 ${CONFIG_FILE}，请先创建（内容见文档）`)
    return EXIT_REJECT
  }

  const { targets, degraded } = fullTargets(ui, render, readText(nuxtPath))

  if (args.dryRun) {
    for (const rel of Object.keys(targets).sort()) {
      const body = targets[rel]
      console.log(`DRY   ${rel} (${body.split('\n').length} 行)`)
    }
    if (degraded.length) console.log(`DRY   降级项：${degraded.join(', ')}`)
    return EXIT_OK
  }

  const changed = []
  for (const rel of Object.keys(targets).sort()) {
    const path = join(dir, rel)
    const next = targets[rel]
    if (!(existsSync(path) && readText(path) === normalize(next))) {
      writeText(path, next)
      changed.push(rel)
    }
  }

  console.log(`OK    ui=${ui} render=${render} 已写入 ${Object.keys(targets).length} 个文件，其中 ${changed.length} 个发生变化`)
  for (const rel of changed) console.log(`      ~ ${rel}`)
  if (degraded.length) console.log(`      降级项已在生成物中置为关闭：${degraded.join(', ')}`)
  return EXIT_OK
}

function cmdCheck(args) {
  const dir = args.dir
  const nuxtPath = join(dir, NUXT_CONFIG)
  const cfgPath = join(dir, CONFIG_FILE)

  for (const p of [nuxtPath, cfgPath]) {
    if (!existsSync(p)) {
      console.error(`ERROR 缺少文件：${p}`)
      return EXIT_REJECT
    }
  }

  let cfg
  try {
    cfg = JSON.parse(readText(cfgPath))
  } catch (err) {
    console.error(`ERROR ${CONFIG_FILE} 不是合法 JSON：${err.message}`)
    return EXIT_REJECT
  }

  const { ui, render } = cfg
  if (!UI_KEYS.includes(ui) || !RENDER_KEYS.includes(render)) {
    console.error(`ERROR ${CONFIG_FILE} 里的取值非法：ui=${ui} render=${render}`)
    return EXIT_REJECT
  }
  if ('personalize' in cfg && cfg.personalize !== personalizeOf(render)) {
    console.error(
      `FAIL  ${CONFIG_FILE} 里的 personalize 与 render 不一致：\n`
      + `      该字段由 render 派生（ssr → true，ssg → false），不应手工修改。\n`
      + `      当前 render=${render}，期望 ${j(personalizeOf(render))}，实际 ${j(cfg.personalize)}`,
    )
    return EXIT_REJECT
  }

  const { targets, degraded } = fullTargets(ui, render, readText(nuxtPath))
  const bad = []
  for (const rel of Object.keys(targets).sort()) {
    const path = join(dir, rel)
    if (!existsSync(path)) bad.push([rel, '文件缺失'])
    else if (readText(path) !== normalize(targets[rel])) bad.push([rel, '内容与 ui.config.json 不一致'])
  }

  if (bad.length) {
    console.log('FAIL  --check 未通过：')
    for (const [rel, why] of bad) console.log(`      ${rel}：${why}`)
    console.log(`      共 ${bad.length} 个文件漂移；跑一次 --ui ${ui} --render ${render} 即收敛`)
    return EXIT_REJECT
  }

  console.log(`OK    --check 通过：${Object.keys(targets).length} 个生成物与 ${CONFIG_FILE} 完全一致`)
  if (degraded.length) console.log(`      当前降级项：${degraded.join(', ')}`)
  return EXIT_OK
}

function cmdPrint(args) {
  const cfgPath = join(args.dir, CONFIG_FILE)
  if (!existsSync(cfgPath)) {
    console.error(`ERROR 找不到 ${cfgPath}`)
    return EXIT_REJECT
  }
  const cfg = JSON.parse(readText(cfgPath))
  console.log(`当前取值：ui=${cfg.ui} render=${cfg.render}`)
  console.log(`重新生成：node scripts/ui-select.mjs --ui ${cfg.ui} --render ${cfg.render}`)
  console.log('CI 门禁：  node scripts/ui-select.mjs --check')
  return EXIT_OK
}

// --------------------------------------------------------------------------
// 入口
// --------------------------------------------------------------------------
function parseArgs(argv) {
  const out = { dir: '.', _unknown: [] }
  const takeValue = name => {
    const v = argv[++out.i]
    if (!v) throw Object.assign(new Error(`缺少 ${name} 的值`), { usage: true })
    return v
  }
  for (out.i = 0; out.i < argv.length; out.i++) {
    const a = argv[out.i]
    if (a === '--ui') out.ui = takeValue(a)
    else if (a === '--render') out.render = takeValue(a)
    else if (a === '--preset') out.preset = takeValue(a)
    else if (a === '--dir') out.dir = takeValue(a)
    else if (a === '--check') out.check = true
    else if (a === '--list') out.list = true
    else if (a === '--dry-run') out.dryRun = true
    else if (a === '--print') out.print = true
    else if (a === '--allow-experimental') out.allowExperimental = true
    else if (a === '--allow-degraded-personalize') out.allowDegraded = true
    else if (a === '--help' || a === '-h') out.help = true
    else out._unknown.push(a)
  }
  return out
}

const USAGE = `用法：
  node scripts/ui-select.mjs --ui <${UI_KEYS.join('|')}> --render <${RENDER_KEYS.join('|')}>
  node scripts/ui-select.mjs --preset <${Object.keys(PRESETS).join('|')}>
  node scripts/ui-select.mjs --list | --check | --print
  node scripts/ui-select.mjs --dry-run --ui <key> --render <key>
选项：
  --dir <path>                     工程根目录（默认当前目录）
  --allow-experimental             明确接受实验性模块的风险
  --allow-degraded-personalize     明确接受 SSG 下个性化能力降级`

/**
 * 命令行入口：把 argv 映射为退出码，**不自己调 process.exit**。
 * 拆出来的目的是让自测能在同一个进程里直接驱动它（受限环境下子进程可能不可用）。
 */
function runCli(argv) {
  let args
  try {
    args = parseArgs(argv)
  } catch (err) {
    console.error(`ERROR ${err.message}\n\n${USAGE}`)
    return EXIT_USAGE
  }

  if (args.help) {
    console.log(USAGE)
    return EXIT_OK
  }
  // 未知参数先于「没给参数」判断：拼错一个开关时，回显错在哪比甩一份用法有用得多。
  if (args._unknown.length) {
    console.error(`ERROR 未知参数：${args._unknown.join(' ')}\n\n${USAGE}`)
    return EXIT_USAGE
  }
  if (!args.list && !args.check && !args.print && !args.ui && !args.preset) {
    console.log(USAGE)
    return EXIT_USAGE
  }
  if (args.list) return cmdList()
  if (args.check) return cmdCheck(args)
  if (args.print) return cmdPrint(args)

  const pick = resolvePick(args)
  if (!pick) return EXIT_USAGE
  const [ui, render] = pick
  if (!gate(ui, render, args)) return EXIT_REJECT

  try {
    return cmdApply(args, ui, render)
  } catch (err) {
    if (err instanceof Reject) {
      console.error(`ERROR ${err.message}`)
      return EXIT_REJECT
    }
    throw err
  }
}

// 只有「被直接执行」时才跑 CLI；被 import 时仅导出函数，供自测在进程内驱动。
const isDirectRun
  = Boolean(process.argv[1]) && resolve(process.argv[1]) === resolve(fileURLToPath(import.meta.url))

if (isDirectRun) process.exit(runCli(process.argv.slice(2)))

export {
  CATALOG,
  EXIT_OK,
  EXIT_REJECT,
  EXIT_USAGE,
  FILES,
  MARKER_BEGIN,
  MARKER_END,
  PRESETS,
  RENDER_KEYS,
  Reject,
  UI_KEYS,
  applyMarker,
  buildArtifacts,
  cmdApply,
  cmdCheck,
  cmdList,
  cmdPrint,
  fullTargets,
  gate,
  markerBlock,
  normalize,
  parseArgs,
  personalizeOf,
  readText,
  resolvePick,
  runCli,
  writeText,
}
