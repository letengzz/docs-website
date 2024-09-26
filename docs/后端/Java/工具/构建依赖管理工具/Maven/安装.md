# Maven 安装并配置核心程序

官方下载：https://maven.apache.org/download.cgi

## Windows 安装并配置核心程序

### 安装程序

1. 进入[官方下载Maven核心程序](https://maven.apache.org/download.cgi)：

   ![image-20231023162709009](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231627100.png)

2. 解压Maven核心程序：核心程序压缩包：[apache-maven-3.9.5-bin.zip](https://dlcdn.apache.org/maven/maven-3/3.9.5/binaries/apache-maven-3.9.5-bin.zip)，解压到**非中文、没有空格**的目录

   ![image-20231023162924067](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231629474.png)

### 核心配置

#### 指定本地仓库

**本地仓库默认值**：用户家目录/.m2/repository。由于本地仓库的默认位置是在用户的家目录下，而家目录往往是在 C 盘，也就是系统盘。将来 Maven 仓库中 jar 包越来越多，仓库体积越来越大，可能会拖慢 C 盘运行速度，影响系统性能。所以建议将 Maven 的本地仓库放在其他盘符下

**指定本地仓库**：打开**conf/settings.xml**核心配置文件，修改并保存即可：

```xml
<!-- localRepository
| The path to the local repository maven will use to store artifacts.
|
| Default: ${user.home}/.m2/repository
<localRepository>/path/to/local/repo</localRepository>
-->
<!-- 配置本地仓库的路径 -->
<localRepository>D:\repo\maven-repository</localRepository>
```

**注意**：

- 本地仓库这个目录，需要手动创建一个空的目录。

- 本地仓库本身也需要使用一个**非中文、没有空格**的目录。

![image-20231023163525529](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231635725.png)

#### 配置阿里云镜像仓库

Maven 下载 jar 包默认访问境外的中央仓库，而国外网站速度很慢。改成阿里云提供的镜像仓库，**访问国内网站**，可以让 Maven 下载 jar 包的时候速度更快。

**配置方式**：

- 将原有的例子配置注释掉：

  ```xml
  <!-- <mirror>
    <id>maven-default-http-blocker</id>
    <mirrorOf>external:http:*</mirrorOf>
    <name>Pseudo repository to mirror external repositories initially using HTTP.</name>
    <url>http://0.0.0.0/</url>
    <blocked>true</blocked>
  </mirror> -->
  ```

- **加入配置**：将下面 mirror 标签整体复制到 settings.xml 文件的 mirrors 标签的内部。

  ```xml
  <mirror>
  	<id>nexus-aliyun</id>
  	<mirrorOf>central</mirrorOf>
  	<name>Nexus aliyun</name>
  	<url>http://maven.aliyun.com/nexus/content/groups/public</url>
  </mirror>
  ```

  ![image-20231023165010075](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231650145.png)

#### 配置Maven 工程基础JDK版本

如果按照默认配置运行，Java 工程使用的默认 JDK 版本是 1.5，可以根据自己的版本来配置。

修改配置的方式是：将 profile 标签整个复制到 settings.xml 文件的 profiles 标签内：

> 配置jdk8

```xml
<profile>
	<id>jdk-1.8</id>
	<activation>
		<activeByDefault>true</activeByDefault>
		<jdk>1.8</jdk>
	</activation>
	<properties>
		<maven.compiler.source>1.8</maven.compiler.source>
		<maven.compiler.target>1.8</maven.compiler.target>
		<maven.compiler.compilerVersion>1.8</maven.compiler.compilerVersion>
	</properties>
</profile>
```

> 配置jdk17

```xml
<profile>  
    <id>jdk17</id>  
    <activation>  
        <activeByDefault>true</activeByDefault>  
        <jdk>17</jdk>  
    </activation>  
    <properties>  
        <maven.compiler.source>17</maven.compiler.source>  
        <maven.compiler.target>17</maven.compiler.target>  
        <maven.compiler.compilerVersion>17</maven.compiler.compilerVersion>  
    </properties>   
</profile>  
```

#### 设置多个配置

setting 通常公司都有私服地址，但不是所有包私服上都有，这时就要用阿里云或者其他地址去拉包。
那么可以直接设置setting 使其拉包时第一个地址拉取不到自动到第二个地址拉取以此类推可设置多个仓库地址进行补充。

> settings.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">

<localRepository>D:\repo\maven-repository</localRepository>
  <pluginGroups></pluginGroups>
  <proxies></proxies>
  <servers></servers>
  <mirrors></mirrors>

  <profiles>
    <profile>
      <id>aliyun</id> 
      <repositories>
        <repository>
          <id>aliyun</id> 
          <url>https://maven.aliyun.com/repository/public</url> 
          <releases>
            <enabled>true</enabled>
          </releases> 
          <snapshots>
            <enabled>true</enabled> 
            <updatePolicy>always</updatePolicy>
          </snapshots>
        </repository>
      </repositories>
    </profile>
	<profile>
		<id>private</id>
		<repositories>
			<repository>
				<id>maven-releases</id>
				<name>User Porject Release</name>
				<url>http://私服地址/nexus/repository/maven-releases/</url>
				<snapshots>
					<enabled>false</enabled>
				</snapshots>
				<releases>
					<enabled>true</enabled>
				</releases>
			</repository>
			<repository>
				<id>maven-snapshots</id>
				<name>User Porject Snapshot</name>
				<url>http://私服地址/nexus/repository/maven-snapshots/</url>
				<snapshots>
					<enabled>true</enabled>
					<updatePolicy>always</updatePolicy>
				</snapshots>
			</repository>
			<!-- 也可以把阿里云等仓库地址直接在这里补充 -->
			<repository>
				<id>com.e-iceblue</id>
				<name>e-iceblue</name>
				 <url>http://xxx.cn/repository/maven-public/</url>
			</repository>
		</repositories>
	</profile>
<!--    <profile>-->
<!--      <id>repo1</id>-->
<!--      <repositories>-->
<!--        <repository>-->
<!--          <id>repo1</id>-->
<!--          <url>https://repo1.maven.org/maven2</url>-->
<!--          <releases>-->
<!--            <enabled>true</enabled>-->
<!--          </releases>-->
<!--          <snapshots>-->
<!--            <enabled>true</enabled>-->
<!--            <updatePolicy>always</updatePolicy>-->
<!--          </snapshots>-->
<!--        </repository>-->
<!--      </repositories>-->
<!--    </profile>-->
<!--    <profile>-->
<!--      <id>repo2</id>-->
<!--      <repositories>-->
<!--        <repository>-->
<!--          <id>repo2</id>-->
<!--          <url>https://repo2.maven.org/maven2</url>-->
<!--          <releases>-->
<!--            <enabled>true</enabled>-->
<!--          </releases>-->
<!--          <snapshots>-->
<!--            <enabled>true</enabled>-->
<!--            <updatePolicy>always</updatePolicy>-->
<!--          </snapshots>-->
<!--        </repository>-->
<!--      </repositories>-->
<!--    </profile>-->
  </profiles>

  <activeProfiles>
    <activeProfile>aliyun</activeProfile>
    <activeProfile>private</activeProfile>
<!--  <activeProfile>repo1</activeProfile>-->
<!--  <activeProfile>repo2</activeProfile>-->
    </activeProfiles>
</settings>
```

#### 其他问题

maven 默认有一个setting文件，如果setting文件有很多，而默认setting中的mirror 直接指定了仓库路径，此时无论引用哪个setting文件，都会首先到默认setting内指定的仓库中拉取。

默认setting文件设置后，指定了另外的setting文件，但是他会去D:\repo\maven-repository路径下寻包，寻找不到直接报错`Could not find artifact xxx in public` **最好只保留一个setting文件**

### 配置环境变量

1. 检查 JAVA_HOME 配置是否正确：Maven 是一个用 Java 语言开发的程序，它必须基于 JDK 来运行，需要通过 JAVA_HOME 来找到 JDK 的安装位置。

   ```shell
   echo %JAVA_HOME%
   java -version
   ```

   ![image-20231023164035243](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231640828.png)

2. 配置 MAVEN_HOME：(**配置环境变量的规律**：XXX_HOME 通常指向的是 bin 目录的上一级，PATH 指向的是 bin 目录)

   将Maven安装位置配置为`MAVEN_HOME`

   ![image-20231023164256215](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231642938.png)

3. 配置PATH：

   ```
   %MAVEN_HOME%\bin
   ```

   ![image-20231023164634590](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231646546.png)

4. 验证：

   ```shell
   mvn -v
   ```

   ![image-20231105132734015](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051327939.png)

## MacOS 安装核心程序

### 安装程序

1. 进入[官方下载Maven核心程序](https://maven.apache.org/download.cgi)：

   ![image-20231023162709009](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231627100.png)

2. 解压Maven核心程序：核心程序压缩包：[apache-maven-3.9.5-bin.zip](https://dlcdn.apache.org/maven/maven-3/3.9.5/binaries/apache-maven-3.9.5-bin.zip)，解压到**非中文、没有空格**的目录

   ![image-20231127222432799](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202311272224295.png)

### 配置环境变量

检查 JAVA_HOME 配置是否正确：Maven 是一个用 Java 语言开发的程序，它必须基于 JDK 来运行，需要通过 JAVA_HOME 来找到 JDK 的安装位置。

```shell
java -version
```

![image-20231129211809719](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202311292119030.png)

配置 MAVEN_HOME：(**配置环境变量的规律**：XXX_HOME 通常指向的是 bin 目录的上一级，PATH 指向的是 bin 目录)

打开终端，并编辑 `/etc/profile` 文件(执行`sudo nano /etc/profile`)，添加内容：

```bash
export MAVEN_HOME=/Users/cuifendemac/Program/apache-maven-3.9.5
export PATH=$MAVEN_HOME/bin:$PATH
```

![image-20231129215104064](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202311292151180.png)

按下"Ctrl+ X"，输入"Y"，再按下"Enter"保存文件并退出

运行`source /etc/profile`命令使环境变量立即生效

```
source /etc/profile
```

验证：

```shell
mvn -v
```

![image-20231129215518069](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202311292155257.png)

### 核心配置

#### 指定本地仓库

打开**conf/settings.xml**核心配置文件，修改并保存即可：

```xml
<!-- localRepository
| The path to the local repository maven will use to store artifacts.
|
| Default: ${user.home}/.m2/repository
<localRepository>/path/to/local/repo</localRepository>
-->
<!-- 配置本地仓库的路径 -->
<localRepository>/Users/cuifendemac/Data/mvn-repo</localRepository>
```

**注意**：

- 本地仓库这个目录，需要手动创建一个空的目录。

- 本地仓库本身也需要使用一个**非中文、没有空格**的目录。

![image-20231127222737961](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/Java/202311272227030.png)

#### 配置阿里云镜像仓库

Maven 下载 jar 包默认访问境外的中央仓库，而国外网站速度很慢。改成阿里云提供的镜像仓库，**访问国内网站**，可以让 Maven 下载 jar 包的时候速度更快。

**配置方式**：

- 将原有的例子配置注释掉：

  ```xml
  <!-- <mirror>
    <id>maven-default-http-blocker</id>
    <mirrorOf>external:http:*</mirrorOf>
    <name>Pseudo repository to mirror external repositories initially using HTTP.</name>
    <url>http://0.0.0.0/</url>
    <blocked>true</blocked>
  </mirror> -->
  ```

- **加入配置**：将下面 mirror 标签整体复制到 settings.xml 文件的 mirrors 标签的内部。

  ```xml
  <mirror>
  	<id>nexus-aliyun</id>
  	<mirrorOf>central</mirrorOf>
  	<name>Nexus aliyun</name>
  	<url>http://maven.aliyun.com/nexus/content/groups/public</url>
  </mirror>
  ```

  ![image-20231023165010075](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231650145.png)

#### 配置Maven 工程基础JDK版本

如果按照默认配置运行，Java 工程使用的默认 JDK 版本是 1.5，可以根据自己的版本来配置。

修改配置的方式是：将 profile 标签整个复制到 settings.xml 文件的 profiles 标签内：

> 配置jdk8

```xml
<profile>
	<id>jdk-1.8</id>
	<activation>
		<activeByDefault>true</activeByDefault>
		<jdk>1.8</jdk>
	</activation>
	<properties>
		<maven.compiler.source>1.8</maven.compiler.source>
		<maven.compiler.target>1.8</maven.compiler.target>
		<maven.compiler.compilerVersion>1.8</maven.compiler.compilerVersion>
	</properties>
</profile>
```

> 配置jdk17

```xml
<profile>  
    <id>jdk17</id>  
    <activation>  
        <activeByDefault>true</activeByDefault>  
        <jdk>17</jdk>  
    </activation>  
    <properties>  
        <maven.compiler.source>17</maven.compiler.source>  
        <maven.compiler.target>17</maven.compiler.target>  
        <maven.compiler.compilerVersion>17</maven.compiler.compilerVersion>  
    </properties>   
</profile>  
```

#### 设置多个配置

setting 通常公司都有私服地址，但不是所有包私服上都有，这时就要用阿里云或者其他地址去拉包。
那么可以直接设置setting 使其拉包时第一个地址拉取不到自动到第二个地址拉取以此类推可设置多个仓库地址进行补充。

> settings.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">

<localRepository>/Users/cuifendemac/Data/mvn-repo</localRepository>
  <pluginGroups></pluginGroups>
  <proxies></proxies>
  <servers></servers>
  <mirrors></mirrors>

  <profiles>
    <profile>
      <id>aliyun</id> 
      <repositories>
        <repository>
          <id>aliyun</id> 
          <url>https://maven.aliyun.com/repository/public</url> 
          <releases>
            <enabled>true</enabled>
          </releases> 
          <snapshots>
            <enabled>true</enabled> 
            <updatePolicy>always</updatePolicy>
          </snapshots>
        </repository>
      </repositories>
    </profile>
	<profile>
		<id>private</id>
		<repositories>
			<repository>
				<id>maven-releases</id>
				<name>User Porject Release</name>
				<url>http://私服地址/nexus/repository/maven-releases/</url>
				<snapshots>
					<enabled>false</enabled>
				</snapshots>
				<releases>
					<enabled>true</enabled>
				</releases>
			</repository>
			<repository>
				<id>maven-snapshots</id>
				<name>User Porject Snapshot</name>
				<url>http://私服地址/nexus/repository/maven-snapshots/</url>
				<snapshots>
					<enabled>true</enabled>
					<updatePolicy>always</updatePolicy>
				</snapshots>
			</repository>
			<!-- 也可以把阿里云等仓库地址直接在这里补充 -->
			<repository>
				<id>com.e-iceblue</id>
				<name>e-iceblue</name>
				 <url>http://xxx.cn/repository/maven-public/</url>
			</repository>
		</repositories>
	</profile>
<!--    <profile>-->
<!--      <id>repo1</id>-->
<!--      <repositories>-->
<!--        <repository>-->
<!--          <id>repo1</id>-->
<!--          <url>https://repo1.maven.org/maven2</url>-->
<!--          <releases>-->
<!--            <enabled>true</enabled>-->
<!--          </releases>-->
<!--          <snapshots>-->
<!--            <enabled>true</enabled>-->
<!--            <updatePolicy>always</updatePolicy>-->
<!--          </snapshots>-->
<!--        </repository>-->
<!--      </repositories>-->
<!--    </profile>-->
<!--    <profile>-->
<!--      <id>repo2</id>-->
<!--      <repositories>-->
<!--        <repository>-->
<!--          <id>repo2</id>-->
<!--          <url>https://repo2.maven.org/maven2</url>-->
<!--          <releases>-->
<!--            <enabled>true</enabled>-->
<!--          </releases>-->
<!--          <snapshots>-->
<!--            <enabled>true</enabled>-->
<!--            <updatePolicy>always</updatePolicy>-->
<!--          </snapshots>-->
<!--        </repository>-->
<!--      </repositories>-->
<!--    </profile>-->
  </profiles>

  <activeProfiles>
    <activeProfile>aliyun</activeProfile>
    <activeProfile>private</activeProfile>
<!--  <activeProfile>repo1</activeProfile>-->
<!--  <activeProfile>repo2</activeProfile>-->
    </activeProfiles>
</settings>
```

#### 其他问题

maven 默认有一个setting文件，如果setting文件有很多，而默认setting中的mirror 直接指定了仓库路径，此时无论引用哪个setting文件，都会首先到默认setting内指定的仓库中拉取。

默认setting文件设置后，指定了另外的setting文件，但是他会去路径下寻包，寻找不到直接报错`Could not find artifact xxx in public` **最好只保留一个setting文件**

## Linux 安装核心程序