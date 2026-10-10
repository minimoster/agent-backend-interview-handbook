# 二分查找：6题

二分查找依赖单调判断。半开区间与闭区间不能混用；旋转数组每轮找有序的一半，中位数题把搜索对象从数值改为分割位置。

## 本类题目

- [35. 搜索插入位置](../problems/0035-search-insert-position.md) · 简单 · 半开区间 lower_bound
- [74. 搜索二维矩阵](../problems/0074-search-a-2d-matrix.md) · 中等 · 视作有序一维数组后二分
- [34. 在排序数组中查找元素的第一个和最后一个位置](../problems/0034-find-first-and-last-position-of-element-in-sorted-array.md) · 中等 · 两次二分寻找左右边界
- [33. 搜索旋转排序数组](../problems/0033-search-in-rotated-sorted-array.md) · 中等 · 二分判断哪半边有序
- [153. 寻找旋转排序数组中的最小值](../problems/0153-find-minimum-in-rotated-sorted-array.md) · 中等 · 二分比较中点和右端点
- [4. 寻找两个正序数组的中位数](../problems/0004-median-of-two-sorted-arrays.md) · 困难 · 较短数组上二分分割位置

## 学完后自检

- 能说出每题结构里保存的是什么，而不只是背容器名称。
- 能解释每次丢弃候选、移动边界或改变状态为什么安全。
- 能写出最容易出错的最小输入，并说明预期输出。

[返回Hot100总导航](../README.md)
