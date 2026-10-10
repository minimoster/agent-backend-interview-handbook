# 155. 最小栈

[官方题目](https://leetcode.cn/problems/min-stack/) · MEDIUM · 官方分类：栈

## 题意与接口

设计栈，支持push、pop、top、getMin，所有操作均为O(1)。类名`MinStack`；pop不返回元素；题设保证读取和弹出时栈非空。

## 从朴素方法到优化

每次getMin扫描整个栈是O(n)。每一层入栈时顺便保存“到这一层为止的最小值”，弹出后自然恢复旧最小值。

## 核心思路

栈项存(value,prefix_min)。push时新最小值是当前值与旧最小值的min；top读第一项，getMin读第二项。

## 手推一个小例子

push(4)保存(4,4)，push(1)保存(1,1)，push(3)保存(3,1)。getMin为1；弹3后仍为1；弹1后回到4。

## 为什么正确

归纳地，每层第二个数等于该层及以下所有值的最小值。push通过与旧最小比较维持性质，pop删除整层后暴露的上一层已经包含正确历史最小值，因此查询始终正确。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0155_min_stack.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class MinStack:
    def __init__(self):
        self._items = []

    def push(self, val: int) -> None:
        # 每层保存前缀最小值，弹出后自动恢复上一层状态。
        current_min = min(val, self._items[-1][1]) if self._items else val
        self._items.append((val, current_min))

    def pop(self) -> None:
        self._items.pop()

    def top(self) -> int:
        return self._items[-1][0]

    def getMin(self) -> int:
        return self._items[-1][1]
```

## 复杂度

每次操作O(1)（Python动态数组push按摊还O(1)），存n个元素需O(n)空间。

## 边界与易错点

- 重复最小值要能分别弹出，不能只存一个全局最小变量。
- 本接口pop返回None，不是被弹出的值。
- 空栈访问不在题设内，当前实现会抛IndexError。

## 本地测试与复习

测试重复最小值、负数、清空后重用；随机操作序列与Python列表的min和末项对拍。

复习：如果用两个独立栈，遇到与当前最小值相等的新值时应如何处理？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/min-stack/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0100-0199/0155.Min%20Stack/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/0155.min-stack.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/0155.min-stack.html#python3)。可与上面的本仓库原创实现对照。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：用连续多个相等最小值检查最小值栈，确认弹出一个最小值后另一个仍可正确返回。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
