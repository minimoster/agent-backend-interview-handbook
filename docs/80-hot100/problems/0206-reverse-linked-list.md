# 206. 反转链表

难度：EASY · 分类：链表

## 题意与接口

把单链表的 next 方向全部反转，返回新头。接口：`reverseList(head)`；空链表返回 None，复用原节点。

约束核对（2026-10-09）：长度 0..5000，允许空链；返回反转后的链头。

## 从朴素方法到优化

把节点压入栈再重连需要 O(n) 辅助空间。链表反转只需要已反转前缀的头、当前节点和未处理后继三个引用。

## 核心思路

循环中先保存 next，再让当前节点指向 prev，最后推进两个指针。prev 永远是已反转部分的头，cur 永远是未处理部分的头。

## 手推一个小例子

`6→3→8`：初始 prev=None；处理 6 后得到 `6→None`；处理 3 后得到 `3→6`；处理 8 后得到 `8→3→6`，cur 变 None。

## 为什么正确

初始已反转前缀为空。每步把未处理前缀的第一个节点接到反向链表头，同时保留其余节点的入口，故不丢失节点并保持不变式。全部处理后 prev 正是整条反向链。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0206_reverse_linked_list.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def reverseList(self, head):
        prev, cur = None, head
        while cur is not None:
            nxt = cur.next  # 改写前保存未处理部分
            cur.next = prev
            prev, cur = cur, nxt
        return prev
```

## 复杂度

时间 O(n)，辅助空间 O(1)。

## 边界与易错点

先改 next 再取后继会丢失链表。空链表、单节点无需特判。原头最终必须指向 None。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：用一句话描述 prev 和 cur 的循环不变式。

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：画出 prev、current、next 三个引用，解释为什么必须先保存后继再反转当前边。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
