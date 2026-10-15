# 160. 相交链表

难度：EASY · 分类：链表

## 题意与接口

给定两条无环单链表，返回它们共享的第一个节点对象；没有交点返回 `None`。接口：`getIntersectionNode(headA, headB)`。相交指对象相同，不是数值相同。

约束核对（2026-10-09）：两链无环且返回后保持原结构；每条长度 1..30000，相交按节点身份判断。

## 从朴素方法到优化

把 A 的节点存入集合，再扫描 B，可用 O(m+n) 时间和 O(m) 空间解决。若让两个指针都走完 A+B 的总长度，就能抵消独有前缀的长度差，不必保存节点。

## 核心思路

指针 a 到尾后从 B 的头继续，b 到尾后从 A 的头继续。每次比较对象身份；相交时最终对齐公共后缀，不相交时都停在 None。整个过程不修改 next。

## 手推一个小例子

A 为 `4→7→9`，B 为 `1→2→7→9`，其中 7、9 是共享对象。按状态 (a,b) 观察：`(4,1)→(7,2)→(9,7)→(None,9)→(1,None)→(2,4)→(7,7)`，此时返回共享的 7。

## 为什么正确

设独有前缀长度为 a、b，公共后缀长度为 c。换头后，一个指针先走完整 A 再走 B 的独有前缀，另一个先走完整 B 再走 A 的独有前缀；二者经过的节点数量均为 a+b+c，并经历相同的一次换链动作，独有长度差被抵消。若无公共节点，两条总路程相等，只能在 None 相遇。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0160_intersection_of_two_linked_lists.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def getIntersectionNode(self, headA, headB):
        a, b = headA, headB
        # 换头后都遍历两条链，抵消独有前缀的长度差。
        while a is not b:
            a = a.next if a is not None else headB
            b = b.next if b is not None else headA
        return a
```

## 复杂度

时间 O(m+n)，辅助空间 O(1)。

## 边界与易错点

不要比较 `val`；等值节点不一定相交。空链表和两个头本就相同均可处理。算法前提是链表无环。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：为什么换头可以抵消长度差？如果有环，终止性还有保证吗？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：用两条长度不同的链表推演切换头节点，区分节点身份相同与节点值相同。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
