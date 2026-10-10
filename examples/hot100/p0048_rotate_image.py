"""48 · 旋转图像：原创教学实现。"""
class Solution:
    def rotate(self, matrix: list[list[int]]) -> None:
        n = len(matrix)
        for row in range(n):
            # 只交换对角线一侧，避免同一对称格交换两次。
            for col in range(row + 1, n):
                matrix[row][col], matrix[col][row] = matrix[col][row], matrix[row][col]
        for row in matrix:
            row.reverse()
