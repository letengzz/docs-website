# 管理发布包

## 创建与发布

可以将自己开发的工具包发布到 npm 服务上，方便自己和其他开发者使用。

**操作步骤**：

1. 创建文件夹，并创建文件 index.js

   在文件中声明函数，使用 module.exports 暴露

   npm 初始化工具包

   package.json 填写包的信息 (包的名字是唯一的)

2. 注册账号：https://www.npmjs.com/signup

3. 激活账号 ( 一定要激活账号)

4. 修改为官方的官方镜像 (命令行中运行 `nrm use npm`)

5. 命令行下 `npm login` 填写相关用户信息

6. 命令行下`npm publish` 提交包

**问题**：

![image-20231026205719680](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202310262057422.png)

**原因**：由于包名被使用

**解决办法**：package.json 换个名

## 更新包

可以对自己发布的包进行更新。

**操作步骤**：

1. 更新包中的代码

2. 测试代码是否可用

3. 修改 package.json 中的版本号

4. 发布更新

   ```shell
   npm publish
   ```

## 删除包

执行命令删除包：

```shell
npm unpublish --force
```

删除包需要满足一定的条件：https://docs.npmjs.com/policies/unpublish

- 你是包的作者
- 发布小于 24 小时
- 大于 24 小时后，没有其他包依赖，并且每周小于 300 下载量，并且只有一个维护者