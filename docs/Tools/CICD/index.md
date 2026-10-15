# CI/CD

<p style="text-align:center;"><img src="./assets/cicd-logo.png" alt="CI/CD" style="zoom:75%;" /></p>

CI/CD（持续集成 / 持续交付与部署）把代码从提交到上线全流程自动化：每次提交自动构建、测试、扫描，通过质量门禁后自动部署，出问题可一键回滚。本专题覆盖 GitHub Actions、GitLab CI/CD、Jenkins 三大主流工具与流水线设计、质量门禁、制品管理、部署回滚的完整实践。

- [CI/CD 概念与流水线设计](Overview/index.md)
- [GitHub Actions 入门](GithubActions/index.md)
- [GitLab CI/CD](GitlabCI/index.md)
- [Jenkins 流水线](Jenkins/index.md)
- [流水线设计最佳实践](PipelineDesign/index.md)
- [自动化测试与质量门禁](Testing/index.md)
- [制品管理](Artifacts/index.md)
- [自动部署与回滚](DeployRollback/index.md)
- [常见问题与最佳实践](FAQ/index.md)

## 与自建工具链专题的分工

- **本页**讲流水线侧：阶段怎么设计、门禁挂在哪一步、制品怎么管。
- [自建工具链](../Toolchain/index.md) 讲**跑在开发者本机上的那一半**：脚手架、CLI、代码生成器，以及它们怎么分发给别人装。
- 判据：同一件事在两侧都出现时，**校验命令只能有一份实现** —— CI 调用的应当是开发者本机能原样跑的那条命令，而不是流水线里另写一套。否则「本地绿、CI 红」会变成常态。

## 相关专题

- [完整项目交付](../../Others/ProjectDelivery/index.md)：本专题解决「流水线怎么搭」，该专题解决「一条流水线上该挂哪些门禁、每个门禁的判据从哪来」——把需求拆分、架构决策、接口契约、数据迁移、测试门禁、一键部署与上线验收串成一条可复用的交付方法线
- [故障应急体系](../../Ops/IncidentResponse/index.md)：**发布类事故的止血主力是回滚，而回滚能力属于本专题**。分工是：本专题建设「回滚是一条命令、耗时已知、数据库变更可前向兼容」，该专题规定「什么时候必须回滚、由谁决定、回滚后怎么确认」。三处交界：① **回滚必须实测过耗时**（该专题的「发布类预案」把「回滚耗时量过吗」列为判据）；② **破坏性数据库迁移的回退方案要在发布前写好**，而不是出事时想；③ **回滚记录要落进流水线**，因为事故时间线上的每一步都应当可回溯。
