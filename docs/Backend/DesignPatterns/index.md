# 设计模式

<p style="text-align:center;"><img src="./assets/dp-logo.png" alt="设计模式" style="zoom:75%;" /></p>

设计模式（Design Pattern）是软件设计中**可复用的解决方案**：针对反复出现的问题，给出经过验证的类与对象组织方式。本专题覆盖设计原则、创建型/结构型/行为型三大类模式、框架中的应用（Spring/MyBatis）与实战重构案例。

- [设计原则](Principles/index.md)
- [创建型模式](Creational/index.md)
- [结构型模式](Structural/index.md)
- [行为型模式](Behavioral/index.md)
- [框架中的应用](FrameworkUsage/index.md)
- [JDK 源码中的设计模式](JdkPatterns/index.md)
- [现代 Java 与设计模式](ModernJava/index.md)
- [反模式与过度设计](AntiPatterns/index.md)
- [重构实战：安全地改代码](RefactorPractice/index.md)
- [实战案例](Practice/index.md)
- [常见问题与最佳实践](FAQ/index.md)

与 [领域驱动设计](../DDD/index.md) 的分工：本专题讲**代码级可复用模式**（怎么组织类与对象）；DDD 讲**业务模型怎么切分与表达**——DDD 的战术设计构件（工厂、策略、规格模式）会用到本专题的模式，但两边的抽象层级不同。

与 [工作流与规则引擎](../WorkflowEngine/index.md) 的分工：本专题的**策略模式与规格模式**，正是「判定逻辑会变、但还不到上规则引擎的程度」时的标准答案——把条件抽成 `Specification`、把算法抽成 `Strategy`，可读性与可测性都优于引入一套 BRMS。什么时候这种「代码内模式」会真的撑不住、需要换成规则引擎（判据是规则数量与是否要业务自助维护），见那边的[规则引擎选型](../WorkflowEngine/RuleEngine/index.md)。**先试模式，再上引擎**——反过来做，等于为一个三条件的判断建了一张数据库表。
