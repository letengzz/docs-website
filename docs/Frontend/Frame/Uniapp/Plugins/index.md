# Uniapp 插件与扩展

## uni_modules 插件

### 安装插件

```bash [终端]
# 使用 HBuilderX
# 右键项目 → 选择 插件市场 → 搜索插件 → 安装

# 使用 CLI
npm install @dcloudio/uni-ui
```

### 使用 uni-ui

```vue
<template>
  <view>
    <uni-badge text="10" type="primary" />
    <uni-button type="primary">按钮</uni-button>
    <uni-card title="卡片标题">
      <text>卡片内容</text>
    </uni-card>
    <uni-list>
      <uni-list-item title="列表项 1" />
      <uni-list-item title="列表项 2" />
    </uni-list>
  </view>
</template>

<script setup>
import { ref } from 'vue'
</script>
```

## 常用插件

### uView UI

```bash [终端]
npm install uview-ui
```

```javascript [main.js]
import { createSSRApp } from 'vue'
import App from './App.vue'
import uView from 'uview-ui'

export function createApp() {
  const app = createSSRApp(App)
  app.use(uView)
  return { app }
}
```

```vue
<template>
  <view>
    <u-button type="primary">按钮</u-button>
    <u-input v-model="value" placeholder="请输入" />
    <u-cell-group>
      <u-cell-item title="单元格" />
    </u-cell-group>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const value = ref('')
</script>
```

### ColorUI

```bash [终端]
# 下载 ColorUI 源码
# 将 colorui 文件夹复制到项目根目录
```

```vue
<template>
  <view class="bg-white padding">
    <view class="cu-btn bg-blue lg">大按钮</view>
    <view class="cu-btn bg-red round">圆角按钮</view>
  </view>
</template>
```

## 自定义插件开发

### 创建插件目录

```
uni_modules/
└── my-plugin/
    ├── components/
    │   └── my-component/
    │       └── my-component.vue
    ├── changelog.md
    ├── package.json
    └── readme.md
```

### package.json 配置

```json [uni_modules/my-plugin/package.json]
{
  "id": "my-plugin",
  "displayName": "我的插件",
  "version": "1.0.0",
  "description": "这是一个自定义插件",
  "keywords": [
    "插件",
    "自定义"
  ],
  "dcloudext": {
    "category": [
      "前端组件",
      "通用组件"
    ]
  }
}
```

### 插件组件

```vue [uni_modules/my-plugin/components/my-component/my-component.vue]
<template>
  <view class="my-component">
    <text>{{ title }}</text>
    <slot />
  </view>
</template>

<script setup>
const props = defineProps({
  title: {
    type: String,
    default: '默认标题'
  }
})
</script>

<style scoped>
.my-component {
  padding: 20rpx;
  background-color: #fff;
  border-radius: 8rpx;
}
</style>
```

## 原生插件

### App 端原生插件

```javascript [utils/native.js]
// 调用原生插件
export function callNativePlugin(data) {
  const MyPlugin = uni.requireNativePlugin('MyPlugin')
  MyPlugin.doSomething(data, (res) => {
    console.log('原生插件返回:', res)
  })
}
```

### 原生插件开发（Android）

```java [android/src/main/java/com/example/MyPlugin.java]
package com.example;

import com.taobao.weex.annotation.JSMethod;
import com.taobao.weex.bridge.JSCallback;
import com.taobao.weex.common.WXModule;

public class MyPlugin extends WXModule {
    @JSMethod(uiThread = true)
    public void doSomething(String data, JSCallback callback) {
        // 处理数据
        String result = "处理结果：" + data;
        // 回调 JS
        callback.invoke(result);
    }
}
```

## 插件市场

### 常用插件分类

| 分类 | 插件 | 说明 |
|------|------|------|
| UI 组件 | uni-ui | 官方 UI 组件库 |
| UI 组件 | uView | 全端 UI 框架 |
| UI 组件 | ColorUI | 轻量级 CSS 组件库 |
| 图表 | uCharts | 跨平台图表库 |
| 图表 | echarts | 百度图表库 |
| 地图 | amap | 高德地图 |
| 地图 | tencent-map | 腾讯地图 |
| 工具 | luch-request | 请求库 |
| 工具 | dayjs | 日期处理库 |
| 工具 | validator | 表单验证 |

### 使用插件市场插件

```vue
<template>
  <view>
    <qiun-data-charts type="line" :chartData="chartData" />
  </view>
</template>

<script setup>
import { ref } from 'vue'
import qiunDataCharts from '@/uni_modules/qiun-data-charts/components/qiun-data-charts/qiun-data-charts.vue'

const chartData = ref({
  categories: ['2023-01', '2023-02', '2023-03'],
  series: [{ name: '销量', data: [100, 200, 300] }]
})
</script>
```

## 插件配置

### easycom 自动导入

```json [pages.json]
{
  "easycom": {
    "autoscan": true,
    "custom": {
      "^uni-(.*)": "@dcloudio/uni-ui/lib/uni-$1/uni-$1.vue",
      "^u-(.*)": "uview-ui/components/u-$1/u-$1.vue"
    }
  }
}
```

配置后可直接使用组件，无需手动导入：

```vue
<template>
  <view>
    <uni-button type="primary">按钮</uni-button>
    <u-input v-model="value" />
  </view>
</template>

<script setup>
import { ref } from 'vue'

const value = ref('')
</script>
```
