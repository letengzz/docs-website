package com.blog.web.post;

import com.blog.common.api.ErrorCode;
import com.blog.common.api.Result;
import com.blog.common.exception.BizException;
import com.blog.data.Page;
import com.blog.data.PostRepository;
import com.blog.data.model.Post;
import com.blog.web.post.dto.PostDetailView;
import com.blog.web.post.dto.PostPageView;
import com.blog.web.post.dto.PostSummaryView;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * 读者端文章接口。
 *
 * <p>本类只做两件事：**把契约里的参数约束挡在入口**、**把领域对象映射成契约形状**。
 * 任何排序、过滤、分页计算都在数据层，Controller 里不该出现。
 */
@RestController
@RequestMapping("/api/v1/posts")
public class PostController {

    /** 契约里 size 的上限是 50，这里必须与契约一致，否则「契约通过、实现越界」。 */
    private static final int MAX_PAGE_SIZE = 50;

    private final PostRepository postRepository;

    public PostController(PostRepository postRepository) {
        this.postRepository = postRepository;
    }

    /** GET /api/v1/posts —— 已发布文章分页列表。 */
    @GetMapping
    public Result<PostPageView> list(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) String categorySlug,
            @RequestParam(required = false) String tagSlug) {

        if (page < 1 || size < 1 || size > MAX_PAGE_SIZE) {
            throw new BizException(ErrorCode.PARAM_PAGE_OUT_OF_RANGE);
        }

        Page<Post> paged = postRepository.findPublished(page, size, categorySlug, tagSlug);
        List<PostSummaryView> records = paged.records().stream().map(PostController::toSummary).toList();
        return Result.ok(new PostPageView(paged.total(), records));
    }

    /** GET /api/v1/posts/{slug} —— 文章详情；草稿与下线文章一律 404（不暴露存在性）。 */
    @GetMapping("/{slug}")
    public Result<PostDetailView> detail(@PathVariable String slug) {
        Post post = postRepository.findPublishedBySlug(slug)
                .orElseThrow(() -> new BizException(ErrorCode.RESOURCE_NOT_FOUND));
        return Result.ok(new PostDetailView(
                post.id(), post.slug(), post.title(), post.status(), post.categorySlug(),
                post.tagSlugs(), post.viewCount(), post.publishedAt(),
                post.authorNickname(), post.contentHtml()));
    }

    private static PostSummaryView toSummary(Post post) {
        return new PostSummaryView(
                post.id(), post.slug(), post.title(), post.status(), post.categorySlug(),
                post.tagSlugs(), post.viewCount(), post.publishedAt());
    }
}
