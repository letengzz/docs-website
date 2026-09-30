// Nuxt 通用模板的配置入口。
// 手写区域：本文件除 marker 区间外都由人维护，脚本永不改动。
import { uiModules, uiCss, uiBuild, uiNitroPreset, uiRouteRules, uiRuntimeConfigPublic, uiAlias }
  from './app/ui/generated/nuxt-ui.config.mjs'

// 与 UI 实现层无关的模块，放在手写区；marker 区间只负责把 uiModules 合并进来。
const baseModules = ['@nuxt/eslint', '@pinia/nuxt', '@vueuse/nuxt']

export default defineNuxtConfig({
  compatibilityDate: '2026-09-01',
  future: { compatibilityVersion: 4 },

  // ui:modules:begin
  modules: [...baseModules, ...uiModules],
  // ui:modules:end

  css: [...uiCss],
  alias: uiAlias,
  build: uiBuild,
  routeRules: uiRouteRules,
  nitro: { preset: uiNitroPreset },
  runtimeConfig: {
    public: uiRuntimeConfigPublic,
  },
  devtools: { enabled: true },
  experimental: { appManifest: false },
})
