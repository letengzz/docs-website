# 单文件组件

单文件组件（Single File Component, SFC）是 Vue 推荐的组件组织方式，使用 `.vue` 文件。

## 基本结构

```vue [App.vue]
<template>
  <div id="app">
    <h1>{{ title }}</h1>
    <p>{{ message }}</p>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      title: '单文件组件',
      message: 'Hello Vue!'
    }
  }
}
</script>

<style scoped>
#app {
  font-family: Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
```

## 模板部分

```vue [template.vue]
<template>
  <div class="container">
    <h1>{{ title }}</h1>
    <p v-if="showMessage">{{ message }}</p>
    <ul>
      <li v-for="item in list" :key="item.id">
        {{ item.name }}
      </li>
    </ul>
    <button @click="handleClick">点击</button>
  </div>
</template>
```

## 脚本部分

```vue [script.vue]
<script>
export default {
  name: 'MyComponent',
  // 组件数据
  data() {
    return {
      title: '标题',
      message: '消息',
      list: [
        { id: 1, name: '项目 1' },
        { id: 2, name: '项目 2' }
      ]
    }
  },
  // 计算属性
  computed: {
    reversedMessage() {
      return this.message.split('').reverse().join('')
    }
  },
  // 方法
  methods: {
    handleClick() {
      this.message = '按钮被点击了'
    }
  },
  // 侦听器
  watch: {
    message(newVal) {
      console.log('消息变化:', newVal)
    }
  },
  // 生命周期
  mounted() {
    console.log('组件已挂载')
  }
}
</script>
```

## 样式部分

```vue [style.vue]
<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  color: #2c3e50;
}

button {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #3aa876;
}
</style>
```

## 组件导入和使用

```vue [import-component.vue]
<template>
  <div>
    <my-header></my-header>
    <my-content></my-content>
    <my-footer></my-footer>
  </div>
</template>

<script>
import MyHeader from './components/Header.vue'
import MyContent from './components/Content.vue'
import MyFooter from './components/Footer.vue'

export default {
  name: 'App',
  components: {
    MyHeader,
    MyContent,
    MyFooter
  }
}
</script>
```

## 组件注册方式

```vue [component-registration.vue]
<script>
import ChildComponent from './ChildComponent.vue'

export default {
  // 局部注册
  components: {
    ChildComponent,
    // 或使用对象简写
    'my-component': ChildComponent
  }
}
</script>
```

## Props 定义

```vue [props.vue]
<script>
export default {
  props: {
    // 基础类型检查
    title: String,
    // 多种类型
    value: [String, Number],
    // 必填
    id: {
      type: Number,
      required: true
    },
    // 带默认值
    count: {
      type: Number,
      default: 0
    },
    // 对象默认值
    config: {
      type: Object,
      default() {
        return { theme: 'default' }
      }
    },
    // 自定义验证
    status: {
      validator(value) {
        return ['success', 'warning', 'danger'].includes(value)
      }
    }
  }
}
</script>
```

## 事件定义

```vue [events.vue]
<template>
  <button @click="$emit('update', 'new value')">
    更新
  </button>
</template>

<script>
export default {
  emits: ['update'],
  methods: {
    handleClick() {
      this.$emit('custom-event', {
        message: '自定义事件数据'
      })
    }
  }
}
</script>
```

::: tip 提示
- 单文件组件使用 .vue 扩展名
- 包含 template、script、style 三部分
- scoped 样式只在当前组件生效
- 推荐使用局部注册组件
- Props 需要定义类型验证
:::
