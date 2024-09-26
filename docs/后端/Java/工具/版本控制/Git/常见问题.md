# Git 常见问题

## SSH 公钥错误

![image-20230514005537921](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140114775.png)

Git远程仓库的SSH免密公钥和推送用户提供的公钥不一致导致的。

## Windows与Linux换行符问题

在hello.html文件中，LF将被替换为CRLF。在工作目录中，文件将使用原始的行结束符。LF为Linux下的换行符，而CRLF为Windows下的换行符。由于文件创建于Linux下，保存在Windows中，所以文件的行结束符使用的是Windows下的CRLF。

**例**：

1. 在Linux 下创建一个文件：hello.html

   ![image-20230817140203460](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202308171402617.png)

2. 保存到Window并提交会提示：`warning: LF will be replaced by CRLF in hello.html.`

   ![image-20230817140258013](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202308171402114.png)

