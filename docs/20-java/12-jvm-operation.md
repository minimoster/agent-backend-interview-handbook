# JVM 运行、垃圾回收与诊断补充

[总目录](../../README.md) · [原 JVM 题](03-jvm-and-classloading.md)

规范概念以 Java SE 25 核查；HotSpot 专有部分标明实现。诊断命令和过程均为未运行教学示例，需在获得授权的测试环境验证；抓取堆转储可能暂停应用、写入大量数据并暴露敏感信息。

<a id="fj13"></a>
### FJ13 一个对象从创建到回收会经历什么，GC Roots 为什么不能死背

**优先级：P0。**

**知识点详解**：执行 new 时需要相应类的加载、链接以及必要初始化；分配实例存储，建立字段默认值，然后执行初始化与构造器语义。实际执行可被解释器/JIT 优化；HotSpot 常用线程本地分配缓冲 TLAB 减少常规分配竞争。逃逸分析若证明对象不需要以完整对象形式存在，可进行标量替换，不能据源代码 new 数量反推物理分配次数。对象头、类型信息和身份哈希的布局属于实现；身份哈希通常在需要时生成，不是每个对象一创建就计算并固定写入头部。

垃圾追踪从虚拟机认定的根开始，沿强引用找可达对象；活跃线程栈、JNI 引用及虚拟机内部存活结构是根来源的典型例子。静态字段能让对象经存活的类结构保持可达，但这不意味着所有 static、字符串池内容或曾被锁过的对象都永远不能回收。类加载器可回收时，相应类有机会卸载；具体根集合和工具分类需按收集器、时刻理解。运行时常量池也不只是几个编译期字符串常量。

不可达只是进入相应回收处理的前提，不等于该行代码后立刻释放内存；软、弱、虚引用有不同处理规则。Java 的可达性追踪能处理孤立循环，不能把单纯引用计数的弱点推广到所有语言运行时。例如 CPython 在引用计数之外还提供循环垃圾收集器，不能说 Python 一律无法回收环。现代 HotSpot 的类元数据在元空间，但 String 实例和普通静态字段引用的业务对象不能因此归入元空间。

**具体例子**：请求创建 Node A/B，彼此互指；若没有根能到达，循环本身不阻止回收。反之，静态缓存 map 留着 A，即便请求结束，两个对象都可能被保留。修复对象保留路径比“手动置空所有局部变量”更有用。

**面试答法**：创建流程讲规范与优化两层；回收看根可达性及引用类型，不按业务是否用完。静态字段和字符串池不是永生证明。

**追问**：方法区等于 JMM 吗？不同，见 [J09](02-concurrency-and-thread-pools.md#j09)。弱引用能保存不可丢的唯一业务状态吗？不合适。

**误区**：每个 new 都一定物理堆分配；对象头必有已计算 hash；所有静态内容都在元空间且永不回收。

**一手来源**：[FJ-S009 JVM 数据区](https://docs.oracle.com/javase/specs/jvms/se25/html/jvms-2.html)、[FJ-S036 JLS 实例创建与类卸载](https://docs.oracle.com/javase/specs/jls/se25/html/jls-12.html)、[FJ-S037 引用处理](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ref/package-summary.html)、[FJ-S038 HotSpot 同步与身份哈希源码](https://github.com/openjdk/jdk25u/blob/master/src/hotspot/share/runtime/synchronizer.cpp)、[FJ-S039 java 命令与逃逸分析选项](https://docs.oracle.com/en/java/javase/25/docs/specs/man/java.html)、[FJ-S132 HotSpot 字符串表弱句柄](https://raw.githubusercontent.com/openjdk/jdk25u/master/src/hotspot/share/classfile/stringTable.cpp)、[FJ-S134 CPython 循环收集器](https://docs.python.org/3/library/gc.html)。

<a id="fj14"></a>
### FJ14 分代、CMS、G1 与 Full GC 的名词怎样连起来

**优先级：P1。**

**知识点详解**：分代假说是一种经验规律：很多对象很快死亡，活得久的对象更可能继续存活。按寿命组织回收可减少每次扫描范围，但跨代引用需要记忆集/屏障等机制配合。复制、清除、压缩是算法手段，年轻代/老年代是组织方式，G1/CMS/ZGC 是具体收集器；不要混成同一个分类轴。复制也不要求把整个堆永远等分成两个半区。

CMS 是历史性的并发标记清除收集器，常见流程包含初始标记、并发标记、重新标记和并发清理，仍有停顿、碎片及并发失败边界。CMS 在 JDK 14 已移除，现代部署不应套用它的参数。G1 将堆分为 Region，通过标记判断存活情况并选择回收集合，暂停阶段疏散存活对象；年轻代回收和包含部分老年代 Region 的 mixed collection 都要结合日志解释。停顿目标是优化目标，不是硬实时上限。

ZGC 和 Shenandoah 代表把更多移动/整理相关工作并发化的低停顿方向，所支持模式、代际和默认值依 JDK/发行版而变。Java 25 的 ZGC 已采用分代实现，不能继续概括为“ZGC 从不分代”；不是所有发行包都一定带相同 GC 选择。

“Minor/Young GC”常指年轻代事件；“Major GC”缺少跨收集器统一定义；“Full GC”应引用该收集器日志事件，不要自动等同所有代、元空间和所有引用都清空。元空间本来就不是 Java 堆的一代，类仍存活时也不会因 Full GC 自动卸载。

**具体例子**：看到 G1 Mixed GC 不能直接判断发生了昂贵 Full GC。先看日志中的事件名称、原因、暂停时间和回收前后占用，再与接口尾延迟对齐。若年轻代每秒回收但暂停很短且吞吐正常，不应仅因次数多就认定故障。

**面试答法**：把经验假说、回收算法、收集器和日志事件分开；CMS 是历史实现，G1 有 Region 和疏散，低停顿 GC 仍需 CPU/内存余量及测量。

**追问**：并发 GC 等于没有 STW 吗？不等于。调大堆能自动消除泄漏吗？只可能推迟耗尽。

**误区**：老年代一定用标记清除；所有 GC 都有同一 Full/Major 定义；G1 保证每次暂停不超过目标毫秒数。

**一手来源**：[FJ-S040 G1 指南](https://docs.oracle.com/en/java/javase/25/gctuning/garbage-first-g1-garbage-collector1.html)、[FJ-S041 JDK 14 迁移指南](https://docs.oracle.com/en/java/javase/14/migrate/index.html)、[FJ-S042 Java 25 GC 指南](https://docs.oracle.com/en/java/javase/25/gctuning/hotspot-virtual-machine-garbage-collection-tuning-guide.pdf)、[FJ-S043 JEP 379 Shenandoah](https://openjdk.org/jeps/379)、[FJ-S133 Java 8 历史 CMS 流程](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/cms.html)。

<a id="fj15"></a>
### FJ15 频繁 Full GC、OOM、栈溢出该按什么顺序查

**优先级：P0。**

**知识点详解**：先区分症状和原因。StackOverflowError 通常指调用栈需求超过允许深度，它不是 OutOfMemoryError 的子类。OOM 可能来自 Java heap、元空间、直接内存，或本地线程等资源不足；容器 OOM kill 还可能由进程总内存超限触发，不一定先有 Java 异常。只调 Xmx 既可能无效，也可能挤压线程栈、直接内存和本地库空间。

排查顺序：
1. 记录 JDK/收集器/进程参数/容器限制，读错误具体文本和发生时间。
2. 对齐分配速率、GC 原因、暂停、GC 后存活量、类加载数量、线程数和请求流量。分清堆确实保留增长，还是瞬时大输入、元数据压力或配置过小。
3. 对持续堆增长，受控比较对象直方图和堆转储的 dominator/根引用链；对本地内存看相应监控及已启用的 Native Memory Tracking，而不是继续只看堆。
4. 修改有证据的根因，例如有界缓存、释放线程局部值、限制批量读入，之后在同负载下复测存活量与 p99。参数优化要有前后指标及回滚计划。

常用参数按目的记：Xms/Xmx 控制堆初始/上限；Xss 控制线程栈相关大小；MaxMetaspaceSize 约束元空间；MetaspaceSize 主要是首次触发类元数据 GC 的阈值，并非固定预分配容量；`-Xlog:gc*` 属于 JDK 9+ 统一日志；`-XX:+HeapDumpOnOutOfMemoryError` 与 HeapDumpPath 影响故障证据。旧 CMS 与旧日志开关先查目标版本，不能把网上参数列表整包粘贴。

**具体例子**（未运行）：测试环境可先按实际启动方式加入 `-Xlog:gc*:file=gc.log:time,uptime,level,tags`；日志文件需轮转和空间预算。若每次 GC 后 heap 都从 700MB 回到 150MB，但 p99 仍高，重点未必是内存泄漏，还要查暂停/CPU/外部依赖。

**面试答法**：先确认耗尽区域和 GC 触发原因，再找保留对象或资源边界，最后验证修复；不把 Full GC 次数当结论，也不直接照抄调参。

**追问**：增加 Xss 有何副作用？每线程资源预算上升，可能减少可创建线程数。为什么生产 dump 必须谨慎？停顿、磁盘和敏感数据风险。

**误区**：StackOverflowError 就是堆 OOM；元空间设大就不会泄漏；Xmx 等于进程总内存。

**一手来源**：[FJ-S044 Oracle 内存问题诊断](https://docs.oracle.com/en/java/javase/25/troubleshoot/troubleshooting-memory-leaks.html)、[FJ-S039 java 参数](https://docs.oracle.com/en/java/javase/25/docs/specs/man/java.html)、[FJ-S009 JVM 错误条件](https://docs.oracle.com/javase/specs/jvms/se25/html/jvms-2.html)。

<a id="fj16"></a>
### FJ16 自定义类加载器为什么不能只写一段“先自己加载”

**优先级：P1。**

**知识点详解**：标准 ClassLoader.loadClass 的典型路径是先查 findLoadedClass，再委派父加载器，再由 findClass 查找并定义，必要时解析；类加载同步避免同一加载器并发重复定义。自定义常先覆盖 findClass 保留正常委派，只有确实需要隔离时再有意识改变 loadClass 的顺序。

父优先使共同基础类型尽可能由同一父加载器定义，减少“同名却无法强转”。但类型身份由二进制名与定义加载器共同决定；父优先不是完整安全沙箱，定义 java.* 包等还受独立限制。插件可对子集采用 child-first，同时将共享 API 委派给父加载器。要定义包白名单、资源查找顺序、加载锁、失败回退与 close/卸载生命周期，不能复制三行伪代码就声称生产可用。

**具体例子**（设计示例，未运行）：宿主与插件都使用 `api.Task`。让该接口由父加载器定义；插件私有的某 JSON 依赖才隔离加载。否则宿主接到“api.Task”对象时仍可能因定义加载器不同而 ClassCastException。卸载插件时停止其线程、移除注册表和 ThreadLocal 引用，否则加载器仍可达，类元数据也可能长期保留。

**面试答法**：改查找顺序之前先定义隔离边界；保留已加载检查和并发协议，共享 API 统一由父加载器提供，避免同名不同类型。

**追问**：加载即初始化吗？不必，见 [J28](03-jvm-and-classloading.md#j28)。线程上下文加载器有什么作用？让框架按调用环境查找服务实现，不能简单说它总是推翻所有父委派。

**误区**：覆盖 loadClass 后不调用 findLoadedClass；子优先能随意伪造 java.lang.String；只有清空一个引用就一定立刻卸载。

**一手来源**：[FJ-S045 ClassLoader](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ClassLoader.html)、[FJ-S036 JLS 执行与类卸载](https://docs.oracle.com/javase/specs/jls/se25/html/jls-12.html)。
