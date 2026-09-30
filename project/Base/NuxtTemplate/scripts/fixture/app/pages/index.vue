<script setup lang="ts">
// 手写业务文件：只使用自家组件名，不出现任何组件库的名字。
import { uiKey } from '~/ui/generated/adapter'
import { uiManifest } from '~/ui/generated/manifest'

const saving = ref(false)

async function save() {
  saving.value = true
  try {
    await $fetch('/api/demo/save', { method: 'POST' })
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>Nuxt 通用模板</h1>
    <p>当前 UI 实现层：{{ uiManifest.uiLabel }}（{{ uiKey }}）</p>
    <XButton type="primary" :loading="saving" @click="save">
      保存
    </XButton>
  </div>
</template>
