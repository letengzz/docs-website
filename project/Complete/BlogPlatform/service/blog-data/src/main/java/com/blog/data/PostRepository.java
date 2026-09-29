package com.blog.data;

import com.blog.data.model.Post;

import java.util.Optional;

/**
 * 文章仓储接口：**只声明数据层需要的能力，不暴露 ORM**。
 *
 * <p>这一层刻意不继承任何「通用 CRUD 基类」——四套 ORM 的 CRUD 接口取交集等于最弱能力集，
 * 分页模型、条件构造、多表 join 各不相同，统一它们的代价远大于收益。
 */
public interface PostRepository {

    /**
     * 已发布文章分页查询（读者端）。
     *
     * @param page         页码，从 1 开始
     * @param size         每页条数
     * @param categorySlug 分类过滤，可为 null
     * @param tagSlug      标签过滤，可为 null
     */
    Page<Post> findPublished(int page, int size, String categorySlug, String tagSlug);

    /** 按 slug 查已发布文章；草稿与下线文章对读者端一律视为不存在。 */
    Optional<Post> findPublishedBySlug(String slug);
}
