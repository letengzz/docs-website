package com.blog.data;

import com.blog.data.model.Category;
import com.blog.data.model.Tag;

import java.util.List;
import java.util.Optional;

/**
 * 分类与标签的字典仓储。
 *
 * <p>它同时承担两个职责，且**必须分清**：
 * <ul>
 *   <li>读者端读：{@link #listCategories()} / {@link #listTags()}，返回契约里的全量列表；</li>
 *   <li>写入端解析：把 {@code PostUpsert.categoryId} / {@code tagIds} 解析成 slug 写进文章。</li>
 * </ul>
 * 契约里「写入用 id、读出用 slug」是刻意的：**id 是内部主键，不该出现在 URL 与 SEO 里**；
 * 而写入方（后台）拿到的是下拉框的 id。两者的翻译只发生在这一个地方。
 */
public interface TaxonomyRepository {

    List<Category> listCategories();

    List<Tag> listTags();

    Optional<Category> findCategory(long id);

    /** 按 id 批量查标签；不存在的 id 被丢弃（是否存在由调用方在入口校验并报 400）。 */
    List<Tag> findTags(List<Long> ids);

    boolean existsCategorySlug(String slug);

    boolean existsTagSlug(String slug);

    boolean existsCategoryName(String name);

    boolean existsTagName(String name);

    Category insertCategory(String name, String slug);

    Tag insertTag(String name, String slug);
}
