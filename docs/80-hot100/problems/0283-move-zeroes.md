# 283. 移动零

[官方题目](https://leetcode.cn/problems/move-zeroes/) · EASY · 官方分类：双指针

## 题意与接口

将数组所有非零元素稳定地移到前面，零集中到末尾。`moveZeroes(nums)` 原地修改并返回None。

## 从朴素方法到优化

额外建非零数组再补零可用 O(n) 空间。扫描过程中用一个写入位置压缩非零元素，可以保留原顺序并使用常数额外空间。

## 核心思路

write指向下一个非零元素应存放的位置。先顺序写回所有非零值，最后把剩余后缀填零；始终write不超过当前读取位置，所以不会破坏未读数据。

## 手推一个小例子

[0,4,0,2]中，4写入位置0，2写入位置1，write变成2；最后把位置2、3清零，得到[4,2,0,0]。

## 为什么正确

每次处理后，nums[:write]恰为已扫描前缀中按原顺序排列的非零元素。扫描结束后这些元素完整且稳定，剩余位置只需补齐零。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0283_move_zeroes.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def moveZeroes(self, nums: list[int]) -> None:
        # nums[:write]始终是已读区域中稳定排列的非零前缀。
        write = 0
        for value in nums:
            if value != 0:
                nums[write] = value
                write += 1
        for i in range(write, len(nums)):
            nums[i] = 0
```

## 复杂度

时间 O(n)，辅助空间 O(1)。原地写入，输出占用原数组。

## 边界与易错点

- 不能重新绑定 nums 为新列表来冒充原地修改。
- 已写入前缀可能暂时留下旧值，最后填零不可省略。
- 全零、全非零及单元素都无需特殊分支。

## 本地测试与复习

测试稳定顺序、全零、全非零，随机对拍非零列表加对应数量零；同时断言返回None与对象身份不变。

复习：如果非零元素允许改变顺序，可以如何减少某些情况下的写操作？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/move-zeroes/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0200-0299/0283.Move%20Zeroes/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/0283.move-zeroes.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/0283.move-zeroes.html#python3)。可与上面的本仓库原创实现对照。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：画出读指针与写指针，检查非零元素的相对顺序为何保持不变，以及补零从哪里开始。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
