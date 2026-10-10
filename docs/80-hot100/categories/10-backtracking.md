# 回溯：8题

回溯=选择、递归、撤销。先保证不漏不重，再根据输入性质剪枝；复杂度包含复制最终答案的成本，不能把指数输出算法写成线性。

## 本类题目

- [46. 全排列](../problems/0046-permutations.md) · 中等 · 回溯与 used 标记
- [78. 子集](../problems/0078-subsets.md) · 中等 · 回溯枚举选或不选
- [17. 电话号码的字母组合](../problems/0017-letter-combinations-of-a-phone-number.md) · 中等 · 回溯逐位枚举字母
- [39. 组合总和](../problems/0039-combination-sum.md) · 中等 · 排序、起始下标、可重复选择与剪枝
- [22. 括号生成](../problems/0022-generate-parentheses.md) · 中等 · 回溯维护左右括号数量
- [79. 单词搜索](../problems/0079-word-search.md) · 中等 · DFS 回溯：暂时标记访问并恢复
- [131. 分割回文串](../problems/0131-palindrome-partitioning.md) · 中等 · 预处理回文区间，再回溯切分
- [51. N 皇后](../problems/0051-n-queens.md) · 困难 · 按行回溯，用列与两条对角线集合剪枝

## 学完后自检

- 能说出每题结构里保存的是什么，而不只是背容器名称。
- 能解释每次丢弃候选、移动边界或改变状态为什么安全。
- 能写出最容易出错的最小输入，并说明预期输出。

[返回Hot100总导航](../README.md)
