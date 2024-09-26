# GitLab 团队操作

去到一家公司，应该是已经有了GitLab平台，运维人员拥有root管理员账号。而作为一名普通的开发人员，你的leader和同事都拥有各自的GitLab账号和不同权限。入职后，你只需要申请开通GitLab账号和对应权限，不需要你来操作。

## 创建用户

假设数据组的leader账号为leader01，你是hjc

点击管理中心-用户-新用户：

![image-20240613133743468](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406131337523.png)

创建一个leader的账号：

![image-20240613221040128](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132210482.png)

再申请一个hjc账号：

![image-20240613134159618](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406131342014.png)

用户会收到重置密码的邮件，也可以由管理员设置：

![image-20240613134316069](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406131343633.png)

![image-20240613134400924](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406131344343.png)

## 创建群组

在GitLab里，可以创建出组、组下的子组。在小公司里可以看见GitLab里边会创建出后端，大数据等等一系列组。尽量不要使用中文创建组名，可以在组信息中的备注编写中文描述以及中文组名，组内人员名称也尽量用全拼命名。

对于人员权限以及角色的控制也比较简单，有如下五种：

- Owner：最高权限，谁去创建组，这个组就被谁拥有，它可以开除管理员，但管理员无法操作owner的角色。

- Maintainer：（管理员-只是具备sudo权限的用户）管理员一般是给小组的组长，或者是给产品线的总监设定。

- Developer：是干活的人，就是写代码的程序员，可以进行代码的上传以及代码的下载，不能下载其他的组内的代码，只能下载它们组的代码。

- Repoter：比如现在有需求，其他组的大牛到我们组过来指导工作，要审视我们的代码，人家就提出需要一个权限，我不能给它developer因为它会改你代码，其他组的人不能改我们组的代码，所以就给一个repoter权限，他只能看，只读权限。

- guest：不用看，匿名，直接去掉。一般出现在从ldap中把离职人员的信息删掉，再去gitlab查这个人的时候，它就是一个guest用户（匿名）需要再到gitlab把它删掉（不删也没事）。


假设研发部群组是rdc，下属后端组、前端组、大数据组等子群组：

![1img](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406131347314.jpg) 

创建研发中心群组rdc：

![image-20240613134944564](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406131349212.png)

 ![image-20240613135050321](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406131350690.png)

创建大数据组：

在研发中心组下，再创建一个大数据组 (当然，其他还会有后端组、前端组等)：

![image-20240613135205154](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406131352897.png) 

![image-20240613135821194](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406131358480.png) 

当然，根据公司情况还可以进一步在数据组下面细分子组（比如：离线、实时、湖等），这里就不再细分。

将数据组的leader设为bigdata的负责人：

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406131359269.png) 

将hjc添加为普通的开发人员：

![image-20240613140055251](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406131400880.png) 

现在就有一个顶级群组rdc，其下有一个子群组bigdata，组内有管理员leader01，开发人员hjc。