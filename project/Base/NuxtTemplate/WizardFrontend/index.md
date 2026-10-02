# 引导页：信息架构与选择模型

引导页要做两件事，而且必须同时做对：**看起来很直观**（用户三十秒内能选完），**模型上没有歧义**（后端拿到的选择一定能被机器校验）。前者靠布局，后者靠一份唯一的选择模型。

![引导页两栏布局：左栏技术栈 / 右栏依赖预览 + Nuxt 配置 / 底部初始化](../assets/wizard-layout.svg)

## 1. 信息架构

页面是**两栏 + 底部操作条**，位置即语义——左栏改变「用什么写」，右栏改变「怎么跑」，右栏顶部常驻一块「依赖与变更预览」（它是当前选择的结果，与右栏的配置项是同一件事的两面）：

| 区 | 分组 | 控件 | 默认值 | 影响面 |
| --- | --- | --- | --- | --- |
| 右上 | 依赖与变更预览 | 可折叠面板 | 折叠（点「预览变更」后自动展开） | 展示会装什么、删什么、生成什么；不是选择项 |
| 左 | UI 框架 | 横向单选 ×5（无 / Element Plus / Ant Design Vue / Nuxt UI / Vuetify） | 无 | 依赖 + 自动导入配置 + 样式入口 |
| 左 | CSS 预处理器 | 横向单选 ×4（无 / Sass / Less / Stylus） | 无 | 依赖 + 组件内样式语言 + Stylelint 配置 |
| 左 | 原子化框架 | 横向单选 ×3（无 / UnoCSS / Tailwind CSS） | 无 | 依赖 + 构建插件 + 样式入口优先级 |
| 右 | 渲染模式 | 横向单选 ×4（SSR / SPA / SSG / 混合） | SSR | `ssr` 开关 + `routeRules` + 部署形态 |
| 右 | 模块 | 复选 ×6（Pinia / VueUse / i18n / Icon / Image / SEO） | Pinia、Icon | `modules` 数组 |
| 右 | 工程 | 复选 ×4 + 横向单选 ×1（ESLint、测试栈、TS 严格度、Docker；包管理器） | ESLint、测试栈、严格 TS、pnpm | 依赖 + 配置文件 |

::: tip 为什么「渲染模式」放在右侧而不是左侧
左侧三个维度是**技术栈身份**——选完基本不会再改，团队之间差异最大。右侧是**运行形态与工程配置**——同一个团队的不同项目会不一样，也可能初始化后再手动调整。把「身份」和「配置」分区，用户的心智负担最小。
:::

### 1.1 每个控件的呈现规则

| 控件形态 | 用于 | 交互 |
| --- | --- | --- |
| 横向单选按钮组 | 全部单选组：UI 框架、预处理器、原子化（左栏），渲染模式、包管理器（右栏） | 每个候选一个带边框的小块，整组左右排开、一行放不下才换行；选中态是边框 + 底色 + 标签加粗变色；「说明 + 会装什么」收进 `title`，悬停可见 |
| 复选行 | 模块、工程开关（右栏） | 左侧复选框，右侧标题 + 一行说明；勾选后展开「附带文件」提示 |
| 可折叠预览 | 依赖与变更预览（**右上角**） | 展开后汇总运行时/开发依赖、Nuxt 模块、样式入口顺序、将删除与将生成的文件；默认折叠，展开高度有上限（内部自己滚） |

### 1.2 「会装什么」必须有地方看得到

单选组一律**横向**排开：组内是互斥关系，横向正好呼应「从这几个里挑一个」；候选彼此相邻时，名字长短、有没有「实验性」标记都是一眼可比的，竖排一列反而要上下移动视线。每项只占一行「○ 名称」，说明与「会装什么」收进元素的 `title`。

多选组（模块、工程开关）保持**纵向复选行**：每项都有一行说明要读，而且它们是「加不加」而不是「选哪个」，横向排开就分不清与单选组的区别了。

两种形态遵循同一条标准：**选择成本主要来自不确定**——用户不是不知道该选哪个，而是不知道选了会带来什么。所以信息不删，只决定它是「一直占着版面」还是「需要时才展开」。用 `title` 而不是自造 tooltip 还有一层原因：按 HTML-AAM，`title` 就是表单控件的 accessible description，屏幕阅读器拿到的是同一份内容，不是只给鼠标用的。

## 2. 选择模型：`options.json`

所有可选项、默认值、依赖映射、冲突规则，全部写在服务端的**一个 JSON 文件**里。前端不硬编码任何选项，而是启动时 `GET /api/wizard/schema` 拿。

![选择模型：一份 JSON 驱动页面、校验与初始化计划](../assets/option-model.svg)

### 2.1 模型结构

```json [server/utils/wizard/options.json]
{
  "version": "1.0.0",
  "groups": [
    {
      "key": "ui",
      "label": "UI 框架",
      "column": "left",
      "multiple": false,
      "default": "none",
      "options": [
        {
          "value": "none",
          "label": "不使用组件库",
          "desc": "纯手写 CSS 与原生元素",
          "deps": [],
          "files": [],
          "note": "体积最小，适合内容型站点"
        },
        {
          "value": "element-plus",
          "label": "Element Plus",
          "desc": "国内生态最全的 Vue 3 组件库",
          "deps": ["element-plus"],
          "devDeps": ["@element-plus/nuxt"],
          "modules": ["@element-plus/nuxt"],
          "files": ["app/assets/styles/ui-element-plus.css"],
          "note": "会装 element-plus + 自动导入模块"
        }
      ]
    }
  ],
  "rules": [
    {
      "level": "block",
      "when": { "ui": "nuxt-ui", "atomic": "unocss" },
      "message": "Nuxt UI 自带 Tailwind CSS 与语义色系统，与 UnoCSS 同时使用会导致工具类解析冲突。请把原子化框架改为「Tailwind CSS」或「不使用」。"
    }
  ]
}
```

::: info 三处刻意设计
1. **`column` 字段决定渲染到左区还是右区**——布局不是写死在模板里的，加一个新分组只改 JSON。
2. **`files` 字段声明本选项需要额外生成/删除的文件**——引擎据此执行删除白名单，不靠通配。见 [初始化引擎](../InitEngine/index.md)。
3. **`rules` 与选项分离**——规则表达的是「两个选择之间的关系」，塞进任一侧的选项里都会让模型失衡。规则引擎实现见 [引导器服务端](../WizardBackend/index.md)。
:::

### 2.2 类型定义（前后端共享）

```ts [app/utils/wizard/option-model.ts]
export type Column = 'left' | 'right';
export type RuleLevel = 'block' | 'warn' | 'info';

export interface OptionItem {
  value: string;
  label: string;
  desc: string;
  note?: string;
  deps?: string[];
  devDeps?: string[];
  modules?: string[];
  files?: string[];
}

export interface OptionGroup {
  key: string;
  label: string;
  column: Column;
  multiple: boolean;
  default: string | string[];
  options: OptionItem[];
}

export interface Rule {
  level: RuleLevel;
  when: Record<string, string | string[]>;
  message: string;
}

export interface WizardSchema {
  version: string;
  groups: OptionGroup[];
  rules: Rule[];
}

export type Selection = Record<string, string | string[]>;
```

::: warning 这个文件是「类型 only」的
`app/utils/wizard/` 整个目录会随引导器删除，所以这里**只能放类型与常量**。一旦写入运行时函数，删除后就会留下断掉的 import。共享的运行时逻辑放 `shared/` 目录（Nuxt 4 的共享层，客户端与服务端都能用）。
:::

## 3. 从模型到表单

呈现形态不由 `multiple` + 选项数猜出来，而是写在 `options.json` 的 `renderAs` 字段里。引擎不解释它的样式，只保证取值合法——加一个分组、换一种形态都不用改前端：

| `renderAs` | 用于 | 长什么样 |
| --- | --- | --- |
| `radios` | 全部单选组（左栏三组 + 渲染模式 + 包管理器） | 横向单选按钮组，每个候选一个「○ 名称」小块，整组左右排开、放不下才换行 |
| `checks` | 模块、工程开关（多选） | 复选行，勾选后展开「附带文件」 |

::: info 形态只有两种，是有意收窄的
早先还有 `cards`（带标题与说明的纵向卡片）与 `select`（原生下拉）：前者在横向排布下与 `radios` 重复，后者只有两个取值、不如直接摊开成单选按钮。**留着没人使用的形态会让「组件实现的」与「类型声明的」对不上**——自测 A10 正是卡这一条（它要求两者一一对应），所以删形态时类型、`options.json`、组件分支三处必须一起动。

`renderAs` 落在联合类型之外时，组件渲染的是一块**可见的报错**而不是空白（服务端的 `assertShape` 只校验选择、不校验这个字段）。静默不渲染的后果是「某个分组整块消失」而控制台干干净净，最难定位。
:::

```vue [app/components/wizard/OptionGroup.vue]
<script setup lang="ts">
/**
 * 渲染一个分组。两种控件形态由 options.json 的 `renderAs` 决定，组件不猜：
 * `radios` = 横向单选按钮组，`checks` = 复选行。
 *
 * 为什么用原生 <input type="radio|checkbox">：
 * ① 键盘导航、屏幕阅读器语义、焦点管理全部白送，自己用 div 造要写两百行还写不对；
 * ② 引导期是零依赖的（dependencies 里只有 nuxt），不能用组件库；
 * ③ 这些组件会在初始化时被删除 —— 不值得为它引入任何依赖。
 * 样式靠 :checked 与 :has() 完成，见 app/assets/styles/wizard.css。
 */
import type { OptionGroup, OptionItem, Selection } from '~/utils/wizard/option-model';

const props = defineProps<{
  group: OptionGroup;
  modelValue: Selection;
  blocked: Set<string>;   // 被 block 规则命中的选项 value 集合
}>();
const emit = defineEmits<{ 'update:modelValue': [Selection] }>();

const current = computed(() => props.modelValue[props.group.key]);

function pick(value: string) {
  if (props.blocked.has(value)) return;
  emit('update:modelValue', { ...props.modelValue, [props.group.key]: value });
}

function toggle(value: string, checked: boolean) {
  const list = Array.isArray(current.value) ? [...current.value] : [];
  const next = checked ? [...new Set([...list, value])] : list.filter(v => v !== value);
  emit('update:modelValue', { ...props.modelValue, [props.group.key]: next });
}

/** 横向单选小块的悬停提示：说明 + 会装什么 + 实验性原因，拼成一段 */
function hintFor(opt: OptionItem) {
  const parts = [opt.desc, opt.note];
  if (opt.experimental) parts.push(`实验性：${opt.experimentalReason}`);
  return parts.filter(Boolean).join('\n');
}
</script>

<template>
  <fieldset class="group">
    <legend>{{ group.label }}</legend>
    <p v-if="group.desc" class="group__desc">{{ group.desc }}</p>

    <!-- radios：全部单选组。横向排开，说明收进 title -->
    <div v-if="group.renderAs === 'radios'" class="radio-row">
      <label
        v-for="opt in group.options"
        :key="opt.value"
        class="radio"
        :class="{ 'is-blocked': blocked.has(opt.value) }"
        :title="hintFor(opt)"
      >
        <input
          type="radio"
          :name="group.key"
          :value="opt.value"
          :checked="current === opt.value"
          :disabled="blocked.has(opt.value)"
          @change="pick(opt.value)"
        >
        <span class="radio__label">{{ opt.label }}</span>
        <span v-if="opt.experimental" class="radio__flag">实验性</span>
      </label>
    </div>

    <!-- checks：模块与工程开关（多选，每项一行说明，保持纵向） -->
    <div v-else-if="group.renderAs === 'checks'" class="row-stack">
      <label v-for="opt in group.options" :key="opt.value" class="row">
        <input
          type="checkbox"
          :value="opt.value"
          :checked="Array.isArray(current) && current.includes(opt.value)"
          :disabled="blocked.has(opt.value)"
          @change="toggle(opt.value, ($event.target as HTMLInputElement).checked)"
        >
        <strong>{{ opt.label }}</strong>
        <span class="desc">{{ opt.desc }}</span>
      </label>
    </div>

    <!-- 兜底：renderAs 落到联合类型之外时必须**吵**，不能静默不渲染 -->
    <div v-else class="hint hint--block">
      未知的控件形态 renderAs={{ group.renderAs }}，分组「{{ group.label }}」未能渲染。
    </div>
  </fieldset>
</template>
```

::: tip 为什么用原生 `<input type="radio|checkbox">`
① 键盘导航、屏幕阅读器语义、表单可访问性全部白送；② 不依赖任何组件库，符合「引导期零依赖」；③ 初始化后这些组件会被删除，不值得为它引入依赖。样式靠 `:checked + 兄弟选择器` 与 `:has()` 完成。
:::

## 4. 三层规则：阻断 / 警告 / 提示

`rules` 里的 `level` 决定页面行为，**只有 `block` 会禁用「初始化项目」按钮**：

| level | 语义 | 页面表现 | 能否提交 |
| --- | --- | --- | --- |
| `block` | 组合会导致构建失败或运行冲突 | 冲突项置灰、下方红字说明、底部按钮禁用并提示「有 N 项冲突」 | ❌ |
| `warn` | 能跑，但有冗余或体积代价 | 黄色提示条，列出「为什么冗余、建议怎么改」 | ✅ |
| `info` | 纯粹的知识性说明 | 灰色提示条 | ✅ |

### 4.1 典型规则清单

| 组合 | level | 理由 |
| --- | --- | --- |
| Nuxt UI + UnoCSS | `block` | Nuxt UI 基于 Tailwind v4，两套工具类解析器会互相覆盖 |
| Nuxt UI + Tailwind CSS | `info` | Tailwind 由 Nuxt UI 自带，显式选上只是确认，不重复安装 |
| Nuxt UI + Sass | `warn` | Tailwind 4 自身不依赖 Sass，但两者共存需注意 `@import` 顺序 |
| Vuetify + Tailwind | `warn` | Vuetify 自带大量基础样式与 Tailwind 的 preflight 会相互影响，需手动调整 |
| Tailwind + UnoCSS | `block` | 两个原子化引擎同时生效，产出重复且不可预测 |
| 预处理器 = 无 + 原子化 = 无 | `info` | 纯 CSS 方案，组件内样式写在 `<style scoped>` 里 |
| SSG + i18n | `info` | 需为每种语言生成路由，构建时间与页面数成倍 |
| SPA + SEO 模块 | `warn` | SPA 下 SEO 模块能力受限，建议改用 SSR |
| UI 框架 = 无 + Icon 模块 | `info` | Nuxt Icon 可独立使用，和组件库无关 |

::: danger 规则必须双向可读
每条 `message` 都要写清「**为什么冲突**」和「**怎么改**」，只写「不能同时选」等于让用户猜。上面 Nuxt UI + UnoCSS 的文案就是范本：说清原因（工具类解析冲突）+ 给出两条出路。
:::

## 5. 选择页状态机

引导页不是「一个表单 + 一个按钮」，它有明确的状态迁移：

```text
idle ──(加载 schema)──► selecting ──(点「预览变更」)──► planned
   ▲                        │                            │
   │                        │(改任一选项)                 │(点「初始化项目」)
   └────────────────────────┘                            ▼
                                                     running ──► done
                                                        │
                                                        └──► failed（可重试，进度保留）
```

| 状态 | 页面表现 | 可做的事 |
| --- | --- | --- |
| `selecting` | 三区表单可编辑，底部按钮为「初始化项目」但点击先出计划 | 改选项 |
| `planned` | 右上角预览面板自动展开（「将安装的依赖 / 将删除的文件 / 将写入的配置」） | 确认或回退 |
| `running` | 表单整体 `disabled`，进度面板接管（五阶段 + 日志行） | 只能等或中断 |
| `done` | 显示完成摘要 + 下一步命令（`pnpm dev`） | 打开首页 |
| `failed` | 显示失败的阶段、错误原文、可回滚提示 | 重试 / 联系维护者 |

::: warning 用户离开页面时必须拦
从点下「初始化项目」到跑完，中间会删除文件并安装依赖。此时若用户关闭标签页，**半成品仓库是最难排查的状态**。做法：`running` 状态下注册 `beforeunload`（导航离开警告），同时在服务端把「已开始执行」写成文件标记 `template.init.lock`——即使页面关了，重开也能看到进度与结论。
:::

## 6. 交互细节清单

这些细节不做不算错，做了体验会明显不同：

| 细节 | 做法 | 收益 |
| --- | --- | --- |
| **默认值就是推荐组合** | 默认 `无 UI / 无预处理器 / 无原子化 / SSR / Pinia + Icon / ESLint + 测试` | 直接点「初始化」也能得到能跑的工程 |
| **选择状态可分享** | 把 `Selection` 序列化进 URL query（如 `?ui=element-plus&css=sass`） | 同事之间可以发链接对齐技术栈 |
| **本地记住上次选择** | `localStorage` 存上一次的 `Selection` | 重复初始化第二个项目时省事 |
| **实时依赖预览** | 右上角常驻折叠面板，展示去重后的依赖清单与大致数量 | 用户对「会装多少东西」有预期 |
| **计划与实际一致** | 「预览变更」调用的接口和「初始化」是同一份 `plan` 计算 | 不会出现「说删 7 个文件、实际删了 9 个」 |
| **错误原文不美化** | 失败时展示引擎的原始输出（可折叠） | 排障时这行字比任何友好文案都有用 |
| **`prefers-reduced-motion`** | 进度动效在系统设置「减少动态效果」时关闭 | 可访问性 |
| **键盘全可达** | Tab 顺序 = 左栏 → 右栏 → 底部按钮；`Enter` 提交 | 可访问性 |

## 7. 组件清单

| 组件 | 职责 | 删除时机 |
| --- | --- | --- |
| `OptionGroup.vue` | 渲染一个分组的控件（横向单选 / 复选行，由 `renderAs` 决定） | 初始化时删除 |
| `NuxtConfigPanel.vue` | 右栏容器（渲染模式、模块、工程开关、包管理器） | 初始化时删除 |
| `ConflictHint.vue` | 三层规则的呈现（红/黄/灰） | 初始化时删除 |
| `DependencyPreview.vue` | 右上角的依赖与变更预览面板 | 初始化时删除 |
| `ProgressStream.vue` | 消费 SSE，渲染五阶段进度与日志 | 初始化时删除 |
| `useWizard.ts` | 状态机与接口调用 | 初始化时删除 |

::: danger 组件之间引用必须写显式 `import`

这六个组件都在 `app/components/wizard/` 下，Nuxt 会**按目录加前缀注册**：自动导入的名字是 `WizardOptionGroup`，而不是 `OptionGroup`。所以在别的组件里直接写 `<OptionGroup>` 不会报错、也不会警告，Vue 只会把它当成一个未解析的自定义元素 —— 页面表现是**那一块整片空白**，且控制台干净得让人无从查起（本页的右栏就这么空过一次）。

规范：`app/components/wizard/` 内部的互相引用一律 `import OptionGroup from '~/components/wizard/OptionGroup.vue'`，不依赖自动导入。另注意 `<script setup>` 里一个标识符只能有一个声明——同文件里既要用 `OptionGroup` 这个**类型**又要用它这个**组件**时，把类型改成 `OptionGroupSpec` 之类的别名。
:::

## 8. 验证方式

```shell
pnpm dev
# ① 打开 http://localhost:3000/setup
#    期望：左栏三个单选组、右栏顶部一块依赖预览 + 四个分组、底部按钮齐备；未加载 schema 时显示骨架态
#    每个单选组是一行横向排开的小块，悬停任一小块应弹出含「说明 + 会装什么」的原生 tooltip

# ② 制造一个 block 冲突：UI 选 Nuxt UI、原子化选 UnoCSS
#    期望：两个冲突项置灰 + 红字说明 + 底部按钮禁用并显示「有 1 项冲突」

# ③ 改成 UI = Nuxt UI、原子化 = Tailwind CSS
#    期望：冲突消失，提示条变为 info（说明 Tailwind 已随 Nuxt UI 安装）

# ④ 点「预览变更」
#    期望：右上角面板展开，列出 deps / devDeps / 将删除文件 / 将写入的 marker 区间键名；
#          文件多时面板内部自己滚动，不会把下面的分组推出屏幕

# ⑤ 键盘操作
#    期望：Tab 可遍历全部控件，焦点环清晰，Enter 能触发预览
```

## 相关页面

- [引导器服务端与安全边界](../WizardBackend/index.md)：这份模型由谁校验、怎么变成计划
- [技术栈矩阵与组合兼容](../StackMatrix/index.md)：规则清单背后的完整依赖映射
- [零依赖引导期骨架](../Bootstrap/index.md)：这些组件与样式的落盘位置

## 参考资料

- 表单与可访问性基线：[MDN · Form accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility/Guides/Forms)
- `prefers-reduced-motion`：[MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)
- Vue 3 组合式 API（`computed` / `defineProps`）：[vuejs.org](https://vuejs.org/api/sfc-script-setup.html)
