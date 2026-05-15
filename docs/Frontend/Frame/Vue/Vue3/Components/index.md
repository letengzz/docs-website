# Vue3 构建组件

Vue3组件封装应秉持"实用至上"的理念。不要为了封装而封装，而是为了提高代码的可维护性、可测试性和调试便捷性。在实际开发中，需要权衡组件复用的价值与维护成本，做出合理的架构决策。

:::warning 说明

最好的代码是能够快速通过测试、易于修改UI和修复bug的代码。组件封装应该为开发体验服务，而非增加不必要的复杂度。

:::

## 开发插件

插件官网：https://devtools.vuejs.org/guide/vite-plugin

```ts
import VueDevTools from 'vite-plugin-vue-devtools'
/**
 *  开启DevTools
 */
const useVueDevTools = () => {
  return VueDevTools({
    componentInspector: {
      // 如果是windows 'control-shift' , 如果是macOS 'meta-shift'
      toggleComboKey: 'meta-shift',
    },
  })
}

export default useVueDevTools
```

## 组件封装的原则

组件封装的目的： **隔离性** **复用性** 脱离这两种情况请务必不要封装！！！

组件封装的原则只有一个: **服务于调试** 如果出现让VueDevTools调试卡手情况，请务必删除当前组件。

组件封装达到的调试效果: 选取渲染输入进入的业务组件务必能找到接口请求

重复的业务类型能用函数解决就不要用组件。例如： 上传下载功能，echarts图表渲染 也应该用函数封装

## 适合封装的组件类型

### 纯展示性小组件【复用性】

例如：小的 tab tag countdown ... 等等。除非大UI 大改 谁没事会用VueDevTools 点击去看

```vue
<script setup lang="ts">
defineProps<{
  text: string
  type: string
}>()
</script>

<template>
  <span class="state" :class="`state--${type}`">
    {{ text }}
  </span>
</template>

<style lang="less" scoped>
.state {
  padding: 1px 8px;
  border-radius: 4px;
  font-size: 12px;
  flex: none;
  &--green {
    background: #e9fbf8;
    border: 1px solid #c1f3ec;
    color: #21d7bb;
  }
  &--yellow {
    background: #fffbe6;
    color: #faad14;
    border: 1px solid #fff1b8;
  }
  &--red {
    background: #fff2f2;
    color: #f74949;
    border: 1px solid #ffe2e2;
  }
  &--blue {
    background: #f2f8ff;
    color: #0075ff;
    border: 1px solid rgba(0, 117, 255, 0.5);
  }
  &--gray {
    background: #f6f7f7;
    color: #b3b8bf;
    border: 1px solid #dcdee1;
  }
  &--purple {
    background: #eee6ff;
    color: #7424ff;
    border: 1px solid #c7baff;
  }
}
</style>
```

使用示例：

```vue
<template>
  <Tag text="完成" type="green" />
</template>
```

### 接口数据渲染组件 【隔离性】

模块的接口和渲染放在一起形成一个独立组件 目的是为了调试方便找到接口和模板渲染字段

```vue
<script setup lang="ts">
const { data } = useRequest(xxxxx)
</script>

<template>
  <div>
    <div>
      {{ data.aa }}
    </div>
    <div>
      {{ data.bb }}
    </div>
  </div>
</template>

<style lang="less" scoped></style>
```

### 容器性质组件【复用性】

这个组件目的就是因为slot 插槽内容全符合期望的flex布局需求

```vue
<script setup lang="ts">
defineProps<{
  title: string
}>()
</script>

<template>
  <div mb20>
    <!-- 头部 -->
    <div class="header" flex-middle>
      <span t16b6>{{ title }}</span>
      <div flex-middle>
        <slot name="left" />
      </div>
      <div ml-auto flex-middle>
        <slot name="right" />
      </div>
    </div>
    <!-- 内容 -->
    <div flex flex-col gap32 px24 pt24>
      <slot />
    </div>
  </div>
</template>

<style lang="less" scoped>
.header {
  height: 50px;
  padding: 0 24px;
  border-bottom: 1px solid #e1e8f0;
}
</style>
```

使用示例：

```vue
<EasyContainer title="详情">
    <template #right>
      <Button ml-auto @click="show = false">
        返回
      </Button>
    </template>
    <!-- 详情信息 -->
    <DetailSummary  />
    <!-- 需求详情-图/表 -->
    <DetailMiddle  />
    <!-- 邀约详情 -->
    <DetailInvite  />
  </EasyContainer>
```

## 组件封装的最佳实践

1. **保持组件功能单一**：每个组件应专注于单一功能，避免过度复杂化

2. **使用组合式API**：Vue3的组合式API可以更好地组织逻辑，提高代码可读性

3. **使用 Props 和 Emits 定义清晰的接口 如果能用v-model 请务必用**：明确定义组件的输入和输出，增强可维护性

4. **添加适当的注释**：对复杂逻辑或特殊处理进行注释说明

5. **考虑组件在 Vue Devtools 中的表现**：确保组件在开发工具中易于定位和调试

6. **使用TypeScript增强类型安全**：为Props和事件添加类型定义，提前发现潜在问题
