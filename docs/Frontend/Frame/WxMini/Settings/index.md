# 微信小程序 配置文件

`JSON`是一种轻量级的数据格式，常用于前后端数据的交互，但是在小程序中，`JSON` 扮演的静态配置的角色，用于配置当前页面或组件的属性和行为，每个页面或组件也都可以拥有一个对应的 json 文件。

小程序中常见的配置文件有以下几种：

1. 全局配置文件 (`app.json` )：小程序全局配置文件，用于配置小程序的一些全局属性和页面路由。
2. 局部配置文件 (`页面.json `)：小程序页面配置文件，用于配置当前页面的窗口样式、页面标题等。
3. 项目配置文件 (`project.config.json`)：小程序项目的配置文件，用于保存项目的一些配置信息和开发者的个人设置。
4. 搜索配置文件 (`sitemap.json`)：配置小程序及其页面是否允许被微信索引，提高小程序在搜索引擎搜索到的概率。

## 全局配置

小程序 `app.json` 文件是小程序的全局配置文件，用于配置小程序的一些全局属性和页面路由。

当小程序启动时，会自动读取 `app.json` 文件中的配置，根据配置生成对应的页面和组件、界面表现、网络超时时间、底部 tab，在小程序运行过程中起着关键的作用。

官方文档：https://developers.weixin.qq.com/miniprogram/dev/reference/configuration/app.html

### pages

`pages` 字段：用于指定小程序由哪些页面组成，用于为了让小程序知道由哪些页面组成以及页面定义在哪个目录，每一项都对应一个页面的 路径 (含文件名)信息。

可以通过配置小程序的页面路径快速生成小程序的页面。

官方文档：https://developers.weixin.qq.com/miniprogram/dev/reference/configuration/app.html#pages

:::danger 注意

1. 文件名不需要写文件后缀框架会自动去寻找对应位置的 `.json`, `.js`, `.wxml`, `.wxss` 四个文件进行处理。
2. 小程序中新增/减少页面，都需要对 pages 数组进行修改。
3. 未指定 `entryPagePath` 时，数组的第一项代表小程序的初始页面 (首页)。

:::

```json
{
  "pages": ["pages/index/index", "pages/list/list"]
}
```

### window

`window`字段： 用于设置小程序的状态栏、导航条、标题、窗口背景色。

官方文档：https://developers.weixin.qq.com/miniprogram/dev/reference/configuration/app.html#window

<img src="./assets/window%E9%85%8D%E7%BD%AE%E9%A1%B9.png" style="zoom:60%;" />

|             属性             |                     描述                      |   类型   |  默认值  |
| :--------------------------: | :-------------------------------------------: | :------: | :------: |
| navigationBarBackgroundColor |                导航栏背景颜色                 | HexColor | \#000000 |
|    navigationBarTextStyle    |   导航栏标题颜色，仅支持 `black` / `white`    |  string  |  white   |
|    navigationBarTitleText    |              导航栏标题文字内容               |  string  |          |
|       backgroundColor        | 下拉 loading 的样式，仅支持 `dark` / `light`  |  string  |   dark   |
|    enablePullDownRefresh     |            是否开启全局的下拉刷新             | boolean  |  false   |
|    onReachBottomDistance     | 页面上拉触底事件触发时距页面底部距离单位为 px |  number  |    50    |

按照下图来配置 `window`：

![image-20250813214753096](assets/image-20250813214753096.png)

```json
{
  "window": {
    "backgroundTextStyle": "light",
    "backgroundColor": "#eee",
    "navigationBarBackgroundColor": "#f3514f",
    "navigationBarTitleText": "微信小程序",
    "navigationBarTextStyle": "white",
    "enablePullDownRefresh": true
  }
}
```

### tabBar

`tabBar` 字段：定义小程序顶部、底部 `tab` 栏，如果小程序是一个多 tab 应用，例如：可以在客户端窗口的底部或顶部通过 tab 栏可以切换页面，可以通过 tabBar 配置项指定 tab 栏的表现，以及 tab 切换时显示的对应页面。

官方文档：https://developers.weixin.qq.com/miniprogram/dev/reference/configuration/app.html#tabBar

:::danger 注意

1. list 是一个数组，**只能配置最少 2 个、最多 5 个 tab**。
2. 当 `position` 为 `top` 时，不显示 icon。

:::

![image-20250813214911399](assets/image-20250813214911399.png)

**`tabBar` 配置项**：

|      属性       |                            描述                            |   类型   | 默认值 |
| :-------------: | :--------------------------------------------------------: | :------: | :----: |
|      color      |          tab 上的文字默认颜色，仅支持十六进制颜色          | HexColor |        |
|  selectedColor  |        tab 上的文字选中时的颜色，仅支持十六进制颜色        | HexColor |        |
| backgroundColor |              tab 的背景色，仅支持十六进制颜色              | HexColor |        |
|   borderStyle   |       tabbar 上边框的颜色， 仅支持 `black` / `white`       |  string  | black  |
|      list       | tab 的列表，详见 `list` 属性说明，最少 2 个、最多 5 个 tab |          |        |
|    position     |           tabBar 的位置，仅支持 `bottom` / `top`           |  string  | bottom |

**List 配置项**：list 是一个数组，**只能配置最少 2 个、最多 5 个 tab**，tab 按数组的顺序排序，每个项都是一个对象。

|       属性       |                                          描述                                           |  类型  | 是否必填 |
| :--------------: | :-------------------------------------------------------------------------------------: | :----: | :------: |
|     pagePath     |                             页面路径，必须在 pages 中先定义                             | string |    是    |
|       text       |                                     tab 上按钮文字                                      | string |    是    |
|     iconPath     |             图片路径，icon 大小限制为 40kb，<br />建议尺寸为 81px \* 81px，             | string |    是    |
| selectedIconPath | 选中时的图片路径，icon 大小限制为 40kb，<br />建议尺寸为 81px \* 81px，不支持网络图片。 | string |    是    |

按照下图来配置 `tabBar`：

<img src="./assets/image-20250813235438402.png" alt="image-20250813235438402" style="zoom:70%;" />

```json
{
  "tabBar": {
    "color": "#252933",
    "selectedColor": "#FF734C",
    "backgroundColor": "#ffffff",
    "borderStyle": "black",
    "list": [
      {
        "text": "首页",
        "iconPath": "./assets/tabbar/home.png",
        "selectedIconPath": "/./assets/tabbar/home-active.png",
        "pagePath": "pages/home/home"
      },
      {
        "text": "列表",
        "iconPath": "./assets/tabbar/list.png",
        "selectedIconPath": "/./assets/tabbar/list-active.png",
        "pagePath": "pages/list/list"
      },
      {
        "text": "购物车",
        "iconPath": "./assets/tabbar/cart.png",
        "selectedIconPath": "/./assets/tabbar/cart-active.png",
        "pagePath": "pages/cart/cart"
      },
      {
        "text": "我的",
        "iconPath": "./assets/tabbar/my.png",
        "selectedIconPath": "/./assets/tabbar/my-active.png",
        "pagePath": "pages/my/my"
      }
    ]
  }
}
```

## 页面配置

小程序的页面配置，也称局部配置，每一个小程序页面也可以使用自己的 .json 文件来对本页面的窗口表现进行配置。

:::danger 注意

页面配置文件的属性和 全局配置文件(`app.json`)中的 window 属性几乎一致，但这里不需要额外指定 `window` 字段。

:::

只不过这里不需要额外指定 window 字段，因此如果出现相同的配置项，页面中配置项 会覆盖全局配置文件中相同的配置项。

官方文档：https://developers.weixin.qq.com/miniprogram/dev/reference/configuration/page.html

|             属性             |                     描述                      |   类型   |  默认值  |
| :--------------------------: | :-------------------------------------------: | :------: | :------: |
| navigationBarBackgroundColor |                导航栏背景颜色                 | HexColor | \#000000 |
|    navigationBarTextStyle    |   导航栏标题颜色，仅支持 `black` / `white`    |  string  |  white   |
|    navigationBarTitleText    |              导航栏标题文字内容               |  string  |          |
|       backgroundColor        | 下拉 loading 的样式，仅支持 `dark` / `light`  |  string  |   dark   |
|    enablePullDownRefresh     |            是否开启全局的下拉刷新             | boolean  |  false   |
|    onReachBottomDistance     | 页面上拉触底事件触发时距页面底部距离单位为 px |  number  |    50    |

<img src="./assets/%E5%95%86%E5%93%81%E5%88%86%E7%B1%BB.png" style="zoom: 67%; border: 1px solid rgb(204, 204, 204);" />

```json
{
  "usingComponents": {},
  "navigationBarTitleText": "商品分类",
  "navigationBarTextStyle": "white",
  "navigationBarBackgroundColor": "#00AF92",
  "enablePullDownRefresh": true,
  "backgroundColor": "#eee",
  "backgroundTextStyle": "light"
}
```

## 项目配置文件

通常在使用一个工具的时候，都会针对各自喜好做一些个性化配置，例如 编译配置等等，当换了另外一台电脑重新安装工具的时候，还要重新配置。

考虑到这点，小程序开发者工具在每个项目的根目录都会生成一个 `project.config.json`，在工具上做的任何配置都会写入到这个文件，当重新安装工具或者换电脑工作时，只要载入同一个项目的代码包，开发者工具就自动会恢复到当时开发项目时的个性化配置，其中会包括编辑器的颜色、代码上传时自动压缩等等一系列选项。

官方文档：https://developers.weixin.qq.com/miniprogram/dev/devtools/projectconfig.html

<img src="./assets/%E9%A1%B9%E7%9B%AE%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6.png" style="zoom:67%;" />

项目根目录中的`project.config.json`和`project.private.config.json` 文件都可以对项目进行配置：

- `project.config.json`：项目配置文件，常用于配置公共的配置。
- `project.private.config.json`：项目私有的配置，常用于配置个人配置。

`project.private.config.json`中的相同设置优先级高于`project.config.json`。

:::danger 注意

1. project.private.config.json 写到 .gitignore 避免版本管理的冲突。

2. 与最终编译结果有关的设置 必须 设置到 project.config.json 中。

:::

可以在微信开发者工具，点击以下两个配置选项进行相关的设置，然后观察两个文件的变化即可。

<img src="./assets/%E6%B5%8B%E8%AF%95%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6.png" style="zoom:60%;" />

## 支持使用 sass/less

小程序代码包要求代码文件为 wxml / wxss / js / json / wxs。

如果希望使用 sass 或 less 去开发小程序，就需要将 sass / less 文件编译成对应的 wxss 文件。

在 `project.config.json` 文件中，修改 `setting` 下的 `useCompilerPlugins` 字段为 `["sass"]`，即可开启工具内置的 sass 编译插件。 如需同时开启 typescript 编译插件，可将该字段修改为 ["typescript ", "sass"]。 目前支持三个编译插件：typescript、less、sass。

官方文档：https://developers.weixin.qq.com/miniprogram/dev/devtools/compilets.html

```json
{
  "setting": {
    "useCompilerPlugins": [  // [!code highlight]
      "sass"  // [!code highlight]
    ]  // [!code highlight]
  }
}
```

配置好以后，需要将 `.wxss` 改成 `.scss`。

:::danger 注意

在配置的时候，编译插件的名称是 sass，但是文件的后缀名是 .scss。

这是因为 Sass 是 Css 预处理语言，scss 是 Sass 的一个语法版本。

:::

## 自定义导航栏

小程序默认的导航栏与 APP 一样都位于顶部固定位置。但是默认导航栏可能会影响小程序整体风格，且无法满足特定的设计需求，这时候，就需要进行自定义导航栏。

<img src="./assets/%E8%87%AA%E5%AE%9A%E4%B9%89%20TabBar.png" style="zoom:60%;" />

在 app.json 或者 page.json 中，**配置 navigationStyle 属性为 custom**，即可实现自定义导航栏。

在设置以后，就会移除默认的导航栏，只保留右上角胶囊按钮：

```json
{
  "usingComponents": {},
  "navigationStyle": "custom"
}
```

```html
<!--pages/cate/cate.wxml-->
<!-- <text>pages/cate/cate.wxml</text> -->

<swiper class="custom-swiper" indicator-dots autoplay interval="2000">
  <swiper-item>
    <image src="../../assets/banner/banner-1.png" mode=""/>
  </swiper-item>

  <swiper-item>
    <image src="../../assets/banner/banner-2.png" mode=""/>
  </swiper-item>

  <swiper-item>
    <image src="../../assets/banner/banner-3.png" mode=""/>
  </swiper-item>
</swiper>
```

```js
/* pages/cate/cate.wxss */

.custom-swiper {
  height: 440rpx;
}

.custom-swiper image {
  height: 100%;
  width: 100%;
}

```

## sitemap.json

微信现已开放小程序内搜索，当开发者允许微信索引时，微信会通过爬虫的形式，为小程序的页面内容建立索引。当用户的搜索词条触发该索引时，小程序的页面将可能展示在搜索结果中。

可以通过 `sitemap.json` 配置，或者管理后台页面收录开关来配置其小程序页面是否允许微信索引。

:::danger 注意

1. 没有 sitemap.json 则默认所有页面都能被索引。
2. sitemap.json 文件中默认的设置，是优先级最低的默认规则，所有页面都会被微信索引。

:::

语法：

```json
{
  "rules": [
    {
      "action": "allow",
      "page": "*"
    }
  ]
}
```

常用配置项：

|  属性  |        属性说明         |           属性值           |
| :----: | :---------------------: | :------------------------: |
| action |     是否允许被搜索      | 可选项有：allow 、disallow |
|  page  | 允许/不允许被搜索的页面 |     页面路径或者通配符     |

```json
// 所有页面都会被微信索引（默认情况）
{
  "rules": [
    {
      "action": "allow",
      "page": "*"
    }
  ]
}
```

```json
// 配置 path/to/page 页面不被索引，其余页面允许被索引
{
  "rules": [
    {
      "action": "disallow",
      "page": "path/to/page"
    }
  ]
}
```
