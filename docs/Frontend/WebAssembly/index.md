# WebAssembly

<p style="text-align:center;"><img src="./assets/webassembly-logo.png" style="zoom:75%;" /></p>

**WebAssembly**（缩写 **Wasm**）是一种可移植、体积小、加载快、能在安全沙箱里运行的**二进制指令格式**。它一头把 C/C++、Rust、Go 这些非 JavaScript 语言编译成 `.wasm` 带进浏览器，让计算密集型代码以接近原生的速度跑起来；另一头用 Wasmtime、wazero 这类运行时把同一份 `.wasm` 带出浏览器，跑在服务端、边缘节点和插件沙箱里。

一句话记住本专题的定位：**把非 JS 代码带进浏览器，把 Wasm 带出浏览器**。

参考基线（截至 2026-09 核对）：W3C **WebAssembly 2.0 规范**已在 2025 年底发布，2026 年主流浏览器已完整实现；工具链以 **Emscripten 4.x** 与 Rust **wasm-bindgen** 为主线。

## 页面导航

1. [概述与场景](Overview/index.md) —— Wasm 是什么、四类真正跑得通的场景、2.0 规范能力速览
2. [编译工具链](Toolchain/index.md) —— Emscripten / Rust / TinyGo / AssemblyScript 四条路线与体积优化
3. [与 JavaScript 互操作](Interop/index.md) —— 线性内存、传值三条路线、字符串互传与内存泄漏
4. [性能对比与实测](Performance/index.md) —— 四类负载结论、基准测试纪律与「热点占比 × 加速倍数」决策算法
5. [WASI 与服务端运行时](WASI/index.md) —— 能力型安全模型、组件模型与 WIT、运行时对照
6. [实战：图像处理加速](Practice/index.md) —— 用 C 写灰度 + 3×3 卷积滤波器，端到端加速图片处理
7. [常见问题与排错](FAQ/index.md) —— 12 个高频问题，从 MIME 类型到「什么时候该放弃 Wasm」

## 建议的阅读顺序

- 只想知道**值不值得引入**：先看 [概述与场景](Overview/index.md) 的「不适合的场景与判据」，再看 [性能对比与实测](Performance/index.md) 的决策算法。
- 准备**动手编译**：直接进 [编译工具链](Toolchain/index.md)，然后回来读 [与 JavaScript 互操作](Interop/index.md)。
- 打算**上服务端**：可以跳过浏览器互操作部分，直接读 [WASI 与服务端运行时](WASI/index.md)。

## 本专题与相邻专题的分工

- [前端性能优化](../Others/PerformanceOptimization/index.md)：负责**工程级性能**——加载、渲染、包体积、缓存、Core Web Vitals 与性能预算；本专题只负责**算法级加速**，即某个热点函数改用 Wasm 重写后究竟快多少。两者的度量口径与优化手段不重叠。
- [前端性能优化 · 运行时优化](../Others/PerformanceOptimization/Runtime/index.md)：负责长任务切分、渲染帧调度、内存与 GC 压力治理；本专题的 Wasm 模块同样会被丢进 Worker 执行，但讲的是「怎么把计算搬进 Wasm」，不是「怎么调度主线程任务」。
- [云原生](../../Ops/CloudNative/index.md)：负责容器、镜像、编排与集群治理；本专题只在 [WASI 与服务端运行时](WASI/index.md) 里讨论「比容器更轻的隔离」这一种替代关系，不涉及集群层面的任何话题。
- [Serverless](../../Ops/CloudNative/Serverless/index.md)：负责函数计算的触发、伸缩与计费模型；Wasm 组件可以作为毫秒级冷启动的运行时载体接进函数计算，但函数计算的工程体系仍归它讲。
- [浏览器渲染原理](../Basic/Browser/Rendering/index.md)：负责渲染管线与合成；Wasm 不参与排版与绘制，只是被主线程或 Worker 调用的一段计算。

## 本专题讲什么、不讲什么

| 会讲 | 不讲（去对应专题） |
| --- | --- |
| `.wasm` 怎么编译、怎么压体积 | 前端包体积与代码分割策略 → [前端性能优化](../Others/PerformanceOptimization/index.md) |
| 线性内存、传值与字符串互操作 | 长任务切分、渲染帧调度 → [运行时优化](../Others/PerformanceOptimization/Runtime/index.md) |
| 「热点占比 × 加速倍数」的收益判断 | Core Web Vitals 指标与性能预算 → [前端性能优化](../Others/PerformanceOptimization/index.md) |
| WASI、组件模型与服务端运行时 | 容器编排、镜像治理 → [云原生](../../Ops/CloudNative/index.md) |
| 把 Wasm 组件当函数计算载体 | 函数计算的触发、伸缩与计费 → [Serverless](../../Ops/CloudNative/Serverless/index.md) |
| 客户端数据库引擎（如 SQLite）的编译 | 数据库设计与运维 → [数据库](../../DB/index.md) |

## 版本基线

- **规范**：W3C WebAssembly 2.0 规范 2025 年底发布，2026 年主流浏览器完整实现。
- **浏览器**：Safari 侧异常处理在 18.4 落地、JavaScript String Builtins 在 26.2 落地，并新增 JIT-less Wasm 与原地解释器。
- **工具链**：Emscripten 4.x（WebGPU 后端自 4.0.10+ 改用 `--use-port=emdawnwebgpu`）；Rust 侧 `wasm-bindgen` + `wasm-pack`。
- **服务端**：WASI 0.2 为当前稳定线，0.3 于 2026-06 发布，1.0 目标 2026 年末至 2027 年初。

以上均标注「截至 2026-09 核对」；涉及具体版本行为的细节**按官方文档，建议本地验证**。

## 参考资料

1. WebAssembly 官网：<https://webassembly.org/>
2. WebAssembly 规范（W3C / GitHub）：<https://webassembly.github.io/spec/core/>
3. MDN WebAssembly 指南：<https://developer.mozilla.org/zh-CN/docs/WebAssembly>
4. Emscripten 官方文档：<https://emscripten.org/docs/>
5. WASI 官网：<https://wasi.dev/>
6. Bytecode Alliance（Wasmtime 与组件模型）：<https://bytecodealliance.org/>
