package com.blog.common.exception;

import com.blog.common.api.ErrorCode;

/**
 * 业务异常：只携带一个 {@link ErrorCode}。
 *
 * <p>不在各处手写错误文案——文案属于错误码的定义，散在业务代码里就没法统一改。
 */
public class BizException extends RuntimeException {

    private final transient ErrorCode errorCode;

    public BizException(ErrorCode errorCode) {
        super(errorCode.message());
        this.errorCode = errorCode;
    }

    public ErrorCode errorCode() {
        return errorCode;
    }
}
