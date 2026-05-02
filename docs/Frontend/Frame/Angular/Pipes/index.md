# Angular 管道

管道用于在模板中转换数据，Angular 提供了多种内置管道，也支持自定义管道。

## 内置管道

### 日期管道

```html
<p>{{ today | date }}</p>
<p>{{ today | date:'yyyy-MM-dd' }}</p>
<p>{{ today | date:'short' }}</p>
<p>{{ today | date:'fullDate' }}</p>
<p>{{ today | date:'HH:mm:ss' }}</p>
```

### 货币管道

```html
<p>{{ price | currency }}</p>
<p>{{ price | currency:'CNY' }}</p>
<p>{{ price | currency:'CNY':'symbol':'1.2-2' }}</p>
<p>{{ price | currency:'USD':'symbol-narrow' }}</p>
```

### 数字管道

```html
<p>{{ value | number }}</p>
<p>{{ value | number:'1.0-0' }}</p>
<p>{{ value | number:'3.2-2' }}</p>
<p>{{ value | number:'2.1-1' }}</p>
```

### 百分比管道

```html
<p>{{ ratio | percent }}</p>
<p>{{ ratio | percent:'1.0-0' }}</p>
```

### JSON 管道

```html
<pre>{{ data | json }}</pre>
```

### 大小写管道

```html
<p>{{ text | uppercase }}</p>
<p>{{ text | lowercase }}</p>
<p>{{ text | titlecase }}</p>
```

### 切片管道

```html
<ul>
  <li *ngFor="let item of items | slice:0:5">{{ item }}</li>
</ul>
```

### 异步管道

```html
<p>{{ data$ | async }}</p>
<ul>
  <li *ngFor="let item of items$ | async">{{ item.name }}</li>
</ul>
```

## 管道链式调用

```html
<p>{{ today | date:'fullDate' | uppercase }}</p>
<p>{{ price | currency:'CNY' | lowercase }}</p>
```

## 自定义管道

### 创建管道

```bash [终端]
ng generate pipe pipes/format-date
```

### 管道实现

```typescript [src/app/pipes/format-date.pipe.ts]
import { Pipe, PipeTransform } from '@angular/core'

@Pipe({
  name: 'formatDate',
  standalone: true
})
export class FormatDatePipe implements PipeTransform {
  transform(value: Date | string, format: string = 'yyyy-MM-dd'): string {
    if (!value) return ''
    
    const date = new Date(value)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    
    return format
      .replace('yyyy', String(year))
      .replace('MM', month)
      .replace('dd', day)
  }
}
```

### 使用管道

```html
<p>{{ user.createdAt | formatDate }}</p>
<p>{{ user.createdAt | formatDate:'MM/dd/yyyy' }}</p>
```

## 纯管道与非纯管道

### 纯管道（默认）

纯管道只在输入值变化时执行：

```typescript
@Pipe({
  name: 'purePipe',
  pure: true  // 默认
})
export class PurePipe implements PipeTransform {
  transform(value: any): any {
    return value
  }
}
```

### 非纯管道

非纯管道在每次变更检测时都执行：

```typescript
@Pipe({
  name: 'impurePipe',
  pure: false
})
export class ImpurePipe implements PipeTransform {
  transform(value: any[]): any[] {
    return value.sort()
  }
}
```

::: danger
非纯管道会影响性能，因为每次变更检测都会执行。尽量避免使用非纯管道，除非必要。
:::

## 管道参数

```typescript
@Pipe({ name: 'multiply', standalone: true })
export class MultiplyPipe implements PipeTransform {
  transform(value: number, factor: number = 1): number {
    return value * factor
  }
}
```

```html
<p>{{ 10 | multiply:2 }}</p>
<p>{{ 10 | multiply:3 }}</p>
```

