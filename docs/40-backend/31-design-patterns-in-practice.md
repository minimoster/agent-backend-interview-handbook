# 设计模式：从结构识别到可运行实现

[返回总目录](../../README.md) · [题目索引](../../QUESTION_INDEX.md) · [版本与纠错](../../errata/README.md)

官方资料核查于2026-10-09。示例参数用于教学推演，代码、SQL 与实验的执行情况在对应题中标注。

- [FB10 怎样识别创建型、结构型、行为型模式和 Spring 工厂抽象](#fb10)
- [FB11 如何手写安全的延迟单例，DCL 为什么必须关注发布](#fb11)
- [FB12 代理和适配器怎样在真实 API 中区分](#fb12)
- [FB13 拒绝策略为什么是策略模式，也是业务过载语义](#fb13)
- [FB14 模板方法与模板加回调的扩展方式有什么不同](#fb14)

<a id="fb10"></a>

### FB10 怎样识别创建型、结构型、行为型模式和 Spring 工厂抽象

**优先级：P1**

**知识点详解**：创建型关注对象怎样生成，如工厂、建造者、单例；结构型关注接口与对象如何组合，如适配器、代理、装饰器；行为型关注职责如何协作，如策略、观察者、模板方法。模式是讨论变化点的语言，不是必须加入的类数量。Spring 容器承担创建和管理职责，BeanFactory 提供获取对象的接口；FactoryBean 定制某个对象的创建。不能仅凭 getBean 这个名字就断言严格实现 GoF 工厂方法的继承结构。

**具体例子**：第三方 SDK 客户端需要证书、连接池和复杂构造，可以用容器配置或 FactoryBean 封装生命周期；若只 new 一个无状态普通对象，额外建五个工厂类反而增加理解成本。

**面试答法**：我先说哪部分会变，再说明模式如何把变化隔离；能画出参与者与调用方向，才给它贴模式名称。

**追问**：策略与工厂会同时出现吗？工厂选择并创建一个策略，业务按统一策略接口执行，两者解决不同问题。

**常见误区**：每个 get 方法都是工厂方法；为了凑模式修改稳定代码；把 Spring 单例作用域等同全 JVM 只有一个对象。

**来源**：[FB-S016 Spring 容器扩展点与 FactoryBean](https://docs.spring.io/spring-framework/reference/core/beans/factory-extension.html)、[FB-S018 ThreadPoolExecutor Java SE 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html)。

<a id="fb11"></a>

### FB11 如何手写安全的延迟单例，DCL 为什么必须关注发布

**优先级：P0**

**知识点详解**：静态字段提前初始化发生于类初始化，不是笼统的加载瞬间。延迟方案可以同步整个访问方法、静态持有者，或双重检查锁。DCL 外层检查避免每次加锁，内层检查防止两个等待线程重复构造，volatile 写与后续读建立 happens-before，使读到引用的线程看到初始化效果。volatile 不使对象所有后续操作都线程安全，也不是禁止程序中全部重排。锁是否成为瓶颈需要测量。

**具体例子**：配置对象构建昂贵且仅少数请求使用，可采用持有者模式。若需要显式展示 DCL，以下完整类用于讲清两个检查与 volatile；反射、序列化、类加载器隔离仍是额外约束。

**面试答法**：我优先选择容易证明的初始化方式；解释 DCL 时用安全发布关系，而不是只背“三条机器指令顺序”。

**追问**：枚举能替换任何延迟单例吗？它有类初始化和序列化语义优势，但初始化时机、继承与构造需求未必相同。

**常见误区**：只写一个外层 if；去掉 volatile；认为单例天然保证字段操作线程安全。

**完整 Java 示例（原创，已在 OpenJDK 21 编译并做并发获取测试）**：
```java
public final class DclSingleton {
    private static volatile DclSingleton instance;
    private final String mode;
    private DclSingleton() { this.mode = "ready"; }
    public static DclSingleton getInstance() {
        DclSingleton result = instance;
        if (result == null) {
            synchronized (DclSingleton.class) {
                result = instance;
                if (result == null) {
                    result = new DclSingleton();
                    instance = result;
                }
            }
        }
        return result;
    }
    public String mode() { return mode; }
}
```
持有者方案把对象放进静态内部类的 static final 字段，仅在访问该字段时触发内部类初始化；初始化安全由语言规范负责。验证时并发取实例检查引用一致与字段状态，但有限次测试不能替代 JMM 正确性证明。

**第二种完整实现：静态持有者（原创）**：
```java
public final class HolderSingleton {
    private final String mode;
    private HolderSingleton() { this.mode = "ready"; }
    private static final class Holder {
        private static final HolderSingleton INSTANCE = new HolderSingleton();
    }
    public static HolderSingleton getInstance() { return Holder.INSTANCE; }
    public String mode() { return mode; }
}
```
两个类分别保存为同名 Java 文件。该保证以一个定义类加载器为范围，不声称抵抗所有反射、克隆或定制序列化路径。

**实际验证**（2026-10-09）：OpenJDK 21.0.12.1 的编译器模块编译两个完整类与测试器；16 个工作线程共 10000 次获取，分别只观察到一个实例引用，mode 均为 ready；Future 逐一检查且线程池在 10 秒内结束。这个有限运行验证代码可用，不替代安全发布的规范证明，也未测试序列化、反射与多个类加载器。

可复验源码与运行命令见 [examples/backend](../../examples/backend/README.md)。

**来源**：[FB-S012 JLS 21 类初始化](https://docs.oracle.com/javase/specs/jls/se21/html/jls-12.html#jls-12.4)、[FB-S013 JLS 21 happens-before](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html#jls-17.4.5)。

<a id="fb12"></a>

### FB12 代理和适配器怎样在真实 API 中区分

**优先级：P1**

**知识点详解**：代理保持目标服务接口，在调用前后加入权限、事务或日志；适配器转换不同接口。Spring JDK 动态代理基于接口，CGLIB 以子类方式工作；final 类不能被继承代理，final/private 方法不能按普通覆写方式增强，目标内 self-invocation 通常绕过代理。Executors.callable(Runnable) 是把 Runnable 适配成 Callable，而不是反过来。InputStreamReader 把字节输入解码成字符输入，也需指定正确字符集。

**具体例子**：Controller 调用带事务代理的服务时增强生效，而同对象 this.save() 可能不经过代理。另一个例子是任务只有 run()，调用 Executors.callable(task, result) 后交给接受 Callable 的 API。

**面试答法**：我分别看“是否保留接口”和“是否转换契约”，再解释 Spring 代理入口和自调用边界。

**追问**：记录访问日志时应该记录什么？请求 ID、路由、耗时和结果类别；不能无差别记录密码、令牌和完整敏感正文。

**常见误区**：子类代理能增强所有方法；代理等于适配器；将 Executors.callable 的转换方向写反。

**来源**：[FB-S014 Executors Java SE 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/Executors.html)、[FB-S015 Spring AOP 代理机制](https://docs.spring.io/spring-framework/reference/core/aop/proxying.html)。

<a id="fb13"></a>

### FB13 拒绝策略为什么是策略模式，也是业务过载语义

**优先级：P0**

**知识点详解**：RejectedExecutionHandler 将任务被拒时的行为与线程池调度解耦。AbortPolicy 显式失败；CallerRunsPolicy 在调用线程执行且关闭时不执行；DiscardPolicy 丢弃；DiscardOldestPolicy 丢弃队首后尝试重交。选择取决于任务是否允许丢、调用方是否能阻塞、失败是否可重试。尤其 CompletableFuture 或等待结果的请求不能把静默丢任务当作成功。

**具体例子**：导出任务队列满时返回“系统忙，请稍后用相同任务键重试”，比静默丢弃更符合契约。若在网络事件循环使用 CallerRunsPolicy，重任务会阻塞事件循环并拖慢其他连接。

**面试答法**：我先定义拒绝对用户的可观察结果，再选策略，并记录拒绝率、队列年龄和恢复路径。

**追问**：最大线程数不大为什么仍排很多任务？无界队列通常先持续接纳任务，使 maximumPoolSize 难以发挥预期扩容作用。

**常见误区**：所有场景 CallerRuns 都能优雅背压；拒绝只在队列满时发生而忽略关闭状态。

**来源**：[FB-S018 ThreadPoolExecutor Java SE 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html)。

<a id="fb14"></a>

### FB14 模板方法与模板加回调的扩展方式有什么不同

**优先级：P1**

**知识点详解**：经典模板方法在父类固定算法骨架，由子类覆写步骤；模板加回调通过组合传入变化行为，不要求继承模板对象。JdbcTemplate 统一连接、语句和异常处理，把参数设置、结果映射等交给回调；因此可以说体现模板化资源管理思想，但不能把所有 Callback 都称为严格的继承式模板方法。

**具体例子**：查询商户时模板负责 JDBC 资源边界，RowMapper 负责把一行映射为商户 DTO。若在回调里把连接保存到全局变量延迟使用，就破坏了模板的生命周期约定。

**面试答法**：我先指出哪些步骤被固定、哪些步骤能定制，再说扩展点采用继承还是对象组合。

**追问**：为什么回调仍可能写出慢查询？模板减少样板代码，不自动优化 SQL、索引或连接池等待。

**常见误区**：用了 Template 名称就完全等于 GoF 模板方法；框架管理资源就不必考虑事务边界。

**来源**：[FB-S017 Spring JDBC 核心与回调](https://docs.spring.io/spring-framework/reference/data-access/jdbc/core.html)。
