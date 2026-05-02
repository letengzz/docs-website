# Angular 指令系统

指令是 Angular 中用于操作 DOM 行为的类。Angular 提供了多种内置指令，也支持自定义指令。

## 指令类型

| 类型 | 说明 | 示例 |
|------|------|------|
| 组件指令 | 带模板的指令 | `@Component` |
| 结构指令 | 改变 DOM 结构 | `*ngIf`, `*ngFor` |
| 属性指令 | 改变元素外观/行为 | `ngClass`, `ngStyle` |

## 内置结构指令

### @if / @else（Angular 17+）

```html
@if (isLoggedIn) {
  <p>欢迎回来!</p>
} @else {
  <p>请先登录</p>
}
```

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
  <li *ngFor="let user of users; let i = index; let isFirst = first; let isLast = last">
    {{ i + 1 }}. {{ user.name }}
    <span *ngIf="isFirst">(第一个)</span>
    <span *ngIf="isLast">(最后一个)</span>
  </li>
</ul>
```

### trackBy 优化

```typescript [src/app/app.component.ts]
trackByUserId(index: number, user: User): number {
  return user.id
}
```

```html
<ul>
  <li *ngFor="let user of users; trackBy: trackByUserId">
    {{ user.name }}
  </li>
</ul>
```

## 内置属性指令

### ngClass

```html
<!-- 对象语法 -->
<div [ngClass]="{ 'active': isActive, 'disabled': isDisabled }">内容</div>

<!-- 数组语法 -->
<div [ngClass]="['btn', 'btn-primary']">按钮</div>

<!-- 字符串语法 -->
<div [ngClass]="'btn btn-primary'">按钮</div>
```

### ngStyle

```html
<div [ngStyle]="{ 'color': textColor, 'font-size': fontSize + 'px' }">内容</div>
```

### ngModel

```html
<input [(ngModel)]="username" placeholder="用户名">
```

## 自定义属性指令

### 创建指令

```bash [终端]
ng generate directive directives/highlight
```

### 指令实现

```typescript [src/app/directives/highlight.directive.ts]
import { Directive, ElementRef, HostListener, Input, Renderer2 } from '@angular/core'

@Directive({
  selector: '[appHighlight]',
  standalone: true
})
export class HighlightDirective {
  @Input('appHighlight') highlightColor: string = 'yellow'
  
  constructor(private el: ElementRef, private renderer: Renderer2) {}
  
  @HostListener('mouseenter') onMouseEnter() {
    this.renderer.setStyle(this.el.nativeElement, 'backgroundColor', this.highlightColor)
  }
  
  @HostListener('mouseleave') onMouseLeave() {
    this.renderer.removeStyle(this.el.nativeElement, 'backgroundColor')
  }
}
```

### 使用指令

```html
<p [appHighlight]="'lightblue'">鼠标悬停高亮</p>
<p appHighlight>默认黄色高亮</p>
```

## 自定义结构指令

```typescript [src/app/directives/unless.directive.ts]
import { Directive, Input, TemplateRef, ViewContainerRef } from '@angular/core'

@Directive({
  selector: '[appUnless]',
  standalone: true
})
export class UnlessDirective {
  @Input() set appUnless(condition: boolean) {
    if (!condition) {
      this.vc.createEmbeddedView(this.templateRef)
    } else {
      this.vc.clear()
    }
  }
  
  constructor(
    private templateRef: TemplateRef<any>,
    private vc: ViewContainerRef
  ) {}
}
```

```html
<p *appUnless="isLoggedIn">请先登录</p>
```

## HostListener 和 HostBinding

### @HostListener

监听宿主元素事件：

```typescript
@Directive({ selector: '[appClickLog]' })
export class ClickLogDirective {
  @HostListener('click') onClick() {
    console.log('元素被点击')
  }
}
```

### @HostBinding

绑定宿主元素属性：

```typescript
@Directive({ selector: '[appDisabled]' })
export class DisabledDirective {
  @HostBinding('disabled') isDisabled = true
  @HostBinding('attr.aria-disabled') ariaDisabled = 'true'
}
```

## 指令生命周期

| 钩子 | 说明 |
|------|------|
| `ngOnInit` | 指令初始化 |
| `ngOnChanges` | 输入属性变化 |
| `ngOnDestroy` | 指令销毁前 |

```typescript
@Directive({ selector: '[appLifecycle]' })
export class LifecycleDirective implements OnInit, OnDestroy {
  ngOnInit() {
    console.log('指令初始化')
  }
  
  ngOnDestroy() {
    console.log('指令销毁')
  }
}
```

