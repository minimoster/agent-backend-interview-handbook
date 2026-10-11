# Transformer先修一手参考与证据边界

[讲义](../docs/10-agent/05-transformer-prerequisite.md) · [运行范围](../coverage/TRANSFORMER_PREREQUISITE_VALIDATION.md)

核查日期：2026-10-11。技术结论使用作者论文和框架官方文档；手设矩阵、逐步算例、反例、练习与Python实现为独立组织的原创教学内容，不转载第三方课程、论文图表或大段原文。

| 来源 | 固定版本或标识 | 本章核查用途 |
| --- | --- | --- |
| [Vaswani等 Attention Is All You Need](https://arxiv.org/html/1706.03762v7) | arXiv:1706.03762v7 | 原始encoder-decoder、scaled attention、FFN、位置编码和原始块结构；不是所有现代模型的统一规格 |
| [Ba等 Layer Normalization](https://arxiv.org/abs/1607.06450) | arXiv:1607.06450 | 归一化方法的原始出处；本实验的具体轴与方差约定另由框架文档核对 |
| [PyTorch MultiheadAttention](https://docs.pytorch.org/docs/2.9/generated/torch.nn.MultiheadAttention.html) | 2.9 | 投影、头的拼接与W_O、batch/位置/特征轴、MHA布尔mask方向 |
| [PyTorch scaled_dot_product_attention](https://docs.pytorch.org/docs/2.9/generated/torch.nn.functional.scaled_dot_product_attention.html) | 2.9 | 缩放、key轴softmax、V宽度、SDPA布尔mask与MHA方向差异 |
| [PyTorch LayerNorm](https://docs.pytorch.org/docs/2.9/generated/torch.nn.LayerNorm.html) | 2.9 | normalized_shape、尾轴、总体方差、eps及逐特征gamma/beta |
| [PyTorch TransformerEncoderLayer](https://docs.pytorch.org/docs/2.9/generated/torch.nn.TransformerEncoderLayer.html) | 2.9 | self-attention加FFN、norm_first与activation可配置；不把参考层当作所有新模型 |
| [PyTorch Linear](https://docs.pytorch.org/docs/2.9/generated/torch.nn.Linear.html) | 2.9 | 框架权重存储方向与本文`X @ W`行向量约定的区别 |
| [Xiong等 On Layer Normalization in the Transformer Architecture](https://proceedings.mlr.press/v119/xiong20b.html) | ICML 2020 PMLR 119 | Pre-LN/Post-LN位置与优化影响；保留论文的假设和实验范围，不做普遍保证 |
| [Transformers Summary of the tokenizers](https://huggingface.co/docs/transformers/v4.57.1/en/tokenizer_summary) | 4.57.1 | token不必与完整单词一一对应；本实验不实现tokenizer |

这些文档版本用于固定可复查的API说明，不声称它们是截至核查日的最新版本。PyTorch被用来核对接口和公式，没有被本实验导入或执行，也没有据此声明实现完全等价。

## 算例与运行结果分别是什么

- `[1,0]`查询、两个key、`[[10,0],[0,20]]`的value是原创手算数据，输出约`[6.697615,6.604769]`。
- `B=2,L=3,d_model=4,h=2,d_ff=6`是讲解batch轴的形状示例。代码只实现省略B的二维输入。
- `L=3,d_model=4,h=2,d_ff=6`的demo是手设权重CPU前向算术，不是训练结果、模型准确率或吞吐测量。
- 39项测试记录只覆盖明确的有限小输入合同；未做GPU训练、真实模型对照或线上验收。

## 阅读与版权边界

只保留必要引用、主题归属和链接。没有保存或镜像论文全文、原图、原始课程全文、受限文档导出、私人飞书链接或个人内部材料。链接可读不代表获得整篇转载许可，第三方各自权利仍适用。
