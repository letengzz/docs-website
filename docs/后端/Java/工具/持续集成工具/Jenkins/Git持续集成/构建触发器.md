# 自动构建

## 构建方式

- 快照依赖构建 (`Build whenever a SNAPSHOT dependency is built`)：当依赖的快照被构建时执行本job
- 触发远程构建 (例如，使用脚本)：远程调用本job的restapi时执行本job
- job依赖构建 (`Build after other projects are built`)：当依赖的job被构建时执行本job
- 定时构建 (`Build periodically`)：使用cron表达式定时构建本job
- 向GitHub提交代码时触发Jenkins自动构建 (`GitHub hook trigger for GITScm polling`)：Github-WebHook出发时构建本job
- 定期检查代码变更 (`Poll SCM`)：使用cron表达式定时检查代码变更，变更后构建本job

## 快照依赖构建

## 触发远程构建

通过访问URL来远程触发构建项目。

创建一个令牌：

![image-20240331221535291](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403312215192.png)

使用 GET请求来访问`JENKINS_URL/job/first-project/build?token=TOKEN_NAME` 或者 `/buildWithParameters?token=TOKEN_NAME`来构建项目

![image-20240331222212125](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403312222416.png)

但是直接请求需要在登录的情况下才可以构建成功，可以借助插件来解决该问题：

![image-20240331222843327](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403312228035.png)

访问该地址来构建：

![image-20240331223428620](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403312234731.png)

![image-20240331223621381](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403312236364.png)

### 使用GitLab

代码改动自动可以使用GitLab的Webhooks回调钩子调起Jenkins的启动任务接口

配置网络：

![image-20240331224301559](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403312243735.png)

新建Webhooks：

![image-20240331223800391](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403312238498.png)

![image-20240331224537252](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403312245804.png)

![image-20240331224552883](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403312245772.png)

![image-20240331224615660](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403312246417.png)

![image-20240331224712679](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403312247412.png)

## Job依赖构建

## 定时构建

标准cron表达式：https://crontab.guru

Jenkins cron不是标准的cron表达式

cron表达式：

- 第一个 `*`：表示每个小时的第几分钟，取值0~59

  `H * * * *`：每小时执行一次

- 第二颗 `*`：表示小时，取值0~23

  `15 * * *`：表示每天下午3点

  `1 * * *`：表示每天凌晨1点

- 第三颗 `*`：表示一个月的第几天，取值1~31

  `1 5 * *`：表示每月5日凌晨1点

- 第四颗 `*`：表示第几月，取值1~12

  `15 5 1 *`：表示每年几月执行

- 第五颗 `*`：表示一周中的第几天，取值0~7，其中0和7代表的都是周日

**特殊用法**：

- `/`：表示每隔多长时间，比如 `*/10 * * * *` 表示 每隔10分钟

- `H`：hash散列值，以job名取值，获取到以job名为入参的唯一值，相同名称值也相同，这个偏移量会和实际时间相加，获得一个真实的运行时间

  意义在于：不同的项目在不同的时间运行，即使配置的值是一样的，比如 都是`15 * * * * ` ，表示每个小时的第15分钟开始执行任务，那么会造成同一时间内在Jenkins中启动很多job，换成`H/15 * * * *`,那么在首次启动任务时，会有随机值参与进来，有的会在17分钟启动 有的会在19分钟启动，随后的启动时间也是这个值。这样就能错开相同cron值的任务执行了。

  H的值也可以设置范围：`H(1-30) * * * *`

**示例**：

- `H * * * *`：表示一小时内的任意时间

- `*/10 * * * *`：每10分钟

- `H/10 * * * *`：每10分钟,可能是7,17,27，起始时间hash，步长不变

- `45 3 * * 1-6 ` ：每个周一至周六，凌晨3点45 执行1次

- `45 3-5 * * 1-6 `：每个周一至周六，凌晨3点45 ，凌晨4点45，凌晨5点45 各执行1次

- `H(40-48) 3-5 * * 1-6 `：在40~48之间取值 其他同上

- `45 3-5/2 * * 1-6 `：每个周一至周六，凌晨3点45 ，凌晨5点45 各执行1次

- ` 45 0-6/2 * * 1-6 * * 1-6 `：0点开始，每间隔2小时执行一次 0:45、2:45、4:45

## GitHub 自动构建

## SCM 构建

使用Poll SCM 方式与Build periodically类似，但是该方式是Jenkins主动发起的，会主动定期检查代码托管服务器上是否有变化，一旦发生变化执行job构建。

## 邮件接收构建通知

使用163免费邮箱发送邮件时注意密码填认证码，不要用登录邮箱的密码

配置系统管理员邮件地址：

![image-20240331234951592](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403312349494.png)

配置邮件地址：

![image-20240331235247325](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403312352872.png)

![image-20240331235333322](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403312353131.png)

![image-20240331235417958](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403312354760.png)

![image-20240331235512699](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403312355983.png)

![image-20240331235547635](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403312355756.png)

配置系统邮件通知：

![image-20240401000704938](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404010007637.png)

创建构建后操作：

![image-20240401000210108](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404010002080.png)

添加用户组：

![image-20240401000246724](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404010002117.png)

![image-20240401000302032](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404010003792.png)