# Angular 路由守卫

路由守卫用于在导航前后执行检查，控制用户是否可以访问特定路由。

## 守卫类型

| 守卫 | 说明 | 返回值 |
|------|------|--------|
| `CanActivate` | 控制是否可以激活路由 | `boolean` / `UrlTree` / `Observable` |
| `CanActivateChild` | 控制是否可以激活子路由 | `boolean` / `UrlTree` / `Observable` |
| `CanDeactivate` | 控制是否可以离开路由 | `boolean` / `UrlTree` / `Observable` |
| `Resolve` | 在激活路由前预加载数据 | `Observable` / `Promise` |
| `CanMatch` | 控制是否匹配路由 | `boolean` |

## CanActivate 守卫

### 函数式守卫（推荐）

```typescript [src/app/guards/auth.guard.ts]
import { inject } from '@angular/core'
import { CanActivateFn, Router } from '@angular/router'
import { AuthService } from '../services/auth.service'

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService)
  const router = inject(Router)
  
  if (authService.isAuthenticated()) {
    return true
  }
  
  return router.parseUrl('/login')
}
```

### 类守卫

```typescript [src/app/guards/role.guard.ts]
import { Injectable, inject } from '@angular/core'
import { CanActivateFn, Router, ActivatedRouteSnapshot } from '@angular/router'
import { AuthService } from '../services/auth.service'

export const roleGuard: CanActivateFn = (route: ActivatedRouteSnapshot) => {
  const authService = inject(AuthService)
  const router = inject(Router)
  
  const requiredRole = route.data['role']
  
  if (authService.hasRole(requiredRole)) {
    return true
  }
  
  return router.parseUrl('/unauthorized')
}
```

### 使用守卫

```typescript [src/app/app.routes.ts]
import { Routes } from '@angular/router'
import { authGuard } from './guards/auth.guard'
import { roleGuard } from './guards/role.guard'

export const routes: Routes = [
  {
    path: 'dashboard',
    component: DashboardComponent,
    canActivate: [authGuard]
  },
  {
    path: 'admin',
    component: AdminComponent,
    canActivate: [authGuard, roleGuard],
    data: { role: 'admin' }
  }
]
```

## CanDeactivate 守卫

用于防止用户在未保存更改时离开页面：

```typescript [src/app/guards/can-deactivate.guard.ts]
import { Injectable } from '@angular/core'
import { CanDeactivateFn } from '@angular/router'
import { Observable } from 'rxjs'

export interface CanComponentDeactivate {
  canDeactivate: () => Observable<boolean> | Promise<boolean> | boolean
}

export const canDeactivateGuard: CanDeactivateFn<CanComponentDeactivate> = (component) => {
  if (component.canDeactivate) {
    return component.canDeactivate()
  }
  return true
}
```

```typescript [src/app/components/edit.component.ts]
import { Component } from '@angular/core'
import { CanComponentDeactivate } from '../guards/can-deactivate.guard'

@Component({
  selector: 'app-edit',
  template: `
    <form [formGroup]="form">
      <input formControlName="name">
      <button (click)="save()">保存</button>
    </form>
  `
})
export class EditComponent implements CanComponentDeactivate {
  form = new FormGroup({ name: new FormControl('') })
  isDirty = false
  
  canDeactivate(): boolean {
    if (this.form.dirty) {
      return confirm('有未保存的更改，确定离开吗？')
    }
    return true
  }
}
```

```typescript [src/app/app.routes.ts]
export const routes: Routes = [
  {
    path: 'edit',
    component: EditComponent,
    canDeactivate: [canDeactivateGuard]
  }
]
```

## Resolve 守卫

在路由激活前预加载数据：

```typescript [src/app/resolvers/user.resolver.ts]
import { inject } from '@angular/core'
import { ResolveFn } from '@angular/router'
import { UserService } from '../services/user.service'

export const userResolver: ResolveFn<User> = (route) => {
  const userService = inject(UserService)
  const userId = route.params['id']
  return userService.getUser(userId)
}
```

```typescript [src/app/app.routes.ts]
export const routes: Routes = [
  {
    path: 'users/:id',
    component: UserDetailComponent,
    resolve: { user: userResolver }
  }
]
```

```typescript [src/app/components/user-detail.component.ts]
import { Component, inject, OnInit } from '@angular/core'
import { ActivatedRoute } from '@angular/router'

@Component({
  selector: 'app-user-detail',
  template: `<p>{{ user.name }}</p>`
})
export class UserDetailComponent implements OnInit {
  private route = inject(ActivatedRoute)
  user!: User
  
  ngOnInit() {
    this.user = this.route.snapshot.data['user']
  }
}
```

## 多个守卫组合

```typescript
export const routes: Routes = [
  {
    path: 'admin/settings',
    component: AdminSettingsComponent,
    canActivate: [authGuard, roleGuard],
    canDeactivate: [canDeactivateGuard],
    resolve: { settings: settingsResolver },
    data: { role: 'admin' }
  }
]
```

