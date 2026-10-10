# 25. K 个一组翻转链表

[官方题目](https://leetcode.cn/problems/reverse-nodes-in-k-group/) · HARD · 官方分类：链表

## 题意与接口

每 k 个节点翻转一次，最后不足 k 个保持原顺序。接口：`reverseKGroup(head, k)`，只能改连接。官方页已核实 `1 <= k <= n <= 5000`。

约束核对（2026-10-09）：1<=k<=n<=5000；尾部不足 k 个不翻转，不能仅改值。 [官方来源](https://leetcode.com/problems/reverse-nodes-in-k-group/)

## 从朴素方法到优化

每组压栈容易实现，但空间 O(k)。先确认完整的一组，再用原地反转，能把辅助空间压到 O(1)。

## 核心思路

group_prev 指向待处理组前驱，先向后探 k 个节点得到 kth；不足立即结束。保存 group_next，将组内节点逐个指向 prev（初始为 group_next），反转结束后把组前驱接到 kth。原组头成为新组尾。

## 手推一个小例子

`1→4→7→2→5`，k=3：确认第一组三个节点齐全，保存后继 2，依次让 1 指 2、4 指 1、7 指 4；dummy 指 7。剩余 2、5 不足三节点，结果 `7→4→1→2→5`。

## 为什么正确

探测保证只有完整组被修改。反转时 prev 始终是当前已反转部分的头并通向原组后继；最后连接前驱，新组与其余链完整相连。每组处理完成后，已处理前缀满足要求且后缀未变。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0025_reverse_nodes_in_k_group.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
from examples.hot100.structures import ListNode

class Solution:
    def reverseKGroup(self, head, k):
        dummy = ListNode(0, head)
        group_prev = dummy
        while True:
            # 先确认完整的 k 个节点，尾部残组绝不改写。
            kth = group_prev
            for _ in range(k):
                kth = kth.next
                if kth is None:
                    return dummy.next
            group_next = kth.next
            # 初始接向组后继，反转结束后原组头自动成为组尾。
            prev, cur = group_next, group_prev.next
            while cur is not group_next:
                nxt = cur.next
                cur.next = prev
                prev, cur = cur, nxt
            old_head = group_prev.next
            group_prev.next = kth
            group_prev = old_head
```

## 复杂度

时间 O(n)：完整组先探测再反转，每个节点被常数次访问。辅助空间 O(1)。

## 边界与易错点

不足 k 个必须完全不变。k=1 仍须推进前驱。不要在反转完成后再读取旧 kth.next 作为后继。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：为何反转的 prev 初始化为 group_next 而不是 None？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/reverse-nodes-in-k-group/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0025.Reverse%20Nodes%20in%20k-Group/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：本次已核验的官方站点、sitemap、固定仓库目录与精确题号/标题检索中未找到本题直接匹配；不代表永久不存在。
- 官方Python：本次核验未找到本题精确匹配的官方实现区。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：翻转前先确认剩余节点足够 k 个；检查不足一组的尾部是否保持原顺序。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
