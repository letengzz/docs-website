#!/usr/bin/env node
/**
 * selftest.mjs —— scripts/ui-select.mjs 的自测。
 *
 * 设计原则：**门禁断言必须是变异测试**。
 * 不只验证「正常路径能过」，还要主动把东西改坏，确认它**必须报红**。
 * 只跑正常路径的自测，会在校验器本身失效时一路绿灯——那比没有自测更危险。
 *
 * 覆盖十组：
 *   A 用法与元数据      B 生成物内容        C 幂等
 *   D 手写文件保护      E marker/import 缺失  F 门禁
 *   G --check 行为      H 全矩阵            I --dry-run
 *   J --print
 *
 * 驱动方式：**进程内调用 runCli()**，不起子进程。
 * 因为脚本把「直接执行」与「被 import」分开了（`isDirectRun` 守卫），
 * 所以自测可以在同一个进程里驱动它——这在子进程被禁用的受限环境里也能跑通。
 *
 * 零依赖，只用 Node 内置模块。用法：
 *   node scripts/selftest.mjs
 *   node scripts/selftest.mjs --verbose
 */
import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync, statSync, unlinkSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, relative } from 'node:path'
import process from 'node:process'
import { fileURLToPath } from 'node:url'

import { runCli } from './ui-select.mjs'

const HERE = dirname(fileURLToPath(import.meta.url))
const SCRIPT = join(HERE, 'ui-select.mjs')
const FIXTURE = join(HERE, 'fixture')
const VERBOSE = process.argv.includes('--verbose')
/** --only A,C,D ：只跑部分分组，排查问题时用。 */
const ONLY = (() => {
  const i = process.argv.indexOf('--only')
  if (i < 0) return null
  const v = process.argv[i + 1]
  if (!v) return null
  return new Set(v.split(',').map(s => s.trim().toUpperCase()).filter(Boolean))
})()

// ---------------------------------------------------------------------------
// 断言与统计
// ---------------------------------------------------------------------------
let pass = 0
const failures = []
const warnings = []

function check(group, name, cond, detail = '') {
  if (cond) {
    pass++
    if (VERBOSE) console.log(`  ok   [${group}] ${name}`)
  }
  else {
    failures.push(`[${group}] ${name}${detail ? `\n        ${detail}` : ''}`)
  }
}

function warn(group, name, detail) {
  warnings.push(`[${group}] ${name}：${detail}`)
}

const normalize = text => text.replace(/\r\n/g, '\n').replace(/\r/g, '\n')

// ---------------------------------------------------------------------------
// 沙箱：把 fixture 复制到临时目录，脚本只在那里跑，绝不碰仓库
// ---------------------------------------------------------------------------
/**
 * 沙箱根目录固定、每个用例一个子目录，**全程不删除任何目录**。
 *
 * 为什么不删：`rmSync(..., { recursive: true })` 与 `rmdirSync()` 在部分 Windows
 * 环境（含本仓库的验证机）会直接挂住不返回，而挂住比报错更难排查。
 * 子目录编号是确定的，重跑会原地覆盖，所以占用是有界的（约 40 个目录），不会无限增长。
 */
const SANDBOX_ROOT = join(tmpdir(), 'nuxt-ui-selftest')
let caseSeq = 0

function sandbox() {
  caseSeq += 1
  const dir = join(SANDBOX_ROOT, `case-${String(caseSeq).padStart(2, '0')}`)
  mkdirSync(dir, { recursive: true })
  cpSync(FIXTURE, dir, { recursive: true })
  return dir
}

function reportSandbox() {
  console.log(`\n沙箱目录（可手动删除）：${SANDBOX_ROOT}`)
}

// ---------------------------------------------------------------------------
// 运行脚本（进程内）与快照
// ---------------------------------------------------------------------------
/**
 * 在 dir 里跑一次 CLI，返回 { code, out, err }。
 * 临时接管 console 与 cwd，跑完原样恢复——避免测试之间互相污染。
 */
function run(dir, ...args) {
  const out = []
  const err = []
  const origLog = console.log
  const origErr = console.error
  const prevCwd = process.cwd()
  let code
  console.log = (...a) => out.push(a.join(' '))
  console.error = (...a) => err.push(a.join(' '))
  try {
    process.chdir(dir)
    code = runCli(args)
  }
  catch (e) {
    code = `THREW:${e.message}`
  }
  finally {
    process.chdir(prevCwd)
    console.log = origLog
    console.error = origErr
  }
  return { code, out: out.join('\n'), err: err.join('\n') }
}

function walk(dir, base = dir, acc = new Map()) {
  for (const name of readdirSync(dir)) {
    const full = join(dir, name)
    if (statSync(full).isDirectory()) walk(full, base, acc)
    else acc.set(relative(base, full).replace(/\\/g, '/'), normalize(readFileSync(full, 'utf8')))
  }
  return acc
}

const snap = dir => walk(dir)

function same(a, b) {
  if (a.size !== b.size) return false
  for (const [k, v] of a) {
    if (!b.has(k) || b.get(k) !== v) return false
  }
  return true
}

function diffKeys(a, b) {
  const keys = [...new Set([...a.keys(), ...b.keys()])].sort()
  return keys.filter(k => a.get(k) !== b.get(k))
}

const read = (dir, rel) => normalize(readFileSync(join(dir, rel), 'utf8'))
const write = (dir, rel, text) => writeFileSync(join(dir, rel), text, 'utf8')

const GEN = {
  manifest: 'app/ui/generated/manifest.ts',
  adapter: 'app/ui/generated/adapter.ts',
  deps: 'app/ui/generated/deps.json',
  fragment: 'app/ui/generated/nuxt-ui.config.mjs',
  tokens: 'app/assets/styles/generated-tokens.css',
  summary: 'UI.md',
  config: 'ui.config.json',
  nuxt: 'nuxt.config.ts',
}
const ALL_TARGETS = Object.values(GEN)

const UI_KEYS = ['element', 'antd', 'nuxtui', 'vuetify']
const RENDER_KEYS = ['ssr', 'ssg']
const LIB = {
  element: {
    label: 'Element Plus',
    module: '@element-plus/nuxt',
    dep: 'element-plus',
    tokenMark: '--el-color-primary: var(--ui-color-primary);',
    experimental: false,
  },
  antd: {
    label: 'Ant Design Vue',
    module: '@ant-design-vue/nuxt',
    dep: 'ant-design-vue',
    tokenMark: '--ant-color-primary: var(--ui-color-primary);',
    experimental: false,
  },
  nuxtui: {
    label: 'Nuxt UI',
    module: '@nuxt/ui',
    dep: '@nuxt/ui',
    tokenMark: '--ui-primary: var(--ui-color-primary);',
    experimental: false,
  },
  vuetify: {
    label: 'Vuetify',
    module: 'vuetify-nuxt-module',
    dep: 'vuetify',
    tokenMark: '--v-theme-primary: var(--ui-color-primary);',
    experimental: true,
  },
}
const PRESETS = ['element-admin', 'antd-enterprise', 'nuxtui-content', 'vuetify-material', 'static-demo']

/** 门禁要求显式接受的取值，这里替测试补上。 */
function flags(ui, render) {
  const extra = []
  if (LIB[ui].experimental) extra.push('--allow-experimental')
  if (render === 'ssg') extra.push('--allow-degraded-personalize')
  return extra
}

// ---------------------------------------------------------------------------
// A. 用法与元数据
// ---------------------------------------------------------------------------
function groupA() {
  const dir = sandbox()

  const listed = run(dir, '--list')
  check('A', '--list 退出码 0', listed.code === 0, `实际 ${listed.code}`)
  for (const ui of UI_KEYS) check('A', `--list 列出 ${ui}`, listed.out.includes(ui))
  check('A', '--list 标记实验性实现层', listed.out.includes('[实验性]'))
  const experimentalLines = listed.out.split('\n').filter(l => l.includes('[实验性]'))
  check('A', '实验性标记只出现在 vuetify 一行',
    experimentalLines.length === 1 && experimentalLines[0].includes('vuetify'),
    `实际 ${experimentalLines.length} 行：${experimentalLines.join(' | ')}`)
  for (const p of PRESETS) check('A', `--list 列出预设 ${p}`, listed.out.includes(p))

  const helped = run(dir, '--help')
  check('A', '--help 退出码 0', helped.code === 0, `实际 ${helped.code}`)
  check('A', '--help 打印用法', helped.out.includes('用法'))

  const noArgs = run(dir)
  check('A', '无参数退出码 2（用法错误）', noArgs.code === 2, `实际 ${noArgs.code}`)

  const badFlag = run(dir, '--nope')
  check('A', '未知参数退出码 2', badFlag.code === 2, `实际 ${badFlag.code}`)
  check('A', '未知参数被回显', badFlag.err.includes('--nope'))

  const badUi = run(dir, '--ui', 'bootstrap', '--render', 'ssr')
  check('A', '--ui 取值非法退出码 2', badUi.code === 2, `实际 ${badUi.code}`)

  const badRender = run(dir, '--ui', 'element', '--render', 'csr')
  check('A', '--render 取值非法退出码 2', badRender.code === 2, `实际 ${badRender.code}`)

  const badPreset = run(dir, '--preset', 'nope')
  check('A', '未知预设退出码 2', badPreset.code === 2, `实际 ${badPreset.code}`)

  const halfGiven = run(dir, '--ui', 'element')
  check('A', '只给 --ui 不给 --render 退出码 2', halfGiven.code === 2, `实际 ${halfGiven.code}`)

  const missingValue = run(dir, '--ui')
  check('A', '--ui 缺值退出码 2', missingValue.code === 2, `实际 ${missingValue.code}`)

  // --dir：从别处驱动同一个工程（写进的是 --dir 指定的目录，不是 cwd）
  const elsewhere = sandbox()
  const target = sandbox()
  const viaDir = run(elsewhere, '--ui', 'nuxtui', '--render', 'ssg', '--allow-degraded-personalize', '--dir', target)
  check('A', '--dir 把产物写到指定目录而不是 cwd',
    viaDir.code === 0
    && existsSync(join(target, GEN.manifest))
    && !existsSync(join(elsewhere, GEN.manifest)),
    `code=${viaDir.code}；target 有产物=${existsSync(join(target, GEN.manifest))}；cwd 被误写=${existsSync(join(elsewhere, GEN.manifest))}`)
}

// ---------------------------------------------------------------------------
// B. 生成物内容
// ---------------------------------------------------------------------------
function groupB() {
  for (const ui of UI_KEYS) {
    for (const render of RENDER_KEYS) {
      const tag = `${ui}/${render}`
      const dir = sandbox()
      const r = run(dir, '--ui', ui, '--render', render, ...flags(ui, render))
      const meta = LIB[ui]

      check('B', `${tag} 退出码 0`, r.code === 0, `实际 ${r.code}；stderr=${r.err.trim().slice(0, 160)}`)
      check('B', `${tag} 生成全部 8 个目标文件`, ALL_TARGETS.every(rel => existsSync(join(dir, rel))),
        `缺失：${ALL_TARGETS.filter(rel => !existsSync(join(dir, rel))).join(', ')}`)

      const manifest = read(dir, GEN.manifest)
      check('B', `${tag} manifest 记录 ui`, manifest.includes(`ui: ${JSON.stringify(ui)}`))
      check('B', `${tag} manifest 记录 uiLabel`, manifest.includes(meta.label))
      check('B', `${tag} manifest 记录 render`, manifest.includes(`render: ${JSON.stringify(render)}`))
      check('B', `${tag} manifest 记录 experimental`, manifest.includes(`experimental: ${meta.experimental}`))
      check('B', `${tag} manifest 记录降级项`,
        manifest.includes(`degraded: ${render === 'ssr' ? '[]' : '["personalize"]'}`))
      check('B', `${tag} manifest 带「请勿手工修改」banner`,
        manifest.startsWith('// 本文件由 scripts/ui-select.mjs 生成'))

      const adapter = read(dir, GEN.adapter)
      check('B', `${tag} adapter 导出实现层包名`, adapter.includes(JSON.stringify(`@app/ui-${ui}`)))
      // adapter 的 import 只能指向「实现层包」或相对路径；出现组件库包名就等于业务被写死到某个库
      const adapterImports = [...adapter.matchAll(/from\s+["']([^"']+)["']/g)].map(m => m[1])
      check('B', `${tag} adapter 不 import 任何组件库`,
        adapterImports.length > 0 && adapterImports.every(s => s.startsWith('@app/ui-') || s.startsWith('.')),
        `实际 import：${adapterImports.join(', ') || '(无)'}`)

      const fragment = read(dir, GEN.fragment)
      check('B', `${tag} fragment 导出对应 Nuxt 模块`, fragment.includes(JSON.stringify([meta.module])))
      check('B', `${tag} fragment 的 #ui-impl 指向本实现`,
        fragment.includes(`"#ui-impl":"./app/ui/impl/${ui}"`))
      check('B', `${tag} fragment 的 nitro preset 由 render 派生`,
        fragment.includes(render === 'ssr' ? '"node-server"' : '"static"'))
      check('B', `${tag} fragment 的 routeRules 与 render 一致`,
        render === 'ssr'
          ? fragment.includes('export const uiRouteRules = {}')
          : fragment.includes('"prerender":true'))

      const deps = JSON.parse(read(dir, GEN.deps))
      check('B', `${tag} deps.json 可解析且取值正确`, deps.ui === ui && deps.render === render)
      check('B', `${tag} deps.json 含组件库依赖`,
        meta.dep in deps.dependencies || meta.dep in deps.devDependencies)
      check('B', `${tag} deps.json 的 personalize 由 render 派生`, deps.personalize === (render === 'ssr'))

      const tokens = read(dir, GEN.tokens)
      check('B', `${tag} tokens 映射到本库变量体系`, tokens.includes(meta.tokenMark),
        `期望包含 ${meta.tokenMark}`)
      check('B', `${tag} tokens 保留第 ② 层语义令牌`, tokens.includes('--ui-color-primary: var(--brand-500)'))

      const summary = read(dir, GEN.summary)
      check('B', `${tag} UI.md 摘要含库名与渲染模式`,
        summary.includes(meta.label) && summary.includes(`（${render}）`))
      check('B', `${tag} UI.md 摘要含可复制命令`, summary.includes(`--ui ${ui} --render ${render}`))

      const nuxt = read(dir, GEN.nuxt)
      check('B', `${tag} nuxt.config.ts marker 区间内容与取值无关`,
        nuxt.includes('modules: [...baseModules, ...uiModules],'))
      check('B', `${tag} nuxt.config.ts 保留手写 import`,
        nuxt.includes('\'./app/ui/generated/nuxt-ui.config.mjs\''))
    }
  }

  // 交叉验证：不同库的令牌文件必须真的不同，否则「换库」可能只是没写进去
  const dirA = sandbox()
  run(dirA, '--ui', 'element', '--render', 'ssr')
  const tokensElement = read(dirA, GEN.tokens)
  const dirB = sandbox()
  run(dirB, '--ui', 'antd', '--render', 'ssr')
  check('B', '两个库的令牌文件内容不同', tokensElement !== read(dirB, GEN.tokens))
}

// ---------------------------------------------------------------------------
// C. 幂等
// ---------------------------------------------------------------------------
function groupC() {
  const dir = sandbox()
  const r1 = run(dir, '--preset', 'element-admin')
  check('C', '首次切换退出码 0', r1.code === 0, `实际 ${r1.code}`)
  const after1 = snap(dir)

  const r2 = run(dir, '--preset', 'element-admin')
  check('C', '第二次切换退出码 0', r2.code === 0, `实际 ${r2.code}`)
  check('C', '第二次切换报告 0 个文件发生变化', /其中 0 个发生变化/.test(r2.out),
    `实际输出：${r2.out.trim().split('\n')[0]}`)

  const after2 = snap(dir)
  const changed = diffKeys(after1, after2)
  check('C', '连跑两次后全目录字节不变（幂等）', changed.length === 0,
    `变化的文件：${changed.join(', ')}`)

  const r3 = run(dir, '--preset', 'element-admin')
  check('C', '第三次切换仍 0 变化', /其中 0 个发生变化/.test(r3.out))

  // 幂等也必须在「切过去再切回来」时成立
  run(dir, '--ui', 'antd', '--render', 'ssr')
  run(dir, '--preset', 'element-admin')
  check('C', '切走再切回，产物回到同一状态', same(after1, snap(dir)),
    `差异文件：${diffKeys(after1, snap(dir)).join(', ')}`)
}

// ---------------------------------------------------------------------------
// D. 手写文件保护
// ---------------------------------------------------------------------------
function groupD() {
  const dir = sandbox()
  run(dir, '--ui', 'element', '--render', 'ssr')

  // 区间外手改一处配置，模拟「人在 nuxt.config.ts 里加了自己的东西」
  const nuxt0 = read(dir, GEN.nuxt)
  check('D', 'fixture 默认带区间外手写配置', nuxt0.includes('appManifest: false'))
  write(dir, GEN.nuxt, nuxt0.replace('appManifest: false', 'appManifest: true'))

  const page0 = read(dir, 'app/pages/index.vue')
  const tokens0 = read(dir, 'app/assets/styles/tokens.css')
  const nuxtBefore = read(dir, GEN.nuxt)

  const r = run(dir, '--ui', 'antd', '--render', 'ssr')
  check('D', '换库退出码 0', r.code === 0, `实际 ${r.code}`)

  check('D', '换库不改业务页面', read(dir, 'app/pages/index.vue') === page0)
  check('D', '换库不改手写令牌文件', read(dir, 'app/assets/styles/tokens.css') === tokens0)

  const nuxtAfter = read(dir, GEN.nuxt)
  check('D', '换库不改 nuxt.config.ts（marker 区间内容与取值无关）', nuxtAfter === nuxtBefore)
  check('D', '换库后变更列表里不出现 nuxt.config.ts', !r.out.includes('nuxt.config.ts'),
    `实际变更列表：\n        ${r.out.trim().split('\n').join('\n        ')}`)
  check('D', '区间外的手改配置在换库后保留', nuxtAfter.includes('appManifest: true'))
  check('D', '换库后 ui.config.json 记录了新取值', JSON.parse(read(dir, GEN.config)).ui === 'antd')

  // 反向：marker 区间内的内容被改坏时，脚本必须修复它
  write(dir, GEN.nuxt, nuxtBefore.replace(
    'modules: [...baseModules, ...uiModules],',
    'modules: [...baseModules],',
  ))
  const repaired = run(dir, '--ui', 'antd', '--render', 'ssr')
  check('D', 'marker 区间被改坏后能自动修复', repaired.code === 0 && read(dir, GEN.nuxt).includes('...uiModules'))
  check('D', 'marker 区间修复后其余手写内容不动', read(dir, GEN.nuxt).includes('appManifest: true'))
}

// ---------------------------------------------------------------------------
// E. marker / import 缺失 —— 拒绝执行而不是猜位置
// ---------------------------------------------------------------------------
function groupE() {
  // E1：marker 被删
  const dir = sandbox()
  run(dir, '--ui', 'element', '--render', 'ssr')
  write(dir, GEN.nuxt, read(dir, GEN.nuxt).replace('// ui:modules:begin', '// oops:modules:begin'))
  // 快照必须取在「我们自己把它改坏」之后：否则比出来的差异是测试自己造成的
  const before = snap(dir)
  const e1 = run(dir, '--ui', 'antd', '--render', 'ssr')
  check('E', 'marker 缺失时退出码 1', e1.code === 1, `实际 ${e1.code}`)
  check('E', 'marker 缺失时给出可操作提示', e1.err.includes('marker') && e1.err.includes('ui:modules:begin'),
    `stderr=${e1.err.trim().slice(0, 200)}`)
  check('E', 'marker 缺失时不写任何文件', same(before, snap(dir)),
    `被误写的文件：${diffKeys(before, snap(dir)).join(', ')}`)

  // E2：只留 begin 不留 end
  const dirHalf = sandbox()
  run(dirHalf, '--ui', 'element', '--render', 'ssr')
  write(dirHalf, GEN.nuxt, read(dirHalf, GEN.nuxt).replace('// ui:modules:end', '// ui:modules:END'))
  const e1b = run(dirHalf, '--ui', 'antd', '--render', 'ssr')
  check('E', '只有 begin 没有 end 时退出码 1', e1b.code === 1, `实际 ${e1b.code}`)

  // E3：import 被改
  const dir2 = sandbox()
  run(dir2, '--ui', 'element', '--render', 'ssr')
  write(dir2, GEN.nuxt, read(dir2, GEN.nuxt)
    .replace('\'./app/ui/generated/nuxt-ui.config.mjs\'', '\'./app/ui/generated/nope.mjs\''))
  const before2 = snap(dir2)
  const e2 = run(dir2, '--ui', 'antd', '--render', 'ssr')
  check('E', 'import 缺失时退出码 1', e2.code === 1, `实际 ${e2.code}`)
  check('E', 'import 缺失时提示如何补回', e2.err.includes('import'), `stderr=${e2.err.trim().slice(0, 200)}`)
  check('E', 'import 缺失时不写任何文件', same(before2, snap(dir2)),
    `被误写的文件：${diffKeys(before2, snap(dir2)).join(', ')}`)

  // E4：nuxt.config.ts 整个丢了
  const dir3 = sandbox()
  run(dir3, '--ui', 'element', '--render', 'ssr')
  unlinkSync(join(dir3, GEN.nuxt))
  const e3 = run(dir3, '--ui', 'antd', '--render', 'ssr')
  check('E', 'nuxt.config.ts 缺失时退出码 1', e3.code === 1, `实际 ${e3.code}`)
  check('E', 'nuxt.config.ts 缺失时报错回显路径', e3.err.includes('nuxt.config.ts'))
}

// ---------------------------------------------------------------------------
// F. 门禁：默认拒绝、必须显式接受，且拒绝时不落盘
// ---------------------------------------------------------------------------
function groupF() {
  // F1：实验性模块
  const dir = sandbox()
  run(dir, '--ui', 'element', '--render', 'ssr')
  const before = snap(dir)

  const f1 = run(dir, '--ui', 'vuetify', '--render', 'ssr')
  check('F', '实验性模块无 flag 时退出码 1', f1.code === 1, `实际 ${f1.code}`)
  check('F', '实验性门禁报错指明模块与版本',
    f1.err.includes('vuetify-nuxt-module') && f1.err.includes('rc'),
    `stderr=${f1.err.trim().slice(0, 220)}`)
  check('F', '实验性门禁给出两条出路',
    f1.err.includes('--allow-experimental') && f1.err.includes('--ui element'))
  check('F', '实验性门禁被拒时不写任何文件', same(before, snap(dir)),
    `被误写的文件：${diffKeys(before, snap(dir)).join(', ')}`)

  const f1b = run(dir, '--ui', 'vuetify', '--render', 'ssr', '--allow-experimental')
  check('F', '实验性模块加 flag 后通过', f1b.code === 0, `实际 ${f1b.code}`)
  check('F', '接受风险后生成物标记 experimental=true',
    read(dir, GEN.manifest).includes('experimental: true'))
  check('F', '接受风险后 UI.md 写明实验性', read(dir, GEN.summary).includes('锁死版本'))

  // F2：SSG 降级
  const dir2 = sandbox()
  run(dir2, '--ui', 'element', '--render', 'ssr')
  const before2 = snap(dir2)
  const f2 = run(dir2, '--ui', 'element', '--render', 'ssg')
  check('F', 'SSG 降级无 flag 时退出码 1', f2.code === 1, `实际 ${f2.code}`)
  check('F', '降级门禁说明失去的是哪项能力', f2.err.includes('按请求个性化'),
    `stderr=${f2.err.trim().slice(0, 220)}`)
  check('F', '降级门禁被拒时不写任何文件', same(before2, snap(dir2)),
    `被误写的文件：${diffKeys(before2, snap(dir2)).join(', ')}`)

  const f2b = run(dir2, '--ui', 'element', '--render', 'ssg', '--allow-degraded-personalize')
  check('F', 'SSG 加 flag 后通过', f2b.code === 0, `实际 ${f2b.code}`)
  check('F', '接受降级后生成物 personalize=false',
    JSON.parse(read(dir2, GEN.deps)).personalize === false)
  check('F', '接受降级后 UI.md 写明降级项', read(dir2, GEN.summary).includes('personalize'))

  // F3：两条门禁同时触发时都报出来（不要只报第一条就退出）
  const dir3 = sandbox()
  const f3 = run(dir3, '--ui', 'vuetify', '--render', 'ssg')
  check('F', '两条门禁同时触发时都报出',
    f3.err.includes('--allow-experimental') && f3.err.includes('--allow-degraded-personalize'),
    `stderr=${f3.err.trim().slice(0, 260)}`)
}

// ---------------------------------------------------------------------------
// G. --check：漂移必须报红，且能收敛
// ---------------------------------------------------------------------------
function groupG() {
  const dir = sandbox()
  run(dir, '--ui', 'antd', '--render', 'ssr')
  const clean = snap(dir)

  const g0 = run(dir, '--check')
  check('G', '一致时 --check 退出码 0', g0.code === 0, `实际 ${g0.code}`)
  check('G', '一致时 --check 报告比对个数', /8 个生成物/.test(g0.out), `输出=${g0.out.trim()}`)

  // G1：篡改一个生成物
  write(dir, GEN.manifest, `${read(dir, GEN.manifest)}// tampered\n`)
  const afterTamper = snap(dir)
  const g1 = run(dir, '--check')
  check('G', '篡改生成物后 --check 退出码 1', g1.code === 1, `实际 ${g1.code}`)
  check('G', '篡改后 --check 指出具体文件', g1.out.includes(GEN.manifest), `输出=${g1.out.trim()}`)
  check('G', '篡改后 --check 报告漂移文件数', /共 1 个文件漂移/.test(g1.out), `输出=${g1.out.trim()}`)

  // G2：--check 本身不修改文件
  check('G', '--check 是只读的，不修文件', same(afterTamper, snap(dir)),
    `被 --check 误改的文件：${diffKeys(afterTamper, snap(dir)).join(', ')}`)

  // G3：跑一次切换即收敛
  run(dir, '--ui', 'antd', '--render', 'ssr')
  const g3 = run(dir, '--check')
  check('G', '重跑一次切换后收敛，--check 退出码 0', g3.code === 0, `实际 ${g3.code}`)
  check('G', '收敛后目录与最初一致', same(clean, snap(dir)),
    `差异文件：${diffKeys(clean, snap(dir)).join(', ')}`)

  // G4：personalize 被手工篡改
  write(dir, GEN.config, `${JSON.stringify({ ui: 'antd', render: 'ssr', personalize: false }, null, 2)}\n`)
  const g4 = run(dir, '--check')
  check('G', 'personalize 被篡改后 --check 退出码 1', g4.code === 1, `实际 ${g4.code}`)
  check('G', 'personalize 漂移的报错说明它是派生值', g4.err.includes('派生'), `stderr=${g4.err.trim()}`)

  // G5：删掉一个生成物
  const dir5 = sandbox()
  run(dir5, '--ui', 'antd', '--render', 'ssr')
  unlinkSync(join(dir5, GEN.tokens))
  const g5 = run(dir5, '--check')
  check('G', '生成物被删后 --check 退出码 1', g5.code === 1, `实际 ${g5.code}`)
  check('G', '生成物被删后备注「文件缺失」', g5.out.includes('文件缺失'), `输出=${g5.out.trim()}`)

  // G6：缺 ui.config.json
  const dir6 = sandbox()
  unlinkSync(join(dir6, GEN.config))
  const g6 = run(dir6, '--check')
  check('G', '缺 ui.config.json 时 --check 退出码 1', g6.code === 1, `实际 ${g6.code}`)
  check('G', '缺文件报错回显路径', g6.err.includes(GEN.config), `stderr=${g6.err.trim()}`)

  // G7：配置不是合法 JSON
  const dir7 = sandbox()
  write(dir7, GEN.config, '{ this is not json ')
  const g7 = run(dir7, '--check')
  check('G', '配置非法 JSON 时退出码 1（不抛异常）', g7.code === 1, `实际 ${g7.code}`)
  check('G', '非法 JSON 报错说明解析失败', g7.err.includes('JSON'), `stderr=${g7.err.trim()}`)

  // G8：配置里取值非法
  const dir8 = sandbox()
  write(dir8, GEN.config, `${JSON.stringify({ ui: 'bootstrap', render: 'ssr' }, null, 2)}\n`)
  const g8 = run(dir8, '--check')
  check('G', '配置取值非法时退出码 1', g8.code === 1, `实际 ${g8.code}`)
}

// ---------------------------------------------------------------------------
// H. 全矩阵：4 库 × 2 渲染模式
// ---------------------------------------------------------------------------
function groupH() {
  const dir = sandbox()
  let ok = 0
  const lines = []
  for (const ui of UI_KEYS) {
    for (const render of RENDER_KEYS) {
      const a = run(dir, '--ui', ui, '--render', render, ...flags(ui, render))
      const c = run(dir, '--check')
      const good = a.code === 0 && c.code === 0
      if (good) ok++
      lines.push(`${good ? 'OK  ' : 'FAIL'} ${ui}/${render}`)
    }
  }
  check('H', '全矩阵 8/8 通过（切换 + --check）', ok === 8,
    `实际 ${ok}/8\n        ${lines.join('\n        ')}`)
}

// ---------------------------------------------------------------------------
// I. --dry-run：只打印不落盘
// ---------------------------------------------------------------------------
function groupI() {
  const dir = sandbox()
  run(dir, '--ui', 'element', '--render', 'ssr')
  const before = snap(dir)

  const r = run(dir, '--dry-run', '--ui', 'nuxtui', '--render', 'ssr')
  check('I', '--dry-run 退出码 0', r.code === 0, `实际 ${r.code}`)
  check('I', '--dry-run 列出将写入的文件', r.out.includes('DRY') && r.out.includes(GEN.manifest))
  check('I', '--dry-run 覆盖全部 8 个目标', (r.out.match(/^DRY/gm) || []).length >= 8,
    `DRY 行数 ${(r.out.match(/^DRY/gm) || []).length}`)
  check('I', '--dry-run 不落盘', same(before, snap(dir)),
    `被误写的文件：${diffKeys(before, snap(dir)).join(', ')}`)
  check('I', '--dry-run 不改变 ui.config.json', JSON.parse(read(dir, GEN.config)).ui === 'element')
}

// ---------------------------------------------------------------------------
// J. --print
// ---------------------------------------------------------------------------
function groupJ() {
  const dir = sandbox()
  run(dir, '--ui', 'nuxtui', '--render', 'ssg', '--allow-degraded-personalize')
  const r = run(dir, '--print')
  check('J', '--print 退出码 0', r.code === 0, `实际 ${r.code}`)
  check('J', '--print 回显当前取值', r.out.includes('nuxtui') && r.out.includes('ssg'), `输出=${r.out.trim()}`)
  check('J', '--print 给出可复制的重跑命令',
    r.out.includes('node scripts/ui-select.mjs --ui nuxtui --render ssg'))
  check('J', '--print 不写文件', JSON.parse(read(dir, GEN.config)).ui === 'nuxtui')

  const dir2 = sandbox()
  unlinkSync(join(dir2, GEN.config))
  const r2 = run(dir2, '--print')
  check('J', 'ui.config.json 缺失时 --print 退出码 1', r2.code === 1, `实际 ${r2.code}`)
}

// ---------------------------------------------------------------------------
// 主流程
// ---------------------------------------------------------------------------
const GROUPS = [
  ['A', '用法与元数据', groupA],
  ['B', '生成物内容', groupB],
  ['C', '幂等', groupC],
  ['D', '手写文件保护', groupD],
  ['E', 'marker / import 缺失', groupE],
  ['F', '门禁（默认拒绝）', groupF],
  ['G', '--check 行为', groupG],
  ['H', '全矩阵', groupH],
  ['I', '--dry-run', groupI],
  ['J', '--print', groupJ],
]

function main() {
  if (!existsSync(SCRIPT)) {
    console.error(`FATAL 找不到被测脚本：${SCRIPT}`)
    return 1
  }
  if (!existsSync(join(FIXTURE, 'nuxt.config.ts'))) {
    console.error(`FATAL 找不到 fixture：${join(FIXTURE, 'nuxt.config.ts')}`)
    return 1
  }

  console.log('ui-select.mjs 自测（零依赖 · 进程内驱动 · 门禁断言为变异测试）\n')
  if (ONLY) warn('scope', '本次只跑了部分分组，结果不代表全量通过', [...ONLY].join(', '))
  for (const [id, title, fn] of GROUPS) {
    if (ONLY && !ONLY.has(id)) continue
    const beforeFail = failures.length
    const beforePass = pass
    try {
      fn()
    }
    catch (err) {
      failures.push(`[${id}] 组内抛出异常：${err.message}`)
    }
    const bad = failures.length - beforeFail
    const n = pass - beforePass + bad
    console.log(`  ${bad ? 'FAIL' : 'PASS'}  ${id}  ${title}（${n} 项，失败 ${bad}）`)
  }

  console.log(`\n断言：通过 ${pass} / 失败 ${failures.length}`)
  if (failures.length) {
    console.log('\n失败明细：')
    for (const f of failures) console.log(`  - ${f}`)
  }
  if (warnings.length) {
    console.log('\n警告：')
    for (const w of warnings) console.log(`  - ${w}`)
  }
  console.log(failures.length ? '\n结果：FAIL' : '\n结果：OK')

  reportSandbox()
  return failures.length ? 1 : 0
}

process.exit(main())
