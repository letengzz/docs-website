### Linux下安装
- 上传安装包jdk-8u333-linux-x64.tar.gz
- mkdir /usr/local/java
- tar -zxvf jdk-8u333-linux-x64.tar.gz -C /usr/local/java
- vim /etc/profile
在文件末尾添加
export JAVA_HOME=/usr/local/java/jdk1.8.0_333
export PATH=$PATH:$JAVA_HOME/bin
- source /etc/profile
- java -version 验证是否配置成功

