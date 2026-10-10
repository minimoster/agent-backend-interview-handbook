# 189. 轮转数组

[官方题目](https://leetcode.cn/problems/rotate-array/) · MEDIUM · 官方分类：普通数组

## 题意与接口

将数组向右轮转k步，尾部元素绕到开头。`rotate(nums,k)` 原地修改，返回None；k为非负整数。

## 从朴素方法到优化

每次移动一步需要 O(nk) 时间；拼接切片需 O(n)空间。三次原地反转能用 O(n)时间/O(1)额外空间实现同一重排。

## 核心思路

先令k%=n。把数组写成AB，其中B是最后k个元素。整体反转得到rev(B)rev(A)，再分别反转前k个和后n-k个，得到BA。

## 手推一个小例子

[1,4,7,9,2]右移2：整体反转为[2,9,7,4,1]；前2个反转为[9,2,7,4,1]；剩余反转为[9,2,1,4,7]。

## 为什么正确

整体反转交换了两个分段的位置，同时反转了各段内部顺序；后两次反转恢复各段内部顺序。因此每个元素最终位于原下标加k对n取模的位置。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0189_rotate_array.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def rotate(self, nums: list[int], k: int) -> None:
        if not nums:
            return
        k %= len(nums)
        def reverse(left, right):
            while left < right:
                nums[left], nums[right] = nums[right], nums[left]
                left += 1
                right -= 1
        # AB -> rev(B)rev(A) -> B rev(A) -> BA。
        reverse(0, len(nums) - 1)
        reverse(0, k - 1)
        reverse(k, len(nums) - 1)
```

## 复杂度

时间 O(n)，辅助空间 O(1)。反转函数迭代执行，未复制切片。

## 边界与易错点

- k可能大于n，先取模。
- 空数组先返回，避免对0取模；这属于题设外保护。
- k=0时前段为空，整体与后段的两次反转互相抵消。

## 本地测试与复习

测试k=0、k=n、k>n、单元素；随机与切片重排对拍并断言返回None。

复习：用AB两个符号写出三次反转的代数过程；左移k和右移k有什么对应关系？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/rotate-array/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0100-0199/0189.Rotate%20Array/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/algo/other/0189-rotate-array.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/algo/other/0189-rotate-array.html#python)。可与上面的本仓库原创实现对照。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：先化简 k，再画出三次反转对每段的作用；检查 k 为零或数组长度的倍数。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
