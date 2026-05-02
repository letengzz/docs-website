# Angular 部署与优化

Angular 提供了多种部署方式和优化策略，确保应用在生产环境中高效运行。

## 构建命令

### 基础构建

```bash [终端]
# 开发构建
ng build

# 生产构建
ng build --configuration production

# 指定输出路径
ng build --output-path dist/my-app

# 监听模式
ng build --watch
```

## 部署方式

### 静态服务器部署

```bash [终端]
# 构建
ng build --configuration production

# 使用 http-server 预览
npx http-server dist/my-angular-app/browser
```

### Nginx 部署

```nginx [nginx.conf]
server {
  listen 80;
  server_name example.com;
  root /var/www/my-angular-app/browser;
  index index.html;

  location / {
    try_files $uri $uri/ /index.html;
  }

  location /api {
    proxy_pass http://localhost:3000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }

  # 缓存静态资源
  location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
  }
}
```

### Docker 部署

```dockerfile [Dockerfile]
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build -- --configuration production

FROM nginx:alpine
COPY --from=build /app/dist/my-angular-app/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```bash [终端]
# 构建镜像
docker build -t my-angular-app .

# 运行容器
docker run -p 80:80 my-angular-app
```

## 性能优化

### 懒加载

```typescript [src/app/app.routes.ts]
import { Routes } from '@angular/router'

export const routes: Routes = [
  {
    path: 'dashboard',
    loadComponent: () => import('./components/dashboard.component').then(m => m.DashboardComponent)
  },
  {
    path: 'admin',
    loadChildren: () => import('./admin/admin.routes').then(m => m.adminRoutes)
  }
]
```

### 延迟加载

```html
@defer (on viewport) {
  <app-heavy-component />
} @placeholder {
  <p>加载中...</p>
} @loading (minimum 1s) {
  <p>正在加载...</p>
} @error {
  <p>加载失败</p>
}
```

### OnPush 变更检测

```typescript
import { Component, ChangeDetectionStrategy } from '@angular/core'

@Component({
  selector: 'app-optimized',
  template: `<p>{{ data }}</p>`,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class OptimizedComponent {
  data: string = '初始数据'
  
  // 使用 markForCheck 或 immutable 数据更新
  updateData(newData: string) {
    this.data = newData
  }
}
```

### trackBy 优化

```html
<ul>
  @for (item of items; track item.id) {
    <li>{{ item.name }}</li>
  }
</ul>
```

### 虚拟滚动

```bash [终端]
npm install @angular/cdk
```

```typescript
import { Component } from '@angular/core'
import { ScrollingModule } from '@angular/cdk/scrolling'

@Component({
  selector: 'app-virtual-scroll',
  standalone: true,
  imports: [ScrollingModule],
  template: `
    <cdk-virtual-scroll-viewport itemSize="50" style="height: 500px">
      <div *cdkVirtualFor="let item of items" class="item">
        {{ item.name }}
      </div>
    </cdk-virtual-scroll-viewport>
  `
})
export class VirtualScrollComponent {
  items = Array.from({ length: 10000 }, (_, i) => ({ id: i, name: `Item ${i}` }))
}
```

## 构建优化配置

```json [angular.json]
{
  "architect": {
    "build": {
      "options": {
        "optimization": true,
        "aot": true,
        "buildOptimizer": true,
        "sourceMap": false,
        "extractLicenses": true,
        "vendorChunk": false
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
        }
      }
    }
  }
}
```

## 预渲染（SSR）

### 安装 SSR

```bash [终端]
ng add @angular/ssr
```

### 构建 SSR

```bash [终端]
# 构建 SSR 应用
ng build --configuration production

# 运行 SSR 服务器
node dist/my-angular-app/server/server.mjs
```

## 服务工作者（PWA）

### 安装 PWA

```bash [终端]
ng add @angular/pwa
```

### 配置

```json [ngsw-config.json]
{
  "index": "/index.html",
  "assetGroups": [
    {
      "name": "app",
      "installMode": "prefetch",
      "resources": {
        "files": [
          "/favicon.ico",
          "/index.html",
          "/*.css",
          "/*.js"
        ]
      }
    },
    {
      "name": "assets",
      "installMode": "lazy",
      "updateMode": "prefetch",
      "resources": {
        "files": [
          "/assets/**",
          "/*.(svg|cur|jpg|jpeg|png|apng|webp|avif|gif|otf|ttf|woff|woff2)"
        ]
      }
    }
  ]
}
```

## 性能监控

### 启用性能分析

```bash [终端]
# 构建性能分析
ng build --configuration production --stats-json

# 使用 webpack-bundle-analyzer
npx webpack-bundle-analyzer dist/my-angular-app/stats.json
```

### 运行时性能

```typescript
import { Component, inject, OnInit } from '@angular/core'
import { Router } from '@angular/router'

@Component({
  selector: 'app-root',
  template: `<router-outlet></router-outlet>`
})
export class AppComponent implements OnInit {
  private router = inject(Router)

  ngOnInit() {
    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        const perf = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
        console.log('页面加载时间:', perf.loadEventEnd - perf.startTime, 'ms')
      }
    })
  }
}
```

## 安全检查清单

- [ ] 启用 CSP（Content Security Policy）
- [ ] 移除 source map
- [ ] 配置 HTTPS
- [ ] 启用 HSTS
- [ ] 设置安全头
- [ ] 定期更新依赖
- [ ] 使用环境变量管理敏感信息
- [ ] 启用 CORS 限制
- [ ] 验证用户输入
- [ ] 使用 HTTPS API
