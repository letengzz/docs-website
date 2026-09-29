package com.blog.common.api;

/**
 * 统一响应外壳。契约里 {@code Result} 的必填字段是 {@code code} 与 {@code message}，
 * {@code data} 可选 —— 三类字段在这里一次定死，全站所有接口都从这里出。
 *
 * @param <T> 业务数据类型；无数据时为 {@code Void}
 */
public record Result<T>(int code, String message, T data) {

    /** 成功且有数据。 */
    public static <T> Result<T> ok(T data) {
        return new Result<>(ErrorCode.OK.code(), ErrorCode.OK.message(), data);
    }

    /** 成功且无数据（写接口常见）。 */
    public static Result<Void> ok() {
        return new Result<>(ErrorCode.OK.code(), ErrorCode.OK.message(), null);
    }

    /** 业务失败：错误码与文案都来自 {@link ErrorCode}，避免各处自己拼字符串。 */
    public static <T> Result<T> fail(ErrorCode errorCode) {
        return new Result<>(errorCode.code(), errorCode.message(), null);
    }
}
