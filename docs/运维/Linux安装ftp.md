### 安装ftp
设置本地用户访问用户主目录 和 特定用户指定访问目录
添加ftp用户 和 指定访问目录
```shell
 yum install -y vsftpd
```
```shell
useradd ftpuser
passwd ftpuser
```
配置：
```shell
# 禁用匿名登录
anonymous_enable=NO
# 允许本地用户登录
local_enable=YES
# 允许FTP用户进行写操作
write_enable=YES
# 将所有本地用户限制在他们的主目录中
chroot_local_user=YES
# 允许主目录可写
allow_writeable_chroot=YES
# 指定用户特定配置文件的目录
user_config_dir=/etc/vsftpd/vsftpd_user_conf

# /etc/vsftpd/user_list文件不生效
userlist_enable=NO

# 以被动模式连接
pasv_enable=YES
# 设置端口范围 防火墙和云服务器安全组记得开放
pasv_min_port=50000
pasv_max_port=50300
```
```shell
mkdir /etc/vsftpd/vsftpd_user_conf
cd /etc/vsftpd/vsftpd_user_conf
vim ftpuser
```
```shell
local_root=/var/ftp/uploads
```
```shell
mkdir -p /var/ftp/uploads
chown ftpuser:ftpuser /var/ftp/uploads
chmod 755 /var/ftp
chmod 755 /var/ftp/uploads
```
```shell
# 修改配置文件需要重启服务
systemctl restart vsftpd
```
> 注意：如果vsftpd_user_conf目录下账号名对应的文件删除，然后重启服务
> 用户的访问目录就会变成 自己的主目录，ftpuser --> /home/ftpuser


### 指定目录不显示文件
**如果特定用户指定的访问目录内，只显示目录，不显示文件，使用以下方法测试：**
```shell
sestatus
```
```shell
setenforce 0
# 如确认问题，请调整 SELinux 策略，而不是永久禁用
```
自定义SELinux策略
```shell
# CentOS 系统
yum install policycoreutils-python-utils
# Debian 系统
apt-get install policycoreutils
```
生成 SELinux 策略模块
```shell
# 首先，将 SELinux 设置回 enforcing 模式：
setenforce 1
```
```shell
# 提取相关的 SELinux 警报并生成策略模块：
ausearch -m avc -ts recent | audit2allow -M myftpd
```
```shell
semodule -i myftpd.pp
```
验证新的 SELinux 策略
```shell
# 再次验证 FTP 用户是否可以正常访问和操作指定目录。
setenforce 1

# 然后尝试使用 FTP 进行操作，以确保新策略生效。
```
确保策略持久化
```shell
# 生成的策略模块会在系统重启后继续生效。可以通过以下命令检查已加载的 SELinux 模块：
semodule -l | grep ftp
```
其他注意事项
```shell
ausearch -m avc -ts recent
```
如果遇到新的权限问题，可以重复上述步骤，生成新的自定义 SELinux 策略模块。
