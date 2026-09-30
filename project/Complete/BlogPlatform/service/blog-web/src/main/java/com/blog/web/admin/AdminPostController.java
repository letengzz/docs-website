package com.blog.web.admin;

import com.blog.common.api.ErrorCode;
import com.blog.common.api.Result;
import com.blog.common.exception.BizException;
import com.blog.data.PostRepository;
import com.blog.data.PostWrite;
import com.blog.data.TaxonomyRepository;
import com.blog.data.model.Post;
import com.blog.data.model.PostStatus;
import com.blog.web.admin.dto.PostUpsertRequest;
import com.blog.web.post.dto.PostSummaryView;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * 管理端文章写接口：创建草稿、更新、软删除、发布。
 *
 * <p>这一层的三项纪律：
 * <ol>
 *   <li><b>状态只能由状态机动作改变</b>：创建与更新一律不碰 status，发布是唯一的「转 PUBLISHED」入口。
 *       把 status 放进 upsert 是状态机失控的起点——前端随手传一个 PUBLISHED 就绕过了所有校验。</li>
 *   <li><b>引用的字典项必须在入口校验</b>：categoryId / tagIds 不存在时直接 400，
 *       而不是让它落到数据层变成一个 null 分类（那会变成「创建成功但前台按分类查不到」的幽灵数据）。</li>
 *   <li><b>slug 冲突统一 409</b>：更新时用「排除自己」的判断，否则作者不改 slug 也会撞上自己。</li>
 * </ol>
 *
 * <p>尚未接入的部分：契约里声明的 401 / 403 分支依赖认证与角色（第 2 周后续步骤），
 * 当前实现覆盖 200 / 400 / 404 / 409 四类。
 */
@RestController
@RequestMapping("/api/v1/admin/posts")
public class AdminPostController {

    private final PostRepository posts;
    private final TaxonomyRepository taxonomy;

    public AdminPostController(PostRepository posts, TaxonomyRepository taxonomy) {
        this.posts = posts;
        this.taxonomy = taxonomy;
    }

    /** POST /api/v1/admin/posts —— 创建草稿，返回摘要。 */
    @PostMapping
    public Result<PostSummaryView> create(@Valid @RequestBody PostUpsertRequest req) {
        validateReferences(req);
        if (posts.existsSlug(req.slug())) {
            throw new BizException(ErrorCode.RESOURCE_CONFLICT);
        }
        return Result.ok(toSummary(posts.insert(toWrite(req))));
    }

    /** PUT /api/v1/admin/posts/{id} —— 更新标题、slug、归属与正文（不影响状态与发布时间）。 */
    @PutMapping("/{id}")
    public Result<PostSummaryView> update(@PathVariable long id,
                                         @Valid @RequestBody PostUpsertRequest req) {
        requireAlive(id);
        validateReferences(req);
        if (posts.existsSlugExcept(req.slug(), id)) {
            throw new BizException(ErrorCode.RESOURCE_CONFLICT);
        }
        Post updated = posts.update(id, toWrite(req))
                .orElseThrow(() -> new BizException(ErrorCode.RESOURCE_NOT_FOUND));
        return Result.ok(toSummary(updated));
    }

    /** DELETE /api/v1/admin/posts/{id} —— 软删除（重复删除返回 404，不做「幂等成功」）。 */
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable long id) {
        requireAlive(id);
        posts.softDelete(id);
        return Result.ok();
    }

    /**
     * POST /api/v1/admin/posts/{id}/publish —— 发布。
     *
     * <p>状态机是 **DRAFT → PUBLISHED**：已经是 PUBLISHED 或 OFFLINE 的文章都返回 409，
     * 而不是「重复发布也返回成功」。契约里写明这一条，是因为**幂等的假象会掩盖状态错乱**：
     * 如果重复发布返回 200，调用方就永远发现不了自己手里是一份过期状态。
     */
    @PostMapping("/{id}/publish")
    public Result<PostSummaryView> publish(@PathVariable long id) {
        Post current = requireAlive(id);
        if (!PostStatus.DRAFT.equals(current.status())) {
            throw new BizException(ErrorCode.STATE_CONFLICT);
        }
        Post published = posts.publish(id)
                .orElseThrow(() -> new BizException(ErrorCode.RESOURCE_NOT_FOUND));
        return Result.ok(toSummary(published));
    }

    // ------------------------------------------------------------ 内部

    /** 软删除过的文章对所有接口一律按「不存在」处理：否则会产生「删了还能改」的错觉。 */
    private Post requireAlive(long id) {
        return posts.findById(id)
                .filter(p -> !PostStatus.DELETED.equals(p.status()))
                .orElseThrow(() -> new BizException(ErrorCode.RESOURCE_NOT_FOUND));
    }

    private void validateReferences(PostUpsertRequest req) {
        if (taxonomy.findCategory(req.categoryId()).isEmpty()) {
            throw new BizException(ErrorCode.PARAM_INVALID, "categoryId 不存在：" + req.categoryId());
        }
        List<Long> distinct = req.tagIds() == null
                ? List.of()
                : req.tagIds().stream().distinct().toList();
        if (taxonomy.findTags(distinct).size() != distinct.size()) {
            throw new BizException(ErrorCode.PARAM_INVALID, "tagIds 存在无效值");
        }
    }

    private PostWrite toWrite(PostUpsertRequest req) {
        return new PostWrite(req.title(), req.slug(), req.categoryId(),
                req.tagIds() == null ? List.of() : req.tagIds(), req.contentMd());
    }

    private static PostSummaryView toSummary(Post post) {
        return new PostSummaryView(post.id(), post.slug(), post.title(), post.status(),
                post.categorySlug(), post.tagSlugs(), post.viewCount(), post.publishedAt());
    }
}
