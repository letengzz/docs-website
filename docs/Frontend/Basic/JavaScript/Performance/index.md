# JavaScript 性能优化

## 性能分析工具

```javascript [performance-api.js]
// Performance API
const start = performance.now()
// 执行代码
const end = performance.now()
console.log(`耗时：${end - start}ms`)

// 标记
performance.mark('start-task')
// 执行代码
performance.mark('end-task')
performance.measure('task-duration', 'start-task', 'end-task')

const measures = performance.getEntriesByName('task-duration')
console.log(measures[0].duration)

// 资源加载
performance.getEntriesByType('resource').forEach(resource => {
  console.log(`${resource.name}: ${resource.duration}ms`)
})

// 导航信息
const navigation = performance.getEntriesByType('navigation')[0]
console.log(`DNS: ${navigation.domainLookupEnd - navigation.domainLookupStart}ms`)
console.log(`TCP: ${navigation.connectEnd - navigation.connectStart}ms`)
console.log(`DOM: ${navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart}ms`)
console.log(`Load: ${navigation.loadEventEnd - navigation.loadEventStart}ms`)
```

## 内存优化

```javascript [memory.js]
// 及时释放引用
function processData() {
  const largeArray = new Array(1000000).fill('data')
  // 处理数据
  return result
  // largeArray 自动释放
}

// 避免内存泄漏
class EventEmitter {
  constructor() {
    this.listeners = new Map()
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  off(event, callback) {
    const listeners = this.listeners.get(event)
    if (listeners) {
      this.listeners.set(event, listeners.filter(cb => cb !== callback))
    }
  }

  emit(event, data) {
    const listeners = this.listeners.get(event)
    if (listeners) {
      listeners.forEach(callback => callback(data))
    }
  }

  removeAllListeners() {
    this.listeners.clear()
  }
}

// WeakMap/WeakSet
const cache = new WeakMap()
function getData(obj) {
  if (cache.has(obj)) {
    return cache.get(obj)
  }
  const result = computeData(obj)
  cache.set(obj, result)
  return result
}

// 对象池
class ObjectPool {
  constructor(createFn, resetFn, maxSize = 100) {
    this.createFn = createFn
    this.resetFn = resetFn
    this.pool = []
    this.maxSize = maxSize
  }

  acquire() {
    if (this.pool.length > 0) {
      return this.pool.pop()
    }
    return this.createFn()
  }

  release(obj) {
    if (this.pool.length < this.maxSize) {
      this.resetFn(obj)
      this.pool.push(obj)
    }
  }
}

// 使用
const pool = new ObjectPool(
  () => ({ x: 0, y: 0 }),
  (obj) => { obj.x = 0; obj.y = 0 }
)

const obj = pool.acquire()
obj.x = 10
obj.y = 20
pool.release(obj)
```

## DOM 优化

```javascript [dom-optimization.js]
// 文档片段
function createList(items) {
  const fragment = document.createDocumentFragment()
  items.forEach(item => {
    const li = document.createElement('li')
    li.textContent = item
    fragment.appendChild(li)
  })
  document.querySelector('ul').appendChild(fragment)
}

// 批量样式修改
function updateElement(el, styles) {
  el.style.cssText = Object.entries(styles)
    .map(([key, value]) => `${key}: ${value}`)
    .join(';')
}

// 虚拟列表
class VirtualList {
  constructor(container, itemHeight, renderFn) {
    this.container = container
    this.itemHeight = itemHeight
    this.renderFn = renderFn
    this.items = []
    this.visibleCount = Math.ceil(container.clientHeight / itemHeight)
  }

  setItems(items) {
    this.items = items
    this.container.style.height = `${items.length * this.itemHeight}px`
    this.render()
  }

  render() {
    const scrollTop = this.container.scrollTop
    const startIndex = Math.floor(scrollTop / this.itemHeight)
    const endIndex = Math.min(startIndex + this.visibleCount, this.items.length)

    const visibleItems = this.items.slice(startIndex, endIndex)
    const html = visibleItems.map((item, i) => {
      const top = (startIndex + i) * this.itemHeight
      return `<div style="position:absolute;top:${top}px;height:${this.itemHeight}px">${this.renderFn(item)}</div>`
    }).join('')

    this.container.innerHTML = html
  }
}

// 防抖
function debounce(fn, delay) {
  let timer = null
  return function(...args) {
    clearTimeout(timer)
    timer = setTimeout(() => fn.apply(this, args), delay)
  }
}

// 节流
function throttle(fn, delay) {
  let lastTime = 0
  return function(...args) {
    const now = Date.now()
    if (now - lastTime >= delay) {
      fn.apply(this, args)
      lastTime = now
    }
  }
}

// 使用
window.addEventListener('resize', debounce(() => {
  console.log('窗口大小变化')
}, 300))

window.addEventListener('scroll', throttle(() => {
  console.log('滚动事件')
}, 100))
```

## 渲染优化

```javascript [render.js]
// requestAnimationFrame
function animate() {
  element.style.transform = `translateX(${x}px)`
  requestAnimationFrame(animate)
}
requestAnimationFrame(animate)

// 避免强制同步布局
function badPractice() {
  const height = element.offsetHeight  // 读取
  element.style.height = '100px'       // 写入
  const width = element.offsetWidth    // 强制同步布局
}

function goodPractice() {
  element.style.height = '100px'       // 写入
  const height = element.offsetHeight  // 读取
  const width = element.offsetWidth    // 读取
}

// 使用 transform 和 opacity
.element {
  transform: translateX(100px);  // GPU 加速
  opacity: 0.5;                  // GPU 加速
}

// will-change
.element {
  will-change: transform;  // 提示浏览器优化
}

// 图片懒加载
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target
      img.src = img.dataset.src
      observer.unobserve(img)
    }
  })
})

document.querySelectorAll('img[data-src]').forEach(img => {
  observer.observe(img)
})
```

## 算法优化

```javascript [algorithm.js]
// 缓存计算结果
function memoize(fn) {
  const cache = new Map()
  return function(...args) {
    const key = JSON.stringify(args)
    if (cache.has(key)) {
      return cache.get(key)
    }
    const result = fn.apply(this, args)
    cache.set(key, result)
    return result
  }
}

const fibonacci = memoize((n) => {
  if (n <= 1) return n
  return fibonacci(n - 1) + fibonacci(n - 2)
})

// 二分查找
function binarySearch(arr, target) {
  let left = 0
  let right = arr.length - 1

  while (left <= right) {
    const mid = Math.floor((left + right) / 2)
    if (arr[mid] === target) return mid
    if (arr[mid] < target) left = mid + 1
    else right = mid - 1
  }
  return -1
}

// 快速排序
function quickSort(arr) {
  if (arr.length <= 1) return arr
  const pivot = arr[Math.floor(arr.length / 2)]
  const left = arr.filter(x => x < pivot)
  const middle = arr.filter(x => x === pivot)
  const right = arr.filter(x => x > pivot)
  return [...quickSort(left), ...middle, ...quickSort(right)]
}

// 去重优化
function unique(arr) {
  return [...new Set(arr)]
}

// 数组扁平化
function flatten(arr, depth = Infinity) {
  return arr.flat(depth)
}
```

## 网络优化

```javascript [network.js]
// 资源预加载
<link rel="preload" href="script.js" as="script">
<link rel="prefetch" href="next-page.html">
<link rel="preconnect" href="https://api.example.com">

// 数据缓存
class DataCache {
  constructor(ttl = 300000) {  // 5 分钟
    this.cache = new Map()
    this.ttl = ttl
  }

  async fetch(url, options = {}) {
    const key = `${url}:${JSON.stringify(options)}`
    const cached = this.cache.get(key)
    
    if (cached && Date.now() - cached.timestamp < this.ttl) {
      return cached.data
    }

    const response = await fetch(url, options)
    const data = await response.json()
    
    this.cache.set(key, { data, timestamp: Date.now() })
    return data
  }

  clear() {
    this.cache.clear()
  }
}

// 请求合并
class RequestBatcher {
  constructor(delay = 100) {
    this.delay = delay
    this.queue = []
    this.timer = null
  }

  add(request) {
    return new Promise((resolve, reject) => {
      this.queue.push({ request, resolve, reject })
      
      if (!this.timer) {
        this.timer = setTimeout(() => this.flush(), this.delay)
      }
    })
  }

  async flush() {
    const batch = this.queue.splice(0)
    this.timer = null

    try {
      const results = await Promise.all(batch.map(item => fetch(item.request)))
      batch.forEach((item, i) => item.resolve(results[i]))
    } catch (error) {
      batch.forEach(item => item.reject(error))
    }
  }
}

// 分页加载
async function loadMore(page = 1, limit = 20) {
  const response = await fetch(`/api/items?page=${page}&limit=${limit}`)
  return response.json()
}

// 无限滚动
const observer = new IntersectionObserver((entries) => {
  if (entries[0].isIntersecting) {
    loadMore(currentPage++).then(items => {
      renderItems(items)
    })
  }
})

observer.observe(document.querySelector('#load-more-trigger'))
```

## 代码分割

```javascript [code-splitting.js]
// 动态导入
async function loadModule() {
  const module = await import('./heavy-module.js')
  module.init()
}

// 路由懒加载
const routes = {
  '/home': () => import('./pages/Home.js'),
  '/about': () => import('./pages/About.js'),
  '/dashboard': () => import('./pages/Dashboard.js')
}

async function navigate(path) {
  const loadPage = routes[path]
  if (loadPage) {
    const page = await loadPage()
    page.render()
  }
}

// 条件加载
if (user.isAdmin) {
  import('./admin-panel.js').then(module => {
    module.init()
  })
}

// 预加载关键资源
function preloadCriticalResources() {
  const link = document.createElement('link')
  link.rel = 'preload'
  link.href = '/critical.css'
  link.as = 'style'
  document.head.appendChild(link)
}
```

## 性能监控

```javascript [monitoring.js]
// 核心指标
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    switch (entry.name) {
      case 'first-paint':
        console.log('首次绘制:', entry.startTime)
        break
      case 'first-contentful-paint':
        console.log('首次内容绘制:', entry.startTime)
        break
      case 'largest-contentful-paint':
        console.log('最大内容绘制:', entry.startTime)
        break
    }
  }
})

observer.observe({ entryTypes: ['paint', 'largest-contentful-paint'] })

// 自定义指标
function measureFunction(fn, name) {
  return function(...args) {
    performance.mark(`${name}-start`)
    const result = fn.apply(this, args)
    performance.mark(`${name}-end`)
    performance.measure(name, `${name}-start`, `${name}-end`)
    return result
  }
}

// 错误监控
window.addEventListener('error', (e) => {
  reportError({
    type: 'js-error',
    message: e.message,
    stack: e.error?.stack,
    url: window.location.href,
    timestamp: Date.now()
  })
})

window.addEventListener('unhandledrejection', (e) => {
  reportError({
    type: 'promise-rejection',
    message: e.reason?.message,
    stack: e.reason?.stack,
    url: window.location.href,
    timestamp: Date.now()
  })
})

// 上报
function reportError(data) {
  navigator.sendBeacon('/api/error', JSON.stringify(data))
}
```

::: tip 提示
- 使用 Performance API 分析性能瓶颈
- 避免频繁 DOM 操作，使用文档片段
- 使用 requestAnimationFrame 进行动画
- 实现防抖和节流优化事件处理
- 使用缓存减少重复计算
:::
