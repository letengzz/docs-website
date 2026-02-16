# HTML 列表标签

HTML 列表是网页内容组织的重要元素。可以显示内容更加整齐有序。

- 无序列表 ul：顺序无关紧要的列表。

- 有序列表 ol：顺序有关紧要的列表。

- 描述列表 dl：标记一组项目及相关描述。

## 无序列表

无序列表在布局中非常常用。常用于一些整齐对齐的模块中使用。

- `<ul>`：定义列表的容器，只能包含 `<li>` 元素。
- `<li>`：定义列表的选项，里面可以放其他html元素。

```html
<ul>
  <li>1</li>
  <li>2</li>
  <li>3</li>
</ul>
```

## 有序列表

有序列表在布局中使用较少。了解即可，实际开发即使有顺序，一般也是用其他替代。

- `<ol>`：定义列表的容器，只能包含 `<li>` 元素。

- `<li>`：定义列表的选项，里面可以放其他html元素。

```html
<ol>
  <li>1</li>
  <li>2</li>
  <li>3</li>
</ol>
```

## 列表嵌套

列表中的某项内容，又包含一个列表。

:::danger

- 嵌套时，请务必把解构写完整。
- li 标签最好写在 ul 或 ol 中，不要单独使用。

:::

```html
<h2>我想去的几个城市</h2>
<ul>
  <li>成都</li>
  <li>
    <span>上海</span>
    <ul>
      <li>外滩</li>
      <li>杜莎夫人蜡像馆</li>
      <li>
        <a href="https://www.opg.cn/">东方明珠</a>
      </li>
      <li>迪士尼乐园</li>
    </ul>
  </li>
  <li>西安</li>
  <li>武汉</li>
</ul>
```

## 描述列表

描述列表在布局中主要是在页面底部。

- `<dl>`：定义列表的容器，只能包含 `<dt>` 和 `<dd>` 元素。
- `<dt>`：定义被描述的术语，通常显示为左对齐或加粗。一个 `<dt>` 可以对应多个 `<dd>`。
- `<dd>`：包含术语的定义或描述，通常显示为缩进形式。可以包含段落、图片、链接等其他HTML元素

```html
<dl>
  <dt>家电</dt>
  <dd>电视</dd>
  <dd>冰箱</dd>
  <dd>烟灶</dd>
</dl>
```

## 搜索框

用于搜索框的关键字提示。

```html
<input type="text" list="mydata" />
<datalist id="mydata">
  <option value="周冬雨">周冬雨</option>
  <option value="周杰伦">周杰伦</option>
  <option value="温兆伦">温兆伦</option>
  <option value="马冬梅">马冬梅</option>
</datalist>
```

## 展示

用于展示问题和答案，或对专有名词进行解释。

summary 标签写在 details 的里面，用于指定问题或专有名词。

```html
<details>
  <summary>如何走上人生巅峰？</summary>
  <p>一步一步走呗</p>
</details>
```
