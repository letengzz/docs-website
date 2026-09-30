package com.blog.web.admin.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

/**
 * 分类/标签的创建入参，与契约 {@code Category} / {@code Tag} 的字段对齐（id 由服务端生成，不接收）。
 *
 * <p>把校验注解写在**入参**上而不是在 Controller 里手写 if：注解是声明式的、能被统一异常处理器
 * 汇聚成「字段 + 原因」，也不会出现「某个接口忘了校验」这类漏项。
 */
public record TaxonomyUpsertRequest(
        @NotBlank(message = "不能为空")
        @Size(max = 32, message = "长度不能超过 32")
        String name,

        @NotBlank(message = "不能为空")
        @Size(max = 64, message = "长度不能超过 64")
        @Pattern(regexp = "^[a-z0-9-]+$", message = "只能包含小写字母、数字与短横线")
        String slug) {
}
