package com.blog.data;

import java.util.List;

/**
 * 文章写命令：与契约里的 {@code PostUpsert} **字段一一对应**。
 *
 * <p>刻意用独立类型而不是直接收 Web 层的 DTO：数据层一旦依赖 Web 层，模块的依赖方向就反了
 * （{@code blog-data} 不能依赖 {@code blog-web}）。两边各有一个同形状的类型，由 Controller 做翻译，
 * 代价是一次赋值，收益是「改契约不会牵动数据层」。
 *
 * <p>注意它**不含 status 与 publishedAt**：状态属于状态机（发布/下线是独立动作），
 * 不由「创建/更新」这一入口决定——把状态塞进 upsert 是状态机失控的常见起点。
 */
public record PostWrite(
        String title,
        String slug,
        long categoryId,
        List<Long> tagIds,
        String contentMd) {
}
