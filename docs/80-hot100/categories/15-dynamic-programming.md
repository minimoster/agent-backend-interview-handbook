# 动态规划：10题

DP先说状态含义，再说转移、初始化和遍历顺序。滚动数组只能在依赖关系明确之后优化；完全背包与0/1背包的容量循环方向不同。

## 本类题目

- [70. 爬楼梯](../problems/0070-climbing-stairs.md) · 简单 · 滚动变量动态规划
- [118. 杨辉三角](../problems/0118-pascals-triangle.md) · 简单 · 逐行由上一行相邻两数生成
- [198. 打家劫舍](../problems/0198-house-robber.md) · 中等 · 相邻不可同时选的滚动动态规划
- [279. 完全平方数](../problems/0279-perfect-squares.md) · 中等 · 完全背包动态规划
- [322. 零钱兑换](../problems/0322-coin-change.md) · 中等 · 完全背包动态规划，不可达状态用无穷大
- [139. 单词拆分](../problems/0139-word-break.md) · 中等 · 前缀动态规划与单词集合
- [300. 最长递增子序列](../problems/0300-longest-increasing-subsequence.md) · 中等 · 先讲 O(n^2) DP，再讲 tails 数组与二分
- [152. 乘积最大子数组](../problems/0152-maximum-product-subarray.md) · 中等 · 同时维护以当前位置结尾的最大积和最小积
- [416. 分割等和子集](../problems/0416-partition-equal-subset-sum.md) · 中等 · 0/1 背包，容量倒序更新
- [32. 最长有效括号](../problems/0032-longest-valid-parentheses.md) · 困难 · 动态规划或带哨兵下标栈

## 学完后自检

- 能说出每题结构里保存的是什么，而不只是背容器名称。
- 能解释每次丢弃候选、移动边界或改变状态为什么安全。
- 能写出最容易出错的最小输入，并说明预期输出。

[返回Hot100总导航](../README.md)
