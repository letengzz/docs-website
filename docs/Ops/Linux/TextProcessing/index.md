# Linux 文本处理命令

服务器运维中大量工作是对日志和配置文件的处理，掌握文本命令能事半功倍。

## 查看文件

```shell
cat /etc/os-release          # 全部内容
less /var/log/syslog         # 分页查看（q 退出）
head -n 20 app.log           # 前 20 行
tail -n 20 app.log           # 后 20 行
tail -f app.log              # 实时跟踪（看日志神器）
```

## 重定向与管道

```shell
ls > files.txt               # 覆盖写入
ls >> files.txt              # 追加写入
grep error app.log > err.txt # 过滤后保存
ls | wc -l                   # 管道：统计行数
ls | head -5                 # 只看前 5 个
```

::: tip
管道 `|` 把前一个命令的输出作为后一个命令的输入，是 Linux 命令组合的核心。
:::

## grep 文本搜索

```shell
grep "ERROR" app.log                 # 查找关键字
grep -i error app.log                # 忽略大小写
grep -n error app.log                # 显示行号
grep -r error /var/log/nginx/        # 递归搜索目录
grep -v "INFO" app.log               # 排除匹配行
grep -E "ERROR|WARN" app.log         # 扩展正则（或）
grep -c "ERROR" app.log              # 统计匹配次数
```

## sed 流编辑

```shell
sed 's/old/new/' file.txt            # 替换每行第一个匹配
sed 's/old/new/g' file.txt           # 替换全部匹配
sed -i 's/127.0.0.1/0.0.0.0/g' app.conf   # 原地修改
sed -n '10,20p' file.txt             # 打印 10~20 行
sed '/^#/d' file.txt                 # 删除注释行
```

::: danger 注意
`sed -i` 会直接修改原文件，建议先不加 `-i` 预览输出，确认无误再原地修改。
:::

## awk 列处理

```shell
awk '{print $1}' file.txt            # 打印第一列
awk -F: '{print $1, $3}' /etc/passwd # 指定冒号分隔
awk '{print NR, NF}' file.txt        # 行号、列数
awk '$3 > 100 {print $1}' data.txt   # 条件过滤
```

## 实战：分析访问日志

```shell
# 统计 Nginx 日志中各 IP 的访问次数（取第一列，排序）
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10

# 统计 500 错误数量
grep -c '" 500 ' access.log

# 统计每个 URL 的访问次数
awk '{print $7}' access.log | sort | uniq -c | sort -rn | head -10
```

## 验证方式

```shell
echo -e "a 1\nb 2\na 3" > /tmp/demo.txt
awk '{print $1}' /tmp/demo.txt | sort | uniq -c
sed 's/a/A/' /tmp/demo.txt
```

能正确输出统计结果即验证通过。
