# 后端场景：有约束、有失败路径的答法

[返回总目录](../../README.md) · [题目索引](../../QUESTION_INDEX.md) · [版本与纠错](../../errata/README.md)

本章为原创补充讲义。P0 为应能独立讲清并写出关键步骤；P1 为常见追问；P2 为理解边界。官方资料核查日：2026-10-09。示例参数均为教学设定，不是作者或读者的项目实测。代码与 SQL 的实际执行范围在对应题中标注；没有实测的吞吐、可用性和故障恢复效果不作为事实。

- [FB67 只有十件库存，怎样让大量无效抢购早停](#fb67)
- [FB68 面试中的 QPS、并行流与扩容收益怎样证明](#fb68)
- [FB69 订单接口突然超时，按什么证据缩小范围](#fb69)
- [FB70 深分页怎样降低回表，又怎样真正避开大 OFFSET](#fb70)
- [FB71 秒杀和突增事故如何按不变量与应急顺序回答](#fb71)
- [FB72 高 CPU 与 OOM 怎样留下能解释原因的证据](#fb72)
- [FB73 下单幂等为什么需要结果状态，而不只是 SET NX](#fb73)
- [FB74 短链从创建到跳转有哪些必须解释的边界](#fb74)
- [FB75 支付超时与重复请求如何避免重复扣款](#fb75)
- [FB76 慢 HTTP 依赖怎样隔离，CompletableFuture 为何不够](#fb76)
- [FB77 唯一索引写入成本为什么不能一句“普通索引更快”](#fb77)
- [FB78 令牌桶、漏桶与分布式全局限额怎样取舍](#fb78)

<a id="fb67"></a>

### FB67 只有十件库存，怎样让大量无效抢购早停

**优先级：P0**

**知识点详解**：首先分离详情展示、资格准入、库存预占和最终成交。可公开缓存详情与“已售罄”提示，网关按活动限制进入，服务端验证用户资格后才进入原子库存路径。售罄标志可能滞后或因取消回补变化，不能做不可恢复的永久拒绝依据；更不能拿展示层余量当成交授权。每次成功预占有稳定流水，订单创建和补偿按状态机恢复。

**具体例子**：十件库存全部预占后，大量请求在前置售罄标志快速结束；两笔预占失效释放时，事件更新可售状态。若漏了更新，后台核对能解除错误售罄，监控欠售而不只监控超卖。

**面试答法**：我把昂贵链路留给可能成功的少数请求，同时证明售罄标记失效只影响体验/可用性，不能突破权威库存约束。

**追问**：活动结束才把 Redis 总数同步数据库够吗？不够，期间崩溃、重复、回补与并发修改需逐操作证据。

**常见误区**：库存很少就不用持久流水；全部排队永不拒绝；库存归零永久缓存且不处理取消回补。

**来源**：[FB-S065 Google SRE 过载处理](https://sre.google/sre-book/handling-overload/)、[FB-S068 AWS 幂等 API](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)、[FB-S076 AWS Transactional Outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)。业务组合、反例与答题组织为原创教学推导。

<a id="fb68"></a>

### FB68 面试中的 QPS、并行流与扩容收益怎样证明

**优先级：P0**

**知识点详解**：压测需说明版本、硬件、数据规模、命中率、请求分布、并发/到达率、预热、持续时间及错误定义。成功吞吐必须满足延迟与错误率目标，不能把被拒绝请求都算业务成功。分解 CPU、连接池等待、锁、存储 I/O、外部依赖和网络，找真正限制。并行流共享执行资源并可能增加拆分/合并成本；池化能减少创建，却增加排队与争用，不是普遍加速。

**具体例子**：假设 2000 请求/s 时 p99 从 100 ms 跳到 2 s，同时连接池等待增长而 CPU 不高，优先分析数据库执行与连接占用，不直接开十倍线程。该数字是分析示例，并非任何项目实测。

**面试答法**：我只报告自己测过的配置和曲线，给出瓶颈证据、改动前后对比和回归风险，没有数据就描述测试方案。

**追问**：为什么只看平均延迟不够？少量长尾可能影响用户体验与资源滞留，平均值会掩盖排队和抖动。

**常见误区**：一秒峰值就是稳定容量；压测机自身没饱和无需检查；线程越多速度越快。

**来源**：[FB-S065 Google SRE 过载处理](https://sre.google/sre-book/handling-overload/)、[FB-S066 OpenTelemetry Traces](https://opentelemetry.io/docs/concepts/signals/traces/)、[FB-S018 ThreadPoolExecutor Java SE 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html)。业务组合、反例与答题组织为原创教学推导。

<a id="fb69"></a>

### FB69 订单接口突然超时，按什么证据缩小范围

**优先级：P0**

**知识点详解**：先看发生范围、开始时间、错误类别与发布/依赖变化，再用 trace 拆入口排队、线程/连接获取、SQL、锁等待、缓存、MQ 和外部 HTTP。区分超时前服务端有没有提交；客户端重试不能凭超时新建订单。短期先限流、隔离慢依赖、回滚已证实有问题的变更或按预案降级；长期优化有证据的瓶颈。库存异步化改变一致性，不是临时性能开关。

**具体例子**：链路显示 2 秒中有 1.7 秒等待连接，SQL 本身只用 20 ms。排查连接泄漏、长事务和远端调用占连接，比单独给 SQL 加索引更接近证据。

**面试答法**：我先分清排队、执行、网络和结果不确定，再保核心容量；每个操作都说明验证指标与回退条件。

**追问**：加大连接池为什么可能更糟？数据库并行执行能力有限，更多连接可能增加竞争与内存，让有效吞吐下降。

**常见误区**：所有超时都重试；所有慢请求都改异步；只看总耗时不看分段。

**来源**：[FB-S066 OpenTelemetry Traces](https://opentelemetry.io/docs/concepts/signals/traces/)、[FB-S067 AWS 超时、重试与抖动退避](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)、[FB-S068 AWS 幂等 API](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)。业务组合、反例与答题组织为原创教学推导。

<a id="fb70"></a>

### FB70 深分页怎样降低回表，又怎样真正避开大 OFFSET

**优先级：P0**

**知识点详解**：LIMIT offset,count 即使通过覆盖索引先找 ID，通常仍要扫描/跳过前面的索引项；延迟回表只是减少对宽行的无效读取。连续翻页更适合 keyset：以稳定唯一排序记录上一页边界，再向后查。组合排序应加唯一 tie-breaker，游标绑定查询条件与权限，防止恶意篡改。跳任意第 N 页、总数和跨更新快照是另外需求，不能说游标等价替换所有分页。

**具体例子**：按 created_at DESC,id DESC：下一页条件为 created_at<:t OR (created_at=:t AND id<:id)，ORDER BY 相同，LIMIT 20。建立匹配筛选与排序的索引，并测试多个时间相同、插入新数据和删除旧数据；这些 SQL 未在 MySQL 实跑。

**面试答法**：我把减少宽行回表和减少跳过扫描区分开，先问随机跳页还是连续加载，再设计稳定游标。

**追问**：并发更新排序字段会怎样？记录可能跨边界移动，若要求严格快照，应有快照版本/时间边界与相应存储方案。

**常见误区**：子查询里仍 OFFSET 百万就完全解决深分页；只用非唯一时间戳做边界；客户端自由改游标就无安全风险。

**来源**：[FB-S051 MySQL 8.4 ICP](https://dev.mysql.com/doc/refman/8.4/en/index-condition-pushdown-optimization.html)、[FB-S058 RFC 9110 HTTP 语义](https://datatracker.ietf.org/doc/html/rfc9110)。业务组合、反例与答题组织为原创教学推导。

<a id="fb71"></a>

### FB71 秒杀和突增事故如何按不变量与应急顺序回答

**优先级：P0**

**知识点详解**：不变量包括库存不为负、同用户活动唯一、受理请求可查询、终态不被迟到消息逆转、补偿最多一次。先识别影响并保核心：限入流、阻断重试风暴、控制队列与回源；再依据瓶颈扩应用或消费者，确认数据库/MQ 余量；然后修查询、热点和资源占用。分库分表是经过迁移验证的架构变更，通常不是几分钟内的第一应急动作。

**具体例子**：订单链路尚健康但推荐接口占满共享线程池，可先隔离/关闭可降级推荐；恢复后做压测与故障演练。秒杀消费可并行，但每个订单的状态转换和唯一约束仍要原子，不能只靠“全局单线程”证明。

**面试答法**：我先给用户影响和停止恶化措施，再用证据选择恢复动作，最后检查库存/订单账是否一致。

**追问**：什么条件算恢复？有效成功率、尾延迟、队列最老年龄与业务对账均回到目标，而不只是 CPU 降下去。

**常见误区**：第一步是加所有池子；无限降级放量到数据库；补偿不检查状态直接加库存。

**来源**：[FB-S065 Google SRE 过载处理](https://sre.google/sre-book/handling-overload/)、[FB-S067 AWS 超时、重试与抖动退避](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)、[FB-S068 AWS 幂等 API](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)。业务组合、反例与答题组织为原创教学推导。

<a id="fb72"></a>

### FB72 高 CPU 与 OOM 怎样留下能解释原因的证据

**优先级：P0**

**知识点详解**：先确认 PID、时间窗口和容器限制。高 CPU 用线程级观测（如 top -H -p PID）定位 TID，再转换十六进制与 Java 线程 dump 中 nid 对照，重复采样排除偶然瞬间；JFR 可进一步看热点、分配和阻塞。OOM 先分 Java heap、metaspace、direct memory、本地线程与容器 OOM kill。后者可能来不及生成 Java heap dump；采集本身可停顿、耗盘并包含敏感信息，需在授权范围控制。

**具体例子**：线程热点是正则回溯或死循环，优化堆容量没有意义；另一进程堆使用平稳但 native thread 创建失败，可能是线程数与本地内存限制。应保存日志、GC/JFR、进程状态和部署版本形成同一时间线。

**面试答法**：我先保留现场再缩小假设，不重启后再凭记忆猜。诊断命令先看影响等级并遵守生产预案。

**追问**：heap dump 很大怎么处理？确认磁盘、访问权限与保留期限，离线分析最短必要副本，不能公开上传完整业务对象。

**常见误区**：OOM 全是堆太小；jstack 一次就证明根因；未做线程 TID 映射就猜热点方法。

**来源**：[FB-S049 JDK 21 jcmd](https://docs.oracle.com/en/java/javase/21/docs/specs/man/jcmd.html)、[FB-S050 Linux cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)、[FB-S056 Linux proc_pid_stat(5)](https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html)。业务组合、反例与答题组织为原创教学推导。

<a id="fb73"></a>

### FB73 下单幂等为什么需要结果状态，而不只是 SET NX

**优先级：P0**

**知识点详解**：幂等键由客户端或入口生成一次，重试保持不变，绑定用户、操作与请求参数摘要。服务端原子创建处理记录，状态可为 PROCESSING、SUCCEEDED、FAILED/UNKNOWN，并保留可重放结果。相同键不同参数返回冲突；处理中返回状态查询或有界等待。去重记录与本地业务效果尽量同事务，外部副作用则依赖对方幂等与查询。保留期覆盖客户端重试窗口，不可随意到期后允许旧请求再做一遍。

**具体例子**：只 SET NX 成功后业务崩溃，键不清理会永久阻断，直接删键又可能允许并行重做。持久请求记录能表达“尚待确认”，恢复者查询真实订单后再决定继续或返回结果。

**面试答法**：我定义重复请求是否同一个操作、参数是否相同、处理中如何响应和何时允许重试，最后证明记录与业务提交的原子边界。

**追问**：失败结果该不该缓存？要区分输入永久错误、未开始执行的临时失败与结果不确定，按契约处理，不能统一永远返回第一次错误。

**常见误区**：分布式锁就是幂等；失败删标记一定安全；每次重试重新生成 key。

**来源**：[FB-S068 AWS 幂等 API](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)、[FB-S076 AWS Transactional Outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)。业务组合、反例与答题组织为原创教学推导。

<a id="fb74"></a>

### FB74 短链从创建到跳转有哪些必须解释的边界

**优先级：P1**

**知识点详解**：创建时校验 URL 格式与允许 scheme，决定是否允许自定义域名、过期与目的地修改；生成短码并以唯一约束检测碰撞。短码可由 ID 编码或随机/哈希截断产生，短不代表不碰撞。跳转路径查缓存/数据库、检查状态与滥用，再发重定向。301 的永久语义与缓存可能影响后续修改和统计，302 等临时跳转也应明确缓存策略。若服务端预抓取预览，还要防 SSRF。

**具体例子**：原地址可修改的活动短链优先评估临时跳转加明确缓存控制；管理员禁用恶意链接后必须同步热点缓存，否则旧映射仍继续跳。点击统计异步化，但不能让统计系统失效阻断核心跳转。

**面试答法**：我按唯一生成、持久映射、缓存、重定向、统计和风控六段设计，并说明碰撞和过期恢复。

**追问**：长 URL 的同一内容是否一定返回同短码？这是产品去重语义，涉及用户隔离、参数规范化与隐私，不能随便全局去重。

**常见误区**：截断哈希绝无碰撞；301 总是最快所以总用；允许 javascript 等任意 scheme。

**来源**：[FB-S058 RFC 9110 HTTP 语义](https://datatracker.ietf.org/doc/html/rfc9110)、[FB-S068 AWS 幂等 API](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)。业务组合、反例与答题组织为原创教学推导。

<a id="fb75"></a>

### FB75 支付超时与重复请求如何避免重复扣款

**优先级：P0**

**知识点详解**：支付业务使用稳定 payment_id 与渠道认可的幂等键，持久记录 CREATED、SUBMITTED、UNKNOWN、SUCCEEDED、FAILED 等状态。网络超时可能是响应丢失，不能立即当失败再次换键扣款；应查询渠道或重试同一幂等请求，按渠道契约恢复。回调验签、去重、金额币种和订单关联校验之后才改变支付状态；本地唯一索引或 Redis 锁只保护本地流程，不能单方面约束外部渠道。

**具体例子**：渠道已扣款但返回链路断开，订单显示“确认中”。恢复任务按 payment_id 查渠道，确认成功后以条件更新订单并触发后续；迟到失败通知不能覆盖已经确认的成功事实，必要时对账人工处理。

**面试答法**：我明确支付发起、扣款事实、回调接收和本地入账四个边界；未知结果先查明，重试使用同一逻辑操作身份。

**追问**：渠道幂等键保留多久？必须核查具体 API 契约并让本地保留与对账覆盖业务重试窗口，不能假定永久有效。

**常见误区**：超时就是没扣；每次重试换新 payment_id；收到任意自称支付成功的 HTTP 回调就发货。

**来源**：[FB-S068 AWS 幂等 API](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)、[FB-S067 AWS 超时、重试与抖动退避](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)、[FB-S075 AWS Saga Orchestration](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-orchestration.html)、[FB-S078 Stripe 幂等请求契约](https://docs.stripe.com/api/idempotent_requests)。业务组合、反例与答题组织为原创教学推导。

<a id="fb76"></a>

### FB76 慢 HTTP 依赖怎样隔离，CompletableFuture 为何不够

**优先级：P0**

**知识点详解**：为慢依赖设置独立有界执行器/并发许可、连接与请求超时、端到端 deadline、队列上限、熔断和重试预算。CompletableFuture.supplyAsync 不指定 executor 时默认用公共执行资源，不能据此声称已隔离。Future 超时只改变调用侧等待状态，不一定中止底层网络操作；需把取消传到底层客户端并释放连接、订阅和上下文。响应式不意味着阻塞驱动自动变非阻塞。

**具体例子**：聊天供应商慢时，把每个调用丢 commonPool 会拖累无关任务；教学方案给供应商设 50 个并发许可，超过立即返回可重试忙状态，deadline 到期关闭实际请求并释放许可。50 是示例，必须按测量调整。

**面试答法**：我分别限制正在执行、正在排队和总等待时间，并验证超时后资源真的释放，不只验证调用方收到了异常。

**追问**：重试放哪一层？尽量集中在知道业务语义的一层，避免网关、SDK、服务各重试把一次变成指数多次。

**常见误区**：用了异步就没有阻塞；orTimeout 自动停止一切底层工作；独立池使用无限队列仍算隔离充分。

**来源**：[FB-S053 CompletableFuture Java SE 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/CompletableFuture.html)、[FB-S018 ThreadPoolExecutor Java SE 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html)、[FB-S067 AWS 超时、重试与抖动退避](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)。业务组合、反例与答题组织为原创教学推导。

<a id="fb77"></a>

### FB77 唯一索引写入成本为什么不能一句“普通索引更快”

**优先级：P1**

**知识点详解**：唯一索引必须维护唯一性语义，通常需要检查冲突；非唯一二级索引在满足引擎、页面和配置条件时可利用 change buffer 延迟合并，减少某些随机读写。MySQL 8.4 官方默认 innodb_change_buffering 为 none，所以不能套用旧版本默认开启的性能推断。热页、写入分布、索引宽度和锁竞争会改变结果，先满足业务约束，再测成本。普通索引也不能概括成每次只加某一种间隙锁。

**具体例子**：订单 (activity_id,user_id) 需要唯一性，即便唯一检查有开销也不能为了快改普通索引再靠应用先查；并发两个先查都可能不存在。性能优化可减少无效请求、控制索引数量并验证访问页。

**面试答法**：我先说唯一索引表达的数据约束，再限定版本与 change buffer 的适用条件，最后用执行与 I/O 指标比较。

**追问**：同样 insert 为什么冷库与热库差很多？页面是否已在 buffer pool 会影响随机页访问，不能只按索引名字预测。

**常见误区**：普通索引永远更快；所有版本默认 change buffer 一样；去掉业务唯一约束仅是性能优化。

**来源**：[FB-S052 MySQL 8.4 Change Buffer](https://dev.mysql.com/doc/refman/8.4/en/innodb-change-buffer.html)、[FB-S051 MySQL 8.4 ICP](https://dev.mysql.com/doc/refman/8.4/en/index-condition-pushdown-optimization.html)。业务组合、反例与答题组织为原创教学推导。

<a id="fb78"></a>

### FB78 令牌桶、漏桶与分布式全局限额怎样取舍

**优先级：P0**

**知识点详解**：令牌桶以速率 r 补充最多 b 个令牌，允许积累后有限突发；漏桶常用于以近固定速率输出，超量排队或丢弃。应明示容量、初始状态、时间源和每次消耗成本。单实例本地限额低延迟但总额度随副本数变化；集中 Redis 原子脚本或配额分片能协调，但复制丢写、时钟偏差、故障放行会影响精确性。限速与并发上限不同，慢请求还需并发隔离。

**具体例子**：桶容量 100、每秒补 10，空闲足够久后可瞬发 100，但下一秒只新增约 10；若只允许一个实例 100/s，扩成十实例可能到 1000/s，不能称原来全局 100/s 仍成立。

**面试答法**：我先定义长期速率、短突发和排队预算，再选本地或协调限额，并明确 fail-open/fail-closed 及误拒风险。

**追问**：为什么同一 QPS 也可能压垮服务？请求时长上升使在途并发增长；只限制每秒到达量没有限制资源占用时间。

**常见误区**：共享 Redis 就任何故障下精确全局 QPS；令牌桶完全不允许突发；漏桶无限排队不会有问题。

**来源**：[FB-S065 Google SRE 过载处理](https://sre.google/sre-book/handling-overload/)、[FB-S036 Redis Lua 脚本执行](https://redis.io/docs/latest/develop/programmability/eval-intro/)、[FB-S067 AWS 超时、重试与抖动退避](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)。业务组合、反例与答题组织为原创教学推导。

