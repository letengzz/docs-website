# JWT

JWT (`JSON Web Token`)即JSON Web令牌，是一种**自包含令牌**。 是为了在网络应用环境间传递声明而执行的一种基于JSON的开放标准。

JWT的声明一般被用来在身份提供者和服务提供者间传递被认证的用户身份信息，以便于从资源服务器获取资源。比如用在用户登录上。

JWT最重要的作用就是对 token信息的防伪作用。

**官方网站**：https://jwt.io/

## JWT令牌组成

一个JWT由三个部分组成：**JWT头、有效载荷、签名哈希**，最后由这三者组合进行base64url编码得到JWT

JWT为一个很长的字符串，字符之间通过"`.`"分隔符分为三个子串。

![image-20220606162842454](assets/image-20220606162842454.png)

### JWT头

JWT头部分是一个描述JWT元数据的JSON对象。

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

- alg属性：表示签名使用的算法，默认为`HMAC SHA256` (写为HS256)

- typ属性：表示令牌的类型，JWT令牌统一写为JWT

最后，使用Base64 URL算法将上述JSON对象转换为字符串保存。

### 有效载荷

有效载荷部分，是JWT的主体内容部分，也是一个JSON对象，包含需要传递的数据。 JWT指定七个默认字段供选择：

- iss：jwt签发者
- sub：主题
- aud：接收jwt的一方
- exp：jwt的过期时间，这个过期时间必须要大于签发时间
- nbf：定义在什么时间之前，该jwt都是不可用的.
- iat：jwt的签发时间
- jti：jwt的唯一身份标识，主要用来作为一次性token,从而回避重放攻击。

除以上默认字段外，还可以自定义私有字段：

```json
{
  "name": "Helen",
  "role": "editor",
  "avatar": "helen.jpg"
}
```

**注意**：默认情况下JWT是未加密的，任何人都可以解读其内容，因此不要构建隐私信息字段，存放保密信息，以防止信息泄露。

JSON对象也使用Base64 URL算法转换为字符串保存。

### 签名哈希

签名哈希部分是对上面两部分数据签名，通过指定的算法生成哈希，以确保数据不会被篡改。

首先，需要指定一个密码(secret)。该密码仅仅为保存在服务器中，并且不能向用户公开。然后，使用标头中指定的签名算法 (默认情况下为HMAC SHA256) 根据以下公式生成签名。

> HMACSHA256(base64UrlEncode(header) + "." + base64UrlEncode(claims), secret) ==> 签名hash

在计算出签名哈希后，JWT头，有效载荷和签名哈希的三个部分组合成一个字符串，每个部分用"`.`"分隔，就构成整个JWT对象。

## Base64URL算法

JWT头和有效载荷序列化的算法都用到了Base64URL。该算法和常见Base64算法类似，稍有差别。

作为令牌的JWT可以放在URL中（例如api.example/?token=xxx）。 Base64中用的三个字符是"`+`"，"`/`"和"`=`"，由于在URL中有特殊含义，因此Base64URL中对他们做了替换："`=`"去掉，"`+`"用"`-`"替换，"`/`"用"`_`"替换，这就是Base64URL算法。

# 用户登录方式

### HttpSession

缺陷：

session无法实现共享

### token共享

每次登录，登录成功之后，返回生成token字符串。

前端把返回token放到Cookie里面(Cookie不能跨越传递)

每次发送请求携带这个token发送(把token值放到请求头)

## 创建Token

subject 组名

setExpiration过期时间

claim 有效载荷

signWith 加密

compressWith 压缩

```java
private static long tokenExpiration = 365 * 24 * 60 * 60 * 1000;
private static String tokenSignKey = "123456";

public static String createToken(String userId, String username) {
    return Jwts.builder()
            .setSubject("AUTH-USER")
            .setExpiration(new Date(System.currentTimeMillis() + tokenExpiration))
            .claim("userId", userId)
            .claim("username", username)
            .signWith(SignatureAlgorithm.HS512, tokenSignKey)
            .compressWith(CompressionCodecs.GZIP)
            .compact();
}
```

## 获取Token数据

```java
Jws<Claims> claimsJws = Jwts.parser().setSigningKey(tokenSignKey).parseClaimsJws(token);
Claims claims = claimsJws.getBody();
return (String) claims.get("username");
```

```xml
<!-- 添加jwt的依赖 -->
<dependency>
    <groupId>com.auth0</groupId>
    <artifactId>java-jwt</artifactId>
    <version>3.11.0</version>
</dependency>
```
