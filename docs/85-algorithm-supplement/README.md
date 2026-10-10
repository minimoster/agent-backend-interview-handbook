# 算法基础补充题库：代码随想录官方资源

这里单独收录15道非Hot100基础题，按方法分类。它们都不在当前[官方Hot100的100题清单](../80-hot100/manifest.json)中，不加入主清单计数，也不替换主清单里的任何解答。

作者：[代码随想录（程序员Carl）](https://programmercarl.com/)。核验日期：2026-10-10（UTC）。15题均核验到官网讲解和Python实现区，14题核验到本题直接视频。这里只提供官方链接与自主复习提示，没有复制外部完整题解或实现。

用法：先尝试做题，再读官网讲解，对照Python区手推状态；视频分为“本题配套”和“相关题迁移”。本页是资源练习单，没有新增可导入源码，也没有新增这些题的本地测试或在线AC记录。

[回到Hot100](../80-hot100/README.md) · [覆盖与权利说明](../../sources/carl-hot100-resources.md) · [逐题来源映射](../../sources/carl-hot100-resources.json)

## 分类导航

- 回溯：[77. 组合](#problem-77)
- 二分查找：[704. 二分查找](#problem-704)
- 双指针：[27. 移除元素](#problem-27)、[977. 有序数组的平方](#problem-977)
- 滑动窗口：[209. 长度最小的子数组](#problem-209)
- 矩阵：[59. 螺旋矩阵II](#problem-59)
- 链表：[203. 移除链表元素](#problem-203)、[707. 设计链表](#problem-707)
- 哈希：[242. 有效的字母异位词](#problem-242)、[349. 两个数组的交集](#problem-349)、[202. 快乐数](#problem-202)
- 字符串：[344. 反转字符串](#problem-344)、[151. 翻转字符串里的单词](#problem-151)
- 栈与队列：[232. 用栈实现队列](#problem-232)、[225. 用队列实现栈](#problem-225)

## 回溯

<a id="problem-77"></a>

### 77. 组合

补充分类：回溯 · 官方难度：中等（[来源](https://leetcode.com/problems/combinations/)）

[力扣题目](https://leetcode.cn/problems/combinations/) · [官网讲解](https://programmercarl.com/algo/backtracking/0077-combinations.html) · [官方Python区](https://programmercarl.com/algo/backtracking/0077-combinations.html#python)

- 本题配套视频：[本题：组合基础](https://www.bilibili.com/video/BV1ti4y1L7cv) · [本题：组合剪枝](https://www.bilibili.com/video/BV1wi4y157er)
- 同题其他官方页面：[77.组合优化](https://programmercarl.com/algo/backtracking/0077-combinations-optimized.html) · [77. 组合](https://programmercarl.com/hot100/0077.combinations.html)。代码随想录Hot100栏目收录77，但当前力扣官方Hot100清单不含77，所以仍放在本补充区。

自主复习提示：先画出起始下标限制，再根据还缺多少个数推导剪枝上界。对比“组合”与“全排列”为什么状态不同。


## 二分查找

<a id="problem-704"></a>

### 704. 二分查找

补充分类：二分查找 · 官方难度：简单（[来源](https://leetcode.com/problems/binary-search/)）

[力扣题目](https://leetcode.cn/problems/binary-search/) · [官网讲解](https://programmercarl.com/algo/array/0704-binary-search.html) · [官方Python区](https://programmercarl.com/algo/array/0704-binary-search.html#python)

- 本题配套视频：[704. 二分查找](https://www.bilibili.com/video/BV1fA4y1o715)

自主复习提示：分别采用闭区间与半开区间手推目标位于两端、缺失和单元素输入，保持更新规则与区间定义一致。


## 双指针

<a id="problem-27"></a>

### 27. 移除元素

补充分类：双指针 · 官方难度：简单（[来源](https://leetcode.com/problems/remove-element/)）

[力扣题目](https://leetcode.cn/problems/remove-element/) · [官网讲解](https://programmercarl.com/algo/array/0027-remove-element.html) · [官方Python区](https://programmercarl.com/algo/array/0027-remove-element.html#python)

- 本题配套视频：[27. 移除元素](https://www.bilibili.com/video/BV12A4y1Z7LP)

自主复习提示：让写指针表示已经保留的前缀长度，检查连续待删值与所有元素都被删的情况。迁移到移动零时再考虑稳定顺序。

<a id="problem-977"></a>

### 977. 有序数组的平方

补充分类：双指针 · 官方难度：简单（[来源](https://leetcode.com/problems/squares-of-a-sorted-array/)）

[力扣题目](https://leetcode.cn/problems/squares-of-a-sorted-array/) · [官网讲解](https://programmercarl.com/algo/array/0977-squares-of-a-sorted-array.html) · [官方Python区](https://programmercarl.com/algo/array/0977-squares-of-a-sorted-array.html#python)

- 本题配套视频：[977. 有序数组的平方](https://www.bilibili.com/video/BV1QB4y1D7ep)

自主复习提示：平方后的最大值来自原数组两端。先确定输出从哪一端填，再检查全负数与正负混合输入。


## 滑动窗口

<a id="problem-209"></a>

### 209. 长度最小的子数组

补充分类：滑动窗口 · 官方难度：中等（[来源](https://leetcode.com/problems/minimum-size-subarray-sum/)）

[力扣题目](https://leetcode.cn/problems/minimum-size-subarray-sum/) · [官网讲解](https://programmercarl.com/algo/array/0209-minimum-size-subarray-sum.html) · [官方Python区](https://programmercarl.com/algo/array/0209-minimum-size-subarray-sum.html#python)

- 本题配套视频：[209. 长度最小的子数组](https://www.bilibili.com/video/BV1tZ4y1q7XE)

自主复习提示：利用原题正数条件解释窗口收缩为何安全；加入负数后先重新检查这个依据，而不是直接沿用模板。


## 矩阵

<a id="problem-59"></a>

### 59. 螺旋矩阵II

补充分类：矩阵 · 官方难度：中等（[来源](https://leetcode.com/problems/spiral-matrix-ii/)）

[力扣题目](https://leetcode.cn/problems/spiral-matrix-ii/) · [官网讲解](https://programmercarl.com/algo/array/0059-spiral-matrix-ii.html) · [官方Python区](https://programmercarl.com/algo/array/0059-spiral-matrix-ii.html#python3)

- 本题配套视频：[59. 螺旋矩阵II](https://www.bilibili.com/video/BV1SL4y1N7mV)

自主复习提示：为每圈规定一致的边界归属，检查 n 为奇数时中心元素只填一次。和读取螺旋矩阵比较输出动作。


## 链表

<a id="problem-203"></a>

### 203. 移除链表元素

补充分类：链表 · 官方难度：简单（[来源](https://leetcode.com/problems/remove-linked-list-elements/)）

[力扣题目](https://leetcode.cn/problems/remove-linked-list-elements/) · [官网讲解](https://programmercarl.com/algo/linked-list/0203-remove-linked-list-elements.html) · [官方Python区](https://programmercarl.com/algo/linked-list/0203-remove-linked-list-elements.html#python)

- 本题配套视频：[203. 移除链表元素](https://www.bilibili.com/video/BV18B4y1s7R9)

自主复习提示：画出 dummy 与当前前驱的引用，检查删除头部、连续删除和删除尾部时前驱何时前进。

<a id="problem-707"></a>

### 707. 设计链表

补充分类：链表 · 官方难度：中等（[来源](https://leetcode.com/problems/design-linked-list/)）

[力扣题目](https://leetcode.cn/problems/design-linked-list/) · [官网讲解](https://programmercarl.com/algo/linked-list/0707-design-linked-list.html) · [官方Python区](https://programmercarl.com/algo/linked-list/0707-design-linked-list.html#python)

- 本题配套视频：[707. 设计链表](https://www.bilibili.com/video/BV1FU4y1X7WD)

自主复习提示：给每个操作写出合法下标边界，再连续执行头插、尾插、删除和查询，检查长度与链接同时维护。


## 哈希

<a id="problem-242"></a>

### 242. 有效的字母异位词

补充分类：哈希 · 官方难度：简单（[来源](https://leetcode.com/problems/valid-anagram/)）

[力扣题目](https://leetcode.cn/problems/valid-anagram/) · [官网讲解](https://programmercarl.com/algo/hash-table/0242-valid-anagram.html) · [官方Python区](https://programmercarl.com/algo/hash-table/0242-valid-anagram.html#python)

- 本题配套视频：[242. 有效的字母异位词](https://www.bilibili.com/video/BV1YG411p7BA)

自主复习提示：先说明字符范围决定数组计数还是字典计数，检查长度相等但频次不同的输入。

<a id="problem-349"></a>

### 349. 两个数组的交集

补充分类：哈希 · 官方难度：简单（[来源](https://leetcode.com/problems/intersection-of-two-arrays/)）

[力扣题目](https://leetcode.cn/problems/intersection-of-two-arrays/) · [官网讲解](https://programmercarl.com/algo/hash-table/0349-intersection-of-two-arrays.html) · [官方Python区](https://programmercarl.com/algo/hash-table/0349-intersection-of-two-arrays.html#python3)

- 本题配套视频：[349. 两个数组的交集](https://www.bilibili.com/video/BV1ba411S7wu)

自主复习提示：区分集合交集与多重集合交集，检查重复值不应在结果中重复出现。

<a id="problem-202"></a>

### 202. 快乐数

补充分类：哈希 · 官方难度：简单（[来源](https://leetcode.com/problems/happy-number/)）

[力扣题目](https://leetcode.cn/problems/happy-number/) · [官网讲解](https://programmercarl.com/algo/hash-table/0202-happy-number.html) · [官方Python区](https://programmercarl.com/algo/hash-table/0202-happy-number.html#python)

- 本题配套视频：本次已核验的官方题页未找到视频直链，不填造链接。

自主复习提示：把数字变换看作有限状态上的迭代，解释重复状态为何意味着无法到达 1；对比集合检测与快慢指针。


## 字符串

<a id="problem-344"></a>

### 344. 反转字符串

补充分类：字符串 · 官方难度：简单（[来源](https://leetcode.com/problems/reverse-string/)）

[力扣题目](https://leetcode.cn/problems/reverse-string/) · [官网讲解](https://programmercarl.com/algo/string/0344-reverse-string.html) · [官方Python区](https://programmercarl.com/algo/string/0344-reverse-string.html#python)

- 本题配套视频：[344. 反转字符串](https://www.bilibili.com/video/BV1fV4y17748)

自主复习提示：检查交换的停止条件与原地接口，说明切片写法是否额外创建线性大小的副本。

<a id="problem-151"></a>

### 151. 翻转字符串里的单词

补充分类：字符串 · 官方难度：中等（[来源](https://leetcode.com/problems/reverse-words-in-a-string/)）

[力扣题目](https://leetcode.cn/problems/reverse-words-in-a-string/) · [官网讲解](https://programmercarl.com/algo/string/0151-reverse-words-in-a-string.html) · [官方Python区](https://programmercarl.com/algo/string/0151-reverse-words-in-a-string.html#python)

- 本题配套视频：[151. 翻转字符串里的单词](https://www.bilibili.com/video/BV1uT41177fX)
- 相关题迁移视频：[27. 移除元素](https://www.bilibili.com/video/BV12A4y1Z7LP)。这条视频讲其他题，不计入本题直接视频覆盖。

自主复习提示：先明确多余空格如何规范化，再比较按词分割与逐字符压缩的空间代价。


## 栈与队列

<a id="problem-232"></a>

### 232. 用栈实现队列

补充分类：栈与队列 · 官方难度：简单（[来源](https://leetcode.com/problems/implement-queue-using-stacks/)）

[力扣题目](https://leetcode.cn/problems/implement-queue-using-stacks/) · [官网讲解](https://programmercarl.com/algo/stack-queue/0232-implement-queue-using-stacks.html) · [官方Python区](https://programmercarl.com/algo/stack-queue/0232-implement-queue-using-stacks.html#python)

- 本题配套视频：[232. 用栈实现队列](https://www.bilibili.com/video/BV1nY4y1w7VC)

自主复习提示：只有输出栈为空时才搬移输入栈；用一串 push、pop 和 peek 解释摊还复杂度。

<a id="problem-225"></a>

### 225. 用队列实现栈

补充分类：栈与队列 · 官方难度：简单（[来源](https://leetcode.com/problems/implement-stack-using-queues/)）

[力扣题目](https://leetcode.cn/problems/implement-stack-using-queues/) · [官网讲解](https://programmercarl.com/algo/stack-queue/0225-implement-stack-using-queues.html) · [官方Python区](https://programmercarl.com/algo/stack-queue/0225-implement-stack-using-queues.html#python)

- 本题配套视频：[225. 用队列实现栈](https://www.bilibili.com/video/BV1Fd4y1K7sm)

自主复习提示：每次入队后把新元素旋到队首，检查空结构边界与连续 push/pop 的顺序。
