# 二叉树：15题

树题先定义每次访问返回什么，以及答案是否允许同时使用左右分支。显式栈与队列避免Python递归深度限制；节点身份与节点值要区分。

## 本类题目

- [94. 二叉树的中序遍历](../problems/0094-binary-tree-inorder-traversal.md) · 简单 · 显式栈中序遍历
- [104. 二叉树的最大深度](../problems/0104-maximum-depth-of-binary-tree.md) · 简单 · DFS 求高度；BFS 或显式栈处理深树
- [226. 翻转二叉树](../problems/0226-invert-binary-tree.md) · 简单 · 主实现用显式栈交换左右子树；递归或队列是备选
- [101. 对称二叉树](../problems/0101-symmetric-tree.md) · 简单 · 成对比较镜像位置
- [543. 二叉树的直径](../problems/0543-diameter-of-binary-tree.md) · 简单 · 主实现用迭代后序和已存高度更新直径；递归返回高度是备选
- [102. 二叉树的层序遍历](../problems/0102-binary-tree-level-order-traversal.md) · 中等 · 队列按层 BFS
- [108. 将有序数组转换为二叉搜索树](../problems/0108-convert-sorted-array-to-binary-search-tree.md) · 简单 · 中点做根，递归处理左右区间
- [98. 验证二叉搜索树](../problems/0098-validate-binary-search-tree.md) · 中等 · 中序严格递增或上下界约束
- [230. 二叉搜索树中第 K 小的元素](../problems/0230-kth-smallest-element-in-a-bst.md) · 中等 · BST 中序遍历，计数到 k
- [199. 二叉树的右视图](../problems/0199-binary-tree-right-side-view.md) · 中等 · 按层 BFS 记录最右节点
- [114. 二叉树展开为链表](../problems/0114-flatten-binary-tree-to-linked-list.md) · 中等 · 逆先序遍历或原地寻找前驱重连
- [105. 从前序与中序遍历序列构造二叉树](../problems/0105-construct-binary-tree-from-preorder-and-inorder-traversal.md) · 中等 · 主实现用栈同步前序/中序进度；中序位置字典加递归切分是备选
- [437. 路径总和 III](../problems/0437-path-sum-iii.md) · 中等 · 根到当前的前缀和频次与回溯撤销
- [236. 二叉树的最近公共祖先](../problems/0236-lowest-common-ancestor-of-a-binary-tree.md) · 中等 · 主实现用父节点映射和祖先集合，辅助空间O(n)；后序递归汇总命中是备选
- [124. 二叉树中的最大路径和](../problems/0124-binary-tree-maximum-path-sum.md) · 困难 · 后序 DFS：向上仅返回单侧贡献，答案允许两侧

## 学完后自检

- 能说出每题结构里保存的是什么，而不只是背容器名称。
- 能解释每次丢弃候选、移动边界或改变状态为什么安全。
- 能写出最容易出错的最小输入，并说明预期输出。

[返回Hot100总导航](../README.md)
