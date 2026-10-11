# Agent协议追问：来源、版本与实际验证范围

核验日2026-10-11。对应[32 A2A任务生命周期](../docs/10-agent/32-a2a-task-lifecycle-lab.md)和[33 工具调用流组装](../docs/10-agent/33-tool-stream-assembly-lab.md)。章节、例子与代码为原创教学材料，第三方面经只保留短主题和公开出处，不转载正文或图片。

## 公开面试线索与归类

本次使用有界便利样本，不能估计面试频率、公司统一题库或录用概率。“作者自述”与“技术结论得到官方资料支持”分开记录；标题写面经不自动构成第一手经历。

|记录|公开出处与日期|归类与使用边界|
|---|---|---|
|AE01|[GitHub hello-agents面试总结](https://github.com/datawhalechina/hello-agents/blob/main/Extra-Chapter/Extra01-%E9%9D%A2%E8%AF%95%E9%97%AE%E9%A2%98%E6%80%BB%E7%BB%93.md)，文件显示更新2025-10-15，提交d2f693f24f64282f1bfaa534584130c1c83ff7a3|正文可读。作者自述来源为2025秋招多次线上面试；是回顾式自报，没有逐题公司/轮次。A2A、工具调用、框架选型与评测作为主题线索；文件更新时间不是面试日期。|
|AE02|[牛客：大模型应用开发面经（5年经验）](https://www.nowcoder.com/feed/main/detail/129eaa1c20444651ac3b932e200d3da4)，作者大模型小坛，原页显示2025-07-27 08:47|公开作者栏与正文可读。第一人称回顾自称近半年的面试，列出A2A、工具、并发和系统设计主题。公司与经历未经独立核实；没有精确面试日期，不能把题目绑定到某一家企业。|
|AE03|[牛客：阿里Agent面经](https://www.nowcoder.com/feed/main/detail/19d7174168ca4bd280f5ece41897a3b5)，作者做算法的小吴，显示07-14 00:40|公开正文与作者栏可读，年份未显示，不补年份。问题列表涉及不完整/不标准工具JSON、捏造参数与并发；缺明确第一人称经历段落，低置信度题单，不计为新增已核实候选经历。|
|AE04|[知乎：百度文心一言团队大模型Agent面经分享](https://zhuanlan.zhihu.com/p/28923477420)|公开正文可读，开头明确是整理面试题的商业/编辑文章，归类二手报告。主题含工具调用和Agent设计；未取得可靠发表/面试日期，不计第一手经验。|

补充检查的[牛客匿名游戏公司Agent面试自述](https://www.nowcoder.com/feed/main/detail/416c3118a9c84fe0a43dc00f9eb9bec2)正文可读，涉及迭代反馈、最小发布和Coding Agent反复修复；没有本次核对的作者/日期，不计入核心带日期样本。[Binance面经](https://www.nowcoder.com/discuss/883873610329341952)混合自述与长推荐答案，作者评论也承认现场回答是临场发挥；产品架构描述和百分比均未作为事实使用。

### 请求平台的访问边界

- GitHub、牛客：本章采用的上述公开正文可读；面试发生及作者身份没有公司级验证
- 知乎：AE04可读但为二手；另一个候选页[大模型应用开发面经](https://zhuanlan.zhihu.com/p/1928735725647562675)本次未取得可用正文，不据此判断网站或全站可达性
- 小红书：限定三次尝试。第一次site域名搜索无结果；第二次explore范围搜索只得到[公开发现页](https://www.xiaohongshu.com/explore?language=zh-CN)；第三次读取该入口只取得发现导航与无关推荐卡片，另有广告屏蔽提示。该页返回的是2026-10-09缓存，不能冒充当日实时复核。本次没有符合原帖URL、作者、日期、正文核对要求的Agent面经，第一手样本为0。没有登录、转载OCR替代、构造访问令牌或绕过受限页面

“小红书公司在牛客的面经”仍属于牛客平台，不能为了凑齐平台数量改标成小红书来源。以上是本次搜索边界，不是断言平台上不存在相关经验。

## 一手技术依据与固定版本

|编号|已读官方资料|支持点与限制|
|---|---|---|
|AP01|[A2A v1.0.1发布](https://github.com/a2aproject/A2A/releases/tag/v1.0.1)|官方发布标签关联3303592588e388e62e0f69f701af531d2f4e3991；发布页显示2026-05-28，变更记录标题为2026-05-26。两种日期不混为同一事件。|
|AP02|[v1.0.1规范](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md)|CancelTask、SubscribeToTask首快照、终态、授权可见性及SendMessage可选幂等。固定标签，不依赖滚动latest。规范Markdown中的表格生成宏不能当成展开的数据定义。|
|AP03|[v1.0.1 specification/a2a.proto](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)|已通过只读官方仓库资源获取，blob400cdbad934654e27d7abbae1e145923eb40ac52。确认TaskState、Message、Artifact、append/last_chunk与接口protocol_version。路径是specification/a2a.proto，猜测的spec/a2a.proto在该标签不存在。|
|AP04|[v1.0.1任务指南](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/topics/life-of-a-task.md)|Message/Task、上下文分组、终态不可重启、后续修订和客户端管理产物版本。指南可能保留旧表示，线上枚举与方法以固定规范/proto为准。|
|AP05|[v1.0.1流式指南](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/topics/streaming-and-async.md)|状态与产物分开、append/lastChunk、流中断及现有任务订阅。没有把指南老类型名和历史anchor拼成可运行客户端。|
|AP06|[v1.0.1 A2A/MCP比较](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/topics/a2a-and-mcp.md)|接入工具/资源与独立Agent交付的互补定位；不把分类当所有实现绝对边界。|
|AP07|[v1.0迁移概览](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/whats-new-v1.md)|0.3到1.0方法名、枚举、包装和接口版本的迁移提醒。具体字段仍回到AP02/AP03，不把指南每个示例当无误数据结构。|
|AP08|[OpenAI函数调用](https://developers.openai.com/api/docs/guides/function-calling)|应用执行工具、Chat Completions工具delta按index聚合、初始身份与增量参数。滚动官方网页核验于2026-10-11，没有SDK/model/API头的运行记录。|
|AP09|[OpenAI Responses流事件](https://developers.openai.com/api/reference/resources/responses/streaming-events)|item_id/output_index、sequence_number、function_call_arguments.delta/done及请求completed/failed/incomplete。没有把本地连续sequence契约宣称为厂商无损续传保证。|
|AP10|[Claude Messages streaming](https://platform.claude.com/docs/en/build-with-claude/streaming)|content_block index、input_json_delta/partial_json、block stop、消息结束/错误及未知事件处理。滚动文档当日可读；没有实际Messages API调用。|
|AP11|[Claude Messages create](https://platform.claude.com/docs/en/api/messages/create)|确认API家族为/v1/messages及版本头存在。其versioning链接本次未取得可用内容，所以没有编造指定版本头的核验结果。|
|AP12|[Python3.12 JSON文档](https://docs.python.org/3.12/library/json.html)|默认重复键处理、NaN/Infinity行为、hook和错误边界；读取时网页标题是3.12.15，实际实验解释器是3.12.14，不把二者补丁版本合并。|

官网[v1.0.0渲染页](https://a2a-protocol.org/v1.0.0/specification/)在核验日仍以1.0.0作Latest Released Version标签，而GitHub发布页已有v1.0.1。这是可见版本提示差异，本章采用固定v1.0.1资料，不声称已测最新SDK或全部版本互通。

## 原创实验合同：规范事实与设计选择分开

- 规范事实：任务与消息身份分开；A2A中断与终态不同，取消不保证成功；工具参数流会有半段JSON；厂商接口的定位字段和结束事件需分别适配
- 本地设计：TaskSnapshot.revision、TaskEvent.kind、ToolEvent.sequence；相同本地身份＋内容才判重复；缺口立即失效；全量快照替换投影；completed请求后才释放工具候选；最终参数快照按字符串精确比较；增量事件不能修改已标complete的产物，非终态任务的新权威快照可重建产物视图；限制字节/事件/调用/JSON资源
- 本地实现：内存TaskMonitor、ToolAssembler、严格JSON对象子集和单一只读lookup_doc预览验证。候选参数没有真正执行，allowed_documents只是可信调用环境提供的合成集合
- 运行结果：Python3.12.14，38项unittest方法通过。两段切分循环是同一方法里的边界子样本，不额外计作独立评测任务。源码检查通过；没有安装额外依赖
- 没有运行：A2A或厂商SDK、模型请求、真实HTTP/SSE/socket、原始UTF-8解码、跨Agent互通、真实权限、工具副作用、跨进程并发、持久化或生产负载。也没有LLM分数、准确率、延迟提升或面试命中率

## 回查与复现实验

```sh
python -m unittest discover -s examples/interview_followups -p 'test_agent_protocol_lab.py' -v
```

产物验收还要读代码中的边界与测试断言。通过这些有限样本，只支持“这个教学实现的这些合同在该解释器上通过”，不能扩大为整个协议安全或端到端系统已验证。
