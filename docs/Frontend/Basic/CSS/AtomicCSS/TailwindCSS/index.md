# Tailwind CSS

官网：

- https://tailwindcss.com/
- https://www.tailwindcss.cn/

安装Tailwind CSS：

首先安装 tailwindcss 以及它使用到的包：

```shell
npm install tailwindcss postcss autoprefixer -D
```

然后执行：

```shell
npx tailwindcss init -p
```

会发现项目中会生成`postcss.config.js`和`tailwind.config.js`两个配置文件，修改一下`tailwind.config.js`

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
};
```

在 `src` 下新建 `index.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

最后在`main.ts`引入`index.css`就大功告成了

引入了`tailwindcss`后，只需要在元素中中添加`class`即可实现想要的样式。例如：

这个 `div` 为 `flex` 盒子,同时设置了`align-items: center;justify-content: center`且高度撑满整个屏幕,以及背景颜色为色调 100(色调越高,颜色越深)的 gray。

```html
<div class="flex items-center justify-center h-screen bg-gray-100">text</div>
```