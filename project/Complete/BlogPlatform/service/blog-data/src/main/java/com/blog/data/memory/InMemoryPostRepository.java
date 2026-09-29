package com.blog.data.memory;

import com.blog.data.Page;
import com.blog.data.PostRepository;
import com.blog.data.model.Post;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;

/**
 * 本地内存实现：让「契约 → 实现 → 契约测试」这条闭环**不依赖数据库**就能跑通。
 *
 * <p>刻意不加任何 Spring 注解——数据层保持框架无关，Bean 的注册放在
 * {@code blog-application} 的配置类里。这样换实现（内存 → JDBC → ORM）不会牵动上层。
 */
public class InMemoryPostRepository implements PostRepository {

    private final List<Post> posts = new ArrayList<>();

    public InMemoryPostRepository() {
        Instant base = Instant.parse("2026-09-01T08:00:00Z");
        posts.add(new Post(9001L, "hello-blog", "从零搭建一个博客平台", "PUBLISHED",
                "engineering", List.of("java", "spring-boot"), 128L,
                base.plus(2, ChronoUnit.DAYS), "站长",
                "# 从零搭建\n\n第一篇：骨架与契约先行。",
                "<h1>从零搭建</h1><p>第一篇：骨架与契约先行。</p>"));
        posts.add(new Post(9002L, "mysql-ngram-search", "中文搜索先用 MySQL ngram", "PUBLISHED",
                "database", List.of("mysql", "search"), 76L,
                base.plus(5, ChronoUnit.DAYS), "站长",
                "# 中文搜索\n\n先打通链路，再考虑换引擎。",
                "<h1>中文搜索</h1><p>先打通链路，再考虑换引擎。</p>"));
        posts.add(new Post(9003L, "nuxt-ssr-notes", "SEO 是博客的生命线", "PUBLISHED",
                "frontend", List.of("nuxt"), 41L,
                base.plus(9, ChronoUnit.DAYS), "站长",
                "# SEO\n\n纯 CSR 不合格。",
                "<h1>SEO</h1><p>纯 CSR 不合格。</p>"));
        // 一条草稿：用来验证「读者端一律不可见」
        posts.add(new Post(9004L, "draft-post", "还没写完的草稿", "DRAFT",
                "engineering", List.of(), 0L,
                null, "站长", "# 草稿", "<h1>草稿</h1>"));
    }

    @Override
    public Page<Post> findPublished(int page, int size, String categorySlug, String tagSlug) {
        List<Post> matched = posts.stream()
                .filter(Post::published)
                .filter(p -> categorySlug == null || categorySlug.equals(p.categorySlug()))
                .filter(p -> tagSlug == null || p.tagSlugs().contains(tagSlug))
                .sorted(Comparator.comparing(Post::publishedAt).reversed())
                .toList();

        int from = Math.min((page - 1) * size, matched.size());
        int to = Math.min(from + size, matched.size());
        return Page.of(matched.size(), matched.subList(from, to));
    }

    @Override
    public Optional<Post> findPublishedBySlug(String slug) {
        return posts.stream()
                .filter(Post::published)
                .filter(p -> p.slug().equals(slug))
                .findFirst();
    }
}
