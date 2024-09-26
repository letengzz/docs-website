# 使用VMWare安装CentOS7

## 安装CentOS 7

整个安装过程分两大步，第一步装机器，第二步装系统.

**第一步: 装机器**

检查物理机虚拟化支持是否开启，需要进入到BIOS中设置，因各种电脑型号进入BIOS方式不同，同学们自行查找对应品牌电脑如何进入BIOS

建议: 先安装，如果安装中提示虚拟化未开启，再进入BIOS设置，如安装一切顺序，则不需要进行任何设置。

可以在任务管理器查看是否开启虚拟化

![image-20240724134241545](images/VM安装Linux/image-20240724134241545.png)在VMware中新建虚拟机

![image-20240724134428079](images/VM安装Linux/image-20240724134428079.png)

默认即可,不需要做任何修改，直接下一步

![image-20240724134814350](images/VM安装Linux/image-20240724134814350.png)

选择稍后安装操作系统，然后下一步

![image-20240724134820717](images/VM安装Linux/image-20240724134820717.png)

选择安装的操作系统为Linux,版本为CentOS7 64位

![image-20240724134826291](images/VM安装Linux/image-20240724134826291.png)

虚拟机命名，可随意取， 安装位置最好选择固态硬盘(有固态的情况..)，快的飞起

![image-20240724134832366](images/VM安装Linux/image-20240724134832366.png)

按照物理机CPU实际情况，选择处理器配置, 处理器数量\*每个处理器内存数量要小于等于物理机CPU的数量，否则报错.

查看物理机CPU数量:

![image-20240724135016066](images/VM安装Linux/image-20240724135016066.png)

选择虚拟机CPU配置

![image-20240724135024386](images/VM安装Linux/image-20240724135024386.png)

选择分配给虚拟机的内存，最少2G

![image-20240724135031272](images/VM安装Linux/image-20240724135031272.png)

网络类型选择NAT

![image-20240724135041812](images/VM安装Linux/image-20240724135041812.png)

I/O控制器类型选择默认推荐即可，同学们无须纠结不同处，不重要。

![image-20240724135046327](images/VM安装Linux/image-20240724135046327.png)

磁盘类型选择SCSI， 同学们无须纠结不同处，不重要。

![image-20240724135052272](images/VM安装Linux/image-20240724135052272.png)

IDE: 老的磁盘类型

SCSI: 服务器上推荐使用的磁盘类型，串口。

SATA: 也是串口，也是新的磁盘类型。

选择创建新虚拟磁盘

![image-20240724135100641](images/VM安装Linux/image-20240724135100641.png)

磁盘容量指定20G（或50GB），选择将虚拟磁盘拆分成多个文件. 不要勾选立即分配所有磁盘空间,否则会直接占用20G(或50GB)大小的磁盘空间。

![image-20240724135106008](images/VM安装Linux/image-20240724135106008.png)

选择Linux文件的存储位置，建议选择到Linux的安装位置，存储到先前创建的目录下

![image-20240724135112737](images/VM安装Linux/image-20240724135112737.png)

至此，装机器完成。 点击完成即可。如果想更改配置，可点击自定义硬件。对之前步骤的选择进行更改。

![image-20240724135148406](images/VM安装Linux/image-20240724135148406.png)

**第二步 装系统**

选择系统盘位置

![image-20240724135156678](images/VM安装Linux/image-20240724135156678.png)

加电，开启虚拟机

![image-20240724135201397](images/VM安装Linux/image-20240724135201397.png)

进入倒计时,鼠标点进去, 键盘上下键可以选择，选择Install CentOS 7 ，然后回车即可.

不要选择Test this media & install CentOS 7, 然后就没有然后了......

> TIPS: Ctrl+Alt可以实现Windows主机和VM之间窗口的切换

![image-20240724135229036](images/VM安装Linux/image-20240724135229036.png)

选择简体中文

![image-20240724135308932](images/VM安装Linux/image-20240724135308932.png)

设置日期和时间 选择亚洲/上海

![image-20240724135314008](images/VM安装Linux/image-20240724135314008.png)

设置软件选择 GNOME桌面,

> TIPS：第一次安装建议选择GNOME桌面，实际以后真实服务器中不会带桌面,都是最小化安装，进入系统就是Shell界面，全部通过命令操作。 等学习完Linux命令，能使用命令熟练操作Linux后，可选择最小安装.

![image-20240724135327054](images/VM安装Linux/image-20240724135327054.png)

![image-20240724135336929](images/VM安装Linux/image-20240724135336929.png)

设置安装位置,即进行分区。（可选）

![image-20240724135343329](images/VM安装Linux/image-20240724135343329.png)

选择我要配置分区,然后点左上角完成进入分区界面

![image-20240724135407890](images/VM安装Linux/image-20240724135407890.png)

第一个分区: /boot 引导分区,建议给1G

![image-20240724135426780](images/VM安装Linux/image-20240724135426780.png)

修改设备类型为标准分区,文件系统为ext4

![image-20240724135445014](images/VM安装Linux/image-20240724135445014.png)

第二个分区 swap , 交换分区，建议设置与内存大小一致. 2G

![image-20240724135509823](images/VM安装Linux/image-20240724135509823.png)

修改设备类型为标准分区,文件系统为swap

![image-20240724135459693](images/VM安装Linux/image-20240724135459693.png)

第三个分区 / , 剩余的磁盘大小全部分配。 /为linux文件系统的根目录。

![image-20240724135521013](images/VM安装Linux/image-20240724135521013.png)

修改设备类型为标准分区,文件系统为ext4

![image-20240724135525963](images/VM安装Linux/image-20240724135525963.png)

确认最终分区后的情况,点击左上角完成即可。

![image-20240724135534150](images/VM安装Linux/image-20240724135534150.png)

关闭KDUMP

> Kdump在实际生产环境中需要勾选，这里我在授课环境中就不勾选了。

![image-20240724135541145](images/VM安装Linux/image-20240724135541145.png)

配置网络和主机名(可选,也可在安装好后进入到系统中配置).

![image-20240724135555205](images/VM安装Linux/image-20240724135555205.png)

![image-20240724135600873](images/VM安装Linux/image-20240724135600873.png)

最后确认配置的各个选项无误,点击开启安装即可.

配置ROOT密码 和 创建用户。Linux会默认提供一个超级管理员用户，就是root. 

![image-20240724135631131](images/VM安装Linux/image-20240724135631131.png)

等待安装完成，重启虚拟机

![image-20240724135711899](images/VM安装Linux/image-20240724135711899.png)

初始设置,接受许可证即可， 其他的不用配置。

![image-20240724135703387](images/VM安装Linux/image-20240724135703387.png)

![image-20240724135722266](images/VM安装Linux/image-20240724135722266.png)

点击完成配置

![image-20240724135730527](images/VM安装Linux/image-20240724135730527.png)

进入欢迎界面，选择汉语 ，点击右上角 前进

![image-20240724135734721](images/VM安装Linux/image-20240724135734721.png)

选择键盘布局为汉语

![image-20240724135740954](images/VM安装Linux/image-20240724135740954.png)

隐私设置 ，根据自己的喜好选择即可

![image-20240724135744514](images/VM安装Linux/image-20240724135744514.png)

确定时区

![image-20240724135817483](images/VM安装Linux/image-20240724135817483.png)

跳过关联账号

![image-20240724135759061](images/VM安装Linux/image-20240724135759061.png)

CentOS要求必须设置一个普通账户,可随意设置

![image-20240724135824457](images/VM安装Linux/image-20240724135824457.png)

设置普通账户密码

![image-20240724135829486](images/VM安装Linux/image-20240724135829486.png)

终于可以开始使用了

![image-20240724135834724](images/VM安装Linux/image-20240724135834724.png)

关闭Getting Started

注销当前普通用户，使用root用户登录

选择未列出,使用root登录

为root用户配置欢迎设置。参考上面设置的步骤

安装总结:

整个Linux的安装分两大步，第一个大步装机器，也就是要虚拟一台机器出来,这里需要注意的是以后工作中不需要装虚拟机，全部都是真实的服务器，直接装系统即可.

第二大步就是装系统。

步骤比较多，大家安装时一定要仔细,如果安装过程出错，可选择删除重新安装.多试几次也好，毕竟慢慢就熟练了。

到此，可以开心的使用Linux了。

## 卸载CentOS 7

1、打开虚拟机VMware Wvorkstation

![image-20240724135853788](images/VM安装Linux/image-20240724135853788.png)

2、在菜单栏选择"虚拟机"，在弹出的子菜单栏中选择"管理"

![image-20240724135859437](images/VM安装Linux/image-20240724135859437.png)

3、点击"从磁盘中删除"

![image-20240724135903532](images/VM安装Linux/image-20240724135903532.png)

4、弹出警告，点击"是"

![image-20240724135907147](images/VM安装Linux/image-20240724135907147.png)

5、在我的计算机列表中已经移除了CentOS 7

![image-20240724135912111](images/VM安装Linux/image-20240724135912111.png)

6、在D:\\Program Files (x86)\\Virtual Machines目录下已移除了CentOS 7

![image-20240724135917011](images/VM安装Linux/image-20240724135917011.png)

7、至此从虚拟机卸载CentOS 7已完成。

## 配置静态IP

打开VMWare

选择【虚拟网络编辑器】

![image-20240724140017769](images/VM安装Linux/image-20240724140017769.png)

配置VMnet8网络、子网IP、子网掩码

![image-20240724140143515](images/VM安装Linux/image-20240724140143515.png)

设置网关

![image-20240724140257844](images/VM安装Linux/image-20240724140257844.png)

修改DHCP设置

![image-20240724140332095](images/VM安装Linux/image-20240724140332095.png)

打开Windows网络适配器配置

![image-20240724140513521](images/VM安装Linux/image-20240724140513521.png)

修改IPv4配置，和VMWare网络配置处于同一子网

![image-20240724140553582](images/VM安装Linux/image-20240724140553582.png)

进入Linux命令行界面

输入

``` shell
vim /etc/sysconfig/network-scripts/ifcfg-ens33
```

![image-20240724140719916](images/VM安装Linux/image-20240724140719916.png) 

修改配置

> 修改项： BOOTPROTO、UUID
>
> 添加项：GATEWAY、DNS1、IPADDR、ZONE

```shell
TYPE="Ethernet"
PROXY_METHOD="none"
BROWSER_ONLY="no"
BOOTPROTO="static"
DEFROUTE="yes"
IPV4_FAILURE_FATAL="no"
IPV6INIT="yes"
IPV6_AUTOCONF="yes"
IPV6_DEFROUTE="yes"
IPV6_FAILURE_FATAL="no"
IPV6_ADDR_GEN_MODE="stable-privacy"
NAME="ens33"
UUID="20f658d8-f2b2-4ac9-a70c-b717f3a260aa"
DEVICE="ens33"
ONBOOT="yes"
GATEWAY=192.168.10.2
DNS1=192.168.10.2
IPADDR=192.168.10.100
ZONE=public
```

重启网络

```shell
systemctl restart network
```

输入`ifconfig`查看IP

![image-20240724140959012](images/VM安装Linux/image-20240724140959012.png)