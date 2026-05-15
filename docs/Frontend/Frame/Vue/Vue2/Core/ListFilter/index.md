# 列表过滤

列表过滤用于根据条件筛选数组中的数据。

## 基本用法

```html [basic-filter.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>列表过滤</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <input v-model="searchText" placeholder="搜索...">
    <ul>
      <li v-for="item in filteredList" :key="item.id">
        {{ item.name }}
      </li>
    </ul>
  </div>
</body>
<script>
  const vm = new Vue({
    data: {
      searchText: '',
      list: [
        { id: 1, name: '苹果' },
        { id: 2, name: '香蕉' },
        { id: 3, name: '橙子' },
        { id: 4, name: '葡萄' }
      ]
    },
    computed: {
      filteredList() {
        if (!this.searchText) {
          return this.list
        }
        return this.list.filter(item => 
          item.name.includes(this.searchText)
        )
      }
    },
    el: '#app'
  })
</script>
</html>
```

## 使用 watch 实现过滤

```html [watch-filter.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>列表过滤</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <input v-model="searchText" placeholder="搜索...">
    <ul>
      <li v-for="item in filteredList" :key="item.id">
        {{ item.name }}
      </li>
    </ul>
  </div>
</body>
<script>
  const vm = new Vue({
    data: {
      searchText: '',
      list: [
        { id: 1, name: '苹果' },
        { id: 2, name: '香蕉' },
        { id: 3, name: '橙子' },
        { id: 4, name: '葡萄' }
      ],
      filteredList: []
    },
    watch: {
      searchText(newVal) {
        if (!newVal) {
          this.filteredList = this.list
        } else {
          this.filteredList = this.list.filter(item =>
            item.name.includes(newVal)
          )
        }
      }
    },
    mounted() {
      this.filteredList = this.list
    },
    el: '#app'
  })
</script>
</html>
```

## 多条件过滤

```html [multi-filter.html]
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>多条件过滤</title>
  <script src="https://fastly.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="app">
    <input v-model="searchText" placeholder="搜索名称...">
    <select v-model="category">
      <option value="">全部</option>
      <option value="水果">水果</option>
      <option value="蔬菜">蔬菜</option>
    </select>
    <ul>
      <li v-for="item in filteredList" :key="item.id">
        {{ item.name }} - {{ item.category }}
      </li>
    </ul>
  </div>
</body>
<script>
  const vm = new Vue({
    data: {
      searchText: '',
      category: '',
      list: [
        { id: 1, name: '苹果', category: '水果' },
        { id: 2, name: '香蕉', category: '水果' },
        { id: 3, name: '胡萝卜', category: '蔬菜' },
        { id: 4, name: '西红柿', category: '蔬菜' }
      ]
    },
    computed: {
      filteredList() {
        let result = this.list
        if (this.searchText) {
          result = result.filter(item =>
            item.name.includes(this.searchText)
          )
        }
        if (this.category) {
          result = result.filter(item =>
            item.category === this.category
          )
        }
        return result
      }
    },
    el: '#app'
  })
</script>
</html>
```

::: tip 提示
- 推荐使用 computed 实现列表过滤
- watch 也可以实现，但代码更复杂
- 可以组合多个过滤条件
:::
