# Electron 打包应用

## electron-builder

### 安装

```bash [终端]
npm install electron-builder -D
```

### 基础配置

```json [package.json]
{
  "name": "my-electron-app",
  "version": "1.0.0",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "build": "electron-builder",
    "build:win": "electron-builder --win",
    "build:mac": "electron-builder --mac",
    "build:linux": "electron-builder --linux"
  },
  "build": {
    "appId": "com.example.myapp",
    "productName": "我的应用",
    "directories": {
      "output": "release"
    },
    "files": [
      "main.js",
      "preload.js",
      "dist/**/*",
      "assets/**/*"
    ],
    "win": {
      "icon": "./assets/icon.ico",
      "target": [
        {
          "target": "nsis",
          "arch": ["x64"]
        }
      ]
    },
    "nsis": {
      "oneClick": false,
      "perMachine": true,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    },
    "mac": {
      "icon": "./assets/icon.icns",
      "category": "public.app-category.utilities",
      "target": ["dmg", "zip"]
    },
    "linux": {
      "icon": "./assets/icon.png",
      "category": "Utility",
      "target": ["AppImage", "deb"]
    }
  }
}
```

### 执行打包

```bash [终端]
# 打包所有平台
npm run build

# 仅打包 Windows
npm run build:win

# 仅打包 macOS
npm run build:mac

# 仅打包 Linux
npm run build:linux
```

## NSIS 安装程序配置

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `oneClick` | boolean | true | 一键安装 |
| `perMachine` | boolean | false | 每台机器安装 |
| `allowToChangeInstallationDirectory` | boolean | false | 允许更改安装目录 |
| `createDesktopShortcut` | boolean | true | 创建桌面快捷方式 |
| `createStartMenuShortcut` | boolean | true | 创建开始菜单快捷方式 |
| `shortcutName` | string | - | 快捷方式名称 |
| `installerIcon` | string | - | 安装程序图标 |
| `uninstallerIcon` | string | - | 卸载程序图标 |
| `installerHeaderIcon` | string | - | 安装程序头部图标 |
| `deleteAppDataOnUninstall` | boolean | false | 卸载时删除应用数据 |

## 平台特定配置

### Windows

```json [package.json]
{
  "build": {
    "win": {
      "icon": "./assets/icon.ico",
      "target": [
        {
          "target": "nsis",
          "arch": ["x64", "ia32"]
        },
        {
          "target": "portable",
          "arch": ["x64"]
        }
      ],
      "sign": "./sign.js",
      "certificateFile": "./cert.pfx",
      "certificatePassword": "password"
    }
  }
}
```

### macOS

```json [package.json]
{
  "build": {
    "mac": {
      "icon": "./assets/icon.icns",
      "category": "public.app-category.utilities",
      "target": ["dmg", "zip"],
      "hardenedRuntime": true,
      "gatekeeperAssess": false,
      "entitlements": "./build/entitlements.mac.plist",
      "entitlementsInherit": "./build/entitlements.mac.plist"
    },
    "dmg": {
      "sign": false,
      "contents": [
        { "x": 130, "y": 220 },
        { "x": 410, "y": 220, "type": "link", "path": "/Applications" }
      ]
    }
  }
}
```

### Linux

```json [package.json]
{
  "build": {
    "linux": {
      "icon": "./assets/icon.png",
      "category": "Utility",
      "target": ["AppImage", "deb", "rpm"],
      "maintainer": "example@example.com",
      "vendor": "My Company",
      "synopsis": "我的应用简介",
      "description": "我的应用详细描述"
    }
  }
}
```

## 自动更新配置

```json [package.json]
{
  "build": {
    "publish": {
      "provider": "github",
      "owner": "username",
      "repo": "my-electron-app",
      "releaseType": "release"
    }
  }
}
```

## 代码签名

### Windows 签名

```javascript [sign.js]
exports.default = async function (configuration) {
  // 自定义签名逻辑
}
```

### macOS 签名

```json [package.json]
{
  "build": {
    "mac": {
      "hardenedRuntime": true,
      "gatekeeperAssess": false,
      "entitlements": "./build/entitlements.mac.plist",
      "entitlementsInherit": "./build/entitlements.mac.plist"
    }
  }
}
```

## 优化打包体积

```json [package.json]
{
  "build": {
    "files": [
      "main.js",
      "preload.js",
      "dist/**/*",
      "assets/**/*"
    ],
    "extraResources": [
      {
        "from": "resources",
        "to": "resources",
        "filter": ["**/*"]
      }
    ],
    "asar": true,
    "compression": "maximum"
  }
}
```

