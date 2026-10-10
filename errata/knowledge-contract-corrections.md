# 知识合同与追问补充

日期：2026-10-10。[返回纠错目录](README.md)。这里区分事实修正、适用条件和教学补充；一条追问增加参考答案，不等于发现一条事实错误。

## Python与算法

- [可哈希条件](../docs/80-hot100/PATTERNS.md)：元组仅在全部元素可哈希时可哈希；整数计数元组与含列表的元组不同。
- [MinStack](../docs/80-hot100/problems/0155-min-stack.md)和[MedianFinder](../docs/80-hot100/problems/0295-find-median-from-data-stream.md)：动态数组扩缩容的单次成本与均摊界分开。
- [LC53](../docs/80-hot100/problems/0053-maximum-subarray.md)增加四值区间合并；[LC295](../docs/80-hot100/problems/0295-find-median-from-data-stream.md)增加全范围与99%范围条件下的精确中位数追问，明确查询前缀与完整流承诺。
- [X04](../docs/70-practice/interview-algorithm-supplements.md#x04)明确CPython十进制转换限额与大规模字符串接口；X02补节点保留不变量。
- [R01](../docs/70-practice/reasoning-twelve-puzzles.md#r01)明确组测试的成员/OR响应模型；测试证据与证明区分。

## Agent、案例与平台

- [可靠执行](../docs/10-agent/04-streaming-and-reliable-execution.md#a29)区分首次在内的总尝试次数与首次之后的额外重试。
- [任务身份](../docs/50-projects/data-engineering-agent-case.md#job-lifecycle)把租户/操作/客户端键的唯一身份与首次请求指纹分开，同身份异指纹拒绝。
- [Openresearch与Saber固定提交案例](../docs/50-projects/public-repository-case-studies.md)：跨query键是子块全文字符串；FilePlanStore错误可留下已改变的RAM或已Rename的磁盘；ExecutionEpoch存在不自动提供外部fencing。
- A01–A30与A39–A44的追问旁补参考答法及验收点；[先修清单](../docs/10-agent/14-controlled-improvement.md#prerequisite-reading-checklist)提供当前可读链接与官方入门阅读。
- [Chroma](../docs/10-agent/22-chroma-persistence-and-embedding.md)区分本地开发测试和server-backed生产建议。
- [Java定位场景](../docs/70-practice/scenario-backend-worked-answers.md#fb72)区分Linux HotSpot平台线程的OS TID/nid与虚拟线程；HashMap掩码和WaitGroup.Go的合同补在对应正文。

## 元数据与验证边界

[题目元数据](../coverage/README.md)明确Unicode码点及段落边界，脚本从实际索引条目生成分区题数。Agent补充分区实际23题；R12按明确范围计590码点。长度与分区数更新不新增题号。

[教学合同测试](../examples/agent_contracts/README.md)是内存反例，不是案例项目、数据库、文件系统断电或Spark集成测试。算法有限对拍、静态构建与语言示例分别记录。MySQL/Redis/MQ、外部模型和真实部署故障实验仍不能由这些测试推出已经通过。[本版验证记录](../coverage/VALIDATION.md)列出实际执行范围。
