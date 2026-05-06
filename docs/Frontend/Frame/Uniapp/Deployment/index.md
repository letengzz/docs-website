# Uniapp 打包与发布

## H5 打包

### 开发环境

```bash [终端]
npm run dev:h5
```

### 生产环境

```bash [终端]
npm run build:h5
```

### 配置

```javascript [vite.config.js]
import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'

export default defineConfig({
  plugins: [uni()],
  build: {
    outDir: 'dist/build/h5',
    assetsDir: 'static',
    rollupOptions: {
      output: {
        chunkFileNames: 'static/js/[name]-[hash].js',
        entryFileNames: 'static/js/[name]-[hash].js',
        assetFileNames: 'static/[ext]/[name]-[hash].[ext]'
      }
    }
  }
})
```

### 部署

将 `dist/build/h5` 目录下的文件部署到服务器：

```bash [终端]
# 使用 nginx 配置
server {
    listen 80;
    server_name example.com;
    root /path/to/dist/build/h5;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## 微信小程序发布

### 开发环境

```bash [终端]
npm run dev:mp-weixin
```

### 生产环境

```bash [终端]
npm run build:mp-weixin
```

### 上传发布

1. 打开微信开发者工具
2. 导入 `dist/build/mp-weixin` 目录
3. 点击 上传 按钮
4. 填写版本号和项目备注
5. 登录 [微信公众平台](https://mp.weixin.qq.com/) 提交审核

### 小程序配置

```json [manifest.json]
{
  "mp-weixin": {
    "appid": "wx1234567890",
    "setting": {
      "urlCheck": false,
      "es6": true,
      "postcss": true,
      "minified": true
    },
    "usingComponents": true,
    "permission": {
      "scope.userLocation": {
        "desc": "你的位置信息将用于小程序位置接口的效果展示"
      }
    },
    "requiredPrivateInfos": [
      "getLocation",
      "chooseLocation"
    ]
  }
}
```

## App 打包

### 云打包

在 HBuilderX 中操作：

1. 点击 发行 → 原生 App-云打包
2. 选择打包平台（iOS/Android）
3. 填写应用信息
4. 点击打包

### 离线打包

#### Android 离线打包

1. 下载 [Android 离线打包 SDK](https://nativesupport.dcloud.net.cn/AppDocs/download/android)
2. 使用 Android Studio 打开项目
3. 配置应用信息
4. 点击 Build → Generate Signed Bundle / APK

#### iOS 离线打包

1. 下载 [iOS 离线打包 SDK](https://nativesupport.dcloud.net.cn/AppDocs/download/ios)
2. 使用 Xcode 打开项目
3. 配置应用信息
4. 点击 Product → Archive

### 应用配置

```json [manifest.json]
{
  "app-plus": {
    "usingComponents": true,
    "nvueCompiler": "uni-app",
    "splashscreen": {
      "alwaysShowBeforeRender": true,
      "waiting": true,
      "autoclose": true,
      "delay": 0
    },
    "distribute": {
      "android": {
        "permissions": [
          "<uses-permission android:name=\"android.permission.INTERNET\"/>",
          "<uses-permission android:name=\"android.permission.ACCESS_NETWORK_STATE\"/>",
          "<uses-permission android:name=\"android.permission.ACCESS_WIFI_STATE\"/>",
          "<uses-permission android:name=\"android.permission.CAMERA\"/>",
          "<uses-permission android:name=\"android.permission.WRITE_EXTERNAL_STORAGE\"/>"
        ],
        "abiFilters": ["armeabi-v7a", "arm64-v8a", "x86"],
        "targetSdkVersion": 30,
        "minSdkVersion": 21
      },
      "ios": {
        "dSYMs": false,
        "privacyDescription": {
          "NSPhotoLibraryUsageDescription": "用于选择照片",
          "NSCameraUsageDescription": "用于拍照",
          "NSLocationWhenInUseUsageDescription": "用于获取位置信息"
        }
      },
      "sdkConfigs": {
        "maps": {
          "amap": {
            "appkey_ios": "",
            "appkey_android": ""
          }
        },
        "oauth": {
          "weixin": {
            "appid": "",
            "appsecret": "",
            "UniversalLinks": ""
          }
        },
        "payment": {
          "weixin": {
            "__platform__": ["ios", "android"],
            "appid": "",
            "UniversalLinks": ""
          }
        },
        "push": {
          "unipush": {}
        }
      },
      "icons": {
        "android": {
          "hdpi": "unpackage/res/icons/72x72.png",
          "xhdpi": "unpackage/res/icons/96x96.png",
          "xxhdpi": "unpackage/res/icons/144x144.png",
          "xxxhdpi": "unpackage/res/icons/192x192.png"
        },
        "ios": {
          "appstore": "unpackage/res/icons/1024x1024.png",
          "ipad": {
            "app": "unpackage/res/icons/76x76.png",
            "app@2x": "unpackage/res/icons/152x152.png",
            "notification": "unpackage/res/icons/20x20.png",
            "notification@2x": "unpackage/res/icons/40x40.png",
            "proapp@2x": "unpackage/res/icons/167x167.png",
            "settings": "unpackage/res/icons/29x29.png",
            "settings@2x": "unpackage/res/icons/58x58.png",
            "spotlight": "unpackage/res/icons/40x40.png",
            "spotlight@2x": "unpackage/res/icons/80x80.png"
          },
          "iphone": {
            "app@2x": "unpackage/res/icons/120x120.png",
            "app@3x": "unpackage/res/icons/180x180.png",
            "notification@2x": "unpackage/res/icons/40x40.png",
            "notification@3x": "unpackage/res/icons/60x60.png",
            "settings@2x": "unpackage/res/icons/58x58.png",
            "settings@3x": "unpackage/res/icons/87x87.png",
            "spotlight@2x": "unpackage/res/icons/80x80.png",
            "spotlight@3x": "unpackage/res/icons/120x120.png"
          }
        }
      },
      "splashscreen": {
        "android": {
          "hdpi": "unpackage/res/splash/480x762.png",
          "xhdpi": "unpackage/res/splash/720x1242.png",
          "xxhdpi": "unpackage/res/splash/1080x1882.png"
        },
        "ios": {
          "iphone": {
            "portrait-896h@3x": "unpackage/res/splash/1242x2688.png",
            "portrait-896h@2x": "unpackage/res/splash/828x1792.png"
          }
        }
      }
    }
  }
}
```

## 热更新

### 生成 wgt 包

在 HBuilderX 中操作：

1. 点击 发行 → 原生 App-制作移动 App 资源升级包
2. 填写版本号
3. 生成 wgt 文件

### 应用内更新

```vue
<script setup>
const checkUpdate = async () => {
  const res = await fetch('/api/app/version')
  const data = await res.json()

  const currentVersion = plus.runtime.version
  const latestVersion = data.version

  if (latestVersion !== currentVersion) {
    uni.showModal({
      title: '发现新版本',
      content: data.description,
      success: (res) => {
        if (res.confirm) {
          downloadUpdate(data.wgtUrl)
        }
      }
    })
  }
}

const downloadUpdate = (url) => {
  uni.showLoading({ title: '下载中...' })

  uni.downloadFile({
    url: url,
    success: (res) => {
      if (res.statusCode === 200) {
        plus.runtime.install(res.tempFilePath, {
          force: false
        }, () => {
          uni.hideLoading()
          plus.runtime.restart()
        }, (e) => {
          uni.hideLoading()
          uni.showToast({ title: '安装失败', icon: 'none' })
        })
      }
    }
  })
}
</script>
```

## 发布检查清单

### H5 发布

- [ ] 代码压缩和混淆
- [ ] 图片资源优化
- [ ] CDN 配置
- [ ] HTTPS 配置
- [ ] 域名备案

### 小程序发布

- [ ] 小程序名称和简介
- [ ] 小程序图标
- [ ] 服务类目
- [ ] 隐私协议
- [ ] 测试版本
- [ ] 提交审核

### App 发布

- [ ] 应用名称和图标
- [ ] 应用描述
- [ ] 权限配置
- [ ] 签名证书
- [ ] 隐私协议
- [ ] 应用市场审核
