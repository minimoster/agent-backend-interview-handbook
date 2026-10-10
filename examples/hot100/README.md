# Hot100 Python：接口与运行

[100题学习导航](../../docs/80-hot100/README.md) · [测试说明](../../docs/80-hot100/TESTING.md)

## 环境

Python 3.10+，仅标准库。每题单独一个 `p四位题号_slug.py` 模块。请从仓库根目录运行命令，使 `examples.hot100` 能被导入。不是要求直接运行源码文件得到打印输出，而是导入算法接口或执行测试。

```python
from examples.hot100.p0001_two_sum import Solution
assert Solution().twoSum([8, 1, 6, 4], 10) == [2, 3]
```

```bash
python -m unittest discover -s tests/hot100 -p 'test_*.py' -v
python examples/hot100/check_hot100.py
```

## 统一接口

- 普通题：模块内的 `Solution` 与LeetCode对应方法名，参数名见每题页。
- 设计题：使用 `LRUCache`、`Trie`、`MinStack`、`MedianFinder`，保留题目要求的方法名。
- 节点：`structures.py` 提供 `ListNode`、`TreeNode`、`Node`（随机指针节点，别名 `RandomNode`）。比较节点时使用对象身份；同值节点不等于同一节点。
- 构造帮助：`list_from` / `list_values` 用于无环链表，`tree_from` / `tree_values` 用于含 `None` 的层序树表示。`list_values`遇到环会明确报错，避免测试卡死。
- 原地题通常返回 `None`，测试检查输入对象的修改结果；需要返回新头节点的链表操作，以返回值为准。
- 题设外输入不做统一承诺。有些实现便于学习提供空输入保护，有些显式报错；这些扩展不得被误当作官方题意。

## 提交到LeetCode

复制对应模块的算法主体及标准库导入；删除 `from examples.hot100.structures import ...` 这一类本地导入，使用平台提供的节点类型。设计题复制设计类，普通题复制 `Solution`。本地测试通过不代表在平台提交过，仓库不提供虚构的提交记录。

## 关于复杂度

页面分别计算辅助空间与输出空间。Python切片和 `sorted` 会分配新容器；递归栈、显式栈、哈希表、堆都应计入辅助空间。整数算术通常按题设有限范围的单位成本模型说明；超出题设的大整数场景需另算位复杂度。
