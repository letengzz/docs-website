package com.blog.web.taxonomy;

import com.blog.common.api.Result;
import com.blog.data.TaxonomyRepository;
import com.blog.web.post.dto.CategoryView;
import com.blog.web.post.dto.TagView;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * 分类与标签的读者端接口。
 *
 * <p>这两个接口看起来「只是把字典全量返回」，但它们是前台导航的**数据来源**：
 * 分类与标签页需要 slug 做路由（SEO 要求 URL 稳定），所以返回的是 {@code name + slug} 而不是 id。
 */
@RestController
@RequestMapping("/api/v1")
public class TaxonomyController {

    private final TaxonomyRepository taxonomy;

    public TaxonomyController(TaxonomyRepository taxonomy) {
        this.taxonomy = taxonomy;
    }

    /** GET /api/v1/categories —— 全部分类。 */
    @GetMapping("/categories")
    public Result<List<CategoryView>> categories() {
        return Result.ok(taxonomy.listCategories().stream()
                .map(c -> new CategoryView(c.id(), c.name(), c.slug()))
                .toList());
    }

    /** GET /api/v1/tags —— 全部标签。 */
    @GetMapping("/tags")
    public Result<List<TagView>> tags() {
        return Result.ok(taxonomy.listTags().stream()
                .map(t -> new TagView(t.id(), t.name(), t.slug()))
                .toList());
    }
}
