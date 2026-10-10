"""118 · 杨辉三角：原创教学实现。"""
class Solution:
    def generate(self, numRows: int) -> list[list[int]]:
        triangle = []
        for row_index in range(numRows):
            row = [1] * (row_index + 1)  # 每行独立，两端保持为 1。
            for column in range(1, row_index):
                row[column] = (
                    triangle[-1][column - 1] + triangle[-1][column]
                )
            triangle.append(row)
        return triangle
