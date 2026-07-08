# Windows 安装

## WSL 安装

### 开启虚拟化

![image.png](assets/img202408031605845.png)

### 安装wsl2

Windows10使用：https://learn.microsoft.com/zh-cn/windows/wsl/install-manual

```shell
wsl --install

#有可能连不上网络，需要更新github hosts
```

![image-20240803161348066](assets/img202408031613832.png)

## 安装 Docker Desktop

下载地址：https://docs.docker.com/desktop/install/windows-install/

## 配置镜像

Docker Desktop默认去 hub.docker.com 去下载软件镜像，需要配置国内源：

```shell
{
  "registry-mirrors": [
  	"https://iuyisnhp.mirror.aliyuncs.com",
    "https://mirror.ccs.tencentyun.com",
    "http://hub-mirror.c.163.com"
  ]
}
```

![image-20240803170120713](assets/img202408031701981.png)

## 使用操作

可以使用cmd命令行来进行Docker命令操作，也可以使用可视化界面来操作。

![image-20240803170457063](assets/img202408031704721.png)

![image-20240803170521667](assets/img202408031705406.png)
