# SpringBoot 提前编译AOT

## JIT与AOT的区别

JIT和AOT 这个名词是指两种不同的编译方式，这两种编译方式的主要区别在于是否在"运行时"进行编译：

- **JIT**(Just-in-time,动态(即时)编译，边运行边编译)：

  在程序运行时，根据算法计算出热点代码，然后进行 JIT 实时编译，这种方式吞吐量高，有运行时性能加成，可以跑得更快，并可以做到动态生成代码等，但是相对启动速度较慢，并需要一定时间和调用频率才能触发 JIT 的分层机制。JIT 缺点就是编译需要占用运行时资源，会导致进程卡顿。

- **AOT**(Ahead Of Time，指运行前编译，预先编译)：

  AOT 编译能直接将源代码转化为机器码，内存占用低，启动速度快，可以无需 runtime 运行，直接将 runtime 静态链接至最终的程序中，但是无运行时性能加成，不能根据程序运行情况做进一步的优化，AOT 缺点就是在程序运行前编译会使程序安装的时间增加。

**AOT 与 JIT 对比**：

![image-20230723004830490](assets/202307230049192.png)

**简单来讲**：JIT即时编译指的是在程序的运行过程中，将字节码转换为可在硬件上直接运行的机器码，并部署至托管环境中的过程。而 AOT 编译指的则是，在程序运行之前，便将字节码转换为机器码的过程。

> **.java -> .class -> (使用jaotc编译工具) -> .so（程序函数库,即编译好的可以供其他程序使用的代码和数据）**

![image-20221207113544080](assets/202412102332176.png)

## 编译器与解释器

语言：

- 编译型语言：编译器

- 解释型语言：解释器

Java：半编译半解释

https://anycodes.cn/editor

![image.png](assets/1683766057952-6f218ecf-4d0a-44ee-a930-1fc7f19085db-17346654042383.png)

| 对比项                 | 编译器                                             | 解释器                                                   |
| ---------------------- | -------------------------------------------------- | -------------------------------------------------------- |
| **机器执行速度**       | **快**，因为源代码只需被转换一次                   | **慢**，因为每行代码都需要被解释执行                     |
| **开发效率**           | **慢**，因为需要耗费大量时间编译                   | **快**，无需花费时间生成目标代码，更快的开发和测试       |
| **调试**               | **难以调试**编译器生成的目标代码                   | **容易调试**源代码，因为解释器一行一行地执行             |
| **可移植性（跨平台）** | 不同平台需要重新编译目标平台代码                   | 同一份源码可以跨平台执行，因为每个平台会开发对应的解释器 |
| **学习难度**           | 相对较高，需要了解源代码、编译器以及目标机器的知识 | 相对较低，无需了解机器的细节                             |
| **错误检查**           | 编译器可以在编译代码时检查错误                     | 解释器只能在执行代码时检查错误                           |
| **运行时增强**         | 无                                                 | 可以**动态增强**                                         |

在 OpenJDK 的官方 Wiki 上，介绍了HotSpot 虚拟机一个相对比较全面的、即时编译器（JIT）中采用的[优化技术列表](https://xie.infoq.cn/link?target=https%3A%2F%2Fwiki.openjdk.java.net%2Fdisplay%2FHotSpot%2FPerformanceTacticIndex)。

可使用：`-XX:+PrintCompilation` 打印JIT编译信息

![image.png](assets/1683773230399-b3fe0f68-f85a-4efb-bf38-d1783ea63d49.png)

![image.png](assets/1683773247546-787b3fcf-ad8a-42d2-9a7b-2980eccff97d.png)

## AOT的优点

**优点**：

- Java 虚拟机加载已经预编译成二进制库，可以直接执行。不必等待及时编译器的预热，减少 Java 应用给人带来"第一次运行慢"的不良体验。

- 在程序运行前编译，可以避免在运行时的编译性能消耗和内存消耗

- 可以在程序运行初期就达到最高性能，程序启动速度快
- 运行产物只有机器码，打包体积小

## AOT的缺点

**缺点**：

- 由于是静态提前编译，不能根据硬件情况或程序运行情况择优选择机器指令序列，理论峰值性能不如JIT

- 没有动态能力，同一份产物不能跨平台运行

JIT即时编译是默认模式，Java Hotspot 虚拟机使用它在运行时将字节码转换为机器码。

AOT提前编译 由新颖的 GraalVM 编译器支持，并允许在构建时将字节码直接静态编译为机器码。

现在正处于云原生，降本增效的时代，Java 相比于 Go、Rust 等其他编程语言非常大的弊端就是启动编译和启动进程非常慢，这对于根据实时计算资源，弹性扩缩容的云原生技术相冲突，SpringBoot3 借助 AOT 技术在运行时内存占用低，启动速度快，逐渐的来满足 Java 在云原生时代的需求，对于大规模使用 Java 应用的商业公司可以考虑尽早调研使用 JDK17，通过云原生技术为公司实现降本增效。

## JVM架构

JVM：既有解释器，又有编辑器 (JIT：即时编译)

![未命名绘图.png](assets/1684124528903-feb1ce8f-302a-4872-a63d-ae5da99501eb.png)

## Java的执行过程

建议阅读：

- 美团技术：https://tech.meituan.com/2020/10/22/java-jit-practice-in-meituan.html
- openjdk官网：https://wiki.openjdk.org/display/HotSpot/Compiler

  **流程概要**：

如果需要**编译执行**时，就会保存到CodeCache代码缓存中，之后可以从代码缓存中读取出来。如果不需要编译时，就会**解释执行**时，每次解释都会统计次数，当达到阈值时，就会触发编译并保存到代码缓存中。

![img](assets/1683774822566-f6860477-868e-4115-8ee9-7fe9d787e7a9.png)

**详细流程**：

热点代码：调用次数非常多的代码

![未命名绘图2.png](assets/1684143084003-df41f505-f8d0-4ab9-a684-5c39037e8e30.png)

## JVM编译器

JVM中集成了两种编译器，Client Compiler 和 Server Compiler：

- Client Compiler注重启动速度和局部的优化
  - HotSpot VM带有一个Client Compiler C1编译器
  - 这种编译器**启动速度快**，但是性能比较Server Compiler来说会差一些
  - 编译后的机器码执行效率没有C2的高
- Server Compiler更加关注全局优化，性能更好，但由于会进行更多的全局分析，所以启动速度会慢
  - Hotspot虚拟机中使用的Server Compiler有两种：C2 和 Graal
  - 在Hotspot VM中，默认的Server Compiler是C2编译器

## 分层编译

Java 7开始引入了分层编译(`Tiered Compiler)`的概念，它结合了C1和C2的优势，追求启动速度和峰值性能的一个平衡。分层编译将JVM的执行状态分为了五个层次。五个层级分别是：

- 解释执行。
- 执行不带profiling的C1代码。
- 执行仅带方法调用次数以及循环回边执行次数profiling的C1代码。
- 执行带所有profiling的C1代码。
- 执行C2代码。

profiling就是收集能够反映程序执行状态的数据。其中最基本的统计数据就是方法的调用次数，以及循环回边的执行次数。

![img](assets/1683775747739-e428b122-ace8-4b33-b860-6a6c7ea11abd.png)

- 图中第①条路径，代表编译的一般情况，**热点方法**从解释执行到被3层的C1编译，最后被4层的C2编译。
- 如果方法比较小（比如Java服务中常见的**getter/setter**方法），3层的profiling没有收集到有价值的数据，JVM就会断定该方法对于C1代码和C2代码的执行效率相同，就会执行图中第②条路径。在这种情况下，JVM会在3层编译之后，放弃进入C2编译，**直接选择用1层的C1编译运行**。
- 在**C1忙碌**的情况下，执行图中第③条路径，在解释执行过程中对程序进行**profiling** ，根据信息直接由第4层的**C2编译**。
- 前文提到C1中的执行效率是**1层>2层>3层**，**第3层一般要比第2层慢35%以上**，所以在**C2忙碌**的情况下，执行图中第④条路径。这时方法会被2层的C1编译，然后再被3层的C1编译，以减少方法在**3层**的执行时间。
- 如果**编译器**做了一些比较**激进的优化**，比如分支预测，在实际运行时**发现预测出错**，这时就会进行**反优化**，重新进入解释执行，图中第⑤条执行路径代表的就是反优化。

总的来说，C1的编译速度更快，C2的编译质量更高，分层编译的不同编译路径，也就是JVM根据当前服务的运行情况来寻找当前服务的最佳平衡点的一个过程。从JDK 8开始，JVM默认开启分层编译。

## 云原生

云原生：Cloud Native

存在的问题：

- java应用如果用jar，解释执行，热点代码才编译成机器码；初始启动速度慢，初始处理请求数量少。
- 大型云平台，要求每一种应用都必须秒级启动。每个应用都要求效率高。

希望的效果：

- java应用也能提前被编译成机器码，随时急速启动，一启动就急速运行，最高性能

- 编译成机器码的好处：

  - 另外的服务器还需要安装Java环境

  - 编译成机器码的，可以在这个平台 Windows X64 直接运行。

原生镜像：native-image（机器码、本地镜像）把应用打包成能适配本机平台 的可执行文件 (机器码、本地镜像)

## Native Image 构建过程

目前业界除了在JVM中进行AOT的方案，还有另外一种实现Java AOT的思路，那就是直接摒弃JVM，和C/C++一样通过编译器直接将代码编译成机器代码，然后运行。这无疑是一种直接颠覆Java语言设计的思路，那就是`GraalVM Native Image`。它通过C语言实现了一个超微缩的运行时组件：Substrate VM，基本实现了JVM的各种特性，但足够轻量、可以被轻松内嵌，这就让Java语言和工程摆脱JVM的限制，能够真正意义上实现和C/C++一样的AOT编译。这一方案在经过长时间的优化和积累后，已经拥有非常不错的效果，基本上成为Oracle官方首推的Java AOT解决方案。

Native Image 是一项创新技术，可将 Java 代码编译成独立的本机可执行文件或本机共享库。在构建本机可执行文件期间处理的 Java 字节码包括所有应用程序类、依赖项、第三方依赖库和任何所需的 JDK 类。生成的自包含本机可执行文件特定于不需要 JVM 的每个单独的操作系统和机器体系结构。

相比于使用JVM运行，Native Image的速度要快上不少，cpu占用也更低一些，从官方提供的各类实验数据也可以看出Native Image对于启动速度和内存占用带来的提升是非常显著的：

![image-20221207111947283](assets/202412102331778.png)

![image-20221207112009852](assets/202412102326830.png)

## GraalVM

GraalVM是一个高性能的JDK，旨在加速用Java和其他JVM语言编写的应用程序的执行，同时还提供JavaScript、Python和许多其他流行语言的运行时。

SpringBoot3 支持的 AOT 技术，这个 GraalVM 就是底层的支持，Spring 也对 GraalVM 本机映像提供了一流的支持。

官方网站：https://www.graalvm.org/

GraalVM 提供两种运行 Java 应用程序的方法：

1. 在 HotSpot JVM 上使用 **Graal 即时 (JIT) 编译器**
2. 作为**预先编译** (AOT) 的本机可执行文件运行(本地镜像)

GraalVM 的多语言能力使得在单个应用程序中混合多种编程语言成为可能，同时消除了外语调用成本。GraalVM 向 HotSpot Java 虚拟机添加了一个用 Java 编写的高级即时 (JIT) 优化编译器。

**GraalVM 特性**：

- 一种高级优化编译器，它生成更快、更精简的代码，需要更少的计算资源

- AOT 本机图像编译提前将 Java 应用程序编译为本机二进制文件，立即启动，无需预热即可实现最高性能

- Polyglot 编程在单个应用程序中利用流行语言的最佳功能和库，无需额外开销

- 高级工具在 Java 和多种语言中调试、监视、分析和优化资源消耗

**架构**：

![image.png](assets/202412221505229.png)

跨平台提供原生镜像原理：

![image.png](assets/1684149328177-6e1474c9-bec3-4b9a-afbe-b17b851f3ab1.png)

## 操作过程

### GraalVM安装

#### 下载GraalVM

进入官网下载：https://www.graalvm.org/downloads/

![image-20230716161940239](assets/202412102326428.png)

![image-20230716162000548](assets/202307161625221.png)

#### 配置环境变量

**添加GRAALVM_HOME**：

> GRAALVM_HOME

![image-20230716162616952](assets/202307161626450.png)

**把JAVA_HOME修改为graalvm的位置**：

![image-20230716163234864](assets/202307161632906.png)

**把Path修改位graalvm的bin位置**：

![image-20230716163435742](assets/202307161635913.png)

**使用命令查看是否安装成功**：

![image-20230716163611625](assets/202307161636987.png)

#### 安装native-image插件

**使用命令 gu install native-image下载安装**

```bash
gu install native-image
```

![image-20230716163953634](assets/202307161640143.png)

### 安装C++的编译环境

#### 下载Visual Studio安装软件

https://visualstudio.microsoft.com/zh-hans/downloads/

![image-20230716164202286](assets/202307161642408.png)

#### 安装Visual Studio

选择：使用C++的桌面开发

![image-20230716165549354](assets/202307161655216.png)

![image-20230716175636312](assets/202307161756130.png)

推荐语言使用英文：避免乱码问题

![image-20241220152858850](assets/image-20241220152858850.png)

![image.png](assets/1684143982484-bac17232-7e72-4bca-9a74-311fa888a8ca.png)

#### 添加Visual Studio环境变量

INCLUDE：

> C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.42.34433\include
>
> C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt
>
> C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\um
>
> C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\shared
>
> C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\cppwinrt
>
> C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\winrt

![image-20241221222339683](assets/image-20241221222339683.png)

lib：

> C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.42.34433\lib\x64;C:\Program Files (x86)\Windows Kits\10\Lib\10.0.22621.0\um\x64;C:\Program Files (x86)\Windows Kits\10\Lib\10.0.22621.0\ucrt\x64;C:\Program Files (x86)\Windows Kits\10\Lib\10.0.22621.0\ucrt_enclave\x64

![image-20230716200330943](assets/202307162003035.png)

Path：

> C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.42.34433\bin\Hostx64\x64

![image-20230716200359542](assets/202307162004878.png)

#### 打开工具，在工具中操作

![image-20221207111206279](assets/202307161801011.png)

![image-20230716180104377](assets/202307161801868.png)

### 编写代码，构建Native Image

#### 构建单代码

编写Java代码：

```java
public class Hello {

    public static void main(String[] args) {
        System.out.println("hello world");
    }
}
```

执行编译：

![image-20230716201408030](assets/202307162014640.png)

Native Image 进行构建：

![image-20230716202128905](assets/202307162021804.png)

![image-20230716202143589](assets/202307162021254.png)

查看构建的文件：

![image-20230716202219242](assets/202307162022562.png)

执行构建的文件：

![image-20230716202256297](assets/202412102332912.png)

可以看到这个Hello最终打包产出的二进制文件大小为13M，这是包含了SVM和JDK各种库后的大小，虽然相比C/C++的二进制文件来说体积偏大，但是对比完整JVM来说，可以说是已经是非常小了。

#### 构建Maven项目

创建项目：

![image-20241220170037844](assets/image-20241220170037844.png)

创建Java类：

![image-20241220170151487](assets/image-20241220170151487.png)

打包：

![image-20241220170302979](assets/image-20241220170302979.png)

打开生成的Jar包，找到`META-INF/MANIFEST.MF`

![image-20241220170359811](assets/image-20241220170359811.png)

添加：`Main-Class: 全类名`

![image-20241220170626330](assets/image-20241220170626330.png)

运行Jar包：

![image-20241220170718788](assets/image-20241220170718788.png)

编译镜像：编译为原生镜像 (native-image)：使用native-tools终端

![image.png](assets/1684147385110-bd82ed80-a65a-439f-b82d-fec40e40edec.png)

```shell
#从入口开始，编译整个jar
native-image -cp aop-demo-1.0-SNAPSHOT.jar com.hjc.demo.MainApplication -o Haha

#编译某个类【必须有main入口方法，否则无法编译】
native-image -cp .\classes org.example.App
```

## Linux平台测试

1. 安装gcc等环境：

   ```shell
   yum install lrzsz
   sudo yum install gcc glibc-devel zlib-devel
   ```

2. 下载安装配置Linux下的GraalVM、native-image

   - 下载：https://www.graalvm.org/downloads/

   - 安装：GraalVM、native-image

   - 配置：JAVA环境变量为GraalVM

     ```shell
     tar -zxvf graalvm-ce-java17-linux-amd64-22.3.2.tar.gz -C /opt/java/

     sudo vim /etc/profile
     #修改以下内容
     export JAVA_HOME=/opt/java/graalvm-ce-java17-22.3.2
     export PATH=$PATH:$JAVA_HOME/bin

     source /etc/profile
     ```

3. 安装native-image

   ```shell
   gu install --file native-image-installable-svm-java17-linux-amd64-22.3.2.jar
   ```

4. 使用native-image编译jar为原生程序

   ```shell
   native-image -cp xxx.jar org.example.App
   ```

## SpringBoot整合

并不是所有的Java代码都能支持本地打包，SpringBoot需要保证Spring应用的所有程序都能在AOT的时候提前告知GraalVM

- 动态能力损失：

  解决方案：额外处理 (Spring提供注解)，提前告知GraalVM反射会用到哪些方法、构造器

- 配置文件损失：

  解决方案：额外处理 (配置中心)，提前告知GraalVM配置文件

### 依赖导入

```xml
 <build>
        <plugins>
            <plugin>
                <groupId>org.graalvm.buildtools</groupId>
                <artifactId>native-maven-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
</build>
```

### 生成native-image

1. 调整命令行工具：

   ![image-20241222152544745](assets/202412221525454.png)

2. 使用maven编译：

   ![image-20241222144853645](assets/image-20241222144853645.png)

3. 运行aot提前处理命令：

   ```shell
   mvn springboot:process-aot
   ```

   ![image-20241222145015842](assets/image-20241222145015842.png)

4. 选中native：

   ![image-20241222145538552](assets/image-20241222145538552.png)

5. 运行native打包：

   ```shell
   # 推荐加上 -Pnative
   mvn -Pnative native:build -f pom.xml
   ```

![image.png](assets/1684152780642-b82e9976-170c-4118-bcd3-a319bc325774.png)

## 常见问题

可能提示如下各种错误，无法构建原生镜像，需要配置环境变量；

- 出现cl.exe找不到错误

- 出现乱码

- 提示no include path set

- 提示fatal error LNK1104: cannot open file 'LIBCMT.lib'

- 提示 LINK : fatal error LNK1104: cannot open file 'kernel32.lib'

- 提示各种其他找不到
