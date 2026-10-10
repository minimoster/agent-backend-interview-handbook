"""79 · 单词搜索：原创教学实现。"""
class Solution:
    def exist(self, board, word):
        if not word:
            return True
        if not board or not board[0]:
            return False
        rows, cols = len(board), len(board[0])
        if len(word) > rows * cols:
            return False
        def search(r, c, index):
            if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != word[index]:
                return False
            if index == len(word) - 1:
                return True
            original = board[r][c]
            board[r][c] = None  # 输入是字符，None 可作当前路径标记
            found = (search(r-1, c, index+1) or search(r+1, c, index+1)
                     or search(r, c-1, index+1) or search(r, c+1, index+1))
            board[r][c] = original
            return found
        return any(search(r, c, 0) for r in range(rows) for c in range(cols))
