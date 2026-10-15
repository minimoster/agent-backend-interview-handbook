# 算法基础补充：15题与完整题解

本章按方法整理15道基础练习，每题都给出可独立阅读的题意、接口合同、推导、完整 Python 答案和边界样例。示例使用函数或类接口，直接调用即可，不需要额外的输入解析器。实现仅使用标准库；默认输入满足各题说明的类型与结构前提，不为有序数组额外排序，也不把正数窗口算法用于负数输入。

[回到Hot100](../80-hot100/README.md) · [完整可运行源码](../../examples/algorithm_supplement/solutions.py) · [独立测试](../../examples/algorithm_supplement/test_solutions.py)

## 分类导航

- 回溯：[77. 组合](#problem-77)
- 二分查找：[704. 二分查找](#problem-704)
- 双指针：[27. 移除元素](#problem-27)、[977. 有序数组的平方](#problem-977)
- 滑动窗口：[209. 长度最小的子数组](#problem-209)
- 矩阵：[59. 螺旋矩阵II](#problem-59)
- 链表：[203. 移除链表元素](#problem-203)、[707. 设计链表](#problem-707)
- 哈希：[242. 有效的字母异位词](#problem-242)、[349. 两个数组的交集](#problem-349)、[202. 快乐数](#problem-202)
- 字符串：[344. 反转字符串](#problem-344)、[151. 翻转字符串里的单词](#problem-151)
- 栈与队列：[232. 用栈实现队列](#problem-232)、[225. 用队列实现栈](#problem-225)

## 本地验证

在仓库根目录运行：

```sh
python3 examples/algorithm_supplement/test_solutions.py
```

2026-10-15 实际使用 Python 3.12.14 运行，15个独立测试入口全部通过，共检查100,264个输入或状态操作场景。一个场景可以有多个断言，场景数不等于断言数。数组、组合与字符串使用小范围穷举，正数窗口另与暴力枚举对拍；链表、栈和队列使用固定种子的随机操作序列，与简单容器模型比较，并检查长度、节点身份或内部顺序。测试范围不等同于在线判题提交结果。

各题场景数：77为56，704为5,632，27为4,372，977为3,432，209为13,418，59为14，203为1,556，707为16,018，242为14,847，349为2,100，202为2,015，344为3,381，151为1,398，232为16,013，225为16,012。

## 回溯

<a id="problem-77"></a>

### 77. 组合

补充分类：回溯 · 难度：中等

#### 题目与接口合同

给定非负整数 `n`、`k`，从整数 `1` 到 `n` 中选出 `k` 个互不相同的数，返回所有选择。一次选择只关心包含哪些数，不区分选择顺序。函数 `combine(n, k)` 将每组数按递增顺序排列，所有组按字典序返回，每组都有独立的列表对象。

本实现明确扩展边界：`k == 0` 返回 `[[]]`，表示唯一的空选择；`k > n` 返回 `[]`；`n` 或 `k` 为负时抛出 `ValueError`。

#### 解析与不变量

维护当前路径 `path` 和下一个可选下界 `start`。路径始终严格递增，下一层只能选择比刚选数字更大的值，因此不会出现重复元素，也不会把同一组合的不同排列重复收录。

若还缺 `needed` 个数，当前值最大只能取 `n - needed + 1`，否则后面凑不够剩余位置。循环的右端使用 Python 的不包含上界，所以写成 `n - needed + 2`。路径长度到达 `k` 时复制保存，随后撤销本层选择。任意合法组合的下一个数都不会被此上界剪去，因此结果既无重复也不遗漏。

#### 完整 Python 答案

```python
def combine(n: int, k: int) -> list[list[int]]:
    """Return increasing k-element selections from 1..n, in lexical order."""
    if n < 0 or k < 0:
        raise ValueError("n and k must be nonnegative")
    if k > n:
        return []
    result: list[list[int]] = []
    path: list[int] = []

    def visit(start: int) -> None:
        needed = k - len(path)
        if needed == 0:
            result.append(path.copy())
            return
        for value in range(start, n - needed + 2):
            path.append(value)
            visit(value + 1)
            path.pop()

    visit(1)
    return result
```

#### 复杂度与边界样例

- `1 <= k <= n` 时，输出包含 `C(n, k)` 组，每组复制 `k` 个数，时间为 `O(k · C(n, k))`；除返回结果外，路径与递归栈为 `O(k)`。结果本身为 `O(k · C(n, k))`。
- `k == 0` 或 `k > n` 时为 `O(1)`。
- `combine(3, 2)` → `[[1, 2], [1, 3], [2, 3]]`。
- `combine(0, 0)` → `[[]]`；`combine(2, 3)` → `[]`；`combine(3, 3)` → `[[1, 2, 3]]`。

## 二分查找

<a id="problem-704"></a>

### 704. 二分查找

补充分类：二分查找 · 难度：简单

#### 题目与接口合同

输入严格递增、没有重复值的整数数组 `nums` 和目标整数 `target`。`binary_search(nums, target)` 返回目标的零基下标；找不到时返回 `-1`，不修改数组。空数组是合法输入。有序且无重复是调用前提，函数不额外扫描验证它。

#### 解析与不变量

使用半开区间 `[left, right)`，初始化为整个数组。若目标存在且还未返回，它一定在当前候选区间内。

中点小于目标时，递增性说明中点及其左侧都不可能命中，令 `left = middle + 1`；中点大于目标时，目标只能位于中点左侧，令 `right = middle`。命中直接返回。两种未命中更新都会严格缩短区间；当 `left == right`，候选区间为空，故返回 `-1`。不要把闭区间模板中的 `middle - 1` 混进这里。

#### 完整 Python 答案

```python
def binary_search(nums: list[int], target: int) -> int:
    """Search a strictly increasing array; return -1 if target is absent."""
    left, right = 0, len(nums)
    while left < right:
        middle = (left + right) // 2
        if nums[middle] < target:
            left = middle + 1
        elif nums[middle] > target:
            right = middle
        else:
            return middle
    return -1
```

#### 复杂度与边界样例

时间 `O(log n)`，额外空间 `O(1)`；空输入耗时 `O(1)`。

- `binary_search([-5, 0, 7, 12], 7)` → `2`。
- 同一数组查 `-5` → `0`，查 `12` → `3`，查 `6` → `-1`。
- `binary_search([], 4)` → `-1`；`binary_search([4], 4)` → `0`；`binary_search([4], 3)` → `-1`。

## 双指针

<a id="problem-27"></a>

### 27. 移除元素

补充分类：双指针 · 难度：简单

#### 题目与接口合同

输入可变整数数组 `nums` 和待删除值 `val`。`remove_element(nums, val)` 把所有不等于 `val` 的值写到原数组的前缀，并返回有效长度 `k`。读取答案时只看 `nums[:k]`，后面的内容没有意义；列表本身不缩短。

本实现额外保持保留元素的相对顺序。不创建另一个线性大小的数组，不返回新列表，空输入返回 `0`。

#### 解析与不变量

读指针 `read` 逐个查看原元素，写指针 `write` 等于已经保留的元素个数。每轮开始时，`nums[:write]` 恰好是已经读取部分中不等于 `val` 的元素，顺序保持不变。

遇到保留值就写入 `nums[write]`，随后推进写指针；遇到删除值则只推进读指针。始终有 `write <= read`，所以写入不会破坏尚未读取的元素。读完整个数组后，不变量直接给出答案前缀和长度。

#### 完整 Python 答案

```python
def remove_element(nums: list[int], val: int) -> int:
    """Write retained values into nums' prefix, stably; return its length."""
    write = 0
    for read in range(len(nums)):
        if nums[read] != val:
            nums[write] = nums[read]
            write += 1
    return write
```

#### 复杂度与边界样例

时间 `O(n)`，额外空间 `O(1)`。

- `nums = [3, 2, 3, 4]`、`val = 3`：返回 `2`，有效前缀是 `[2, 4]`，不要求尾部是什么。
- `nums = []`：返回 `0`；`nums = [7, 7]`、`val = 7`：返回 `0`。
- `nums = [1, 2]`、`val = 9`：返回 `2`，有效前缀仍为 `[1, 2]`。

<a id="problem-977"></a>

### 977. 有序数组的平方

补充分类：双指针 · 难度：简单

#### 题目与接口合同

输入非递减整数数组 `nums`，允许负数、零和重复值。`sorted_squares(nums)` 返回由每个元素平方组成的新数组，结果也要非递减，且不修改输入。空数组返回新空列表。有序是调用前提，不在函数内排序或验证。

#### 解析与不变量

负数平方后顺序会反转，因此不能按原顺序直接输出。但是，在剩余有序区间内，绝对值最大的一定是左端或右端，平方最大值也只可能来自这两个位置。

左右指针表示还没处理的区间，写指针从答案最后一格向前移动。每次把两端较大的平方放到当前写入位置，只移动被选中的端点。已填好的答案后缀始终有序，且它的每个值都不小于尚未放入的值；区间耗尽时整个结果有序。空数组的写入循环执行零次，不会访问越界位置。

#### 完整 Python 答案

```python
def sorted_squares(nums: list[int]) -> list[int]:
    """Return nondecreasing squares of a nondecreasing integer array."""
    result = [0] * len(nums)
    left, right = 0, len(nums) - 1
    for write in range(len(nums) - 1, -1, -1):
        if abs(nums[left]) > abs(nums[right]):
            result[write] = nums[left] * nums[left]
            left += 1
        else:
            result[write] = nums[right] * nums[right]
            right -= 1
    return result
```

#### 复杂度与边界样例

时间 `O(n)`；返回数组占 `O(n)`，除返回数组外额外空间 `O(1)`。

- `sorted_squares([-5, -2, 0, 3])` → `[0, 4, 9, 25]`。
- 全负数 `[-4, -3, -1]` → `[1, 9, 16]`。
- 相同绝对值 `[-2, -2, 2]` → `[4, 4, 4]`；`[]` → `[]`；`[0]` → `[0]`。

## 滑动窗口

<a id="problem-209"></a>

### 209. 长度最小的子数组

补充分类：滑动窗口 · 难度：中等

#### 题目与接口合同

给定正整数 `target` 和只含正整数的数组 `nums`，寻找元素和至少为 `target` 的非空连续子数组，返回其中最小长度。不存在时返回 `0`。`min_sub_array_len(target, nums)` 不修改输入，空数组返回 `0`；`target <= 0` 抛出 `ValueError`。

“所有数组元素为正”是调用前提，函数不逐项验证。不允许把此实现直接用于含负数的数组，因为那时窗口和不再具有这里依赖的单调性。

#### 解析与不变量

维护窗口 `[left, right]` 及其准确的元素和 `total`。右端每前进一步，加入新值；只要窗口已经达标，就记录当前长度，再删掉最左值、向右收缩，直到不达标为止。

正数保证收缩时和严格减小，所以这一轮会依次检查以当前右端结尾的所有可行左端，并得到其中最短者。一个左端一旦作为达标窗口被检查并丢弃，将来右端更远时长度只会更长，不可能改善已经记录的答案，因此无需回退左指针。左右指针都最多前进 `n` 次，嵌套循环并非二次复杂度。

#### 完整 Python 答案

```python
def min_sub_array_len(target: int, nums: list[int]) -> int:
    """For positive nums and target, return shortest sum>=target length, or 0."""
    if target <= 0:
        raise ValueError("target must be positive")
    left = 0
    total = 0
    best = len(nums) + 1
    for right, value in enumerate(nums):
        total += value
        while total >= target:
            best = min(best, right - left + 1)
            total -= nums[left]
            left += 1
    return 0 if best == len(nums) + 1 else best
```

#### 复杂度与边界样例

时间 `O(n)`，额外空间 `O(1)`。

- `min_sub_array_len(7, [2, 3, 1, 2, 4, 3])` → `2`，对应 `[4, 3]`。
- `min_sub_array_len(4, [1, 4, 2])` → `1`；`min_sub_array_len(8, [1, 2, 3])` → `0`。
- `min_sub_array_len(3, [])` → `0`；`min_sub_array_len(3, [3])` → `1`。
- 不能忽略正数前提：`target = 3`、`nums = [1, -1, 3]` 的正确答案为 `1`，本窗口模板却会漏掉它。

## 矩阵

<a id="problem-59"></a>

### 59. 螺旋矩阵II

补充分类：矩阵 · 难度：中等

#### 题目与接口合同

给定非负整数 `n`，`generate_matrix(n)` 创建 `n × n` 矩阵，把 `1` 到 `n²` 从左上角开始按顺时针螺旋写入：先向右，再向下、向左、向上，逐层向内。各行必须是独立列表。本实现中 `n == 0` 返回 `[]`，`n < 0` 抛出 `ValueError`。

#### 解析与不变量

用 `top`、`bottom`、`left`、`right` 描述尚未填入的矩形。每轮开始时，此矩形之外的位置都已按螺旋顺序填好，`value` 是下一次要写的数字。

依次填上边后令 `top` 下移一行，填右边后令 `right` 左移一列，再在边界仍合法时填下边与左边。每填完一条边立即收缩对应边界，角点便不会被相邻边重复使用。下边与左边的额外判断用于处理只剩一行、一列或中心一格的情况。未填矩形最终为空，所有位置恰好被填一次。

#### 完整 Python 答案

```python
def generate_matrix(n: int) -> list[list[int]]:
    """Fill an n-by-n matrix clockwise from its upper-left corner with 1..n²."""
    if n < 0:
        raise ValueError("n must be nonnegative")
    matrix = [[0] * n for _ in range(n)]
    top, bottom, left, right = 0, n - 1, 0, n - 1
    value = 1
    while top <= bottom and left <= right:
        for column in range(left, right + 1):
            matrix[top][column] = value
            value += 1
        top += 1
        for row in range(top, bottom + 1):
            matrix[row][right] = value
            value += 1
        right -= 1
        if top <= bottom:
            for column in range(right, left - 1, -1):
                matrix[bottom][column] = value
                value += 1
            bottom -= 1
        if left <= right:
            for row in range(bottom, top - 1, -1):
                matrix[row][left] = value
                value += 1
            left += 1
    return matrix
```

#### 复杂度与边界样例

时间 `O(n²)`；结果占 `O(n²)`，除结果外额外空间 `O(1)`。

- `generate_matrix(3)` → `[[1, 2, 3], [8, 9, 4], [7, 6, 5]]`，中心只写一次。
- `generate_matrix(2)` → `[[1, 2], [4, 3]]`。
- `generate_matrix(1)` → `[[1]]`；`generate_matrix(0)` → `[]`。

## 链表

<a id="problem-203"></a>

### 203. 移除链表元素

补充分类：链表 · 难度：简单

#### 题目与接口合同

给定无环单链表的头节点 `head` 和整数 `val`，删除链上值等于 `val` 的所有节点，返回新的头节点。节点提供 `val` 和 `next` 两个字段，`None` 表示空链表。

`remove_elements(head, val)` 会改写链的连接，保留节点必须复用原对象且顺序不变，不复制一条新链。若头部被删除，调用方须接住返回的新头；不保证已经删除的节点被清空或销毁。输入无环是前提。

#### 解析与不变量

在真实头之前添加不属于答案的哨兵 `dummy`，统一删除头节点与删除中间节点的处理。`previous` 始终是接下来待检查节点的前驱；它之前的有效链段已经检查完，且没有目标值。

若 `previous.next` 需要删除，就让前驱跨过该节点，前驱本身不动，因为新接过来的下一个节点也可能要删除。只有保留当前节点时，前驱才向前走一步。这样连续待删值、头部和尾部都使用同一逻辑，最后返回 `dummy.next`。

#### 完整 Python 答案

下面包含本题所需的节点定义，可直接独立运行。

```python
class ListNode:
    """A mutable node shared by exercises 203 and 707."""

    def __init__(self, val: int = 0, next: "ListNode | None" = None) -> None:
        self.val = val
        self.next = next


def remove_elements(head: ListNode | None, val: int) -> ListNode | None:
    """Unlink all matching nodes from an acyclic list; reuse retained nodes."""
    dummy = ListNode(next=head)
    previous = dummy
    while previous.next is not None:
        if previous.next.val == val:
            previous.next = previous.next.next
        else:
            previous = previous.next
    return dummy.next
```

#### 复杂度与边界样例

节点数为 `n` 时，时间 `O(n)`，除一个哨兵和引用变量外额外空间 `O(1)`。

- `1 → 6 → 6 → 2 → 6` 删除 `6`，返回 `1 → 2`，这两个节点仍是原节点。
- `6 → 6` 删除 `6`，返回 `None`；`None` 删除任意值仍为 `None`。
- `1 → 2` 删除 `9`，返回的头仍是原头，链接不变。

<a id="problem-707"></a>

### 707. 设计链表

补充分类：链表 · 难度：中等

#### 题目与接口合同

实现 `MyLinkedList`，内部存整数，使用零基下标。允许重复值和负数值，初始为空：

- `get(index)`：合法下标 `0 <= index < size` 时返回该节点值，否则返回 `-1`。
- `addAtHead(val)`、`addAtTail(val)`：分别在头部、尾部加入一个节点。
- `addAtIndex(index, val)`：在原下标 `index` 节点之前插入；`index == size` 表示尾插；`index > size` 不做修改；负下标按 `0` 处理。
- `deleteAtIndex(index)`：仅当 `0 <= index < size` 时删除，其他下标不做修改，不能让负数采用 Python 列表的倒数语义。
- 所有修改操作返回 `None`。由于允许值为 `-1`，一次查询返回 `-1` 本身不能区分“合法值为-1”和“非法下标”。

#### 解析与不变量

用哨兵保存链头，用 `_size` 保存真实节点数。所有修改都先定位目标位置的前驱，再修改一处链接。内部 `_predecessor(index)` 只在已经检查过的 `0 <= index <= size` 范围调用；它走 `index` 步，返回插入位置的前驱。

始终保持两个条件：从哨兵之后可达的节点恰有 `_size` 个，且它们的顺序就是逻辑列表顺序。插入时将新节点接在前驱与后继之间并加一；删除时跨过一个节点并减一；非法操作两者都不变。本实现没有额外尾指针，因此尾插也要从头走到尾，避免把它误写成 `O(1)`。

#### 完整 Python 答案

这里再次给出节点定义，使本题答案不依赖上一题的代码块；同一模块使用时节点类只定义一次。

```python
class ListNode:
    """A mutable node shared by exercises 203 and 707."""

    def __init__(self, val: int = 0, next: "ListNode | None" = None) -> None:
        self.val = val
        self.next = next


class MyLinkedList:
    """Zero-based singly linked list; invalid reads return -1."""

    def __init__(self) -> None:
        self._dummy = ListNode()
        self._size = 0

    def _predecessor(self, index: int) -> ListNode:
        previous = self._dummy
        for _ in range(index):
            previous = previous.next
        return previous

    def get(self, index: int) -> int:
        if index < 0 or index >= self._size:
            return -1
        return self._predecessor(index).next.val

    def addAtHead(self, val: int) -> None:
        self.addAtIndex(0, val)

    def addAtTail(self, val: int) -> None:
        self.addAtIndex(self._size, val)

    def addAtIndex(self, index: int, val: int) -> None:
        index = max(0, index)
        if index > self._size:
            return
        previous = self._predecessor(index)
        previous.next = ListNode(val, previous.next)
        self._size += 1

    def deleteAtIndex(self, index: int) -> None:
        if index < 0 or index >= self._size:
            return
        previous = self._predecessor(index)
        previous.next = previous.next.next
        self._size -= 1
```

#### 复杂度与边界样例

头插 `O(1)`；合法的查询、按下标插入、删除最坏为 `O(n)`，尾插 `O(n)`。检查后直接拒绝的非法操作为 `O(1)`。保存 `n` 个节点占 `O(n)`，每次操作额外空间 `O(1)`。

- 新建后 `get(0)` → `-1`；依次头插 `1`、尾插 `3`、`addAtIndex(1, 2)`，链为 `[1, 2, 3]`，`get(1)` → `2`。
- 接着 `deleteAtIndex(1)` 得 `[1, 3]`，`get(1)` → `3`。
- 空链 `addAtIndex(-2, 9)` 得 `[9]`；对 `[9]` 调 `addAtIndex(2, 7)` 或 `deleteAtIndex(-1)` 均不改变状态。
- 只有一个节点时删除下标 `0`，应恢复空链且长度归零；随后再次尾插仍应正常。

## 哈希

<a id="problem-242"></a>

### 242. 有效的字母异位词

补充分类：哈希 · 难度：简单

#### 题目与接口合同

给定字符串 `s`、`t`，如果两者由完全相同的字符及频次组成，仅顺序可以不同，则返回 `True`，否则返回 `False`。`is_anagram(s, t)` 不修改输入。

这里用字典支持任意 Python 字符，不局限于26个英文字母；大小写敏感，按字符串中的 Unicode 码点精确比较，不做大小写折叠或 Unicode 归一化。两个空字符串互为异位词。

#### 解析与不变量

长度不同可立即否定。先为 `s` 建立频次表，再依次消费 `t` 的字符。处理完 `t` 的一个前缀后，表中计数等于 `s` 的原频次减去该前缀消耗的频次。

如果某个字符没有剩余次数，说明 `t` 需要的比 `s` 提供的多，立即返回 `False`。如果长度相同并且所有字符都成功消费，总共减掉的次数等于初始总频次，所有余量必然为零，因此无需再扫描字典。

#### 完整 Python 答案

```python
def is_anagram(s: str, t: str) -> bool:
    """Compare exact character frequencies, without case/Unicode normalization."""
    if len(s) != len(t):
        return False
    counts: dict[str, int] = {}
    for character in s:
        counts[character] = counts.get(character, 0) + 1
    for character in t:
        if counts.get(character, 0) == 0:
            return False
        counts[character] -= 1
    return True
```

#### 复杂度与边界样例

令字符串长度分别为 `m`、`n`，`u` 为 `s` 的不同字符数。哈希平均时间 `O(m + n)`，额外空间 `O(u)`；长度不同时直接 `O(1)` 返回。

- `is_anagram("aabc", "caba")` → `True`；`is_anagram("aab", "abb")` → `False`。
- `is_anagram("", "")` → `True`；`is_anagram("A", "a")` → `False`。
- `is_anagram("你🙂你", "🙂你你")` → `True`；`"é"` 与 `"e\u0301"` 的码点构成不同，返回 `False`。

<a id="problem-349"></a>

### 349. 两个数组的交集

补充分类：哈希 · 难度：简单

#### 题目与接口合同

输入两个整数数组，`intersection(nums1, nums2)` 返回同时出现在两者中的值，每个值最多一次，不修改任意输入。这里求的是集合意义上的交集，不保留重复次数。

为了让示例和测试稳定，本实现将结果按该值在 `nums2` 中首次出现的顺序排列；这比“任意顺序”更明确，但不承诺升序。任一数组为空时返回 `[]`。

#### 解析与不变量

把第一个数组放进集合 `remaining`。顺序扫描第二个数组，若当前值仍在集合，就将它加入答案，并从集合删除。

`remaining` 始终恰好包含第一个数组中尚未输出的不同值；因此只有同时存在于两边的值会输出，而且每个值输出后不可能再次命中。扫描顺序则保证输出顺序满足合同。与求多重集合交集不同，这里不需要维护每个值出现多少次。

#### 完整 Python 答案

```python
def intersection(nums1: list[int], nums2: list[int]) -> list[int]:
    """Return distinct common values in order of first occurrence in nums2."""
    remaining = set(nums1)
    result: list[int] = []
    for value in nums2:
        if value in remaining:
            result.append(value)
            remaining.remove(value)
    return result
```

#### 复杂度与边界样例

令两个数组长度为 `m`、`n`，第一个数组有 `u` 个不同值，结果有 `r` 个值。哈希平均时间 `O(m + n)`，辅助集合占 `O(u)`，返回结果另占 `O(r)`。

- `intersection([1, 2, 2, 4], [2, 2, 1, 3])` → `[2, 1]`，不是 `[2, 2, 1]`。
- `intersection([5], [5, 5])` → `[5]`；`intersection([1], [2])` → `[]`。
- `intersection([], [1, 1])` → `[]`；两个空数组也返回 `[]`。

<a id="problem-202"></a>

### 202. 快乐数

补充分类：哈希 · 难度：简单

#### 题目与接口合同

对一个正整数反复进行以下变换：取它的十进制各位数字，计算每位数字平方的总和，把这个和作为下一个整数。若最终到达 `1`，称它为快乐数。`is_happy(n)` 返回判定布尔值；本实现对 `n <= 0` 返回 `False`，而不是继续迭代。

#### 解析与不变量

用集合记录已经作为当前状态处理过的整数。没有到 `1`、也没有重复时，将当前状态记入集合，用反复 `divmod(n, 10)` 拆出末位并累加平方，得到下一状态。

同一个整数的下一状态是唯一的，因此状态一旦重复，后面的路径会完全重复，不可能突然走到之前没到过的 `1`。还需要说明检测一定会结束：一个 `d` 位数变换后不超过 `81d`；当 `d >= 4` 时这个上界小于最小的 `d` 位数，所以大数会缩小到不足四位。三位以内下一步不超过243，之后一直在有限范围内运动，最终必到 `1` 或重复。

#### 完整 Python 答案

```python
def is_happy(n: int) -> bool:
    """Return whether positive n reaches 1 under decimal digit-square sums."""
    if n <= 0:
        return False
    seen: set[int] = set()
    while n != 1 and n not in seen:
        seen.add(n)
        total = 0
        while n:
            n, digit = divmod(n, 10)
            total += digit * digit
        n = total
    return n == 1
```

#### 复杂度与边界样例

令 `t` 为停止前执行的状态变换次数，`d` 为过程中最大的十进制位数。按通常逐位处理模型，时间上界 `O(t · d)`，集合保存 `O(t)` 个状态。这里不把每一次数字变换不加说明地当作 `O(1)`；对任意大整数，底层大整数运算还会有其自身成本。

- `is_happy(19)` → `True`：`19 → 82 → 68 → 100 → 1`。
- `is_happy(2)` → `False`：`2 → 4 → 16 → 37 → 58 → 89 → 145 → 42 → 20 → 4`，重复的是 `4`。
- `is_happy(1)` → `True`；`is_happy(0)` 与 `is_happy(-7)` → `False`。

## 字符串

<a id="problem-344"></a>

### 344. 反转字符串

补充分类：字符串 · 难度：简单

#### 题目与接口合同

输入可变字符数组 `characters`，每个元素是一个单字符字符串。`reverse_string(characters)` 在原列表上反转元素顺序，返回 `None`，不能用新列表替换原对象。空列表和单元素列表都是合法输入。

这里反转的是字符数组的元素，不是返回一个新的 Python 字符串，也不额外解析多个码点组合成的视觉字符。

#### 解析与不变量

左右指针分别从两端向内移动，交换对应位置。每轮开始时，左指针之前和右指针之后的元素已经位于最终位置，中间区间尚未处理。交换使两端各有一个元素归位，随后缩短中间区间。

当 `left >= right` 时，区间已空或只剩无需交换的中心元素。无需切片复制，也不要把停止条件写成 `left != right`，因为偶数长度时两指针会直接交错。

#### 完整 Python 答案

```python
def reverse_string(characters: list[str]) -> None:
    """Reverse a mutable character array in place and return None."""
    left, right = 0, len(characters) - 1
    while left < right:
        characters[left], characters[right] = characters[right], characters[left]
        left += 1
        right -= 1
```

#### 复杂度与边界样例

时间 `O(n)`，额外空间 `O(1)`。

- `characters = ["h", "e", "l", "l", "o"]` 调用后为 `["o", "l", "l", "e", "h"]`，返回值是 `None`。
- `[]` 和 `["a"]` 调用后不变；`["a", "b"]` 调用后为 `["b", "a"]`。
- 连续调用两次恢复原顺序，而且始终是同一个列表对象。

<a id="problem-151"></a>

### 151. 翻转字符串里的单词

补充分类：字符串 · 难度：中等

#### 题目与接口合同

给定字符串 `s`，把单词顺序反转，单词内部字符顺序保持不变，结果只用一个普通空格连接，去掉首尾空白与多余分隔符。`reverse_words(s)` 返回新字符串。

本实现把 Python `str.split()` 识别的所有空白字符都视为分隔符，包括普通空格、制表符、换行和全角空格；单词是连续的非空白片段，标点属于单词本身。空串或全空白输入返回空串，不承诺原地修改不可变字符串。

#### 解析与不变量

无参数 `split()` 会跳过连续空白并仅生成非空单词，因此切分结果已经完成空白规范化。随后反向遍历单词列表，并用一个普通空格连接。

切分后每个单词都与输入中的对应片段完全相同；反向遍历只改变这些片段之间的顺序，不改变片段内部字符；连接时每对相邻词之间恰好一个空格，因此三项要求分别得到保证。这里选择清楚的线性空间答案，而不是把 Python 分词误称为常数空间。

#### 完整 Python 答案

```python
def reverse_words(s: str) -> str:
    """Reverse whitespace-separated words; join with one ASCII space."""
    return " ".join(reversed(s.split()))
```

#### 复杂度与边界样例

令输入长度为 `n`，时间 `O(n)`，单词列表与返回字符串合计需要 `O(n)` 空间；不含返回字符串时，分词仍需要 `O(n)` 辅助空间。

- `reverse_words("  the sky  is blue ")` → `"blue is sky the"`。
- `reverse_words("你\t好\n世界")` → `"世界 好 你"`，这里的 `\t`、`\n` 表示真实制表符与换行。
- `reverse_words("")` → `""`；`reverse_words("   ")` → `""`；`reverse_words("single")` → `"single"`。

## 栈与队列

<a id="problem-232"></a>

### 232. 用栈实现队列

补充分类：栈与队列 · 难度：简单

#### 题目与接口合同

实现先进先出队列 `MyQueue`，提供 `push(x)` 入队、`pop()` 移除并返回队首、`peek()` 返回但不移除队首、`empty()` 返回是否为空。`push` 返回 `None`。

内部只使用两个栈的栈顶入栈、出栈、读栈顶与判空操作。输入可重复且可以为负数。初始为空；本实现明确规定空队列 `pop()` 或 `peek()` 抛出 `IndexError`，发生异常后队列仍为空，不返回与合法数据冲突的哨兵值。

#### 解析与不变量

`_in` 接收新元素，`_out` 提供最早入队的元素。队列逻辑顺序始终等于“从 `_out` 栈顶到栈底，再从 `_in` 栈底到栈顶”。

当 `_out` 非空时，它的栈顶就是队首，不能再次搬移 `_in`，否则较新的元素会越过较旧的元素。只有 `_out` 为空时才把 `_in` 全部逐个弹出并压入 `_out`；一次逆序将最早入队者放到栈顶。`peek` 只查看这个栈顶，`pop` 再将其移除。`peek` 可能调整内部存放位置，但不改变逻辑队列。

#### 完整 Python 答案

```python
class MyQueue:
    """FIFO queue using two stacks. Empty pop/peek raise IndexError."""

    def __init__(self) -> None:
        self._in: list[int] = []
        self._out: list[int] = []

    def push(self, x: int) -> None:
        self._in.append(x)

    def _prepare(self) -> None:
        if not self._out:
            while self._in:
                self._out.append(self._in.pop())

    def pop(self) -> int:
        self._prepare()
        if not self._out:
            raise IndexError("pop from empty queue")
        return self._out.pop()

    def peek(self) -> int:
        self._prepare()
        if not self._out:
            raise IndexError("peek from empty queue")
        return self._out[-1]

    def empty(self) -> bool:
        return not self._in and not self._out
```

#### 复杂度与边界样例

`push` 和 `empty` 为 `O(1)`；一次 `pop` 或 `peek` 最坏可能搬移 `n` 个元素，为 `O(n)`。但每个元素最多进入 `_in` 一次、从 `_in` 转入 `_out` 一次、离开 `_out` 一次，因此一串操作的摊还单次时间为 `O(1)`。保存 `n` 个元素占 `O(n)` 空间。

- 新建后 `empty()` → `True`，`pop()`、`peek()` 都抛出 `IndexError`。
- 依次 `push(1)`、`push(2)`，`peek()` → `1`，`pop()` → `1`。
- 接着 `push(3)`，`peek()` 仍为 `2`，随后两次 `pop()` 依次得到 `2`、`3`，再 `empty()` → `True`。
- 连续多次 `peek()` 不会丢元素；清空后再次 `push`，新元素仍可正常取出。

<a id="problem-225"></a>

### 225. 用队列实现栈

补充分类：栈与队列 · 难度：简单

#### 题目与接口合同

实现后进先出栈 `MyStack`，提供 `push(x)` 入栈、`pop()` 移除并返回栈顶、`top()` 查看栈顶、`empty()` 判空。`push` 返回 `None`，输入整数可重复且可为负数。

内部仅使用一个先进先出队列，允许队尾入队、队首出队、查看队首、取长度和判空。代码用标准库 `deque` 实现这些操作，不用其队尾出队能力模拟栈。空栈 `pop()` 或 `top()` 抛出 `IndexError`，异常不改变空状态。

#### 解析与不变量

始终使队首是栈顶，整个队列从首到尾等于栈从顶到底的顺序。入栈时先把新元素放到队尾，然后把之前的所有旧元素依次从队首取出、放到队尾。

如果原来有 `m` 个元素，恰好转动 `m` 次后，新元素位于队首，旧元素之间的先后顺序保持不变，不变量恢复。于是出栈只需队首出队，查看栈顶只需读队首。必须只转动旧元素的数量，不能把新元素也转到尾部。

#### 完整 Python 答案

```python
from collections import deque


class MyStack:
    """LIFO stack using a FIFO queue. Empty pop/top raise IndexError."""

    def __init__(self) -> None:
        self._queue: deque[int] = deque()

    def push(self, x: int) -> None:
        self._queue.append(x)
        for _ in range(len(self._queue) - 1):
            self._queue.append(self._queue.popleft())

    def pop(self) -> int:
        if not self._queue:
            raise IndexError("pop from empty stack")
        return self._queue.popleft()

    def top(self) -> int:
        if not self._queue:
            raise IndexError("top from empty stack")
        return self._queue[0]

    def empty(self) -> bool:
        return not self._queue
```

#### 复杂度与边界样例

当栈内原有 `n` 个元素时，`push` 时间 `O(n)`；`pop`、`top`、`empty` 时间 `O(1)`。保存 `n` 个元素占 `O(n)` 空间，每次操作额外空间 `O(1)`。

- 新建后 `empty()` → `True`，`pop()`、`top()` 都抛出 `IndexError`。
- 依次 `push(1)`、`push(2)`，`top()` → `2`，`pop()` → `2`。
- 接着 `push(3)`，随后两次 `pop()` 依次得到 `3`、`1`，`empty()` → `True`。
- 仅一个元素时 `top()` 可以重复调用；弹出后再入栈仍应正常，不能残留旧队列顺序。
