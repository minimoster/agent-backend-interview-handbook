# 检索、排序与树结构练习

[检索指标解析](../../docs/10-agent/35-retrieval-evaluation-worked-example.md) · [Top-K与RRF](../../docs/70-practice/retrieval-ranking-algorithms.md) · [构树与层序题解](../../docs/60-interviews/agent-followups-20261015.md)

- [检索指标与排序实现](retrieval_worked_examples.py)：固定K分母、唯一证据身份、稳定Top-K与RRF聚合。
- [树结构实现](interview_build_forest.py)：乱序记录构森林与二叉树之字形层序。
- [检索与排序测试](test_retrieval_worked_examples.py) · [树结构测试](test_interview_build_forest.py)

在仓库根目录执行：

```sh
python3 -B -m unittest discover -s examples/retrieval_worked_examples -p 'test_*.py' -v
```

实现使用Python 3.10+标准库；最终复跑环境为Python 3.12.14。测试覆盖22个入口，验证教学合同与边界，不代表真实检索、ASR或模型服务的效果。
