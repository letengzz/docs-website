# Angular 路由系统

Angular Router 是 Angular 的官方路由库，提供了强大的路由功能。

## 路由配置

### 基础路由

```typescript [src/app/app.routes.ts]
import { Routes } from '@angular/router'
import { HomeComponent } from './components/home.component'
import { AboutComponent } from './components/about.component'
import { UserComponent } from './components/user.component'

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'about', component: AboutComponent },
  { path: 'users/:id', component: UserComponent },
  { path: '**', redirectTo: '' }
]
```

### 路由提供者

```typescript [src/app/app.config.ts]
import { ApplicationConfig } from '@angular/core'
import { provideRouter } from '@angular/router'
import { routes } from './app.routes'

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes)
  ]
}
```

## 路由出口

```html [src/app/app.component.html]
<nav>
  <a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: true }">首页</a>
  <a routerLink="/about" routerLinkActive="active">关于</a>
  <a routerLink="/users" routerLinkActive="active">用户</a>
</nav>
<router-outlet></router-outlet>
```

## 路由导航

### 声明式导航

```html
<!-- 基础链接 -->
<a routerLink="/dashboard">仪表盘</a>

<!-- 带参数的链接 -->
<a [routerLink]="['/users', userId]">用户详情</a>

<!-- 带查询参数 -->
<a [routerLink]="['/products']" [queryParams]="{ page: 1, category: 'all' }">产品</a>

<!-- 高亮链接 -->
<a routerLink="/profile" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: true }">个人中心</a>
```

### 编程式导航

```typescript [src/app/components/login.component.ts]
import { Component, inject } from '@angular/core'
import { Router } from '@angular/router'

@Component({
  selector: 'app-login',
  template: `<button (click)="login()">登录</button>`
})
export class LoginComponent {
  private router = inject(Router)
  
  async login() {
    await loginApi()
    this.router.navigate(['/dashboard'])
    // this.router.navigate(['/users', userId])
    // this.router.navigate(['/products'], { queryParams: { page: 1 } })
    // this.router.navigateByUrl('/dashboard')
  }
}
```

## 路由参数

### 路径参数

```typescript [src/app/components/user.component.ts]
import { Component, inject, OnInit } from '@angular/core'
import { ActivatedRoute } from '@angular/router'

@Component({
  selector: 'app-user',
  template: `<p>用户 ID: {{ userId }}</p>`
})
export class UserComponent implements OnInit {
  private route = inject(ActivatedRoute)
  userId: string = ''
  
  ngOnInit() {
    this.route.params.subscribe(params => {
      this.userId = params['id']
    })
    
    // 或使用 snapshot
    this.userId = this.route.snapshot.params['id']
  }
}
```

### 查询参数

```typescript
import { Component, inject, OnInit } from '@angular/core'
import { ActivatedRoute } from '@angular/router'

@Component({
  selector: 'app-products',
  template: `<p>页码: {{ page }}, 分类: {{ category }}</p>`
})
export class ProductsComponent implements OnInit {
  private route = inject(ActivatedRoute)
  page: number = 1
  category: string = 'all'
  
  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      this.page = Number(params['page']) || 1
      this.category = params['category'] || 'all'
    })
  }
}
```

### 状态传参

```typescript
// 导航时传递状态
this.router.navigate(['/detail'], { state: { from: 'list', productId: 123 } })

// 目标页面获取状态
import { Component, inject } from '@angular/core'
import { Router } from '@angular/router'

const navigation = this.router.getCurrentNavigation()
const state = navigation?.extras.state as { from: string; productId: number }
```

## 嵌套路由

```typescript [src/app/app.routes.ts]
export const routes: Routes = [
  {
    path: '',
    component: RootLayoutComponent,
    children: [
      { path: '', component: HomeComponent },
      {
        path: 'products',
        component: ProductsLayoutComponent,
        children: [
          { path: '', component: ProductListComponent },
          { path: ':id', component: ProductDetailComponent }
        ]
      },
      {
        path: 'users',
        component: UsersLayoutComponent,
        children: [
          { path: 'me', component: UserProfileComponent },
          { path: 'settings', component: UserSettingsComponent }
        ]
      }
    ]
  }
]
```

## 路由懒加载

```typescript [src/app/app.routes.ts]
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

### 模块懒加载

```typescript [src/app/admin/admin.routes.ts]
import { Routes } from '@angular/router'
import { AdminComponent } from './admin.component'

export const adminRoutes: Routes = [
  { path: '', component: AdminComponent },
  { path: 'users', loadComponent: () => import('./users.component').then(m => m.AdminUsersComponent) },
  { path: 'settings', loadComponent: () => import('./settings.component').then(m => m.AdminSettingsComponent) }
]
```

## 路由守卫

### CanActivate 守卫

```typescript [src/app/guards/auth.guard.ts]
import { inject } from '@angular/core'
import { CanActivateFn, Router } from '@angular/router'

export const authGuard: CanActivateFn = (route, state) => {
  const router = inject(Router)
  const isAuthenticated = checkAuth()
  
  if (!isAuthenticated) {
    router.navigate(['/login'], { queryParams: { returnUrl: state.url } })
    return false
  }
  
  return true
}
```

```typescript [src/app/app.routes.ts]
export const routes: Routes = [
  {
    path: 'dashboard',
    component: DashboardComponent,
    canActivate: [authGuard]
  }
]
```

## 404 与错误处理

```typescript
export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'about', component: AboutComponent },
  { path: '**', component: NotFoundComponent }
]
```

## 路由事件监听

```typescript
import { Component, inject, OnInit } from '@angular/core'
import { Router, NavigationStart, NavigationEnd, NavigationError } from '@angular/router'

@Component({
  selector: 'app-root',
  template: `<router-outlet></router-outlet>`
})
export class AppComponent implements OnInit {
  private router = inject(Router)
  
  ngOnInit() {
    this.router.events.subscribe(event => {
      if (event instanceof NavigationStart) {
        console.log('导航开始:', event.url)
      }
      if (event instanceof NavigationEnd) {
        console.log('导航结束:', event.url)
      }
      if (event instanceof NavigationError) {
        console.log('导航错误:', event.error)
      }
    })
  }
}
```

