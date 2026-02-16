# HTML 视频标签

`<video>` 元素来轻松地嵌入视频。

语法：

```html
<video src=""></video> <video src="video.mp4" controls width="300"></video>
```

属性：

- `src`：指向要插入到页面的视频地址。
- `controls`：显示浏览器自带播放控件。
- `width`/`height`：设置视频的宽度和高度。
- `autoplay`：自动播放 (需设置静音才可以自动播放)。
- `loop`：循环播放。
- `muted`：静音。
- `poster`：预览图像。

视频标签兼容性：

| 浏览器            | MP4                  | WebM | Ogg |
| ----------------- | -------------------- | ---- | --- |
| Internet Explorer | YES                  | NO   | NO  |
| Chrome            | YES                  | YES  | YES |
| Firefox           | YES                  | YES  | YES |
| Safari            | YES                  | NO   | NO  |
| Opera             | YES (从 Opera 25 起) | YES  | YES |

视频标签兼容性写法：

1. 将 src 属性放在几个单独的 `<source>` 元素当中，这些元素分别指向各自的资源。
2. 浏览器会检查 `<source>` 元素，并且播放第一个与其自身相匹配的媒体。
3. 每个 `<source>` 元素都含有 type 属性，浏览器也会通过检查这个属性来迅速的跳过那些不支持的格式。如果你没有添加 type 属
   性，浏览器会尝试加载每一个文件，直到找到一个能正确播放的格式，但是这样会消耗掉大量的时间和资源。

```html
<video controls>
  <source src="video.mp4" type="video/mp4" />
  <source src="video.ogg" type="video/ogg" />
  <source src="video.webm" type="video/webm" />
  <p>您的浏览器不支持HTML5 Video标签，请升级浏览器。</p>
</video>
```
