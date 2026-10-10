# 本版验证记录

[返回目录](../README.md) · [主题范围](README.md) · [版本与纠错](../errata/README.md)

核验日期：2026-10-09。本记录针对规范Markdown、学习源码与覆盖数据；阅读站点的显示、交互和发布可达性另行验收。

## 内容完整性

- Hot100另有17类、100个官方题号，100份原创Python源码与100篇讲解；不与讲义题数混为同一编号体系。
- 缺少候选数字等完整条件的题，明确标注必要约束，并另外标明教学变体。
- 全量检查题号与必要字段、相对路径和锚点。

## 独立语义复核

抽查55个高风险技术主题，重点看目标正文是否真正回答具体约束，并核对版本与证据边界。发现的年度消费SQL完整字段/双门槛缺口、RocketMQ4.x广播失败重试边界和赛马下界的任务/对抗条件，已经补充并复核。

这不是对全部技术事实的第二次逐句核验，也不等于证明原作者每次面试经历属实。章节的一手来源核验与独立抽查范围分别记录；证据不足的产品内部实现、原作者贡献和无条件排行榜没有当成已确认事实采用。

## 已运行的验证

| 模块 | 实际验证 | 边界 |
|---|---|---|
| Hot100 | 100个逐题unittest；100篇正文代码与源码一致；模块内679个本地链接；5个高风险题另有159709组有限穷举 | 本地验证，不是在线判题提交或全输入形式化证明 |
| 补充算法X01–X06 | 6个测试入口，含边界、固定种子随机对拍、数位小范围穷举、链表节点身份与环检查 | 数位题只验证本讲义明确的可重复数字变体 |
| SQL | 10组SQLite等价关系语义与Python参考检查 | 没有运行MySQL，不能证明其锁、事务、执行计划或语法实测通过 |
| 推理题 | 倒水有限状态BFS、沙漏时间线、海盗递推、金条子集、空瓶守恒；两种赛马构造各10000个随机全序 | 随机检查不证明最优下界；R07另有有序模型对抗论证，R08只给至多11场上界 |
| Java顺序输出 | OpenJDK21.0.12.1；101正常用例，工作线程中断/异常与协调线程中断清理，全部join | 不证明任意调度、JVM崩溃或OOM恢复 |
| Java单例 | 两种实现，16线程、10000次获取校验同一实例 | 不声称跨ClassLoader/JVM全局唯一 |
| Python LRU | 30000步固定种子对拍及双链指针不变量检查 | 单进程教学实现，不把它当并发分布式缓存 |

上述模块均做过独立再次运行。可复验命令：

```sh
python3 -B examples/hot100/run_validation.py
python3 -B tests/hot100/exhaustive_checks.py
python3 -B examples/interview_algorithms/test_solutions.py
python3 -B examples/sql/check-relational-examples.py
python3 -B examples/reasoning/verify-puzzles.py
java examples/java/OrderedPrinter.java
```

单例与LRU的独立运行方式见[后端实验目录](../examples/backend/README.md)。部分命令会更新自己的验证报告，运行者应记录所用版本，不把本文日期当作新环境已通过。

## 明确未运行或未证明

- MySQL/InnoDB、Redis/Lua、消息队列、LangGraph持久恢复、MCP跨版本等依赖目标服务的集成实验，除正文明确给出运行记录外均未宣称通过。
- 原作者具体项目实现与性能数字不作为学习者成果；公开仓库案例以所列固定提交和已核范围为限。
- 64马全局最优场数、条件不充分的具体题面，不补造结论。
- 独立审查没有把全部来源原文逐句做版权相似度比对；公开版使用原创讲解、代码与短主题标识，不附受限正文导出或原图。

## 公开内容边界

已检查规范文件的明显凭证、私人身份、手机号和机器路径模式，未发现待处理命中；生成的pyc/class缓存不在发布资料中。必要的公开来源链接继续保留，链接可访问并不代表原站授予整篇转载许可。

本记录证明的是列明范围内的检查与结果，不是生产系统、安全、版权或招聘结果的保证。

## 2026-10-10：知识合同与追问复验

在Python 3.12.14中重新运行100个Hot100逐题测试、159709组原有限穷举、LC395对拍、SQLite十组检查、推理程序及LRU检查。新增Python可哈希条件与LC53/LC295追问9个测试入口，含97655个非空LC53数组、19530个带内流、19607个混合流及每个前缀；X01–X06现在8个入口，含306176组全部数位集/小界限对拍及5000位字符串边界。主Hot100的100份原源码与官方manifest保持字节一致，100份Carl资源/署名区块保持字节一致；五篇原创正文按修订版本另记当前前缀哈希，历史记录未冒充当前字节。

[Agent内存合同](../examples/agent_contracts/README.md)8个测试通过，覆盖进行中去重、客户端键/参数冲突、租户与操作身份、并发重复及失败窗口反例；[题目元数据](../tools/refresh_question_metadata.py)的6个测试通过，题数与Unicode长度检查通过。内存反例不构成案例仓库、真实文件系统、数据库或外部执行验证。

OpenJDK21.0.12.1再次运行顺序输出101个正常用例和三类中断/失败路径、单例16线程10000调用，均通过。SQLite/Python通过仍不表示MySQL目标引擎的锁、事务和恢复通过。

[Go取消与SSE fixture](../examples/go/cancellation/README.md)已提供源码和测试，但本地缺少Go编译器，编译/测试/race仍未运行。仓库的[知识检查工作流](../.github/workflows/knowledge-checks.yml)将分别记录Node/Python/Java/Go实际版本及测试结果；只有对应提交的CI实际完成才能据此更新通过范围。MySQL/Redis/MQ故障实验保持待验证，未运行模型API、Spark集群或公开案例项目的故障注入。

## 2026-10-10：已有fixture的CI实测记录

提交[4ae3bfca6ad0925cae8b98522e1c4d82c5f3dbc4](https://github.com/minimoster/agent-backend-interview-handbook/commit/4ae3bfca6ad0925cae8b98522e1c4d82c5f3dbc4)的[知识检查38053168150](https://github.com/minimoster/agent-backend-interview-handbook/actions/runs/38053168150)已成功。该次Node22.23.3、Python3.12.3、Temurin17.0.20.1与Go1.24.13 linux/amd64在CI实际运行教学fixture；Go取消与模拟SSE使用`go test -race -count=1 -timeout=60s ./...`通过。上文“本地Go未运行”仍描述本地环境，这条记录另列CI结果。它不证明真实MySQL/Redis/MQ、模型API、Spark集群或案例仓库故障注入。

新增[公开场景模块](../docs/90-public-interview-scenarios/README.md)的26卡、4个Python练习33项测试及12条未运行合成评测设计分别见[模块验证](../docs/90-public-interview-scenarios/VALIDATION.md)，不加入原有361/100/15题数。
