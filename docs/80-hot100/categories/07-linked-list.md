# 链表：14题

链表操作先画引用关系，再断开旧边。值相等不代表同一个节点；dummy统一头部边界，快慢指针表达距离或环结构。

## 本类题目

- [160. 相交链表](../problems/0160-intersection-of-two-linked-lists.md) · 简单 · 双指针分别走完两条链表
- [206. 反转链表](../problems/0206-reverse-linked-list.md) · 简单 · 前驱、当前、后继三指针迭代翻转
- [234. 回文链表](../problems/0234-palindrome-linked-list.md) · 简单 · 快慢指针找中点、翻转后半段、比较后恢复
- [141. 环形链表](../problems/0141-linked-list-cycle.md) · 简单 · Floyd 快慢指针判环
- [142. 环形链表 II](../problems/0142-linked-list-cycle-ii.md) · 中等 · Floyd 相遇后重置一个指针找入口
- [21. 合并两个有序链表](../problems/0021-merge-two-sorted-lists.md) · 简单 · 哑节点加尾指针迭代归并
- [2. 两数相加](../problems/0002-add-two-numbers.md) · 中等 · 哑节点、逐位相加与进位
- [19. 删除链表的倒数第 N 个结点](../problems/0019-remove-nth-node-from-end-of-list.md) · 中等 · 哑节点与相隔 n 步的双指针
- [24. 两两交换链表中的节点](../problems/0024-swap-nodes-in-pairs.md) · 中等 · 哑节点，每次重连两个节点
- [25. K 个一组翻转链表](../problems/0025-reverse-nodes-in-k-group.md) · 困难 · 哑节点，先确认组长，再反转半开区间
- [138. 随机链表的复制](../problems/0138-copy-list-with-random-pointer.md) · 中等 · 旧节点到新节点的哈希映射；交织节点作进阶
- [148. 排序链表](../problems/0148-sort-list.md) · 中等 · 归并排序；自底向上版本可降辅助空间
- [23. 合并 K 个升序链表](../problems/0023-merge-k-sorted-lists.md) · 困难 · 小根堆合并 k 条有序链表
- [146. LRU 缓存](../problems/0146-lru-cache.md) · 中等 · 字典与带哨兵的双向链表

## 学完后自检

- 能说出每题结构里保存的是什么，而不只是背容器名称。
- 能解释每次丢弃候选、移动边界或改变状态为什么安全。
- 能写出最容易出错的最小输入，并说明预期输出。

[返回Hot100总导航](../README.md)
