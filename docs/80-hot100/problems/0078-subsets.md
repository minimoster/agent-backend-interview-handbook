# 78. 子集

[官方题目](https://leetcode.cn/problems/subsets/) · MEDIUM · 官方分类：回溯

## 题意与接口

返回互不相同整数数组的全部子集，含空集。接口：`subsets(nums)`，答案顺序不限。

约束核对（2026-10-09）：长度 1..10，整数互异；子集必须无重复，顺序不限。 [官方来源](https://leetcode.com/problems/subsets/)

## 从朴素方法到优化

可以用位掩码枚举 2^n 种选法；回溯则直接维护已选位置严格递增的路径。每一个递归状态本身就是一个合法子集。

## 核心思路

start 表示后续只可选的最小下标。每进入一层先保存当前子集，再依次选 i≥start，并递归到 i+1，避免 `[a,b]` 与 `[b,a]` 的重复。

## 手推一个小例子

`[3,6]`：初始输出 `[]`；选 3 输出 `[3]`，再选 6 输出 `[3,6]`；返回根后选 6 输出 `[6]`，共四个子集。

## 为什么正确

每个子集由一组递增下标唯一确定。搜索只沿递增下标前进，因此不会重复；任意下标组都可按其顺序选择，故不会遗漏。

## Python 实现

[完整可导入源码](../../../examples/hot100/p0078_subsets.py)。节点结构来自 [structures.py](../../../examples/hot100/structures.py)；普通题使用 `Solution`，设计题使用题目类名。提交到 LeetCode 时保留算法主体，删除本地节点导入，使用平台提供的节点类型。

```python
class Solution:
    def subsets(self, nums):
        answer, path = [], []
        def search(start):
            answer.append(path.copy())
            for i in range(start, len(nums)):
                path.append(nums[i])
                # 下标严格递增，避免把同一子集的不同顺序重复输出。
                search(i + 1)
                path.pop()
        search(0)
        return answer
```

## 复杂度

时间 O(n·2^n)，辅助空间 O(n)，输出 O(n·2^n)；所有子集总元素数为 n·2^(n-1)。

## 边界与易错点

空集必须输出。递归传 i+1 而非 start+1。若输入重复，此方法不会自动去重。

## 本地测试与复习

可执行测试：`tests/hot100/test_structures_algorithms.py`，包含本题典型情况和边界；随机对拍使用固定种子。

复习：为什么排列需要 used，子集仅需 start？

本地测试只能提供有限输入上的证据；本仓库没有把“测试通过”写成“LeetCode 已 AC”。复现命令和覆盖边界见[测试说明](../TESTING.md)。

## 延伸阅读

- [官方原题与约束](https://leetcode.cn/problems/subsets/)
- [doocs 对照材料（固定版本，仅链接）](https://github.com/doocs/leetcode/blob/c412a46586590f020b0d861c163758cb60987270/solution/0000-0099/0078.Subsets/README.md)
- [返回分类导航](../README.md)

## 代码随想录延伸阅读

外部资源作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。以下提供官方外链，不复制上游题解、Python代码或视频。

- 官网讲解：[本题对应页面或区块](https://programmercarl.com/hot100/0078.subsets.html)
- 官方Python：[本题对应实现区](https://programmercarl.com/hot100/0078.subsets.html#python3)。可与上面的本仓库原创实现对照。
- 本题配套视频：[78. 子集](https://www.bilibili.com/video/BV1U84y1q7Ci)。上传者已核验为代码随想录（MID 525438321）。

自主复习提示：明确答案是在每个搜索节点记录还是只在叶子记录，验证空集与完整集合都恰好出现一次。

资源覆盖与权利说明见[代码随想录来源记录](../../../sources/carl-hot100-resources.md)；非Hot100练习单列在[算法基础补充题库](../../85-algorithm-supplement/README.md)。
