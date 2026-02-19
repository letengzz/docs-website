# CSS3 过渡

过渡可以在不使用 Flash 动画，不使用 JavaScript 的情况下，让元素从一种样式，平滑过渡为另一种样式。

## transition-property

作用：定义哪个属性需要过渡，只有在该属性中定义的属性（比如宽、高、颜色等）才会以有过渡效果。

常用值：

1. none ：不过渡任何属性。

2. all ：过渡所有能过渡的属性。

3. 具体某个属性名 ，例如： width 、 heigth ，若有多个以逗号分隔。

:::tip

不是所有的属性都能过渡，值为数字，或者值能转为数字的属性，都支持过渡，否则不支持过渡。

常见的支持过渡的属性有：颜色、长度值、百分比、 z-index 、 opacity 、 2D 变换属性、 3D 变换属性、阴影。

:::

## transition-duration

作用：设置过渡的持续时间，即：一个状态过渡到另外一个状态耗时多久。

常用值：

1. 0 (默认值)：没有任何过渡时间。

2. s 或 ms ：秒或毫秒。

3. 列表 ：

   - 如果想让所有属性都持续一个时间，那就写一个值。

   - 如果想让每个属性持续不同的时间那就写一个时间的列表。

## transition-delay

作用：指定开始过渡的延迟时间，单位： s 或 ms

## transition-timing-function

作用：设置过渡的类型

常用值：

1. ease (默认值)： 平滑过渡

2. linear ： 线性过渡

3. ease-in ： 慢 → 快

4. ease-out ： 快 → 慢

5. ease-in-out ： 慢 → 快 → 慢

6. step-start ： 等同于 steps(1, start)

7. step-end ： 等同于 steps(1, end)

8. steps( integer,?) ： 接受两个参数的步进函数。第一个参数必须为正整数，指定函数的步数。第二个参数取值可以是 start 或 end ，指定每一步的值发生变化的时间点。第二个参数默认值为 end 。

9. cubic-bezie ( number, number, number, number)： 特定的贝塞尔曲线类型。

在线制作贝赛尔曲线：https://cubic-bezier.com

## transition 复合属性

如果设置了一个时间，表示 duration ；如果设置了两个时间，第一是 duration ，第二个是delay ；其他值没有顺序要求。

```css
transition:1s 1s linear all;
```

