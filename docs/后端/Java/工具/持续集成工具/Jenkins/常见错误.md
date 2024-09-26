# Jenkins 常见错误

## jenkins使用shell脚本执行nohup java -jar包失败

通过jenkins执行shell脚本时，脚本中是通过nohup java -jar &的方式启动，显示执行成功，但是服务却没启动：

```sh
nohup /usr/local/java/bin/java -jar /root/test1/demo*.jar  &
```

Jenkins默认会在构建完成后，杀掉构建过程中由shell命令触发的衍生进程。

Jenkins根据BUILD_ID识别某个进程是否为构建过程的衍生进程，故修改BUILD_ID后，jenkins就无法识别是否为衍生进程，则此进程能在后台保留运行。

结论就是Jenkins程序只负责运行伪命令行nuhup 命令，并不保证是否成功运行 nuhup后面的命令。

**解决办法**：

1. 使用 `BUILD_ID=xxx` ,其中xxx可以是任意内容 (只要不是原来的BUILD_ID内容即可)，同时需要把nohup输出内容重定向到文件里面，如"/usr/local/nohup.out"

   ```sh
   #! /bin/bash
   BUILD_ID=dontKillMe
   nohup /usr/local/java/bin/java -jar /root/test1/demo*.jar >mylog.log 2>&1 &
   ```

2. 使用at now代替nohup命令。

   - set -e ： 执行的时候如果出现了返回值为非零，整个脚本 就会立即退出
   - set +e： 执行的时候如果出现了返回值为非零将会继续执行下面的脚本

   ```sh
   #! /bin/bash
   #so "at now" will run even if java -jar fails
   set +e 
   #Run java app in background
   echo "java -jar /usr/local/joshua317-test-core-1.0-SNAPSHOT.jar" | at now
   ```

