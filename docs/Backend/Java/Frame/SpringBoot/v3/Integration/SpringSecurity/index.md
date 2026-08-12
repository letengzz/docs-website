```
# SpringBoot 整合 SpringSecurity

- [SpringSecurity 操作](../../../SpringSecurity/README.md)
- 

 安全架构 

  1. 认证：Authentication  

who are you?
登录系统，用户系统



  2. 授权：Authorization 

what are you allowed to do？
权限管理，用户授权



  3. 攻击防护 

●XSS（Cross-site scripting）
●CSRF（Cross-site request forgery）
●CORS（Cross-Origin Resource Sharing）
●SQL注入
●...



 扩展. 权限模型 

  1. RBAC(Role Based Access Controll) 

●用户（t_user）
○id,username,password，xxx
○1,zhangsan
○2,lisi 
●用户_角色（t_user_role）【N对N关系需要中间表】
○zhangsan, admin
○zhangsan,common_user
○lisi, hr
**○**lisi, common_user
●角色（t_role）
○id,role_name
○admin
○hr
○common_user
●角色_权限(t_role_perm)
○admin, 文件r
○admin, 文件w
○admin, 文件执行
○admin, 订单query，create,xxx
**○**hr, 文件r
●权限（t_permission）
○id,perm_id
○文件 r,w,x
○订单 query,create,xxx



  2. ACL(Access Controll List) 

直接用户和权限挂钩
●用户（t_user）
○zhangsan
○lisi
●用户_权限(t_user_perm)
○zhangsan,文件 r
○zhangsan,文件 x
○zhangsan,订单 query
●权限（t_permission）
○id,perm_id
○文件 r,w,x
○订单 query,create,xxx







  2. Spring Security 原理 

  3. 过滤器链架构 

Spring Security利用 FilterChainProxy 封装一系列拦截器链，实现各种安全拦截功能
Servlet三大组件：Servlet、Filter、Listener

SPRING SECURITY FI TERS

CLIENT

FILTER

FILTER

FILTER

FILTERCHAINPROXY

FILTER

FILTER

SERVLET

![image.png](https://cdn.nlark.com/yuque/0/2023/png/1613913/1682513527616-e1e9054a-9049-4005-8c92-86392f3012a2.png?x-oss-process=image%2Fwatermark%2Ctype_d3F5LW1pY3JvaGVp%2Csize_34%2Ctext_5bCa56GF6LC3IGF0Z3VpZ3UuY29t%2Ccolor_FFFFFF%2Cshadow_50%2Ct_80%2Cg_se%2Cx_10%2Cy_10)





  2. FilterChainProxy 

FILTERCHAINPROXY

/FROO/

/BAR/

米米

FILTER

FILTER

FILTER

---50000000000555

FILTER

FILTER

FILTER

FILTER

![image.png](https://cdn.nlark.com/yuque/0/2023/png/1613913/1682513900851-013516c0-b3d4-4a09-823a-e924a5fa8f2c.png?x-oss-process=image%2Fwatermark%2Ctype_d3F5LW1pY3JvaGVp%2Csize_34%2Ctext_5bCa56GF6LC3IGF0Z3VpZ3UuY29t%2Ccolor_FFFFFF%2Cshadow_50%2Ct_80%2Cg_se%2Cx_10%2Cy_10)





  3. SecurityFilterChain 

CLIENT

FILTERCHAIN

3000300:000:00000000.

SECURITYLILIERCHAIN

FILTER.

SECURITY FILTER.

DELEGATINGFILTERPROXY

99988903939859085909888829988888888899

FILTERCHAINPROXY

SOONSSOOSSOOSSOSSAOSANSAOSEOOSSOOSOOSSOOR

SECURITY FILTER

FILTER

SERVLET

![image.png](https://cdn.nlark.com/yuque/0/2023/png/1613913/1683548784456-8c66fd8e-783e-4f89-b81f-d3f2771a3ef9.png?x-oss-process=image%2Fwatermark%2Ctype_d3F5LW1pY3JvaGVp%2Csize_20%2Ctext_5bCa56GF6LC3IGF0Z3VpZ3UuY29t%2Ccolor_FFFFFF%2Cshadow_50%2Ct_80%2Cg_se%2Cx_10%2Cy_10)





  3. 使用 

  4. HttpSecurity 





  2. MethodSecurity 





核心

**●**WebSecurityConfigurerAdapter

●@EnableGlobalMethodSecurity： 开启全局方法安全配置

○@Secured

○@PreAuthorize

○@PostAuthorize

**●**UserDetailService： 去数据库查询用户详细信息的service（用户基本信息、用户角色、用户权限）

  4. 实战 

  5. 引入依赖 



  2. 页面 

 首页 





 Hello页 





 登录页 



  3. 配置类 

 视图控制 



 Security配置 





Java

复制代码

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

45

46

47

48

49

50

51

package com.atguigu.security.config;

import org.springframework.context.annotation.Bean;

import org.springframework.context.annotation.Configuration;

import org.springframework.security.config.annotation.web.builders.HttpSecurity;

import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;

import org.springframework.security.core.userdetails.User;

import org.springframework.security.core.userdetails.UserDetails;

import org.springframework.security.core.userdetails.UserDetailsService;

import org.springframework.security.provisioning.InMemoryUserDetailsManager;

import org.springframework.security.web.SecurityFilterChain;

/**

 \* @author lfy

 \* @Description

 \* @create 2023-03-08 16:54

 */

@Configuration

@EnableWebSecurity

public class WebSecurityConfig {

​    @Bean

​    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {

​        http

​                .authorizeHttpRequests((requests) -> requests

​                        .requestMatchers("/", "/home").permitAll()

​                        .anyRequest().authenticated()

​                )

​                .formLogin((form) -> form

​                        .loginPage("/login")

​                        .permitAll()

​                )

​                .logout((logout) -> logout.permitAll());

​        return http.build();

​    }

​    @Bean

​    public UserDetailsService userDetailsService() {

​        UserDetails user =

​                User.withDefaultPasswordEncoder()

​                        .username("admin")

​                        .password("admin")

​                        .roles("USER")

​                        .build();

​        return new InMemoryUserDetailsManager(user);

​    }

}



  4. 改造Hello页 





HTML

复制代码

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

<!DOCTYPE html>


<html

  xmlns="http://www.w3.org/1999/xhtml"

  xmlns:th="https://www.thymeleaf.org"

  xmlns:sec="https://www.thymeleaf.org/thymeleaf-extras-springsecurity6"

\>

  <head>


​    <title>Hello World!</title>

  </head>

  <body>

​    <h1 th:inline="text">

​      Hello <span th:remove="tag" sec:authentication="name">thymeleaf</span>!

​    </h1>

​    <form th:action="@{/logout}" method="post">

​      <input type="submit" value="Sign Out" />

​    </form>

  </body>

</html>
```

