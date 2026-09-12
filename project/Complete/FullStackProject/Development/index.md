# 编码实现

本页给出四个关键模块的实现骨架：**登录鉴权、项目 CRUD、任务看板与状态流转、权限校验**。代码按"能被替换"的原则组织：Controller 薄、Service 承载业务、权限与数据范围在服务层校验。

## 一、模块划分

| 模块 | 前端 | 后端 | 关键约束 |
| --- | --- | --- | --- |
| 登录鉴权 | 登录页 + token 存储 | `/api/auth/*`、JWT 签发与校验 | 密码 bcrypt，令牌短过期 + 刷新 |
| 项目 | 列表/详情/表单 | `/api/projects/*` | 只有负责人可改，成员只读 |
| 任务 | 看板 + 拖拽 | `/api/tasks/*` | 状态枚举校验，排序字段维护 |
| 权限 | 路由/按钮权限 | 注解 + 数据范围校验 | 前端隐藏 ≠ 安全 |

## 二、登录与鉴权（后端）

```java [AuthController.java]
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthService authService;

    @PostMapping("/login")
    public ApiResult<LoginVO> login(@RequestBody @Valid LoginDTO dto) {
        // 1. 校验账号密码（bcrypt），失败计数与锁定在 Service 内处理
        // 2. 签发 access_token（15 分钟）与 refresh_token（7 天）
        return ApiResult.ok(authService.login(dto));
    }

    @PostMapping("/logout")
    public ApiResult<Void> logout(@RequestHeader("Authorization") String authorization) {
        authService.logout(authorization);
        return ApiResult.ok();
    }
}
```

```java [AuthService.java（登录核心逻辑）]
@Service
public class AuthService {

    public LoginVO login(LoginDTO dto) {
        SysUser user = userMapper.findByUsername(dto.getUsername());
        // 账号不存在时也执行一次哈希校验，避免通过响应时间枚举账号
        boolean matched = user != null
                && passwordEncoder.matches(dto.getPassword(), user.getPasswordHash());
        if (!matched) {
            loginAttemptService.recordFailure(dto.getUsername());
            throw new BizException(ErrorCode.LOGIN_FAILED);
        }
        if (!"ACTIVE".equals(user.getStatus())) {
            throw new BizException(ErrorCode.ACCOUNT_DISABLED);
        }
        loginAttemptService.reset(dto.getUsername());
        return tokenService.issue(user);        // 签发 access / refresh
    }
}
```

## 三、任务状态流转（核心业务规则）

```java [TaskStatusService.java]
@Service
public class TaskStatusService {

    private static final Map<String, Set<String>> ALLOWED = Map.of(
            "TODO",  Set.of("DOING", "DONE"),
            "DOING", Set.of("TODO", "DONE"),
            "DONE",  Set.of("DOING")
    );

    @Transactional
    public void changeStatus(Long taskId, String targetStatus, Integer sort, Long currentUserId) {
        Task task = taskMapper.findById(taskId);
        if (task == null || task.getDeletedAt() != null) throw new BizException(ErrorCode.TASK_NOT_FOUND);

        // ① 数据权限：必须是项目成员
        if (!memberMapper.exists(task.getProjectId(), currentUserId)) {
            throw new BizException(ErrorCode.NO_PERMISSION);
        }
        // ② 状态机校验：只允许合法流转
        if (!ALLOWED.getOrDefault(task.getStatus(), Set.of()).contains(targetStatus)) {
            throw new BizException(ErrorCode.ILLEGAL_STATUS_TRANSITION);
        }
        taskMapper.updateStatusAndSort(taskId, targetStatus, sort);
        // ③ 审计：记录变更前后状态
        operationLogService.record("TASK", taskId, "STATUS_CHANGE",
                Map.of("from", task.getStatus(), "to", targetStatus, "sort", sort), currentUserId);
    }
}
```

::: danger 拖拽功能的三个必踩坑
1. **只改前端状态不落库**：刷新后回到原样，必须在拖拽成功后调用接口（乐观更新要带失败回滚）。
2. **状态流转不校验**：允许任意状态互跳，业务规则形同虚设，用状态机白名单约束。
3. **排序字段重排代价大**：一次性重排整列会放大写放大，实践中常用"间隔步长 + 局部重排"，并限制单次移动影响的行数。
:::

## 四、权限与数据范围（统一入口）

```java [权限校验的统一写法]
@RestController
@RequestMapping("/api/projects")
public class ProjectController {

    // 功能权限：注解声明权限点（由 Spring Security 统一拦截）
    @PreAuthorize("hasAuthority('project:update')")
    @PutMapping("/{id}")
    public ApiResult<Void> update(@PathVariable Long id, @RequestBody ProjectDTO dto,
                                  @AuthenticationPrincipal LoginUser user) {
        // 数据权限：服务层校验归属，不接受前端传入的 ownerId
        projectService.update(id, dto, user.getId());
        return ApiResult.ok();
    }
}
```

前端侧：路由与按钮权限的完整实现见 [权限模块](../../../Base/Vue3Template/Permission/index.md)；后端权限的通用方法见 [认证与授权专题](../../../../docs/Backend/Auth/index.md)。

## 五、统一响应与异常

```java [GlobalExceptionHandler.java（节选）]
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BizException.class)
    public ApiResult<Void> handleBiz(BizException e) {
        return ApiResult.fail(e.getCode(), e.getMessage());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ApiResult<Void> handleValid(MethodArgumentNotValidException e) {
        String msg = e.getBindingResult().getFieldErrors().stream()
                .map(err -> err.getField() + ": " + err.getDefaultMessage())
                .collect(Collectors.joining("; "));
        return ApiResult.fail(ErrorCode.PARAM_INVALID, msg);
    }

    @ExceptionHandler(Exception.class)
    public ApiResult<Void> handleOther(Exception e) {
        log.error("未处理异常", e);              // 日志留堆栈，响应不暴露细节
        return ApiResult.fail(ErrorCode.SYSTEM_ERROR);
    }
}
```

## 验证方式

1. 用错误密码连续登录 5 次，确认触发失败计数/锁定策略。
2. 用非项目成员身份调用任务状态变更接口，确认返回 403（不是 200）。
3. 尝试非法状态流转（DONE → TODO 若未在允许集合中），确认返回业务错误码。
4. 变更任务状态后查询操作日志，确认有完整记录（人、时间、前后状态）。
5. 触发一次未处理异常，确认响应是统一错误结构且日志中有堆栈。

## 参考资料

- Spring Boot 官方文档：https://docs.spring.io/spring-boot/index.html
- 本库认证授权：[认证与授权专题](../../../../docs/Backend/Auth/index.md)
- 前端权限实现：[权限模块](../../../Base/Vue3Template/Permission/index.md)
