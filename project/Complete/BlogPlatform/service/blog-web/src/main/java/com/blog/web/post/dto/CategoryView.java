package com.blog.web.post.dto;

/** 分类视图：与契约 {@code Category} 一一对应。数据层模型不直接出网，接口形状只在这里定义。 */
public record CategoryView(long id, String name, String slug) {
}
