# 75. 颜色分类

[官方题目](https://leetcode.cn/problems/sort-colors/) · MEDIUM · 官方分类：技巧

## 题意与接口

接口：`Solution.sortColors(nums: list[int]) -> None`。数组只含 0、1、2，需要原地按 0、1、2 分组排序，不能调用排序库。官方长度 1 至 300。返回值为 None，结果保存在原列表内。

约束与规则于 2026-10-09 查阅[官方英文题面](https://leetcode.com/problems/sort-colors/)核对；以下为原创概述，并非完整题面转载。

## 从朴素方法到优化

统计三种值的次数，再覆盖原数组，已经是 O(n) 时间、O(1) 空间，但需要两轮扫描。荷兰国旗算法把数组分成已完成与未分类区间，一轮处理即可完成。

## 核心思路

维护四段：`[0,left)` 全是 0，`[left,scan)` 全是 1，`[scan,right]` 未分类，`(right,n)` 全是 2。遇 0 交换到 left，并推进 left、scan；遇 1 只推进 scan；遇 2 交换到 right 并缩小 right，此时换来的值尚未分类，scan 不动。

## 手推一个小例子

取 `[1, 2, 0, 1, 0]`：
1. scan=0 是 1，向前移动。
2. scan=1 是 2，与末尾 0 交换，数组为 `[1,0,0,1,2]`，right=3，scan 仍为 1。
3. 读到 0，与 left=0 交换，成为 `[0,1,0,1,2]`。
4. 再读 0，放到下标 1，得到 `[0,0,1,1,2]`。
5. 扫完最后一个 1，未知区间为空。

## 为什么正确

初始只有未分类区间，四段不变量成立。遇 0 时，left 处若不是当前格，必为已分类的 1，交换后仍维护 0 段和 1 段；遇 1 可直接并入 1 段；遇 2 放到右端后只需保留换入值等待检查。每步未知区间至少缩小一格，终止时所有位置均属正确段，且交换保持元素多重集合不变。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0075_sort_colors.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def sortColors(self, nums: list[int]) -> None:
        left = scan = 0
        right = len(nums) - 1
        while scan <= right:
            if nums[scan] == 0:
                nums[left], nums[scan] = nums[scan], nums[left]
                left += 1
                scan += 1
            elif nums[scan] == 1:
                scan += 1
            else:
                nums[scan], nums[right] = nums[right], nums[scan]
                right -= 1
                # 新换到 scan 的值尚未分类，不能跳过。
```

## 复杂度

时间 O(n)，辅助空间 O(1)。虽然 scan 在遇 2 时不前进，但 right 会后退，未分类长度每轮都减一。

## 边界与易错点

- while 条件包含等号，未知区间最后一格也要处理。
- 交换 2 后不能 scan+=1。
- 不要返回新排序列表；题目要求原对象被修改。
- else 分支按官方输入把剩余值视为 2，未对其他数字额外校验。

## 本地测试与复习

测试文件：[`test_greedy_dp_tricks.py`](../../../tests/hot100/test_greedy_dp_tricks.py)，对应 `test_p0075`。含合法最小输入、典型与关键边界；适用题使用固定随机种子与独立穷举或参考算法对拍。

复习：交换 0 后为什么可以立即推进 scan，而交换 2 后不能？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/sort-colors/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0075.Sort%20Colors/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：本次已核验的官方站点、sitemap、固定仓库目录与精确题号/标题检索中未找到本题直接匹配；不代表永久不存在。
- 官方Python：本次核验未找到本题精确匹配的官方实现区。
- 本题配套视频：本次已核验的官方来源中未找到直接匹配视频。

自主复习提示：定义三段已分类区间，解释交换高值到右侧后当前下标为什么不能立刻前进。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
