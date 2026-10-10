# Spring 容器、自动配置与事务边界补充

[总目录](../../README.md) · [原 Spring 题](04-spring-and-backend.md)

Spring Framework 6+ 的行为与历史版本差异分开说明；自动配置示例按现代 Spring Boot imports 机制。参考手册滚动更新，发布前核对日期为 2026-10-09；源码示例固定到 Framework 6.2.0。所有代码、配置与故障测试均未运行。

<a id="fj22"></a>
### FJ22 Bean 作用域和生命周期怎样一起决定状态与资源归属

**优先级：P0。**

**知识点详解**：singleton 是每个容器、每个 Bean 定义的共享实例，不是每 JVM 某个类只能一个；prototype 是每次向容器请求/创建时新建，不是每 HTTP 请求新建。把 prototype 直接注入 singleton，注入时得到的那一个对象可一直被单例持有；要每次使用新实例，可在合适边界通过 ObjectProvider 等机制取得。request/session 是 Web 作用域，分别按请求/会话组织，不能用 prototype 代替它们的全部语义。

典型生命周期是读取定义、通过构造器或工厂产生实例、注入依赖、Aware/后处理/初始化回调、暴露可用对象，再在适用生命周期结束时销毁。工厂方法也能创建 Bean，不必都是容器直接反射其构造器。后处理器可返回代理；初始化回调通常在目标对象完成代理包装前，因此不应在 @PostConstruct 里依赖自身代理事务。

当配置了不同名称的多个初始化回调，常见顺序是 @PostConstruct → InitializingBean.afterPropertiesSet → 自定义 init；销毁对应 @PreDestroy → DisposableBean.destroy → 自定义 destroy。相同方法被多种机制登记时不能简单假定执行多次。prototype 的初始化仍由容器执行，但交付后的销毁通常不自动由容器负责，使用方要清理昂贵资源。

**具体例子**：单例 Service 的局部变量 `var list = sharedField` 虽然引用本身是局部变量，指向的列表仍共享；方法局部不等于对象线程隔离。请求缓冲放请求私有对象；连接客户端可由长生命周期 Bean 管理，并明确关闭阶段。

**面试答法**：scope 决定实例复用边界，生命周期决定依赖可用与资源清理时机；单例不保证线程安全，prototype 不自动对应请求，也不完整托管销毁。

**追问**：容器关闭回调能保证在进程强杀后执行吗？不能。post processor 可以把原对象换为代理吗？可以，因此注入引用与原始目标要区分。

**误区**：prototype 每个方法调用都新建；只要状态在局部变量就绝对线程安全；所有 Bean 都通过直接反射构造。

**一手来源**：[FJ-S061 Bean scopes](https://docs.spring.io/spring-framework/reference/core/beans/factory-scopes.html)、[FJ-S062 生命周期](https://docs.spring.io/spring-framework/reference/core/beans/factory-nature.html)。

<a id="fj23"></a>
### FJ23 Autowired、Resource 和循环依赖的“三级缓存”各解决什么

**优先级：P0。**

**知识点详解**：@Autowired 先围绕类型候选解析，可用 @Qualifier 缩小集合、@Primary 表达默认优先候选；必需依赖通常适合构造器注入，单一构造器不必写 @Autowired。按名称的回退等细节不能简化成永远“先类型后名称”两条 if。@Resource 表达资源名称语义，未显式指定 name 时通常由字段/属性名推导，并在合适的默认情形回退类型；显式 name 找不到时不能普遍回退为任何同类型 Bean。现代 Spring 6+ 使用 jakarta.annotation.Resource，旧项目常见 javax.annotation，包名和依赖需随平台迁移。

循环依赖是对象创建图里的环。构造器 A 需要 B、B 又需要 A，会在任何完整对象出现前循环等待；所谓三级缓存不能凭空创造已构造对象。对于允许循环引用的部分单例属性注入，Spring 6.2.0 使用 singletonObjects、earlySingletonObjects、singletonFactories 协调完成对象、早期引用和生成早期引用的工厂。A 实例化后暴露可取早期引用的入口，创建 B 时注入 A 的早期引用，随后完成 A；代理相关后处理需保证早期引用与最终暴露对象一致。

这不覆盖所有作用域、构造器与代理组合。Spring Boot 2.6 起默认禁止循环引用，应优先拆出共同协作者或调整依赖方向；开启配置只是允许容器尝试解决支持的环，不是修复设计。

**具体例子**（设计示例）：OrderService 与 InventoryService 互相调用，不妨由 OrderWorkflow 依赖两者来协调流程，使它们不再相互注入。若两个 SearchClient 同类型，构造器参数明确 @Qualifier("internalSearch")，比依赖字段命名碰巧匹配更清楚。

**面试答法**：注入规则解决“选哪个依赖”，早期引用解决部分“创建中的单例如何互相引用”；不能用缓存口诀解释所有循环，也不能忽略 Boot 默认设置。

**追问**：为何第三层放工厂而不总提前放原对象？为了按需获得可能经过早期代理处理的引用，而不是普遍注入未增强的裸对象。Lazy 可缓解环是否就设计正确？仍需审查运行时依赖与首次调用行为。

**误区**：Resource 显式名字缺失也总回退类型；三级缓存能解决所有构造器循环；开启循环配置是推荐长期方案。

**一手来源**：[FJ-S063 Autowired](https://docs.spring.io/spring-framework/reference/core/beans/annotation-config/autowired.html)、[FJ-S064 Resource](https://docs.spring.io/spring-framework/reference/core/beans/annotation-config/resource.html)、[FJ-S065 依赖注入与循环](https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html)、[FJ-S066 6.2.0 单例注册表源码](https://github.com/spring-projects/spring-framework/blob/v6.2.0/spring-beans/src/main/java/org/springframework/beans/factory/support/DefaultSingletonBeanRegistry.java)、[FJ-S067 Boot 2.6 变更](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-2.6-Release-Notes)。

<a id="fj24"></a>
### FJ24 Starter、自动配置与 Boot 启动怎样串起来，Cloud 又负责什么

**优先级：P1。**

**知识点详解**：starter 主要提供依赖组合入口；autoconfigure 模块提供条件配置；具体客户端库承载功能。它们可按规模拆模块，概念上仍应分开。现代 Boot 的自动配置类通过 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` 登记，一行一个全限定类名。旧教程通过 spring.factories 注册 EnableAutoConfiguration 的方式需要版本限定，不能作为 Boot 3/4 新项目通用模板。

自动配置先导入候选，再按类路径、属性、已有 Bean 等条件判断是否应用。@ConditionalOnClass 避免缺少可选依赖时强建配置；@ConditionalOnMissingBean 允许用户提供自定义实现后退让；@ConfigurationProperties 将配置集中绑定并验证。条件装配是“要不要提供”，lazy 是“需要时才实例化”，二者不是一回事。

**启动主线**（按 Boot 3.5.0 SpringApplication 源码理解，未运行）：静态 run 入口创建/运行 SpringApplication；准备启动监听、参数与 Environment；根据应用类型创建 ApplicationContext；把环境、初始器与配置来源放入上下文；调用 refresh，运行容器的配置解析、后处理、非懒单例创建等生命周期，Web 上下文也在刷新相关阶段准备并启动嵌入式服务器；刷新成功后发 Started，再调用 ApplicationRunner/CommandLineRunner，完成后发 Ready。不是先把所有 Bean 完全创建，再单独补一次自动配置；自动配置参与容器定义解析。具体 WebServer 子阶段依 Servlet/Reactive 与版本而异。端口已经监听不代表耗时 runner 已完成，流量准入仍应尊重 readiness。

**Spring、Boot、Cloud 的职责**：Spring Framework 提供 IoC、AOP、事务和 Web 等基础编程模型；Boot 在其上提供约定、依赖管理、自动配置、启动与运维整合；Cloud 是处理跨服务问题的一组项目，不是要求所有应用都上微服务。例子包括 Config 管理外部配置，Eureka/Consul 集成注册发现，Gateway 处理入口路由，LoadBalancer 做客户端实例选择，CircuitBreaker 统一熔断抽象，Stream 整合消息驱动。单体也能用 Boot；引入 Cloud 不会自动消除网络超时、重复请求或分布式事务问题。具体组件和 Boot 必须按官方 release train/BOM 兼容表配套，不能照搬旧“全家桶”的组件清单。

**具体例子**（简化代码，未运行，省略导入、属性类和依赖配置）：
```java
@AutoConfiguration
@ConditionalOnClass(SearchClient.class)
@EnableConfigurationProperties(SearchProperties.class)
class SearchAutoConfiguration {
    @Bean
    @ConditionalOnMissingBean(SearchClient.class)
    SearchClient searchClient(SearchProperties p) {
        return new SearchClient(p.endpoint());
    }
}
```
客户端构造器只是示意。imports 文件登记该类；测试至少包括：依赖存在能创建、依赖缺失不误触发、用户自定义 Bean 能退让、非法属性明确报错。可使用 ApplicationContextRunner 做小范围条件测试，并检查条件报告。

**面试答法**：Starter 是依赖入口，自动配置是条件化默认装配；现代 imports 注册，保留用户覆盖能力，测试命中与不命中场景，不把条件判断误称延迟加载。

**追问**：一个 starter 应强行扫描用户包吗？应避免扩大组件扫描和命名冲突，明确配置导入边界。自动配置执行顺序是否等于 Bean 实例创建顺序？不是同一个概念。

**误区**：加 @Configuration 就自动成为任何项目的 Starter；默认配置覆盖用户明确 Bean；将 spring.factories 用法无版本复制。

**一手来源**：[FJ-S068 官方自定义自动配置指南](https://docs.spring.io/spring-boot/reference/features/developing-auto-configuration.html)、[FJ-S139 SpringApplication 生命周期](https://docs.spring.io/spring-boot/reference/features/spring-application.html)、[FJ-S140 Boot 3.5.0 启动入口源码](https://raw.githubusercontent.com/spring-projects/spring-boot/v3.5.0/spring-boot-project/spring-boot/src/main/java/org/springframework/boot/SpringApplication.java)、[FJ-S141 Spring Cloud 项目与兼容表](https://spring.io/projects/spring-cloud/)。

<a id="fj25"></a>
### FJ25 Spring 的 isolation 设置什么时候生效，怎样区分“没事务”和“没回滚”

**优先级：P0。**

**知识点详解**：Isolation.DEFAULT 使用底层默认；READ_UNCOMMITTED、READ_COMMITTED、REPEATABLE_READ、SERIALIZABLE 是请求给资源层的隔离语义，是否支持取决于事务管理器与数据库。传播 REQUIRED 加入已有物理事务时，通常继承外层特征，内层隔离声明不会自动重新配置那个已运行的事务；可用相应严格校验选项拒绝不匹配。REQUIRES_NEW 新建独立物理事务才可有独立设置，但会带来额外连接需求。

排错分三问：调用是否经过事务拦截；拦截后资源是否确实加入；发生异常后是否满足回滚规则。Spring 6+ 类代理默认可处理 protected/package-visible 方法，接口代理仍要求 public 且在接口上；private/final 与自调用边界要按代理机制说明。自调用不触发内层注解，不等于外层已有事务消失。命令式事务常绑定线程，新线程不继承原事务，但它通过代理调用另一事务方法可以开启自己的事务。

默认异常回滚规则及全局配置见 [J35](04-spring-and-backend.md#j35)：捕获异常正常返回、checked exception 默认不回滚、管理器选错，都与完全绕过代理不同。数据库事务不能撤回已经发送到外部的邮件。

**具体例子**（测试设计，未运行）：外层 RC REQUIRED 调用另一 Bean 的 RR REQUIRED，观察实际连接隔离仍为外层 RC；随后开启严格校验，应预期拒绝不兼容声明，而不是悄悄开第二个事务。回滚测试在第二次数据库写入前抛异常，并在事务完成后用独立查询确认第一条是否存在。

**面试答法**：注解声明、代理路径、物理事务和资源四层必须一致；加入已有事务通常沿用外层隔离，排错先确认有没有开启，再查为什么没回滚。

**追问**：外层捕获内层 REQUIRED 异常能保证提交吗？共享事务可能已经 rollback-only，最终出现 UnexpectedRollbackException。反应式事务还总靠线程绑定吗？不是同一模型，需用 Reactor 上下文和反应式事务管理器。

**误区**：每个 @Transactional 都新建事务；非 public 在所有 Spring 版本都失效；任意新线程都绝不能有自己的事务。

**一手来源**：[FJ-S069 事务传播](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html)、[FJ-S070 Transactional 注解边界](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)。
