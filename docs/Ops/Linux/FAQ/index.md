# Linux 常见问题与最佳实践

## Permission denied（权限不足）

```shell
ls -l script.sh
chmod +x script.sh      # 加执行权限
sudo command            # 需要管理员权限时
```

如果文件属于其他用户，先确认是否需要 `chown` 或使用 `sudo`。

## command not found

1. 命令没安装：Debian 系 `sudo apt install xxx`，Red Hat 系 `sudo dnf install xxx`。
2. 命令存在但不在 PATH：

```shell
echo $PATH
export PATH="/usr/local/bin:$PATH"
```

## 磁盘满了

```shell
df -h                     # 查看各分区占用
du -sh /var/log /home /tmp   # 定位大目录
find / -xdev -type f -size +1G 2>/dev/null   # 找大文件
journalctl --vacuum-size=200M   # 清理 systemd 日志
```

清理建议：

- 日志：`logrotate` 自动轮转。
- 包缓存：`sudo apt clean` / `sudo dnf clean all`。
- 临时文件：`sudo rm -rf /tmp/*`（确认无进程占用）。

## 端口被占用

```shell
ss -lntp | grep 8080
sudo lsof -i :8080        # 需要安装 lsof
```

找到 PID 后：`kill PID` 或检查是否已有服务占用。

## 服务启动失败

```shell
systemctl status nginx
journalctl -u nginx -xe
```

常见原因：配置文件语法错误、端口冲突、权限不足。改完配置先 `nginx -t` 这类语法检查再重启。

## 忘记 root 密码

这是高危操作，仅限物理机/虚拟机控制台：

1. 重启进入 GRUB，在引导项按 `e`。
2. 在 `linux` 行末尾加 `init=/bin/bash`。
3. `Ctrl+X` 进入单用户 shell，重新挂载根分区并修改密码：

```shell
mount -o remount,rw /
passwd root
reboot
```

::: danger 注意
云主机不建议这样做，优先使用云厂商的“重置密码”功能；操作不当可能导致系统无法启动。
:::

## 安全加固

1. 保持系统更新：`sudo apt update && sudo apt upgrade`。
2. SSH 使用密钥登录，禁止 root 密码登录：

```txt [/etc/ssh/sshd_config]
PermitRootLogin no
PasswordAuthentication no
```

```shell
sudo systemctl restart sshd
```

3. 开启防火墙，只放行必要端口。
4. 安装 `fail2ban` 防暴力破解。
5. 最小权限：普通用户 + sudo，不用 root 跑业务。

## 日常监控命令

```shell
uptime               # 负载
free -h              # 内存
df -h                # 磁盘
top                  # 进程与 CPU
ss -lntp             # 端口
dmesg -T | tail      # 内核日志
```

## 最佳实践清单

1. 命令前先想清楚目标，危险命令（`rm -rf`）先 `ls` 确认。
2. 重要操作先在测试机验证。
3. 配置文件修改前备份：`cp a.conf a.conf.bak`。
4. 用 `crontab` 定期备份并演练恢复。
5. 服务配置改完先语法检查再重启。
6. 生产环境避免 root 直连，用密钥 + sudo。

## 相关链接

- Ubuntu 文档：https://ubuntu.com/server/docs
- Debian 管理员手册：https://www.debian.org/doc/manuals/debian-handbook/
- RHEL 文档：https://docs.redhat.com/en/documentation/red_hat_enterprise_linux
