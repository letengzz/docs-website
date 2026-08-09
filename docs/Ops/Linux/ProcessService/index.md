# Linux 进程与服务

## 进程基础

- **进程（Process）**：运行中的程序实例，每个进程有唯一的 **PID**。
- **PPID**：父进程 ID，进程由父进程创建。
- **守护进程（Daemon）**：后台常驻服务，如 nginx、sshd。

## 查看进程

```shell
ps aux                 # 所有进程（BSD 风格）
ps -ef                 # 所有进程（标准风格）
ps -ef | grep nginx    # 查找指定进程
top                    # 动态监控（q 退出）
htop                   # 更友好的监控（需安装）
```

`ps aux` 关键字段：

| 字段 | 含义 |
| --- | --- |
| USER | 进程所属用户 |
| PID | 进程号 |
| %CPU / %MEM | CPU / 内存占用 |
| STAT | 状态（S 睡眠、R 运行、Z 僵尸） |
| COMMAND | 启动命令 |

## 结束进程

```shell
kill 1234              # 正常终止
kill -9 1234           # 强制杀死（慎用）
pkill nginx            # 按名字结束
pkill -f "java -jar"   # 按完整命令行匹配
```

::: danger 注意
1. `kill -9` 不会给进程清理机会，可能丢数据或留脏状态，先试普通 `kill`。
2. 杀进程前先确认 PID：`ps -ef | grep 进程名`。
:::

## 前后台任务

```shell
long_task &            # 后台运行
jobs                   # 查看后台任务
fg %1                  # 切回前台
bg %1                  # 放入后台
```

## systemd 服务管理

现代发行版用 systemd 管理服务：

```shell
systemctl status nginx          # 查看状态
systemctl start nginx           # 启动
systemctl stop nginx            # 停止
systemctl restart nginx         # 重启
systemctl reload nginx          # 平滑重载配置
systemctl enable nginx          # 开机自启
systemctl disable nginx         # 取消自启
systemctl list-units --type=service   # 列出服务
```

查看服务日志：

```shell
journalctl -u nginx             # 指定服务日志
journalctl -u nginx -f          # 实时跟踪
journalctl -xe                  # 最近错误（排障神器）
```

## 定时任务 cron

```shell
crontab -e              # 编辑当前用户的定时任务
crontab -l              # 查看
```

格式：`分 时 日 月 周 命令`

```text
# 每天 2 点执行备份脚本
0 2 * * * /opt/backup.sh

# 每 5 分钟清理一次临时文件
*/5 * * * * rm -f /tmp/*.tmp
```

::: tip
1. cron 的环境变量很少，脚本里尽量写绝对路径。
2. 排障先看 `/var/log/syslog` 或 `journalctl -u cron`。
:::

## 常见问题

- **僵尸进程（Z）**：父进程未回收，通常由父进程 bug 导致，重启父进程可清理。
- **端口被占用**：用 `ss -lntp | grep 端口` 找到 PID 再处理（见网络篇）。
- **服务起不来**：先 `journalctl -xe` 看错误日志。

## 验证方式

```shell
ps -ef | head -5
top -b -n 1 | head -15
systemctl status nginx   # 按实际服务名
crontab -l
```

能正常输出进程、系统状态和定时任务即验证通过。
