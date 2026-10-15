# 41. 缺失的第一个正数

难度：HARD · 分类：普通数组

## 题意与接口

找出数组中没有出现的最小正整数。`firstMissingPositive(nums)` 返回整数；本实现会原地重排输入，满足线性时间与常数额外空间。

## 从朴素方法到优化

用集合记录后从1找起需 O(n)额外空间。长度n的数组答案一定在1..n+1；可把原数组位置0..n-1当作值1..n是否存在的登记处。

## 核心思路

只要当前值x在1..n且其目标位置x-1还不是x，就交换过去；重复处理换回来的值。结束后第一个nums[i]≠i+1的位置，对应缺失的i+1；全匹配则返回n+1。

## 手推一个小例子

[4,1,-2,2]：位置0的4归位到3，得到[2,1,-2,4]；2归位到1得[1,2,-2,4]；前两格匹配，第三格不是3，答案3。

## 为什么正确

每次有效交换都会把一个1..n内的值永久放到正确位置，不会再被其他不同值挤走，因此总交换次数至多n。最终若值x曾存在，它的目标格必为x；所以首个不匹配目标格就是最小缺失正数。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0041_first_missing_positive.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def firstMissingPositive(self, nums: list[int]) -> int:
        n = len(nums)
        # 合法值x的登记位置是x-1；每次交换至少归位一个值。
        for i in range(n):
            while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
                target = nums[i] - 1  # 先存目标，避免交换后再读nums[i]
                nums[i], nums[target] = nums[target], nums[i]
        for i, value in enumerate(nums):
            if value != i + 1:
                return i + 1
        return n + 1
```

## 复杂度

时间 O(n)，辅助空间 O(1)。双层语法不等于平方复杂度：所有while累计成功交换至多n次。

## 边界与易错点

- [1,1]必须用目标格已等于当前值的条件终止，否则可能死循环。
- 先检查范围，不能让负数触发Python负索引。
- 本解修改输入；若调用者要保留原数组，复制的成本由调用者承担。

## 本地测试与复习

测试重复值、全部负数、完整1..n、超范围大值；随机与集合查找对拍。

复习：为什么答案不会超过n+1？怎样证明每次交换有不可逆的进展？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[运行方式](../../../examples/hot100/README.md)。

[返回分类导航](../README.md)

## 复习与迁移

自主复习提示：解释原地换位的目标位置；用重复数字检查停止条件，避免同一个位置无限交换。

[算法基础补充题库](../../85-algorithm-supplement/README.md)
