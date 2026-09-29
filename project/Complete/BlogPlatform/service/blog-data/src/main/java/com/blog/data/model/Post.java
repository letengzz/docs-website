package com.blog.data.model;

import java.time.Instant;
import java.util.List;

/**
 * 文章领域对象（数据层内部形态）。
 *
 * <p>注意它**不等于**读者端契约里的 {@code PostDetail}：此处带 {@code contentMd}，
 * 而读者端不暴露原始 Markdown。领域对象与对外形状分开，才是「契约不变、内部随便改」的前提。
 */
public record Post(
        long id,
        String slug,
        String title,
        String status,
        String categorySlug,
        List<String> tagSlugs,
        long viewCount,
        Instant publishedAt,
        String authorNickname,
        String contentMd,
        String contentHtml) {

    public boolean published() {
        return "PUBLISHED".equals(status) && publishedAt != null;
    }
}
