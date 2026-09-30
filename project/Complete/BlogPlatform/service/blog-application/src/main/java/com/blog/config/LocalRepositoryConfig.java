package com.blog.config;

import com.blog.data.PostRepository;
import com.blog.data.TaxonomyRepository;
import com.blog.data.memory.InMemoryPostRepository;
import com.blog.data.memory.InMemoryTaxonomyRepository;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;

/**
 * 仓储实现的装配点。
 *
 * <p>数据层刻意不加 Spring 注解（保持框架无关），所以「用哪个实现」这件事只在装配层出现：
 * {@code local} 用内存实现，后续接入 JDBC/ORM 时在这里换 Bean，上层一行不改。
 *
 * <p>注意两个 Bean 的**装配顺序由参数依赖表达**：{@code postRepository} 显式声明需要
 * {@link TaxonomyRepository}，因为文章写入时要把 {@code categoryId}/{@code tagIds} 翻译成 slug。
 * 这里不写 {@code @DependsOn}——用构造参数表达依赖比注解更可读，也让编译期就能发现循环依赖。
 */
@Configuration
@Profile("local")
public class LocalRepositoryConfig {

    @Bean
    public TaxonomyRepository taxonomyRepository() {
        return new InMemoryTaxonomyRepository();
    }

    @Bean
    public PostRepository postRepository(TaxonomyRepository taxonomyRepository) {
        return new InMemoryPostRepository(taxonomyRepository);
    }
}
