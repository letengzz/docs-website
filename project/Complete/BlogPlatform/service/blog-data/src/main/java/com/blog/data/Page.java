package com.blog.data;

import java.util.List;

/**
 * 分页结果。字段名与契约里 200 响应的 {@code data} 形状一致（{@code total} + {@code records}），
 * 这样 Web 层不需要再做一次「集合改名」的无意义映射。
 *
 * @param <T> 元素类型
 */
public record Page<T>(long total, List<T> records) {

    public static <T> Page<T> of(long total, List<T> records) {
        return new Page<>(total, List.copyOf(records));
    }

    public static <T> Page<T> empty() {
        return new Page<>(0L, List.of());
    }
}
