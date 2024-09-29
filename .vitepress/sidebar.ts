import { set_sidebar } from "../utils/auto-gen-sidebar.mjs";	// 改成自己的路径
import { defineConfig } from 'vitepress'
export const sidebar = {
    "/docs": [
        {
            text: '前端',
            collapsed: true,
            items: [
                {
                    text: '基础', collapsed: true,link: '/docs/前端/基础', items: [
                        { text: '前端开发', link: '/docs/前端/基础/前端开发' },
                        { text: 'HTML', link: '/docs/前端/基础/HTML' },
                        { text: 'CSS', link: '/docs/前端/基础/CSS' },
                        { text: 'JavaScript', link: '/docs/前端/基础/JavaScript' },
                        { text: 'TypeScript', link: '/docs/前端/基础/TypeScript' },
                    ]
                },
                {
                    text: '框架', collapsed: true, items: [
                        { text: 'Vue', link: '/docs/前端/框架/Vue', collapsed: true,items:[
                            { text: 'Vue 概述', link: '/docs/前端/框架/Vue/概述.md' },
                            { text: 'Vue2',collapsed: true, link: '/docs/前端/框架/Vue/Vue2',items:[
                                { text: 'Vue2 创建工程', link: '/docs/前端/框架/Vue/Vue2/创建工程.md' },
                                { text: 'Vue2 核心', collapsed: true,link: '/docs/前端/框架/Vue/Vue2/核心',items:[
                                    { text: '内置指令', link: '/docs/前端/框架/Vue/Vue2/核心/内置指令.md' },
                                    { text: '事件处理', link: '/docs/前端/框架/Vue/Vue2/核心/事件处理.md' },
                                    { text: '计算属性', link: '/docs/前端/框架/Vue/Vue2/核心/计算属性.md' },
                                    { text: '数据绑定', link: '/docs/前端/框架/Vue/Vue2/核心/数据绑定.md' },
                                    { text: '条件渲染', link: '/docs/前端/框架/Vue/Vue2/核心/条件渲染.md' },
                                    { text: '列表渲染', link: '/docs/前端/框架/Vue/Vue2/核心/列表渲染.md' },
                                    { text: '生命周期', link: '/docs/前端/框架/Vue/Vue2/核心/生命周期.md' },
                                    { text: 'vue_config.js 配置', link: '/docs/前端/框架/Vue/Vue2/核心/配置.md' },
                                ] },
                                { text: 'Vue2 组件化', link: '/docs/前端/框架/Vue/Vue2/组件化' },
                            ] },
                            { text: 'Vue3', collapsed: true,link: '/docs/前端/框架/Vue/Vue3',items:[
                                { text: 'Vue3 概述', link: '/docs/前端/框架/Vue/Vue3/概述.md' },
                                { text: 'Vue3 基本操作', link: '/docs/前端/框架/Vue/Vue3/基本操作.md' },
                                { text: 'Vue3 核心语法', link: '/docs/前端/框架/Vue/Vue3/核心语法.md' },
                                { text: 'Vue3 路由', link: '/docs/前端/框架/Vue/Vue3/路由.md' },
                                { text: 'Vue3 Pinia', link: '/docs/前端/框架/Vue/Vue3/Pinia.md' },
                                { text: 'Vue3 组件通信', link: '/docs/前端/框架/Vue/Vue3/组件通信.md' },
                                { text: 'Vue3 新组件', link: '/docs/前端/框架/Vue/Vue3/新组件.md' },
                                { text: '拓展', collapsed: true,items:[
                                    { text: 'Vue3 常见问题', link: '/docs/前端/框架/Vue/Vue3/拓展/常见问题.md' },
                                ] },
                            ] },
                        ] },
                        { text: 'React', link: '/docs/前端/框架/React', collapsed: true},
                        { text: 'Uniapp', link: '/docs/前端/框架/Uniapp', collapsed: true, items:[
                            { text: '组件库', collapsed: true,items:[
                                { text: 'Wot Design Uni', link: '/docs/前端/框架/Uniapp/组件库/WotDesignUni.md' },
                            ]}
                        ]},
                        {
                            text: 'Electron', link: '/docs/前端/框架/Electron', collapsed: true, items: [
                                { text: 'Electron 概述', link: '/docs/前端/框架/Electron/概述.md' },
                                { text: 'Electron 搭建环境', link: '/docs/前端/框架/Electron/搭建环境.md' },
                                { text: 'Electron 配置', link: '/docs/前端/框架/Electron/配置.md' },
                                { text: 'Electron 进程', link: '/docs/前端/框架/Electron/进程.md' },
                                { text: 'Electron Preload脚本', link: '/docs/前端/框架/Electron/预加载脚本.md' },
                                { text: 'Electron 进程通信IPC', link: '/docs/前端/框架/Electron/IPC.md' },
                                { text: 'Electron 打包应用', link: '/docs/前端/框架/Electron/打包应用.md' },
                                { text: 'Electron 构建工具', link: '/docs/前端/框架/Electron/构建工具.md' },
                                { text: '拓展', collapsed: true,items: [{ text: 'Electron+Vue3项目打包', link: '/docs/前端/框架/Electron/拓展/vue打包.md' }] }
                            ]
                        },
                    ]
                },
                {
                    text: '工具', collapsed: true, items: [
                        { text: 'IDE', collapsed: true, items: set_sidebar("/docs/前端/工具/IDE") },
                    ]
                },
                { text: '其他', collapsed: true, items: set_sidebar("/docs/前端/其他") }
            ]
        },
        {
            text: '后端',
            collapsed: true,
            items: [
                { text: 'Go', collapsed: true, items: set_sidebar("/docs/后端/Go") },
                {
                    text: 'Java', collapsed: true, link: '/docs/后端/Java', items: [
                        { text: 'JavaSE', link: '/docs/后端/Java/JavaSE' },
                        { text: 'JavaWeb', link: '/docs/后端/Java/JavaWeb' },
                        { text: 'JDBC', link: '/docs/后端/Java/JDBC' },
                        {
                            text: 'Java框架', collapsed: true, link: '/docs/后端/Java/Java框架',
                            items: [
                                { text: '框架基本概念', link: '/docs/后端/Java/Java框架/框架基本概念.md' },
                                { text: 'Spring', link: '/docs/后端/Java/Java框架/Spring' },
                                { text: 'SpringBoot', link: '/docs/后端/Java/Java框架/SpringBoot' },
                                { text: 'Spring Cloud', link: '/docs/后端/Java/Java框架/SpringCloud' },
                                { text: 'MyBatis', link: '/docs/后端/Java/Java框架/MyBatis' },
                                { text: 'MyBatis Plus', link: '/docs/后端/Java/Java框架/MyBatisPlus' },
                                { text: 'Sa-token', link: '/docs/后端/Java/Java框架/Sa-token' },
                            ]
                        },
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
                { text: 'Python', collapsed: true, items: set_sidebar("/docs/后端/Python") },

            ]
        },
        {
            text: '其他',
            collapsed: true,
            items: set_sidebar("/docs/其他")
        },
    ],
    "/project": [
        {
            text: '通用权限项目',
            collapsed: true,
            items: [
                {
                    text: '通用权限项目(一)', collapsed: true, link: '/project/通用权限项目/通用权限项目(一)/index', items: [
                        { text: '项目介绍', link: '/project/通用权限项目/通用权限项目(一)/项目介绍' },
                        { text: '项目搭建', link: '/project/通用权限项目/通用权限项目(一)/项目搭建' },
                    ]
                },
                { text: '通用权限项目(二)', link: '/project/通用权限项目/通用权限项目(二)/index' },
            ]
        },
    ],
    "/other": set_sidebar("/other") 
}