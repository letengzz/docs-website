package com.blog.common.exception;

import com.blog.common.api.ErrorCode;

/**
 * 业务异常：携带一个 {@link ErrorCode}，可选附带一段**定位信息**。
 *
 * <p>不在各处手写错误文案——文案属于错误码的定义，散在业务代码里就没法统一改。
 * 但有时调用方需要更多定位信息（例如「是哪个字段不合法」），这类信息用
 * {@code detail} 承载：它会被统一异常出口拼到 {@code message} 尾部，
 * 而 {@code code} 始终还是那个错误码，客户端按 code 分支、人看 message。
 */
public class BizException extends RuntimeException {

    private final transient ErrorCode errorCode;
    private final transient String detail;

    public BizException(ErrorCode errorCode) {
        this(errorCode, null);
    }

    public BizException(ErrorCode errorCode, String detail) {
        super(detail == null || detail.isBlank()
                ? errorCode.message()
                : errorCode.message() + "：" + detail);
        this.errorCode = errorCode;
        this.detail = detail;
    }

    public ErrorCode errorCode() {
        return errorCode;
    }

    /** 定位信息，可能为 null。 */
    public String detail() {
        return detail;
    }
}
