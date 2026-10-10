# Linux 与容器

[返回总目录](../../README.md) · [题目索引](../../QUESTION_INDEX.md) · [版本与纠错](../../errata/README.md)

<a id="b42"></a>

### B42 进程、线程与协程有什么区别

**优先级：P0** 

**知识点详解**： 进程提供地址空间和资源组织边界；同一进程的线程共享许多进程资源，同时保有各自的栈与调度状态。协程是语言/运行时层面的并发抽象，如何映射到 OS 线程依赖运行时。并发表示任务推进有重叠，并行表示同一时刻确实在多个执行资源上运行。

**具体例子**： 两个线程修改同一内存对象要协调共享状态；两个独立进程不能仅靠同一变量名共享数据，需使用 IPC 或外部存储。

**面试答法**： 我从内存与资源共享、调度者、通信方式和故障边界比较，不把协程简单叫成更小的线程。

**追问**： 共享内存为什么快却难用？减少复制不等于自动同步，还要解决并发访问、生命周期和一致性。

**常见误区**： 认为线程有完全独立地址空间；认为并发数量等于 CPU 并行度。

**来源**： [BS58 Linux pthreads 手册](https://man7.org/linux/man-pages/man7/pthreads.7.html)、[BS75 Go FAQ Goroutines](https://go.dev/doc/faq#goroutines)。

<a id="b43"></a>

### B43 epoll 的 I/O 多路复用为什么有用

**优先级：P1** 

**知识点详解**： 多路复用让程序同时等待多个文件描述符上的就绪事件，不必为每个闲置连接忙等。epoll 维护关注集合并返回就绪事件；LT 与 ET 的通知方式不同，ET 常需配合非阻塞 I/O 并持续读写到 EAGAIN。就绪表示操作可能推进，不等于整条业务消息已到齐。

**具体例子**： 聊天服务器有大量连接但只有少量活跃，用事件通知处理就绪连接，再由应用层协议组装完整消息。

**面试答法**： epoll 帮助处理大量连接的等待问题；应用仍要处理非阻塞读写、消息边界和慢客户端。

**追问**： ET 下只读一部分就返回循环有什么风险？剩余数据若没正确读尽，可能不能按预期获得后续边沿通知。

**常见误区**： 说 epoll 自动处理业务并发；把所有操作与总成本都概括成恒定 O(1)。

**来源**： [BS59 Linux epoll 手册](https://man7.org/linux/man-pages/man7/epoll.7.html)。

<a id="b44"></a>

### B44 容器与虚拟机怎么区分，namespace 和 cgroup 分别做什么

**优先级：P0** 

**知识点详解**： Linux 容器是受隔离与资源管理约束的进程环境，通常共享宿主内核；虚拟机通常包含独立客户机内核。namespace 让进程看见不同的进程号、网络等视图；cgroup 组织进程并控制 CPU、内存等资源。隔离视图和限制资源不是同一个功能。

**具体例子**： 容器里只看见少量进程，不表示宿主机只有这些进程；设置内存上限后，应用仍可能因达到限制被终止。

**面试答法**： 我用“看到什么”解释 namespace，用“能用多少”解释 cgroup，再说明共享内核与权限边界。

**追问**： 为什么容器能启动但访问不到另一个容器的 localhost？不同网络命名空间里的回环地址不是同一台应用的入口。

**常见误区**： 认为容器是完整虚拟机；认为只要用了容器就无需考虑权限、内核与密钥安全。

**来源**： [BS60 Linux namespaces](https://man7.org/linux/man-pages/man7/namespaces.7.html)、[BS61 Linux cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)、[BS62 Docker 容器概念](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/)。

<a id="b45"></a>

### B45 镜像构建和健康检查，实习生要懂到什么程度

**优先级：P1** 

**知识点详解**： 多阶段构建把编译工具与最终运行环境分开，最终镜像只保留所需产物。Kubernetes 的 startup probe 检查启动是否完成，readiness 判断能否接流量，liveness 判断是否需要重启。健康检查应匹配应用状态，不能把所有依赖抖动都转换为重启。

**具体例子**： Go 服务在构建阶段编译，再复制到较小运行镜像；数据库短暂不可用时，应用可能暂时不 ready，但不一定需要让 liveness 失败而反复重启。

**面试答法**： 我能说明镜像内容、配置注入、端口、资源限制和探针用途，并复现一次依赖故障下的行为。

**追问**： 为什么启动很慢的服务需要 startup probe？避免启动尚未完成时被正常存活检查不断重启。

**常见误区**： 把密钥写进 Dockerfile；readiness 与 liveness 永远共用一个只返回 200 的接口。

**来源**： [BS63 Docker 多阶段构建](https://docs.docker.com/build/building/multi-stage/)、[BS64 Kubernetes Probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/)。

<a id="b46"></a>

### B46 优雅退出怎样避免发布时丢请求

**优先级：P0** 

**知识点详解**： 优雅退出先停止接收新工作，再在有限宽限期内处理在途工作、释放连接和保存必要状态。SIGTERM 可以被应用处理；SIGKILL 不能被捕获执行清理。容器编排终止有宽限期，应用必须让自身收尾预算与平台配置相容。

**具体例子**： 收到终止信号后，服务进入不接新任务状态；HTTP 在途请求等待完成，消费者停止拉新消息并完成可提交的处理。到达截止时间后按设计终止，未完成任务依赖重试与幂等恢复。

**面试答法**： 我会解释摘流、停止拉取、在途等待和最终期限，并测试退出期间的客户端错误与重复消息。

**追问**： 所有任务都等完再退一定更好吗？长流或卡死依赖可能永不结束，因此必须有上限和恢复策略。

**常见误区**： 只监听信号但立即关闭数据库；先提交未处理消息位点；把强制 kill 当成优雅关闭。

**来源**： [BS65 Linux signal 手册](https://man7.org/linux/man-pages/man7/signal.7.html)、[BS66 Kubernetes Pod 生命周期](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)。

<a id="b47"></a>

### B47 服务突然变慢，如何从 Linux 走到应用定位

**优先级：P0** 

**知识点详解**： 慢不一定是 CPU 忙，也可能等待网络、磁盘、锁或连接池。Linux /proc 提供进程与系统状态；Go 的 profiling、tracing 等诊断工具能进一步观察热点、分配和执行。排查应先界定影响范围与时间，再逐层验证假设。

**具体例子**： 先看错误和延迟何时上升，再看进程 CPU、内存、文件描述符与连接数；CPU 高则分析 CPU profile，内存持续增长则看 heap 与分配，CPU 不高但延迟高则查等待链、慢 SQL 和下游 trace。

**面试答法**： 我会按现象建立假设，用指标和 profile 验证，最后做同条件复测；不会第一步就重启抹掉证据。

**追问**： 线上开启诊断有什么注意点？采样与追踪有成本，调试入口应受限并避免暴露敏感数据。

**常见误区**： 只背 top、ps 命令却不解释看到什么；凭单个瞬时 CPU 值下结论。

**来源**： [BS67 Linux /proc 文档](https://docs.kernel.org/filesystems/proc.html)、[BS68 Go Diagnostics](https://go.dev/doc/diagnostics)。

本节题号：B42、B43、B44、B45、B46、B47。原有题号保持稳定，补充主题另行编号。
