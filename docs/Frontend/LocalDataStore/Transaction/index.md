# 事务：一次提交写几条

IndexedDB 的事务和你在服务端认识的不太一样。它没有 `BEGIN`、没有隔离级别的选择、不能手动 `COMMIT`——**它在你创建之后自动就开始了**，在「所有请求完成且事件循环回到浏览器」时**自动提交**。这个设计带来的两个后果，构成了本地库最贵的一类 bug：提交粒度决定吞吐，而「自动提交」会让一段看起来同步的代码**悄悄断成两半**。

本页两个读数：批量与逐条差 **6.6 倍**，事务里 `await` 会让第二次写抛 `TransactionInactiveError` 且**不落盘**。

![逐条事务与单事务批量的耗时对比，以及事务内 await 导致自动提交](../assets/lds-tx.svg)

本页判据族 `TXN-A` ~ `TXN-H`，共 8 条。定义表在第六节。

## 一、提交粒度：167.2 ms 与 1,098.2 ms

2,000 条记录（每条约 230 字节），两种写法：

```js
// A. 逐条事务：2,000 次「开始 → 写 1 条 → 提交」
for (let i = 0; i < 2000; i++) {
  await tx(db, 'items', 'readwrite', s => s.put(rec(i)));
}
// 1,098.2 ms → 0.549 ms/条

// B. 单事务批量：1 次「开始 → 写 2,000 条 → 提交」
await tx(db, 'items', 'readwrite', s => {
  for (let i = 0; i < 2000; i++) s.put(rec(i));
});
// 167.2 ms → 0.084 ms/条
```

**6.6 倍**。差距不在「写」上，在**提交**上：每次提交都要把这次事务的改动落一次日志并刷盘，2,000 次提交就是 2,000 次刷盘。

| 粒度 | 2,000 条耗时 | 单条均摊 | 适合 |
| --- | --- | --- | --- |
| 逐条事务 | 1,098.2 ms | 0.549 ms | 需要「每条独立成败」（如逐条导入并给用户逐条报错） |
| 单事务批量 | 167.2 ms | 0.084 ms | 绝大多数场景 |

::: tip 批量的上限在哪
批量不是越大越好。事务越大，**它持锁的时间越长**，其他标签页的写会被排队；而且一次 `QuotaExceededError` 会让整批失败。实践值是 **500~2,000 条一批**：既能摊薄提交成本，又能在失败时只损失一批。
:::

## 二、自动提交：`await` 是那条分界线

下面这段代码，很多人以为是「一个事务写两条」：

```js
const tx = db.transaction('items', 'readwrite');
const store = tx.objectStore('items');

store.put({ id: 9001, title: 'a' });        // ① 成功
await fetch('/api/lock');                   // ② 控制权回到浏览器 → 事务可能在此提交
store.put({ id: 9002, title: 'b' });        // ③ TransactionInactiveError
```

本机实测结果：

| 观察点 | 结果 |
| --- | --- |
| 第 3 步 | 抛 `TransactionInactiveError` |
| `id = 9002` 是否落盘 | **`missing`（没写进去）** |
| `id = 9001` 是否落盘 | 写进去了 |

这就是最危险的一类缺陷：**①成功了、③抛错了、②中间那条不存在的记录没人知道**。如果这段代码在 `try/catch` 里，错误会被当成「临时失败」重试，于是 9001 被写两次、9002 永远缺失。

规范只有一条：

> **事务里不允许出现任何非 IDB 的 `await`。**

需要先拿外部数据（token、锁、配置），就把它拿到事务外面：

```js
const token = await fetchToken();            // 先在事务外 await
await tx(db, 'items', 'readwrite', s => {    // 再开事务，里面全是同步调用
  s.put({ id: 9001, token });
  s.put({ id: 9002, token });
});
```

同理，`Promise.all` 里包多个 `put` 再 `await` 也是错的——`put` 本身返回的是 `IDBRequest`（有 `onsuccess`，不是 thenable），把它 `await` 掉在某些封装里会等到微任务队列，同样可能让事务失活。

## 三、abort：回滚是真的，而且很便宜

```js
await new Promise(r => {
  const tx = db.transaction('items', 'readwrite');
  const s = tx.objectStore('items');
  for (let i = 0; i < 500; i++) s.put(rec(20000 + i));   // 先写 500 条
  s.put(rec(1));                                         // 再故意写一条已存在的
  tx.abort();                                            // 立刻中止
  tx.onabort = r; tx.oncomplete = r;
});
```

实测：`count()` 前后都是 **4,001**——500 条 `put` 全部回滚，**18.9 ms** 完成中止。

两个结论：

1. **abort 是廉价且彻底的**，可以放心用它做「整批校验失败就全部不要」；
2. 但 `abort` 与「某一条 request 失败」不是一回事，见下一节。

## 四、两种错误：请求级失败 vs 事务级中止

| 层面 | 怎么观察 | 典型原因 | 会不会回滚 |
| --- | --- | --- | --- |
| **请求级** | 单个 `IDBRequest` 的 `onerror` | `ConstraintError`（unique 冲突）、`DataError`（键不合法）、`QuotaExceededError` | 默认**会**冒泡到事务并触发 abort |
| **事务级** | `transaction.onabort` / `onerror` | 上面任一请求未 `preventDefault()`、显式 `abort()`、升级失败 | 全部回滚 |

想让「单条失败、其余照写」，必须在请求的 `onerror` 里 `event.preventDefault()`：

```js
const req = store.put(row);
req.onerror = ev => {
  ev.preventDefault();        // 阻止冒泡到事务
  ev.stopPropagation();
  failed.push({ row, err: req.error.name });
};
```

::: danger `preventDefault()` 不是一个「宽容模式」开关
它只阻止**中止**，不阻止**这条数据没写进去**。用了它以后，你必须自己记录失败清单并在业务上处理——否则就是「静默丢数据」。判据：每一处 `preventDefault()` 都要能指向一个 `failed` 数组和它的后续逻辑。
:::

## 五、跨仓库：一个事务，还是两个

```js
// 同时写订单与它的 outbox 事件
const tx = db.transaction(['orders', 'outbox'], 'readwrite');
tx.objectStore('orders').put(order);
tx.objectStore('outbox').put({ type: 'order.created', payload: order.id });
// 两个仓库一起提交，要么都成，要么都不成
```

`db.transaction([...])` 里的仓库列表决定了**作用域**：不在列表里的仓库，`tx.objectStore(name)` 抛 `NotFoundError`。这条规则常被误读成「事务只能用一个仓库」，其实它可以横跨任意多个仓库——这是本地库唯一的多表原子性来源。

反过来，**两个事务之间没有原子性**。所以「先写业务表、再开一个事务写队列」在崩溃点上会留下「有业务数据、没有事件」的不一致——这才是离线场景里最难查的一类问题。

## 六、并发：读读并行，写写排队

| 场景 | 行为 |
| --- | --- |
| 多个 `readonly` 事务 | **可并行** |
| 一个 `readwrite` 与任何其他事务（同仓库） | **串行**，后到的等前一个结束 |
| 不同仓库的 `readwrite` | 可并行 |
| 事务创建后长时间不发请求 | 事件循环一空就自动提交，随后再用即 `TransactionInactiveError` |

所以「用事务做锁」在本地库是可行的（同一个仓库的 `readwrite` 天然互斥），但**不能跨页面/跨标签页**——多标签页之间只有 `BroadcastChannel` 或 Web Locks 能协调。

## 七、本页判据

| 编号 | 判据 | 看什么现象 | 不满足时改哪里 |
| --- | --- | --- | --- |
| `TXN-A` | 批量写走单事务 | 写入路径上事务创建次数 ≤ 批数而非条数 | 改成单事务循环 `put` |
| `TXN-B` | 单事务批大小在 500~2,000 | 代码里有常量且有注释说明 | 加常量 |
| `TXN-C` | 事务内无非 IDB 的 `await` | 逐行检查 `db.transaction` 与 `oncomplete` 之间 | 把 await 提到事务外 |
| `TXN-D` | 需要外部数据时先取再开事务 | 事务开始前已有 token / 配置 | 调整顺序 |
| `TXN-E` | 跨仓库写入在同一个事务里 | `db.transaction([a, b])` 出现在写路径 | 合并事务 |
| `TXN-F` | 每处 `preventDefault()` 都有失败清单 | `failed.push` 与后续处理存在 | 补失败处理 |
| `TXN-G` | 有 abort 后的用户可见反馈 | abort 分支里有提示或重试 | 补反馈 |
| `TXN-H` | 多标签页写协调有方案 | 存在 `BroadcastChannel` / Web Locks | 补协调 |

## 验证方式

三个验证，都能在控制台直接跑：

```js
(async () => {
  // ① 批量 vs 逐条
  const db = await new Promise((res, rej) => {
    const r = indexedDB.open('txlab', 1);
    r.onupgradeneeded = e => e.target.result.createObjectStore('i', { keyPath: 'id' });
    r.onsuccess = e => res(e.target.result); r.onerror = () => rej(r.error);
  });
  const one = () => new Promise(r => { const t = db.transaction('i', 'readwrite'); t.objectStore('i').put({ id: Math.random() }); t.oncomplete = r; });
  let t = performance.now();
  for (let i = 0; i < 500; i++) await one();
  console.log('per-record', (performance.now() - t).toFixed(1), 'ms');

  t = performance.now();
  await new Promise(r => {
    const tx = db.transaction('i', 'readwrite'), s = tx.objectStore('i');
    for (let i = 0; i < 500; i++) s.put({ id: Math.random() });
    tx.oncomplete = r;
  });
  console.log('batch', (performance.now() - t).toFixed(1), 'ms');

  // ② 事务里的 await
  try {
    await new Promise((res, rej) => {
      const tx = db.transaction('i', 'readwrite'), s = tx.objectStore('i');
      s.put({ id: 'after-await' });
      setTimeout(() => { try { s.put({ id: 'second' }); res(); } catch (e) { rej(e.name); } }, 0);
    });
  } catch (e) { console.log('expect error:', e); }   // TransactionInactiveError
})();
```

预期：`batch` 明显小于 `per-record`（本机 6.6 倍）；第 ② 段打出 `TransactionInactiveError`。

## 参考资料

- W3C：*Indexed Database API 3.0*（事务的 `active` / `inactive` 状态、自动提交时机、`onabort` 与 `preventDefault`）
- MDN：*IDBTransaction*（`mode`、`objectStoreNames`、`commit()` 在新版浏览器中的语义）
- MDN：*Using IndexedDB*（事务生命周期与 promise 封装的注意事项）
- 本仓库：[索引](../IndexDesign/index.md)、[PWA 离线数据](../../PWA/OfflineData/index.md)、[幂等与状态机](../../../Backend/IdempotencyStateMachine/index.md)
