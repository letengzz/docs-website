# 语法降级的硬边界

本页判据族 `BBJ-A` ~ `BBJ-H`，共 8 条。

「把 target 调低一点就兼容了」这句话隐含一个假设：工具能把任何新语法改写成旧语法。这个假设**不成立**，而且不成立的方式很不友好——不是「降得不完美」，是「直接报错不产出」。本页先量清楚边界在哪（本机 esbuild 0.21.5 对 `es5` 全线失败），再讲降级之后**剩下了什么语义**（这一部分才是真正会咬人的地方），最后给一套「降级前后行为一致」的可跑验证。

::: tip 一句话理解
语法降级不是翻译，是**重写**：`async` 变成状态机、`class` 变成构造函数加原型、`#x` 变成外部存储。重写一定丢东西，问题只是丢的是「性能」还是「语义」。
:::

![语法降级的三个层次与各自的硬边界](../assets/bb-transpile-curve.svg)

## 一、降级其实是两件事

| 层次 | 做什么 | 由谁负责 | 失败可见性 |
| --- | --- | --- | --- |
| 语法改写 | 把新语法改写成旧语法的等价结构（`?.` → 嵌套判断、`class` → 构造函数） | 编译器的 `target` | **硬失败**：不支持时报错，不产出 |
| helper 注入 | 为改写后的代码补运行时函数（`_defineProperty`、`__awaiter`、`__spreadValues`） | 编译器 + `@babel/runtime` 一类共享包 | 静默：每个 chunk 各带一份，体积翻倍也无人报错 |
| API 补齐 | 补内置对象与方法（`Array.prototype.at`、`Object.hasOwn`） | polyfill | 静默：旧内核运行时才抛错 |

第一层是**编译期**的，第三层是**运行期**的，第二层夹在中间——它不改变语义，只决定体积。三层的失败方式完全不同，所以不能放在一个「兼容性」标签下讨论。

## 二、硬边界：本机实测的「降不下去」清单

同一份含 `class`、`const`、`let`、`async`、异步生成器、类字段的源码，用 esbuild 0.21.5 逐个目标编译（`--bundle --minify`，2026-11-12 本机）：

| 目标 | 结果 | 说明 |
| --- | --- | --- |
| `es5` | **失败** | `Transforming class syntax to the configured target environment ("es5") is not supported yet` |
| `es2015` 及更高 | 成功 | `es2015` 与 `es2016` 同体积，`es2017` 起明显下降 |

把语法点拆开逐个试 `es5`，失败清单如下（这是本页最有用的表）：

| 语法点 | `es5` 结果 | 报错里的主语 |
| --- | --- | --- |
| `const` / `let` | 失败 | `Transforming const to the configured target environment ("es5")` |
| `class` | 失败 | `Transforming class syntax ...` |
| 类字段 / 静态块 | 失败 | 同上（随 `class` 一起） |
| `async` / `await` | 失败 | `Transforming async functions ...` |
| 异步生成器 | 失败 | `Transforming async generator functions ...` |
| 箭头函数 / 模板字符串 / 展开 | 失败 | 都因同一份探针里的 `const` 先被拦下 |
| 可选链 / 空值合并 | 失败 | 同上，被 `const` 挡住，无法单独判定 |

最后两行是一个方法论提醒：**逐特性探针必须只含该特性**，否则会被同一文件里的 `const` 抢先报错，得出「可选链降不到 es5」的错误结论。把 `const` 换成 `var` 重跑，可选链与空值合并在 `es5` 上是能降的——但 `class` 与 `async` 仍然不行。

::: danger 三个必须知道的边界
1. **esbuild 不是 ES5 编译器。** 它的定位是「快」，官方明确不支持把 `class` / `async` 降到 `es5`。要 ES5 产物只能换 Babel、SWC 或 tsc（见 [ES5 兼容线](../LegacyES5/index.md)）。**正确做法**：基线含 IE 或旧 Android WebView 时，在选型阶段就把「谁负责降到 es5」写进技术方案。
2. **`target` 写错不会有人提醒你。** 把 `es2020` 误写成 `es202` 一类的拼写错误，工具会报错；但把 `es2020` 写成 `esnext` 是完全合法的——产物里保留最新语法，旧内核整包不执行。**正确做法**：`esnext` 只允许出现在「仅供本地调试」的配置里，产物配置必须有具体档位。
3. **降级成功 ≠ 语义一致。** 见下面第三节：`#私有字段` 降级后实例内存翻倍，`async` 降级后栈帧与调试信息丢失，这些都不报错。
:::

## 三、降级之后剩下的语义

### 3.1 类字段：`[[Define]]` 与 `[[Set]]` 之争（本机实测：没有差异）

流传很广的一条经验是「类字段降级后，继承时会触发父类的 setter」。本机实测（esbuild 0.21.5，`class Base { set x(v) {...} }` + `class Child extends Base { x = 42 }`，四个目标档 + 原生运行）：

| 目标档 | 父类 setter 是否被调用 | 结论 |
| --- | --- | --- |
| 原生 / `esnext` | 否（输出空数组） | 规范照办：类字段走 `[[Define]]` |
| `es2022` / `es2020` / `es2015` | 否（输出空数组） | **esbuild 全档位保持 define 语义** |

这条老经验在本机 esbuild 链上**不成立**——它是 Babel 的历史行为：`@babel/plugin-transform-class-properties` 在 `useDefineForClassFields: false` 或 loose 模式下会走 `[[Set]]`，从而触发父类 setter。Babel 的这条路径本机未安装、未实测，按官方文档说明登记，不作断言。

**这一节的真正教训不是「谁对」，而是「降级语义要自己验」**：同一条经验在不同工具链上结论相反，只有把探针跑一遍才知道你的构建器站在哪一边。

### 3.2 私有字段：内存翻倍，且比手写 WeakMap 更贵

`#x` 在旧引擎里没有对应物，只能存在实例之外。本机实测 20 万实例（`--format=cjs`，Node v22.22.2，取 `heapUsed`）：

| 写法 | 产物大小 | 200k 实例的 `heapUsed` |
| --- | --- | --- |
| 原生 `#x`（`target=es2022`） | 391 B | **15.11 MB** |
| 降级后的 `#x`（`target=es2015`） | 1,135 B | **29.67 MB**（+96.3%） |
| 手写 `WeakMap` 等价物（对照） | 406 B | 14.98 MB |

两个结论：降级后的私有字段**每个实例多占约一倍内存**（因为要额外维护外部映射与访问检查）；而且它比「一开始就手写 WeakMap」还贵（29.67 vs 14.98 MB）。**存量大列表、长驻对象多的场景，`#私有字段` 是降级的重点成本项**，这条在评审里远比「语法能不能降」更值得讨论。

### 3.3 `async`：能降，但调试信息与栈帧一起丢

`async/await` 在 `es2015` 上会被改写成「生成器 + 状态机 + `Promise` 调度」。功能等价，代价有三处：**栈帧变浅**（异常栈里看到的是状态机而不是你的函数调用链）、**调试断点错位**、**每次调用多一层调度开销**。这也是 `es2017` 档位比 `es2015` 便宜 6.8%（gzip 983 → 916 B）的原因：`es2017` 原生支持 `async`，不用改写。

### 3.4 可选链：能降，代价可测

同一段可选链代码编译到两个档位（本机实测）：

| 目标档 | 产物 | gzip | 产物里是否还有 `?.` |
| --- | --- | --- | --- |
| `es2015` | 421 B | 274 B | 否（已改写成嵌套判断） |
| `es2020` | 242 B | 212 B | 是 |

差价 **29.2%**（274 → 212 B）。可选链在长链表达式里降级后会产生多层嵌套三元，可读性与体积同时变差——这也是「现代单包能省三分之一」的主要来源之一。

## 四、helper 注入：多 chunk 时的隐性重复

改写后的代码需要 helper（`__awaiter`、`_defineProperty`、`__spreadValues`…）。两种注入方式：

| 方式 | 体积行为 | 适用 |
| --- | --- | --- |
| 内联（每个 chunk 各带一份） | chunk 数 × helper 体积；10 个 chunk 就是 10 份 | 单包、chunk 很少 |
| 共享 runtime（`@babel/runtime` + `transform-runtime`） | 一份共享模块，多一次请求（或进 vendor chunk） | 多入口、多路由、chunk 多 |

判据很直接：**数一下产物里同一个 helper 出现了几份**。本机做法是一条命令（见验证第 3 条），同名 helper 出现次数应等于「1 或 chunk 数」而不是「chunk 数 × 每 chunk 的 helper 数」。

## 五、怎么证明「降级前后行为一致」

不能靠读代码，只能跑探针。方法是：**同一份源码编译到两个档位，各跑一遍同一组断言，比较输出**。

```shell
# 1. 准备一个只依赖语言特性的探针（不引第三方包）
cat > /tmp/bb-sem.mjs <<'JS'
class P { #v; constructor(v){ this.#v = v } get v(){ return this.#v } }
const rows = [{ user: null }];
const out = {
  priv: new P(7).v,
  chain: rows[0]?.user?.profile?.nick ?? "none",
  spread: { ...{ a: 1 }, b: 2 },
  async: await Promise.resolve(3),
};
console.log(JSON.stringify(out));
JS

# 2. 两个档位各编译一次并运行
for t in es2015 es2022; do
  node_modules/.pnpm/@esbuild+win32-x64@0.21.5/node_modules/@esbuild/win32-x64/esbuild.exe \
    /tmp/bb-sem.mjs --bundle --target=$t --format=cjs --outfile=/tmp/bb-sem-$t.cjs
  echo -n "$t -> "; node /tmp/bb-sem-$t.cjs
done
# 期望：两行 JSON 完全一致

# 3. 数 helper 重复份数（共享 runtime 时应为 1）
grep -o '__awaiter\|_defineProperty\|__spreadValues' dist/assets/*.js | sort | uniq -c
# 期望：每个 helper 的出现次数远小于「chunk 数 × 每 chunk 出现次数」
```

第 2 步是这个专题里**最便宜的高价值检查**：它不依赖真机、不依赖浏览器，几十毫秒就能证明「降级没有改变这段代码的结果」。它证明不了性能与渲染行为，但能挡住 90% 的「降级改坏了逻辑」。

## 六、降不下去时的三条出路

| 出路 | 代价 | 什么时候选 |
| --- | --- | --- |
| 换工具（Babel / SWC / tsc） | 构建变慢、要维护两套 pipeline | 基线含 `es5` 档，且必须单包 |
| 抬基线 | 放弃一部分旧内核用户（要能说出比例） | 旧内核占比低于业务可接受线，且有数据 |
| 分流（给旧内核发另一份产物） | 双包体积与缓存成本（本机实测双包达现代线的 2.51×） | 过渡期，且能按 `module`/`nomodule` 或服务端能力协商分流 |

三条出路的量化对比在[实战：从双包迁到单包](../Practice/index.md)里算完整账，本页只给判定顺序：**先看旧内核占比，再看双包体积代价，最后才看构建时间**——构建时间是唯一可以用钱解决的。

## 本页判据


| 判据 | 约定 | 定错了会怎样 | 怎么验证 |
| --- | --- | --- | --- |
| `BBJ-A` | 产物配置必须写具体档位，禁止 `esnext` 进入生产配置 | 最新语法直发旧内核，整包不执行 | 构建配置里 `target` 为具体版本（`es20xx` 或浏览器列表） |
| `BBJ-B` | 选型阶段就确认「所选编译器能否降到基线最低档」 | 上线前才发现降不下去，返工换工具 | 有一条 `--target=<最低档>` 的成功构建记录 |
| `BBJ-C` | 逐特性探针只含该特性，避免被同文件的 `const` 抢先报错 | 得出错误结论，误判某语法不可降 | 探针文件里每个特性单独一个文件 |
| `BBJ-D` | 降级前后必须跑同一组语义探针，输出一致 | 降级改坏逻辑且无异常可查 | 两档产物跑同一探针，JSON 输出一致 |
| `BBJ-E` | 私有字段 / 大对象列表要评估降级后的实例内存 | 20 万实例堆内存翻倍（15.11 → 29.67 MB） | 有内存实测记录或明确的「不做降级」决策 |
| `BBJ-F` | 多 chunk 项目使用共享 runtime，helper 不重复内联 | 每个 chunk 各带一份 helper，体积白涨 | 产物里 helper 出现次数与 chunk 数不成正比 |
| `BBJ-G` | `async` 降级要评估栈帧与调试信息损失 | 线上异常栈全是状态机，排障困难 | 异常上报里能看到业务函数名（或已接受该损失） |
| `BBJ-H` | 基线下调（放宽）必须重跑体积与语义探针 | 体积悄悄上涨、语义悄悄改变 | 每次改 `target` 的 PR 里都有前后对比 |

## 验证方式

```shell
# 1. 确认「降不下去会硬失败」（es5 探针）
printf 'class A { #x = 1; get x(){ return this.#x } }\nexport default A;\n' > /tmp/bb-es5.js
node_modules/.pnpm/@esbuild+win32-x64@0.21.5/node_modules/@esbuild/win32-x64/esbuild.exe \
  /tmp/bb-es5.js --bundle --target=es5 --outfile=/tmp/bb-es5.out.js; echo "EXIT=$?"
# 期望：EXIT 非 0，stderr 含 "Transforming class syntax"

# 2. 复算各档位的 gzip 体积（同一份夹具）
printf 'const a={b:{c:1}};class K{#x=1;get x(){return this.#x}}\nexport const y=a?.b?.c;export default K;\n' > /tmp/bb-size.js
for t in es2015 es2017 es2020 es2022; do
  node_modules/.pnpm/@esbuild+win32-x64@0.21.5/node_modules/@esbuild/win32-x64/esbuild.exe \
    /tmp/bb-size.js --bundle --minify --target=$t --outfile=/tmp/bb-$t.js
  echo -n "$t gzip="; gzip -9 -c /tmp/bb-$t.js | wc -c
done
# 期望：es2015 最大，es2017 明显小一档，es2022 最小（本机读数 983 / 916 / 606 / 428）

# 3. 数产物里的 helper 重复份数
grep -o '__awaiter\|_defineProperty\|__spreadValues' dist/assets/*.js 2>/dev/null | sort | uniq -c
# 期望：每个 helper 的出现次数与 chunk 数不成正比

# 4. 看本页判据族定义完整
grep -c 'BBJ-[A-H]' docs/Frontend/BuildBaseline/Transpile/index.md
# 期望：≥ 8
```

## 参考资料

- [esbuild — Target 与「不支持降到 ES5」的说明](https://esbuild.github.io/api/#target)
- [Babel — `@babel/plugin-transform-class-properties` 与 `useDefineForClassFields`](https://babeljs.io/docs/babel-plugin-transform-class-properties)
- [TC39 — 类字段提案的 `[[Define]]` 语义](https://github.com/tc39/proposal-class-fields)
- [Vite — `build.target` 与 `@vitejs/plugin-legacy`](https://vite.dev/config/build-options)
- [MDN — 可选链（可选链对 `document.all` 的历史特例）](https://developer.mozilla.org/docs/Web/JavaScript/Reference/Operators/Optional_chaining)
- [本册目录页](../index.md)
