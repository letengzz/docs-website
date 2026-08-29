# JVM 调优参数

JVM 调优不是“背参数”，而是**明确目标 → 收集数据 → 调整 → 验证**的循环。这一篇给出最常用的内存、GC 日志、故障保留参数，并纠正常见误区。

## 调优目标

| 目标 | 关注指标 |
| --- | --- |
| 吞吐量 | GC 时间占比、单位时间处理请求数 |
| 延迟 | Full GC 频率、单次停顿时间、P99 |
| 稳定性 | OOM 次数、堆/元空间使用曲线 |

## 堆内存参数

```shell
java -Xms4g -Xmx4g \
  -Xmn1g \
  -XX:MetaspaceSize=256m \
  -XX:MaxMetaspaceSize=512m \
  -jar app.jar
```

| 参数 | 说明 | 建议 |
| --- | --- | --- |
| `-Xms` / `-Xmx` | 堆初始/最大 | 生产设为相同，避免扩容抖动 |
| `-Xmn` | 新生代大小 | 一般占堆 1/3~1/2，先测再调 |
| `-XX:MaxMetaspaceSize` | 元空间上限 | 防止动态代理/类加载泄漏打爆内存 |
| `-XX:SurvivorRatio` | Eden : Survivor 比例 | 默认 8 |
| `-XX:MaxDirectMemorySize` | 直接内存上限 | 使用 NIO 时显式设置 |

## 收集器与停顿参数

```shell
java -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=100 \
  -XX:ParallelGCThreads=8 \
  -jar app.jar
```

| 参数 | 说明 |
| --- | --- |
| `-XX:+UseG1GC` / `-XX:+UseZGC` | 选择收集器 |
| `-XX:MaxGCPauseMillis` | G1 停顿目标（默认 200ms） |
| `-XX:ParallelGCThreads` | 并行 GC 线程数 |
| `-XX:G1HeapRegionSize` | G1 Region 大小（一般不手动设） |

## GC 日志（JDK 9+ 统一日志）

JDK 9 起使用 `-Xlog` 统一日志，旧参数（`-verbose:gc`、`-XX:+PrintGCDetails`）已移除：

```shell
# 输出到控制台
java -Xlog:gc* -jar app.jar

# 输出到滚动文件（10 个文件，每个 10MB）
java -Xlog:gc*:file=gc.log:time,uptime,level,tags:filecount=10,filesize=10m -jar app.jar
```

常用日志标签：`gc`、`gc+heap`、`gc+ergo`、`gc+promotion`、`safepoint`。

## 故障保留参数

```shell
java -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/data/dumps \
  -XX:OnOutOfMemoryError='kill -9 %p' \
  -jar app.jar
```

| 参数 | 作用 |
| --- | --- |
| `-XX:+HeapDumpOnOutOfMemoryError` | OOM 时自动生成堆转储 |
| `-XX:HeapDumpPath` | 转储文件路径 |
| `-XX:OnOutOfMemoryError` | OOM 后执行命令（如重启） |
| `-XX:+ExitOnOutOfMemoryError` | OOM 直接退出（配合外部守护重启） |

## 查看当前生效参数

```shell
jcmd <pid> VM.flags          # 查看生效参数
jcmd <pid> VM.command_line   # 查看启动命令
java -XshowSettings:vm -version
```

## 调优流程

```text
1. 设定目标（P99 延迟 < 200ms，无 OOM）
2. 采集基线：jstat、GC 日志、压测数据
3. 定位瓶颈：Full GC 频繁？停顿超时？堆使用率异常？
4. 单变量调整（一次只改一个参数）
5. 验证：回归压测，对比指标
6. 固化到启动脚本/容器参数
```

## 易错点

::: danger 常见错误
1. 盲目抄网上的“万能参数”：不同应用模型差异巨大，先有目标再调参。
2. `-Xms` 与 `-Xmx` 不一致：运行中频繁扩容/收缩，GC 日志出现大量 heap 大小变化。
3. `-Xmn` 设置过大：新生代太大挤占老年代，Full GC 反而更频繁。
4. 还在用 JDK 8 的 `-XX:+PrintGCDetails`：JDK 9+ 参数不存在，统一用 `-Xlog`。
5. 生产环境不保留 OOM 现场：没有 HeapDump，事后只能靠猜。
6. 把“GC 次数少”当健康：次数少但单次停顿长也可能拖垮延迟，要看停顿时间分布。
:::

## 验证方式

1. 用 `java -XshowSettings:vm -version` 查看默认参数，再通过 `jcmd <pid> VM.flags` 对比运行中生效值。
2. 配置 `-Xlog:gc*:file=gc.log` 运行压测，用 GC 日志分析工具（GCeasy、gceasy.io）生成报告。
3. 用 `jstat -gcutil <pid> 1000` 观察 1 秒间隔的堆使用率与 GC 次数变化。

## 参考资料

- IO 相关调优前置知识：[Java IO/NIO 专题](../IO/index.md)
- Oracle GC 调优指南：https://docs.oracle.com/en/java/javase/25/gctuning/
- JEP 158（统一 JVM 日志）：https://openjdk.org/jeps/158
- 常用 JVM 参数列表：https://docs.oracle.com/en/java/javase/25/docs/specs/man/java.html
