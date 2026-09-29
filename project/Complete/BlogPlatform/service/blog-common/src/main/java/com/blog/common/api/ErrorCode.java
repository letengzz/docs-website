package com.blog.common.api;

/**
 * 错误码分段：0 成功、1xxx 参数、2xxx 资源、3xxx 认证授权、5xxx 服务端。
 *
 * <p>分段的意义不在「好看」，而在排查时能一眼判断该找谁：看到 2xxx 先看数据是否存在，
 * 看到 5xxx 才去看日志与依赖。
 */
public enum ErrorCode {

    OK(0, "成功"),

    PARAM_INVALID(1001, "参数不合法"),
    PARAM_PAGE_OUT_OF_RANGE(1002, "分页参数超出允许范围"),

    RESOURCE_NOT_FOUND(2001, "资源不存在"),

    UNAUTHORIZED(3001, "未认证"),
    FORBIDDEN(3002, "无权限"),

    INTERNAL_ERROR(5001, "服务内部错误");

    private final int code;
    private final String message;

    ErrorCode(int code, String message) {
        this.code = code;
        this.message = message;
    }

    public int code() {
        return code;
    }

    public String message() {
        return message;
    }
}
