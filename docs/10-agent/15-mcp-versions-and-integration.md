# MCP版本边界与安全集成

[返回 Agent 目录](README.md) · [基础题](01-agent-loop-tools-and-state.md) · [版本与纠错](../../errata/README.md)

本章以2026-07-28为现代协议基准，并显式对照2025-11-25。SDK版本、协议版本、传输和业务状态是不同概念；面试与示例都应明确使用哪一组。

技术资料核查于2026-10-09。设计建议用于练习方案取舍，文中实验仍待执行；实际运行记录另列。

<a id="fa26"></a>

### FA26 MCP为什么是接入协议 与HTTP函数调用和Skill是什么关系？

**优先级：P0。**

**知识点详解**

Host是使用模型的应用，内部Client承担与服务交互，Server提供工具、资源或提示模板。MCP用统一消息与方法定义能力接入；HTTP是可承载消息的传输，二者不是替代关系。Function Calling表达模型想调用什么，执行层把它路由到本地函数或MCP；Skill描述怎样完成任务，可组织多个工具。Server可以是远程服务，不必是本地子进程，也不必包含一个Agent。

**具体例子**

三个应用都要接两个知识服务。没有共同接口时可能重复写多组适配；共同遵循MCP后，应用接Client接口，服务实现Server契约，通用适配可复用。所谓从M×N到M+N只是解释复用方向的概念模型，实际仍有认证、字段语义、版本、部署和运维成本。

**常见误区与适用边界**

“通用插口”类比止于接口契约；版本、可选能力、权限和数据格式必须兼容。MCP不会自动生成正确工具描述，也不承诺调用结果准确。HTTP本身可支持流式响应，应用也可在其上维护业务会话，因此不能说只有MCP才有这些能力。

**30 秒答题主线**

我按层解释：模型提出调用，工具提供能力，MCP统一能力接入，HTTP或stdio承载消息，Skill提供任务方法。协议减少重复集成，但业务语义与安全责任不会消失。

**追问与验证**

追问：工具发现后能否直接执行？验证：发现、模型选择、参数校验、身份授权与调用分别设置检查点；列出工具并不等于用户批准所有动作。

**来源**：[FA-S024](https://modelcontextprotocol.io/specification/2026-07-28)、[FA-S026](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports)。

<a id="fa27"></a>

### FA27 MCP 2026-07-28和旧版生命周期 传输有何关键区别？

**优先级：P0。**

**知识点详解**

2025-11-25及更早版本使用initialize初始化握手；2026-07-28的核心采用自包含请求，逐请求携带版本、客户端身份和能力元数据，取消旧initialize/initialized交换与协议层Mcp-Session-Id。server/discover由服务端实现，客户端可以先调用但不是每次业务调用的前置握手。业务需要跨调用状态时仍可保存自己的任务记录和显式句柄。

**具体例子**

现代客户端先确认或发现支持版本，取得工具契约后发送tools/call；Host执行校验与授权，接收结果再反馈模型。工具中途需要输入时，新版MRTR用input_required结果请求补充，客户端按协议附带输入重发原调用，而非假设服务端始终能在长连接上反向发请求。

**常见误区与适用边界**

标准传输包含stdio与Streamable HTTP，后者可返回JSON或请求范围内的SSE流；“旧HTTP+SSE被弃用”不等于SSE技术被禁止。新版无协议会话不等于无业务状态。SDK可能默认仍使用legacy模式或提供auto/pin，安装新SDK不自动证明实际走新版；弃用也不等于已移除。

**30 秒答题主线**

我先声明协议和SDK版本。旧版讲握手，新版讲逐请求元数据与可选发现，再说明stdio或Streamable HTTP的实际绑定；兼容回退和业务状态单独处理，不把两代行为拼成一个流程。

**追问与验证**

追问：新版客户端遇到旧服务器怎么办？验证：用固定SDK版本测试modern、legacy、双模式组合及不兼容失败。本文不提供未经运行的SDK构造代码，也不声称完成跨版本互通测试。

**来源**：[FA-S025](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning)、[FA-S026](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports)、[FA-S029](https://blog.modelcontextprotocol.io/posts/2026-07-28/)、[FA-S030](https://ts.sdk.modelcontextprotocol.io/v2/protocol-versions)、[FA-S031](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle)。

<a id="fa28"></a>

### FA28 MCP工具目录怎样发现 缓存和感知变化？

**优先级：P1。**

**知识点详解**

工具目录由tools/list获得，包含工具名称、描述和输入schema，分页时需继续读取游标。目录会变，不能只启动时读一次便永久缓存。2026-07-28工具规范允许列表缓存提示；服务声明listChanged后，应向已用subscriptions/listen订阅toolsListChanged的客户端发送列表变更通知，客户端据此刷新。旧版通知流程应查对应版本。

**具体例子**

服务把export_report新增一个必填format字段。Host收到变更通知后使旧schema缓存失效，重新获取目录，后续参数按新契约构造。若通知连接中断，Host按缓存有效期或调用失败后的刷新策略补救，而不是永远重发旧参数。

**常见误区与适用边界**

通知通常表示“目录变了”，不应假设它携带全部新定义。缓存必须考虑用户身份、权限、服务和协议版本；私人目录不能因为某次响应可缓存就跨用户分享。工具说明和安全注解本身也可能来自不可信服务，不能用它们免除执行鉴权。

**30 秒答题主线**

我把目录当有版本和寿命的契约缓存，既支持主动拉取，也处理声明且订阅的变更通知。刷新后校验schema与权限，失败时区分过期目录和业务错误，避免无意义重试。

**追问与验证**

追问：拉取第一页就够吗？验证：构造多页工具列表、权限撤销、通知丢失和schema变更，确认目录完整且旧权限不会被缓存恢复。

**来源**：[FA-S027](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)、[FA-S021](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)。

<a id="fa29"></a>

### FA29 多个MCP服务怎样编排 谁负责失败预算和业务状态？

**优先级：P0。**

**知识点详解**

MCP提供能力接入契约，具体业务顺序通常由Host的运行时或上层编排器决定。它需要维护服务与工具的唯一标识、依赖、任务状态、超时、并发限制和总预算。工具名相同也不能混淆来源；只读且独立的调用可以并行，有数据依赖或共享副作用的操作要显式排序。

**具体例子**

任务先搜索公开文件，再生成摘要，最后经批准上传。两个搜索服务可并行；摘要依赖已核对证据；上传依赖审批与文件版本。一个搜索超时可以退化为报告覆盖不足，上传超时却可能已成功，不能简单重发而造成重复文件。

**常见误区与适用边界**

RPC请求成功不代表业务目标完成，重试也不保证幂等。由服务返回的工具结果只是观察，不能给下一服务授权。跨服务传递数据前必须检查接收方和用途；较小的调用结果也可能包含敏感信息。不存在“接入MCP就自动拥有完整多Agent编排”的保证。

**30 秒答题主线**

我把MCP作为工具接入层，把依赖、预算、状态和副作用控制放在应用运行时。每次调用关联服务、任务和调用ID，区分可重试错误与结果未知，最终按业务证据验收。

**追问与验证**

追问：两个服务都叫search怎么办？验证：内部路由使用服务ID加工具名，故意返回错误服务结果应被拦截；中途取消后检查未开始步骤不再执行。

**来源**：[FA-S024](https://modelcontextprotocol.io/specification/2026-07-28)、[FA-S023](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)。

<a id="fa30"></a>

### FA30 MCP部署时为什么仍需要鉴权 沙箱和审计？

**优先级：P0。**

**知识点详解**

MCP不天然提供沙箱，也不把所有部署强制变成API Key认证。HTTP授权规范与stdio凭据获取方式不同，远程实现应按采用版本核对OAuth、受保护资源、issuer和token受众等要求。Host和Server还要分别验证当前身份、资源范围与动作权限，不能把模型参数中的user_id当真实身份。

**具体例子**

一个MCP查询服务接入内部文档：网关确认调用者，服务端把租户与资源权限加入检索条件；工具只允许受约束查询，返回有界内容。执行代码的服务另用隔离环境，默认不挂载宿主机凭据，并限制网络、时间和产物大小。日志记录状态与请求关联，秘密字段先脱敏。

**常见误区与适用边界**

网络认证成功只说明连接身份，不代表能访问每个文档；允许使用某工具也不代表任何参数都安全。本地stdio进程继承过多环境变量同样危险。不能把上游token随意透传给不同受众的下游服务，也不能用工具自称只读作为唯一安全依据。

**30 秒答题主线**

我按传输和版本实现认证，再在每次操作做资源级授权与参数校验。危险能力放隔离环境，凭据不进入模型与日志；审计保留必要证据，协议接入不替代这些控制。

**追问与验证**

追问：工具被撤权但旧调用已排队怎么办？验证：执行时再次授权，测试跨租户ID、过期token、错误受众和恶意URL，并检查日志无秘密原文。

**来源**：[FA-S028](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)、[FA-S021](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)、[FA-S022](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)、[FA-S012](https://opentelemetry.io/docs/security/handling-sensitive-data/)。
