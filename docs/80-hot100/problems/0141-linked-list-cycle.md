# 141. 环形链表

难度：EASY · 分类：链表

## 题意与接口

判断单链表是否含环。接口：`hasCycle(head) -> bool`。不修改节点；题目中的 pos 只是构造说明，并非方法参数。

约束核对（2026-10-09）：长度 0..10000；pos 只供判题器构造环，不传入方法。

## 从朴素方法到优化

记录所有访问节点，遇到重复对象即可判环，但集合要 O(n) 空间。环中快慢指针的相对位置能代替整个访问历史。

## 核心思路

慢指针一步、快指针两步。每轮先移动再检查是否为同一对象。快指针遇到空指针说明已走到链尾。

## 手推一个小例子

链 `2→5→8→5...`：初始都在 2；第一轮 slow=5、fast=8；第二轮 slow=8、fast=8，确认有环。

## 为什么正确

无环时 fast 必到 None。有环时两指针进入环后，每轮相对距离增加 1，模环长的余数必在一个环长内成为 0，因此一定相遇。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0141_linked_list_cycle.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def hasCycle(self, head):
        slow = fast = head
        while fast is not None and fast.next is not None:
            # 先移动再比较，初始同在 head 不代表有环。
            slow, fast = slow.next, fast.next.next
            if slow is fast:
                return True
        return False
```

## 复杂度

时间 O(n)，辅助空间 O(1)；n 是可达不同节点数。

## 边界与易错点

先检查 fast 和 fast.next 才能访问 fast.next.next。初始两个指针相同不能直接判有环。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：如果快指针每次走三步，还能直接套用入口定位证明吗？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：画出无环链和有环链的快慢指针轨迹，解释相遇依据节点身份而不是节点值。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
