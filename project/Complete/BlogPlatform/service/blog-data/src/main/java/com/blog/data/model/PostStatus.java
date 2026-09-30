package com.blog.data.model;

/**
 * 文章状态常量。
 *
 * <p>为什么用一个常量类而不是 Java 枚举：契约里的 {@code status} 是字符串枚举，
 * 而数据层还要用到一个**契约尚未声明**的内部状态 {@link #DELETED}（软删除）。
 * 用常量类 + 注释把这件事摆在明面上，比悄悄多加一个枚举值更容易被发现。
 */
public final class PostStatus {

    public static final String DRAFT = "DRAFT";
    public static final String PUBLISHED = "PUBLISHED";
    public static final String OFFLINE = "OFFLINE";

    /**
     * 软删除。
     *
     * <p>注意它**不在契约 {@code PostSummary.status} 的枚举里**（契约只有 DRAFT / PUBLISHED / OFFLINE）。
     * 当前它不会被任何契约接口返回，所以不构成契约违背；等后台列表接口进契约时，
     * 必须同步给枚举补上这个值——否则那天会变成「接口返回了一个契约没定义的枚举值」。
     */
    public static final String DELETED = "DELETED";

    private PostStatus() {
    }
}
