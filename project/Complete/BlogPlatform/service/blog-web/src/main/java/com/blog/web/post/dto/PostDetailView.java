package com.blog.web.post.dto;

import java.time.Instant;
import java.util.List;

/**
 * 读者端文章详情 —— 契约 {@code PostDetail} = {@code PostSummary} 全部字段 + 作者昵称 + 渲染后 HTML。
 *
 * <p>**{@code contentMd} 不在这里**：原始 Markdown 不出读者端，这是契约里写死的边界，
 * 也是「以后要换渲染管线不必改契约」的前提。
 */
public record PostDetailView(
        long id,
        String slug,
        String title,
        String status,
        String categorySlug,
        List<String> tagSlugs,
        long viewCount,
        Instant publishedAt,
        String authorNickname,
        String contentHtml) {
}
