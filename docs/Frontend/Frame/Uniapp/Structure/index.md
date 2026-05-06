# Uniapp 项目结构

## 标准项目结构

```
my-uniapp/
├── static/              # 静态资源（图片、字体等）
├── pages/               # 页面目录
│   ├── index/
│   │   ├── index.vue    # 页面文件
│   │   └── index.css    # 页面样式（可选）
│   └── about/
│       └── index.vue
├── components/          # 公共组件
│   └── MyComponent.vue
├── uni_modules/         # uni_modules 插件目录
├── utils/               # 工具函数
│   └── request.js
├── store/               # 状态管理
│   └── index.js
├── App.vue              # 应用配置，配置应用全局样式和生命周期
├── main.js              # 入口文件
├── pages.json           # 页面配置，配置页面路由、窗口样式等
├── manifest.json        # 应用配置，配置应用名称、图标、权限等
├── uni.scss             # 全局 SCSS 变量
├── package.json         # 项目依赖
└── vite.config.js       # Vite 配置
```

## 核心文件说明

### App.vue

应用根组件，配置全局样式和应用生命周期：

```vue [App.vue]
<script>
export default {
  onLaunch() {
    console.log('应用启动')
  },
  onShow() {
    console.log('应用显示')
  },
  onHide() {
    console.log('应用隐藏')
  }
}
</script>

<style>
/* 全局样式 */
page {
  background-color: #f5f5f5;
  font-size: 14px;
  color: #333;
}

/* 全局组件样式 */
.container {
  padding: 20rpx;
}
</style>
```

### main.js

应用入口文件：

```javascript [main.js]
import { createSSRApp } from 'vue'
import App from './App.vue'

export function createApp() {
  const app = createSSRApp(App)
  return { app }
}
```

### pages.json

页面路由和窗口样式配置：

```json [pages.json]
{
  "pages": [
    {
      "path": "pages/index/index",
      "style": {
        "navigationBarTitleText": "首页"
      }
    },
    {
      "path": "pages/about/index",
      "style": {
        "navigationBarTitleText": "关于"
      }
    }
  ],
  "globalStyle": {
    "navigationBarTextStyle": "black",
    "navigationBarTitleText": "Uniapp",
    "navigationBarBackgroundColor": "#F8F8F8",
    "backgroundColor": "#F8F8F8"
  },
  "tabBar": {
    "color": "#7A7E83",
    "selectedColor": "#3cc51f",
    "borderStyle": "black",
    "backgroundColor": "#ffffff",
    "list": [
      {
        "pagePath": "pages/index/index",
        "iconPath": "static/home.png",
        "selectedIconPath": "static/home-active.png",
        "text": "首页"
      },
      {
        "pagePath": "pages/about/index",
        "iconPath": "static/about.png",
        "selectedIconPath": "static/about-active.png",
        "text": "关于"
      }
    ]
  }
}
```

### manifest.json

应用配置文件：

```json [manifest.json]
{
  "name": "my-uniapp",
  "appid": "__UNI__XXXXXXX",
  "description": "应用描述",
  "versionName": "1.0.0",
  "versionCode": "100",
  "transformPx": false,
  "app-plus": {
    "usingComponents": true,
    "splashscreen": {
      "alwaysShowBeforeRender": true,
      "waiting": true,
      "autoclose": true,
      "delay": 0
    },
    "modules": {},
    "distribute": {
      "android": {
        "permissions": [
          "<uses-permission android:name=\"android.permission.INTERNET\"/>"
        ]
      },
      "ios": {},
      "sdkConfigs": {}
    }
  },
  "mp-weixin": {
    "appid": "",
    "setting": {
      "urlCheck": false
    },
    "usingComponents": true
  }
}
```

## 页面配置选项

### 页面样式配置

| 配置项 | 说明 | 类型 |
|--------|------|------|
| `navigationBarBackgroundColor` | 导航栏背景颜色 | String |
| `navigationBarTextStyle` | 导航栏标题颜色（white/black） | String |
| `navigationBarTitleText` | 导航栏标题文字内容 | String |
| `backgroundColor` | 页面背景颜色 | String |
| `backgroundTextStyle` | 下拉 loading 样式（dark/light） | String |
| `enablePullDownRefresh` | 是否开启下拉刷新 | Boolean |
| `onReachBottomDistance` | 页面上拉触底距离 | Number |

### 页面导航配置

```json [pages.json]
{
  "pages": [
    {
      "path": "pages/detail/index",
      "style": {
        "navigationBarTitleText": "详情页",
        "enablePullDownRefresh": true,
        "onReachBottomDistance": 50,
        "app-plus": {
          "titleNView": {
            "buttons": [
              {
                "text": "\ue670",
                "fontSrc": "/static/uni.ttf",
                "fontSize": "22px"
              }
            ]
          }
        }
      }
    }
  ]
}
```

## 条件编译目录

```
├── platform/
│   ├── h5/          # 仅 H5 平台
│   ├── mp-weixin/   # 仅微信小程序
│   └── app-plus/    # 仅 App 平台
```

## uni_modules 规范

```
uni_modules/
└── uni-ui/
    ├── components/           # 组件目录
    ├── changelog.md          # 更新日志
    ├── package.json          # 插件配置
    └── readme.md             # 使用说明
```
