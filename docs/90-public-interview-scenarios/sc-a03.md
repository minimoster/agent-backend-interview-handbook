# SC-A03 混合召回 融合 重排分别做什么

[返回场景卡目录](README.md) · [公开报告与日期边界](../../sources/public-interviews/README.md)

**练习问题：** 为什么不把BM25分数和向量相似度直接相加，然后取前五？

**知识点详解**： 关键词检索擅长精确词、编号和缩写；向量检索补语义相近表达。它们的原始分数来自不同计算，尺度和分布通常不同。融合先得到候选名单，重排再用更贵的模型检查查询与候选的匹配。

## 参考答案

我先比较两条检索路径各自失败的样本。若两者确实互补，可用RRF等排名融合减少直接比较原分数的需要：某文档在每个结果列表的名次r贡献1/(k+r)，再求和。候选去重使用稳定文档/块ID。Cross-Encoder联合处理query与document，通常比独立向量打分更贵，所以只在候选集使用，是否改善必须在业务集验证。

## 追问1：RRF只看名次有什么代价？

它不使用原分数间隔，一个遥遥领先的第一名也只得到第一名的排名贡献。k与候选窗口都会影响结果，需要实验，不存在脱离任务的万能值。

## 追问2：重排模型公开榜单很好，能直接上线吗？

域、语言、文本长度和训练目标可能不同。检查长文截断、产品编号、否定句、过期证据与权限样本；分别量检索Recall@K、排序和最终任务质量，避免把某一分数当总效果。

## 常见误区

“Cross-Encoder一定更准确”“余弦总比内积好”都过度。向量归一化后内积与余弦的排序可一致，但模型使用方式与索引合同必须匹配。

## 练习与验收

对两个各含4个ID的列表手算RRF，加入重复ID及同分。附带的小练习会测试列表去重、确定性排序和非法k输入；它不代表真实检索效果已提升。

**主题来源：** P05、P06。**技术依据：** [Elastic RRF定义](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion)、[Sentence Transformers检索和重排](https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html)。使用 Elasticsearch 时需按目标版本核对 API 与许可。

## 阅读与复验入口

公开主题线索：[P05](../../sources/public-interviews/README.md#report-p05)、[P06](../../sources/public-interviews/README.md#report-p06)。

先读基础：

- [02-rag-retrieval-and-reranking](../../docs/10-agent/02-rag-retrieval-and-reranking.md)

可检查的练习材料：

- [interview_lab.py#rrf](../../examples/public_interview_scenarios/interview_lab.py#rrf)

[本模块验证范围](VALIDATION.md)。正文的手工、目标服务或模型验收是待执行标准；只有明确记录的Python测试已经运行。
