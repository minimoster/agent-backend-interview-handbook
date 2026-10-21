# 所有最长回文：位置、去重与结果空间

<a id="all-longest-palindromes"></a>

## 题目：返回一个最长回文，怎样改成返回所有最长回文？

先会做[最长回文子串](../80-hot100/problems/0005-longest-palindromic-substring.md)，再改输出合同。“所有”需要先说清两个问题：按出现位置保留，还是相同内容只留一个？结果按什么顺序返回？不能未经确认就用集合丢掉位置信息。

这里提供两个明确接口。`longest_palindrome_spans(s)`返回所有最长出现位置，使用左闭右开区间`(start, end)`，按起点递增；`all_longest_palindromes(s)`返回按内容去重的字符串，保留首次出现顺序。空串返回空列表。比较区分大小写，按Python字符串中的码点进行，不自动做Unicode规范化或按用户感知的字形分组。

**口述版：**“我先确认按位置还是按内容去重。算法仍枚举奇偶两类中心；发现更长的回文就清空旧候选，长度并列就追加。扩展时只存区间，最后才切片。如果要去重，另用集合判断内容是否出现过，同时用列表保留首次出现顺序；字符串复制和存储成本也要计入。”

## 用两个例子理解输出的区别

`babad`的最长长度是3，区间为`(0, 3)`与`(1, 4)`，对应`bab`和`aba`。只保存一个`best_start`会遗漏另一个答案。

`abaxyaba`的最长长度同样是3，区间为`(0, 3)`与`(5, 8)`，两处内容都是`aba`。位置接口返回两个区间，内容接口只返回`["aba"]`。这是接口语义的差别，不能靠“子串一般怎么理解”代替题设。

## 原理与正确性

每个回文都有唯一的奇数或偶数中心。固定中心向外扩展，停止后有效区间是`[left + 1, right)`，长度为`right - left - 1`。只需看该中心能扩出的最长回文：如果某个全局最长回文还能沿同一中心扩长，它就不是全局最长，产生矛盾。

遍历中的不变量是：`best_length`为已处理中心的最大长度，`spans`恰好保存达到该长度的区间。更长时替换列表，并列时追加，更短时忽略。所有中心处理完就覆盖所有全局最优出现位置。

同一最终长度的回文奇偶性相同，因此它们只来自同一类中心；中心从左到右移动时，起点也从左到右移动。保留下来的区间天然按起点排序，不必再排序。每个区间也不会被两个不同中心重复生成。

## Python答案

[可导入实现](../../examples/interview_algorithms/all_longest_palindromes.py)包含以下两个函数。

```python
def longest_palindrome_spans(s: str) -> list[tuple[int, int]]:
    best_length = 0
    spans = []
    for center in range(len(s)):
        for left, right in ((center, center), (center, center + 1)):
            while left >= 0 and right < len(s) and s[left] == s[right]:
                left -= 1
                right += 1
            length = right - left - 1
            if length > best_length:
                best_length = length
                spans = [(left + 1, right)]
            elif length == best_length and length > 0:
                spans.append((left + 1, right))
    return spans


def all_longest_palindromes(s: str) -> list[str]:
    seen = set()
    values = []
    for start, end in longest_palindrome_spans(s):
        value = s[start:end]
        if value not in seen:
            seen.add(value)
            values.append(value)
    return values
```

## 复杂度：结果空间不能漏算

设输入长度为`n`，最长回文长度为`L`，最长出现位置数为`m`，去重后内容数为`u`。

区间接口最坏时间`O(n²)`，例如全是相同字符时；最多检查`2n - 1`个有效中心，最终`m = O(n)`。实现中候选列表在中途也可能有`O(n)`项，因此整体峰值空间是`O(n)`；只有循环的标量工作状态是常数，不能把整个实现说成`O(1)`空间。

内容接口对每个保留区间切片并判断去重。按字符串复制及哈希的通常成本，平均时间上界为`O(n² + mL)`；集合操作的这里使用平均情形，不保证哈希碰撞下的最坏常数时间。去重后的文本本身需`O(uL)`存储，加上候选区间与容器，总空间上界为`O(n + uL)`，不能只说`O(u)`。这里是按每个码点占常数量级存储的分析，不是Python对象的精确字节数。

## 追问与常见误区

- **只把原算法的`>`改成`>=`可以吗？** 不行，那仍然只保留一个位置，只是换成最后遇到的并列答案。需要一个候选列表。
- **每次扩展都把当前回文加进结果可以吗？** 那会混入短回文，并反复切片。每个中心先扩到头，再与当前最优长度比较。
- **只检查奇数中心会怎样？** `abba`中的偶数回文会被遗漏。
- **为什么不用`list(set(values))`？** 如果要保留首次出现顺序，它不符合合同；如果要保留所有位置，按内容去重本身就是错的。
- **空串、一个字符和全不相同的字符串怎么处理？** 依次返回空列表、一个长度1的区间、全部长度1的区间。不能在空串时捏造`(0, 1)`。
- **回文子序列也能这样做吗？** 不能。这里的子串必须连续；允许跳过字符后，问题的状态与算法都不同。

## 边界与测试

[测试代码](../../examples/interview_algorithms/test_all_longest_palindromes.py)使用独立的“枚举全部子串并反转比较”作为小输入判定器，穷举`abc`上长度0到7的全部3280个字符串。同时覆盖奇偶中心、多个不同答案、重复内容的不同位置、更长答案清空旧候选、大小写，以及1000字符的重复串和全不同字符串。有限测试不能替代上面的不变量证明。

```sh
python -B examples/interview_algorithms/test_all_longest_palindromes.py
```
