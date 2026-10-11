# A2A任务生命周期：身份、中断、终态与断线恢复

[返回Agent目录](README.md) · [执行与工具基础](01-agent-loop-tools-and-state.md) · [异步可靠性](04-streaming-and-reliable-execution.md)

这是一章原创面试补充，解决跨Agent交付的协议边界。泛化的多Agent分工已见A07，checkpoint与外部副作用已见FA40、SC-A09，本章不再重写它们。先掌握任务、状态、工具、幂等，再读这里的身份和失败时间线。

核验日：2026-10-11。技术基准固定为A2A官方仓库v1.0.1，提交3303592588e388e62e0f69f701af531d2f4e3991；协议接口版本字符串为1.0，与仓库补丁发布号1.0.1区分。官网渲染页仍标1.0.0，因此本章不使用含糊的“最新版”。[v1.0.1发布](https://github.com/a2aproject/A2A/releases/tag/v1.0.1)、[固定版规范](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md)、[规范数据定义](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

配套实验只用Python标准库模拟一个任务的客户端视图，没有启动A2A服务、调用SDK或远程Agent。38项测试覆盖本章与下一章的有限合同，不是38次真实面试或互通测试。[源码](../../examples/interview_followups/agent_protocol_lab.py) · [测试](../../examples/interview_followups/test_agent_protocol_lab.py) · [来源与验证边界](../../sources/agent-protocol-references.md)

<a id="a2a-versus-mcp"></a>
## 1 A2A补的是哪一层，为什么不能只说“多Agent框架”

本地函数解决一项明确能力；MCP为工具、资源等提供接入合同；A2A为独立Agent系统之间的发现、交互和任务交付提供合同。接收方可以隐藏内部提示、记忆、工具和框架，只公开能力、接收消息、任务状态和产物。协议不替你决定任务怎样拆、哪种模型最好或何时相信结果。[官方比较](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/topics/a2a-and-mcp.md)

原创例子：本地报告助手把“生成带出处的三页摘要”交给另一个组织的文献Agent。后者内部可以使用MCP检索，客户端只需知道交付格式、允许的数据、状态与产物。若只是调用本进程内的求和函数，没有必要为了“多Agent”再造远程任务协议。

**追问链：** 为什么不是普通REST接口？→ 哪些独立系统需要互通？→ 什么需要协议统一，什么仍是业务合同？→ 接收方换掉内部框架，客户端哪些接口不变？

**参考主线：** REST同样能表达业务服务；采用A2A的理由应是已有独立Agent需要共同的发现、消息和任务语义。它减少一部分专用适配，不自动减少网络往返、授权工作或验证成本。角色名称和Agent Card描述也不是身份认证或数据共享许可。

<a id="a2a-identity"></a>
## 2 Message、Task、contextId和调用身份怎样分开

Message是一轮沟通，Task是一项可跟踪工作；简单请求可以直接返回Message，持续处理则返回Task。contextId把相关消息与任务组织在一起，不保证其中只有一个任务。taskId定位具体工作，messageId识别消息；JSON-RPC id只关联一次协议请求与响应。三者不能互相代替。[任务指南](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/topics/life-of-a-task.md)

原创身份表：

|身份|本例用途|不能当成什么|
|---|---|---|
|ctx-report|一次报告讨论的上下文|所有并行工作的唯一任务ID|
|task-research / task-check|调研和核查两项工作|一条网络连接|
|msg-scope / msg-input|界定范围与补充输入的消息|必然幂等的业务操作键|
|rpc-17|一次GetTask请求|任务本体或支付操作身份|
|artifact-brief|某任务内的一份产物|可随意访问的公共文件|

本实验TaskMonitor只投影一个固定task/context。context相同但task不同的事件仍拒绝；批量系统应有按“已认证身份＋远程服务＋taskId”划分的任务表，并单独记录权限。ID格式正确不证明调用者有权读取。

**追问：** 两个任务同属ctx-report，第二个完成会不会把第一个误标完成？如果两个服务都返回task-1呢？

**参考答案：** 用明确的远程服务和任务身份定位，避免仅按contextId或无命名空间的taskId覆盖。跨服务任务ID碰撞不是模型推理问题，应在存储和事件路由层解决。实验没有多租户认证，也没有跨服务表，不能把这一设计说成已经实现。

<a id="a2a-state"></a>
## 3 等输入、等认证、失败与完成为何需要不同状态

v1.0数据枚举用TASK_STATE前缀的大写名字。本章在本地教学代码中转换成较短字符串；这些不是v1.0线上的JSON枚举值。[固定版proto](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

|v1.0枚举|教学字符串|理解重点|
|---|---|---|
|TASK_STATE_SUBMITTED|submitted|已受理，尚不能推断产物存在|
|TASK_STATE_WORKING|working|工作在进行|
|TASK_STATE_INPUT_REQUIRED|input-required|中断，需要补充输入|
|TASK_STATE_AUTH_REQUIRED|auth-required|中断，需要认证条件|
|TASK_STATE_COMPLETED|completed|成功终态|
|TASK_STATE_FAILED|failed|失败终态|
|TASK_STATE_CANCELED|canceled|取消终态|
|TASK_STATE_REJECTED|rejected|拒绝执行的终态|

TASK_STATE_UNSPECIFIED表示未知/不确定，实验拒绝把它当可继续执行的确定状态。input-required和auth-required并不代表已经成功、永远失败或获得了权限。接到认证要求，应回到受控认证流程；不能因为对方说“需要权限”就自行创建凭据。

**原创时间线：** submitted → working → input-required；用户补充目标版本后，仍是同一个task → working → completed。另一条路径可能在working时被拒绝，进入rejected。实验只验证已知状态与终态不可改变，没有宣称规范定义了一个必须逐边遵守的完整状态转移图，也不模拟输入或认证的有效性。

**追问：** 收到“正在等用户输入”，客户端应继续每秒重复发同一句话吗？

**参考答案：** 先明确缺什么输入、由谁提供、等待如何展示和超时如何处理。相同请求不能补足缺失信息。等待时保存当前任务身份和已验证产物，后续信息只发给对应任务；另一个任务的回答不能误解除这个等待。

<a id="a2a-terminal"></a>
## 4 任务完成后还想改报告，为什么要开新的工作单元

终态任务不能重新启动。后续修改可在同一context中建立新Task，并明确参考原任务和目标artifact；不要把旧Task改回working来掩盖新需求。客户端还需自行管理“哪一份新产物被接受”及版本关系，不能从同名文件推出它一定是最新认可版本。[任务不可变与后续修订](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/topics/life-of-a-task.md)

原创例子：task-1产出brief-v1，用户要求加一段失败分析。新工作记录输入来源为task-1的brief-v1，并有新的taskId。新产物未通过检查前，已接受的brief-v1保持可回查。若同context下已有两份简报，先确认指的是哪份，不自行选择最后到达的一份。

**实验验收：** 分别让completed、failed、canceled、rejected收到“改回working”，均拒绝且保持原状态；给终态任务追加产物也拒绝。实验对“增量事件不再修改已标complete的artifact”采用较严格的本地政策；非终态任务的较新权威快照仍可重建产物视图。终态Task的状态和产物则不能由快照改写。这些是本地验证选择，不等于A2A对每种产物修订方式都作了同样限制。

**追问：** 既然失败任务不能重启，重试是不是不可能？

**参考答案：** 可以创建新的执行尝试/任务，关联原任务、输入与失败原因。要另行检查哪些外部操作已完成或结果未知；新taskId不应自动生成新的付款、上传或邮件意图。任务重试与业务操作重试是两个身份域，幂等仍见A30。

<a id="a2a-artifact-stream"></a>
## 5 artifact最后一块到了，为什么整个任务仍可能没完成

产物更新带artifact身份；append控制追加到已有产物，lastChunk表示这一产物块流结束。状态更新与产物更新是不同事件，lastChunk不等于Task成功。客户端还需验证产物的格式、来源和业务要求。[流式指南](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/topics/streaming-and-async.md)

原创反例：报告正文已收完，但引用检查失败，Task随后进入failed。若UI在报告lastChunk时显示“全部成功”，就把一个中间产物当成了业务验收。

配套本地合同从空产物开始：revision1创建“draft”，revision2用append=False替换成“v2”，revision3追加“!”并标最后一块。得到v2!，任务仍是submitted。append=True却没有已有基块，会拒绝。重复收到同一个本地revision且内容相同，不会重复追加；同revision内容不同视为冲突。

这里的revision、冲突检测和摘要哈希是原创应用信封，不是A2A核心事件强制字段。若上游既无稳定事件身份也无回放保证，不能通过“给收到的事件临时编号”识别断线前后的重复，更不能按相同文本删除重复块。

**追问：** 两个内容相同的块是不是重复？→ 若正文真的连续写了两个“哈”呢？→ 断线后是重放增量还是返回全量快照？

**参考答案：** 内容相同不足以判断投递重复。使用协议/应用明确支持的事件身份；没有可靠身份时，重新取得权威快照，并按快照语义替换本地投影，不把全量快照追加到旧正文。

<a id="a2a-reconnect-cancel"></a>
## 6 断线恢复与取消竞争：先问远端发生了什么

断线只是观测连接中断，远端可能继续working、已经完成或已失败。v1.0的SubscribeToTask用于订阅现有非终态任务，规范要求首事件带当前Task快照；这减少先GetTask、再订阅之间的观察缺口。它不承诺每个历史增量都按通用SSE游标逐条回放。若任务已终态，查询终态与产物即可，不能硬把终态任务重新订阅成运行中。[订阅与取消规范](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#316-subscribe-to-task)

CancelTask是取消请求，可能与完成竞争，也可能在当前阶段不可取消。收到调用返回之前，UI可显示“已请求取消”；收到实际取消状态才显示“已取消”。若CancelTask返回不可取消错误，应查询当前Task，不能用客户端点击时间覆盖远端完成事实。[取消语义](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#315-cancel-task)

**原创两条时间线：**

1. 客户端请求取消 → 服务端先提交完成结果 → 客户端看到completed。取消没赢，不能把既有产物或副作用当不存在。
2. 客户端请求取消 → 服务端确认取消 → 客户端看到canceled。若已存在部分产物，是否保留或发布由业务合同决定。

本地request_cancel只改变cancel_requested；它既不调用网络，也不改Task状态。disconnect只使synchronized=False；已知working仍保留。后续事件被拒绝，直到install_snapshot安装非过期的权威视图。相同revision只接受与已知视图完全一致的快照，内容冲突仍拒绝。超过deadline或接收预算时不再通过无限重连续命，应结束这个观测器并按业务决定下一步。

**追问：** 当前快照仍是working，是不是系统卡死？

**参考答案：** 仅凭状态不变不能判断停滞。检查服务端更新时间、实际进度、等待条件、子任务和deadline。可按声明的服务节奏有界查询；告警与停止规则用明确证据，不用“连续三次相同”取代所有长任务的判断。

<a id="a2a-design-debug"></a>
## 7 系统设计题：让两个组织的Agent交付一份可核查报告

下面是原创设计答案，尚未部署：

1. 固定双方支持的协议版本、binding、输入/输出媒体类型和可选streaming能力。Agent Card的接口版本与Agent产品version分别记录；不把产品版本当协议版本。
2. 用户身份和允许分享的数据在可信入口确定。调用按接收方与任务范围限制；任务ID、Agent名称和公开Card都不能自行扩权。
3. 把任务目标、证据范围、输出要求、预算、等待出口写成业务合同。接收方内部怎样规划可以不公开，交付仍需有产物与缺口。
4. 持久化任务身份、状态、最后可信快照和产物引用；接收事件按任务分区，重复/冲突/失序进入恢复处理。生产写入要有原子边界，内存字典不能证明跨进程正确。
5. 断线使用已声明的GetTask/SubscribeToTask能力恢复；取消记录请求与结果；发送消息超时先查业务事实。SendMessage的重复检测是可选能力，messageId不是规范承诺的exactly-once执行。[幂等规则](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#331-idempotency)
6. 接收产物后独立核对引用、格式和允许动作，未通过验收不发布。链接型产物还要检查接收者确实可打开，不能把URL存在当可用性证据。

**排障顺序：**

- 收到0.3的working字符串却按1.0枚举解析：先核对协议与适配器，不先改模型Prompt
- 同context下两个Task状态互相覆盖：查存储分区和事件身份
- 重连后报告内容重复：查全量快照是否被当增量追加、append语义和稳定事件身份
- 点击取消后仍出现结果：查取消响应和提交先后，不直接判作违规忽视取消
- 主控自称成功却引用无效：查产物验证与最终验收，不把COMPLETED替代业务正确性

从v0.3迁移到v1.0要核对方法名、枚举大小写和消息包装；不能只改一个版本字符串。规范、proto和指南有表述差异时，先查固定提交的规范与数据定义，不依照老教程示例补字段。[迁移概览](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/whats-new-v1.md)

<a id="a2a-lab"></a>
## 8 真正运行的小实验与面试验收

在仓库根目录运行：

```sh
python -m unittest discover -s examples/interview_followups -p 'test_agent_protocol_lab.py' -v
```

核验环境Python3.12.14。38项unittest联合覆盖任务投影和工具流组装；其中任务测试覆盖中断/继续、四种终态不复活、取消胜负、产物追加/替换、重复冲突、失序后快照恢复、跨context、断线、时间和字节预算。本实验的TaskSnapshot.revision是本地应用字段，TaskEvent.kind也是本地类型，不是v1.0线上的序列化格式。

先预测，再跑测试：

1. Task是working、artifact已lastChunk，业务完成了吗？分别写两个断言
2. revision2未到而revision3到了，能不能直接把3追加？恢复全量abc后再收到4的d应是什么？
3. canceled和completed同时竞争，客户端怎样报告真实结果？谁负责原子裁决？
4. 同messageId重发能否必然只执行一次？原请求结果未知时应查哪份业务记录？
5. 四种终态中哪种能直接改回working？若答案是“没有”，怎样关联新的尝试？

**未测：** A2A SDK、协议线级编解码、HTTP/JSON-RPC/gRPC、认证、Agent Card获取、推送回调、真实重连、数据库持久化、跨进程原子性、外部副作用和真实模型。能够解释并运行本地合同，不等于完成了跨Agent生产互通。

**30秒主线：** A2A统一独立Agent之间的交付接口。先分消息、上下文、任务与产物身份，再分中断和终态。取消是请求，断线是观测中断；恢复读取权威快照，终态修订另开任务。协议版本、授权与业务验收仍需要单独验证。
