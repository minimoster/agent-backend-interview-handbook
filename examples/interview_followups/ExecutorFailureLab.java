import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** Original finite Java 21 API-contract exercises. No network or throughput claims. */
public class ExecutorFailureLab {
    static int cases;
    static void check(boolean value, String message) { if (!value) throw new AssertionError(message); }
    static void await(CountDownLatch latch) throws InterruptedException {
        check(latch.await(3, TimeUnit.SECONDS), "coordination did not finish");
    }
    static ThreadPoolExecutor pool(RejectedExecutionHandler handler) {
        return new ThreadPoolExecutor(1, 1, 0, TimeUnit.SECONDS,
            new ArrayBlockingQueue<>(1), handler);
    }
    static void stop(ExecutorService pool) throws InterruptedException {
        pool.shutdownNow();
        check(pool.awaitTermination(3, TimeUnit.SECONDS), "worker did not terminate");
    }
    static Runnable held(CountDownLatch entered, CountDownLatch release) {
        return () -> { entered.countDown(); try { release.await(); }
            catch (InterruptedException e) { Thread.currentThread().interrupt(); } };
    }
    static void boundedReject() throws Exception {
        var p=pool(new ThreadPoolExecutor.AbortPolicy()); var e=new CountDownLatch(1); var r=new CountDownLatch(1);
        try { p.execute(held(e,r)); await(e); p.execute(()->{});
            boolean rejected=false; try { p.execute(()->{}); } catch(RejectedExecutionException ex){ rejected=true; }
            check(rejected && p.getQueue().size()==1, "bounded queue must reject the third task");
        } finally { r.countDown(); stop(p); } cases++;
    }
    static void callerRuns() throws Exception {
        var p=pool(new ThreadPoolExecutor.CallerRunsPolicy()); var e=new CountDownLatch(1); var r=new CountDownLatch(1);
        try { p.execute(held(e,r)); await(e); p.execute(()->{});
            var observed=new AtomicReference<Thread>(); Thread caller=Thread.currentThread();
            p.execute(()->observed.set(Thread.currentThread()));
            check(observed.get()==caller, "CallerRuns borrows the submitting thread");
        } finally { r.countDown(); stop(p); } cases++;
    }
    static void silentDiscard() throws Exception {
        var p=pool(new ThreadPoolExecutor.DiscardPolicy()); var e=new CountDownLatch(1); var r=new CountDownLatch(1);
        Future<?> lost=null;
        try { p.execute(held(e,r)); await(e); p.execute(()->{}); lost=p.submit(()->42);
            check(!lost.isDone(), "silent discard leaves a Future without a completion");
        } finally { if(lost!=null) lost.cancel(false); r.countDown(); stop(p); } cases++;
    }
    static void waitingTimeout() throws Exception {
        var p=Executors.newSingleThreadExecutor(); var e=new CountDownLatch(1); var r=new CountDownLatch(1);
        try { Future<?> f=p.submit(held(e,r)); await(e);
            boolean timeout=false; try { f.get(0,TimeUnit.NANOSECONDS); } catch(TimeoutException ex){timeout=true;}
            check(timeout && !f.isDone() && !f.isCancelled(), "get timeout is not task cancellation");
            r.countDown(); f.get(3,TimeUnit.SECONDS);
        } finally { r.countDown(); stop(p); } cases++;
    }
    static void futureInterrupt() throws Exception {
        var p=Executors.newSingleThreadExecutor(); var entered=new CountDownLatch(1); var interrupted=new CountDownLatch(1);
        try { Future<?> f=p.submit(()->{entered.countDown();try{new CountDownLatch(1).await();}
                catch(InterruptedException ex){interrupted.countDown();Thread.currentThread().interrupt();}});
            await(entered); check(f.cancel(true),"first cancellation accepted"); await(interrupted);
        } finally { stop(p); } cases++;
    }
    static void completableCancellation() throws Exception {
        var p=Executors.newSingleThreadExecutor(); var e=new CountDownLatch(1); var r=new CountDownLatch(1); var exited=new CountDownLatch(1);
        var interrupted=new AtomicBoolean();
        try { CompletableFuture<Integer> f=CompletableFuture.supplyAsync(()->{
                e.countDown();try{r.await();return 7;}catch(InterruptedException ex){interrupted.set(true);return -1;}
                finally{exited.countDown();}},p);
            await(e); check(f.cancel(true),"future status changed");
            check(!interrupted.get() && exited.getCount()==1,"CF cancellation did not stop the supplier");
            r.countDown(); await(exited); check(!interrupted.get(),"no interrupt was requested by CF");
        } finally { r.countDown(); stop(p); } cases++;
    }
    static void orTimeoutIdentity() {
        var f=new CompletableFuture<Integer>(); var result=f.orTimeout(0,TimeUnit.NANOSECONDS);
        check(result==f,"orTimeout mutates and returns this future");
        boolean timeout=false;try{f.join();}catch(CompletionException ex){timeout=ex.getCause() instanceof TimeoutException;}
        check(timeout,"timeout cause preserved"); cases++;
    }
    static void lateCompletion() {
        var f=new CompletableFuture<Integer>(); f.completeExceptionally(new TimeoutException());
        check(!f.complete(42),"late success cannot replace an established timeout"); cases++;
    }
    static void allOfWaits() {
        var a=new CompletableFuture<Integer>();var b=new CompletableFuture<Integer>();var all=CompletableFuture.allOf(a,b);
        a.completeExceptionally(new IllegalStateException("teaching failure"));
        check(!all.isDone(),"allOf is not a fail-fast sibling cancellation protocol");b.complete(2);
        check(all.isCompletedExceptionally(),"aggregate completes after both finish");cases++;
    }
    static void anyOfErrorWins() {
        var a=new CompletableFuture<Integer>();var b=new CompletableFuture<Integer>();var any=CompletableFuture.anyOf(a,b);
        a.completeExceptionally(new IllegalArgumentException("failed first"));b.complete(2);
        check(any.isCompletedExceptionally(),"anyOf is first completion, not first successful result");cases++;
    }
    static void threadLocalNotCopied() throws Exception {
        var local=new ThreadLocal<String>();local.set("caller");var p=Executors.newSingleThreadExecutor();
        try{check(p.submit(local::get).get(3,TimeUnit.SECONDS)==null,"ordinary ThreadLocal is not request propagation");}
        finally{local.remove();stop(p);}cases++;
    }
    static void threadLocalLeak() throws Exception {
        var local=new ThreadLocal<String>();var p=Executors.newSingleThreadExecutor();
        try{p.submit(()->local.set("previous-user")).get(3,TimeUnit.SECONDS);
            check("previous-user".equals(p.submit(local::get).get(3,TimeUnit.SECONDS)),"worker reuses previous context");
            p.submit(local::remove).get(3,TimeUnit.SECONDS);
            check(p.submit(local::get).get(3,TimeUnit.SECONDS)==null,"remove clears that worker's context");
        }finally{stop(p);}cases++;
    }
    static void submitCapturesFailure() throws Exception {
        var p=Executors.newSingleThreadExecutor();
        try{Future<?> f=p.submit(()->{throw new IllegalStateException("visible through Future.get");});
            boolean seen=false;try{f.get(3,TimeUnit.SECONDS);}catch(ExecutionException ex){seen=ex.getCause() instanceof IllegalStateException;}
            check(seen,"submit failure must be observed");
        }finally{stop(p);}cases++;
    }
    static void nonAsyncThread() {
        var f=new CompletableFuture<Integer>();var thread=new AtomicReference<Thread>();
        var next=f.thenApply(n->{thread.set(Thread.currentThread());return n+1;});f.complete(1);
        check(next.join()==2 && thread.get()==Thread.currentThread(),"non-async continuation may run on completer");cases++;
    }
    static void explicitAsyncExecutor() throws Exception {
        var p=Executors.newSingleThreadExecutor(r->new Thread(r,"teaching-explicit-executor"));
        try{String name=CompletableFuture.completedFuture(1).thenApplyAsync(n->Thread.currentThread().getName(),p).get(3,TimeUnit.SECONDS);
            check(name.equals("teaching-explicit-executor"),"explicit executor selects this stage");
        }finally{stop(p);}cases++;
    }
    static void queueExpiry() throws Exception {
        var p=pool(new ThreadPoolExecutor.AbortPolicy());var e=new CountDownLatch(1);var r=new CountDownLatch(1);var clock=new AtomicLong(0);
        try{p.execute(held(e,r));await(e);var calls=new AtomicInteger();
            Future<Boolean> f=p.submit(()->{if(clock.get()>=10)return false;calls.incrementAndGet();return true;});
            clock.set(10);r.countDown();check(!f.get(3,TimeUnit.SECONDS)&&calls.get()==0,"expired queued task must recheck its deadline");
        }finally{r.countDown();stop(p);}cases++;
    }
    static void nestedPoolStarvation() throws Exception {
        var p=Executors.newSingleThreadExecutor();
        try{Future<Boolean> outer=p.submit(()->{Future<Integer> inner=p.submit(()->9);
                try{inner.get(0,TimeUnit.NANOSECONDS);return false;}catch(TimeoutException ex){return true;}});
            check(outer.get(3,TimeUnit.SECONDS),"inner cannot run while only worker is occupied by outer");
            check(p.submit(()->1).get(3,TimeUnit.SECONDS)==1,"bounded demonstration leaves no blocked task");
        }finally{stop(p);}cases++;
    }
    static void orderlyShutdown() throws Exception {
        var p=pool(new ThreadPoolExecutor.AbortPolicy());var e=new CountDownLatch(1);var r=new CountDownLatch(1);var ran=new AtomicBoolean();
        try{p.execute(held(e,r));await(e);p.execute(()->ran.set(true));p.shutdown();
            check(!p.isTerminated(),"shutdown doesn't forcibly kill active work");r.countDown();
            check(p.awaitTermination(3,TimeUnit.SECONDS)&&ran.get(),"queued work completes in orderly shutdown");
        }finally{r.countDown();stop(p);}cases++;
    }
    static void shutdownNowQueuedFuture() throws Exception {
        var p=pool(new ThreadPoolExecutor.AbortPolicy());var e=new CountDownLatch(1);var r=new CountDownLatch(1);Future<?> queued=null;
        try{p.execute(held(e,r));await(e);queued=p.submit(()->1);List<Runnable> drained=p.shutdownNow();
            check(drained.contains(queued)&&!queued.isDone(),"drained queued Future is not automatically cancelled");queued.cancel(false);
        }finally{if(queued!=null)queued.cancel(false);r.countDown();stop(p);}cases++;
    }
    public static void main(String[] args) throws Exception {
        boundedReject();callerRuns();silentDiscard();waitingTimeout();futureInterrupt();completableCancellation();
        orTimeoutIdentity();lateCompletion();allOfWaits();anyOfErrorWins();threadLocalNotCopied();threadLocalLeak();
        submitCapturesFailure();nonAsyncThread();explicitAsyncExecutor();queueExpiry();nestedPoolStarvation();
        orderlyShutdown();shutdownNowQueuedFuture();
        check(cases==19,"case count");System.out.println("PASS: 19 finite Java executor/future/context/shutdown contract scenarios");
    }
}
