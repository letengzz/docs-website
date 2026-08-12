# Spring Security 内部机制

## 授权校验流程

SpringSecurity的实现原理：它本质上是依靠N个Filter实现的，也就是一个完整的过滤链（注意这里是过滤器，不是拦截器）

从`AbstractSecurityWebApplicationInitializer`开始下手，我们来看看它配置了什么：

```java
//此方法会在启动时被调用
public final void onStartup(ServletContext servletContext) {
    this.beforeSpringSecurityFilterChain(servletContext);
    if (this.configurationClasses != null) {
        AnnotationConfigWebApplicationContext rootAppContext = new AnnotationConfigWebApplicationContext();
        rootAppContext.register(this.configurationClasses);
        servletContext.addListener(new ContextLoaderListener(rootAppContext));
    }

    if (this.enableHttpSessionEventPublisher()) {
        servletContext.addListener("org.springframework.security.web.session.HttpSessionEventPublisher");
    }

    servletContext.setSessionTrackingModes(this.getSessionTrackingModes());
  	//重点在这里，这里插入了关键的FilterChain
    this.insertSpringSecurityFilterChain(servletContext);
    this.afterSpringSecurityFilterChain(servletContext);
}
```

```java
private void insertSpringSecurityFilterChain(ServletContext servletContext) {
    String filterName = "springSecurityFilterChain";
  	//创建了一个DelegatingFilterProxy对象，它本质上也是一个Filter，但是是多个Filter的集合
    DelegatingFilterProxy springSecurityFilterChain = new DelegatingFilterProxy(filterName);
    String contextAttribute = this.getWebApplicationContextAttribute();
    if (contextAttribute != null) {
        springSecurityFilterChain.setContextAttribute(contextAttribute);
    }
		//通过ServletContext注册DelegatingFilterProxy这个Filter
    this.registerFilter(servletContext, true, filterName, springSecurityFilterChain);
}
```

我们接着来看看，`DelegatingFilterProxy`在做什么：

```java
//这个是初始化方法，它由GenericFilterBean（父类）定义，在afterPropertiesSet方法中被调用
protected void initFilterBean() throws ServletException {
    synchronized(this.delegateMonitor) {
        if (this.delegate == null) {
            if (this.targetBeanName == null) {
                this.targetBeanName = this.getFilterName();
            }

            WebApplicationContext wac = this.findWebApplicationContext();
            if (wac != null) {
              	//耐心点，套娃很正常
                this.delegate = this.initDelegate(wac);
            }
        }

    }
}
```

```java
protected Filter initDelegate(WebApplicationContext wac) throws ServletException {
    String targetBeanName = this.getTargetBeanName();
    Assert.state(targetBeanName != null, "No target bean name set");
  	//这里通过WebApplicationContext获取了一个Bean
    Filter delegate = (Filter)wac.getBean(targetBeanName, Filter.class);
    if (this.isTargetFilterLifecycle()) {
        delegate.init(this.getFilterConfig());
    }

  	//返回Filter
    return delegate;
}
```

这里我们需要添加一个断点来查看到底获取到了什么Bean。

通过断点调试，我们发现这里放回的对象是一个FilterChainProxy类型的，并且调用了它的初始化方法。

我们倒回去看，当Filter返回之后，`DelegatingFilterProxy`的一个成员变量`delegate`被赋值为得到的Filter，也就是FilterChainProxy对象，接着我们来看看，`DelegatingFilterProxy`是如何执行doFilter方法的。

```java
public void doFilter(ServletRequest request, ServletResponse response, FilterChain filterChain) throws ServletException, IOException {
    Filter delegateToUse = this.delegate;
    if (delegateToUse == null) {
        //非正常情况，这里省略...
    }
		//这里才是真正的调用，别忘了delegateToUse就是初始化的FilterChainProxy对象
    this.invokeDelegate(delegateToUse, request, response, filterChain);
}
```

```java
protected void invokeDelegate(Filter delegate, ServletRequest request, ServletResponse response, FilterChain filterChain) throws ServletException, IOException {
  //最后实际上调用的是FilterChainProxy的doFilter方法
    delegate.doFilter(request, response, filterChain);
}
```

所以我们接着来看，`FilterChainProxy`的doFilter方法又在干什么：

```java
public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
    boolean clearContext = request.getAttribute(FILTER_APPLIED) == null;
    if (!clearContext) {
      	//真正的过滤在这里执行
        this.doFilterInternal(request, response, chain);
    } else {
        //...
    }
}
```

![image-20230705005303736](https://s2.loli.net/2023/07/05/LVxihksHZu2qN6X.png)

```java
private void doFilterInternal(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
    FirewalledRequest firewallRequest = this.firewall.getFirewalledRequest((HttpServletRequest)request);
    HttpServletResponse firewallResponse = this.firewall.getFirewalledResponse((HttpServletResponse)response);
  	//这里获取了一个Filter列表，实际上SpringSecurity就是由N个过滤器实现的，这里获取的都是SpringSecurity提供的过滤器
  	//但是请注意，经过我们之前的分析，实际上真正注册的Filter只有DelegatingFilterProxy
  	//而这里的Filter列表中的所有Filter并没有被注册，而是在这里进行内部调用
    List<Filter> filters = this.getFilters((HttpServletRequest)firewallRequest);
  	//只要Filter列表不是空，就依次执行内置的Filter
    if (filters != null && filters.size() != 0) {
        if (logger.isDebugEnabled()) {
            logger.debug(LogMessage.of(() -> {
                return "Securing " + requestLine(firewallRequest);
            }));
        }
				//这里创建一个虚拟的过滤链，过滤流程是由SpringSecurity自己实现的
        FilterChainProxy.VirtualFilterChain virtualFilterChain = new FilterChainProxy.VirtualFilterChain(firewallRequest, chain, filters);
      	//调用虚拟过滤链的doFilter
        virtualFilterChain.doFilter(firewallRequest, firewallResponse);
    } else {
        if (logger.isTraceEnabled()) {
            logger.trace(LogMessage.of(() -> {
                return "No security for " + requestLine(firewallRequest);
            }));
        }

        firewallRequest.reset();
        chain.doFilter(firewallRequest, firewallResponse);
    }
}
```

我们来看一下虚拟过滤链的doFilter是怎么处理的：

```java
//看似没有任何循环，实际上就是一个循环，是一个递归调用
public void doFilter(ServletRequest request, ServletResponse response) throws IOException, ServletException {
  	//判断是否已经通过全部的内置过滤器，定位是否等于当前大小
    if (this.currentPosition == this.size) {
        if (FilterChainProxy.logger.isDebugEnabled()) {
            FilterChainProxy.logger.debug(LogMessage.of(() -> {
                return "Secured " + FilterChainProxy.requestLine(this.firewalledRequest);
            }));
        }

        this.firewalledRequest.reset();
      	//所有的内置过滤器已经完成，按照正常流程走DelegatingFilterProxy的下一个Filter
      	//也就是说这里之后就与DelegatingFilterProxy没有任何关系了，该走其他过滤器就走其他地方配置的过滤器，SpringSecurity的过滤操作已经结束
        this.originalChain.doFilter(request, response);
    } else {
      	//定位自增
        ++this.currentPosition;
      	//获取当前定位的Filter
        Filter nextFilter = (Filter)this.additionalFilters.get(this.currentPosition - 1);
        if (FilterChainProxy.logger.isTraceEnabled()) {
            FilterChainProxy.logger.trace(LogMessage.format("Invoking %s (%d/%d)", nextFilter.getClass().getSimpleName(), this.currentPosition, this.size));
        }
				//执行内部过滤器的doFilter方法，传入当前对象本身作为Filter，执行如果成功，那么一定会再次调用当前对象的doFilter方法
      	//可能最不理解的就是这里，执行的难道不是内部其他Filter的doFilter方法吗，怎么会让当前对象的doFilter方法递归调用呢？
      	//没关系，下面我们接着了解了其中一个内部过滤器就明白了
        nextFilter.doFilter(request, response, this);
    }
}
```

因此，我们差不多已经了解了整个SpringSecurity的实现机制了，那么我们来随便看一个内部的过滤器在做什么。

比如用于处理登陆的过滤器`UsernamePasswordAuthenticationFilter`，它继承自`AbstractAuthenticationProcessingFilter`，我们来看看它是怎么进行过滤的：

```java
public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
    this.doFilter((HttpServletRequest)request, (HttpServletResponse)response, chain);
}

private void doFilter(HttpServletRequest request, HttpServletResponse response, FilterChain chain) throws IOException, ServletException {
  	//如果不是登陆请求，那么根本不会理这个请求
    if (!this.requiresAuthentication(request, response)) {
      	//直接调用传入的FilterChain的doFilter方法
      	//而这里传入的正好是VirtualFilterChain对象
      	//这下知道为什么上面说是递归了吧
        chain.doFilter(request, response);
    } else {
      	//如果是登陆请求，那么会执行登陆请求的相关逻辑，注意执行过程中出现任何问题都会抛出异常
      	//比如用户名和密码错误，我们之前也已经测试过了，会得到一个BadCredentialsException
        try {
          	//进行认证
            Authentication authenticationResult = this.attemptAuthentication(request, response);
            if (authenticationResult == null) {
                return;
            }

            this.sessionStrategy.onAuthentication(authenticationResult, request, response);
            if (this.continueChainBeforeSuccessfulAuthentication) {
                chain.doFilter(request, response);
            }

          	//如果一路绿灯，没有报错，那么验证成功，执行successfulAuthentication
            this.successfulAuthentication(request, response, chain, authenticationResult);
        } catch (InternalAuthenticationServiceException var5) {
            this.logger.error("An internal error occurred while trying to authenticate the user.", var5);
          	//验证失败，会执行unsuccessfulAuthentication
            this.unsuccessfulAuthentication(request, response, var5);
        } catch (AuthenticationException var6) {
            this.unsuccessfulAuthentication(request, response, var6);
        }

    }
}
```

那么我们来看看successfulAuthentication和unsuccessfulAuthentication分别做了什么：

```java
protected void successfulAuthentication(HttpServletRequest request, HttpServletResponse response, FilterChain chain, Authentication authResult) throws IOException, ServletException {
  	//向SecurityContextHolder添加认证信息，我们可以通过SecurityContextHolder对象获取当前登陆的用户
    SecurityContextHolder.getContext().setAuthentication(authResult);
    if (this.logger.isDebugEnabled()) {
        this.logger.debug(LogMessage.format("Set SecurityContextHolder to %s", authResult));
    }

  	//记住我实现
    this.rememberMeServices.loginSuccess(request, response, authResult);
    if (this.eventPublisher != null) {
        this.eventPublisher.publishEvent(new InteractiveAuthenticationSuccessEvent(authResult, this.getClass()));
    }
		
  	//调用默认的或是我们自己定义的AuthenticationSuccessHandler的onAuthenticationSuccess方法
  	//这个根据我们配置文件决定
  	//到这里其实页面就已经直接跳转了
    this.successHandler.onAuthenticationSuccess(request, response, authResult);
}

protected void unsuccessfulAuthentication(HttpServletRequest request, HttpServletResponse response, AuthenticationException failed) throws IOException, ServletException {
  	//登陆失败会直接清理掉SecurityContextHolder中的认证信息
    SecurityContextHolder.clearContext();
    this.logger.trace("Failed to process authentication request", failed);
    this.logger.trace("Cleared SecurityContextHolder");
    this.logger.trace("Handling authentication failure");
  	//登陆失败的记住我处理
    this.rememberMeServices.loginFail(request, response);
  	//同上，调用默认或是我们自己定义的AuthenticationFailureHandler
    this.failureHandler.onAuthenticationFailure(request, response, failed);
}
```

了解了整个用户验证实现流程，其实其它的过滤器是如何实现的也就很容易联想到了，SpringSecurity的过滤器从某种意义上来说，更像是一个处理业务的Servlet，它做的事情不像是拦截，更像是完成自己对应的职责，只不过是使用了过滤器机制进行实现罢了，从而将所有的验证提前到进入Controller之前。

最后附上完整的过滤器清单，这里列出14个常见的内部过滤器：

| 过滤器名称                              | 职责                                                         |
| --------------------------------------- | ------------------------------------------------------------ |
| DisableEncodeUrlFilter                  | 禁止 HttpServletResponse 对 URL 进行编码，以防止在 URL 中包含 Session ID，此类 URL 不被视为 URL，因为会话 ID 可能会在 HTTP 访问日志等内容中泄露。 |
| WebAsyncManagerIntegrationFilter        | 实现了对SecurityContext与WebAsyncManager的集成，使 Controller 中能够线程安全地获取到用户上下文认证信息。 |
| SecurityContextHolderFilter             | 通过HttpSessionSecurityContextRepository接口从Session中读取SecurityContext或是直接创建新的，然后存入到SecurityContextHolder中，最后请求结束时会进行清理。 |
| HeaderWriterFilter                      | 给HTTP响应添加一些Header属性，如：X-Frame-Options、X-XSS-Protection、X-Content-Type-Options等。 |
| CsrfFilter                              | 针对Csrf相关校验。                                           |
| LogoutFilter                            | 对退出登录的请求进行处理，执行登出操作。                     |
| UsernamePasswordAuthenticationFilter    | 对登录的请求进行处理，执行登录操作。                         |
| ConcurrentSessionFilter                 | 检查SessionRegistry保存的Session信息是否过期。               |
| RequestCacheAwareFilter                 | 缓存Request请求，可以用于恢复因登录而打断的请求。            |
| SecurityContextHolderAwareRequestFilter | 对ServletRequest进行进一步包装，让Request具有更加丰富的内容。 |
| RememberMeAuthenticationFilter          | 针对于记住我Cookie进行校验。                                 |
| AnonymousAuthenticationFilter           | 未验证成功的情况下进行匿名登录操作。                         |
| SessionManagementFilter                 | Session管理相关。                                            |
| ExceptionTranslationFilter              | 异常转换处理，比如最常见的AccessDenied之类的。               |

各位小伙伴感兴趣的话可以自行了解。

## 安全上下文

用户登录之后，怎么获取当前已经登录用户的信息呢？通过使用SecurityContextHolder就可以很方便地得到SecurityContext对象了，我们可以直接使用SecurityContext对象来获取当前的认证信息：

```java
@RequestMapping("/index")
    public String index(){
        SecurityContext context = SecurityContextHolder.getContext();
        Authentication authentication = context.getAuthentication();
        User user = (User) authentication.getPrincipal();
        System.out.println(user.getUsername());
        System.out.println(user.getAuthorities());
        return "index";
    }
```

通过SecurityContext我们就可以快速获取当前用户的名称和授权信息等：

![image-20230706215806040](https://s2.loli.net/2023/07/06/uPjdsgbhv9NqA8B.png)

除了这种方式以外，我们还可以直接从Session中获取：

```java
@RequestMapping("/index")
public String index(@SessionAttribute("SPRING_SECURITY_CONTEXT") SecurityContext context){
    Authentication authentication = context.getAuthentication();
    User user = (User) authentication.getPrincipal();
    System.out.println(user.getUsername());
    System.out.println(user.getAuthorities());
    return "index";
}
```

注意SecurityContextHolder是有一定的存储策略的，SecurityContextHolder中的SecurityContext对象会在一开始请求到来时被设定，至于存储方式其实是由存储策略决定的，如果我们这样编写，那么在默认情况下是无法获取到认证信息的：

```java
@RequestMapping("/index")
public String index(){
    new Thread(() -> {   //创建一个子线程去获取
        SecurityContext context = SecurityContextHolder.getContext();
        Authentication authentication = context.getAuthentication();
        User user = (User) authentication.getPrincipal();   //NPE
        System.out.println(user.getUsername());
        System.out.println(user.getAuthorities()); 
    }).start();
    return "index";
}
```

这是因为SecurityContextHolder的存储策略默认是`MODE_THREADLOCAL`，它是基于ThreadLocal实现的，`getContext()`方法本质上调用的是对应的存储策略实现的方法：

```java
public static SecurityContext getContext() {
    return strategy.getContext();
}
```

SecurityContextHolderStrategy有三个实现类：

* GlobalSecurityContextHolderStrategy：全局模式，不常用
* ThreadLocalSecurityContextHolderStrategy：基于ThreadLocal实现，线程内可见
* InheritableThreadLocalSecurityContextHolderStrategy：基于InheritableThreadLocal实现，线程和子线程可见

因此，如果上述情况需要在子线程中获取，那么需要修改SecurityContextHolder的存储策略，在初始化的时候设置：

```java
@PostConstruct
public void init(){
    SecurityContextHolder.setStrategyName(SecurityContextHolder.MODE_INHERITABLETHREADLOCAL);
}
```

这样在子线程中也可以获取认证信息了。

因为用户的验证信息是基于SecurityContext进行判断的，我们可以直接修改SecurityContext的内容，来手动为用户进行登陆：

```java
@RequestMapping("/auth")
@ResponseBody
public String auth(){
    SecurityContext context = SecurityContextHolder.getContext();  //获取SecurityContext对象（当前会话肯定是没有登陆的）
    UsernamePasswordAuthenticationToken token = new UsernamePasswordAuthenticationToken("Test", null,
            AuthorityUtils.commaSeparatedStringToAuthorityList("ROLE_user"));  //手动创建一个UsernamePasswordAuthenticationToken对象，也就是用户的认证信息，角色需要添加ROLE_前缀，权限直接写
    context.setAuthentication(token);  //手动为SecurityContext设定认证信息
    return "Login success！";
}
```

在未登陆的情况下，访问此地址将直接进行手动登陆，再次访问`/index`页面，可以直接访问，说明手动设置认证信息成功。

**疑惑：**SecurityContext这玩意不是默认线程独占吗，那每次请求都是一个新的线程，按理说上一次的SecurityContext对象应该没了才对啊，为什么再次请求依然能够继续使用上一次SecurityContext中的认证信息呢？

SecurityContext的生命周期：请求到来时从Session中取出，放入SecurityContextHolder中，请求结束时从SecurityContextHolder取出，并放到Session中，实际上就是依靠Session来存储的，一旦会话过期验证信息也跟着消失。

下一节我们将详细讨论它的实现过程。

## 安全上下文持久化过滤器

SecurityContextHolderFilter也是内置的Filter，它就是专门用于处理SecurityContext的，这里先说一下大致流程，以便我们后续更加方便地理解：

> 当过滤器链执行到SecurityContextHolderFilter时，它会从HttpSession中把SecurityContext对象取出来（是存在Session中的，跟随会话的消失而消失），然后放入SecurityContextHolder对象中。请求结束后，再把SecurityContext存入HttpSession中，并清除SecurityContextHolder内的SecurityContext对象。

直接进入到源码中：

```java
	@Override
	public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
			throws IOException, ServletException {
    //开始套娃
		doFilter((HttpServletRequest) request, (HttpServletResponse) response, chain);
	}

	private void doFilter(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
			throws ServletException, IOException {
    //防止重复的安全请求，不需要关心，一般是直接走下面
		if (request.getAttribute(FILTER_APPLIED) != null) {
			chain.doFilter(request, response);
			return;
		}
		request.setAttribute(FILTER_APPLIED, Boolean.TRUE);
    //这里通过SecurityContextRepository的loadDeferredContext获取到SecurityContext对象的Supplier
		Supplier<SecurityContext> deferredContext = this.securityContextRepository.loadDeferredContext(request);
		...
	}
```

我们接着来看`loadDeferredContext`的实现细节，其中SecurityContextRepository的实现类是DelegatingSecurityContextRepository类，这个类中维护了多个SecurityContextRepository实现类，而其本身并没有实现`loadDeferredContext`方法，而是靠内部维护的其他SecurityContextRepository实现类来完成：

```java
	@Override
	public DeferredSecurityContext loadDeferredContext(HttpServletRequest request) {
    //DeferredSecurityContext是一个支持延时生成的SecurityContext，本质是一个SecurityContext的Supplier
		DeferredSecurityContext deferredSecurityContext = null;
    //遍历内部维护的其他SecurityContextRepository实现，一般包含以下两个：
    //1. HttpSessionSecurityContextRepository
    //2. RequestAttributeSecurityContextRepository
		for (SecurityContextRepository delegate : this.delegates) {
      //这个if-else语句其实为了添加多个SecurityContextRepository提供的SecurityContext并将其组成一个链状结构的DelegatingDeferredSecurityContext（至于为什么，我们接着往下看）
			if (deferredSecurityContext == null) {
				deferredSecurityContext = delegate.loadDeferredContext(request);
			}
			else {
				DeferredSecurityContext next = delegate.loadDeferredContext(request);
				deferredSecurityContext = new DelegatingDeferredSecurityContext(deferredSecurityContext, next);
			}
		}
		return deferredSecurityContext;
	}
```

首先我们来看第一个HttpSessionSecurityContextRepository，它是第一个被遍历的实现：

```java
	@Override
	public DeferredSecurityContext loadDeferredContext(HttpServletRequest request) {
		Supplier<SecurityContext> supplier = () -> readSecurityContextFromSession(request.getSession(false));  //从Session中取出SecurityContext
		return new SupplierDeferredSecurityContext(supplier, this.securityContextHolderStrategy);
	}

	public static final String SPRING_SECURITY_CONTEXT_KEY = "SPRING_SECURITY_CONTEXT";
	private String springSecurityContextKey = SPRING_SECURITY_CONTEXT_KEY;

	private SecurityContext readSecurityContextFromSession(HttpSession httpSession) {
		...
    //实际上这里就是从Session中通过键“SPRING_SECURITY_CONTEXT”取出的SecurityContext
    //跟我们上一节使用的是完全一样的，这下就很清晰了
    //如果用户没有登录验证，那么这里获取到的SecurityContext就是null了
		Object contextFromSession = httpSession.getAttribute(this.springSecurityContextKey);
		...
		return (SecurityContext) contextFromSession;
	}
```

最后返回回去的是一个SupplierDeferredSecurityContext对象：

```java
final class SupplierDeferredSecurityContext implements DeferredSecurityContext {

	private static final Log logger = LogFactory.getLog(SupplierDeferredSecurityContext.class);

	private final Supplier<SecurityContext> supplier;

	private final SecurityContextHolderStrategy strategy;

	private SecurityContext securityContext;

	private boolean missingContext;

	SupplierDeferredSecurityContext(Supplier<SecurityContext> supplier, SecurityContextHolderStrategy strategy) {
		this.supplier = supplier;
		this.strategy = strategy;
	}

	@Override
	public SecurityContext get() {
    //在获取SecurityContext时会进行一次初始化
		init();
		return this.securityContext;
	}

	@Override
	public boolean isGenerated() {
		init();
    //初始化后判断是否为未登录的SecurityContext
		return this.missingContext;
	}

	private void init() {
    //如果securityContext不为null表示已经初始化过了
		if (this.securityContext != null) {
			return;
		}
		//直接通过supplier获取securityContext对象
		this.securityContext = this.supplier.get();
    //如果securityContext对象为null，那么就标记missingContext
		this.missingContext = (this.securityContext == null);
		if (this.missingContext) {
      //当missingContext为真时，说明没有securityContext（一般是未登录的情况）
      //那么就创建一个空的securityContext，不包含任何认证信息
			this.securityContext = this.strategy.createEmptyContext();
      //日志无视就好
			if (logger.isTraceEnabled()) {
				logger.trace(LogMessage.format("Created %s", this.securityContext));
			}
		}
	}

}
```

接着是第二个被遍历的实现RequestAttributeSecurityContextRepository类：

```java
	@Override
	public DeferredSecurityContext loadDeferredContext(HttpServletRequest request) {
		Supplier<SecurityContext> supplier = () -> getContext(request);
    //同样是返回SupplierDeferredSecurityContext对象
		return new SupplierDeferredSecurityContext(supplier, this.securityContextHolderStrategy);
	}

	private SecurityContext getContext(HttpServletRequest request) {
    //通过HttpServletRequest的Attribute获取SecurityContext
    //由于一般情况下没有设定过，因此得到的就是null
		return (SecurityContext) request.getAttribute(this.requestAttributeName);
	}
```

最后，两个SecurityContext就会以链式存放在DelegatingDeferredSecurityContext对象中，一并返回了，它的内部长这样：

```java
static final class DelegatingDeferredSecurityContext implements DeferredSecurityContext {

		private final DeferredSecurityContext previous;

		private final DeferredSecurityContext next;

		DelegatingDeferredSecurityContext(DeferredSecurityContext previous, DeferredSecurityContext next) {
			this.previous = previous;
			this.next = next;
		}

		@Override
		public SecurityContext get() {
      //在获取SecurityContext时，会首先从最前面的开始获取
			SecurityContext securityContext = this.previous.get();
      //如果最前面的SecurityContext是已登录的，那么直接返回这个SecurityContext
			if (!this.previous.isGenerated()) {
				return securityContext;
			}
      //否则继续看后面的，也许后面的会有已登录的（实在没有就直接返回一个空的SecurityContext了）
			return this.next.get();
		}

		@Override
		public boolean isGenerated() {
			return this.previous.isGenerated() && this.next.isGenerated();
		}
}
```

兜了这么大一圈，现在回到一开始的Filter中：

```java
	private void doFilter(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
			throws ServletException, IOException {
		...
    Supplier<SecurityContext> deferredContext = this.securityContextRepository.loadDeferredContext(request);
    //拿到最终的SecurityContext的Supplier后，继续下面的语句
		try {
      //向securityContextHolderStrategy中设置我们上面得到的DeferredSecurityContext
			this.securityContextHolderStrategy.setDeferredContext(deferredContext);
      //请求前的任务已完成，继续其他过滤器了
			chain.doFilter(request, response);
		}
		finally {
      //请求结束后，清理掉securityContextHolderStrategy中的DeferredSecurityContext
			this.securityContextHolderStrategy.clearContext();
			request.removeAttribute(FILTER_APPLIED);
		}
	}
```

最后我们再来看一下我们之前通过SecurityContextHolder是如何获取到SecurityContext的：

```java
public class SecurityContextHolder {
	...
  private static String strategyName = System.getProperty(SYSTEM_PROPERTY);
	private static SecurityContextHolderStrategy strategy;
	private static int initializeCount = 0;

	static {
    //类加载时会进行一次初始化
		initialize();
	}

	private static void initialize() {
    //初始化会将对应的SecurityContextHolderStrategy对象给创建
		initializeStrategy();
		initializeCount++;
	}

  //初始化SecurityContextHolderStrategy对象
	private static void initializeStrategy() {
		...
		// 尝试加载系统配置中设定的Strategy实现类，默认是MODE_THREADLOCAL
		try {
			Class<?> clazz = Class.forName(strategyName);
			Constructor<?> customStrategy = clazz.getConstructor();
      // 这里直接根据配置中的类名，用反射怒艹一个对象出来
			strategy = (SecurityContextHolderStrategy) customStrategy.newInstance();
		}
		catch (Exception ex) {
			ReflectionUtils.handleReflectionException(ex);
		}
	}

	//清除Context中的内容，实际上就是清理SecurityContextHolderStrategy中的内容
	public static void clearContext() {
		strategy.clearContext();
	}

	//获取SecurityContext对象
	public static SecurityContext getContext() {
    //获取SecurityContext实际上也是通过SecurityContextHolderStrategy根据策略来获取
		return strategy.getContext();
	}
	
  ...
}
```

我们发现，实际上SecurityContextHolder获取SecurityContext对象，就是通过SecurityContextHolderStrategy根据策略来获取，我们直接来看SecurityContextHolderStrategy的实现类：

```java
final class ThreadLocalSecurityContextHolderStrategy implements SecurityContextHolderStrategy {

  //内部维护一个ThreadLocal对象，按线程存储对应的DeferredSecurityContext
	private static final ThreadLocal<Supplier<SecurityContext>> contextHolder = new ThreadLocal<>();

	@Override
	public void clearContext() {
    //清理实际上是直接清理掉ThreadLocal中存的对象
		contextHolder.remove();
	}

	@Override
	public SecurityContext getContext() {
    //获取也很简单，直接通过Supplier拿到需要的SecurityContext对象
		return getDeferredContext().get();
	}

	@Override
	public Supplier<SecurityContext> getDeferredContext() {
		Supplier<SecurityContext> result = contextHolder.get();
    //如果存储的DeferredSecurityContext为null，这里临时创建一个空的SecurityContext并保存
		if (result == null) {
			SecurityContext context = createEmptyContext();
			result = () -> context;
			contextHolder.set(result);
		}
		return result;
	}

	...

}
```

这样，整个流程其实就很清楚了，项目启动时，SecurityContextHolder会自动根据配置创建对应的SecurityContextHolderStrategy对象。当我们的请求到来之后，首先会经过SecurityContextHolderFilter，然后在这个阶段，通过SecurityContextRepository来将不同地方存储（一般是Session中存储）的SecurityContext对象取出并封装为DefferdSecurityContext，然后将其添加到一开始创建好的SecurityContextHolderStrategy对象中，这样，我们的Controller在处理时就能直接从SecurityContextHolder取出SecurityContext对象了，最后在处理结束返回响应时，SecurityContextHolderFilter也会将SecurityContextHolderStrategy存储的DefferdSecurityContext清除掉，至此，一个完整流程结束。