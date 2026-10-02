# 引导页：信息架构与选择模型

引导页要做两件事，而且必须同时做对：**看起来很直观**（用户三十秒内能选完），**模型上没有歧义**（后端拿到的选择一定能被机器校验）。前者靠布局，后者靠一份唯一的选择模型。

![引导页两栏布局：左栏技术栈 / 右栏 Nuxt 配置 / 底部操作条；依赖与变更预览是弹窗](../assets/wizard-layout.svg)

## 1. 信息架构

页面是**两栏 + 底部操作条**，位置即语义——左栏改变「用什么写」，右栏改变「怎么跑」。第三件事「即将发生什么」不占这两栏：它以**弹窗**呈现，由底部的「预览变更」按钮唤出。

| 区 | 分组 | 控件 | 默认值 | 影响面 |
| --- | --- | --- | --- | --- |
| 左 | UI 框架 | 横向单选 ×5（无 / Element Plus / Ant Design Vue / Nuxt UI / Vuetify） | 无 | 依赖 + 自动导入配置 + 样式入口 |
| 左 | CSS 预处理器 | 横向单选 ×4（无 / Sass / Less / Stylus） | 无 | 依赖 + 组件内样式语言 + Stylelint 配置 |
| 左 | 原子化框架 | 横向单选 ×3（无 / UnoCSS / Tailwind CSS） | 无 | 依赖 + 构建插件 + 样式入口优先级 |
| 右 | 渲染模式 | 横向单选 ×4（SSR / SPA / SSG / 混合） | SSR | `ssr` 开关 + `routeRules` + 部署形态 |
| 右 | Nuxt 模块 | 列表面板 ×6 候选（Pinia / VueUse / i18n / Icon / Image / SEO） | Pinia、Icon | `modules` 数组 |
| 右 | 工程开关 | 列表面板 ×4 候选（ESLint、测试栈、TS 严格度、Docker） | ESLint、测试栈、严格 TS | 依赖 + 配置文件 |
| 右 | 包管理器 | 横向单选 ×2（pnpm / npm） | pnpm | 锁文件 + 安装命令 |
| 弹窗 | 依赖与变更预览 | 模态弹窗（底部「预览变更」唤出） | 不弹出 | 会装什么、删什么、生成什么、写哪些区间；不是选择项 |

::: tip 为什么「渲染模式」放在右侧而不是左侧
左侧三个维度是**技术栈身份**——选完基本不会再改，团队之间差异最大。右侧是**运行形态与工程配置**——同一个团队的不同项目会不一样，也可能初始化后再手动调整。把「身份」和「配置」分区，用户的心智负担最小。
:::

### 1.1 每个控件的呈现规则

| 控件形态 | 用于 | 交互 |
| --- | --- | --- |
| 卡片外壳 | 全部七个分组（下面两种形态共用） | 1px 边框 + 左侧 3px 品牌色竖条 + 12px 圆角 + 极浅投影。分组标题就是卡片标题：单选组是骑在上边框上的胶囊 `<legend>`，多选组在面板头的浅底横条里。页首与栏目标题用的是同一条竖条——层级靠同一条线索读出来，而不是靠字号堆砌 |
| 横向单选按钮组 | 全部单选组：UI 框架、预处理器、原子化（左栏），渲染模式、包管理器（右栏） | 每个候选一个带边框的小块，整组左右排开、一行放不下才换行；选中态是边框 + 底色 + 标签加粗变色；「说明 + 会装什么」收进 `title`，悬停可见 |
| 列表面板 | Nuxt 模块、工程开关（右栏） | 卡片由面板本身充当：面板头左侧是分组名与「已选 n / 共 m」，右侧是「新增」按钮；下方是可滑动列表，每行一个已加入项 + 「移除」。候选项与每项的说明都在「新增」弹窗里 |
| 模态弹窗 | 依赖与变更预览、新增候选项 | 原生 `<dialog>` + `showModal()`：遮罩、焦点陷阱、Esc 关闭、点遮罩关闭、背景不可交互，全部来自浏览器 |

### 1.2 「会装什么」必须有地方看得到

单选组一律**横向**排开：组内是互斥关系，横向正好呼应「从这几个里挑一个」；候选彼此相邻时，名字长短、有没有「实验性」标记都是一眼可比的，竖排一列反而要上下移动视线。每项只占一行「○ 名称」，说明与「会装什么」收进元素的 `title`。

多选组（模块、工程开关）改成**列表面板**：面板只说「已加入哪些」，候选项与每项说明放进「新增」弹窗。理由是这两组属于「按需追加」——多数候选长期处于未选中状态，把它们的说明一直挂在版面上，换来的是「每次都要滚过一段与自己无关的文字」。列表有高度上限、自己滚，所以选满 6 个模块也不会把右栏撑长。

第三层是**模态弹窗**：依赖与变更预览回答的是「点下去会发生什么」，属于一次性核对，不是要一直盯着的配置。它先在右栏顶部常驻过一版，问题是展开高度会不断挤压下面那些才要反复调的控件，缩成一行标题又等于没显示——两头不讨好，于是干脆从版面里拿掉，要看时再弹出来。

三种形态遵循同一条标准：**选择成本主要来自不确定**——用户不是不知道该选哪个，而是不知道选了会带来什么。所以信息不删，只决定它是「一直占着版面」「需要时展开」还是「需要时弹出」。用 `title` 而不是自造 tooltip 还有一层原因：按 HTML-AAM，`title` 就是表单控件的 accessible description，屏幕阅读器拿到的是同一份内容，不是只给鼠标用的。

第四层是**卡片**：七个分组在版面上都是一张卡片，分组标题即卡片标题。这不只是装饰——横向单选组与列表面板本来长得完全不同，套上同一套外壳（左竖条 / 圆角 / 投影）之后，「这是七件事、每件要做一个决定」才一眼看得出来，而不是「一堆零散的控件」。

与卡片同时定下的是**说明文字的取舍**：页面上只留页首那一句。七个分组各自的说明（`desc`）不再渲染——它们与卡片标题讲的是同一件事（「UI 框架：决定组件从哪来」），七段都摊在这里时，唯一有信息量的页首那句反而被淹没了。撤掉不等于删掉：悬停候选项能看到 `title`，打开「新增」弹窗能看到每项的完整说明，`desc` 还留在 `options.json` 里没动。

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
| `checks` | Nuxt 模块、工程开关（多选） | 列表面板：面板头右上角「新增」+ 下方可滑动列表；候选项与说明在「新增」弹窗里 |

::: info 形态只有两种，是有意收窄的
早先还有 `cards`（带标题与说明的纵向卡片）与 `select`（原生下拉）：前者在横向排布下与 `radios` 重复，后者只有两个取值、不如直接摊开成单选按钮。**留着没人使用的形态会让「组件实现的」与「类型声明的」对不上**——自测 A10 正是卡这一条（它要求两者一一对应），所以删形态时类型、`options.json`、组件分支三处必须一起动。

`renderAs` 落在联合类型之外时，组件渲染的是一块**可见的报错**而不是空白（服务端的 `assertShape` 只校验选择、不校验这个字段）。静默不渲染的后果是「某个分组整块消失」而控制台干干净净，最难定位。

A10 还给形态与版面钉了结构断言。三条老的：多选面板必须有「新增」按钮、必须有 `<dialog>` 弹窗、列表必须有高度上限——三个部件缺任何一个都会**静默退化**，少了弹窗「新增」就是个点不动的空按钮，少了高度上限列表一长就回到「把整页撑长」的老样子。卡片化之后又加了两组：**三个页面文件里都不许再出现 `class="group__desc"`**、`wizard.css` 里不许再有 `.group__desc` 规则（说明撤掉是显式决定，而「给某个分组加回一段说明」是个不会报错的改动），以及两种形态的卡片外壳必须在（`.group--card` / `.group--panel` 的绑定、单选卡片与面板**各自**那条 3px 品牌色左竖条、`<legend>` 的规则）。十一条变异逐条改坏，全部报红。

判据一律锚定到具体标签或规则，不用裸子串：`wizard.css` 的注释里就写着 `group__desc`，组件注释里也写着 `<dialog>`（都在讲「已经撤掉了」），拿裸子串当判据的话，实现被改回去也照样绿——`<dialog>` 那一次就是这么被骗过去的。
:::

::: tip `<legend>` 会压进内边距
`<legend>` 不是普通块级元素：浏览器把它放在 fieldset 的**上边框**里，并且**向下压进内边距**。所以卡片的上内边距不能与其余三边同值——给 16px 时，胶囊标题恰好贴住第一行候选按钮。`.group--card` 用的是上 24px、其余三边 16px，这个数不是拍出来的：在 CDP 里量了「第一行候选.top − legend.bottom」，五个分组都留出 24px 才算过。读 CSS 源码看不出这个问题，必须真渲染。
:::

```vue [app/components/wizard/OptionGroup.vue]
<script setup lang="ts">
/**
 * 渲染一个分组。两种控件形态由 options.json 的 `renderAs` 决定，组件不猜：
 *   `radios` —— 横向单选按钮组。组内互斥，候选彼此相邻才好比。
 *   `checks` —— 「右上角新增 + 下方可滑动列表」的多选面板。候选默认不占版面，
 *               说明与「会装什么」收进「新增」弹窗，需要时再看。
 *
 * 形态之上套一层统一的「卡片」：每个分组都是一张带左侧品牌色竖条的卡片，
 * 组标题就是卡片标题 —— 单选组由 <legend> 骑在上边框上，多选组由 .panel 的面板头充当。
 * 分组说明（group.desc）不再渲染在页面上，整页只留页首那一句。
 *
 * 为什么用原生 <input> 与 <dialog>：
 * ① 键盘导航、屏幕阅读器语义、焦点陷阱、Esc 关闭、遮罩层全部白送，
 *    自己用 div 造要写两百行还写不对；
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
const isPanel = computed(() => props.group.renderAs === 'checks');

/** 面板里列出的是**已加入的项**，按 options.json 的顺序而不是点击顺序 */
const selected = computed(() => {
  const picked = current.value;
  const list = Array.isArray(picked) ? picked : [];
  return props.group.options.filter((opt) => list.includes(opt.value));
});

/** 草稿：勾选先落在草稿上，点「确定」才写回 —— 否则「取消」就没有意义了 */
const draft = ref<string[]>([]);

function openPicker() {
  draft.value = Array.isArray(current.value) ? [...current.value] : [];
  picker.value?.showModal();
}

function toggleDraft(value: string, checked: boolean) {
  // 只有「加进来」需要拦；「移出去」永远允许 —— 否则某项被规则禁掉后就卡在列表里出不去
  if (checked && props.blocked.has(value)) return;
  draft.value = checked ? [...new Set([...draft.value, value])] : draft.value.filter(v => v !== value);
}

function confirmDraft() {
  // 按 options.json 的顺序写回：勾选顺序会经 URL 与 localStorage 泄漏出去，
  // 同样的选择应该得到同样的链接。
  const next = props.group.options.map(o => o.value).filter(v => draft.value.includes(v));
  emit('update:modelValue', { ...props.modelValue, [props.group.key]: next });
  picker.value?.close();
}

function pick(value: string) {
  if (props.blocked.has(value)) return;
  emit('update:modelValue', { ...props.modelValue, [props.group.key]: value });
}

/** 悬停提示：说明 + 会装什么 + 实验性原因，拼成一段。两种形态都靠它兜住细节 */
function hintFor(opt: OptionItem) {
  const parts = [opt.desc, opt.note];
  if (opt.files?.length) parts.push(`附带文件：${opt.files.join('、')}`);
  if (opt.experimental) parts.push(`实验性：${opt.experimentalReason}`);
  return parts.filter(Boolean).join('\n');
}
</script>

<template>
  <!-- 单选组：fieldset 自己就是卡片（.group--card），<legend> 只能待在上边框上，
       正好当卡片标题；多选面板：卡片由 .panel 充当（面板头右侧要挂「新增」），
       fieldset 退成无框容器，分组名交给 aria-label ——
       否则屏幕阅读器只会念出「分组」两个字 -->
  <fieldset
    class="group"
    :class="isPanel ? 'group--panel' : 'group--card'"
    :aria-label="isPanel ? group.label : undefined"
  >
    <legend v-if="!isPanel">{{ group.label }}</legend>

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
          :checked="isSelected(opt.value)"
          :disabled="blocked.has(opt.value)"
          @change="pick(opt.value)"
        >
        <span class="radio__label">{{ opt.label }}</span>
        <span v-if="opt.experimental" class="radio__flag">实验性</span>
      </label>
    </div>

    <!-- checks：模块与工程开关。面板只说「已加入哪些」，候选与说明在弹窗里 -->
    <div v-else-if="group.renderAs === 'checks'" class="panel">
      <div class="panel__head">
        <h3 class="panel__title">{{ group.label }}</h3>
        <span class="panel__count">{{ selected.length }} / {{ group.options.length }}</span>
        <button type="button" class="panel__add" @click="openPicker()">新增</button>
      </div>
      <ul class="panel__list">
        <li
          v-for="opt in selected"
          :key="opt.value"
          class="panel__item"
          :title="hintFor(opt)"
        >
          <span class="panel__item-label">{{ opt.label }}</span>
          <button type="button" class="panel__remove" @click="remove(opt.value)">移除</button>
        </li>
        <li v-if="!selected.length" class="panel__empty">还没有添加，点右上角「新增」挑一个。</li>
      </ul>
    </div>

    <!-- 兜底：renderAs 落到联合类型之外时必须**吵**，不能静默不渲染 -->
    <div v-else class="hint hint--block">
      未知的控件形态 renderAs={{ group.renderAs }}，分组「{{ group.label }}」未能渲染。
    </div>

    <!-- 「新增」弹窗。原生 <dialog> + showModal() 负责遮罩、焦点陷阱与 Esc，
         零依赖也拿得到一套正确的模态行为 -->
    <dialog v-if="isPanel" ref="picker" class="modal modal--picker" @click="onBackdropClick">
      <div class="modal__panel">
        <header class="modal__head">
          <h2 class="modal__title">新增 · {{ group.label }}</h2>
          <button type="button" class="modal__close" aria-label="关闭" @click="closePicker()">×</button>
        </header>
        <div class="modal__body">
          <p class="modal__lead">{{ group.desc }} 勾选后点「确定」写回；已选中的取消勾选即为移除。</p>
          <label
            v-for="opt in group.options"
            :key="opt.value"
            class="pick"
            :class="{ 'is-checked': draft.includes(opt.value) }"
          >
            <input
              type="checkbox"
              :value="opt.value"
              :checked="draft.includes(opt.value)"
              :disabled="blocked.has(opt.value)"
              @change="toggleDraft(opt.value, ($event.target as HTMLInputElement).checked)"
            >
            <strong>{{ opt.label }}</strong>
            <span class="desc">{{ opt.desc }}</span>
            <span v-if="opt.files?.length" class="desc">附带文件：{{ opt.files.join('、') }}</span>
            <span v-if="opt.note" class="desc">{{ opt.note }}</span>
          </label>
        </div>
        <footer class="modal__foot">
          <span class="modal__note">已勾选 {{ draft.length }} / {{ group.options.length }} 项</span>
          <button type="button" @click="closePicker()">取消</button>
          <button type="button" data-primary @click="confirmDraft()">确定</button>
        </footer>
      </div>
    </dialog>
  </fieldset>
</template>
```

::: tip 为什么用原生 `<input>` 与 `<dialog>`
① 键盘导航、屏幕阅读器语义、表单可访问性，以及弹窗的遮罩、焦点陷阱、Esc 关闭全部白送——自己用 `div` 造一套正确的模态行为要写两百行还写不对；② 不依赖任何组件库，符合「引导期零依赖」；③ 初始化后这些组件会被删除，不值得为它引入依赖。样式靠 `:checked` 与 `:has()` 完成。

弹窗还有一个 `<dialog>` 特有的坑：**不要在 `.modal` 上写 `display`**。浏览器给未打开的 `dialog` 是 `display: none`，一旦覆盖（比如为了排版写成 `display: flex`），关掉的弹窗会一直留在页面上。所以布局只写在 `.modal[open]` 上。
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
| `selecting` | 两栏表单可编辑，底部按钮为「初始化项目」但点击先弹预览 | 改选项 |
| `planned` | 预览弹窗打开（「将安装的依赖 / 将删除的文件 / 将写入的配置区间」） | 确认或回退 |
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
| **依赖数量有预期** | 本地即时估算（不请求服务端），用于「还没算出计划」时的数量提示 | 用户对「会装多少东西」有预期，而不必先等一个往返 |
| **预览是弹窗，不是常驻面板** | 底部按钮唤出 `<dialog>`，七个清单在里面滚动 | 右栏只剩要反复调的控件；只读面板不占版面，也不推动页面 |
| **分组即卡片** | 七个分组共用同一套外壳（左侧品牌色竖条 / 12px 圆角 / 极浅投影）；页首与两栏标题复用同一条竖条 | 「有七件事要做」一眼可见，而不是「一堆零散的控件」 |
| **说明只留一处** | 分组说明（`desc`）不渲染在页面上，整页只留页首那一句；要细节就悬停选项或打开「新增」弹窗 | 七段重复标题的灰字撤掉之后，卡片之间的层次才看得出来 |
| **计划与实际一致** | 「预览变更」调用的接口和「初始化」是同一份 `plan` 计算 | 不会出现「说删 7 个文件、实际删了 9 个」 |
| **错误原文不美化** | 失败时展示引擎的原始输出（可折叠） | 排障时这行字比任何友好文案都有用 |
| **`prefers-reduced-motion`** | 进度动效在系统设置「减少动态效果」时关闭 | 可访问性 |
| **键盘全可达** | Tab 顺序 = 左栏 → 右栏 → 底部按钮；`Enter` 提交 | 可访问性 |

## 7. 组件清单

| 组件 | 职责 | 删除时机 |
| --- | --- | --- |
| `OptionGroup.vue` | 渲染一个分组（卡片外壳 + 横向单选 / 新增 + 可滑动列表，由 `renderAs` 决定），并自带「新增」弹窗 | 初始化时删除 |
| `NuxtConfigPanel.vue` | 右栏容器（渲染模式、模块、工程开关、包管理器）。只放控件，不放任何计划产物，也不放栏目说明 | 初始化时删除 |
| `ConflictHint.vue` | 三层规则的呈现（红/黄/灰） | 初始化时删除 |
| `DependencyPreview.vue` | 「预览变更」弹窗：依赖清单 + 文件变更 + 将写入的配置区间 | 初始化时删除 |
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
#    期望：左栏三张卡片（UI 框架 / CSS 预处理器 / 原子化框架）；右栏依次为渲染模式卡片、
#          Nuxt 模块面板、工程开关面板、包管理器卡片；每张卡片左侧都有一条品牌色竖条，
#          单选卡片的标题是骑在上边框上的胶囊（不要压住第一行候选）；
#          页面上只有页首那一句说明，七个分组里都没有灰字说明；
#          底部「恢复推荐默认 / 预览变更 / 初始化项目」齐备；未加载 schema 时显示骨架态
#    悬停任一单选项，应弹出含「说明 + 会装什么」的原生 tooltip

# ② 点某个面板右上角的「新增」
#    期望：弹出带遮罩的「新增 · Nuxt 模块」，列出全部 6 个候选与各自说明；
#          勾选先落在草稿上 —— 点「取消」不改变列表；
#          点「确定」后新增项按 options.json 的顺序出现在列表里；Esc 与点遮罩都能关掉

# ③ 把模块选满 6 个
#    期望：面板高度封顶、列表内部滚动，右栏不会被撑长

# ④ 制造一个 block 冲突：UI 选 Nuxt UI、原子化选 UnoCSS
#    期望：两个冲突项置灰 + 红字说明 + 底部按钮禁用并显示「有 1 项冲突」

# ⑤ 改成 UI = Nuxt UI、原子化 = Tailwind CSS
#    期望：冲突消失，提示条变为 info（说明 Tailwind 已随 Nuxt UI 安装）

# ⑥ 点「预览变更」
#    期望：弹出「依赖与变更预览」，七个清单（运行时/开发依赖、Nuxt 模块、样式入口顺序、
#          将写入的配置区间、将删除与将生成的文件）；内容超长时弹窗内部自己滚，
#          不推动背后的页面；长文件路径要能折行，不出现横向滚动条

# ⑦ 键盘操作
#    期望：Tab 可遍历全部控件与「新增」按钮，焦点环清晰；
#          弹窗打开后 Tab 只在弹窗内循环（焦点陷阱由浏览器提供）
```

## 相关页面

- [引导器服务端与安全边界](../WizardBackend/index.md)：这份模型由谁校验、怎么变成计划
- [技术栈矩阵与组合兼容](../StackMatrix/index.md)：规则清单背后的完整依赖映射
- [零依赖引导期骨架](../Bootstrap/index.md)：这些组件与样式的落盘位置

## 参考资料

- 表单与可访问性基线：[MDN · Form accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility/Guides/Forms)
- `prefers-reduced-motion`：[MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)
- Vue 3 组合式 API（`computed` / `defineProps`）：[vuejs.org](https://vuejs.org/api/sfc-script-setup.html)
