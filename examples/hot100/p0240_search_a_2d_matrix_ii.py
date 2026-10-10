"""240 · 搜索二维矩阵 II：原创教学实现。"""
class Solution:
    def searchMatrix(self, matrix: list[list[int]], target: int) -> bool:
        if not matrix or not matrix[0]:
            return False
        row, col = 0, len(matrix[0]) - 1
        while row < len(matrix) and col >= 0:
            value = matrix[row][col]
            if value == target:
                return True
            # 太大时本列下方更大，整列都可排除。
            if value > target:
                col -= 1
            else:
                row += 1
        return False
