# Linux 文件与目录命令

## 查看与切换

```shell
pwd                     # 当前目录
ls                      # 列出文件
ls -l                   # 详细列表（权限、属主、大小、时间）
ls -a                   # 包含隐藏文件
ls -lh                  # 人类可读大小
ls -lt                  # 按时间排序
cd /etc                 # 切换目录
cd ~                    # 回用户家目录
```

::: tip
很多发行版把 `ll` 配置为 `ls -l` 的别名，可以直接使用。
:::

## 创建文件与目录

```shell
touch a.txt             # 创建空文件或更新时间戳
mkdir dir1              # 创建目录
mkdir -p a/b/c          # 递归创建多级目录
```

## 复制、移动、删除

```shell
cp a.txt b.txt          # 复制文件
cp -r dir1 dir2         # 递归复制目录
mv a.txt /tmp/          # 移动
mv a.txt b.txt          # 重命名
rm a.txt                # 删除文件
rm -r dir1              # 递归删除目录
rm -rf dir1             # 强制递归删除（危险！）
```

::: danger 注意
1. `rm -rf` 没有回收站，删除后不可恢复，执行前务必确认路径。
2. 不要对 `/`、`~`、`/etc` 使用 `rm -rf` 组合。
3. `cp` 目录必须加 `-r`，否则报错。
:::

## 查看文件信息

```shell
file a.txt              # 文件类型
stat a.txt              # 详细元信息（大小、权限、时间）
du -sh dir1             # 目录占用空间
df -h                   # 磁盘使用情况
```

## 查找文件

```shell
find /etc -name "nginx*"          # 按名字查找
find /var -type f -size +100M     # 大于 100MB 的文件
find /home -type d -name "logs"   # 按目录名查找
which nginx                       # 命令所在路径
locate nginx.conf                 # 数据库快速查找（需 updatedb）
```

## 通配符

| 通配符 | 含义 | 示例 |
| --- | --- | --- |
| `*` | 任意多个字符 | `*.log` |
| `?` | 单个字符 | `file?.txt` |
| `[abc]` | 括号内任一字符 | `file[12].txt` |

```shell
ls *.log
rm file?.txt
```

## 链接

```shell
ln -s /etc/nginx/nginx.conf myconf    # 软链接（快捷方式）
ln a.txt hardlink                     # 硬链接（同一文件多个名字）
```

::: tip
软链接可以跨文件系统、可指向目录；硬链接只能指向文件且不能跨文件系统，日常最常用的是软链接。
:::

## 验证方式

```shell
mkdir -p /tmp/lab && cd /tmp/lab
touch a.txt
cp a.txt b.txt
ls -l
rm a.txt b.txt
cd / && rm -rf /tmp/lab
```

每个命令都能正常执行且无报错，即验证通过。
