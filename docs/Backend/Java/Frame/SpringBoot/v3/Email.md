# SpringBoot 邮件发送

在注册很多的网站时，都会遇到邮件或是手机号验证，也就是通过邮箱或是手机短信去接受网站发给注册验证信息，填写验证码之后，就可以完成注册了，同时，网站也会绑定手机号或是邮箱。

实现一个邮件注册功能验证流程：**请求验证码 -> 生成验证码 (临时有效，注意设定过期时间) -> 用户输入验证码并填写注册信息 -> 验证通过注册成功！**

SpringBoot已经提供了封装好的邮件模块使用：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-mail</artifactId>
</dependency>
```

电子邮件也是一种通信方式，是互联网应用最广的服务。通过网络的电子邮件系统，用户可以以非常低廉的价格（不管发送到哪里，都只需负担网费，实际上就是把信息发送到对方服务器而已）、非常快速的方式，与世界上任何一个地方的电子邮箱用户联系。

要在Internet上提供电子邮件功能，必须有专门的电子邮件服务器。例如现在Internet很多提供邮件服务的厂商：新浪、搜狐、163、QQ邮箱等，他们都有自己的邮件服务器。这些服务器类似于现实生活中的邮局，它主要负责接收用户投递过来的邮件，并把邮件投递到邮件接收者的电子邮箱中。

所有的用户都可以在电子邮件服务器上申请一个账号用于邮件发送和接收，实际上和Http一样，邮件发送也有自己的协议，也就是约定邮件数据长啥样以及如何通信。

![image-20230818113121524](assets/202308181131389.png)

比较常用的协议有两种：

1. SMTP协议 (主要用于发送邮件 Simple Mail Transfer Protocol)
2. POP3协议 (主要用于接收邮件 Post Office Protocol 3)

**整个发送/接收流程**：

![img](assets/202308181355957.jpeg)

实际上每个邮箱服务器都有一个smtp发送服务器和pop3接收服务器，比如要从QQ邮箱发送邮件到163邮箱，那么我们只需要通过QQ邮箱客户端告知QQ邮箱的smtp服务器我们需要发送邮件，以及邮件的相关信息，然后QQ邮箱的smtp服务器就会帮助我们发送到163邮箱的pop3服务器上，163邮箱会通过163邮箱客户端告知对应用户收到一封新邮件。

如果想要实现给别人发送邮件，那么就需要连接到对应电子邮箱的smtp服务器上，并告知其要发送邮件。而SpringBoot已经将最基本的底层通信全部实现了，只需要关心smtp服务器的地址以及要发送的邮件长啥样即可。

## 基础配置

这里以163邮箱 [https://mail.163.com](https://mail.163.com/) 为例，需要在配置文件中告诉SpringBootMail smtp服务器的地址以及邮箱账号和密码，首先去设置中开启smtp/pop3服务才可以，开启后会得到一个随机生成的密钥，这个就是密码。

```yaml
spring:
  mail:
    # 163邮箱的地址为smtp.163.com，直接填写即可
    host: smtp.163.com
    # 你申请的163邮箱
    username: javastudy111@163.com
    # 注意密码是在开启smtp/pop3时自动生成的，记得保存一下，不然就找不到了
    password: RAKTCQGORXBPIVPR
```

## 发送简单内容

配置完成后，测试：

```java
@SpringBootTest
class SpringbootEmailApplicationTests {
    @Resource
    private JavaMailSender sender;


    @Value("${spring.mail.username}")
    private String username;

    /**
     * 发送简单内容
     */
    @Test
    void sendSimpleMessage() {
        //SimpleMailMessage是一个比较简易的邮件封装，支持设置一些比较简单内容
        SimpleMailMessage message = new SimpleMailMessage();
        //邮件发送者，这里要与配置文件中的保持一致
        message.setFrom(username);
        //设置邮件发送给谁，可以多个，这里就发给你的邮箱
        message.setTo("2020885569@qq.com");
        //抄送,收到邮件用户可以看到其他收件人
        message.setCc("2020885569@qq.com");
        //密送 收到邮件用户看不到其他收件人
        message.setBcc("2020885569@qq.com");
        //设置邮件标题
        message.setSubject("【电子科技大学教务处】关于近期学校对您的处分决定");
        //设置邮件内容
        message.setText("XXX同学您好，经监控和教务巡查发现，您近期存在旷课、迟到、早退、上课刷抖音行为，" +
                "现已通知相关辅导员，请手写5000字书面检讨，并在2022年4月1日17点前交到辅导员办公室。");
        //设置当前时间为发送时间
        message.setSentDate(new Date());
        //OK，万事俱备只欠发送
        sender.send(message);
        System.out.println("邮件发送成功");
    }
}
```

## 发送附件内容

:::warning 说明

cc 和 bcc 的区别：

- cc方式接收到的用户可以看到其他接收用户
- bcc方式接收用户看不到其他接收用户

:::

如果需要添加附件等更多功能，可以使用MimeMessageHelper来完成：

```java
@SpringBootTest
class SpringbootEmailApplicationTests {
    @Resource
    private JavaMailSender sender;


    @Value("${spring.mail.username}")
    private String username;

    @Test
    void sendTextMail() throws MessagingException {
        //创建一个MimeMessage
        MimeMessage message = sender.createMimeMessage();
        //使用MimeMessageHelper来修改MimeMessage中的信息
        MimeMessageHelper helper = new MimeMessageHelper(message, true);
        //设置邮件发送给谁，可以多个，这里就发给你的邮箱
        helper.setTo("2020885569@qq.com");
        helper.setFrom(username);
        helper.setSentDate(new Date());
        //设置邮件标题
        helper.setSubject("【电子科技大学教务处】关于近期学校对您的处分决定");
        //设置邮件内容
        helper.setText("XXX同学您好，经监控和教务巡查发现，您近期存在旷课、迟到、早退、上课刷抖音行为，" +
                "现已通知相关辅导员，请手写5000字书面检讨，并在2022年4月1日17点前交到辅导员办公室。");
        //抄送,收到邮件用户可以看到其他收件人
        helper.setCc("2020885569@qq.com");
        //密送 收到邮件用户看不到其他收件人
        helper.setBcc("2020885569@qq.com");
        //附件
        File tmpOne = new File("D:\\es\\hello.doc");
        helper.addAttachment(tmpOne.getName(), tmpOne);
        //发送修改好的MimeMessage
        sender.send(message);
        System.out.println("邮件发送成功");
    }
}
```

## 发送HTML内容

html邮件和普通邮件的处理不一样，需要用map传递参数给thymeleaf模板

```java
import jakarta.annotation.Resource;
import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;

import org.thymeleaf.TemplateEngine;
import org.thymeleaf.context.Context;

import java.io.File;
import java.util.Date;
import java.util.HashMap;

@SpringBootTest
class SpringbootEmailApplicationTests {
    @Resource
    private JavaMailSender sender;

    @Resource
    private TemplateEngine templateEngine;

    @Value("${spring.mail.username}")
    private String username;

    @Test
    void sendHtmlMail() throws MessagingException {
        MimeMessage mimeMessage = sender.createMimeMessage();
        MimeMessageHelper helper = new MimeMessageHelper(mimeMessage, true);
        helper.setFrom(username);
        helper.setSubject("【电子科技大学教务处】关于近期学校对您的处分决定");
        helper.setTo("2020885569@qq.com");
        //抄送,收到邮件用户可以看到其他收件人
        helper.setCc("2020885569@qq.com");
        //密送 收到邮件用户看不到其他收件人
        helper.setBcc("2020885569@qq.com");
        helper.setSentDate(new Date());
        //生成邮件模板上的内容
        Context context = new Context();
        HashMap<String, String> content = new HashMap<String, String>();
        content.put("username", "hjc");
        content.put("nickname", "hjc");
        content.put("id", "0000001");
        for (String key : content.keySet()) {
            context.setVariable(key, content.get(key));
        }
        String process = templateEngine.process("mail/sendMail.html", context);
        helper.setText(process, true);
        sender.send(mimeMessage);
        System.out.println("邮件发送成功");
    }
}
```

**添加依赖**：

```xml
<dependency>
	<groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-thymeleaf</artifactId>
</dependency>
```

添加HTML：

![image-20240107224609036](assets/img202401072247115.png)

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Title</title>
  </head>
  <body>
    <h1>您好，注册成功! 以下是您在本网站的注册信息：</h1>
    <table border="1">
      <tr>
        <td>用户名</td>
        <td th:text="${username}">${username}</td>
      </tr>
      <tr>
        <td>昵称</td>
        <td th:text="${nickname}">${nickname}</td>
      </tr>
      <tr>
        <td>ID</td>
        <td th:text="${id}">${id}</td>
      </tr>
    </table>
  </body>
</html>
```
