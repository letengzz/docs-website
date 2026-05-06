# Uniapp 页面开发

## 页面文件结构

Uniapp 页面使用 Vue 单文件组件（SFC）格式：

```vue [pages/index/index.vue]
<template>
  <view class="container">
    <text class="title">{{ title }}</text>
    <button @click="handleClick">点击</button>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const title = ref('首页')

const handleClick = () => {
  uni.showToast({
    title: '按钮被点击',
    icon: 'success'
  })
}
</script>

<style scoped>
.container {
  padding: 20rpx;
}

.title {
  font-size: 32rpx;
  color: #333;
}
</style>
```

## 页面生命周期

```vue [pages/index/index.vue]
<script setup>
import { onShow, onHide, onReady, onPullDownRefresh, onReachBottom } from '@dcloudio/uni-app'

// 页面加载完成（全局只触发一次）
onReady(() => {
  console.log('页面加载完成')
})

// 页面显示（每次进入页面都会触发）
onShow(() => {
  console.log('页面显示')
})

// 页面隐藏
onHide(() => {
  console.log('页面隐藏')
})

// 下拉刷新
onPullDownRefresh(() => {
  console.log('下拉刷新')
  setTimeout(() => {
    uni.stopPullDownRefresh()
  }, 1000)
})

// 上拉触底
onReachBottom(() => {
  console.log('上拉触底')
})
</script>
```

## 页面参数接收

```vue [pages/detail/index.vue]
<script setup>
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'

const id = ref('')
const title = ref('')

onLoad((options) => {
  console.log('页面参数:', options)
  id.value = options.id
  title.value = options.title
})
</script>

<template>
  <view>
    <text>ID: {{ id }}</text>
    <text>标题: {{ title }}</text>
  </view>
</template>
```

## 常用组件

### view 容器

相当于 HTML 的 div：

```vue
<template>
  <view class="container">
    <view class="item">项目 1</view>
    <view class="item">项目 2</view>
  </view>
</template>
```

### text 文本

```vue
<template>
  <view>
    <text>普通文本</text>
    <text selectable>可选中文本</text>
    <text space="ensp">带 空 格 的文本</text>
    <text decode>&lt;解码&gt;</text>
  </view>
</template>
```

### image 图片

```vue
<template>
  <view>
    <image src="/static/logo.png" mode="aspectFit" />
    <image src="/static/banner.jpg" mode="aspectFill" />
    <image src="/static/avatar.png" mode="widthFix" />
  </view>
</template>
```

### scroll-view 滚动容器

```vue
<template>
  <scroll-view scroll-y class="scroll-container" @scrolltolower="loadMore">
    <view v-for="item in list" :key="item.id" class="item">
      {{ item.name }}
    </view>
  </scroll-view>
</template>

<script setup>
import { ref } from 'vue'

const list = ref([
  { id: 1, name: '项目 1' },
  { id: 2, name: '项目 2' }
])

const loadMore = () => {
  console.log('加载更多')
}
</script>

<style>
.scroll-container {
  height: 100vh;
}
</style>
```

## 表单组件

### input 输入框

```vue
<template>
  <view class="form">
    <input
      v-model="username"
      type="text"
      placeholder="请输入用户名"
      maxlength="20"
      @input="onInput"
      @focus="onFocus"
      @blur="onBlur"
    />
    <input
      v-model="password"
      type="password"
      placeholder="请输入密码"
    />
  </view>
</template>

<script setup>
import { ref } from 'vue'

const username = ref('')
const password = ref('')

const onInput = (e) => {
  console.log('输入值:', e.detail.value)
}

const onFocus = () => {
  console.log('获得焦点')
}

const onBlur = () => {
  console.log('失去焦点')
}
</script>
```

### picker 选择器

```vue
<template>
  <view>
    <picker :value="index" :range="array" @change="onPickerChange">
      <view class="picker">当前选择：{{ array[index] }}</view>
    </picker>

    <picker mode="date" @change="onDateChange">
      <view class="picker">选择日期：{{ date }}</view>
    </picker>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const index = ref(0)
const array = ref(['选项 1', '选项 2', '选项 3'])
const date = ref('')

const onPickerChange = (e) => {
  index.value = e.detail.value
}

const onDateChange = (e) => {
  date.value = e.detail.value
}
</script>
```

## 列表渲染

```vue
<template>
  <view class="list">
    <view v-for="(item, index) in list" :key="item.id" class="list-item">
      <text class="index">{{ index + 1 }}</text>
      <text class="name">{{ item.name }}</text>
      <text class="price">¥{{ item.price }}</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const list = ref([
  { id: 1, name: '商品 A', price: 99 },
  { id: 2, name: '商品 B', price: 199 },
  { id: 3, name: '商品 C', price: 299 }
])
</script>
```

## 条件渲染

```vue
<template>
  <view>
    <view v-if="status === 'loading'">加载中...</view>
    <view v-else-if="status === 'error'">加载失败</view>
    <view v-else>加载成功</view>

    <view v-show="isVisible">显示/隐藏</view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const status = ref('loading')
const isVisible = ref(true)
</script>
```

## 页面样式

### rpx 响应式单位

rpx 是 Uniapp 提供的响应式单位，可以根据屏幕宽度自动适配：

```vue
<style>
.container {
  width: 750rpx;  /* 全屏宽度 */
  padding: 20rpx;
}

.title {
  font-size: 32rpx;
  color: #333;
}

.button {
  width: 200rpx;
  height: 80rpx;
  line-height: 80rpx;
  text-align: center;
  background-color: #007AFF;
  color: #fff;
  border-radius: 8rpx;
}
</style>
```

### 全局样式

```css [App.vue]
<style>
/* 全局样式 */
page {
  background-color: #f5f5f5;
  font-size: 28rpx;
  color: #333;
}

.container {
  padding: 20rpx;
}

.flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
```

### 页面级样式

```vue
<style scoped>
/* 仅当前页面生效 */
.title {
  font-size: 36rpx;
  font-weight: bold;
}
</style>
```

## 页面通信

### 通过全局数据

```javascript [utils/store.js]
const data = {}

export function setGlobalData(key, value) {
  data[key] = value
}

export function getGlobalData(key) {
  return data[key]
}
```

### 通过事件总线

```javascript [utils/eventBus.js]
const events = {}

export function on(event, callback) {
  if (!events[event]) events[event] = []
  events[event].push(callback)
}

export function emit(event, ...args) {
  if (events[event]) {
    events[event].forEach(cb => cb(...args))
  }
}

export function off(event, callback) {
  if (events[event]) {
    events[event] = events[event].filter(cb => cb !== callback)
  }
}
```
