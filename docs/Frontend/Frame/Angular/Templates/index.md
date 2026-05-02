# Angular 模板语法

Angular 模板语法基于 HTML，允许你使用数据绑定、指令和管道来构建动态视图。

## 数据绑定

### 插值表达式

使用 `{{ }}` 将组件属性显示在模板中：

```html [src/app/app.component.html]
<h1>{{ title }}</h1>
<p>当前用户: {{ user.name }}</p>
<p>计算结果: {{ 1 + 2 }}</p>
```

### 属性绑定

使用 `[property]` 绑定元素属性：

```html
<img [src]="imageUrl" [alt]="imageAlt">
<button [disabled]="isDisabled">提交</button>
<div [class.active]="isActive" [style.color]="textColor">内容</div>
```

### 事件绑定

使用 `(event)` 绑定事件处理：

```html
<button (click)="onClick()">点击</button>
<input (input)="onInput($event)" (keyup.enter)="onEnter()">
<form (ngSubmit)="onSubmit()">
  <button type="submit">提交</button>
</form>
```

### 双向绑定

使用 `[(ngModel)]` 实现双向数据绑定：

```html
<input [(ngModel)]="username" placeholder="用户名">
<p>输入的值: {{ username }}</p>
```

::: tip
使用 `ngModel` 需要导入 `FormsModule`：

```typescript
import { FormsModule } from '@angular/forms'

@Component({
  imports: [FormsModule]
})
```
:::

## 新控制流语法（Angular 17+）

Angular 17 引入了新的控制流语法，替代了传统的 `*ngIf` 和 `*ngFor`。

### @if / @else

```html
@if (isLoggedIn) {
  <p>欢迎回来，{{ username }}!</p>
} @else {
  <p>请先登录</p>
}
```

### @if / @else if / @else

```html
@if (status === 'loading') {
  <p>加载中...</p>
} @else if (status === 'error') {
  <p>加载失败</p>
} @else {
  <p>加载成功</p>
}
```

### @for

```html
<ul>
  @for (user of users; track user.id) {
    <li>{{ user.name }} - {{ user.email }}</li>
  }
</ul>
```

### @for 带索引和计数

```html
<ol>
  @for (item of items; track item.id; let i = $index; let count = $count) {
    <li>第 {{ i + 1 }} 项（共 {{ count }} 项）: {{ item.name }}</li>
  }
</ol>
```

### @for 空状态

```html
@for (item of items; track item.id) {
  <li>{{ item.name }}</li>
} @empty {
  <p>暂无数据</p>
}
```

### @switch

```html
@switch (role) {
  @case ('admin') {
    <p>管理员权限</p>
  }
  @case ('user') {
    <p>普通用户</p>
  }
  @default {
    <p>未知角色</p>
  }
}
```

### @defer（延迟加载）

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

## 传统指令语法

### *ngIf

```html
<div *ngIf="isLoggedIn; else loginTemplate">
  <p>欢迎回来!</p>
</div>
<ng-template #loginTemplate>
  <p>请先登录</p>
</ng-template>
```

### *ngFor

```html
<ul>
  <li *ngFor="let user of users; let i = index; let count = count">
    {{ i + 1 }}. {{ user.name }}
  </li>
</ul>
```

### *ngSwitch

```html
<div [ngSwitch]="role">
  <p *ngSwitchCase="'admin'">管理员</p>
  <p *ngSwitchCase="'user'">普通用户</p>
  <p *ngSwitchDefault>未知角色</p>
</div>
```

## 模板引用变量

使用 `#` 创建模板引用变量：

```html
<input #myInput type="text" placeholder="输入内容">
<button (click)="myInput.focus()">聚焦</button>
<button (click)="logValue(myInput.value)">获取值</button>
```

```typescript
logValue(value: string) {
  console.log('输入值:', value)
}
```

## 管道

### 内置管道

```html
<!-- 日期管道 -->
<p>{{ today | date:'yyyy-MM-dd' }}</p>

<!-- 货币管道 -->
<p>{{ price | currency:'CNY':'symbol' }}</p>

<!-- 百分比管道 -->
<p>{{ ratio | percent }}</p>

<!-- 小数管道 -->
<p>{{ value | number:'1.2-2' }}</p>

<!--  JSON 管道 -->
<pre>{{ data | json }}</pre>

<!--  异步管道 -->
<p>{{ data$ | async }}</p>
```

### 管道链式调用

```html
<p>{{ today | date:'fullDate' | uppercase }}</p>
```

## 样式绑定

### 类绑定

```html
<!-- 单个类 -->
<div [class.active]="isActive">内容</div>

<!-- 多个类 -->
<div [ngClass]="{ 'active': isActive, 'disabled': isDisabled }">内容</div>

<!-- 类数组 -->
<div [ngClass]="['btn', 'btn-primary', { 'active': isActive }]">按钮</div>
```

### 样式绑定

```html
<!-- 单个样式 -->
<div [style.color]="textColor">内容</div>

<!-- 多个样式 -->
<div [ngStyle]="{ 'color': textColor, 'font-size': fontSize + 'px' }">内容</div>
```

## 表单绑定

### 模板驱动表单

```html
<form #form="ngForm" (ngSubmit)="onSubmit(form)">
  <input 
    name="username" 
    ngModel 
    #username="ngModel"
    required 
    minlength="3"
    placeholder="用户名">
  
  @if (username.invalid && username.touched) {
    <p class="error">用户名至少3个字符</p>
  }
  
  <button type="submit" [disabled]="form.invalid">提交</button>
</form>
```

### 响应式表单

```html
<form [formGroup]="userForm" (ngSubmit)="onSubmit()">
  <input formControlName="username" placeholder="用户名">
  
  @if (userForm.get('username')?.invalid && userForm.get('username')?.touched) {
    <p class="error">用户名至少3个字符</p>
  }
  
  <button type="submit" [disabled]="userForm.invalid">提交</button>
</form>
```

