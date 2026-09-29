package com.blog.web.post.dto;

import java.time.Instant;
import java.util.List;

/**
 * 读者端文章摘要 —— 字段与契约 {@code PostSummary} 一一对应。
 *
 * <p>{@code status} 保留为字符串而不用枚举：契约里它是 enum，但读者端目前只会看到
 * {@code PUBLISHED}；用字符串可避免「内部枚举一改，对外契约跟着变」。
 */
public record PostSummaryView(
        long id,
        String slug,
        String title,
        String status,
        String categorySlug,
        List<String> tagSlugs,
        long viewCount,
        Instant publishedAt) {
}
