# Transformer先修验证范围

[讲义](../docs/10-agent/05-transformer-prerequisite.md) · [源码与运行](../examples/transformer_prerequisite/README.md) · [一手参考](../sources/transformer-prerequisite-references.md)

日期：2026-10-11。本批是独立原创先修补充，不新增A/FA编号，不改变361/100/15/26各项计数。

## 实际执行通过

在CPython3.12.14上运行：

```bash
python -B examples/transformer_prerequisite/attention_lab.py
python -B -m unittest discover -s examples/transformer_prerequisite -p 'test_attention_lab.py' -v
```

Demo正常产生JSON，单头手算权重约`[0.6697615493,0.3302384507]`，输出约`[6.6976154933,6.6047690135]`。多头拼接和块输出均为`[3,4]`；这些是手设矩阵的前向算术结果。

合计39项unittest通过：

- 矩阵与投影：8项，覆盖乘法、输入形状、有限值、bias和残差形状
- 单头注意力与mask：11项，覆盖手算值、均匀特例、不同Q/K长度和V宽度、key轴归一化、因果mask、未来V修改的前缀隔离、稳定softmax及错误mask
- 多头：7项，覆盖多位置逐头数值、因果前缀隔离、拼接、输出投影、不同Q/K投影、头数/投影错误及输入不变
- FFN与LayerNorm/块：13项，覆盖ReLU与非零bias、逐位置计算、总体方差、eps、gamma/beta、Pre/Post-LN非零分支调用顺序、Pre-LN零分支恒等路径、错误残差和demo确定性

测试包含多个subTest输入，但仍按39个测试方法计数，不把每个输入重复计作额外测试。

## 独立复核与非渲染整合检查

独立复核在内存中分别植入六类错误：MHA忽略mask、所有头复用首头Q/K、Pre-LN第二个归一化读取原输入、Post-LN的FFN读取原输入、残差相加改为相减、FFN忽略第一层bias。每种错误均导致至少一项测试失败；原版39项通过。此检查不修改候选源码，也不证明覆盖所有可能错误。

在独立整合副本中添加本章、源码、来源、验证和导航建议后，Node24.19.0静态构建及`--check`通过，仓库的27组非渲染检查通过。该副本保留原461个题索引以及独立100/15/26计数，没有远端发布。实际浏览器、手机及辅助技术检查仍未运行，非渲染检查不替代它们。

## 这次没有执行

- 真实语言模型、tokenizer或词表输出；真实数据或准确率评测
- 反向传播、参数学习、优化器、预训练或微调
- GPU、半精度、分布式、GQA/MQA、生产kernel或推理服务
- PyTorch数值对照、外部在线判题、远端CI、Pages部署
- 实际浏览器渲染、手机尺寸或辅助技术验收

所有测试都是标准库Python、手设权重和有限小输入。本模块不是生产模型，小型算术通过也不保证任意大数值输入、硬件或框架实现的数值行为。

## 内容与来源核查

技术核对基于原始论文及固定版本官方文档。特别保留这些条件：缩放方差推导的独立假设；Q/K同维但V可异维；等宽MHA只是本例约束；mask布尔方向因API不同；FFN与位置机制并非所有现代架构都采用原版；LayerNorm仿射参数及eps改变最终统计量；Pre-LN优势不能推广为所有训练的保证。

本地测试与线上发布分别验证；复现时先运行上述命令，再检查对应提交的部署结果。
