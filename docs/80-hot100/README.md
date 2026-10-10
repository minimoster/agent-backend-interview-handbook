# LeetCode Hot100：Python原创学习模块

以[力扣中国官方热题100](https://leetcode.cn/studyplan/top-100-liked/)的17类、100题为范围（核对日期2026-10-09），与国际站同名计划的题号/slug集合交叉核对一致。这里用简短自主概述、原创推导与实现帮助理解，不转载完整官方题面。

## 怎样使用

1. 先读题意与接口，写出最直观解法及瓶颈。
2. 用页面里的小例子手推状态，能解释不变量后再编码。
3. 对照源码与边界测试，第二天不看答案重写；一周后尝试口述正确性与复杂度。
4. 源码使用Python 3.10+标准库；从仓库根目录运行测试，不需要联网或第三方依赖。

```bash
python -m unittest discover -s tests/hot100 -p "test_*.py" -v
python examples/hot100/check_hot100.py
```

入口：[接口与本地运行](../../examples/hot100/README.md) · [测试说明](TESTING.md) · [方法迁移与复习路线](PATTERNS.md) · [来源与权利边界](SOURCES.md) · [机器题单](manifest.json)

没有将本地有限测试冒充LeetCode在线AC；每页源码、测试与约束核对范围可追溯。

## 官方17分类与100题

### 01. [哈希](categories/01-hash.md)（3题）

哈希表适合把“反复扫描找匹配”变成“按键直接找到历史信息”。先明确键代表值、字符多重集合还是连续段起点，字典值是下标、频次还是分组。

- [1. 两数之和](problems/0001-two-sum.md) · 简单
- [49. 字母异位词分组](problems/0049-group-anagrams.md) · 中等
- [128. 最长连续序列](problems/0128-longest-consecutive-sequence.md) · 中等

### 02. [双指针](categories/02-two-pointers.md)（4题）

双指针的关键不是两个变量，而是移动一端为什么能安全排除一批候选。相向指针依赖排序或支配关系，同向指针常维护稳定压缩的已处理前缀。

- [283. 移动零](problems/0283-move-zeroes.md) · 简单
- [11. 盛最多水的容器](problems/0011-container-with-most-water.md) · 中等
- [15. 三数之和](problems/0015-3sum.md) · 中等
- [42. 接雨水](problems/0042-trapping-rain-water.md) · 困难

### 03. [滑动窗口](categories/03-sliding-window.md)（2题）

窗口必须对应连续区间。扩张、收缩和记录答案的先后顺序源于窗口不变量；先说清固定长度还是可变长度，再写代码。

- [3. 无重复字符的最长子串](problems/0003-longest-substring-without-repeating-characters.md) · 中等
- [438. 找到字符串中所有字母异位词](problems/0438-find-all-anagrams-in-a-string.md) · 中等

### 04. [子串](categories/04-substring.md)（3题）

官方把前缀和、单调队列与最小覆盖归为“子串”。要区分可用窗口单调性的题与含负数的前缀和计数题，不能看到连续区间就套同一种窗口。

- [560. 和为 K 的子数组](problems/0560-subarray-sum-equals-k.md) · 中等
- [239. 滑动窗口最大值](problems/0239-sliding-window-maximum.md) · 困难
- [76. 最小覆盖子串](problems/0076-minimum-window-substring.md) · 困难

### 05. [普通数组](categories/05-array.md)（5题）

普通数组题常把重复计算拆成前后信息，或用原位置存放登记状态。必须明确是否允许修改输入，排序、切片和返回数组的空间应单独计算。

- [53. 最大子数组和](problems/0053-maximum-subarray.md) · 中等
- [56. 合并区间](problems/0056-merge-intervals.md) · 中等
- [189. 轮转数组](problems/0189-rotate-array.md) · 中等
- [238. 除了自身以外数组的乘积](problems/0238-product-of-array-except-self.md) · 中等
- [41. 缺失的第一个正数](problems/0041-first-missing-positive.md) · 困难

### 06. [矩阵](categories/06-matrix.md)（4题）

矩阵题先画坐标与边界。原地修改要防止新写入数据污染“原始状态”，遍历要防止最后一行或一列被读两次。

- [73. 矩阵置零](problems/0073-set-matrix-zeroes.md) · 中等
- [54. 螺旋矩阵](problems/0054-spiral-matrix.md) · 中等
- [48. 旋转图像](problems/0048-rotate-image.md) · 中等
- [240. 搜索二维矩阵 II](problems/0240-search-a-2d-matrix-ii.md) · 中等

### 07. [链表](categories/07-linked-list.md)（14题）

链表操作先画引用关系，再断开旧边。值相等不代表同一个节点；dummy统一头部边界，快慢指针表达距离或环结构。

- [160. 相交链表](problems/0160-intersection-of-two-linked-lists.md) · 简单
- [206. 反转链表](problems/0206-reverse-linked-list.md) · 简单
- [234. 回文链表](problems/0234-palindrome-linked-list.md) · 简单
- [141. 环形链表](problems/0141-linked-list-cycle.md) · 简单
- [142. 环形链表 II](problems/0142-linked-list-cycle-ii.md) · 中等
- [21. 合并两个有序链表](problems/0021-merge-two-sorted-lists.md) · 简单
- [2. 两数相加](problems/0002-add-two-numbers.md) · 中等
- [19. 删除链表的倒数第 N 个结点](problems/0019-remove-nth-node-from-end-of-list.md) · 中等
- [24. 两两交换链表中的节点](problems/0024-swap-nodes-in-pairs.md) · 中等
- [25. K 个一组翻转链表](problems/0025-reverse-nodes-in-k-group.md) · 困难
- [138. 随机链表的复制](problems/0138-copy-list-with-random-pointer.md) · 中等
- [148. 排序链表](problems/0148-sort-list.md) · 中等
- [23. 合并 K 个升序链表](problems/0023-merge-k-sorted-lists.md) · 困难
- [146. LRU 缓存](problems/0146-lru-cache.md) · 中等

### 08. [二叉树](categories/08-binary-tree.md)（15题）

树题先定义每次访问返回什么，以及答案是否允许同时使用左右分支。显式栈与队列避免Python递归深度限制；节点身份与节点值要区分。

- [94. 二叉树的中序遍历](problems/0094-binary-tree-inorder-traversal.md) · 简单
- [104. 二叉树的最大深度](problems/0104-maximum-depth-of-binary-tree.md) · 简单
- [226. 翻转二叉树](problems/0226-invert-binary-tree.md) · 简单
- [101. 对称二叉树](problems/0101-symmetric-tree.md) · 简单
- [543. 二叉树的直径](problems/0543-diameter-of-binary-tree.md) · 简单
- [102. 二叉树的层序遍历](problems/0102-binary-tree-level-order-traversal.md) · 中等
- [108. 将有序数组转换为二叉搜索树](problems/0108-convert-sorted-array-to-binary-search-tree.md) · 简单
- [98. 验证二叉搜索树](problems/0098-validate-binary-search-tree.md) · 中等
- [230. 二叉搜索树中第 K 小的元素](problems/0230-kth-smallest-element-in-a-bst.md) · 中等
- [199. 二叉树的右视图](problems/0199-binary-tree-right-side-view.md) · 中等
- [114. 二叉树展开为链表](problems/0114-flatten-binary-tree-to-linked-list.md) · 中等
- [105. 从前序与中序遍历序列构造二叉树](problems/0105-construct-binary-tree-from-preorder-and-inorder-traversal.md) · 中等
- [437. 路径总和 III](problems/0437-path-sum-iii.md) · 中等
- [236. 二叉树的最近公共祖先](problems/0236-lowest-common-ancestor-of-a-binary-tree.md) · 中等
- [124. 二叉树中的最大路径和](problems/0124-binary-tree-maximum-path-sum.md) · 困难

### 09. [图论](categories/09-graph.md)（4题）

把节点、边、访问状态说明白，再决定DFS、BFS还是拓扑排序。多源BFS是从所有初始源同时扩散；前缀树是按字符边组织检索状态。

- [200. 岛屿数量](problems/0200-number-of-islands.md) · 中等
- [994. 腐烂的橘子](problems/0994-rotting-oranges.md) · 中等
- [207. 课程表](problems/0207-course-schedule.md) · 中等
- [208. 实现 Trie (前缀树)](problems/0208-implement-trie-prefix-tree.md) · 中等

### 10. [回溯](categories/10-backtracking.md)（8题）

回溯=选择、递归、撤销。先保证不漏不重，再根据输入性质剪枝；复杂度包含复制最终答案的成本，不能把指数输出算法写成线性。

- [46. 全排列](problems/0046-permutations.md) · 中等
- [78. 子集](problems/0078-subsets.md) · 中等
- [17. 电话号码的字母组合](problems/0017-letter-combinations-of-a-phone-number.md) · 中等
- [39. 组合总和](problems/0039-combination-sum.md) · 中等
- [22. 括号生成](problems/0022-generate-parentheses.md) · 中等
- [79. 单词搜索](problems/0079-word-search.md) · 中等
- [131. 分割回文串](problems/0131-palindrome-partitioning.md) · 中等
- [51. N 皇后](problems/0051-n-queens.md) · 困难

### 11. [二分查找](categories/11-binary-search.md)（6题）

二分查找依赖单调判断。半开区间与闭区间不能混用；旋转数组每轮找有序的一半，中位数题把搜索对象从数值改为分割位置。

- [35. 搜索插入位置](problems/0035-search-insert-position.md) · 简单
- [74. 搜索二维矩阵](problems/0074-search-a-2d-matrix.md) · 中等
- [34. 在排序数组中查找元素的第一个和最后一个位置](problems/0034-find-first-and-last-position-of-element-in-sorted-array.md) · 中等
- [33. 搜索旋转排序数组](problems/0033-search-in-rotated-sorted-array.md) · 中等
- [153. 寻找旋转排序数组中的最小值](problems/0153-find-minimum-in-rotated-sorted-array.md) · 中等
- [4. 寻找两个正序数组的中位数](problems/0004-median-of-two-sorted-arrays.md) · 困难

### 12. [栈](categories/12-stack.md)（5题）

普通栈记录尚未匹配或暂停的上下文，单调栈记录还没找到边界的候选。先解释弹出时算出的是什么，再写while。

- [20. 有效的括号](problems/0020-valid-parentheses.md) · 简单
- [155. 最小栈](problems/0155-min-stack.md) · 中等
- [394. 字符串解码](problems/0394-decode-string.md) · 中等
- [739. 每日温度](problems/0739-daily-temperatures.md) · 中等
- [84. 柱状图中最大的矩形](problems/0084-largest-rectangle-in-histogram.md) · 困难

### 13. [堆](categories/13-heap.md)（3题）

堆只承诺根是极值，不保证整个容器有序。Top K用小根堆保留大值；双堆维护左右半边的大小与数值顺序。

- [215. 数组中的第K个最大元素](problems/0215-kth-largest-element-in-an-array.md) · 中等
- [347. 前 K 个高频元素](problems/0347-top-k-frequent-elements.md) · 中等
- [295. 数据流的中位数](problems/0295-find-median-from-data-stream.md) · 困难

### 14. [贪心算法](categories/14-greedy.md)（4题）

贪心必须给出安全性证明：交换论证、支配关系或当前层最远可达。只说“每次选最大”不足以说明正确。

- [121. 买卖股票的最佳时机](problems/0121-best-time-to-buy-and-sell-stock.md) · 简单
- [55. 跳跃游戏](problems/0055-jump-game.md) · 中等
- [45. 跳跃游戏 II](problems/0045-jump-game-ii.md) · 中等
- [763. 划分字母区间](problems/0763-partition-labels.md) · 中等

### 15. [动态规划](categories/15-dynamic-programming.md)（10题）

DP先说状态含义，再说转移、初始化和遍历顺序。滚动数组只能在依赖关系明确之后优化；完全背包与0/1背包的容量循环方向不同。

- [70. 爬楼梯](problems/0070-climbing-stairs.md) · 简单
- [118. 杨辉三角](problems/0118-pascals-triangle.md) · 简单
- [198. 打家劫舍](problems/0198-house-robber.md) · 中等
- [279. 完全平方数](problems/0279-perfect-squares.md) · 中等
- [322. 零钱兑换](problems/0322-coin-change.md) · 中等
- [139. 单词拆分](problems/0139-word-break.md) · 中等
- [300. 最长递增子序列](problems/0300-longest-increasing-subsequence.md) · 中等
- [152. 乘积最大子数组](problems/0152-maximum-product-subarray.md) · 中等
- [416. 分割等和子集](problems/0416-partition-equal-subset-sum.md) · 中等
- [32. 最长有效括号](problems/0032-longest-valid-parentheses.md) · 困难

### 16. [多维动态规划](categories/16-multidimensional-dp.md)（5题）

二维DP通常描述两个前缀或网格位置。压成一维时，要分清当前行、上一行与左上角的旧值；字符串切片的复制成本不能漏记。

- [62. 不同路径](problems/0062-unique-paths.md) · 中等
- [64. 最小路径和](problems/0064-minimum-path-sum.md) · 中等
- [5. 最长回文子串](problems/0005-longest-palindromic-substring.md) · 中等
- [1143. 最长公共子序列](problems/1143-longest-common-subsequence.md) · 中等
- [72. 编辑距离](problems/0072-edit-distance.md) · 中等

### 17. [技巧](categories/17-tricks.md)（5题）

技巧题往往依赖明确前提：异或消去成对值，多数投票要求多数确实存在，环检测依赖值域映射。先验证题设再套模板。

- [136. 只出现一次的数字](problems/0136-single-number.md) · 简单
- [169. 多数元素](problems/0169-majority-element.md) · 简单
- [75. 颜色分类](problems/0075-sort-colors.md) · 中等
- [31. 下一个排列](problems/0031-next-permutation.md) · 中等
- [287. 寻找重复数](problems/0287-find-the-duplicate-number.md) · 中等

