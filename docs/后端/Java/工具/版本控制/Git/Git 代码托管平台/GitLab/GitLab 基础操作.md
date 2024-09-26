# GitLab 基础操作

## 常用命令

- 启动所有 gitlab 组件：

  ```sh
  gitlab-ctl start
  ```

- 停止所有 gitlab 组件：

  ```sh
  gitlab-ctl stop
  ```

- 重启所有 gitlab 组件：

  ```sh
  gitlab-ctl restart  
  ```

- 查看服务状态：

  ```sh
  gitlab-ctl status
  ```

- 启动服务：

  ```sh
  gitlab-ctl reconfigure
  ```

- 修改默认的配置文件：

  ```sh
  vi /etc/gitlab/gitlab.rb 
  ```

- 查看日志：

  ```sh
  gitlab-ctl tail
  ```

## 默认分支配置

推荐使用"初始推送后完全保护"：

![image-20240613210740789](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132107555.png)

## 创建项目

![image-20230514003813146](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140107243.png)

![image-20230514003817553](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140107096.png)

![image-20230514003821768](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140106782.png)

![image-20230514003826117](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140106428.png)

## 标记标题

**作用**：提交带有标记的议题或者合并请求的时候能够收到议题和合并请求

点击标记创建标记：

![image-20240613231324062](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132313394.png)

![image-20240613232751137](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132327061.png)

## 合并分支

点击创建合并请求：

![image-20240613215908619](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132159564.png)

或者新建合并请求并填写源分支、目标分支：

![image-20240613231527559](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132315686.png)

![image-20240613231545306](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132315395.png)

![image-20240613232111152](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132321272.png)

合并分支：

![image-20240613220003117](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132200979.png)

![image-20240613220023160](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132200931.png)

## 议题操作

当不能合并时可以添加一个议题，可以供开发者查看并解决问题：

![image-20240613233029661](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132330145.png)

议题还可以作为开发新功能和模块，能直观查看，并能创建分支：

![image-20240613233218751](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132332151.png)

## 代码查看

点击提交内容：

![image-20240614233950085](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406142339838.png)

![image-20240614234025820](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406142340679.png)

点击"仓库图"：可以查看提交情况

![image-20240614234116107](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406142341230.png)
