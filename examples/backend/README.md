# 后端补充题的可复验实验

这些是原创教学实验，不访问业务数据库、Redis或外部网络。

## FB11：两种线程安全单例

在本目录执行（需要完整 JDK 21；通常也可直接使用 javac）：

```sh
java -m jdk.compiler/com.sun.tools.javac.Main DclSingleton.java HolderSingleton.java SingletonTest.java
java SingletonTest
```

三个源文件与讲义中的两个单例实现相同。测试创建16个工作线程，提交10000次获取；逐个检查Future，确认每种单例只产生一个观察到的实例引用，初始化字段均为ready，并等待线程池退出。运行结果不替代JMM证明，未覆盖反射、序列化、不同类加载器或所有线程调度。

## FB29：哈希表与双链LRU

```sh
python -m unittest -v test_lru.py
```

实现只用普通dict和双向节点。测试的OrderedDict只作为参考模型；覆盖容量0–5、每容量10个种子、每种子500步，合计30000次随机操作，并逐步检查链表顺序、前后指针、哈希键集合和容量；另测示例、更新已有键、零容量和负容量。

## 实际执行范围

2026-10-09在OpenJDK 21.0.12.1与Python 3.12.14环境运行上述命令通过。没有安装额外服务。Lua、MySQL、Kafka及完整分布式系统示例未运行；这不是线上评测或生产验证，也不是性能基准。
