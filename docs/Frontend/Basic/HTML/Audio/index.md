# HTML 音频标签

:::danger

音频标签不让自动播放，可以使用其他方式自动播放。

:::

音频标签兼容性：

| 浏览器               | MP3 | Wav | Ogg |
| -------------------- | --- | --- | --- |
| Internet Explorer 9+ | YES | NO  | NO  |
| Chrome 6+            | YES | YES | YES |
| Firefox 3.6+         | YES | YES | YES |
| Safari 5+            | YES | YES | NO  |
| Opera 10+            | YES | YES | YES |

```html
<audio src="audio.mp3" autoplay></audio>
<audio autoplay>
  <source src="audio.mp3" type="audio/mp3" />
  <p>您的浏览器不支持 HTML5 Audio标签，请升级浏览器。</p>
</audio>
```
