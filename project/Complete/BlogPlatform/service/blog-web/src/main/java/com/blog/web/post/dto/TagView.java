package com.blog.web.post.dto;

/** 标签视图：与契约 {@code Tag} 一一对应。 */
public record TagView(long id, String name, String slug) {
}
