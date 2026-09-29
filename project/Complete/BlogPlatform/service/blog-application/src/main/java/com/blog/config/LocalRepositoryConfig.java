package com.blog.config;

import com.blog.data.PostRepository;
import com.blog.data.memory.InMemoryPostRepository;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;

/**
 * 仓储实现的装配点。
 *
 * <p>数据层刻意不加 Spring 注解（保持框架无关），所以「用哪个实现」这件事只在装配层出现：
 * {@code local} 用内存实现，后续接入 JDBC/ORM 时在这里换 Bean，上层一行不改。
 */
@Configuration
@Profile("local")
public class LocalRepositoryConfig {

    @Bean
    public PostRepository postRepository() {
        return new InMemoryPostRepository();
    }
}
