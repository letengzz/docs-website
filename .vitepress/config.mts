import { defineConfig } from 'vitepress'
import { groupIconMdPlugin, groupIconVitePlugin } from 'vitepress-plugin-group-icons'
import { nav } from './nav'
import { sidebar } from './sidebar'
import { missingAssetPlaceholder } from './plugins/missingAssetPlaceholder'
// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Hjc的个人文档",
  titleTemplate: ":title - Hjc",
  description: "Hjc",
  base: `/docs-website/`,
  lang: 'zh-CN',
  ignoreDeadLinks: true,
  metaChunk: true,
  lastUpdated: false,
  themeConfig: {
    lastUpdated: {
      text: '更新时间',
      formatOptions: {
        dateStyle: 'full',
        timeStyle: 'medium'
      }
    },
    logo: "/logo.svg", // 配置logo位置，public目录
    outline: [2, 6],
    outlineTitle: '目录',
    // 设置搜索框的样式
    search: {
      provider: "local",
      options: {
        translations: {
          button: {
            buttonText: "搜索文档",
            buttonAriaLabel: "搜索文档",
          },
          modal: {
            noResultsText: "无法找到相关结果",
            resetButtonTitle: "清除查询条件",
            footer: {
              selectText: "选择",
              navigateText: "切换",
              closeText: "关闭",
            },
          },
        },
      },
    },
    // search: {
    //   provider: 'local'
    // },
    nav: nav,
    sidebar: sidebar,
    sidebarMenuLabel: '菜单',
    returnToTopLabel: '返回顶部',
    darkModeSwitchLabel: '外观',
    lightModeSwitchTitle: '切换到浅色模式',
    darkModeSwitchTitle: '切换到深色模式',
    socialLinks: [
      { icon: 'github', link: 'https://github.com/letengzz' }
    ],
    footer: {
      message: '开发者笔记仓库',
      copyright: 'Copyright © 2024 Hjc'
    },
    docFooter: {
      prev: false,
      next: false
    },
  },
   head: [
    ['link', { rel: 'icon', href: `/docs-website/logo.svg` }],
    [
      'script',
      {},
      ` window._hmt = window._hmt || [];
      (function() {
        var hm = document.createElement("script");
        hm.src = "https://hm.baidu.com/hm.js?fb46d28a76aba5f6b6c86d5e0098ab4f";
        var s = document.getElementsByTagName("script")[0];
        s.parentNode.insertBefore(hm, s);
      })();`,
    ],
  ],
  
  // vitepress-plugin-group-icons
  markdown: {
          lineNumbers: true, //显示行号
      container: {
        tipLabel: '提示',
        warningLabel: '说明',
        dangerLabel: '注意',
        infoLabel: '信息',
        detailsLabel: '详细信息',
      },
    config(md) {
      md.use(groupIconMdPlugin)
    },
  },
  vite: {
    build: {
      // === 大仓构建的内存与 CPU 预算（2026-11-08 加） ===
      // 真正吃内存的是 Rollup 的模块图（3,200+ 页 × 每页编译后的 render 函数），
      // 所以堆上限才是主开关，见 package.json 的 docs:build。
      // 另注：不要指望 buildConcurrency——VitePress 1.6.4 里它只作用于
      // 「本地搜索索引」与「社交图标」两处 pMap，页面渲染与打包阶段并不读它。
      // 本站 3,200+ 页会产出 3,000+ 个 chunk。默认会给每个 chunk 做一次 gzip，
      // 只为在结尾打印体积报告——纯 CPU + 临时内存开销，CI 上不值得。
      reportCompressedSize: false,
      rollupOptions: {
        // Rollup 默认并发读 20 个模块文件。大仓里同时驻留的 AST 更多，
        // 降到 4 换更低的读入峰值（代价是构建时间略增）。
        maxParallelFileOps: 4,
      },
    },
    plugins: [
      // 缺失配图兜底：把「文件不存在的图片 import」解析成内联占位图，
      // 避免历史欠账（E3 BROKEN_ASSET）阻断整站构建。详见该文件头部说明。
      missingAssetPlaceholder(),
      groupIconVitePlugin()
    ],
  }
})
