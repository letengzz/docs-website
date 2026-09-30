package com.blog.web.common;

import com.blog.common.api.ErrorCode;
import com.blog.common.api.Result;
import com.blog.common.exception.BizException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.stream.Collectors;

/**
 * 统一异常出口：**错误码 → HTTP 状态**的映射只在这里出现一次。
 *
 * <p>取舍说明：这里不把错误码塞进 HTTP 状态码（例如 2001 就返回 HTTP 2001），
 * 而是按语义映射到 4xx/5xx —— 网关、监控、客户端重试策略都依赖标准状态码工作。
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(BizException.class)
    public ResponseEntity<Result<Void>> handleBiz(BizException ex) {
        HttpStatus status = switch (ex.errorCode()) {
            case PARAM_INVALID, PARAM_PAGE_OUT_OF_RANGE -> HttpStatus.BAD_REQUEST;
            case RESOURCE_NOT_FOUND -> HttpStatus.NOT_FOUND;
            case RESOURCE_CONFLICT, STATE_CONFLICT -> HttpStatus.CONFLICT;
            case UNAUTHORIZED -> HttpStatus.UNAUTHORIZED;
            case FORBIDDEN -> HttpStatus.FORBIDDEN;
            default -> HttpStatus.INTERNAL_SERVER_ERROR;
        };
        // detail 一路带到响应里：入口校验（如「categoryId 不存在：9」）靠它才能定位到具体值
        return ResponseEntity.status(status).body(Result.fail(ex.errorCode(), ex.detail()));
    }

    /**
     * 参数校验失败：把**字段名与原因**一并返回，而不是笼统的一句「参数不合法」。
     *
     * <p>这条是写接口的可用性底线：后台页面拿到 {@code title: 不能为空} 可以直接定位到表单哪一格，
     * 拿到「参数不合法」只能去翻服务端日志。
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Result<Void>> handleInvalid(MethodArgumentNotValidException ex) {
        String detail = ex.getBindingResult().getFieldErrors().stream()
                .map(fe -> fe.getField() + " " + fe.getDefaultMessage())
                .sorted()
                .collect(Collectors.joining("；"));
        return ResponseEntity.badRequest().body(Result.fail(ErrorCode.PARAM_INVALID, detail));
    }

    /**
     * 兜底：任何未预料异常都不把堆栈暴露给调用方，但仍然保留 500 语义，
     * 便于监控按状态码聚合。
     *
     * <p>**必须打日志**：兜底处理器只返回统一响应、不记录异常，等于把证据也一起吞了——
     * 排查时会看到「接口返回 5001，但日志里什么都没有」。
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<Result<Void>> handleUnexpected(Exception ex) {
        log.error("未预期的异常，按 {} 处理", ErrorCode.INTERNAL_ERROR, ex);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Result.fail(ErrorCode.INTERNAL_ERROR));
    }
}
