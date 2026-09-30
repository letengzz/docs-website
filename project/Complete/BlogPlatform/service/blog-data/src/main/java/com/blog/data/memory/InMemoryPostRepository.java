package com.blog.data.memory;

import com.blog.common.text.MarkdownRenderer;
import com.blog.data.Page;
import com.blog.data.PostRepository;
import com.blog.data.PostWrite;
import com.blog.data.TaxonomyRepository;
import com.blog.data.model.Category;
import com.blog.data.model.Post;
import com.blog.data.model.PostStatus;
import com.blog.data.model.Tag;

import java.time.Clock;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicLong;

/**
 * 本地内存实现：让「契约 → 实现 → 契约测试」这条闭环**不依赖数据库**就能跑通。
 *
 * <p>刻意不加任何 Spring 注解——数据层保持框架无关，Bean 的注册放在
 * {@code blog-application} 的配置类里。这样换实现（内存 → JDBC → ORM）不会牵动上层。
 *
 * <p>三个实现细节值得留意：
 * <ol>
 *   <li><b>分类/标签 id → slug 的翻译在这里发生</b>：文章表存的是 slug（读者端要用于 URL），
 *       但后台传的是 id，翻译必须只有一处。</li>
 *   <li><b>注入 {@link Clock}</b>：发布时间的取时被收进一个可替换的入口，
 *       写测试时不用 sleep 也不需要「时间偏移」之类的技巧。</li>
 *   <li><b>软删除置为 {@link PostStatus#DELETED}</b>：读者端查已发布、后台端查未删除，两条查询各自过滤，
 *       避免「忘了一个地方没过滤」导致草稿或已删文章漏出去。</li>
 * </ol>
 */
public class InMemoryPostRepository implements PostRepository {

    private final List<Post> posts = new ArrayList<>();
    private final AtomicLong idSeq = new AtomicLong(9100);
    private final TaxonomyRepository taxonomy;
    private final Clock clock;

    public InMemoryPostRepository(TaxonomyRepository taxonomy) {
        this(taxonomy, Clock.systemUTC());
    }

    public InMemoryPostRepository(TaxonomyRepository taxonomy, Clock clock) {
        this.taxonomy = taxonomy;
        this.clock = clock;
        seed();
    }

    private void seed() {
        Instant base = Instant.parse("2026-09-01T08:00:00Z");
        posts.add(new Post(9001L, "hello-blog", "从零搭建一个博客平台", PostStatus.PUBLISHED,
                "engineering", List.of("java", "spring-boot"), 128L,
                base.plus(2, ChronoUnit.DAYS), "站长",
                "# 从零搭建\n\n第一篇：骨架与契约先行。",
                "<h1>从零搭建</h1><p>第一篇：骨架与契约先行。</p>"));
        posts.add(new Post(9002L, "mysql-ngram-search", "中文搜索先用 MySQL ngram", PostStatus.PUBLISHED,
                "database", List.of("mysql", "search"), 76L,
                base.plus(5, ChronoUnit.DAYS), "站长",
                "# 中文搜索\n\n先打通链路，再考虑换引擎。",
                "<h1>中文搜索</h1><p>先打通链路，再考虑换引擎。</p>"));
        posts.add(new Post(9003L, "nuxt-ssr-notes", "SEO 是博客的生命线", PostStatus.PUBLISHED,
                "frontend", List.of("nuxt"), 41L,
                base.plus(9, ChronoUnit.DAYS), "站长",
                "# SEO\n\n纯 CSR 不合格。",
                "<h1>SEO</h1><p>纯 CSR 不合格。</p>"));
        // 一条草稿：用来验证「读者端一律不可见」
        posts.add(new Post(9004L, "draft-post", "还没写完的草稿", PostStatus.DRAFT,
                "engineering", List.of(), 0L,
                null, "站长", "# 草稿", "<h1>草稿</h1>"));
    }

    // ------------------------------------------------------------ 读者端

    @Override
    public synchronized Page<Post> findPublished(int page, int size, String categorySlug, String tagSlug) {
        List<Post> matched = posts.stream()
                .filter(Post::published)
                .filter(p -> categorySlug == null || categorySlug.equals(p.categorySlug()))
                .filter(p -> tagSlug == null || p.tagSlugs().contains(tagSlug))
                .sorted(Comparator.comparing(Post::publishedAt).reversed())
                .toList();
        return Page.of(matched.size(), slice(matched, page, size));
    }

    @Override
    public synchronized Optional<Post> findPublishedBySlug(String slug) {
        return posts.stream()
                .filter(Post::published)
                .filter(p -> p.slug().equals(slug))
                .findFirst();
    }

    // ------------------------------------------------------------ 后台端

    @Override
    public synchronized Optional<Post> findById(long id) {
        return posts.stream().filter(p -> p.id() == id).findFirst();
    }

    @Override
    public synchronized Page<Post> findForAdmin(int page, int size) {
        List<Post> visible = posts.stream()
                .filter(p -> !PostStatus.DELETED.equals(p.status()))
                .sorted(Comparator.comparing(Post::id).reversed())
                .toList();
        return Page.of(visible.size(), slice(visible, page, size));
    }

    @Override
    public synchronized boolean existsSlug(String slug) {
        return posts.stream().anyMatch(p -> p.slug().equals(slug));
    }

    @Override
    public synchronized boolean existsSlugExcept(String slug, long id) {
        return posts.stream().anyMatch(p -> p.slug().equals(slug) && p.id() != id);
    }

    @Override
    public synchronized Post insert(PostWrite write) {
        Post created = new Post(idSeq.incrementAndGet(), write.slug(), write.title(), PostStatus.DRAFT,
                categorySlugOf(write.categoryId()), tagSlugsOf(write.tagIds()), 0L,
                null, "站长", write.contentMd(), null);
        posts.add(created);
        return created;
    }

    @Override
    public synchronized Optional<Post> update(long id, PostWrite write) {
        for (int i = 0; i < posts.size(); i++) {
            Post old = posts.get(i);
            if (old.id() != id) {
                continue;
            }
            // 状态与发布时间保持原值：更新内容不该让一篇文章「重新发布」或被退回草稿。
            // 但 contentHtml 必须跟着 contentMd 重算 —— 它是正文的派生物，
            // 已发布文章改了 contentMd 却沿用旧 HTML，读者端就会一直看到上一版内容。
            String html = PostStatus.PUBLISHED.equals(old.status())
                    ? MarkdownRenderer.toSafeHtml(write.contentMd())
                    : old.contentHtml();
            Post updated = new Post(old.id(), write.slug(), write.title(), old.status(),
                    categorySlugOf(write.categoryId()), tagSlugsOf(write.tagIds()), old.viewCount(),
                    old.publishedAt(), old.authorNickname(), write.contentMd(), html);
            posts.set(i, updated);
            return Optional.of(updated);
        }
        return Optional.empty();
    }

    @Override
    public synchronized boolean softDelete(long id) {
        for (int i = 0; i < posts.size(); i++) {
            Post old = posts.get(i);
            if (old.id() == id) {
                posts.set(i, new Post(old.id(), old.slug(), old.title(), PostStatus.DELETED,
                        old.categorySlug(), old.tagSlugs(), old.viewCount(),
                        // publishedAt 清空：软删除后的文章即便有人绕过状态判断，也不会被 published() 放行
                        null, old.authorNickname(), old.contentMd(), old.contentHtml()));
                return true;
            }
        }
        return false;
    }

    @Override
    public synchronized Optional<Post> publish(long id) {
        for (int i = 0; i < posts.size(); i++) {
            Post old = posts.get(i);
            if (old.id() == id) {
                Post published = new Post(old.id(), old.slug(), old.title(), PostStatus.PUBLISHED,
                        old.categorySlug(), old.tagSlugs(), old.viewCount(),
                        clock.instant(), old.authorNickname(), old.contentMd(),
                        MarkdownRenderer.toSafeHtml(old.contentMd()));
                posts.set(i, published);
                return Optional.of(published);
            }
        }
        return Optional.empty();
    }

    // ------------------------------------------------------------ 内部

    private List<Post> slice(List<Post> source, int page, int size) {
        int from = Math.min((page - 1) * size, source.size());
        int to = Math.min(from + size, source.size());
        return List.copyOf(source.subList(from, to));
    }

    private String categorySlugOf(long categoryId) {
        return taxonomy.findCategory(categoryId).map(Category::slug).orElse(null);
    }

    private List<String> tagSlugsOf(List<Long> tagIds) {
        return taxonomy.findTags(tagIds).stream().map(Tag::slug).toList();
    }
}
