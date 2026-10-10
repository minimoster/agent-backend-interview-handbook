"""74 · 搜索二维矩阵：原创教学实现。"""
class Solution:
    def searchMatrix(self, matrix: list[list[int]], target: int) -> bool:
        if not matrix or not matrix[0]:
            return False
        rows, cols = len(matrix), len(matrix[0])
        left, right = 0, rows * cols
        while left < right:
            middle = (left + right) // 2
            # 逻辑展平，不实际复制整个矩阵。
            value = matrix[middle // cols][middle % cols]
            if value < target:
                left = middle + 1
            else:
                right = middle
        return left < rows * cols and matrix[left // cols][left % cols] == target
