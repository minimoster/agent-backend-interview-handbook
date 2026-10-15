# 155. 最小栈

难度：MEDIUM · 分类：栈

## 题意与接口

设计栈，支持push、pop、top、getMin，题设要求各操作为O(1)。类名`MinStack`；pop不返回元素；题设保证读取和弹出时栈非空。下面用Python动态数组实现，push和pop的具体容器成本按均摊口径说明。

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

按CPython常见动态数组模型，push与尾部pop均摊O(1)，top/getMin为O(1)；存n个元素需O(n)空间。单次扩容或缩容可能搬移O(n)项，不保证每次调用严格常数时间。题设的数据结构目标与具体语言容器的均摊实现口径要区分，也不能从Big-O推出实时延迟保证。在CPython 3.12中，list_resize调整列表存储，尾部pop也可能触发缩容。

## 边界与易错点

- 重复最小值要能分别弹出，不能只存一个全局最小变量。
- 本接口pop返回None，不是被弹出的值。
- 空栈访问不在题设内，当前实现会抛IndexError。

## 本地测试与复习

测试重复最小值、负数、清空后重用；随机操作序列与Python列表的min和末项对拍。

复习：如果用两个独立栈，遇到与当前最小值相等的新值时应如何处理？

答案核对：辅助最小栈应在`val <= 当前最小值`时也压入重复值，并在弹出值等于其栈顶时弹出一次；或者逐层保存前缀最小值。只在严格更小时压入会让两个相等最小值中的一个弹出后，另一个仍在主栈却失去记录。

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：用连续多个相等最小值检查最小值栈，确认弹出一个最小值后另一个仍可正确返回。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
