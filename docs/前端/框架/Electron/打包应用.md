# Electron 打包应用

使用 electron-builder 打包应用：

1. 安装 ﻿electron-builder﻿：

   ```shell
   npm install electron-builder -D
   ```

2. 在﻿package.json﻿ 中进行相关配置：

   **说明**：Json 文件不支持注释，使用时请去掉所有注释。

   ```json
   {
       "name": "video-tools", // 应用程序的名称
       "version": "1.0.0", // 应用程序的版本
       "main": "main.js", // 应用程序的入口文件
       "scripts": {
           "start": "electron .", // 使用 `electron .` 命令启动应用程序
           "build": "electron-builder" // 使用 `electron-builder` 打包应用程序，生成安装包
       },
       "build": {
           "appId": "com.hjc.video", // 应用程序的唯一标识符
           // 打包windows平台安装包的具体配置
           "win": {
               "icon": "./logo.ico", //应用图标
               "target": [
                   {
                       "target": "nsis", // 指定使用 NSIS 作为安装程序格式
                       "arch": [
                           "x64"
                       ] // 生成 64 位安装包
                   }
               ]
           },
           "nsis": {
               "oneClick": false, // 设置为 `false` 使安装程序显示安装向导界面，而不是一键安装
               "perMachine": true, // 允许每台机器安装一次，而不是每个用户都安装
               "allowToChangeInstallationDirectory": true // 允许用户在安装过程中选择安装目录
           }
       },
       "devDependencies": {
           "electron": "^30.0.0", // 开发依赖中的 Electron 版本
           "electron-builder": "^24.13.3" // 开发依赖中的 `electron-builder` 版本
       },
       "author": "hjc", // 作者信息
       "license": "ISC", // 许可证信息
       "description": "A video processing program based on Electron" // 应用程序的描述
   }
   ```

3. 执行打包命令：

   ```shell
   npm run build
   ```

   