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

## 与「音视频交付工程」的分工（第 203 天补充）

本页讲的是**标签语法**：`src` 指向什么、`<source>` 怎么按 `type` 挑选、`controls` 与 `autoplay` 的行为。它不回答「这个 `src` 背后到底是什么」——而在真实点播链路里，那个 `src` 通常不是 `.mp4`，而是一份 `.m3u8` 清单。

| 问题 | 本页（标签层） | [音视频交付工程](../../../../Backend/MediaDelivery/index.md)（交付层） |
| --- | --- | --- |
| `src` 指向什么 | 一个可直接播放的媒体文件 | 一份清单，清单再指向几百上千个分片 |
| 谁负责清晰度切换 | 不涉及 | ABR 策略，见[播放](../../../../Backend/MediaDelivery/Playback/index.md) |
| 兼容性怎么解决 | 多个 `<source>` 按 `type` 挑 | Safari 原生吃 HLS，Chrome/Firefox 走 MSE + hls.js |

::: danger 一个必须知道的差别
`<video src="movie.mp4">` 与 `<video src="master.m3u8">` 在**标签上完全一样**，但后者只在 Safari 能直接播；Chrome 需要 hls.js 通过 MSE 喂数据。所以「这段代码在我这能播、在别人那黑屏」通常不是标签写错了，而是**播放器实现不同**。

另外 `preload="auto"` 在移动端会让浏览器预取整段媒体，一个 90 分钟的视频就是几百 MB 的流量——点播场景通常设 `preload="metadata"`。
:::
