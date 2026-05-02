# Angular 配置详解

Angular 提供了丰富的配置选项，允许你自定义构建、开发和生产行为。

## angular.json

### 基本配置

```json [angular.json]
{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "version": 1,
  "newProjectRoot": "projects",
  "projects": {
    "my-angular-app": {
      "projectType": "application",
      "root": "",
      "sourceRoot": "src",
      "prefix": "app",
      "architect": {
        "build": {
          "builder": "@angular/build:application",
          "options": {
            "outputPath": "dist/my-angular-app",
            "index": "src/index.html",
            "browser": "src/main.ts",
            "polyfills": ["zone.js"],
            "tsConfig": "tsconfig.app.json",
            "assets": [
              "src/assets",
              "src/favicon.ico"
            ],
            "styles": [
              "src/styles.scss"
            ],
            "scripts": []
          },
          "configurations": {
            "production": {
              "budgets": [
                {
                  "type": "initial",
                  "maximumWarning": "500kB",
                  "maximumError": "1MB"
                }
              ],
              "outputHashing": "all"
            },
            "development": {
              "optimization": false,
              "extractLicenses": false,
              "sourceMap": true
            }
          },
          "defaultConfiguration": "production"
        },
        "serve": {
          "builder": "@angular/build:dev-server",
          "configurations": {
            "production": {
              "buildTarget": "my-angular-app:build:production"
            },
            "development": {
              "buildTarget": "my-angular-app:build:development"
            }
          },
          "defaultConfiguration": "development"
        }
      }
    }
  }
}
```

## TypeScript 配置

### tsconfig.json

```json [tsconfig.json]
{
  "compileOnSave": false,
  "compilerOptions": {
    "outDir": "./dist/out-tsc",
    "forceConsistentCasingInFileNames": true,
    "strict": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "sourceMap": true,
    "declaration": false,
    "experimentalDecorators": true,
    "moduleResolution": "node",
    "importHelpers": true,
    "target": "ES2022",
    "module": "ES2022",
    "useDefineForClassFields": false,
    "lib": ["ES2022", "dom"]
  },
  "angularCompilerOptions": {
    "enableI18nLegacyMessageIdFormat": false,
    "strictInjectionParameters": true,
    "strictInputAccessModifiers": true,
    "strictTemplates": true
  }
}
```

## 环境配置

### 开发环境

```typescript [src/environments/environment.ts]
export const environment = {
  production: false,
  apiUrl: 'http://localhost:3000/api',
  debug: true
}
```

### 生产环境

```typescript [src/environments/environment.prod.ts]
export const environment = {
  production: true,
  apiUrl: 'https://api.example.com',
  debug: false
}
```

### 使用环境变量

```typescript [src/app/services/api.service.ts]
import { Injectable, inject } from '@angular/core'
import { HttpClient } from '@angular/common/http'
import { environment } from '../../environments/environment'

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient)
  private baseUrl = environment.apiUrl

  getData() {
    return this.http.get(`${this.baseUrl}/data`)
  }
}
```

## 样式配置

### 全局样式

```scss [src/styles.scss]
/* 全局变量 */
:root {
  --primary-color: #1976d2;
  --secondary-color: #424242;
  --font-family: 'Roboto', sans-serif;
}

/* 重置样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-family);
  color: var(--secondary-color);
}
```

### 组件样式

```typescript [src/app/components/styled.component.ts]
import { Component, ViewEncapsulation } from '@angular/core'

@Component({
  selector: 'app-styled',
  template: `<p class="text">样式文本</p>`,
  styles: [`
    .text {
      color: blue;
      font-size: 18px;
    }
  `],
  // 样式封装模式
  // encapsulation: ViewEncapsulation.Emulated (默认)
  // encapsulation: ViewEncapsulation.None (全局样式)
  // encapsulation: ViewEncapsulation.ShadowDom (Shadow DOM)
})
export class StyledComponent {}
```

## 代理配置

### 开发代理

```json [proxy.conf.json]
{
  "/api": {
    "target": "http://localhost:3000",
    "secure": false,
    "changeOrigin": true
  }
}
```

```json [angular.json]
{
  "architect": {
    "serve": {
      "options": {
        "proxyConfig": "proxy.conf.json"
      }
    }
  }
}
```

## 构建优化

### 预算配置

```json [angular.json]
{
  "architect": {
    "build": {
      "configurations": {
        "production": {
          "budgets": [
            {
              "type": "initial",
              "maximumWarning": "500kB",
              "maximumError": "1MB"
            },
            {
              "type": "anyComponentStyle",
              "maximumWarning": "2kB",
              "maximumError": "4kB"
            }
          ]
        }
      }
    }
  }
}
```

### 分析打包体积

```bash [终端]
# 构建并生成统计文件
ng build --stats-json

# 使用 webpack-bundle-analyzer 分析
npx webpack-bundle-analyzer dist/my-angular-app/stats.json
```

## 国际化（i18n）

### 配置

```json [angular.json]
{
  "architect": {
    "build": {
      "configurations": {
        "zh": {
          "localize": ["zh"],
          "i18nFile": "src/locale/messages.zh.xlf",
          "i18nFormat": "xlf",
          "i18nLocale": "zh"
        }
      }
    }
  }
}
```

### 使用

```html
<h1 i18n="标题|网站标题@@mainHeader">欢迎使用</h1>
<p i18n="描述|网站描述">这是一个示例网站</p>
```

```bash [终端]
# 提取翻译文件
ng extract-i18n --output-path src/locale

# 构建特定语言
ng build --configuration=zh
```

