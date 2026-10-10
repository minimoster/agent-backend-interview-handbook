# 多维动态规划：5题

二维DP通常描述两个前缀或网格位置。压成一维时，要分清当前行、上一行与左上角的旧值；字符串切片的复制成本不能漏记。

## 本类题目

- [62. 不同路径](../problems/0062-unique-paths.md) · 中等 · 二维 DP，进阶压成一维
- [64. 最小路径和](../problems/0064-minimum-path-sum.md) · 中等 · 网格动态规划
- [5. 最长回文子串](../problems/0005-longest-palindromic-substring.md) · 中等 · 中心扩展；二维回文 DP 作对照
- [1143. 最长公共子序列](../problems/1143-longest-common-subsequence.md) · 中等 · 二维前缀 DP
- [72. 编辑距离](../problems/0072-edit-distance.md) · 中等 · 二维前缀 DP：增、删、替换

## 学完后自检

- 能说出每题结构里保存的是什么，而不只是背容器名称。
- 能解释每次丢弃候选、移动边界或改变状态为什么安全。
- 能写出最容易出错的最小输入，并说明预期输出。

[返回Hot100总导航](../README.md)
