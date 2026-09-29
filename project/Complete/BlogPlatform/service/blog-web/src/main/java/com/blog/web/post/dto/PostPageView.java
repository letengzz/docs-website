package com.blog.web.post.dto;

import java.util.List;

/** 分页出参：字段名与契约中 200 响应的 {@code data} 一致（{@code total} + {@code records}）。 */
public record PostPageView(long total, List<PostSummaryView> records) {
}
