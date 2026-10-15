# 31. 下一个排列

难度：MEDIUM · 分类：技巧

## 题意与接口

接口：`Solution.nextPermutation(nums: list[int]) -> None`。原地改成字典序紧接其后的排列；若已经最大，则改成升序最小排列。允许重复元素，要求常量额外空间。官方长度 1 至 100。

约束与规则于 2026-10-09 查阅官方英文题面核对；以下为原创概述，并非完整题面转载。

## 从朴素方法到优化

生成全部排列、去重、排序，时间与空间都是阶乘级。字典序优先比较左边，因此希望让变大的位置尽量靠右，同时使变大的幅度尽量小。

## 核心思路

从右向左找第一个 nums[pivot]<nums[pivot+1]。它右侧已经是非递增的最大后缀，必须增大 pivot 才有更大排列。在后缀从右找首个严格大于 pivot 的值交换，这就是最小可增大的值。交换后后缀仍非递增，将它原地反转成最小升序。若找不到 pivot，反转整个数组。

## 手推一个小例子

取 `[1, 4, 3, 3, 2]`：
1. 从右看，`4,3,3,2` 非递增，pivot 是下标 0 的 1。
2. 从右找首个大于 1 的值，是 2；交换得 `[2,4,3,3,1]`。
3. 将后缀 `[4,3,3,1]` 反转为 `[1,3,3,4]`。
4. 结果 `[2,1,3,3,4]`，比原数组大，且不存在更近的较大排列。

## 为什么正确

非递增后缀已是这些元素的最大字典序排列，仅重排它无法变大，所以右侧所有位置都不能成为首个增加点，pivot 是最靠右的可行位置。选择大于原 pivot 的最小值，令该位置增幅最小；此前前缀不变。最后把后缀排为最小，便在此前决策下使整个排列最小，即下一个排列。全数组非递增时不存在更大排列，应返回最小排列。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0031_next_permutation.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def nextPermutation(self, nums: list[int]) -> None:
        pivot = len(nums) - 2
        while pivot >= 0 and nums[pivot] >= nums[pivot + 1]:
            pivot -= 1
        if pivot >= 0:
            successor = len(nums) - 1
            while nums[successor] <= nums[pivot]:
                successor -= 1
            nums[pivot], nums[successor] = nums[successor], nums[pivot]
        # 后缀仍非递增，用交换反转，避免切片的线性额外内存。
        left, right = pivot + 1, len(nums) - 1
        while left < right:
            nums[left], nums[right] = nums[right], nums[left]
            left += 1
            right -= 1
```

## 复杂度

时间 O(n)，辅助空间 O(1)，原地修改并返回 None。`nums[left:] = reversed(nums[left:])` 会先复制切片，不属于常量额外空间版本。

## 边界与易错点

- 找 pivot 时跳过相等元素，找 successor 时也要求严格大于。
- 全降序或全相等会 pivot=−1，应反转整个数组。
- 单元素数组自然保持不变。
- 不能只交换 pivot 后就结束，否则新后缀通常不是最小。

## 本地测试与复习

测试文件：[`test_greedy_dp_tricks.py`](../../../tests/hot100/test_greedy_dp_tricks.py)，对应 `test_p0031`。含合法最小输入、典型与关键边界；适用题使用固定随机种子与独立穷举或参考算法对拍。

复习：为什么 successor 可以从右侧线性找，而不必排序？如何得到字典序上一个排列？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：从右寻找首次上升位置，再找最小的更大替代值；解释反转后缀为何得到紧邻排列。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
