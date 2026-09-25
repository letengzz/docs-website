# 运行时优化

页面加载完成后的体验由**主线程**决定：JS 执行、渲染、事件响应都在主线程排队。运行时优化围绕「减少长任务、避免布局抖动、控制内存、合理缓存」展开，直接改善 INP 与交互流畅度。

## 主线程三大敌人

![运行时优化](./../assets/runtime-optimize.svg)

| 敌人 | 影响 | 手段 |
| --- | --- | --- |
| 长任务（>50ms） | 阻塞交互 → INP 变差 | 拆分任务、异步化 |
| 强制同步布局（布局抖动） | 频繁重排 → 卡顿 | 读写分离、批量操作 |
| 内存泄漏 | 页面越用越卡 | 清理监听/定时器/缓存 |

## 1. 长任务拆分

```javascript
// Runtime/long-task.js
// 坏：一次性处理 10 万条数据，主线程卡死
function processAll(items) {
  items.forEach(item => expensiveWork(item));
}

// 好：分批处理，让出主线程
async function processInChunks(items, chunkSize = 500) {
  for (let i = 0; i < items.length; i += chunkSize) {
    const chunk = items.slice(i, i + chunkSize);
    await new Promise(r => setTimeout(r, 0));   // 让出主线程
    chunk.forEach(expensiveWork);
  }
}
```

### 用 requestIdleCallback 处理非紧急任务

```javascript
// Runtime/idle.js
// 空闲时才执行（如上报、预计算）
requestIdleCallback(() => {
  precomputeHeavyStuff();
}, { timeout: 2000 });
```

## 2. 虚拟列表

渲染 1 万行 DOM 必然卡顿；虚拟列表只渲染可见项：

```javascript
// Runtime/virtual-list.js（原理示意）
// 1. 外层容器固定高度 + overflow: auto
// 2. 内部占位层高度 = 总行数 × 行高
// 3. 滚动时只渲染视口 ± overscan 的行
// 4. 绝对定位渲染行

// 生产用现成库：vue-virtual-scroller / @tanstack/virtual
```

```html
<!-- Runtime/virtual.html -->
<div class="viewport" style="height: 500px; overflow: auto;">
  <div style="position: relative; height: 1000000px;">
    <!-- 只渲染可见的 20 行 -->
  </div>
</div>
```

## 3. 避免强制同步布局

```javascript
// Runtime/layout-thrash.js
// 坏：读-写交替强制同步布局（layout thrashing）
for (const el of elements) {
  const w = el.offsetWidth;      // 读
  el.style.width = (w - 10) + 'px';  // 写 → 下一次读强制重排
}

// 好：先统一读，再统一写
const widths = elements.map(el => el.offsetWidth);
elements.forEach((el, i) => {
  el.style.width = (widths[i] - 10) + 'px';
});
```

::: danger 高频触发重排的属性
读取 `offsetWidth` / `offsetHeight` / `getBoundingClientRect()` 等几何属性会强制同步布局；动画帧内反复读写会严重卡顿。
:::

## 4. 动画只动合成属性

```css
/* Runtime/animation.css */
.box {
  transition: transform 0.3s ease;   /* 合成层，不触发重排 */
  /* 避免 width/left/top 动画 */
}
```

详细原理见 [动画进阶](../../../Basic/CSS/Advanced/Animation/index.md)。

## 5. 防抖与节流

```javascript
// Runtime/debounce-throttle.js
function debounce(fn, delay = 300) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

function throttle(fn, interval = 200) {
  let last = 0;
  return (...args) => {
    const now = Date.now();
    if (now - last >= interval) {
      last = now;
      fn(...args);
    }
  };
}

// 输入搜索：防抖；滚动监听：节流
input.addEventListener('input', debounce(doSearch, 300));
window.addEventListener('scroll', throttle(onScroll, 200), { passive: true });
```

## 6. 计算缓存

```javascript
// Runtime/memo.js
// 幂等计算缓存结果
const cache = new Map();

function expensiveTransform(input) {
  if (cache.has(input)) return cache.get(input);
  const result = doExpensive(input);
  cache.set(input, result);
  return result;
}
```

React/Vue 侧用 `useMemo` / `computed` 避免重复计算与无效渲染。

## 7. Web Worker 移出重计算

```javascript
// Runtime/worker.js
// 主线程
const worker = new Worker('/worker.js');
worker.postMessage({ type: 'parse', data: hugeText });
worker.onmessage = (e) => renderResult(e.data);

// worker.js（独立线程）
self.onmessage = (e) => {
  if (e.data.type === 'parse') {
    const result = expensiveParse(e.data.data);
    self.postMessage(result);
  }
};
```

适合 Worker 的场景：数据解析、图像处理、加密、大数组计算；不适合：DOM 操作、频繁小任务。

## 8. 内存管理

```javascript
// Runtime/memory.js
// 清理监听器（组件卸载时）
window.addEventListener('resize', onResize);

// 组件卸载 / 页面隐藏时移除
function cleanup() {
  window.removeEventListener('resize', onResize);
  clearInterval(timerId);
  cache.clear();
}

// 大图/Blob 用完释放
URL.revokeObjectURL(objectUrl);
```

::: danger 内存泄漏常见来源
1. 未移除的事件监听器（尤其 SPA 路由切换）；
2. 全局变量/闭包持有大对象；
3. 定时器未清理；
4. `Map`/`Set` 无限增长；
5. 未 revoke 的 ObjectURL、未关闭的 IndexedDB 游标。
:::

## 易错点与最佳实践

::: danger 常见坑
1. **盲目用虚拟列表**：数据量小（<1000）时收益为零还增加复杂度。
2. **防抖节流不分**：输入用防抖、滚动用节流，反了会「粘滞」或「漏事件」。
3. **Worker 传大对象**：postMessage 结构化克隆有拷贝成本，超大对象可能更慢。
4. **`passive: false` 的滚动监听**：会阻塞滚动，能 passive 就 passive。
5. **优化前不测量**：先 Profile 定位瓶颈再动手。
:::

::: tip 最佳实践
- 用 Performance 面板录制交互，找红色长任务与「Forced reflow」警告；
- React 用 Profiler、Vue 用 DevTools 性能面板定位无效渲染；
- 建立「主线程空闲率」「INP」两个监控指标。
:::

## 验证方式

1. DevTools Performance 录制一次交互，确认无 >50ms 长任务、无强制同步布局警告；
2. 打开 Memory 面板做「快照 → 交互 → 快照」，确认无对象持续增长；
3. 用 `requestAnimationFrame` 计时验证动画帧率稳定在 60fps（无掉帧）。

## 特例：把计算搬进 WebAssembly

本页讲的是**长任务怎么切分、怎么用 Worker 调度**，让主线程不被阻塞；而 WebAssembly（Wasm）模块通常**也跑在 Worker 里**——两者的关系是**调度 vs 计算**的配合：本页负责「什么时候算、在哪个线程算」，Wasm 负责「这一次计算本身有多快」。把一个热点函数换成 Wasm 实现（如 Rust 编译产物）后，它一般仍挂在上面这套 Worker 调度里，只是每次调用的耗时变短了。

把计算搬进 Wasm 的三条纪律：

1. **把多次小调用合并成一次大数组调用**：JS 与 Wasm 之间的边界穿越有固定开销，逐元素调用（每次只传一个数）会比纯 JS 还慢。正确做法是先把数据攒成一个大数组，一次性传进去，让 Wasm 在内部循环。
2. **Wasm 内存 `grow()` 之后，旧的 TypedArray 视图会失效必须重建**：`WebAssembly.Memory.grow()` 可能触发底层 `ArrayBuffer` 重新分配（原 buffer 被 detach），此前基于 `memory.buffer` 创建的 `Int32Array` / `Float32Array` 视图会变成「长度 0」，继续读写要么抛错要么读到脏数据。每次 `grow()` 之后都要重新构造视图。
3. **处理完要调 `free`，否则每帧泄漏**：用 C/C++/Rust 导出的分配函数在 Wasm 堆里申请的内存，不会随 JS 作用域回收。每帧（每次调用）申请了就要在结束时释放，否则内存持续增长——表现就是「页面越用越慢」，与本页第 8 节讲的 JS 内存泄漏是同一类病。

```js [Runtime/wasm-worker.js]
// worker.js：在 Worker 里实例化 wasm，用 Transferable 把结果零拷贝传回主线程
let wasm; // { memory, alloc, free, processF32 }

self.onmessage = async (e) => {
  if (e.data.type === "init") {
    const { instance } = await WebAssembly.instantiateStreaming(
      fetch(e.data.url),
      {}
    );
    wasm = instance.exports;
    return;
  }

  if (e.data.type === "compute") {
    const input = new Float32Array(e.data.buffer);   // 主线程转移过来的数据
    const bytes = input.length * 4;
    const ptr = wasm.alloc(bytes);                   // ① 在 wasm 堆里申请
    new Float32Array(wasm.memory.buffer, ptr, input.length).set(input);

    const outPtr = wasm.processF32(ptr, input.length); // ② 一次大调用，内部循环

    // ③ grow() 之后 memory.buffer 可能已换，必须重新建视图
    const out = new Float32Array(wasm.memory.buffer, outPtr, input.length).slice();
    wasm.free(ptr);                                  // ④ 成对释放，避免每帧泄漏

    // ⑤ 用 Transferable 把结果零拷贝交回主线程
    self.postMessage({ type: "done", buffer: out.buffer }, [out.buffer]);
  }
};
```

::: danger 最常见的三个错
1. **逐元素穿越 JS/Wasm 边界**：调用开销大于计算本身，越「优化」越慢；攒成大数组再一次性传。
2. **`grow()` 后继续用旧视图**：视图已失效，读到空数组或抛 `TypeError`；每次 grow 后重建。
3. **只 `alloc` 不 `free`**：单次看不出，动画循环里几十帧就爆内存；申请与释放在同一作用域成对写。
:::

把 Wasm 以模块方式接入 JS 的完整写法（加载、导出、内存管理）见 [WebAssembly · JS 互操作](../../../WebAssembly/Interop/index.md)。

## 参考资料

- [web.dev：长任务](https://web.dev/articles/long-tasks)
- [web.dev：布局抖动](https://web.dev/articles/avoid-large-complex-layouts-and-layout-thrashings)
- [MDN：Web Workers](https://developer.mozilla.org/zh-CN/docs/Web/API/Web_Workers_API)
- 特例实战：[数据可视化 · 大数据量下的性能工程](../../../DataVisualization/LargeData/index.md)——十万级数据点的降采样、动画取舍与 WebGL 方案，是本页「长任务与帧率」方法论的图表场景落地；大屏内存泄漏（实例/定时器未释放）的排查见 [数据可视化 · 常见问题与最佳实践](../../../DataVisualization/FAQ/index.md)。
