# Linux：安全操作与证据采集

[返回总目录](../../README.md) · [题目索引](../../QUESTION_INDEX.md) · [版本与纠错](../../errata/README.md)

官方资料核查于2026-10-09。示例参数用于教学推演，代码、SQL 与实验的执行情况在对应题中标注。

- [FB64 常用文件命令怎样操作才不把排障变成事故](#fb64)
- [FB65 怎样定位进程并优雅终止，何时才用 KILL](#fb65)
- [FB66 top、free、vmstat、df、du 各能证明什么](#fb66)

<a id="fb64"></a>

### FB64 常用文件命令怎样操作才不把排障变成事故

**优先级：P0**

**知识点详解**：先用 pwd、ls -la、stat 核对目录与目标，读文件可用 less、head/tail、grep；mkdir -p 创建目录，touch 更新时戳或创建空文件。重定向 > 会截断已有文件，>> 才是追加。mv、cp、rm 的覆盖与提示由参数和环境决定，不能假设 rm 默认逐项确认。权限 rwx 对目录含遍历/列名/修改目录项等不同语义，chmod 前应核对所有者、组与最小需求，避免全局 777。

**具体例子**：只想建空日志文件时，touch app.log 不会清空原内容，而 >app.log 会截断。编辑配置先保存可恢复副本、核对 diff；vim 的 i 进入插入，Esc 回普通模式，:w 保存，:q 退出，:q! 丢弃未保存修改，理解后再使用。

**面试答法**：我先定位并只读检查，最小化修改范围；危险操作展示精确目标，区分重命名、复制、截断和删除。

**追问**：为什么对目录有写权限可能影响文件删除？删除的是目录项，不能只看文件本身是否可写。

**常见误区**：rm 默认都问确认；touch 和重定向等价；chmod 777 是权限问题通用修复。

**来源**：[FB-S047 GNU Coreutils rm 命令手册](https://www.gnu.org/s/coreutils/manual/html_node/rm-invocation.html)、[FB-S103 GNU Coreutils touch 命令手册](https://www.gnu.org/software/coreutils/manual/coreutils.html#touch-invocation)、[FB-S104 GNU Coreutils chmod 命令手册](https://github.com/coreutils/coreutils/blob/master/man/chmod.x)、[FB-S105 Vim 官方帮助 Quick Reference](https://vimhelp.org/quickref.txt.html)。

<a id="fb65"></a>

### FB65 怎样定位进程并优雅终止，何时才用 KILL

**优先级：P0**

**知识点详解**：用 ps 的 PID、用户、完整命令及启动时间识别目标，pgrep 时限定进程名、用户或更具体模式，避免宽泛匹配。先发送 TERM，给程序停止接收、排空请求与释放资源的时间；必要时经过确认再 KILL。SIGKILL 不能被捕获或忽略，因此没有清理机会，但处于不可中断内核等待的任务也不保证立即消失。信号送达与进程终止结果需分开检查。

**具体例子**：同机器有测试与生产两个同名 Java 进程，只用 pkill java 会同时命中；应先确认精确 PID 和命令行，再看退出后的端口、子进程与管理器是否重启它。本文不执行这些变更命令。

**面试答法**：我先确保对象正确，再走服务管理器支持的优雅停止；超时后调查阻塞原因，最后才升级信号。

**追问**：PID 会复用有什么风险？较早记录的 PID 可能已属于另一进程，执行前重新核对身份。

**常见误区**：kill 等于 SIGKILL；KILL 允许 finally 清理；发送成功等于目标立即消失。

**来源**：[FB-S048 Linux signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html)、[FB-S056 Linux proc_pid_stat(5)](https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html)。

<a id="fb66"></a>

### FB66 top、free、vmstat、df、du 各能证明什么

**优先级：P0**

**知识点详解**：top 看进程/线程 CPU 与调度状态；free 需要结合 available 与缓存理解可用内存；vmstat 看运行队列、上下文切换、换页和 I/O 等变化；df 看文件系统已分配空间，du 统计可遍历文件所占空间，两者因打开的已删除文件、快照等可不同。磁盘利用率高不一定等于吞吐高，还要看延迟、队列深度和设备特性；容器限制需结合 cgroup 观察。

**具体例子**：主机还有空闲内存，但容器 memory.max 较小，应用仍可能因 cgroup 限制退出。另一例 df 满而 du 不大，要检查权限范围及打开的已删除文件，不能立即删除随机目录。

**面试答法**：我把 CPU、内存、磁盘容量与 I/O 延迟分开，先看趋势和相关性，再与应用请求耗时关联。

**追问**：load average 高就是 CPU 满吗？还可能有不可中断等待，需结合任务状态、CPU 利用率与 I/O 指标。

**常见误区**：free 的 free 数值低就是泄漏；du 与 df 不同必是工具坏；一次截图足够解释间歇故障。

**来源**：[procps-ng top(1)](https://man7.org/linux/man-pages/man1/top.1.html)、[procps-ng free(1)](https://man7.org/linux/man-pages/man1/free.1.html)、[procps-ng vmstat(8)](https://man7.org/linux/man-pages/man8/vmstat.8.html)、[GNU Coreutils df](https://www.gnu.org/software/coreutils/manual/html_node/df-invocation.html)、[GNU Coreutils du](https://www.gnu.org/software/coreutils/manual/html_node/du-invocation.html)、[FB-S050 Linux cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)。
