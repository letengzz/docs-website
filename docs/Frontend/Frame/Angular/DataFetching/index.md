# Angular 数据获取

Angular 提供了多种数据获取方式，包括 HttpClient、Signals 和 RxJS。

## HttpClient

### 配置

```typescript [src/app/app.config.ts]
import { ApplicationConfig } from '@angular/core'
import { provideRouter } from '@angular/router'
import { provideHttpClient } from '@angular/common/http'
import { routes } from './app.routes'

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient()
  ]
}
```

### 基本使用

```typescript [src/app/services/user.service.ts]
import { Injectable, inject } from '@angular/core'
import { HttpClient } from '@angular/common/http'
import { Observable } from 'rxjs'

export interface User {
  id: number
  name: string
  email: string
}

@Injectable({ providedIn: 'root' })
export class UserService {
  private http = inject(HttpClient)
  private apiUrl = '/api/users'

  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(this.apiUrl)
  }

  getUser(id: number): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/${id}`)
  }

  createUser(user: Omit<User, 'id'>): Observable<User> {
    return this.http.post<User>(this.apiUrl, user)
  }

  updateUser(id: number, user: Partial<User>): Observable<User> {
    return this.http.put<User>(`${this.apiUrl}/${id}`, user)
  }

  deleteUser(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`)
  }
}
```

### 组件中使用

```typescript [src/app/components/user-list.component.ts]
import { Component, inject, OnInit } from '@angular/core'
import { CommonModule } from '@angular/common'
import { UserService, User } from '../services/user.service'

@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [CommonModule],
  template: `
    @if (loading) {
      <p>加载中...</p>
    } @else if (error) {
      <p class="error">{{ error }}</p>
    } @else {
      <ul>
        @for (user of users; track user.id) {
          <li>{{ user.name }} - {{ user.email }}</li>
        } @empty {
          <p>暂无用户</p>
        }
      </ul>
    }
  `
})
export class UserListComponent implements OnInit {
  private userService = inject(UserService)
  users: User[] = []
  loading = false
  error: string | null = null

  ngOnInit() {
    this.loadUsers()
  }

  loadUsers() {
    this.loading = true
    this.error = null
    this.userService.getUsers().subscribe({
      next: (data) => {
        this.users = data
        this.loading = false
      },
      error: (err) => {
        this.error = '加载失败'
        this.loading = false
      }
    })
  }
}
```

## RxJS 操作符

### 错误处理

```typescript
import { catchError, retry } from 'rxjs/operators'
import { throwError } from 'rxjs'

this.http.get<User[]>('/api/users').pipe(
  retry(3),
  catchError(error => {
    console.error('请求失败:', error)
    return throwError(() => new Error('加载失败'))
  })
).subscribe({
  next: data => this.users = data,
  error: err => this.error = err.message
})
```

### 组合请求

```typescript
import { forkJoin, switchMap } from 'rxjs/operators'

// 并行请求
forkJoin({
  users: this.http.get<User[]>('/api/users'),
  roles: this.http.get<Role[]>('/api/roles')
}).subscribe(({ users, roles }) => {
  this.users = users
  this.roles = roles
})

// 串行请求
this.http.get<User>('/api/users/1').pipe(
  switchMap(user => this.http.get<Order[]>(`/api/users/${user.id}/orders`))
).subscribe(orders => {
  this.orders = orders
})
```

## Signals 数据获取

```typescript [src/app/components/signal-user.component.ts]
import { Component, inject, OnInit, signal } from '@angular/core'
import { UserService, User } from '../services/user.service'

@Component({
  selector: 'app-signal-user',
  template: `
    @if (loading()) {
      <p>加载中...</p>
    } @else {
      <ul>
        @for (user of users(); track user.id) {
          <li>{{ user.name }}</li>
        }
      </ul>
    }
  `
})
export class SignalUserComponent implements OnInit {
  private userService = inject(UserService)
  users = signal<User[]>([])
  loading = signal(false)

  ngOnInit() {
    this.loadUsers()
  }

  loadUsers() {
    this.loading.set(true)
    this.userService.getUsers().subscribe({
      next: data => {
        this.users.set(data)
        this.loading.set(false)
      },
      error: () => this.loading.set(false)
    })
  }
}
```

## 异步管道

```typescript [src/app/components/async-user.component.ts]
import { Component, inject, OnInit } from '@angular/core'
import { CommonModule } from '@angular/common'
import { Observable } from 'rxjs'
import { UserService, User } from '../services/user.service'

@Component({
  selector: 'app-async-user',
  standalone: true,
  imports: [CommonModule],
  template: `
    <ul>
      <li *ngFor="let user of users$ | async">{{ user.name }}</li>
    </ul>
  `
})
export class AsyncUserComponent {
  private userService = inject(UserService)
  users$: Observable<User[]>

  constructor() {
    this.users$ = this.userService.getUsers()
  }
}
```

