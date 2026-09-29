package com.blog;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 唯一可启动模块的入口。
 *
 * <p>四个模块里只有它有 {@code main}：其余三个都是被依赖的库。
 * 「谁可以启动」在多模块工程里必须唯一，否则同一段代码会出现两套启动路径。
 */
@SpringBootApplication(scanBasePackages = "com.blog")
public class BlogApplication {

    public static void main(String[] args) {
        SpringApplication.run(BlogApplication.class, args);
    }
}
