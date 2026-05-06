# Uniapp API 使用

## 网络请求

### 基础请求

```javascript [utils/request.js]
const BASE_URL = 'https://api.example.com'

export function request(options) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}${options.url}`,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${uni.getStorageSync('token')}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else {
          reject(new Error(res.data.message || '请求失败'))
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

export function get(url, data) {
  return request({ url, method: 'GET', data })
}

export function post(url, data) {
  return request({ url, method: 'POST', data })
}

export function put(url, data) {
  return request({ url, method: 'PUT', data })
}

export function del(url, data) {
  return request({ url, method: 'DELETE', data })
}
```

### 使用请求

```vue
<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { get, post } from '@/utils/request.js'

const list = ref([])
const loading = ref(false)

onLoad(async () => {
  await loadList()
})

const loadList = async () => {
  loading.value = true
  try {
    list.value = await get('/api/list')
  } catch (err) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

const addItem = async () => {
  try {
    await post('/api/list', { name: '新项目' })
    uni.showToast({ title: '添加成功', icon: 'success' })
    loadList()
  } catch (err) {
    uni.showToast({ title: '添加失败', icon: 'none' })
  }
}
</script>
```

## 交互反馈

### Toast 提示

```vue
<script setup>
const showToast = () => {
  uni.showToast({
    title: '操作成功',
    icon: 'success',
    duration: 2000
  })
}

const showError = () => {
  uni.showToast({
    title: '操作失败',
    icon: 'error',
    duration: 2000
  })
}

const showLoading = () => {
  uni.showLoading({
    title: '加载中...'
  })

  setTimeout(() => {
    uni.hideLoading()
  }, 2000)
}
</script>
```

### Modal 对话框

```vue
<script setup>
const showConfirm = () => {
  uni.showModal({
    title: '提示',
    content: '确定要删除吗？',
    success: (res) => {
      if (res.confirm) {
        console.log('用户点击确定')
      } else if (res.cancel) {
        console.log('用户点击取消')
      }
    }
  })
}
</script>
```

### ActionSheet 操作菜单

```vue
<script setup>
const showActionSheet = () => {
  uni.showActionSheet({
    itemList: ['拍照', '从相册选择', '取消'],
    success: (res) => {
      console.log('选择了第', res.tapIndex, '项')
    }
  })
}
</script>
```

## 本地存储

### 同步存储

```vue
<script setup>
// 存储数据
const saveData = () => {
  uni.setStorageSync('username', 'admin')
  uni.setStorageSync('config', { theme: 'dark', lang: 'zh' })
}

// 读取数据
const loadData = () => {
  const username = uni.getStorageSync('username')
  const config = uni.getStorageSync('config')
  console.log(username, config)
}

// 删除数据
const removeData = () => {
  uni.removeStorageSync('username')
}

// 清空所有数据
const clearData = () => {
  uni.clearStorageSync()
}
</script>
```

### 异步存储

```vue
<script setup>
const saveDataAsync = async () => {
  try {
    await uni.setStorage({
      key: 'username',
      data: 'admin'
    })
    console.log('存储成功')
  } catch (e) {
    console.error('存储失败', e)
  }
}

const loadDataAsync = async () => {
  try {
    const res = await uni.getStorage({ key: 'username' })
    console.log('读取成功:', res.data)
  } catch (e) {
    console.error('读取失败', e)
  }
}
</script>
```

## 文件操作

### 选择图片

```vue
<script setup>
import { ref } from 'vue'

const images = ref([])

const chooseImage = () => {
  uni.chooseImage({
    count: 9,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: (res) => {
      images.value = res.tempFilePaths
    }
  })
}
</script>

<template>
  <view>
    <button @click="chooseImage">选择图片</button>
    <image
      v-for="(img, index) in images"
      :key="index"
      :src="img"
      mode="aspectFill"
    />
  </view>
</template>
```

### 上传图片

```vue
<script setup>
const uploadImage = (filePath) => {
  uni.uploadFile({
    url: 'https://api.example.com/upload',
    filePath: filePath,
    name: 'file',
    header: {
      'Authorization': `Bearer ${uni.getStorageSync('token')}`
    },
    success: (res) => {
      const data = JSON.parse(res.data)
      console.log('上传成功:', data.url)
    },
    fail: (err) => {
      console.error('上传失败:', err)
    }
  })
}
```

### 下载文件

```vue
<script setup>
const downloadFile = () => {
  uni.downloadFile({
    url: 'https://example.com/file.pdf',
    success: (res) => {
      if (res.statusCode === 200) {
        console.log('下载成功:', res.tempFilePath)
      }
    }
  })
}
```

## 设备信息

### 获取系统信息

```vue
<script setup>
import { ref } from 'vue'

const systemInfo = ref({})

const getSystemInfo = () => {
  uni.getSystemInfo({
    success: (res) => {
      systemInfo.value = res
      console.log('屏幕宽度:', res.windowWidth)
      console.log('屏幕高度:', res.windowHeight)
      console.log('设备型号:', res.model)
      console.log('系统版本:', res.system)
      console.log('平台:', res.platform)
    }
  })
}
</script>
```

### 获取网络状态

```vue
<script setup>
const getNetworkType = () => {
  uni.getNetworkType({
    success: (res) => {
      console.log('网络类型:', res.networkType)
    }
  })
}

uni.onNetworkStatusChange((res) => {
  console.log('网络状态变化:', res.isConnected)
  console.log('网络类型:', res.networkType)
})
</script>
```

### 获取位置信息

```vue
<script setup>
const getLocation = () => {
  uni.getLocation({
    type: 'gcj02',
    success: (res) => {
      console.log('纬度:', res.latitude)
      console.log('经度:', res.longitude)
    }
  })
}

const chooseLocation = () => {
  uni.chooseLocation({
    success: (res) => {
      console.log('位置名称:', res.name)
      console.log('详细地址:', res.address)
    }
  })
}
```

## 分享

### 分享给朋友

```vue
<script setup>
import { onShareAppMessage } from '@dcloudio/uni-app'

onShareAppMessage(() => {
  return {
    title: '分享标题',
    path: '/pages/index/index',
    imageUrl: 'https://example.com/share.jpg'
  }
})
</script>
```

### 分享到朋友圈

```vue
<script setup>
import { onShareTimeline } from '@dcloudio/uni-app'

onShareTimeline(() => {
  return {
    title: '分享标题',
    query: 'id=123',
    imageUrl: 'https://example.com/share.jpg'
  }
})
</script>
```

## 常用 API 列表

| API | 说明 |
|-----|------|
| `uni.request` | 发起网络请求 |
| `uni.uploadFile` | 上传文件 |
| `uni.downloadFile` | 下载文件 |
| `uni.showToast` | 显示提示框 |
| `uni.showModal` | 显示对话框 |
| `uni.showLoading` | 显示加载提示 |
| `uni.navigateTo` | 保留页面跳转 |
| `uni.redirectTo` | 关闭当前页面跳转 |
| `uni.switchTab` | 跳转 TabBar 页面 |
| `uni.navigateBack` | 返回上一页 |
| `uni.setStorageSync` | 同步存储数据 |
| `uni.getStorageSync` | 同步读取数据 |
| `uni.chooseImage` | 选择图片 |
| `uni.previewImage` | 预览图片 |
| `uni.getLocation` | 获取位置 |
| `uni.scanCode` | 扫码 |
| `uni.makePhoneCall` | 拨打电话 |
| `uni.setClipboardData` | 设置剪贴板 |
| `uni.getSystemInfo` | 获取系统信息 |
| `uni.login` | 登录 |
| `uni.getUserProfile` | 获取用户信息 |
