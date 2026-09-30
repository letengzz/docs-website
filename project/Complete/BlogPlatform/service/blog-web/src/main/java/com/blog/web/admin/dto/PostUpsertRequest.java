package com.blog.web.admin.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

import java.util.List;

/**
 * 文章创建/更新入参，与契约 {@code PostUpsert} **逐字对应**。
 *
 * <p>三个容易出错的地方，都在这里一次定死：
 * <ul>
 *   <li>{@code slug} 的 pattern 与契约里的 {@code ^[a-z0-9-]+$} 一致——契约写了限制、实现不校验，
 *       等于契约白写；</li>
 *   <li>{@code categoryId} 是 id 不是 slug（写入用 id、读出用 slug，翻译在数据层做）；</li>
 *   <li>**没有 status 字段**：状态由发布/下线接口驱动，不能由 upsert 随意设置。</li>
 * </ul>
 */
public record PostUpsertRequest(
        @NotBlank(message = "不能为空")
        @Size(max = 128, message = "长度不能超过 128")
        String title,

        @NotBlank(message = "不能为空")
        @Size(max = 128, message = "长度不能超过 128")
        @Pattern(regexp = "^[a-z0-9-]+$", message = "只能包含小写字母、数字与短横线")
        String slug,

        @NotNull(message = "不能为空")
        Long categoryId,

        List<Long> tagIds,

        @NotBlank(message = "不能为空")
        String contentMd) {
}
