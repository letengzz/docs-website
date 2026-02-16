# HTML 表单

表单是用于收集用户输入数据，并将数据提交到后端进行处理。

场景：

- 用户登录/注册。
- 搜索框。
- 联系表单。
- 问卷调查。
- 订单支付。
- 文件上传。
- ...

表单的核心标签有三部分组成：

- 表单容器：`<form>`：定义表单的容器，包裹所有表单控件。默认包含action属性。

- 表单控件：包含`<input>`通用输入控件、`<textarea>`多行文本输入框、`<select>`下拉选择框、`<button>`自定义按钮等。

- 辅助标签：`<label>`关联输入控件的文本标签，提升可访问性 (点击标签可聚焦输入框)更好的提高表单的用户体验。

## 表单容器

使用 form 标签定义表单的容器，包裹所有表单控件。

属性：

- action 属性：定义了在提交表单时，应该把所收集的数据送给谁(URL)去处理。

- target ：用于控制表单提交后，如何打开页面。常用值：

  - \_`self`：在本窗口打开。

  - `_blank`：在新窗口打开。

- method ：用于控制表单的提交方式，值： get 、 post。

```html
<form action="https://www.baidu.com/s" target="_blank" method="get">
  <input type="text" name="wd" />
  <button>去百度搜索</button>
</form>
```

## 表单控件

- input 表单：通用输入控件，包含输入框、单选框、复选框等。
- textarea 表单：多行文本输入框。
- select 下拉表单：下拉选择框。
- button 按钮：自定义按钮。

### 通用输入控件

通用输入控件，包含输入框、单选框、复选框等。

输入标签`<input>`是最常用的表单元素之一，它可以创建文本输入框、密码框、单选框、复选框等。

属性：

- type 属性：定义了输入框的类型。
- name ：用于指定提交数据的名字 (需要与后端人员沟通后确定)。
- value 属性：

  - 对于输入框，指定默认输入的值。
  - 对于单选和复选框，实际提交的数据。
  - 对于按钮，显示按钮文字。

- disabled 属性： 设置表单控件不可用。
- maxlength 属性： 用于输入框，设置最大可输入长度。
- checked 属性： 用于单选按钮和复选框，默认选中。

```html
<input type="text" />
```

#### 文本输入框

常用属性：

- name 属性：数据的名称。
- value 属性：输入框的默认输入值。
- maxlength 属性：输入框最大可输入长度。
- placeholder 属性：提示信息。
- accesskey 属性：使元素获得焦点的快捷键 (Windows：Alt + 设置的快捷键、MacOS：Control + Option + 设置的快捷键)。
- autocomplete 属性：用于控制表单的自动填充行为，帮助浏览器决定是否根据用户历史输入自动填充字段值，取值 on / off。

```html
<input type="text" />
```

#### 密码输入框

常用属性：

- name 属性：数据的名称。
- value 属性：输入框的默认输入值 (一般不用，无意义)。
- maxlength 属性：输入框最大可输入长度。
- placeholder 属性：提示信息。
- accesskey 属性：使元素获得焦点的快捷键 (Windows：Alt + 设置的快捷键、MacOS：Control + Option + 设置的快捷键)。
- autocomplete 属性：用于控制表单的自动填充行为，帮助浏览器决定是否根据用户历史输入自动填充字段值，取值 on / off。

```html
<input type="password" />
```

#### 单选框

常用属性：

- name 属性：数据的名称实现分组。

  :::danger

  想要单选效果，多个radio 的 name 属性值要保持一致。

  :::

- value 属性：提交的数据值。

- checked 属性：让该单选按钮默认选中。

```html
<input type="radio" name="sex" value="female" />女 <input type="radio" name="sex" value="male" />男
```

#### 复选框

常用属性：

- name 属性：数据的名称实现分组。

  :::danger

  想要单选效果，多个radio 的 name 属性值要保持一致。

  :::

- value 属性：提交的数据值。

- checked 属性：让该复选框默认选中。

```html
<input type="checkbox" name="hobby" value="smoke" />抽烟
<input type="checkbox" name="hobby" value="drink" />喝酒
<input type="checkbox" name="hobby" value="perm" />烫头
```

#### 隐藏域

用户不可见的一个输入区域，作用是： 提交表单的时候，携带一些固定的数据。

- name 属性：指定数据的名称。
- value 属性：指定的是真正提交的数据。

```html
<input type="hidden" name="tag" value="100" />
```

#### 文件域

常用属性：

- multiple属性：允许选择多个文件。
- accept属性：规定选择的文件类型，多个类型中间用逗号分隔。

```html
<input type="file" accept=".mp4,.flv,.avi,.wmv,.mov" multiple="multiple" style="display:none;" />
```

### 多行文本控件

`<textarea>` 是一个多行纯文本编辑控件，适用于允许用户输入大量自由格式文本的场景，例如评论或反馈表单。textarea 多行文本框也称为文本域。

常见属性：

- name 属性：表单名称。
- placeholder 属性：提示信息。
- rows 属性： 指定默认显示的行数 (文本行数)，影响文本域的高度。正整数，默认为2。
- cols 属性：指定默认显示的列数 (文本列数)，影响文本域的宽度。正整数，默认20。
- disabled 属性： 设置表单控件不可用。

:::danger

不能编写type 属性，其他属性，与普通文本输入框一致。

:::

```html
<textarea name="msg" rows="22" cols="3">我是文本域</textarea>
```

文本域textarea利用CSS来设定样式，比如宽高边框等。

### 下拉框控件

`<select>` 元素表示一个提供选项菜单的控件。

`<select>` 元素是容器， `<option>`是每一个选项标签，每个选项要跟一个值要想默认选中一个选项，可以添加 selected 属性。

`<select>` 常见属性：

- name 属性： 指定数据名称。
- disabled 属性： 设置整个下拉框不可用。

因为select很难修改为好看的效果，大部分下拉列表可以通过其他标签模拟实现。

`<option>` 常见属性：

- value 属性：该选项事件提交的数据。option 标签设置value 属性， 如果没有value 属性，提交的数据是option 中间的文字；如果设置了value 属性，提交的数据就是value 的值 (建议设置 value 属性)。
- selected 属性：表示默认选中。
- disabled 属性： 设置拉下选项不可用。

```html
<select name="" id="">
  <option value="北京">北京</option>
  <option value="深圳">深圳</option>
  <option value="上海">上海</option>
  <option value="广州">广州</option>
</select>
```

### 按钮控件

`<button>` 标签定义一个按钮。元素内部可以放置内容，比如文本或图像。

常见属性：

- disabled 属性： 设置按钮不可用，禁用按钮，无法点击。
- type 属性： 设置按钮的类型，值： submit (默认)、 reset 、 button。

#### 提交按钮

:::danger

1. button 标签 type 属性的默认值是 submit 。
2. button 不要指定name 属性。
3. input 标签编写的按钮，使用value 属性指定按钮文字。

:::

```html
<input type="submit" value="点我提交表单" /> <button>点我提交表单</button>
```

#### 重置按钮

:::danger

1. button 不要指定name 属性。
2. input 标签编写的按钮，使用value 属性指定按钮文字。

:::

```html
<input type="reset" value="点我重置" /> <button type="reset">点我重置</button>
```

#### 普通按钮

:::danger

普通按钮的type 值为button ，若不写type 值是submit 会引起表单的提交。

:::

```html
<input type="button" value="普通按钮" /> <button type="button">普通按钮</button>
```

## 禁用表单控件

给表单控件的标签设置 disabled 既可禁用表单控件。

input 、 textarea 、 button 、 select 、 option 都可以设置 disabled 属性

## 表单控件分组

fieldset 可以为表单控件分组、 legend 标签是分组的标题。

```html
<fieldset>
  <legend>主要信息</legend>
  <label for="zhanghu">账户：</label>
  <input id="zhanghu" type="text" name="account" maxlength="10" /><br />
  <label
    >密码：
    <input id="mima" type="password" name="pwd" maxlength="6" />
  </label>
  <br />
  性别：
  <input type="radio" name="gender" value="male" id="nan" />
  <label for="nan">男</label>
  <label> <input type="radio" name="gender" value="female" id="nv" />女 </label>
</fieldset>
```

## 辅助标签

label 标签可与表单控件相关联，关联之后点击文字，与之对应的表单控件就会获取焦点，表示用户界面中某个元素的说明，提升可访问性 (点击标签可聚焦输入框)。

常见属性：

- for 属性： 值与要关联的表单控件的ID值相同。

两种与 label 关联方式：

1. 让 label 标签的 for 属性的值等于表单控件的 id 。
2. 把表单控件套在 label 标签的里面。

使用方式：

- 利用for和id相关联：

  ```html
  <label for="nan"> 男 </label> <input type="radio" id="nan" name="sex" />
  ```

- 直接包含：

  ```html
  <label>
    男
    <input type="radio" name="sex" />
  </label>
  ```
