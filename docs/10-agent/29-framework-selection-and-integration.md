# Agent框架选型与组件集成

[返回Agent目录](README.md) · [验证范围](../../coverage/AGENT_LABS_VALIDATION.md)


先说明系统缺什么，再说明框架补什么。固定步骤可以用普通代码；需要长期状态、人审恢复或多角色交付时，再比较相应抽象。本章补选型与接口，不重述[A01–A08](01-agent-loop-tools-and-state.md)的行动循环，也不把厂商介绍当项目成绩。官方入口核查日期为2026-10-10；本章没有安装或运行这些框架，不提供未经版本固定的API代码。

<a id="selection-contract"></a>
## 1 先写选型合同

选型前列出输入输出、确定步骤、动态决策、任务持续时间、状态恢复边界、工具及数据接收方、部署方式和团队语言。然后问：若不用框架，哪些代码仍必须自己写？框架能减少哪一项重复工作，又会增加哪些依赖、学习与升级成本？

例如只需“读取三个授权文件→汇总→生成本地报告”，普通函数组合足够形成基线。若报告中途等待用户批准、进程可能重启、需要查看每个节点的状态，则持久编排更有价值。框架的checkpoint不能替代外部操作的幂等记录，组件名也不证明已经有恢复合同。

<a id="ecosystem-matrix"></a>
## 2 按职责比较候选

下面是官方资料支持的职责定位和原创试验问题，不是品牌排名或互斥分类。同一系统可以组合组件层、数据层和编排层。

|候选|先考察的职责|最小验证问题|
|---|---|---|
|[LangChain](https://docs.langchain.com/oss/python/langchain/overview)|模型、工具与Agent循环组件|替换模型或工具后，输入输出及错误语义能否保持？|
|[LangGraph](https://docs.langchain.com/oss/python/langgraph/overview)|有状态编排、持久化、流式与人审|中断后恢复到哪个节点？哪些节点可能重放？|
|[LlamaIndex](https://developers.llamaindex.ai/python/framework/)|数据摄取、索引、查询与工作流|引用能否回到原文版本与位置？解析和检索能否分别替换？|
|[AutoGen](https://microsoft.github.io/autogen/stable/index.html)|Core事件运行时、AgentChat与扩展|交付边界、终止和消息成本能否被验证？不可把旧0.2接口混入新AgentChat。|
|[CrewAI](https://docs.crewai.com/v1.15.26/en/concepts/crews)|角色、任务与Crew协作|任务产物是否被下游校验？角色名称是否掩盖共享状态冲突？|
|[MetaGPT](https://github.com/FoundationAgents/MetaGPT)|面向任务分工和产物的多Agent组织|角色间实际传什么产物？一个产物错误会怎样阻止后续步骤？|
|[OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)|Agent循环、工具、交接与追踪|handoff如何限制数据和权限？追踪怎样避免记录秘密？|
|[smolagents](https://huggingface.co/docs/smolagents/index)|工具Agent与代码执行路线|代码在哪个隔离环境运行？文件、网络和时间预算由谁落实？|
|[PraisonAI](https://praison.ai/docs)|其官方提供的Agent与工作流接口|先核对实际语言、组件、部署和版本，再用同一任务验证，不能由名称推出优劣。|

这些入口在读取日可访问。CrewAI入口明确重定向到v1.15.26；其余未给代码的入口仅是当日文档观察，不代表已锁定可重现SDK版本。版本选择、许可、支持周期和供应商服务费用仍需随实际采用另查。不要引用未经统一测量的发布时间先后、兼容模型数量、代码行数或流行度作为选型证据。

<a id="pipeline-state-graph"></a>
## 3 普通pipeline与状态图怎样分界

线性pipeline适合步骤和错误出口清楚、无需跨进程等待的流程；分支并不自动要求框架，普通代码同样能表达。状态图更适合显式节点、条件路由、有限循环、并行合并和人审恢复需要共同管理的情形。LangGraph不是只能表达DAG：控制图可以有环，预先排定的一次性依赖计划则可要求DAG并做拓扑检查。

比较两种实现时固定一份合同：同样的输入、工具、预算和终态。至少让流程在检索结束后暂停、恢复、再次收到旧结果，再检查证据是否重复追加、批准是否仍绑定当前产物、外部动作是否被重放。记录节点状态和恢复事实，比“图更高级”更有说服力。状态字段与reducer基础沿用[A05](01-agent-loop-tools-and-state.md#a05)，异步恢复沿用[A27–A30](04-streaming-and-reliable-execution.md#a27)。本节试验未运行。

<a id="component-interfaces"></a>
## 4 模型 模板 状态 工作流 决策与工具分别负责什么

模型适配器统一可支持的请求、拒绝、截断、调用ID和错误语义；模板把可信固定指引与运行变量分开；状态保存当前目标与可恢复事实；工作流定义步骤与分支；决策器提出候选动作；工具执行器完成有界能力。这是职责分解，不要求每个职责都有一个框架类。

提示模板应声明变量含义、类型、来源和默认值。例如user_question只放用户问题，retrieved_evidence只放带来源的数据，不把检索文本插入能授予权限的指令位置。模板版本测试缺变量、空值、超长文本、特殊字符与恶意材料；模板渲染成功只是字符串构造成功，不是答案正确。

“Chain”可以理解为确定步骤组合；动态探索再引入Agent或图。短期上下文与长期事实读写沿用[A19–A23](03-memory-and-context.md#a19)。历史Memory、Chain或Agent类名可能改变，不把旧接口清单当当前LangChain API。

<a id="strategies-and-history"></a>
## 5 策略名称与历史项目要分开

按任务解释策略：已给资料上直接生成、行动后继续决策、先计划后执行、失败后做有界修正、独立分支协作。zero-shot通常指不提供任务示例，不意味着没有提示或指令；某框架旧版的类名也不等于这些通用概念的永久标准。ReAct记录可审计动作、结果和简短理由，不要求公开完整内部推理。

AutoGPT与BabyAGI早期常被用来讲解“目标→任务队列→执行→结果生成后续任务”的循环。它可用来说明任务去重、优先级、公平性、预算及停止，不是当前生产推荐。读取日[AutoGPT官方入口](https://agpt.co/docs/platform)已是平台文档；[BabyAGI当前仓库](https://github.com/yoheinakajima/babyagi)也不能自动等同早期任务队列脚本。引用历史实现时写清具体提交，不能拿历史教程推断当前产品机制。这里没有复现任一项目。

多Agent应围绕可检验交付物设计：检索者提供证据列表和覆盖缺口，审阅者核对引用，主控只合并已验证产物。两分支同时改同一资源或传递大量重复上下文时，收益可能抵不过协调成本。协作合同和同预算基线见[A07](01-agent-loop-tools-and-state.md#a07)与[生产设计](26-agent-production-design-lab.md#multi-agent-contract)。

<a id="retrieval-service-boundary"></a>
## 6 LlamaIndex与工作流怎样组合

让摄取与检索成为可替换组件，不让索引内部对象成为任务持久状态。一个自定义检索合同可以接受query、已认证的访问范围、目标时间和候选预算，返回evidence_id、document_id、revision、原文位置、文本、来源和检索诊断。访问范围由可信调用环境提供，不能直接信任模型填写的tenant_id。

LangChain或其他工作流调用这个组件，再用受控证据构造上下文。LlamaIndex是否以库、服务或工具包装接入，是部署选择；不必把两个框架的数据模型强行放进同一全局状态。没有证据、解析失败和权限不足分别返回明确状态；下游不能把“空列表”一律解释为资料不存在。

**原创接口练习：** 用假检索器分别返回旧版本、越权材料和缺失位置的证据。组装器应拒绝不符合合同的项；更换检索实现时保留同一验收。本节未运行框架集成，具体分块和证据实验见[检索工程补充](30-rag-data-and-chunking-lab.md)。

<a id="rest-tool-adapter"></a>
## 7 框架怎样调用REST服务

模型输出工具名和参数意图，应用在执行入口校验，再由HTTP客户端或MCP适配器真正调用。REST包装处理URL、身份、序列化、超时、响应大小及错误转换；模型厂商的tool-call消息处理调用ID与结果回注。两种合同都要验证，不能说“LLM直接访问API”。

工具注册至少说明名称、用途、必需输入、输出、错误和副作用。增加工具后先验证可发现、可选中、合法调用、非法参数拒绝与结果关联，再加入任务回归。厂商消息、旧RequestsTool或旧functions字段不能凭名称直接套用；本章不复制不完整上传样例。工具细节见[实用工具合同](31-tool-mcp-and-skill-contracts.md#tool-result-contract)。

<a id="selection-experiment"></a>
## 8 怎样证明采用框架值得

做三层对照：普通代码基线、候选框架最小配置、增加可选能力后的配置。用相同任务测可恢复终态、修改接口的工作量、调试所需证据、总调用/上下文、尾延迟和部署维护；不只比较演示代码行数。固定版本和测试环境，保存具体失败，不宣称未执行的提升比例。

工具治理、租户、消息队列、企业身份、人审及审计都应有明确系统责任。框架可以帮助连接这些机制，不能由一个“生产就绪”标签代替核验。一般评测和观测沿用[评测章节](25-agent-evaluation-and-routing.md#eval-contract)与[FA41](18-harness-runtime-and-observability.md#fa41)。

**30秒主线：** 先把状态、数据、工具和交付需求写成合同。选择能减少明确重复工作的框架，用普通代码作基线，验证中断恢复与错误出口。介绍与API按版本讲，设计建议与项目实现分开。

**追问：** 更换检索器但不改Agent控制流，需要哪一份接口？checkpoint恢复后为什么还要核对外部副作用？能举一个有环控制图与DAG任务计划共存的例子吗？
