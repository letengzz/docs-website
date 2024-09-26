import { defineConfig } from 'vitepress'
import { set_sidebar } from "../utils/auto_sidebar.mjs";	// 改成自己的路径\

// https://vitepress.dev/reference/site-config
export default defineConfig({
  head: [["link", { rel: "icon", href: "/logo.svg" }]],
  title: "Hjc的个人文档",
  description: "A VitePress Site",
  themeConfig: {
    logo: 'logo.svg',
    outlineTitle: '目录',
    outline: [2, 6],
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Go', items: [{ text: 'Go', link: '/' }] },
      { text: 'Java', items: [{ text: 'JavaSE', link: '/docs/后端/Java/javase/概述' }, { text: 'JavaWeb', link: '/' }, { text: 'JDBC', link: '/' }, { text: 'Java框架', link: '/docs/后端/java/frame/框架基本概念' }, { text: '消息队列', link: '/' }, { text: '工具', link: '/' }, { text: '其他', link: '/' }, { text: '算法', link: '/' }] },
      { text: '数据库', items: [{ text: 'Home', link: '/' }] },
      { text: 'Linux', items: [{ text: 'Home', link: '/docs/后端/index1' }] },
      { text: '项目', items: [{ text: 'Home', link: '/项目/后台管理系统' }] }
    ],

    // sidebar: [
    //   {
    //     text: 'Examples',
    //     items: [
    //       { text: 'Markdown Examples1', link: '/docs/后端' },
    //       { text: 'Runtime API Examples', link: '/api-examples' }
    //     ]
    //   }
    // ],

    sidebar: {
      "/project": set_sidebar("/project"),
      "/docs": set_sidebar("/docs"),
      "/docs/后端/Java/javase": set_sidebar("/docs/后端/Java/javase"),
      "/docs/后端/Java/frame": set_sidebar("/docs/后端/Java/frame"),
      "/docs/后端": set_sidebar("/docs/后端")
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/letengzz' }
    ],
    footer: {
      // message: 'Released under the MIT License.',
      copyright: 'Copyright © 2024-present Hjc'
    },
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
            },
          },
        },
      },
    },
  }
})
