# 142. 环形链表 II

难度：MEDIUM · 分类：链表

## 题意与接口

返回链表环的入口节点对象；无环返回 None。接口：`detectCycle(head)`，不得把输入链表拆断。

约束核对（2026-10-09）：长度 0..10000；返回入口对象或 None，不能修改原链。

## 从朴素方法到优化

哈希集合可找第一次重复节点，空间 O(n)。Floyd 判环后，再利用相遇位置与入口距离的同余关系，空间降为常数。

## 核心思路

先用一快一慢找相遇点。随后一个指针回到 head，另一个留在相遇点，两者都每次走一步，第一次相遇就是入口。

## 手推一个小例子

`4→6→1→8→1...` 中入口为 1。快慢首次相遇在入口 1；head 到入口有两步，相遇点绕环两步也回到 1，同速阶段因此在入口会合。

## 为什么正确

设头到入口距离 a、入口到首次相遇点距离 b、环长 c。设慢指针已走 t 步，则 t 与 a+b 模 c 相同；快指针走 2t，路程差 t 为整圈，所以 a+b 也是 c 的倍数，a 与 -b 模 c 相同。头指针走 a 步到入口，环上指针也正好到入口。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0142_linked_list_cycle_ii.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def detectCycle(self, head):
        slow = fast = head
        while fast and fast.next:
            slow, fast = slow.next, fast.next.next
            if slow is fast:
                # 相遇后同速走：头到入口的距离与环上剩余距离同余。
                seeker = head
                while seeker is not slow:
                    seeker, slow = seeker.next, slow.next
                return seeker
        return None
```

## 复杂度

时间 O(n)，辅助空间 O(1)。

## 边界与易错点

返回相遇点不一定是入口。单节点自环也是环。身份比较不能换成节点值相等。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：从路程等式推导为何第二阶段两个指针都走一步。

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：用入环前长度、环长和相遇距离推导第二阶段，说明重置一个指针到头部的依据。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
