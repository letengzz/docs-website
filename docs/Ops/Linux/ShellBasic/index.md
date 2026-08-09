# Shell 基础

Shell 是 Linux 的命令解释器，Bash 是最常用的 Shell，也是运维自动化的基础。

## 变量

```shell
name="zhangsan"
echo $name
echo ${name}123

export PATH="/usr/local/bin:$PATH"   # 导出为环境变量
```

特殊变量：

| 变量 | 含义 |
| --- | --- |
| `$0` | 脚本名 |
| `$1`、`$2` | 第 1、2 个参数 |
| `$#` | 参数个数 |
| `$?` | 上一条命令退出码（0 成功） |
| `$$` | 当前进程 PID |

## 条件判断

```shell
if [ -f /etc/nginx/nginx.conf ]; then
  echo "配置文件存在"
else
  echo "配置文件不存在"
fi
```

常用判断：

| 写法 | 含义 |
| --- | --- |
| `-f 文件` | 是否是普通文件 |
| `-d 目录` | 是否是目录 |
| `-z 字符串` | 字符串是否为空 |
| `a = b` | 字符串相等 |
| `a -eq b` | 数字相等（-ne/-gt/-lt/-ge/-le） |

::: danger 注意
1. `[` 和 `]` 两侧必须有空格：`[ "$x" = "a" ]`，写错会报语法错误。
2. 变量建议加双引号：`[ "$name" = "a" ]`，避免空值问题。
:::

## 循环

```shell
# for 循环
for i in 1 2 3; do
  echo "第 $i 次"
done

# 遍历文件
for f in *.log; do
  echo "处理 $f"
done

# while 循环
count=1
while [ $count -le 5 ]; do
  echo $count
  count=$((count + 1))
done
```

## 函数

```shell
greet() {
  echo "Hello, $1"
}

greet "zhangsan"
```

## 脚本示例：备份目录

```shell [backup.sh]
#!/bin/bash

SRC="/var/www"
DEST="/backup"
STAMP=$(date +%Y%m%d_%H%M%S)

if [ ! -d "$SRC" ]; then
  echo "源目录不存在: $SRC"
  exit 1
fi

mkdir -p "$DEST"
tar -czf "$DEST/www_$STAMP.tar.gz" "$SRC"

if [ $? -eq 0 ]; then
  echo "备份完成: $DEST/www_$STAMP.tar.gz"
else
  echo "备份失败"
  exit 1
fi
```

运行：

```shell
bash backup.sh
# 或赋予执行权限后直接运行
chmod +x backup.sh
./backup.sh
```

## 实用小技巧

```shell
set -e                # 脚本中任何命令失败立即退出
set -u                # 使用未定义变量时报错
command || exit 1     # 失败则退出
echo "耗时: $(date +%s)"
```

## 验证方式

```shell
echo "hello $USER"
[ -d /etc ] && echo "/etc 存在"
for i in 1 2 3; do echo $i; done
```

能按预期输出即验证通过。
