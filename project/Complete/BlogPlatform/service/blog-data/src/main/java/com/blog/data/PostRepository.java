package com.blog.data;

import com.blog.data.model.Post;

import java.util.Optional;

/**
 * 文章仓储接口：**只声明数据层需要的能力，不暴露 ORM**。
 *
 * <p>这一层刻意不继承任何「通用 CRUD 基类」——四套 ORM 的 CRUD 接口取交集等于最弱能力集，
 * 分页模型、条件构造、多表 join 各不相同，统一它们的代价远大于收益。
 *
 * <p>方法按**读者端 / 后台端**分两组，这不是洁癖：两组对「可见性」的判定完全不同
 * （读者端必须过滤草稿与软删除，后台端必须全都能看到），混在一起最容易把草稿漏到前台。
 */
public interface PostRepository {

    // ------------------------------------------------------------ 读者端

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

    // ------------------------------------------------------------ 后台端

    /** 按主键查（后台用；包含草稿与已软删除）。 */
    Optional<Post> findById(long id);

    /** 后台列表：包含草稿，但不含已软删除。 */
    Page<Post> findForAdmin(int page, int size);

    /** slug 是否已被占用（创建时用）。 */
    boolean existsSlug(String slug);

    /** slug 是否被**其他**文章占用（更新时用：允许保持自己的 slug 不变）。 */
    boolean existsSlugExcept(String slug, long id);

    /** 创建草稿，返回落库后的完整对象（含生成的 id）。 */
    Post insert(PostWrite write);

    /** 更新正文与归属；文章不存在时返回空。状态与发布时间**不受本操作影响**。 */
    Optional<Post> update(long id, PostWrite write);

    /** 软删除：置为 DELETED。硬删除在内容系统里几乎总是错的（误删无法恢复，且会打断外链与 SEO）。 */
    boolean softDelete(long id);

    /**
     * 发布：状态由 DRAFT 转为 PUBLISHED，同时写入 publishedAt 并渲染 contentHtml。
     *
     * <p>把「渲染」放在发布时刻而不是保存时刻，是因为草稿期间作者可能反复改；
     * 只有确定要发出去的那一刻，才需要一份与当时内容严格对应的、已消毒的 HTML。
     */
    Optional<Post> publish(long id);
}
