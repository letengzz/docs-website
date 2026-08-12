# SpringBoot 可观测性

可观测性( Observability)指对线上应用进行观测、监控、预警

包括：

- 健康状况(Health)：组件状态、存活状态
- 运行指标(Metrics)：cpu、内存、垃圾回收、吞吐量、响应成功率...
- 链路追踪
- ...

## SpringBoot Actuator

### 基本操作

**添加依赖**：

```xml
<dependency>
	<groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
<!-- 可观测性场景启动器，线上指标监控、运行状态监控-->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

**暴露指标**：

```yaml
management:
  endpoints:
    enabled-by-default: true #暴露所有端点信息
    web:
      exposure:
        include: '*' #以web方式暴露所有监控端点
```

### 常用端点

| ID               | 描述                                                                                                                      |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------- |
| auditevents      | 暴露当前应用程序的审核事件信息。需要一个AuditEventRepository组件。                                                        |
| beans            | 显示应用程序中所有Spring Bean的完整列表。                                                                                 |
| caches           | 暴露可用的缓存。                                                                                                          |
| conditions       | 显示自动配置的所有条件信息，包括匹配或不匹配的原因。                                                                      |
| configprops      | 显示所有@ConfigurationProperties。                                                                                        |
| env              | 暴露Spring的属性ConfigurableEnvironment                                                                                   |
| flyway           | 显示已应用的所有Flyway数据库迁移。 需要一个或多个Flyway组件。                                                             |
| health           | 显示应用程序运行状况信息。                                                                                                |
| httptrace        | 显示HTTP跟踪信息（默认情况下，最近100个HTTP请求-响应）。需要一个HttpTraceRepository组件。                                 |
| info             | 显示应用程序信息。                                                                                                        |
| integrationgraph | 显示Spring integrationgraph 。需要依赖spring-integration-core。                                                           |
| loggers          | 显示和修改应用程序中日志的配置。                                                                                          |
| liquibase        | 显示已应用的所有Liquibase数据库迁移。需要一个或多个Liquibase组件。                                                        |
| metrics          | 显示当前应用程序的“指标”信息。                                                                                            |
| mappings         | 显示所有@RequestMapping路径列表。                                                                                         |
| scheduledtasks   | 显示应用程序中的计划任务。                                                                                                |
| sessions         | 允许从Spring Session支持的会话存储中检索和删除用户会话。需要使用Spring Session的基于Servlet的Web应用程序。                |
| shutdown         | 使应用程序正常关闭。默认禁用。                                                                                            |
| startup          | 显示由ApplicationStartup收集的启动步骤数据。需要使用SpringApplication进行配置BufferingApplicationStartup。                |
| threaddump       | 执行线程转储。                                                                                                            |
| heapdump         | 返回hprof堆转储文件。                                                                                                     |
| jolokia          | 通过HTTP暴露JMX bean（需要引入Jolokia，不适用于WebFlux）。需要引入依赖jolokia-core。                                      |
| logfile          | 返回日志文件的内容（如果已设置logging.file.name或logging.file.path属性）。支持使用HTTPRange标头来检索部分日志文件的内容。 |
| prometheus       | 以Prometheus服务器可以抓取的格式公开指标。需要依赖micrometer-registry-prometheus。                                        |

### 访问数据

- 访问 http://localhost:8080/actuator 展示出所有可以用的监控端点

  ![image-20230723181633709](assets/img202401061249904.png)

- 访问 http://localhost:8080/actuator/health 展示出健康信息(UP：运行成功、DOWN：运行失败)

  ![image-20230723181658479](assets/img202401061249031.png)

- 访问 http://localhost:8080/actuator/beans 展示出所有的组件(Bean)，包括组件名、类型、依赖

  ![image-20230723181712639](assets/img202401061249056.png)

- 访问 http://localhost:8080/actuator/caches 展示出所有的缓存信息

  ![image-20230723181728329](assets/img202401061250560.png)

- 访问 http://localhost:8080/actuator/conditions 展示条件判断(自动配置)，判断哪些的功能是开启的

  ![image-20230723181750444](assets/img202401061249186.png)

- 访问 http://localhost:8080/actuator/env 展示出所有的环境变量

  ![image-20230723181829352](assets/img202401061249857.png)

- 访问 http://localhost:8080/actuator/configprops 展示出所有的属性(配置文件)

  ![image-20230723181851463](assets/img202401061249293.png)

- 访问 http://localhost:8080/actuator/loggers 展示出所有的日志级别及信息

  ![image-20230723181908241](assets/img202401061249147.png)

- 访问 http://localhost:8080/actuator/heapdump 下载整个堆内存

  ![image-20230723182137940](assets/img202401061250026.png)

- 访问 http://localhost:8080/actuator/threaddump 展示出所有的线程信息

  ![image-20230723182319764](assets/img202401061250443.png)

- 访问 http://localhost:8080/actuator/metrics 展示出所有的指标

  访问 http://localhost:8080/actuator/metrics/jvm.gc.pause 展示出具体的指标

  ![image-20230723182602649](assets/img202401061249966.png)

- 访问 http://localhost:8080/actuator/mappings 展示出所有的映射信息

  ![image-20230723182749261](assets/img202401061250966.png)

### 定制端点

**定义定制端点一般分为**：

- 健康监控：返回存活、死亡

- 指标监控：次数、率

#### 定制健康监控

**例**：线上监控 `MyHahaComponent`组件：

1. 创建 `MyHahaComponent`：

   ```java
   package com.hjc.demo.component;

   import org.springframework.stereotype.Component;

   /**
    * 自定义组件
    * @author hjc
    */
   @Component
   public class MyHahaComponent {
       public int check(){
           //业务代码判断这个组件是否该是存货状态
           return 1;
       }
   }
   ```

2. 通过实现HealthIndicator接口来定制组件的健康状态对象(Health)返回：

   ```java
   package com.hjc.demo.health;

   import com.hjc.demo.component.MyHahaComponent;
   import jakarta.annotation.Resource;
   import org.springframework.boot.actuate.health.Health;
   import org.springframework.boot.actuate.health.HealthIndicator;
   import org.springframework.stereotype.Component;
   /**
    * 后缀名必须为 Indicator
    * 实现方式：
    *   1、实现HealthIndicator接口来定制组件的健康状态对象(Health)返回
    *   2、实现抽象类 AbstractHealthIndicator
    * @author hjc
    */
   @Component
   public class MyHahaIndicator implements HealthIndicator {
       @Resource
       private MyHahaComponent component;
       /**
        * 返回健康状况
        * @return 健康状况
        */
       @Override
       public Health health() {
           //自定义检查方法
           int errorCode = component.check();
           if (errorCode == 0) {
               //下线
               return Health.down().withDetail("Error Code", errorCode).build();
           }
           //存活
           return Health.up().build();
       }

   }
   ```

   或者实现抽象类 AbstractHealthIndicator：

   ```java
   package com.hjc.demo.health;

   import com.hjc.demo.component.MyHahaComponent;
   import jakarta.annotation.Resource;
   import org.springframework.boot.actuate.health.AbstractHealthIndicator;
   import org.springframework.boot.actuate.health.Health;
   import org.springframework.boot.actuate.health.HealthIndicator;
   import org.springframework.stereotype.Component;

   /**
    * 后缀名必须为 Indicator
    * 1、实现HealthIndicator接口来定制组件的健康状态对象(Health)返回
    * 2、实现抽象类 AbstractHealthIndicator
    * @author hjc
    */
   @Component
   public class MyHaIndicator extends AbstractHealthIndicator {
       @Resource
       private MyHahaComponent component;

       /**
        * 健康检查
        */
       @Override
       protected void doHealthCheck(Health.Builder builder) throws Exception {
           //自定义检查方法
           int check = component.check();
           if (check == 1){
               Health.up()
                       .withDetail("msg", "up")
                       .withDetail("code", "100")
                       .withDetail("data","haha")
                       .build();
           }else {
               Health build = Health.down()
                       .withDetail("msg", "error service")
                       .withDetail("code", "500")
                       .withException(new RuntimeException())
                       .build();
           }
       }
   }
   ```

3. 添加配置：

   ```yaml
   management:
     endpoint:
       health:
         enabled: true
         show-details: always #总是显示详细信息。可显示每个模块的状态信息
   ```

4. 访问：http://localhost:8080/actuator/health

   ![image-20240106140504759](assets/img202401061405599.png)

   当有一个组件DOWN，那么Spring就会认为总体状态就DOWN

#### 定制指标监控

统计Controller调用component 多少次

```java
package com.hjc.demo.controller;

import com.hjc.demo.component.MyHahaComponent;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 统计Controller调用component 多少次
 * @author hjc
 */
@RestController
public class HelloController {
    @Resource
    private MyHahaComponent component;

    @GetMapping("/hello")
    public String hello() {
        //业务调用 打印hello
        component.hello();
        return "哈哈哈";
    }
}
```

```java
package com.hjc.demo.component;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import org.springframework.stereotype.Component;

/**
 * 自定义组件
 *
 * @author hjc
 */
@Component
public class MyHahaComponent {
    Counter counter = null;

    /**
     * 注入 MeterRegistry 来保存和统计所有指标
     * @param registry MeterRegistry
     */
    public MyHahaComponent(MeterRegistry registry) {
        //注册指标
        //得到名叫 myhaha.haha 的计数器
        counter = registry
                .counter("myhaha.haha");
    }

    public void hello() {
        System.out.println("hello");
        //计数器+1
        counter.increment();
    }
}
```

访问：http://localhost:8080/hello

再次访问：http://localhost:8080/actuator/metrics

![image-20240106142639155](assets/img202401061426703.png)

访问：http://localhost:8080/actuator/metrics/myhaha.haha

![image-20240106142732151](assets/img202401061427264.png)

## 基于Prometheus+Grafana监控

![image.png](assets/img202401061314881.png)

### 安装Prometheus

使用Docker安装：

```shell
#安装prometheus:时序数据库
docker run -p 9090:9090 -d \
--name=prometheus \
-v pc:/etc/prometheus \
prom/prometheus
```

访问ip:9090访问Prometheus：

![image-20240106144334929](assets/img202401061443442.png)

### 安装Grafana

```shell
#安装grafana；默认账号密码 admin:admin
docker run -d --name=grafana -p 3000:3000 grafana/grafana
```

访问ip:3000访问Grafana，输入账号：admin，密码：admin，修改密码即可：

![image-20240106144045243](assets/img202401061440403.png)

### 导入依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

```yaml
management:
  endpoints:
    web:
      exposure: #暴露所有监控的端点
        include: '*'
```

访问： http://localhost:8080/actuator/prometheus 验证，返回 prometheus 格式的所有指标

![image-20240106144908405](assets/img202401061449946.png)

### 部署Java应用

```shell
#安装上传工具
yum install lrzsz

#安装openjdk
# 下载openjdk
wget https://download.oracle.com/java/17/latest/jdk-17_linux-x64_bin.tar.gz

mkdir -p /opt/java
tar -xzf jdk-17_linux-x64_bin.tar.gz -C /opt/java/
sudo vi /etc/profile
#加入以下内容
export JAVA_HOME=/opt/java/jdk-17.0.7
export PATH=$PATH:$JAVA_HOME/bin

#环境变量生效
source /etc/profile


# 后台启动java应用
nohup java -jar springboot_actuator-0.0.1-SNAPSHOT.jar > output.log 2>&1 &
```

### 后台启动java应用

```shell
nohup java -jar springboot_actuator-0.0.1-SNAPSHOT.jar > output.log 2>&1 &
```

确认可以访问到： http://ip:8080/actuator/prometheus

### 配置 Prometheus 拉取数据

查看配置文件路径：

```shell
docker inspect pc
```

修改 prometheus.yml 配置文件：

```yaml
scrape_configs:
  - job_name: 'spring-boot-actuator-exporter' #名称随意
    metrics_path: '/actuator/prometheus' #指定抓取的路径
    static_configs:
      - targets: ['192.168.200.1:8001'] #由于部署同一台机器使用私有地址
        labels:
          nodename: 'app-demo'
```

![image-20240106151628445](assets/img202401061516296.png)

配置完成后，访问Prometheus查看：

![image-20240106151655074](assets/img202401061516007.png)

重启Prometheus：

```
docker restart prometheus
```

![image-20240106154844274](assets/img202401061548986.png)

### 配置 Grafana 监控面板

添加数据源 (Prometheus)：

![image-20240106155605296](assets/img202401061556817.png)

![image-20240106160034023](assets/img202401061600971.png)

添加面板。可去 dashboard 市场找一个自己喜欢的面板，也可以自己开发面板：[Dashboards | Grafana Labs](https://grafana.com/grafana/dashboards/?plcmt=footer)

![image-20240106160530876](assets/img202401061605240.png)

![image-20240106160202449](assets/img202401061602515.png)

![image-20240106160555343](assets/img202401061605713.png)

![image-20240106160506829](assets/img202401061605870.png)

### 效果

![image-20240106160720637](assets/img202401061607023.png)
