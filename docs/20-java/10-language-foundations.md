# Java 语言基础补充：从对象语义到版本边界

[总目录](../../README.md) · [原语言题](01-language-and-collections.md)

规范语义以 Java SE 25 文档核查，兼顾 Java 8、17、21 项目；实现细节另标版本。代码为教学示例，尚未编译或运行。

<a id="fj01"></a>
### FJ01 JDK 8 到 25 的特性怎样回答才不会把预览当正式

**优先级：P1。**

**知识点详解**：版本题有三个坐标：语言语法、类库 API、虚拟机实现。还要分首次实验/预览、正式交付、弃用和移除。某功能能在 JDK 17 使用，不表示它首次出现在 17。面试先说自己实际使用的版本和两三个真正理解的变化，再解释迁移风险。

- Java 8：Lambda、Stream、接口 default 方法和 java.time，分别改变行为传递、集合流水线、接口演进和日期建模。Stream 不等于自动并行。
- Java 9：模块系统改变可读性/导出与反射边界；jlink 可组装运行时。Java 10 的局部变量 var 是静态类型推断，变量类型不会运行时任意改变。
- Java 11：标准 HTTP Client；可用于 Lambda 参数的 var 语法。不要把 10 的局部变量推断算成 11 首发。
- Java 14：switch 表达式正式；Java 15：文本块正式，ZGC 由实验转生产功能；Java 16：record、instanceof 模式匹配正式。record 简化数据载体，并不深度冻结其集合字段。
- Java 17：sealed classes 正式；Security Manager 标记为待移除弃用，尚未删除。模块强封装使依赖 JDK 内部反射的旧库更容易暴露问题。
- Java 21：虚拟线程、record patterns、模式 switch 正式。虚拟线程用于扩展阻塞 I/O 并发，不能提高 CPU 密集代码的单核速度。参见 [J21](02-concurrency-and-thread-pools.md#j21)。
- Java 22：Foreign Function & Memory API 正式；它不意味着任意本地调用都没有安全风险。
- Java 24：Stream Gatherers 正式；Security Manager 永久禁用，相关 API 并非全部从类库消失。synchronized 导致的虚拟线程 pinning 获得改进。
- Java 25：模块导入、紧凑源文件/实例 main、灵活构造器正式；基本类型模式匹配仍是第三次预览。预览功能须按相同版本配套编译、运行开关，不能当成长期兼容的稳定接口。

**具体例子**：团队从 8 升到 21，并不能只改编译器版本。先确认依赖是否访问 JDK 内部 API、构建目标字节码、默认编码/GC/启动参数差异，再跑功能、性能、回滚演练。若只是想用 record，仍需核查序列化框架支持及对象不变量。

**面试答法**：我按“解决的问题、正式版本、实际使用、迁移代价”回答。switch 表达式是 14，instanceof 模式是 16；17 的 Security Manager 是待移除弃用，24 才永久禁用；25 的基本类型模式仍是预览。

**追问**：LTS 是语言特性吗？不是，它是发行商支持政策，支持期限应查所用发行版。预览一定会转正吗？不会，可能修改或撤回。

**误区**：把“最新”当无条件推荐；把项目使用版本冒充新特性首发版本；说 JDK 17 已删除 Security Manager。

<a id="fj02"></a>
### FJ02 JVM、JRE、JDK 是什么，为什么现代 JDK 没有传统 jre 目录

**优先级：P0。**

**知识点详解**：JVM 是执行 class 文件的抽象机器及其实现；它还承担类加载、运行时执行、内存管理等职责。运行 Java 程序还需要标准类库、本地库等运行时组件，传统上将这组环境称为 JRE。JDK 面向开发，另有 javac、javadoc、jar、调试诊断等工具。于是“JDK 包含运行能力，运行环境包含 JVM”是概念关系，不能机械推导现代安装目录。

Java 9 的模块化运行时改变布局；Oracle JDK 11 不再单独提供旧式 JRE/Server JRE 下载。其他厂商仍可能发布运行时包。jlink 能针对模块依赖生成定制运行时，但遗漏反射、服务加载所需模块仍可能在运行时出错。JVM 可移植性来自相同字节码规范，不代表平台相关本地库也可直接跨系统复制。

**具体例子**：开发机用 javac 编译 Hello.java 得到 class；部署机可使用兼容的完整 JDK 或定制运行时启动，而不是把编译器拷过去就行。编译时目标为较新的 class 版本，旧 JVM 会报不支持的类版本；仅文件后缀相同不能保证兼容。

**面试答法**：JVM 执行字节码，运行环境还提供类库，JDK 再提供开发工具；现代模块化发行包不必有传统独立 JRE 目录。

**追问**：有 JDK 为什么仍可能找不到 javac？检查 PATH 和实际启动路径，而非立即重装。JIT 与 javac 一样吗？javac 主要从源代码生成字节码，JIT 在运行时编译热点代码。

**误区**：声称 JVM 只负责解释；把 Oracle 发行方式当成所有 JDK 厂商共同保证。

<a id="fj03"></a>
### FJ03 基本类型、装箱和拆箱有哪些隐藏边界

**优先级：P0。**

**知识点详解**：byte、short、int、long 的值分别是 8、16、32、64 位有符号整数；char 是 16 位无符号 UTF-16 代码单元，不能代表所有 Unicode 字符；float/double 对应 32/64 位二进制浮点。boolean 只有 true/false，语言规范没有承诺每个 boolean 变量固定占几个物理字节。数组元素、对象字段、局部变量槽、寄存器和对象对齐是不同层次，不能把一个层次的大小直接套给另一个。

装箱让 int 值在需要引用的位置转成 Integer；拆箱反向取值。常见编译结果调用 valueOf/intValue，但面试重点是语义：拆箱 null 会抛 NullPointerException，装箱会产生对象语义、缓存与分配成本。缓存只是某些值可能共享包装对象，不是业务相等性规则。Integer 与 Long 即使数值相同，equals 也不因此跨类型相等。金额还需明确十进制精度、舍入规则，不能因为 double 占 8 字节就认为可精确表示所有金额。

**具体例子**（未运行）：
```java
Integer quota = null;
// int n = quota;          // 拆箱导致 NullPointerException
Integer a = 1000, b = 1000;
boolean sameValue = a.equals(b); // true；不要依赖 a == b 的结果
int safe = quota == null ? 0 : quota;
```
`a == b` 比较对象身份；涉及一个基本数值操作数时又可能触发拆箱，所以先看静态类型。`"😀".length()` 是 2 个 UTF-16 单元，不是两个完整字符。

**面试答法**：数值宽度由语言规定，物理布局由实现影响；boolean 没有固定字节大小承诺。包装类型要防 null 拆箱、身份比较和大量装箱成本。

**追问**：long 变量一定需要一个堆对象吗？基本值本身不是包装对象。局部变量没赋值能读吗？编译器有明确赋值检查，不能套字段默认值。

**误区**：boolean 永远占 1 字节；用包装类的 == 比业务数值；把 char 等同于任意完整文字字符。

<a id="fj04"></a>
### FJ04 String 不可变意味着什么，StringBuffer 就能保证整段业务安全吗

**优先级：P0。**

**知识点详解**：String 的字符序列不能通过公开 API 原地改写。变量可以重新指向另一 String，这不是原对象变了；返回新内容的方法可能产生新对象，也可能在内容无需变化时返回原对象。不可变对象便于共享和作为稳定 Map 键，但“保存 String 的可变业务字段”仍可能存在并发覆盖。

StringBuilder 是可变字符构建器，适合线程私有的多次追加；StringBuffer 对需要的单个操作同步。一次 length 和一次 append 分别安全，不保证“长度未超限才追加”作为整体原子。可以把整个复合条件放在同一锁内，或更简单地每个请求拥有自己的 builder。不能脱离编译器优化、输入大小、同步开销说 builder 在任何情形都最快；短表达式字符串连接与循环拼接需分别评估。

**具体例子**：两个请求共享一个 StringBuffer 拼回答，即使底层结构不会被并发写坏，用户 A/B 的内容仍可能串在同一输出里。正确设计是每请求独立结果对象，并在需要跨线程传递完成结果时发布 String。

**面试答法**：String 不可变；Builder 用于私有可变构建；Buffer 提供方法级同步，但多步不变量还需整体协调。线程安全容器不能修复错误的业务共享模型。

**追问**：`final StringBuilder b` 能禁止 append 吗？不能，final 限制变量重新赋值。String 的内部表示一直是 char[] 吗？不是，内部编码是版本实现细节。

**误区**：String 每次方法调用必定 new；把 StringBuffer 当跨用户共享答案的合理方案。

<a id="fj05"></a>
### FJ05 封装、继承、多态、重载和重写怎样放进同一个例子

**优先级：P0。**

**知识点详解**：封装不只是 private 加 getter，而是让对象的方法守住不变量，例如余额不能任意被设置为负数。继承表达“是一种”，子类应履行父类型约定；如果只是复用代码，组合常能减少父子耦合。Java 类只有一个直接父类，但可实现多个接口。抽象类可有构造器、实例字段和具体方法，适合共享状态与实现；接口表达能力契约，可有 default、static 方法，Java 9+ 还支持 private 辅助方法，但没有普通实例字段和构造器。

重载是方法名相同、参数签名不同，可以包含继承得到的方法；不能只靠返回类型不同重载。编译期先依据表达式静态类型等规则决定具体签名。重写是子类提供父类可覆盖实例方法的实现；选定签名后，运行时按接收者实际类型动态分派。重写返回值可协变，不能缩小访问权限；不能扩大受检异常范围。static 方法是隐藏，private 方法不按普通继承重写，final 方法禁止重写。

**具体例子**（未运行）：
```java
interface Sender { String send(String text); }
abstract class BaseSender implements Sender {
    protected final String endpoint;
    BaseSender(String endpoint) { this.endpoint = endpoint; }
}
final class MailSender extends BaseSender {
    MailSender(String endpoint) { super(endpoint); }
    @Override public String send(String text) { return "queued:" + text; }
    public String send(String text, int retries) { return send(text); }
}
Sender sender = new MailSender("example");
sender.send("hello"); // 选中接口的 send(String)，动态执行 MailSender 实现
// sender.send("hello", 2); // 静态类型 Sender 没有这个重载
```
省略网络发送只是为了观察类型规则；此示例没有真的投递消息。

**面试答法**：封装保护状态，继承表达替代关系，多态让调用依赖抽象；重载在编译期选签名，重写在运行时选接收者实现。接口适合能力契约，抽象类适合共享实现和状态。

**追问**：两个接口有冲突 default 方法怎么办？实现类通常需显式覆盖消解冲突。为什么推荐 @Override？让编译器发现“本想重写却写成重载”的错误。

**误区**：把 Java 接口多实现说成类多继承；用返回类型区分重载；声称重写返回类型必须完全相同。

<a id="fj06"></a>
### FJ06 身份相等、值相等、浅拷贝和深拷贝怎样区分

**优先级：P0。**

**知识点详解**：引用的 == 判断是否指向同一对象或都为 null，不应把它解释成可见的物理内存地址比较。equals 是类型定义的逻辑相等；哈希契约见 [J01](01-language-and-collections.md#j01)。拷贝则讨论对象图：仅赋值引用没有复制对象；浅拷贝新建外层对象，但引用字段仍指向原来的内部对象；深拷贝按业务需要复制可变的内部图。

Object.clone 的常规语义是字段级复制，引用字段不会递归 clone。Cloneable 是允许相应 clone 行为的标记接口，不提供通用公开 clone 方法。实践中复制构造器或显式工厂更容易定义边界。不变 String 可以共享；对环和共享子节点，应记录“原对象→新对象”的身份映射，否则递归可能不结束，或把本应共享的节点错误拆成多份。序列化不是无条件可靠的深拷贝方案，类型、资源句柄、安全和性能都有限制。

**具体例子**（未运行）：
```java
var a = new java.util.ArrayList<StringBuilder>();
a.add(new StringBuilder("draft"));
var shallow = new java.util.ArrayList<>(a);
shallow.get(0).append("!"); // a 中同一 StringBuilder 也被修改
var deep = new java.util.ArrayList<StringBuilder>();
for (var s : a) deep.add(new StringBuilder(s.toString()));
```
后一方案只对该简单无环元素模型成立，不是任意对象图复制器。List.copyOf 也不深拷贝元素。

**面试答法**：== 看对象身份，equals 看逻辑值；浅拷贝复制外壳并共享内部引用，深拷贝需明确哪些可变状态要隔离，以及如何保留环和别名。

**追问**：不可修改集合能保证元素不变吗？不能。数据库连接应该被深拷贝吗？不应机械复制资源，通常重新建立或明确共享所有权。

**误区**：以为 new ArrayList(old) 克隆了每个元素；只要实现 Cloneable 就自动获得完整深拷贝。

对象图处理为基于这些语义的原创设计。

<a id="fj07"></a>
### FJ07 反射能做什么，为什么 setAccessible 不是万能钥匙

**优先级：P1。**

**知识点详解**：反射用 Class、Constructor、Method、Field 等元数据在运行时发现类型、构造实例和访问成员。框架可据注解完成注入、映射或方法调用；代价是把部分错误推迟到运行时，也增加访问控制、性能与版本兼容的复杂性。正常访问检查仍存在，`getDeclaredMethod` 找到 private 方法不等于可以直接调用。

Java 9+ 模块边界区分 exports 和 opens；跨模块深反射通常需要目标包向调用模块开放。trySetAccessible 可能返回 false，setAccessible 可能抛 InaccessibleObjectException。强封装意味着不能默认反射穿透任何 JDK 内部字段。可控插件系统应暴露受支持接口，而非通过任意类名反射执行用户输入。MethodHandle 是另一套调用能力，也需要正确 lookup 权限。

**具体例子**（未运行）：序列化库扫描自有 DTO 字段可以是合理需求；遇到第三方模块拒绝访问，先升级库或使用公开访问器。不要自动给整个进程加宽泛的 `--add-opens`，更不要把用户上传的类名直接传给 Class.forName 并执行构造器。

**面试答法**：反射提供运行时类型发现与调用，但受语言访问和模块开放规则限制。框架使用要缓存适当元数据、处理异常，并优先依赖稳定公共接口。

**追问**：反射方法抛业务异常时外层看到什么？Method.invoke 通常以 InvocationTargetException 包装目标异常。Class.forName 一定只是读取元数据吗？某些重载会触发初始化，应核对参数与 API。

**误区**：声称“任何属性方法都能访问”；把反射当规避授权的工具。

<a id="fj08"></a>
### FJ08 受检异常、RuntimeException 和 Error 应该怎样处理

**优先级：P0。**

**知识点详解**：Throwable 是异常体系根。Error 与 Exception 是不同分支；RuntimeException 是 Exception 子类。受检异常需要在编译期捕获或声明；RuntimeException、Error 及其子类属于非受检异常。非受检并不等于不会发生，Error 也不是语法上不可捕获，只是常表示常规业务难以合理恢复的运行时严重问题。

异常应沿有能力处理的边界传播。文件打不开可返回明确失败或重试符合条件的短暂故障；参数非法应早拒绝；OOM 后继续分配大量对象打印日志可能使情况更坏。try-with-resources 负责按规则关闭 AutoCloseable 资源，并保留关闭阶段的 suppressed exceptions；业务 finally 中 return 会掩盖原返回或异常，应避免。捕获后不能只打印并返回空结果，让调用方把失败当成功。

**具体例子**（未运行）：读取配置用 try-with-resources 包住输入流，向外抛带 cause 的配置加载异常，并在应用启动边界终止启动；不要 catch(Throwable) 后使用空配置继续服务。并发中的 InterruptedException 应传递或恢复中断状态，见 [J22](02-concurrency-and-thread-pools.md#j22)。

**面试答法**：受检与否是编译期约束；错误恢复取决于具体语义。只在有能力处理的边界捕获，保留 cause，保证资源释放，不吞异常伪装成功。

**追问**：声明 throws 是否处理了异常？没有，只把处理责任交给调用者。业务异常用 checked 还是 unchecked？要按 API 契约和团队错误处理方式设计，不能仅按严重程度机械决定。

**误区**：Error 不能 catch；所有 Exception 都是受检；finally 必定运行于进程被强制终止之后。
