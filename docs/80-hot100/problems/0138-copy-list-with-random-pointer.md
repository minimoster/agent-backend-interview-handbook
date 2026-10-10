# 138. 随机链表的复制

[官方题目](https://leetcode.cn/problems/copy-list-with-random-pointer/) · MEDIUM · 官方分类：链表

## 题意与接口

复制含 next 和 random 的链表；random 可指向任意原节点或 None。返回完全独立的新链表。接口：`copyRandomList(head)`。

约束核对（2026-10-09）：长度 0..1000；random 只指向原链节点或 None；副本不能引用任何原节点。 [官方来源](https://leetcode.com/problems/copy-list-with-random-pointer/)

## 从朴素方法到优化

若复制每个 random 时都从头查找对应位置，可能 O(n²)。建立原节点到新节点的映射可直接找到目标；这里选择便于证明、不会暂时改动输入的两遍哈希解法。

## 核心思路

第一遍只创建节点并保存映射；第二遍通过映射连接 next、random。映射含 `None: None`，减少空指针分支。

## 手推一个小例子

三个节点 `3→8→6` 的 random 依次指第三个、自身、空。先创建独立的 3′、8′、6′，再设置 3′.random=6′、8′.random=8′、6′.random=None，所有指针都留在副本内。

## 为什么正确

映射是一一对应的新对象集合。每一条原边 u→v 被替换为 copy[u]→copy[v]，因此值与边结构相同；所有副本对象新建，故没有原副本共享节点。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0138_copy_list_with_random_pointer.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
from examples.hot100.structures import Node

class Solution:
    def copyRandomList(self, head):
        # 先建立全部对象映射，再填边，支持 random 指向未来节点。
        clones = {None: None}
        cur = head
        while cur:
            clones[cur] = Node(cur.val)
            cur = cur.next
        cur = head
        while cur:
            clones[cur].next = clones[cur.next]
            clones[cur].random = clones[cur.random]
            cur = cur.next
        return clones[head]
```

## 复杂度

期望时间 O(n)，辅助映射 O(n)，输出节点 O(n)。可进一步用穿插节点法降辅助空间，但需要暂时修改再恢复原链。

## 边界与易错点

不能用值作映射键，因为值可重复。浅拷贝 random 会错误引用原节点。测试需检查对象身份以及自指、前指、后指。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：为什么先创建所有节点，再填边，就不怕 random 指向还没遍历到的节点？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/copy-list-with-random-pointer/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0100-0199/0138.Copy%20List%20with%20Random%20Pointer/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：本次已核验的官方站点、sitemap、固定仓库目录与精确题号/标题检索中未找到本题直接匹配；不代表永久不存在。
- 官方Python：本次核验未找到本题精确匹配的官方实现区。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：验证新节点与旧节点没有身份重合；检查 random 指向自身、前方、后方和空的情况。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
