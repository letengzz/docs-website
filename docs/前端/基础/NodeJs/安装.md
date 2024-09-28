# Node.js 安装

## Windows 安装

打开 [Node.js官网](http://nodejs.org) 下载Node.js

- Node.js 官网：http://nodejs.org
- Node.js 中文站下载：http://nodejs.cn/download
- Node.js 历史版本：https://registry.npmmirror.com/binary.html?path=node

**注意**：

- LTS：长期支持版本
- Current：最新版

![image-20231003174023008](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310031740169.png)

也可以通过 https://nodejs.org/en/download 下载

![image-20231003174224837](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310031742716.png)

下载完毕后，双击安装Node.js

![image-20231003174749883](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310031747421.png)

![image-20231003174802617](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310031750726.png)

![image-20231003174846696](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310031750751.png)

![image-20231003174923260](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310031750138.png)

![image-20231003175006696](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310031750612.png)

![image-20231003175014065](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310031750199.png)

安装成功：

![image-20231003175041766](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310031750100.png)

配置依赖库 (`node_global`)：

- 创建node_global目录：

  ![image-20240507134716318](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202405071347227.png)

- 设置依赖库：

  ```shell
  npm config set prefix "D:\ProGram\nodejs\node_global"
  ```

  ![image-20240507134811833](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202405071348208.png)

- 查看设置成功：

  ```shell
  npm config get prefix
  ```

  ![image-20240507134824849](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202405071348657.png)

- 设置环境变量：

  ![image-20240507135338168](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202405071353541.png)

配置缓存 (`node_cache`)：

- 创建node_cache目录：

  ![image-20240507134929846](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202405071349320.png)

- 设置依赖库：

  ```shell
  npm config set cache "D:\ProGram\nodejs\node_cache"
  ```

  ![image-20240507135116077](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202405071351160.png)

- 查看设置成功：

  ```shell
  npm config get cache
  ```

  ![image-20240507135133580](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202405071351017.png)

验证：

Win+R 输入cmd，在cmd中输入 `node -v`

```bash
node -v
```

![image-20231003175215400](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310031752181.png)

## Mac 安装

打开 [Node.js官网](http://nodejs.org) 下载Node.js

- Node.js 官网：http://nodejs.org
- Node.js 中文站下载：http://nodejs.cn/download
- Node.js 历史版本：https://registry.npmmirror.com/binary.html?path=node

**注意**：

- LTS：长期支持版本
- Current：最新版

![image-20240206175117731](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/imgimage-20240206175117731.png)

也可以通过 https://nodejs.org/en/download 下载

![image-20240206175357575](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/imgimgimage-20240206175357575.png)

下载完毕后，双击安装Node.js

![image-20240206175416170](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/imgimage-20240206175416170.png)

![image-20240206175445639](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/imgimage-20240206175445639.png)

![image-20240206175513631](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/imgimage-20240206175513631.png)

安装成功：

![image-20240206175548048](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/imgimage-20240206175548048.png)

环境配置：打开Mac 终端，配置全局环境变量，键盘输入 `vim .bash_profile`进入编辑状态，打开之后添加一行代码：`PATH=$PATH:/usr/local/bin/`。点击 esc 退出编辑状态，此时无法对内容进行修改。键盘输入 `:wq!` 强制保存并退出vim，回到终端的界面

验证：

在Mac 终端，键盘输入 `node -v`验证安装成功：

```bash
node -v
```

![image-20240206180351876](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/imgimage-20240206180351876.png)

## 简单使用

安装完成后，新建一个js文件并输入：

```js
console.log('hello Node.js');
```

![image-20231003181424364](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310031814817.png)

在CMD中输入：

```bash
node 文件名.js
```

![image-20231003181537604](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310031816614.png)

## 注意

1. Node.js 中不能使用 BOM 和 DOM 的API (Node.js 并没有包含BOM 和 DOM)

   ![image-20231003181746154](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310031818515.png)

   ![image-20231003181816993](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202310031818303.png)

   ```js
   //测试 以下命令 程序会报异常
   //BOM
   console.log(window);
   console.log(history);
   console.log(navigator);
   console.log(location);
   //DOM
   console.log(document);
   //AJAX
   let xhr = new XMLHttpRequest();
   ```

   ```js
   //测试 以下命令 程序不会报异常 正常输出
   console.log('1');
   
   setTimeout(() =>{
       console.log('love')
   },1000);
   ```

2. Node.js  的顶级对象并不是window对象 而是 global对象，也可以用globalThis 访问顶级对象

   ```js
   console.log(global);
   console.log(globalThis); 
   console.log(global == globalThis);//ES2020引入的新特性 用globalThis指向顶级对象 Node.js支持此特性
   ```

   