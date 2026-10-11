# 最后自测：把知识变成可以展示的能力

[返回总目录](../../README.md) · [题目索引](../../QUESTION_INDEX.md) · [版本与纠错](../../errata/README.md)

以下是训练建议，均不是你已经完成的履历：

1. 脱离 AI 画出一个模型—工具循环，手写带次数上限和错误分类的伪代码。
2. 给检索准备一小组人工核验的问题，记录正确证据、各阶段候选和错误归因，再逐步扩大测试集；不要用小样本宣传准确率。
3. 用人工构造的慢工具测试取消、超时、迟到结果与重试，解释最终任务状态为什么正确。
4. 断开 SSE 再连，检查重复事件、历史缺失和状态快照；没有实现回放就如实记录限制。
5. 从两个项目各选一条调用链，逐个标注“输入、输出、失败、验证方式、自己贡献”；不理解的部分列为待补，而非靠术语掩盖。
6. 做一轮无 AI 讲解：先30秒概要，再2分钟机制，最后定位到代码或测试。讲不顺时回到具体数据和状态，不增加抽象名词。

## 原创应用合同与编码练习

- [订单/审批/未知结果内存合同](../../examples/agent_scenario_contracts/README.md)
- [RAG、排序与SQL Skill合成实验](../../examples/retrieval_contracts/README.md)
- [Python/FastAPI与资源清理](../40-backend/40-python-fastapi-lab.md)
- [AI Coding参考内核](ai-coding-exercises.md)

每个入口都写明已测范围；[旧MCP stdio测试](../../examples/retrieval_contracts/test_mcp_legacy.py)不证明现代协议、HTTP认证或生产恢复已通过。
