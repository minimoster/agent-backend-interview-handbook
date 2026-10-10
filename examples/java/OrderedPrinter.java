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
