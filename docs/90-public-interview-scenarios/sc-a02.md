# SC-A02 文档分块为什么不能只背一个长度

[返回场景卡目录](README.md) · [公开报告与日期边界](../../sources/public-interviews/README.md)

本卡是原创教学场景，编号独立于361道讲义题、Hot100的100题与15道外部资源题。原帖仅支持作者报告过相关主题，不是公司认证题库；参考答案依据正文所列技术一手来源。

**原创起手问：** 同一知识库有Markdown、扫描PDF和表格，统一每500字符切一块够不够？

**知识点详解**： 分块是把“可理解的知识单位”变成检索候选，不只是把字符串切短。扫描PDF先要OCR，文本PDF需要检查阅读顺序；表格要保留表头、单位和行列关系。字符、字节与token是不同计数，不能互换。

## 参考答案

我先保存文档ID、版本、来源页与权限，再做格式感知解析。Markdown优先按标题和段落切；长段落再按预算拆。表格不能把一行的数值与表头切开。小块有利于精确召回，但生成时可能缺上下文，可以召回小块并补父段落。补父块前仍要查权限、去重并控制token预算。

## 追问1：overlap大一点是不是总更好？

它可能减少断句损失，也会增加重复、索引量和上下文成本。用跨边界问题测试不同长度/重叠，观察召回、引用和最终回答，而不是根据一次演示确定参数。

## 追问2：知识库更新如何不停服？

构建一个带版本的新索引，验证解析、权限和回归样本后切换路由。查询链路记录所用索引版本，并明确旧请求是否允许读完旧版本。文档删除和权限撤销不能只等待向量缓存自然过期。

## 常见误区

“向量库里有这篇文档”不等于有效片段已经进入模型；一张表OCR成功也不等于列关系正确。

## 练习与验收

自写一段制度，把限制条件放在段落末尾，另做一张有单位的表。设计4个跨边界问题。验收检查证据是否完整、引用能否定位、不同用户能否看到不该看到的块。此处是待执行练习，没有声称做过解析或检索实验。

**主题来源：** P01、P06、P10。**技术依据：** [LangChain检索与知识库](https://docs.langchain.com/oss/python/langchain/retrieval)、[LangChain分块接口](https://docs.langchain.com/oss/python/integrations/splitters)。参数须按实际分块器和tokenizer版本记录。

## 阅读与复验入口

公开主题线索：[P01](../../sources/public-interviews/README.md#report-p01)、[P06](../../sources/public-interviews/README.md#report-p06)、[P10](../../sources/public-interviews/README.md#report-p10)。

先读基础：

- [02-rag-retrieval-and-reranking](../../docs/10-agent/02-rag-retrieval-and-reranking.md)
- [17-rag-indexes-and-evidence](../../docs/10-agent/17-rag-indexes-and-evidence.md)

[本模块验证范围](VALIDATION.md)。正文的手工、目标服务或模型验收是待执行标准；只有明确记录的Python测试已经运行。
