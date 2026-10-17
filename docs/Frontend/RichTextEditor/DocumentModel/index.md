# 文档模型：把 HTML 关进 schema

文档模型（document model）是编辑器的**唯一可信数据源**。它决定了三件事：什么内容合法、位置怎么表示、以及一份文档能不能被可靠地比较、序列化与协同。

这一页要解决的核心问题只有一个：**为什么不能把 `contenteditable` 产生的 DOM 直接当数据。**

![文档模型的四层：schema、树、位置、ID](../assets/rte-model-layers.svg)

## 判据族声明

本页判据族 `DOC-A` ~ `DOC-H`，共 8 条。定义表在第八节。

## 一、DOM 为什么不能当模型：四条硬伤

| 硬伤 | 具体表现 | 后果 |
| --- | --- | --- |
| **浏览器会改写结构** | `<p>外层<p>内层` 被自动"修正"成两个并列 `<p>`；`<b>` 里嵌 `<b>` 被合并 | 你写进去的和你读出来的不是同一棵子树 |
| **同一语义有多种写法** | 加粗可以是 `<b>`、`<strong>`、`<span style="font-weight:700">` | 后端解析必须枚举所有变体，且随浏览器升级失效 |
| **没有稳定位置** | DOM 节点会被复用、移动、重建；`Range` 在重绘后失效 | 无法表达"从第 3 段第 2 字到第 5 段末" |
| **允许非法嵌套** | `<table>` 里放裸文本、`<p>` 里放 `<div>` | 序列化成 Markdown/PDF 时无处安放 |

::: danger 一个真实事故的因果链
某产品的"导出 Markdown"功能上线后，10% 的历史文章格式全乱。根因是：早期用户用 Safari 编辑，回车产物是 `<p>`；后来团队在 Chrome 里做了一次"批量清洗"，脚本假设段间分隔是 `<div>`——于是 `<p>` 被当成行内标签原样保留，两层段落变成一层。

**只要数据源是 DOM，这类事故就会周期性复发**，因为 DOM 的形状由浏览器版本决定，而不是由你的业务决定。
:::

## 二、三种模型形态：树、扁平、块

| 形态 | 代表 | 结构 | 优点 | 代价 |
| --- | --- | --- | --- | --- |
| **递归树** | ProseMirror、Lexical | `Node { type, attrs, content: Node[] }` | 表达力最强（表格、嵌套列表天然支持） | 位置计算与遍历要递归；深树容易栈溢出 |
| **扁平数组** | Slate | `Node[]`，段落是数组元素，行内也是数组 | 遍历与 diff 简单；React 渲染直接 | 嵌套结构（表格）要靠约定表达 |
| **块列表** | Notion 式、BlockNote | `Block[]`，块内是受限的行内内容 | 并发粒度天然是块；UI 与数据同构 | 表达力受限；跨块操作（选中两段合并）要额外写 |

本专题后续代码以**递归树**为主，因为它是 ProseMirror 系（Tiptap、Atlassian 编辑器、NYT 编辑器）的共同底座，也是"表达力最强"的一端；理解了它，扁平与块模型只是"约束更少"的特例。

### 一个最小但完整的文档

```typescript
// 一份"标题 + 段落（含加粗与链接）"的文档，用 JSON 表示
type DocNode = {
  type: string;
  attrs?: Record<string, unknown>;
  marks?: Mark[];
  text?: string;
  content?: DocNode[];
};

type Mark = { type: string; attrs?: Record<string, unknown> };

const doc: DocNode = {
  type: 'doc',
  content: [
    { type: 'heading', attrs: { level: 2 }, content: [{ type: 'text', text: '发布说明' }] },
    {
      type: 'paragraph',
      content: [
        { type: 'text', text: '本版修复了 ' },
        { type: 'text', text: '粘贴', marks: [{ type: 'strong' }] },
        { type: 'text', text: ' 的问题，详见 ' },
        { type: 'text', text: '变更记录', marks: [{ type: 'link', attrs: { href: 'https://example.com/changelog' } }] },
      ],
    },
  ],
};
```

要点：**文本与标记是分开的**。`text` 节点只存纯文本，样式在 `marks` 里。这样"取纯文本"永远不需要解析 HTML，而"加粗三个字"也不会变成三次节点创建。

## 三、schema：用文法约束内容

schema 不是"校验函数"，而是**文档的文法**。它以"内容表达式"（content expression）描述每种节点允许装什么：

```typescript
import { Schema } from 'prosemirror-model';

export const schema = new Schema({
  nodes: {
    doc: { content: 'block+' },                        // 顶层只能是块
    paragraph: { group: 'block', content: 'inline*', toDOM: () => ['p', 0] },
    heading: {
      group: 'block',
      content: 'inline*',
      attrs: { level: { default: 2 } },
      defining: true,                                   // 编辑时不会被自动拆散
      toDOM: (node) => [`h${node.attrs.level}`, 0],
      parseDOM: [{ tag: 'h2', attrs: { level: 2 } }, { tag: 'h3', attrs: { level: 3 } }],
    },
    blockquote: { group: 'block', content: 'block+', defining: true, toDOM: () => ['blockquote', 0] },
    bullet_list: { group: 'block', content: 'list_item+', toDOM: () => ['ul', 0] },
    list_item: { content: 'paragraph block*', toDOM: () => ['li', 0] },
    text: { group: 'inline' },
    image: {
      group: 'inline',
      inline: true,
      attrs: { src: {}, alt: { default: '' } },
      toDOM: (n) => ['img', { src: n.attrs.src, alt: n.attrs.alt }],
    },
  },
  marks: {
    strong: { toDOM: () => ['strong', 0], parseDOM: [{ tag: 'strong' }, { tag: 'b' }] },
    em: { toDOM: () => ['em', 0], parseDOM: [{ tag: 'em' }, { tag: 'i' }] },
    link: {
      attrs: { href: {} },
      inclusive: false,                                  // 光标移到链接末尾后不再继续加链接
      toDOM: (m) => ['a', { href: m.attrs.href, rel: 'noopener noreferrer nofollow' }, 0],
      parseDOM: [{ tag: 'a[href]', getAttrs: (dom) => ({ href: (dom as HTMLElement).getAttribute('href') }) }],
    },
  },
});
```

四条设计纪律：

1. **`doc` 的内容表达式用 `block+`**，不要用 `(paragraph | heading)*`——前者允许你以后加新块类型而不用改 doc。
2. **`defining: true` 给"容器型"节点**（heading、blockquote、list_item），否则删除时浏览器式的"合并段落"会把它拆掉。
3. **`inclusive: false` 给 link**，这是"为什么我在链接后面继续打字，字也变蓝了"的根因。
4. **`attrs` 只放必要字段**，`class`、`style` 一律不进模型——它们是渲染细节，应该在 `toDOM` 里由节点类型决定。

## 四、位置：ProseMirror 的 pos 不是字符下标

这是新手最容易算错的一件事。**位置计数的是"节点边界与字符"的总和**，不是字符数。

```text
文档：  <p>ab</p><p>cd</p>
pos 序列：
  0      1  2   3     4   5  6   7
  起始  a  b   </p>  起始 c  d  </p>
```

也就是说：第 1 个段落的文本从 `1` 到 `3`，第 2 个段落从 `5` 到 `7`。**段落边界各占 1 个位置**。

| 想表达 | 错误写法 | 正确写法 |
| --- | --- | --- |
| 第 2 段开头 | `doc.content[1].text.length` | `2`（第一段内容 2 + 两个边界）或 `doc.child(0).nodeSize + 1` |
| 全文末尾 | `text.length` | `doc.content.size` |
| 选中第 1 段全部 | `{ from: 0, to: 2 }` | `{ from: 1, to: 3 }`（0 是段落外） |

::: danger 别用"字符偏移"给跨页数据定位
"评论锚点存在第 120 个字符"这种设计，在**第一段被改短的那一刻**就失效了。跨请求、跨设备、跨版本的位置必须用**节点 ID + 节点内相对偏移**（见下一节），而不是全局字符下标。
:::

## 五、节点 ID：稳定引用从哪来

编辑器内部的位置（`pos`）是**相对于当前文档**的，文档一变就失效。但业务需要"这条评论挂在这段话上""这条待办指向这个块"——这需要**稳定 ID**。

| 方案 | 怎么生成 | 适用 | 风险 |
| --- | --- | --- | --- |
| **块级 ID（推荐）** | 创建块时写 `attrs.id = uuidv7()` | 评论锚点、待办、协同块锁 | ID 会随"复制粘贴"重复，需要去重策略 |
| **内容哈希** | `sha1(块文本)` | 只读引用、去重 | 改一个字就变，无法当锚点 |
| **路径** | `[0,2,1]` 这样的下标链 | 临时定位 | 插入一段就全错位 |
| **字符偏移** | 全文累加 | 同版本内的临时选区 | 跨版本必失效 |

```typescript
// 给每个顶层块补 ID（幂等：已有 ID 的不动）
function ensureBlockIds(doc: DocNode, gen = () => crypto.randomUUID()): DocNode {
  return {
    ...doc,
    content: (doc.content ?? []).map((block) => ({
      ...block,
      attrs: { ...block.attrs, id: (block.attrs?.id as string) ?? gen() },
    })),
  };
}
```

::: tip 复制粘贴时的 ID 冲突
用户复制一个块再粘贴，`attrs.id` 会被一起复制（因为粘贴走的是"克隆节点"）。**必须在粘贴管线里重写 ID**——这一条放在[粘贴与内容清洗](../PasteSanitize/index.md)的第五步，那一页的第八条判据就是它。
:::

## 六、六条模型不变量

任何时刻，一份合法文档都应满足：

| 不变量 | 检查方式 |
| --- | --- |
| 顶层只有块节点 | `doc.content.every(n => schema.nodes[n.type].isBlock)` |
| 行内节点不出现在块外 | `text` / `image` 的父节点必须是 `paragraph`/`heading` 之类 |
| 每个块有唯一 ID | `new Set(ids).size === ids.length` |
| 空块只有一个（末尾的"空段落"） | 末尾最多一个无文本段落 |
| 标记不跨节点嵌套冲突 | 同一 `text` 节点内不出现两个 `link` |
| 文档大小有上限 | `JSON.stringify(doc).length ≤ 上限`（建议 256 KB） |

## 七、一份文档的三种等价表示

| 表示 | 用途 | 是否可信 |
| --- | --- | --- |
| **JSON 树** | 落库、协同、迁移 | ✅ 唯一可信源 |
| **DOM** | 渲染与用户交互 | ❌ 由浏览器生成，随时可被改写 |
| **HTML 字符串** | 展示缓存、邮件、导出 | ⚠️ 派生数据，可重建但不可回读 |

「可回读」是分水岭：如果一份表示能被**无损**解析回 JSON，它才可以当输入；`innerHTML` 永远不满足这一条。

## 八、判据表

| 编号 | 约定 | 定错了会怎样 | 怎么验证没被破坏 |
| --- | --- | --- | --- |
| `DOC-A` | 落库的是 JSON 树，HTML 只能是派生缓存 | 历史数据无法迁移、导出格式失控 | 表结构里正文列类型为 `jsonb`/`text` 存 JSON，HTML 列命名含 `_cache`/`_html` 且有重建脚本 |
| `DOC-B` | schema 必须是唯一的、可被服务端复用的定义 | 前后端各写一套白名单，必然漂移 | 同一份 schema 文件被前端与服务端同时 import，或存在一致性测试 |
| `DOC-C` | 禁止用字符偏移做跨请求定位 | 内容一改，锚点全错 | 评论/待办表的定位字段里没有"纯整数偏移" |
| `DOC-D` | 每个块必须有稳定 ID，且粘贴时重写 | 复制粘贴后两条评论挂到同一个块 | 复制一个块再粘贴，两块 ID 不同 |
| `DOC-E` | `link` 必须 `inclusive: false` 且有协议白名单 | 打链接后继续输入的字也变链接；`javascript:` 可执行 | 在链接末继续打字，模型里新文本无 link 标记 |
| `DOC-F` | 模型层必须能在 Node 里跑（不依赖 DOM） | 所有测试要起浏览器，CI 慢且不稳 | `vitest` 的 node 环境下有模型层测试且通过 |
| `DOC-G` | 文档必须有大小上限与深度上限 | 一次粘贴 5 MB 内容把标签页卡死 | 存在 `serialize(doc).length` 与递归深度的阈值断言 |
| `DOC-H` | 渲染必须是 `doc → DOM` 的单向函数 | 视图反写模型导致回环与重复字符 | 全仓搜索视图层对 `doc` 的直接赋值，命中数为 0 |

## 如何验证

下面这段在 Node 里就能跑（不需要浏览器），验证"位置不是字符下标"这个最容易错的点：

```javascript
// 用最小的自定义模型演示 pos 计数规则
function nodeSize(node) {
  if (node.text != null) return node.text.length;
  // doc 没有"开/闭"两个位置，其余节点各占 1 个开位置与 1 个闭位置
  let size = node.type === 'doc' ? 0 : 2;
  for (const child of node.content ?? []) size += nodeSize(child);
  return size;
}

const para = (t) => ({ type: 'paragraph', content: [{ type: 'text', text: t }] });
const doc = { type: 'doc', content: [para('ab'), para('cd')] };

console.log(nodeSize(doc));                      // 8  = 4 + 4（两个段落）
console.log(nodeSize(para('ab')));               // 4  = 2 字符 + 2 边界
```

**预期输出**：`8` 与 `4`。两个各含 2 个字符的段落，内容总大小是 **8** 而不是 4——多出来的 4 是两个段落各自的开关边界。这与 ProseMirror 的语义一致：`doc.content.size = 8`，而 `doc.nodeSize = 10`（多了 doc 自己的两个边界）。

把它和"直接取 `text.length`"对比一下，就会明白为什么用字符下标做定位会在插入段落后全部错位。

## 参考资料

- [ProseMirror · Schema guide](https://prosemirror.net/docs/guide/#schema)——内容表达式与 `defining` / `inclusive` 的官方说明
- [ProseMirror Reference · Node](https://prosemirror.net/docs/ref/#model.Node)——`nodeSize`、`content.size` 的精确定义
- [Lexical · Nodes](https://lexical.dev/docs/concepts/nodes)——递归节点与不可变状态的设计
- [Slate · Data model](https://docs.slatejs.org/concepts/02-nodes)——扁平数组模型的取舍
- [JSON Schema](https://json-schema.org/)——服务端二次校验时可复用的约束描述语言
