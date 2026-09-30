package com.blog.data.memory;

import com.blog.data.TaxonomyRepository;
import com.blog.data.model.Category;
import com.blog.data.model.Tag;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicLong;

/**
 * 分类与标签的内存实现。
 *
 * <p>种子数据与 {@code InMemoryPostRepository} 里三条示例文章的 category / tags **必须对齐**
 * ——本地跑通「列表按分类过滤」这条链路时，靠的就是这两份数据能对上。
 */
public class InMemoryTaxonomyRepository implements TaxonomyRepository {

    private final List<Category> categories = new ArrayList<>();
    private final List<Tag> tags = new ArrayList<>();
    private final AtomicLong categorySeq = new AtomicLong(1000);
    private final AtomicLong tagSeq = new AtomicLong(2000);

    public InMemoryTaxonomyRepository() {
        categories.add(new Category(1L, "工程实践", "engineering"));
        categories.add(new Category(2L, "数据库", "database"));
        categories.add(new Category(3L, "前端", "frontend"));

        tags.add(new Tag(11L, "Java", "java"));
        tags.add(new Tag(12L, "Spring Boot", "spring-boot"));
        tags.add(new Tag(13L, "MySQL", "mysql"));
        tags.add(new Tag(14L, "搜索", "search"));
        tags.add(new Tag(15L, "Nuxt", "nuxt"));
    }

    @Override
    public List<Category> listCategories() {
        return List.copyOf(categories);
    }

    @Override
    public List<Tag> listTags() {
        return List.copyOf(tags);
    }

    @Override
    public Optional<Category> findCategory(long id) {
        return categories.stream().filter(c -> c.id() == id).findFirst();
    }

    @Override
    public List<Tag> findTags(List<Long> ids) {
        if (ids == null || ids.isEmpty()) {
            return List.of();
        }
        return tags.stream().filter(t -> ids.contains(t.id())).toList();
    }

    @Override
    public boolean existsCategorySlug(String slug) {
        return categories.stream().anyMatch(c -> c.slug().equals(slug));
    }

    @Override
    public boolean existsTagSlug(String slug) {
        return tags.stream().anyMatch(t -> t.slug().equals(slug));
    }

    @Override
    public boolean existsCategoryName(String name) {
        return categories.stream().anyMatch(c -> c.name().equals(name));
    }

    @Override
    public boolean existsTagName(String name) {
        return tags.stream().anyMatch(t -> t.name().equals(name));
    }

    @Override
    public Category insertCategory(String name, String slug) {
        Category created = new Category(categorySeq.incrementAndGet(), name, slug);
        categories.add(created);
        return created;
    }

    @Override
    public Tag insertTag(String name, String slug) {
        Tag created = new Tag(tagSeq.incrementAndGet(), name, slug);
        tags.add(created);
        return created;
    }
}
