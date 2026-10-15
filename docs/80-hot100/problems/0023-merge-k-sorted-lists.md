# 23. 合并 K 个升序链表

难度：HARD · 分类：链表

## 题意与接口

合并 k 条已非递减排序的链表。接口：`mergeKLists(lists)`，可有空链。输出重用原节点。

约束核对（2026-10-09）：链数 0..10000，每链长度 0..500，总节点数不超过 10000；各链有序。

## 从朴素方法到优化

反复扫描 k 个头找最小节点要 O(Nk)。最小堆保存每条非空链的当前头，把每次寻找最小值降到 O(log k)。

## 核心思路

堆元素为 `(值, 链编号, 节点)`。弹出最小节点接到结果尾，再把它原来的后继加入堆。链编号用于值相同时避免 Python 比较节点对象。

## 手推一个小例子

三条链 `[1,8]、[3,6]、[2,9]`，初始堆含 1、3、2。依次弹 1 并加入 8，弹 2 加入 9，弹 3 加入 6，之后为 6、8、9。

## 为什么正确

每条剩余有序链的最小节点都在堆中，所以堆顶是全部剩余节点的最小者。弹出后补入同链后继，维持这个候选集合；归纳可知结果有序且包含所有节点。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0023_merge_k_sorted_lists.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
import heapq
from examples.hot100.structures import ListNode

class Solution:
    def mergeKLists(self, lists):
        # 每链只留一个候选；链编号处理值相等时的堆比较。
        heap = [(node.val, i, node) for i, node in enumerate(lists) if node]
        heapq.heapify(heap)
        dummy = tail = ListNode()
        while heap:
            _, index, node = heapq.heappop(heap)
            nxt = node.next
            tail.next = node
            tail = node
            if nxt:
                heapq.heappush(heap, (nxt.val, index, nxt))
        tail.next = None
        return dummy.next
```

## 复杂度

N 为总节点数，k 为输入链数量。时间 O(k+N log(k+1))，辅助空间 O(k)。heapify 为 O(k)，堆最多一个候选/非空链。

## 边界与易错点

值相同要有可比较的第二字段。输入链按本题模型彼此不共享节点。空列表返回 None。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：同一个链编号在堆中为何不会同时出现两次？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：比较逐条合并、分治和堆；说明堆项的平局处理为什么不能直接比较节点对象。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
