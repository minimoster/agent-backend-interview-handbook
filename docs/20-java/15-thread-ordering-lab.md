# 三线程顺序输出：包含取消协议的可运行练习

[总目录](../../README.md) · [完整可运行源文件](../../examples/java/OrderedPrinter.java) · [并发基础](02-concurrency-and-thread-pools.md)

<a id="fj46"></a>
### FJ46 三个线程如何按 ABC 顺序循环输出，并在中断时全部退出

**优先级：P0。**

**知识点详解**：线程启动顺序和操作系统调度顺序不能保证输出顺序。这里使用共享 next 作为轮次状态，线程角色分别是0/1/2，只有 `(next-1)%3 == role` 时才在锁内产生下一条数字与字母记录，角色0/1/2分别产生A/B/C。相同锁保护 next、cancelled 和输出列表，Condition负责在轮次未到时等待。while反复检查条件应对虚假唤醒、竞争变化和取消；signalAll唤醒竞争者，真正谁能推进由条件决定。

如果只写三个Semaphore轮流release，某线程在获取后中断/异常退出而未交接，另外两者可能永久等待。这个实现增加全局取消标志：任一参与者中断或运行失败，都设置取消并唤醒所有等待者；完成最后一项也唤醒所有人，使其检查退出条件。协调线程负责启动、带截止时间join，并在自身中断/超时后取消、interrupt和再次join清理。所有unlock在finally中。

**具体例子与完整代码**：代码在Java21语言级别编写，先将有序结果记入受锁保护列表，join全部线程后再由协调者打印，避免在临界区做慢终端I/O。取消演示返回已完成的有序前缀，主程序明确按取消分支检查，不能把部分输出当作全部任务成功。生产API应返回带取消状态的结果，或抛CancellationException。

将以下完整代码保存为OrderedPrinter.java，可用 `java OrderedPrinter.java` 启动。它不连接外部服务、不修改用户数据。

```java
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.ReentrantLock;

public final class OrderedPrinter {
    record Item(int role, int number, char letter) {}

    static final class State {
        private final ReentrantLock lock = new ReentrantLock();
        private final Condition changed = lock.newCondition();
        private final int limit;
        private int next = 1;
        private boolean cancelled;
        private final List<Item> output = new ArrayList<>();

        State(int limit) {
            if (limit < 0) throw new IllegalArgumentException("negative limit");
            this.limit = limit;
        }

        void run(int role) throws InterruptedException {
            lock.lockInterruptibly();
            try {
                for (;;) {
                    while (!cancelled && next <= limit && (next - 1) % 3 != role) {
                        changed.await();
                    }
                    if (cancelled || next > limit) {
                        changed.signalAll();
                        return;
                    }
                    if (Thread.currentThread().isInterrupted()) {
                        throw new InterruptedException("worker interrupted");
                    }
                    // Record the output atomically; console I/O happens after joins.
                    output.add(new Item(role, next++, (char) ('A' + role)));
                    changed.signalAll();
                }
            } finally {
                lock.unlock();
            }
        }

        void cancel() {
            lock.lock(); // Complete the cancellation even if caller is interrupted.
            try {
                cancelled = true;
                changed.signalAll();
            } finally {
                lock.unlock();
            }
        }

        List<Item> snapshot() {
            lock.lock();
            try { return List.copyOf(output); }
            finally { lock.unlock(); }
        }
    }

    static boolean joinUntil(Thread[] workers, long deadline) throws InterruptedException {
        for (Thread worker : workers) {
            while (worker.isAlive()) {
                long remaining = deadline - System.nanoTime();
                if (remaining <= 0) return false;
                TimeUnit.NANOSECONDS.timedJoin(worker, remaining);
            }
        }
        return true;
    }

    static void cleanup(Thread[] workers, State state, CountDownLatch start) {
        state.cancel();
        start.countDown();
        for (Thread worker : workers) worker.interrupt();
        boolean interrupted = false;
        long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
        try {
            for (;;) {
                try {
                    if (!joinUntil(workers, deadline)) {
                        throw new IllegalStateException("workers did not terminate");
                    }
                    return;
                } catch (InterruptedException e) {
                    interrupted = true; // Finish cleanup, then restore caller status.
                }
            }
        } finally {
            if (interrupted) Thread.currentThread().interrupt();
        }
    }

    static List<Item> execute(int limit, String mode) throws InterruptedException {
        State state = new State(limit);
        CountDownLatch start = new CountDownLatch(1);
        AtomicReference<Throwable> failure = new AtomicReference<>();
        Thread[] workers = new Thread[3];
        for (int i = 0; i < 3; i++) {
            final int role = i;
            workers[i] = new Thread(() -> {
                try {
                    start.await();
                    if (mode.equals("failure") && role == 1) {
                        throw new IllegalStateException("injected failure");
                    }
                    state.run(role);
                } catch (InterruptedException e) {
                    state.cancel();
                    Thread.currentThread().interrupt();
                } catch (RuntimeException | Error e) {
                    failure.compareAndSet(null, e);
                    state.cancel();
                    // Failure is reported to the joining coordinator below.
                }
            }, "printer-" + role);
        }
        boolean joined = false;
        try {
            for (Thread worker : workers) worker.start();
            if (Thread.interrupted()) throw new InterruptedException("coordinator interrupted");
            if (mode.equals("interrupt")) workers[1].interrupt();
            start.countDown();
            joined = joinUntil(workers,
                    System.nanoTime() + TimeUnit.SECONDS.toNanos(5));
            if (!joined) throw new IllegalStateException("execution timed out");
            if (failure.get() instanceof Error error) throw error;
            if (failure.get() != null) {
                throw new IllegalStateException("worker failed", failure.get());
            }
            return state.snapshot();
        } finally {
            if (!joined) cleanup(workers, state, start);
        }
    }

    static void verifyPrefix(List<Item> output) {
        for (int i = 0; i < output.size(); i++) {
            Item item = output.get(i);
            if (item.number() != i + 1 || item.role() != i % 3 || item.letter() != 'A' + i % 3) {
                throw new AssertionError("invalid ordering at " + i);
            }
        }
    }

    public static void main(String[] args) throws InterruptedException {
        List<Item> normal = execute(30, "normal");
        verifyPrefix(normal);
        if (normal.size() != 30) throw new AssertionError("missing output");
        for (Item item : normal) {
            System.out.print("T" + item.role() + ":" + item.number() + " ");
        }
        System.out.println();
        StringBuilder letters = new StringBuilder();
        for (Item item : normal) letters.append(item.letter());
        if (!letters.toString().equals("ABC".repeat(10))) {
            throw new AssertionError("wrong letter order");
        }
        System.out.println(letters);
        for (int run = 0; run < 100; run++) {
            List<Item> result = execute(run % 37, "normal");
            verifyPrefix(result);
            if (result.size() != run % 37) throw new AssertionError("wrong length");
        }
        List<Item> interrupted = execute(30, "interrupt");
        verifyPrefix(interrupted);
        if (interrupted.size() >= 30) throw new AssertionError("cancellation not observed");
        try {
            execute(30, "failure");
            throw new AssertionError("failure not propagated");
        } catch (IllegalStateException expected) {
            if (expected.getCause() == null) throw expected;
        }
        AtomicReference<Throwable> coordinatorFailure = new AtomicReference<>();
        Thread coordinator = new Thread(() -> {
            Thread.currentThread().interrupt();
            try {
                execute(30, "normal");
                coordinatorFailure.set(new AssertionError("interruption not propagated"));
            } catch (InterruptedException expected) {
                // execute() has already cancelled and joined its worker threads.
            } catch (Throwable unexpected) {
                coordinatorFailure.set(unexpected); // Test harness records failure.
            }
        }, "coordinator-test");
        coordinator.start();
        coordinator.join(6000);
        if (coordinator.isAlive() || coordinatorFailure.get() != null) {
            throw new AssertionError("coordinator cleanup failed", coordinatorFailure.get());
        }
        System.out.println("PASS: ABC x 10, 101 normal cases, worker interruption, worker failure, coordinator interruption; all workers joined");
    }
}
```

**验证记录（2026-10-09）**：实际用OpenJDK 21.0.12.1源文件启动器执行通过：ABC循环10轮的精确字符串断言（`ABC.repeat(10)`），以及101个正常样例（含0上限及多种非3倍数上限）、工作线程中断、工作线程注入异常、协调线程已被中断的清理分支。断言验证每个数字恰出现一次、所属角色正确、正常结果完整，全部参与线程结束并join。输出首段为 `T0:1 T1:2 T2:3`，末段为 `T0:28 T1:29 T2:30`；还输出 `ABCABCABCABCABCABCABCABCABCABC`，末行打印PASS。字母由三个工作线程按轮次条件产生，主线程只展示已生成的序列，不是依靠创建顺序拼接伪造并发正确性。这里没有把有限次测试当成任意调度下的形式化证明，也未模拟JVM崩溃、强制杀进程或OOM恢复。

**面试答法**：用一份受锁保护的轮次状态决定谁能推进，Condition只负责等待/唤醒；while检查，finally释放，取消时唤醒全体，主线程join验证结束。顺序来自状态机，不来自sleep或线程创建顺序。

**追问**：为什么不用signal？一个共享Condition上可能叫醒不是下一角色的线程，没人继续推进；signalAll加条件检查更直接。是否能用三个Condition减少无效唤醒？可以，但取消/结束时仍需广播所有条件队列。公平锁是否必要？不必要，业务轮次条件负责顺序；仍假设线程最终能被调度。

**误区**：sleep轮询能证明顺序；只处理正常路径而忽略某参与者消失；以daemon线程掩盖永久等待；捕获中断后继续无限循环。

**一手来源**：[FJ-S127 Condition等待语义](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/locks/Condition.html)、[FJ-S050 ReentrantLock](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/locks/ReentrantLock.html)、[FJ-S128 Thread启动与join](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Thread.html)。
