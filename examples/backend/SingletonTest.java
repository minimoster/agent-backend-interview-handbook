import java.util.*;
import java.util.concurrent.*;
public class SingletonTest {
 public static void main(String[] args) throws Exception {
  ExecutorService pool=Executors.newFixedThreadPool(16);
  try {
   Set<DclSingleton> d=ConcurrentHashMap.newKeySet();
   Set<HolderSingleton> h=ConcurrentHashMap.newKeySet();
   List<Future<?>> fs=new ArrayList<>();
   for(int i=0;i<10000;i++) fs.add(pool.submit(()->{
    DclSingleton x=DclSingleton.getInstance(); HolderSingleton y=HolderSingleton.getInstance();
    if(!"ready".equals(x.mode()) || !"ready".equals(y.mode()))throw new AssertionError();
    d.add(x);h.add(y);
   }));
   for(Future<?> f:fs) f.get();
   if(d.size()!=1 || h.size()!=1)throw new AssertionError();
   System.out.println("PASS: 10000 calls, 16 workers, one reference each, initialized fields");
  } finally {pool.shutdown();if(!pool.awaitTermination(10,TimeUnit.SECONDS))throw new AssertionError();}
 }
}
