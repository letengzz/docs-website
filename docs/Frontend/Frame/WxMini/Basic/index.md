# 微信小程序 基础

## 微信小程序账号注册

小程序开发与网页开发不一样，在开始微信小程序开发之前，需要访问 [微信公众平台](https://mp.weixin.qq.com/)，注册一个微信小程序账号。

在拥有了小程序的账号以后可以开发和管理小程序，后续可以通过该账号进行开发信息的设置、成员的添加，也可以用该账号查看、运营小程序的相关数据。

:::warning 在申请账号前，需要先准备一个邮箱，该邮箱要求：

1. 未被微信公众平台注册。
2. 未被微信开放平台注册。

3. 未被个人微信号绑定过 (如果被绑定了需要解绑或使用其他邮箱)。

:::

操作流程：

1. 打开 [微信公众平台](https://mp.weixin.qq.com/)，点击立即注册：

   <img src="./assets/02-%E7%AB%8B%E5%8D%B3%E6%B3%A8%E5%86%8C.png" style="zoom:60%; border: 1px solid #ccc" />

2. 选择注册的帐号类型，在这里需要 **选择小程序**：

   <img src="./assets/03-%E9%80%89%E6%8B%A9%E7%B1%BB%E5%9E%8B.png" style="zoom:63%; border: 1px solid #ccc" />

3. 输入账号信息：

   <img src="./assets/04-%E8%B4%A6%E5%8F%B7%E4%BF%A1%E6%81%AF.png" style="zoom:60%; border: 1px solid #ccc" />

4. 邮箱激活，需要进入邮箱进行激活：

   <img src="./assets/05-%E9%82%AE%E7%AE%B1%E6%BF%80%E6%B4%BB.png" style="zoom:60%;  border: 1px solid #ccc" />

   <img src="./assets/06-%E8%B4%A6%E5%8F%B7%E6%BF%80%E6%B4%BB.png" style="zoom:43%; border: 1px solid #ccc" />

5. 信息登记，注册类型 (需要选择中国大陆和个人，企业其他需要资质认证)：

   <img src="./assets/07-%E4%BF%A1%E6%81%AF%E7%99%BB%E8%AE%B0.png" style="zoom:51%; border: 1px solid #ccc" />

6. 主体信息登记与确认：

   :::danger 注意

    在进行管理员身份验证的时候，推荐使用自已的微信进行扫码，将自已设置为小程序账号的管理员，方便以后对小程序进行开发、成员等相关的设置。

   :::

   <img src="./assets/08-%E4%B8%BB%E4%BD%93%E4%BF%A1%E6%81%AF%E7%99%BB%E8%AE%B0.png" style="zoom:52%; border: 1px solid #ccc" />

   <img src="./assets/08-%E4%B8%BB%E4%BD%93%E4%BF%A1%E6%81%AF%E7%99%BB%E8%AE%B0-%E7%A1%AE%E8%AE%A4.png" style="zoom:54%; border: 1px solid #ccc" />

7. 小程序注册完成，点击前往小程序，即可进入小程序后台：

   <img src="./assets/09-%E6%B3%A8%E5%86%8C%E5%AE%8C%E6%88%90.png" style="zoom:54%; border: 1px solid #ccc" />

   <img src="./assets/10-%E5%B0%8F%E7%A8%8B%E5%BA%8F%E5%90%8E%E5%8F%B0.png" style="zoom:46.5%; border: 1px solid #ccc" />

## 完善小程序账号信息

在完成小程序账号的注册后，便可以打开微信公众平台对小程序账号进行一些设置，这是开发前的准备工作，完善后才可以进入后续的开发步骤，这是因为小程序在后续进行提交审核的时候，小程序账号信息是必填项，因此在注册小程序以后，需要补充小程序的基本信息，如名称、图标、描述等。

:::danger 注意

在填写小程序类目时**不要选择游戏类型**，否则微信官方将会视为小游戏开发。

:::

<img src="./assets/11-%E5%AE%8C%E5%96%84%E5%B0%8F%E7%A8%8B%E5%BA%8F%E4%BF%A1%E6%81%AF.png" style="zoom:60%; border: 1px solid #ccc" />

点击 **前往填写**，填写小程序基本信息即可：

<img src="./assets/12-%E5%A1%AB%E5%86%99%E5%B0%8F%E7%A8%8B%E5%BA%8F%E4%BF%A1%E6%81%AF.png" style="zoom:75%; border: 1px solid #ccc" />

点击 **前往设置** , 设置小程序类目信息：

1. 点击右上角添加类目：

   <img src="./assets/13-%E6%B7%BB%E5%8A%A0%E7%B1%BB%E7%9B%AE.png"  style="zoom:68%; border: 1px solid #ccc" />

2. 管理员授权：

   <img src="./assets/14-%E7%AE%A1%E7%90%86%E5%91%98%E9%AA%8C%E8%AF%81.png" style="zoom:63%; border: 1px solid #ccc" />

3. 手机微信进行认证：

<img src="./assets/015-%E8%B5%84%E8%B4%A8%E4%BD%BF%E7%94%A8%E7%A1%AE%E8%AE%A4.png" style="zoom:20%; border: 1px solid #ccc" />

4. 添加小程序类目：

   :::danger 注意

   选择类目的时候不要选择小游戏类目。
   
   :::
   
   <img src="./assets/018-%E7%B1%BB%E7%9B%AE%E9%80%89%E6%8B%A9%E6%B3%A8%E6%84%8F%E4%BA%8B%E9%A1%B9.png"  style="zoom:80%; border: 1px solid #ccc" />
   
   <img src="./assets/017-%E7%B1%BB%E7%9B%AE%E9%80%89%E6%8B%A9%E6%B3%A8%E6%84%8F%E4%BA%8B%E9%A1%B9.png" style="zoom:80%; border: 1px solid #ccc" />

## 小程序开发者 ID

小程序的开发者账号是免费的，只要开发者满足开发资质就可以免费注册，并且会获得对应的开发者 ID。

一个完整的开发者 ID 由 <font color="red">小程序 ID（AppID）</font>和一个 <font color="red">小程序密钥（AppSecret）</font>组成。

**小程序 ID 即 AppId** 是小程序在整个微信账号体系内的唯一身份凭证，后续在很多地方都会用到，例如：新建小程序项目、真机调试、发布小程序等操作时，必须有小程序 ID。

小程序密钥 是开发者对小程序拥有所有权的凭证，在进行 微信登录、微信支付，或进行发送消息等高级操作时会使用到。

在微信公众后台，单击左侧开发标签，选择 "开发管理"，在新的页面中点击 "开发设置"，就可以看到开发者 ID 信息。请妥善保管你的小程序 ID 和小程序密钥，在后续的开发中会经常使用到，获取位置见下图：

<img src="./assets/019-%E5%BC%80%E5%8F%91%E7%AE%A1%E7%90%86.png" style="zoom:80%;" />

## 开发成员和体验成员

小程序提供了两种不同的成员角色：**项目成员** 和 **体验成员**

- **项目成员**：参与小程序开发、运营的成员，可登陆小程序管理后台，包括运营者、开发者及数据分析者。管理员可在“成员管理”中添加、删除项目成员，并设置项目成员的角色。

- **体验成员**：参与小程序内测体验的成员，可使用体验版小程序，但不属于项目成员。管理员及项目成员均可添加、删除体验成员。

<img src="./assets/%E6%88%90%E5%91%98%E7%AE%A1%E7%90%86.jpg" style="zoom:80%; border: 1px solid #ccc" />

<img src="./assets/%E6%B7%BB%E5%8A%A0%E6%88%90%E5%91%98.jpg" style="zoom:80%; border: 1px solid #ccc" />

## 微信开发者工具

为了帮助开发者简单和高效地开发和调试微信小程序，微信官方提供了 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)，利用开发者工具可以很方便地进行小程序开发、代码查看以及编辑、预览和发布等功能。

在 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html) 下载页面，可以看到微信开发者工具包含三个版本：

1. 稳定版：稳定性高，**开发中一般推荐使用稳定版本**

2. 预发布版：稳定性尚可，一般包含新的、大的特性，通过了内部测试

3. 开发版：稳定性差，主要用于尽快修复缺陷和敏捷上线小的特性，如果想体验新特性，可以使用这个版本

<img src="./assets/020-%E5%BE%AE%E4%BF%A1%E5%BC%80%E5%8F%91%E8%80%85%E5%B7%A5%E5%85%B7%E7%89%88%E6%9C%AC.png" style="zoom:70%; border: 1px solid #ccc" />

选择合适的版本进行下载，在下载完成后，双击下载好的微信开发者工具安装包，根据引导点击下一步、我接受、直至安装完成。第一次使用微信开发者工具的时候，需要使用手机微信扫码登录，登录成功即可进入项目选择界面。

:::danger 注意

微信开发者工具必须联网使用。

:::

<img src="./assets/021-%E6%89%AB%E7%A0%81%E7%99%BB%E5%BD%95.png" style="zoom:67%; border: 1px solid #cccc" />

<img src="./assets/023-%E5%B0%8F%E7%A8%8B%E5%BA%8F%E7%99%BB%E5%BD%95%E6%88%90%E5%8A%9F.png" style="zoom:70%; border: 1px solid #ccc" />

## 创建小程序项目

使用小程序开发者工具创建一个新的项目：

1. 打开微信开发者工具，左侧选择小程序，点击 + 号即可新建项目：

   <img src="./assets/024-%E5%88%9B%E5%BB%BA%E9%A1%B9%E7%9B%AE.png" style="zoom:60%; border: 1px solid #ccc" />

2. 在弹出的新页面，填写项目信息：

   - 项目名称：输入项目名称。
   - 目录：选择小程序开发文件夹 (小程序的目录建议是空目录，否则官方会有提示)。
   - AppID：填写自己申请的小程序 AppID。
   - 开发模式：选择小程序。
   - 后端服务：选择不使用云服务。
   - 模板选择：选择不使用模板。

   <img src="./assets/025-%E5%88%9B%E5%BB%BA%E9%A1%B9%E7%9B%AE.png" style="zoom:70%; border: 1px solid #ccc" />

   <img src="./assets/026-%E7%9B%AE%E5%BD%95%E4%B8%8D%E4%B8%BA%E7%A9%BA.png" style="zoom:70%; border: 1px solid #ccc" />

3. 点击确定，如果能够看到小程序的开发主界面，说明小程序项目已经创建成功：

   <img src="./assets/027-%E7%AC%AC%E4%B8%80%E4%B8%AA%E5%B0%8F%E7%A8%8B%E5%BA%8F%E9%A1%B9%E7%9B%AE.png" style="zoom:60%; border-right: 1px solid #ccc" />

## 开发者工具设置

为了后续高效的对小程序项目进行开发，需要对微信开发者工具进行一些个性化的设置，例如：设置模拟器位置、编辑器主题、编辑区行高等，当然可以继续使用官方默认的，也可以按照自己的喜好设置。

设置步骤：

1. 将小程序模拟器移动右侧：点击菜单栏的"视图-外观-将模拟器移到右侧"，小程序模拟器即可调整到右侧：

   <img src="./assets/028-%E6%A8%A1%E6%8B%9F%E5%99%A8%E4%BD%8D%E7%BD%AE.png" style="zoom:80%; border: 1px solid #ccc" />

   <img src="./assets/029-%E6%A8%A1%E6%8B%9F%E5%99%A8%E4%BD%8D%E7%BD%AE.png" style="zoom:80%; border: 1px solid #ccc" />

2. 小程序主题设置，点击菜单栏的 "设置-外观设置 " 在弹框中将主题和调试工具选择为深色：

   <img src="./assets/030-%E4%B8%BB%E9%A2%98%E8%AE%BE%E7%BD%AE.png" style="zoom:80%; border: 1px solid #ccc" />

   <img src="./assets/031-%E4%B8%BB%E9%A2%98%E8%AE%BE%E7%BD%AE.png" style="zoom:80%; border: 1px solid #ccc" />

3. 编辑区的设置，点击菜单栏的 "设置-编辑器设置" 按照自己的洗好调整行距和字号，或者其他设置：

   <img src="./assets/032-%E7%BC%96%E8%BE%91%E5%99%A8%E8%AE%BE%E7%BD%AE.png" style="zoom:80%; border: 1px solid #ccc" />

## 小程序目录结构和文件介绍

在将小程序项目创建好以后，小程序项目的目录结构：

<img src="./assets/033-%E5%B0%8F%E7%A8%8B%E5%BA%8F%E7%9B%AE%E5%BD%95.png" style="zoom:80%; border: 1px solid #ccc" />

一个完整的小程序项目分为两个部分：**主体文件**、**页面文件**

**主体文件** 又称小程序全局文件，顾名思义，全局文件能够作用于整个小程序，影响到小程序的每个页面，且**主体文件必须放到项目的根目录下**，主要由三部分组成：

|  文件名  |       作用       | 是否必须 |
| :------: | :--------------: | :------: |
|  app.js  |  小程序入口文件  |   必须   |
| app.json | 小程序的全局配置 |   必须   |
| app.wxss | 小程序的全局样式 |  非必须  |

**页面文件** 是每个页面所需的文件，小程序页面文件都存放在 pages 目录下，一个页面一个文件夹，每个页面通常由四个文件组成，每个文件只对当前页面有效：

| 文件名 |   作用   | 是否必须 |
| :----: | :------: | :------: |
|  .js   | 页面逻辑 |   必须   |
| .wxml  | 页面结构 |   必须   |
| .wxss  | 页面样式 |  非必须  |
| .json  | 页面配置 |  非必须  |

:::danger 注意

页面文件，wxss、json 文件能够覆盖主体文件中的样式和配置。

:::

:::danger 强烈建议

页面文件夹名称和页面文件名称要保持一致。

:::

新建小程序文件和文件夹作用清单：

```shell
├─pages	                     ➡ 小程序页面存放目录
│
│  ├─index				     ➡ index 文件夹代表是 index 页面所需的文件
│  │      index.js           ➡ index 页面逻辑
│  │      index.json         ➡ index 页面配置
│  │      index.wxml         ➡ index 页面结构
│  │      index.wxss         ➡ index 页面样式
│  .eslintrc.js              ➡ Eslint 配置文件
│  app.js                    ➡ 小程序入口，即打开小程序首页执行的项目
│  app.json                  ➡ 小程序的全局配置
│  app.wxss                  ➡ 小程序的全局样式
│  project.config.json       ➡ 小程序开发者工具配置
│  project.private.config.json
│  sitemap.json              ➡ 小程序搜索优化

```

## 调试小程序

在进行项目开发的时候，不可避免的需要进行调试：

:::danger 注意

微信开发者工具缓存非常严重，如果发现代码和预期不一样，先点击编译。

编译后还是没有达到预期的效果，就需要清除缓存，甚至重启项目才可以。

:::

<img src="./assets/%E8%B0%83%E8%AF%95%E9%9D%A2%E6%9D%BF.png" style="zoom:70%; border: 1px solid  #ccc"/>

<img src="./assets/%E5%B7%A5%E5%85%B7%E6%A0%8F.png" style="zoom:61%; border: 1px solid  #ccc"/>

## 新建页面

**第一种方式：**

1. 在 pages 目录上 点击右键"新建文件夹"，输入页面目录的名称，例如：list。

2. 在 list 目录上 点击右键点击 page，输入页面文件的名称，例如：list。

:::danger 注意

1. 在输入页面文件名称的时候，不要输入后缀名。
2. 新建页面成功以后，会在 app.json 的 pages 选项中新增页面路径。

:::

**第二种方式：**

在 app.json 的 pages 选项中，新增页面路径即可。

在新增页面目录以后，会自动在 pages 目录下生成页面文件。

## 调试基础库

小程序调试基础库是指 微信开发者工具中可以选择的微信基础库版本。

微信基础库是指小程序的运行环境，给小程序提供了运行所需的各种 API 和工具，以及基础框架和运行逻辑等。

小程序开发者可以在微信开发者工具中选择所需的微信基础库版本，作为运行和调试小程序时的运行环境。

每个小程序有自己所允许使用的基础库最低版本要求，开发者需要选择要兼容的基础库版本，从而确保小程序的功能正常运行。

<img src="./assets/%E8%B0%83%E8%AF%95%E5%9F%BA%E7%A1%80%E5%BA%93.png" style="zoom:80%; border: 1px solid  #ccc"/>
