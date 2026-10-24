import fs from 'node:fs'
import path from 'node:path'
import type { Plugin } from 'vite'

// 缺失配图兜底（2026-10-24 新增）
//
// 背景：本机是 `blob:none` 的 partial clone，且 `.git/info/sparse-checkout` 曾把
// `docs/` 下任意层级的 `assets/` 目录整体排除在检出之外（正文引用 1,911 处，
// 本地只有 18 个 SVG）。markdown 里的 `![x](../assets/y.svg)` 会被编译成一次
// ESM import，文件不在磁盘上时 Vite 直接抛错——一条本地缺图就能让整站构建失败，
// 等于把「检出方式」升级成了「构建阻断」。
//
// 本插件把「文件不存在」这一类 import 解析成一个内联的占位 SVG（数据 URI），于是：
//   ① 构建不再被历史欠账阻断，`pnpm docs:build` 可以对新增内容做真正的验证；
//   ② 页面显示「配图待补」而不是破图（比 404 图标更可读）；
//   ③ 欠账没有被隐藏——`linkexistcheck` 仍然逐条报 E3，补图后自动恢复真实图片，
//      本插件对「文件存在」的路径完全不做干预。
//
// 纪律：只在文件确实不存在时介入；不生成文件、不改 Markdown、不吞掉任何一个存在的资源；
// 每一次介入都 `this.warn` 一条，缺图清单可以直接从构建日志里 grep `missing-asset`。
//
// 踩坑记录：本文件原先用块注释写上面这段说明，而说明里出现了含 `assets` 的通配路径，
// 该路径中的 `星号星号斜杠` 序列提前闭合了块注释，剩下的 `assets` 变成游离语句，
// 构建时报 `assets is not defined`。**任何注释里提到通配路径，一律用行注释。**

const ASSET_RE = /\.(?:svg|png|jpe?g|webp|gif|avif)$/i

// 严格模式：设 DOCS_STRICT_ASSETS=1 时退化回 Vite 原生行为（缺图直接构建失败）。
// 用途是「补完欠账之后把这层兜底关掉」，让构建重新具备硬门禁能力。
const STRICT = process.env.DOCS_STRICT_ASSETS === '1'

const PLACEHOLDER = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 140" width="480" height="140">
  <rect x="1" y="1" width="478" height="138" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-dasharray="6 5"/>
  <text x="240" y="62" text-anchor="middle" font-family="system-ui, sans-serif" font-size="15" fill="#64748b">配图待补</text>
  <text x="240" y="88" text-anchor="middle" font-family="system-ui, sans-serif" font-size="11" fill="#94a3b8">该图片尚未提交到仓库，见 DOCS_PLAN 存量整理清单</text>
</svg>`

const PLACEHOLDER_URI = `data:image/svg+xml;utf8,${encodeURIComponent(PLACEHOLDER.replace(/\n\s*/g, ''))}`
const VIRTUAL_PREFIX = '\0missing-asset:'

export function missingAssetPlaceholder(): Plugin {
  // 同一张图可能被多页 import，按绝对路径去重，日志里一条即一处欠账
  const seen = new Set<string>()
  return {
    name: 'docs:missing-asset-placeholder',
    enforce: 'pre',
    buildStart() {
      seen.clear()
    },
    resolveId(id, importer) {
      if (STRICT) return null
      if (!ASSET_RE.test(id)) return null
      if (id.startsWith('\0') || id.includes('?')) return null
      if (/^(?:[a-z]+:)?\/\//i.test(id) || id.startsWith('data:') || id.startsWith('/')) return null
      if (!importer) return null
      const importerPath = importer.split('?')[0]
      const resolved = path.resolve(path.dirname(importerPath), id)
      if (fs.existsSync(resolved)) return null
      // 逐条告警：兜底不等于静默，构建日志里必须能数出缺了哪些图
      if (!seen.has(resolved)) {
        seen.add(resolved)
        this.warn(`[missing-asset] 图片不在磁盘上，已用占位图替代：${path.relative(process.cwd(), resolved)}`)
      }
      return VIRTUAL_PREFIX + resolved
    },
    buildEnd() {
      if (seen.size > 0) {
        this.warn(
          `[missing-asset] 本次构建共 ${seen.size} 张图片走了占位图（去重后计）。` +
            `这属于检出/欠账问题，不是内容正确性：图片补进仓库后自动恢复，无需改任何 Markdown。` +
            `完整清单跑 python3 utils/audit/linkexistcheck.py 看 E3 BROKEN_ASSET。`,
        )
      }
    },
    load(id) {
      if (!id.startsWith(VIRTUAL_PREFIX)) return null
      return `export default ${JSON.stringify(PLACEHOLDER_URI)}`
    },
  }
}
