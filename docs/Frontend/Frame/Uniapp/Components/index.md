# Uniapp 组件开发

## 组件基础

### 组件定义

```vue [components/MyButton.vue]
<template>
  <button
    class="my-button"
    :class="[`my-button--${type}`, { 'my-button--disabled': disabled }]"
    :disabled="disabled"
    @click="handleClick"
  >
    <slot />
  </button>
</template>

<script setup>
const props = defineProps({
  type: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'primary', 'success', 'warning', 'danger'].includes(value)
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

const handleClick = (e) => {
  if (!props.disabled) {
    emit('click', e)
  }
}
</script>

<style scoped>
.my-button {
  padding: 16rpx 32rpx;
  border-radius: 8rpx;
  font-size: 28rpx;
  border: none;
}

.my-button--default {
  background-color: #f5f5f5;
  color: #333;
}

.my-button--primary {
  background-color: #007AFF;
  color: #fff;
}

.my-button--disabled {
  opacity: 0.5;
}
</style>
```

### 组件使用

```vue [pages/index/index.vue]
<template>
  <view>
    <MyButton type="primary" @click="handleClick">主要按钮</MyButton>
    <MyButton type="success" disabled>禁用按钮</MyButton>
  </view>
</template>

<script setup>
import MyButton from '@/components/MyButton.vue'

const handleClick = () => {
  console.log('按钮被点击')
}
</script>
```

## Props 定义

### 基础类型

```vue
<script setup>
const props = defineProps({
  title: String,
  count: Number,
  visible: Boolean,
  items: Array,
  config: Object
})
</script>
```

### 完整定义

```vue
<script setup>
const props = defineProps({
  // 基础类型
  name: {
    type: String,
    required: true
  },

  // 带默认值
  type: {
    type: String,
    default: 'default'
  },

  // 数组默认值
  tags: {
    type: Array,
    default: () => []
  },

  // 对象默认值
  style: {
    type: Object,
    default: () => ({ color: '#333' })
  },

  // 自定义验证
  size: {
    type: String,
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  }
})
</script>
```

## 事件定义

```vue
<script setup>
const emit = defineEmits({
  // 无验证
  click: null,

  // 带验证
  submit: (payload) => {
    if (payload && payload.name) {
      return true
    }
    console.warn('submit 事件需要包含 name 字段')
    return false
  }
})

const handleSubmit = () => {
  emit('submit', { name: '测试', value: 123 })
}
</script>
```

## 插槽

### 默认插槽

```vue [components/Card.vue]
<template>
  <view class="card">
    <view class="card-header">
      <slot name="header">默认标题</slot>
    </view>
    <view class="card-body">
      <slot />
    </view>
    <view class="card-footer">
      <slot name="footer" />
    </view>
  </view>
</template>
```

```vue
<template>
  <Card>
    <template #header>
      <text>自定义标题</text>
    </template>

    <text>卡片内容</text>

    <template #footer>
      <button>底部按钮</button>
    </template>
  </Card>
</template>
```

### 作用域插槽

```vue [components/List.vue]
<template>
  <view>
    <view v-for="item in items" :key="item.id" class="list-item">
      <slot :item="item" :index="item.index">
        <text>{{ item.name }}</text>
      </slot>
    </view>
  </view>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    default: () => []
  }
})
</script>
```

```vue
<template>
  <List :items="users">
    <template #default="{ item }">
      <view class="user-item">
        <text>{{ item.name }}</text>
        <text>{{ item.email }}</text>
      </view>
    </template>
  </List>
</template>
```

## 组件通信

### 父传子（Props）

```vue [components/Child.vue]
<script setup>
const props = defineProps({
  message: String
})
</script>

<template>
  <text>{{ message }}</text>
</template>
```

### 子传父（Events）

```vue [components/Child.vue]
<script setup>
const emit = defineEmits(['update'])

const sendData = () => {
  emit('update', { value: '子组件数据' })
}
</script>
```

```vue [pages/index/index.vue]
<template>
  <Child @update="handleUpdate" />
</template>

<script setup>
const handleUpdate = (data) => {
  console.log('收到子组件数据:', data)
}
</script>
```

### 跨组件通信（Provide/Inject）

```vue [components/Parent.vue]
<script setup>
import { provide, ref } from 'vue'

const theme = ref('light')
const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
}

provide('theme', theme)
provide('toggleTheme', toggleTheme)
</script>
```

```vue [components/DeepChild.vue]
<script setup>
import { inject } from 'vue'

const theme = inject('theme')
const toggleTheme = inject('toggleTheme')
</script>

<template>
  <view :class="theme">
    <text>当前主题：{{ theme }}</text>
    <button @click="toggleTheme">切换主题</button>
  </view>
</template>
```

## 自定义组件示例

### 弹窗组件

```vue [components/Modal.vue]
<template>
  <view v-if="visible" class="modal-overlay" @click="handleOverlayClick">
    <view class="modal-content" @click.stop>
      <view class="modal-header">
        <slot name="header">
          <text class="modal-title">{{ title }}</text>
        </slot>
        <view class="modal-close" @click="close">×</view>
      </view>
      <view class="modal-body">
        <slot />
      </view>
      <view v-if="$slots.footer" class="modal-footer">
        <slot name="footer" />
      </view>
    </view>
  </view>
</template>

<script setup>
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '提示'
  }
})

const emit = defineEmits(['update:visible', 'close'])

const close = () => {
  emit('update:visible', false)
  emit('close')
}

const handleOverlayClick = () => {
  close()
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.modal-content {
  width: 600rpx;
  background-color: #fff;
  border-radius: 16rpx;
  overflow: hidden;
}

.modal-header {
  padding: 30rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1rpx solid #eee;
}

.modal-title {
  font-size: 32rpx;
  font-weight: bold;
}

.modal-close {
  font-size: 40rpx;
  color: #999;
}

.modal-body {
  padding: 30rpx;
}

.modal-footer {
  padding: 20rpx 30rpx;
  border-top: 1rpx solid #eee;
}
</style>
```

### 使用弹窗

```vue
<template>
  <view>
    <button @click="showModal = true">打开弹窗</button>

    <Modal
      v-model:visible="showModal"
      title="确认操作"
      @close="handleClose"
    >
      <text>确定要执行此操作吗？</text>

      <template #footer>
        <button @click="showModal = false">取消</button>
        <button @click="handleConfirm">确定</button>
      </template>
    </Modal>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import Modal from '@/components/Modal.vue'

const showModal = ref(false)

const handleClose = () => {
  console.log('弹窗关闭')
}

const handleConfirm = () => {
  console.log('确认操作')
  showModal.value = false
}
</script>
```
