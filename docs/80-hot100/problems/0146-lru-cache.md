# 146. LRU 缓存

[官方题目](https://leetcode.cn/problems/lru-cache/) · MEDIUM · 官方分类：链表

## 题意与接口

实现 `LRUCache(capacity)`、`get(key)`、`put(key,value)`。命中读取和写入都刷新最近使用顺序；不存在返回 -1，超容量淘汰最久未用项。官方页已核实容量为正、两操作须平均 O(1)。

约束核对（2026-10-09）：容量 1..3000，最多 200000 次调用；get/put 要求平均 O(1)，未命中返回 -1。 [官方来源](https://leetcode.com/problems/lru-cache/)

## 从朴素方法到优化

普通列表保存使用次序时，移动中间项要 O(capacity)。哈希表定位节点，双向链表常数时间摘除和接到最前，合起来满足平均常数时间。

## 核心思路

左右两个哨兵夹住真实节点，左边为最近使用，右边为最久未用。哈希表映射 key→节点。命中先摘下再放最前；新项放最前后若超容量，就摘掉右哨兵前一节点并从哈希表删除。

## 手推一个小例子

容量 2：put(4,40)、put(7,70) 后顺序是 `[7,4]`；get(4) 返回 40，顺序 `[4,7]`；put(8,80) 得 `[8,4]` 并淘汰 7；get(7) 返回 -1。

## 为什么正确

不变式：哈希表与链表的键一一对应，链表从左到右按最后访问时间递减。每个命中或写入把该键移到最前，其他相对顺序不变；超容量删除最右端正是最久未用键，因此始终满足 LRU 规则。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0146_lru_cache.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class _Entry:
    def __init__(self, key=0, value=0):
        self.key, self.value = key, value
        self.prev = self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.nodes = {}
        # 左侧最近使用，右侧最久未用；哨兵不存入哈希表。
        self.left, self.right = _Entry(), _Entry()
        self.left.next, self.right.prev = self.right, self.left

    def _remove(self, node):
        # 已知节点时，双向链可 O(1) 摘除，不必寻找前驱。
        node.prev.next = node.next
        node.next.prev = node.prev

    def _front(self, node):
        node.prev, node.next = self.left, self.left.next
        self.left.next.prev = node
        self.left.next = node

    def get(self, key: int) -> int:
        node = self.nodes.get(key)
        if node is None:
            return -1
        self._remove(node)
        self._front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        node = self.nodes.get(key)
        if node is not None:
            node.value = value
            self._remove(node)
        else:
            node = _Entry(key, value)
            self.nodes[key] = node
        self._front(node)
        # 哈希表与链表必须同步删除同一项。
        if len(self.nodes) > self.capacity:
            oldest = self.right.prev
            self._remove(oldest)
            del self.nodes[oldest.key]
```

## 复杂度

get/put 在哈希操作平均 O(1) 的模型下平均时间 O(1)。空间 O(capacity)。不承诺对抗性哈希冲突下最坏 O(1)。

## 边界与易错点

更新已有键也刷新顺序，不能新增重复节点；get 未命中不改变次序。容量 1、重复 put、值为 0 都要测。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：为什么单链表加哈希表仍不方便 O(1) 删除？哨兵怎样减少边界分支？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/lru-cache/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0100-0199/0146.LRU%20Cache/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：本次已核验的官方站点、sitemap、固定仓库目录与精确题号/标题检索中未找到本题直接匹配；不代表永久不存在。
- 官方Python：本次核验未找到本题精确匹配的官方实现区。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：手推访问后更新最近使用顺序、覆盖已有键和容量淘汰，说明两个操作如何保持平均常数时间。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
