# Angular 表单处理

Angular 提供了两种表单处理方式：模板驱动表单和响应式表单。

## 模板驱动表单

适用于简单表单，逻辑主要在模板中。

### 配置

```typescript [src/app/app.config.ts]
import { ApplicationConfig } from '@angular/core'
import { provideRouter } from '@angular/router'
import { provideHttpClient } from '@angular/common/http'
import { FormsModule } from '@angular/forms'
import { routes } from './app.routes'

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient()
  ]
}
```

```typescript [src/app/app.component.ts]
import { Component } from '@angular/core'
import { FormsModule } from '@angular/forms'

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './app.component.html'
})
export class AppComponent {}
```

### 基础使用

```html [src/app/components/login.component.html]
<form #loginForm="ngForm" (ngSubmit)="onSubmit(loginForm)">
  <div>
    <label>邮箱</label>
    <input 
      type="email" 
      name="email" 
      ngModel 
      #email="ngModel"
      required 
      email
      placeholder="请输入邮箱">
    
    @if (email.invalid && email.touched) {
      <p class="error">
        @if (email.errors?.['required']) { 邮箱不能为空 }
        @if (email.errors?.['email']) { 邮箱格式不正确 }
      </p>
    }
  </div>
  
  <div>
    <label>密码</label>
    <input 
      type="password" 
      name="password" 
      ngModel 
      #password="ngModel"
      required 
      minlength="6"
      placeholder="请输入密码">
    
    @if (password.invalid && password.touched) {
      <p class="error">
        @if (password.errors?.['required']) { 密码不能为空 }
        @if (password.errors?.['minlength']) { 密码至少6位 }
      </p>
    }
  </div>
  
  <button type="submit" [disabled]="loginForm.invalid">登录</button>
</form>
```

```typescript [src/app/components/login.component.ts]
import { Component } from '@angular/core'
import { FormsModule, NgForm } from '@angular/forms'

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html'
})
export class LoginComponent {
  onSubmit(form: NgForm) {
    if (form.valid) {
      console.log('表单数据:', form.value)
    }
  }
}
```

## 响应式表单

适用于复杂表单，逻辑在组件中。

### 配置

```typescript [src/app/app.config.ts]
import { ReactiveFormsModule } from '@angular/forms'

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient()
  ]
}
```

```typescript [src/app/app.component.ts]
import { Component } from '@angular/core'
import { ReactiveFormsModule } from '@angular/forms'

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './app.component.html'
})
export class AppComponent {}
```

### 基础使用

```typescript [src/app/components/register.component.ts]
import { Component, inject, OnInit } from '@angular/core'
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms'
import { CommonModule } from '@angular/common'

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './register.component.html'
})
export class RegisterComponent implements OnInit {
  private fb = inject(FormBuilder)
  registerForm!: FormGroup

  ngOnInit() {
    this.registerForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', [Validators.required]],
      agree: [false, [Validators.requiredTrue]]
    }, { validators: this.passwordMatchValidator })
  }

  passwordMatchValidator(form: FormGroup) {
    const password = form.get('password')?.value
    const confirmPassword = form.get('confirmPassword')?.value
    return password === confirmPassword ? null : { passwordMismatch: true }
  }

  onSubmit() {
    if (this.registerForm.valid) {
      console.log('表单数据:', this.registerForm.value)
    } else {
      this.registerForm.markAllAsTouched()
    }
  }

  get f() {
    return this.registerForm.controls
  }
}
```

```html [src/app/components/register.component.html]
<form [formGroup]="registerForm" (ngSubmit)="onSubmit()">
  <div>
    <label>用户名</label>
    <input type="text" formControlName="username" placeholder="请输入用户名">
    @if (f['username'].invalid && f['username'].touched) {
      <p class="error">
        @if (f['username'].errors?.['required']) { 用户名不能为空 }
        @if (f['username'].errors?.['minlength']) { 用户名至少3位 }
      </p>
    }
  </div>

  <div>
    <label>邮箱</label>
    <input type="email" formControlName="email" placeholder="请输入邮箱">
    @if (f['email'].invalid && f['email'].touched) {
      <p class="error">
        @if (f['email'].errors?.['required']) { 邮箱不能为空 }
        @if (f['email'].errors?.['email']) { 邮箱格式不正确 }
      </p>
    }
  </div>

  <div>
    <label>密码</label>
    <input type="password" formControlName="password" placeholder="请输入密码">
    @if (f['password'].invalid && f['password'].touched) {
      <p class="error">
        @if (f['password'].errors?.['required']) { 密码不能为空 }
        @if (f['password'].errors?.['minlength']) { 密码至少6位 }
      </p>
    }
  </div>

  <div>
    <label>确认密码</label>
    <input type="password" formControlName="confirmPassword" placeholder="请再次输入密码">
    @if (f['confirmPassword'].invalid && f['confirmPassword'].touched) {
      <p class="error">
        @if (f['confirmPassword'].errors?.['required']) { 请再次输入密码 }
        @if (registerForm.errors?.['passwordMismatch']) { 两次密码不一致 }
      </p>
    }
  </div>

  <div>
    <label>
      <input type="checkbox" formControlName="agree">
      同意用户协议
    </label>
    @if (f['agree'].invalid && f['agree'].touched) {
      <p class="error">请同意用户协议</p>
    }
  </div>

  <button type="submit" [disabled]="registerForm.invalid">注册</button>
</form>
```

## 表单数组

```typescript
import { Component, inject, OnInit } from '@angular/core'
import { FormBuilder, FormGroup, FormArray, Validators, ReactiveFormsModule } from '@angular/forms'

@Component({
  selector: 'app-order',
  standalone: true,
  imports: [ReactiveFormsModule],
  template: `
    <form [formGroup]="orderForm" (ngSubmit)="onSubmit()">
      <div formArrayName="items">
        @for (item of items.controls; track item; let i = $index) {
          <div [formGroupName]="i">
            <input formControlName="name" placeholder="商品名称">
            <input formControlName="quantity" type="number" placeholder="数量">
            <input formControlName="price" type="number" placeholder="价格">
            <button type="button" (click)="removeItem(i)">删除</button>
          </div>
        }
      </div>
      <button type="button" (click)="addItem()">添加商品</button>
      <button type="submit" [disabled]="orderForm.invalid">提交</button>
    </form>
  `
})
export class OrderComponent implements OnInit {
  private fb = inject(FormBuilder)
  orderForm!: FormGroup

  ngOnInit() {
    this.orderForm = this.fb.group({
      items: this.fb.array([])
    })
  }

  get items() {
    return this.orderForm.get('items') as FormArray
  }

  createItem(): FormGroup {
    return this.fb.group({
      name: ['', Validators.required],
      quantity: [1, [Validators.required, Validators.min(1)]],
      price: [0, [Validators.required, Validators.min(0)]]
    })
  }

  addItem() {
    this.items.push(this.createItem())
  }

  removeItem(index: number) {
    this.items.removeAt(index)
  }

  onSubmit() {
    if (this.orderForm.valid) {
      console.log('订单数据:', this.orderForm.value)
    }
  }
}
```

## 自定义验证器

```typescript
import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms'

export function phoneValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const value = control.value
    if (!value) return null
    const valid = /^1[3-9]\d{9}$/.test(value)
    return valid ? null : { phone: true }
  }
}

export function idCardValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const value = control.value
    if (!value) return null
    const valid = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/.test(value)
    return valid ? null : { idCard: true }
  }
}
```

```typescript
// 使用自定义验证器
this.form = this.fb.group({
  phone: ['', [Validators.required, phoneValidator()]],
  idCard: ['', [Validators.required, idCardValidator()]]
})
```

## 表单对比

| 特性 | 模板驱动表单 | 响应式表单 |
|------|-------------|-----------|
| 适用场景 | 简单表单 | 复杂表单 |
| 逻辑位置 | 模板中 | 组件中 |
| 数据流 | 双向绑定 | 单向数据流 |
| 测试性 | 较低 | 较高 |
| 动态表单 | 困难 | 容易 |
| 验证器 | 模板指令 | 组件代码 |

