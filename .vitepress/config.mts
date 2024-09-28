import { defineConfig } from 'vitepress'
import { set_sidebar } from "../utils/auto-gen-sidebar.mjs";	// 改成自己的路径

export default defineConfig({
  title: "Hjc的个人文档",
  titleTemplate: ":title - Hjc",
  ignoreDeadLinks: [
    // ignore exact url "/playground"
    '/playground',
    // ignore all localhost links
    /^https?:\/\/localhost/,
    // ignore all links include "/repl/""
    /\/repl\//,
    // custom function, ignore all links include "ignore"
    (url) => {
      return url.toLowerCase().includes('ignore')
    }
  ],
  description: "Hjc",
  // base: `/docs-website/`,
  head: [['link', { rel: 'icon', href: `/docs-website/logo.svg` }]],
  lang: 'zh-CN',
  lastUpdated: true,
  themeConfig: {
    logo: "/logo.svg", // 配置logo位置，public目录
    outline: [2, 6],
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
    // search: {
    //   provider: 'local'
    // },
    nav: [
      { text: '首页', link: '/' },
      { text: '前端', items: [{ text: '基础', link: '/frontend' }, { text: '前端', link: '/frontend' },] },
      { text: '后端', items: [{ text: 'Go', link: '/docs/后端/Go' }, { text: 'Java', link: '/docs/后端/Java' },] },
      { text: '数据库', items: [{ text: 'Go', link: '/docs/后端/Go' }, { text: 'Java', link: '/docs/后端/Java' },] },
      { text: '运维', items: [{ text: 'Go', link: '/docs/后端/Go' }, { text: 'Java', link: '/docs/后端/Java' },] },
      { text: '项目', link: '/project' },
      { text: '其他', link: '/other' },
    ],
    sidebar: {
      "/docs/后端": set_sidebar("/docs/后端"),
      "/docs/前端": set_sidebar("/docs/前端"),
      "/docs/后端/Java": set_sidebar("/docs/后端/Java"),
      "/docs/后端/Go": set_sidebar("/docs/后端/Go"),
      "/other": set_sidebar("/other"),
      "/docs": [
        {
          text: '前端',
          collapsed: true,
          items: [
            { text: '基础', link: '/docs/前端' },
            { text: '进阶', link: '/docs/前端' },
          ]
        },
        {
          text: '后端',
          collapsed: true,
          items: [
            { text: 'Go', collapsed: true, items: set_sidebar("/docs/后端/Go") },
            {
              text: 'Java', collapsed: true, items: [
                { text: 'JavaSE', link: '/docs/前端' },
                { text: 'JavaWeb', link: '/docs/前端' },
                { text: 'JDBC', link: '/docs/前端' },
                { text: 'Java框架',collapsed: true,
                  items: [
                    { text: '框架基本概念', link: '/docs/后端/Java/Java框架/框架基本概念.md' },
                    { text: 'Spring', link: '/docs/后端/Java/消息队列MQ/Kafka/概述.md' },
                    { text: 'SpringBoot', link: '/docs/后端/Java/消息队列MQ/RabbitMQ/概述.md' },
                    { text: 'SpringCloud', link: '/docs/后端/Java/消息队列MQ/RocketMQ/概述.md' },
                    { text: 'MyBatis', link: '/docs/后端/Java/消息队列MQ/RocketMQ/概述.md' },
                    { text: 'MyBatis Plus', link: '/docs/后端/Java/消息队列MQ/RocketMQ/概述.md' },
                  ] },
                {
                  text: '消息队列MQ',
                  collapsed: true,
                  items: [
                    { text: '消息队列MQ 概述', link: '/docs/后端/Java/消息队列MQ/概述.md' },
                    { text: 'Kafka', link: '/docs/后端/Java/消息队列MQ/Kafka/概述.md' },
                    { text: 'RabbitMQ', link: '/docs/后端/Java/消息队列MQ/RabbitMQ/概述.md' },
                    { text: 'RocketMQ', link: '/docs/后端/Java/消息队列MQ/RocketMQ/概述.md' },
                  ]
                },
                {
                  text: '工具',
                  collapsed: true,
                  items: [
                    {
                      text: 'IDE',
                      collapsed: true,
                      items: [
                        { text: 'IDEA', link: '/docs/后端/Java/工具/IDE/IDEA/概述.md' },
                      ]
                    },
                    {
                      text: '版本控制',
                      collapsed: true,
                      items: [
                        { text: '版本控制 概述', link: '/docs/后端/Java/工具/版本控制/概述.md' },
                        { text: 'Git', link: '/docs/后端/Java/工具/版本控制/Git/概述.md' },
                        { text: 'SVN', link: '/docs/后端/Java/工具/版本控制/SVN/概述.md' },
                      ]
                    },
                    {
                      text: '持续集成工具',
                      collapsed: true,
                      items: [
                        { text: 'Jenkins', link: '/docs/后端/Java/工具/持续集成工具/Jenkins/概述.md' },
                      ]
                    },
                    {
                      text: '构建依赖管理工具',
                      collapsed: true,
                      items: [
                        { text: 'Maven', link: '/docs/后端/Java/工具/构建依赖管理工具/Maven/概述.md' },
                      ]
                    },
                  ]
                },
                { text: '算法' },
                { text: '其他' },
              ]
            },

          ]
        },
        {
          text: '其他',
          collapsed: true,
          items: [
            { text: '基础', link: '/docs/前端' },
            { text: '进阶', link: '/docs/前端' },
          ]
        },
      ],
      "/project": [
        {
          text: '通用权限项目',
          collapsed: true,
          items: [
            { text: '通用权限项目(一)', collapsed: true, link: '/project/通用权限项目/通用权限项目(一)/index',items:[
              { text: '项目介绍', link: '/project/通用权限项目/通用权限项目(一)/项目介绍' },
              { text: '项目搭建', link: '/project/通用权限项目/通用权限项目(一)/项目搭建' },
            ] },
            { text: '通用权限项目(二)',  link: '/project/通用权限项目/通用权限项目(二)/index'  },
          ]
        },
      ],
    },

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
    }
  }
})
