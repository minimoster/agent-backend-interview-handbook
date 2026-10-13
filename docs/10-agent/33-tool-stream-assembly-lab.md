# 工具调用流组装：从半段JSON到可验证执行意图

[返回Agent目录](README.md) · [Function Calling与Schema](01-agent-loop-tools-and-state.md#a03) · [SSE与可靠执行](04-streaming-and-reliable-execution.md) · [工具身份合同](31-tool-mcp-and-skill-contracts.md#tool-result-contract)

本章将多个工具调用的碎片组装成完整候选，通过可运行实验学习部分 JSON、重复、失序、截断和断线时的处理方式。基础章节先介绍模型提出调用、执行器负责校验。

核验日2026-10-11。厂商部分分别依据当日的 OpenAI Responses、Chat Completions 与 Claude Messages 官方文档，事件字段按接口分别说明。SDK、模型请求及模型兼容性尚未验证。配套代码接收本地规范化事件；厂商原始 HTTP 字节需要先经适配器转换。[技术参考](../../sources/agent-protocol-references.md)

[标准库源码](../../examples/interview_followups/agent_protocol_lab.py) · [38项联合测试](../../examples/interview_followups/test_agent_protocol_lab.py)

<a id="stream-layers"></a>
## 1 先分清四层，否则“JSON不标准”很容易修错地方

一次模型流经过四个不同边界：

1. 传输层读取字节。网络read可能停在UTF-8字符、SSE行或JSON事件中间
2. 事件层得到一个完整厂商事件。它可以包含文字片段、调用参数片段、结束、错误或其他信息
3. 组装层按调用身份保存参数片段，得到完整候选调用
4. 执行层做结构、业务、权限、预算和必要批准检查，才实际执行

同一个“解析错误”可能属于不同层。半个SSE事件不该进入事件JSON解析；一个完整事件里的arguments delta则可以合法地只有半段参数JSON。把它每次都当完整对象json.loads，会把正常分片误判成模型幻觉。[OpenAI函数调用流](https://developers.openai.com/api/docs/guides/function-calling#streaming)、[Claude输入JSON分片](https://platform.claude.com/docs/en/build-with-claude/streaming#input-json-delta)

例子：工具输入最终是{"document_id":"guide-A","limit":2}。前一个参数片段可能只有{"document_id":"gui，后一个才补de-A","limit":2}。前半段不能执行查询，也没必要要求模型立即修复它。

**追问：** 遇到JSONDecodeError应立刻重试模型吗？

**参考答案：** 先确定在哪一层、是否收到结束标记、请求是否失败/截断、完整参数是什么。正常未完片段继续有界接收；真实完整对象不合法才进入明确的有界修复或失败。工具执行过而响应未知时，问题又变成A29/A30的恢复合同，不能重发模型来猜外部结果。

<a id="provider-event-map"></a>
## 2 三种官方事件合同各自怎样关联身份

|接口|定位和累积|需要区别的完成信息|
|---|---|---|
|OpenAI Responses|output item的item_id/output_index定位；函数调用另外有call_id；arguments.delta提供字符串增量|arguments.done提供完成参数；请求还可能completed、failed或incomplete|
|OpenAI Chat Completions|choice范围内delta.tool_calls[index]；初始片段通常带调用id/name，后续常只带arguments|不能把Responses的事件名称、字段或结束语义直接搬来|
|Claude Messages|content_block的index定位；tool_use块有调用id/name；input_json_delta携带partial_json|content_block_stop结束块；message_delta/message_stop及错误事件属于消息级信息|

依据：[Responses事件参考](https://developers.openai.com/api/reference/resources/responses/streaming-events)、[Chat Completions函数流说明](https://developers.openai.com/api/docs/guides/function-calling#streaming)、[Messages事件流](https://platform.claude.com/docs/en/build-with-claude/streaming#event-types)。这里仅整理函数工具的相关字段，不覆盖内置工具、思考块、服务端工具或所有新增事件。

**原创适配器要求：** 保留provider、接口家族、request/response身份、调用定位键、结果回注身份和工具名。规范化start时建立身份，delta只往对应缓冲区追加，stop核对完成，finish描述整条请求的结果。未经确认不要把item_id当call_id返回工具结果。

OpenAI Responses原始事件有sequence_number，但“只挑出工具事件后还要求原编号连续”会因中间合法文字事件而误报缺口。Claude上述工具参数事件没有同一套必需的全局序号。实验sequence是本地测试信封的连续整数，不是强行增加厂商字段。真正的上游遗漏检测仍依赖原接口合同、适配器保留的信息及可核查的完成结果。

**追问：** 统一成OpenAI兼容HTTP接口，是否就不用做适配测试？

**参考答案：** URL和JSON形状类似不证明调用ID、拒绝、并发工具、流片段、结束、用量和错误语义一致。用明确接口、固定版本与合成边界样本测适配器；本实验只测规范化后的组装，尚未证明任何厂商转换正确。

<a id="stream-call-buffers"></a>
## 3 多个调用交错回来，为什么必须分缓冲区

失败时间线：

- start：调用a，call-a，lookup_doc
- start：调用b，call-b，lookup_doc
- a的delta：{"document_id":"A",
- b的delta：{"document_id":"B","limit":1}
- b停止
- a的delta："limit":2}
- a停止，然后请求成功完成

b先完成是合法的跨调用交错，不等于a内部参数可以乱序。按一个全局字符串拼接会产生不属于任何调用的混合JSON。按工具名分组也错：a、b可以调用同一个lookup_doc，但输入和结果身份不同。

实验使用request_id＋call_key分区，同一request中call_id必须唯一。未知key、第二次start、变更身份或已stop后的新delta均拒绝；没有根据到达顺序猜测工具名。结果返回时仍用各自call_id，不能让b的文档结果满足a的请求。

**追问链：** 同名工具两次调用 → 何时建ID映射？→ 后续没有name怎么办？→ b先结束怎么办？→ 同一个key被重新绑定为别的call_id怎么办？

**参考主线：** 起始事件建立稳定映射，后续按定位键查原身份。缺初始身份、重复冲突和未知调用需要明确错误，不自动补造。允许独立调用交错，保持每个调用的片段顺序与终态独立。

<a id="stream-completion"></a>
## 4 参数看起来已经是JSON，什么时候才可以交给执行器

合法JSON只证明这段文字当前能解析。组装器还要知道上游是否结束该调用、后续是否还有内容、请求是否被截断或失败。一个done事件里的完整arguments是最终快照，不能再追加成两个对象。Claude官方建议累积工具输入片段，到content_block_stop再解析。[Claude工具输入流](https://platform.claude.com/docs/en/build-with-claude/streaming#input-json-delta)

**本实验的保守本地策略：** 每个调用stop后解析完整对象，全部调用已stop且request级finish=completed后才允许calls()取出候选。stop可携带最终参数字符串，本实验要求它与累计字符串完全一致；仅空白不同也会拒绝，这是检测适配器不一致的严格教学选择，不是所有厂商强制的字符串相等规则。

这种策略会延后启动工具。生产系统若在单个call已明确完成后提早执行，也应单独定义：哪些无副作用工作可提前启动，稍后的模型失败如何处理，以及已产生的外部副作用怎样记录。不能把“更低时延”当提前提交支付、发信或上传的许可。

**三个反例：**

1. complete JSON delta已到但stop没到：只能是候选缓存
2. call已stop，但request随后incomplete：实验不释放调用
3. request已completed，随后正常连接关闭：不能把已经完成的候选倒改为失败；也不能认为工具本身已经执行

没有tool call的completed请求返回空候选。这可以代表纯文字回答，不能据此断言用户的业务目标完成。完成条件仍由真实任务产物决定。

<a id="stream-json-validation"></a>
## 5 完整JSON之后，仍有四道不同的检查

第一道是明确的JSON输入政策。本实验要求根是对象，拒绝重复键、NaN/Infinity、解析后溢出为无穷的数字、过长整数及无效Unicode scalar；先限字节与结构深度，再解析，最后限节点数。这是较严格的教学子集，不是完整JSON Schema引擎。Python默认JSON解析会接受部分非标准数值和重复键，因此不能把默认解析成功当严格JSON验证。[Python3.12 JSON说明](https://docs.python.org/3.12/library/json.html)

第二道是工具结构：名字是否注册，必需字段存在吗，类型、未知字段、范围是否符合该工具契约。第三道是业务：目标文档是否存在、版本与任务是否吻合。第四道是授权：当前认证身份是否还能读取这个目标。结构与权限必须分别检查，不能把模型提供的tenant_id当可信身份。

原创lookup_doc只接受document_id和limit，limit必须是真正的整数1–5。Python中bool是int的子类，所以仅用isinstance(limit, int)会把True当1，本实验用type(limit) is int拒绝。allowed_documents来自可信调用环境；模型即使输出合法字符串B，若B不在当前范围内仍拒绝。

validate_lookup只返回经过验证的预览字典，不查数据库、不执行工具；它没有实现目标存在性和版本检查。相同候选在稍后执行时仍要重新核对当前授权。高影响动作的批准、幂等和未知结果恢复继续沿用A30与生产设计章节，不由流式组装器替代。

**追问：** strict输出模式能否删除服务端校验？

**参考答案：** 它缩小一部分结构错误的空间，仍要处理拒绝、未完成响应、适配器错误、业务对象、权限、预算和副作用。官方Schema支持范围也有约束；本实验未运行strict模型请求，不能用它声称模型结构成功率。

<a id="stream-duplicates-disconnect"></a>
## 6 重复、乱序和断线：哪些可以修，哪些只能明确失败

有稳定信封身份时，同序号、同内容的重复可忽略；同序号不同内容是冲突。新的序号即使内容与前块一样，仍是新内容。比如两次独立的“ha”应合成haha，不能按文本去重。

实验对连续本地序号做严格检查：跳号或倒序不缓存等候、不猜排序，直接失效并清理所有未提交参数。允许不同调用交错，却不允许同一事件序列缺口。这是有界失败设计，不是说明真实TCP会乱序交付给应用；失序通常来自自己的并发消费、队列或适配层。

断线前的参数不能接在“重新发模型请求”的新输出上。新请求可能选择不同工具、call_id或参数，旧的半对象没有兼容保证。实验abort(disconnected)使未完成候选不可取；新模型尝试建立新的request_id和Assembler。若旧工具已经执行，先查操作记录，不能用丢弃参数缓冲来撤销现实副作用。

**追问：** 可以根据断线前最后看到的序号恢复吗？

**参考答案：** 只有接口明确支持的恢复/回放合同才可以。SSE这个传输形式本身不证明任意模型API支持通用续传。没有恢复保证时，记录未完成原因、保留受控诊断，再决定是否新请求；是否已经执行的业务结果要另查。

厂商可能新增事件。官方Claude流文档要求优雅处理未知类型；适配器可对已知非工具事件做有界忽略或专门处理，而不能把它们送给本实验后冒称已支持。本实验未知“规范化”kind会拒绝，保护本地合同；两层处理并不矛盾。[事件扩展说明](https://platform.claude.com/docs/en/build-with-claude/streaming#other-events)

<a id="stream-resource-budget"></a>
## 7 只限制输出token，为什么仍可能撑满组装器

工具参数、工具数量、事件数量、重复投递和日志都可能消耗资源。模型max_tokens不是网络请求体、缓冲器、JSON深度或调用并发的完整上限。

本实验默认上限是教学常量，不是生产推荐：

- 256次接收，包括重复与安装任务快照；重复不能无限消耗CPU而不计预算
- 身份字段最多128个UTF-8字节；一个规范化事件最多16384字节
- 最多8个调用，每调用参数最多16384字节，总参数最多32768字节
- JSON嵌套最多16层、解析后值节点最多512个、整数最多256位数字
- 任务最多8份文本产物，单份16384字节、合计32768字节
- 每次update检查调用者提供的可信单调时间；now达到deadline即拒绝

原始对象已经进入Python时，分配的一部分成本已经发生。生产传输层必须在读取和反序列化之前另设请求体、frame/event、连接、队列、时间和日志限额。JSON节点数在标准库解析后检查，先行字节上限约束此前分配；不能说它是能在任意巨大JSON分配前及时停止的流式解析器。

**复杂度：** 各片段用列表保存、stop时join，避免每次字符串相加反复复制完整历史。摘要表最多保留有限事件的固定长度哈希，不保存无限原始事件。调用数与总字节限定内存，错误后清理未提交缓冲。取出参数用deepcopy，外部修改不会污染内部候选；这也有额外分配成本，受前面的总量约束。

**追问：** 重复事件都被忽略，攻击者是否仍能一直占用服务？

**参考答案：** 能，所以计接收次数、总时长和连接预算，第一次预算错误后调用者应停止消费。幂等只解决重复影响，不免费提供无限计算资源。实验没有真实压力、异步背压或多连接测试。

<a id="stream-design-debug"></a>
## 8 设计题与排障题：做一个可替换模型的工具网关

**原创模块合同：** 字节/framing层 → 厂商事件适配器 → 有界组装器 → 工具验证/授权 → 执行器 → 按原call_id回注。每层有独立错误类别，Trace记录provider/API家族、request_id、定位key、call_id、字段版本、结束原因和字节统计，不默认记明文秘密或完整参数。

排障时逐层验证：

|现象|先检查|不要先做什么|
|每收到参数delta就JSON报错|是否把正常半对象提前解析|不断加Prompt要求“输出JSON”|
|a返回了b的数据|key/ID映射和并行合并|按工具名或到达顺序匹配结果|
|完整参数变成两个对象|done快照是否又被追加|删除报错位置的字符后执行|
|同一条内容重复展示|稳定事件身份、不同序号是否真实重复|按文本相同去重所有片段|
|连接断了却仍执行|候选释放时机、取消/失败传播|把EOF当成功标志|
|JSON合法但读取越权文档|可信身份与执行入口授权|相信模型填的tenant_id|
|内存持续上涨|总参数/事件/日志/队列限额|只调模型token上限|

**验收方案：** 先测各厂商真实适配器的保留字段与正常事件，再将相同工具合同放入组装/验证层。拒绝、max-token截断、多个调用、空输出、未知事件、延迟、取消、网络中断和SDK升级应进回归。完整端到端验证还要检查工具真实结果与最终任务目标；组装正确不等于模型选对工具。

<a id="stream-lab"></a>
## 9 先预测，再运行38项联合测试

在仓库根目录运行：

```sh
python -m unittest discover -s examples/interview_followups -p 'test_agent_protocol_lab.py' -v
```

Python3.12.14本地通过。工具测试包括所有两段切分位置的合成JSON、中文/emoji及转义、同名调用交错且倒序结束、完整JSON未提交、重复与真实重复文本、冲突与缺口、最终快照不一致、停止后片段、跨请求、错误身份、截断/取消/断线、空调用、已完成后连接关闭、字节/事件/深度/节点边界、权限与防修改副本。38项按 unittest 方法计数，循环子样本在各方法内部执行。

练习：

1. 给{"x":"中\\u4e2d"}枚举每个字符串切分点；哪些半段能解析？即使能解析，何时可取候选？
2. 两个lookup_doc的key为a/b，b先stop；写出两份输入和对应结果ID
3. 合法JSON里limit为true、limit为6、额外tenant_id分别在哪层拒绝？文档B越权又在哪层？
4. 同sequence重放“ha”和新sequence再次出现“ha”怎样区别？若没有稳定序号能承诺去重吗？
5. 组装器完成后，工具调用超时且可能已经执行，下一步为何不属于本章的字符串修复？

**未测：** 原始UTF-8字节/SSE framing、真实socket、厂商事件适配、模型/SDK/网络、工具执行、完整JSON Schema、异步并发/背压、磁盘恢复、真实认证、外部副作用或API续传。这里测试的字符串含Unicode，但没有证明网络在UTF-8码点中间断开的字节解码实现正确。

**30秒主线：** 流式工具调用先分事件与参数片段，再按调用身份有界累积。完成标记后得到候选，严格解析与服务端业务/权限校验后才可执行。重复靠可靠事件身份，断线与失败分别返回明确状态；厂商适配与真实执行要另外验证。
