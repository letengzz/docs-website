package com.blog.web.admin;

import com.blog.common.api.ErrorCode;
import com.blog.common.api.Result;
import com.blog.common.exception.BizException;
import com.blog.data.TaxonomyRepository;
import com.blog.data.model.Category;
import com.blog.data.model.Tag;
import com.blog.web.admin.dto.TaxonomyUpsertRequest;
import com.blog.web.post.dto.CategoryView;
import com.blog.web.post.dto.TagView;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 分类与标签的后台写接口。
 *
 * <p>唯一性冲突**同时判 name 与 slug**：契约里写明 409 的语义是「name 或 slug 冲突」。
 * 只判 slug 会让「名字重复但 slug 不同」的分类悄悄建出来，前台导航随即出现两个同名入口。
 */
@RestController
@RequestMapping("/api/v1/admin")
public class AdminTaxonomyController {

    private final TaxonomyRepository taxonomy;

    public AdminTaxonomyController(TaxonomyRepository taxonomy) {
        this.taxonomy = taxonomy;
    }

    /** POST /api/v1/admin/categories —— 创建分类。 */
    @PostMapping("/categories")
    public Result<CategoryView> createCategory(@Valid @RequestBody TaxonomyUpsertRequest req) {
        if (taxonomy.existsCategoryName(req.name())) {
            throw new BizException(ErrorCode.RESOURCE_CONFLICT);
        }
        if (taxonomy.existsCategorySlug(req.slug())) {
            throw new BizException(ErrorCode.RESOURCE_CONFLICT);
        }
        Category created = taxonomy.insertCategory(req.name(), req.slug());
        return Result.ok(new CategoryView(created.id(), created.name(), created.slug()));
    }

    /** POST /api/v1/admin/tags —— 创建标签。 */
    @PostMapping("/tags")
    public Result<TagView> createTag(@Valid @RequestBody TaxonomyUpsertRequest req) {
        if (taxonomy.existsTagName(req.name())) {
            throw new BizException(ErrorCode.RESOURCE_CONFLICT);
        }
        if (taxonomy.existsTagSlug(req.slug())) {
            throw new BizException(ErrorCode.RESOURCE_CONFLICT);
        }
        Tag created = taxonomy.insertTag(req.name(), req.slug());
        return Result.ok(new TagView(created.id(), created.name(), created.slug()));
    }
}
