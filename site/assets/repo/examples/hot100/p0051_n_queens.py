"""51 · N 皇后：原创教学实现。"""
class Solution:
    def solveNQueens(self, n):
        answer, placement = [], []
        columns, falling, rising = set(), set(), set()
        def search(row):
            if row == n:
                answer.append(["." * col + "Q" + "." * (n-col-1)
                               for col in placement])
                return
            for col in range(n):
                # 两族斜线分别具有固定的行列差、行列和。
                down, up = row - col, row + col
                if col in columns or down in falling or up in rising:
                    continue
                columns.add(col)
                falling.add(down)
                rising.add(up)
                placement.append(col)
                search(row + 1)
                # 撤销全部四处状态，下一候选从同一棋盘前缀出发。
                placement.pop()
                columns.remove(col)
                falling.remove(down)
                rising.remove(up)
        search(0)
        return answer
