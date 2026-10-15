# 347. 前 K 个高频元素

难度：MEDIUM · 分类：堆

## 题意与接口

返回出现频率最高的k个不同元素。`topKFrequent(nums,k)`返回元素列表，顺序不限；题设保证最优元素集合唯一。

## 从朴素方法到优化

先计数再按频率排序需O(n+u log u)，u为不同值数量。频率只可能在1..n，可按频率放入n+1个桶，从高频向下收集。

## 核心思路

Counter得到value→frequency，把值放入buckets[frequency]。从n到1扫描桶，达到k个立即返回。这里利用了频率有界，避开比较排序。

## 手推一个小例子

[4,6,4,8,6,4]，k=2：频率4→3、6→2、8→1；桶3先取4，桶2再取6，得到[4,6]。

## 为什么正确

每个不同值恰进入与其真实频率对应的桶。按频率从大到小访问，收集到的前k个值不可能被未访问桶的低频值超过，因此构成所求集合。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0347_top_k_frequent_elements.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
from collections import Counter

class Solution:
    def topKFrequent(self, nums: list[int], k: int) -> list[int]:
        counts = Counter(nums)
        # 频率最多n；每个桶必须独立，不能用列表乘法共享。
        buckets = [[] for _ in range(len(nums) + 1)]
        for value, frequency in counts.items():
            buckets[frequency].append(value)
        answer = []
        for frequency in range(len(nums), 0, -1):
            for value in buckets[frequency]:
                answer.append(value)
                if len(answer) == k:
                    return answer
        return answer
```

## 复杂度

平均时间O(n)，辅助空间O(n+u)，输出O(k)。桶列表本身有n+1个，不能仅写O(u)空间。另一种大小k堆方案为O(n+u log k)时间/O(u+k)空间。

## 边界与易错点

- 桶下标是频率，不是原始数值，负数值无需特别处理。
- 用列表推导创建独立桶；[[]]*(n+1)会共享同一列表。
- 题设边界并列不会造成多种合法集合；额外测试并列时只验证频率性质。

## 本地测试与复习

测试单一值、k=不同值数、负数；随机核验返回不同值数量及任一已选频率不少于未选频率，避免错误绑定顺序。

复习：如果n非常大而u很小，为什么桶的空间未必划算？堆解更适合什么输入？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：先统计频次再讨论桶或堆，检查不同元素频次相等时题目允许怎样的返回顺序。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
