# Jenkins集群/并发构建

集群化构建可以有效提升构建效率，尤其是团队项目比较多或是子项目比较多的时候，可以并发在多台机器上执行构建。

创建两个Jenkins服务，并创建节点：

![image-20240404193400402](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404042012703.png)
![image-20240404193626902](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404042012953.png)

![image-20240404194551048](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404042012114.png)

使用相同方式创建jenkins-03：

![image-20240404194819671](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404042012662.png)

## 调整并发执行个数

![image-20240404195244299](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404042012633.png)

## 并发构建

配置：

![image-20240404195053604](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404042012960.png)

效果：

![image-20240404195149195](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404042012221.png)

## 指定节点构建

配置：

![image-20240404195643354](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404042012768.png)

![image-20240404195921190](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404042013227.png)

常见语法：

![image-20240404195658370](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404042012185.png)

