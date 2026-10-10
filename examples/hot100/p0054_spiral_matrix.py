"""54 · 螺旋矩阵：原创教学实现。"""
class Solution:
    def spiralOrder(self, matrix: list[list[int]]) -> list[int]:
        if not matrix or not matrix[0]:
            return []
        top, bottom = 0, len(matrix) - 1
        left, right = 0, len(matrix[0]) - 1
        answer = []
        while top <= bottom and left <= right:
            for col in range(left, right + 1):
                answer.append(matrix[top][col])
            top += 1
            for row in range(top, bottom + 1):
                answer.append(matrix[row][right])
            right -= 1
            # 最内层可能已没有下边，不能重复读取剩余单行。
            if top <= bottom:
                for col in range(right, left - 1, -1):
                    answer.append(matrix[bottom][col])
                bottom -= 1
            if left <= right:
                for row in range(bottom, top - 1, -1):
                    answer.append(matrix[row][left])
                left += 1
        return answer
