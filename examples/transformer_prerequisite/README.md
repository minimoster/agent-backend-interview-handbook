# Transformer前向算术小实验

[讲义](../../docs/10-agent/05-transformer-prerequisite.md) · [验证范围](../../coverage/TRANSFORMER_PREREQUISITE_VALIDATION.md)

使用Python标准库，面向第一次手算注意力的读者。所有输入和权重均为原创、手设小矩阵，不下载模型或数据，不安装第三方包，不调用外部API，不训练模型，不使用GPU。

## 运行

在仓库根目录执行：

```bash
python -B examples/transformer_prerequisite/attention_lab.py
python -B -m unittest discover -s examples/transformer_prerequisite -p 'test_attention_lab.py' -v
```

也可以进入本目录运行`python -B -m unittest -v test_attention_lab`。在CPython3.12.14上实际运行39项测试通过。没有完成PyTorch数值对照、GPU测试或模型训练。

## 看懂输出

- `hand_scores/hand_weights/hand_output`：讲义中的1个query读取2个key的手算结果
- `x_shape/q_shape`：列表表示的`[L,d_model]`，省略batch
- `head_weights`：`[h,L,L]`，本例为`[2,3,3]`
- `concatenated_shape/mha_output`：分别在输出投影前后检查拼接与投影
- `pre_ln_output/post_ln_output`：相同手设权重下的两种块顺序

布尔mask以`True`表示允许；mask在softmax之前生效。全部key禁止会抛`ValueError`。这个约定不是所有框架API的统一约定。

## 文件与合同

- [attention_lab.py](attention_lab.py)：shape、矩阵乘法、线性投影、稳定softmax、单头注意力、等宽多头self-attention、ReLU FFN、逐位置LayerNorm和块顺序
- [test_attention_lab.py](test_attention_lab.py)：39项测试，含手算期望、因果前缀隔离、`Lq != Lk`、`d_k != d_v`、拼接顺序、W_O混合、FFN逐位置、总体方差、常量输入、仿射参数与非法形状

`multihead_self_attention`有意限定正整数头数整除d_model，并使用方形Q/K/V/O投影。`scaled_attention`单独允许Q/K与V特征宽度不同。`transformer_block`略去dropout，每个LayerNorm使用gamma=1、beta=0；这是两次归一化的默认数值，不是让真实模型的LN参数共享。

## 不应据此声称什么

这不是完整Transformer、预训练模型、推理引擎或生产服务。没有batch、padding数据管道、词表输出、位置编码、cross-attention、自动求导、训练循环、优化器、KV缓存、量化、GQA/MQA或硬件kernel。小型有限输入的测试通过不表示任意大数值稳定，也不证明模型语义能力或线上表现。
