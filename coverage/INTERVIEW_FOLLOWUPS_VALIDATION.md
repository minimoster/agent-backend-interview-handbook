# 面经追问补充：发布前验证与未测范围

[本轮学习路线](../docs/00-guide/interview-followup-study-paths.md) · [公开来源边界](../sources/interview-followups/README.md) · [原有验证](README.md)

记录日2026-10-11。本记录描述候选的发布前检查，发布后CI、Pages和浏览器验收是另一个阶段；确切提交的Actions结果及线上检查不能由这个静态记录预先保证。

## 变化范围

六篇原创深读专题：A2A任务生命周期、工具流组装、Java执行器故障、Go生命周期、存储恢复、系统设计与排障。另有一篇学习路线、公开引用说明与配套教学源码。基础章节和Hot100解法不重写；所有新专题question_ids为空，不新增编号题。

原361道讲义题、100道Hot100、15道外部资源练习、26张独立场景卡保持各自口径，原461条编号索引保持不变。原17份场景自报集合与本轮六个自述/回顾页面、弱归属题单和知乎二手整理不混算。不能将便利样本写成统计考频。

## 已执行的有限合同

- Java：本地Java21源启动器执行19个场景，覆盖队列/拒绝、get等待超时、Future与CompletableFuture取消差异、聚合、ThreadLocal、队列过期和退出。门闩协调与有界收尾，不是性能基准
- Python存储：29个unittest方法通过，执行SQLite本地事务、临时数据库文件重开、Outbox/Inbox，以及内存frontier/fence/cache-floor。五个连续整数记录的120种完成排列包含在一个方法内，不膨胀测试计数
- Agent：标准库任务投影与工具参数组装测试实际执行，精确方法数及合同见[协议参考记录](../sources/agent-protocol-references.md)。使用合成事件，不调用真实服务或SDK

本地Python3.12.14、Java21.0.12.1；这是已观察的执行环境，不据此认证所有版本。章节所述故障注入是可控异常/状态，不是真实断电、网络故障或生产进程崩溃。

## Go检查状态

已编写10个测试函数，含200轮正常/失败重复回归，go.mod语法下限1.23。当前云环境没有Go编译工具，**本地未执行**go test或race。已有GitHub Actions继续运行原Go实验，并新增本模块的`go test -race -count=1 -timeout=60s ./...`；是否运行通过必须读取同一提交的日志，而不是由源码审阅推断。

## 集成要求

- 编号索引、既有题目清单与Hot100不变，新文档有完整模块/路线入口
- 站点重新生成，搜索能定位新章实际锚点，源码资源字节与公开源文件一致
- 保留原28组静态站点检查，增加本批检查；这些是非渲染测试
- 公开树与归档仅包含公开安全源文件及必要生成文件；不含私人来源、凭据、原帖全文、内部审查或截图

## 未执行，不能宣传为通过

没有真实A2A服务器或跨Agent互通、OpenAI/Claude供应商调用、SDK协议兼容、实际SSE传输、模型评测/训练、GPU、生产内核或PyTorch比较。没有真实MySQL锁/断电恢复、Redis故障转移、Kafka消费组重平衡、在线迁移、生产压测或容器发布实验。

SQLite与内存模型不能替代这些组件。密集整数offset模型不适用于Kafka跳号；资源端fence不负责签发token；缓存floor未验证持久恢复；任务回调不合作时Go模型无强杀保证。

发布前尚无本批线上浏览器、真实移动设备或完整辅助技术验收。发布后若通过云桌面检查，应另报实际视窗、导航/搜索/下载范围，不能自动扩成手机或无障碍认证。原有外部受限资料与未读外部技能ZIP保持缺口，现代MCP2026-07-28互通仍未执行。

## 复验命令

```bash
python3 -B tools/refresh_question_metadata.py --check
python3 -B tests/test_question_metadata.py
node site/build.mjs --check
node site/test.mjs
python3 -B -m unittest discover -s examples/interview_followups -v
java examples/interview_followups/ExecutorFailureLab.java
(cd examples/go/followup_lifecycle && go test -race -count=1 -timeout=60s ./...)
```

最后一条需要真实Go工具链；其他既有教学、算法与语言检查由原CI保留。实际输出、同提交CI/Pages结果和浏览器观察分别作为不同层证据，不合并成“所有内容全部验证”。
