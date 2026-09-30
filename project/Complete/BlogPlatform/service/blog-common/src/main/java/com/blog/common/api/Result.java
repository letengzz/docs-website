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

    /**
     * 业务失败并附带定位信息。用于「参数校验」这类**必须说清是哪一格错了**的场景：
     * 只回一句「参数不合法」，调用方（尤其是后台页面）无法自行修复。
     *
     * <p>{@code code} 仍然取错误码本身，{@code message} 变成「错误码文案：定位信息」——
     * 客户端按 code 分支、人看 message，两者不混。
     */
    public static <T> Result<T> fail(ErrorCode errorCode, String detail) {
        String message = detail == null || detail.isBlank()
                ? errorCode.message()
                : errorCode.message() + "：" + detail;
        return new Result<>(errorCode.code(), message, null);
    }
}
