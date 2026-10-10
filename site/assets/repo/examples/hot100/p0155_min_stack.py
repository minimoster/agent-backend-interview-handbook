"""155 · 最小栈：原创教学实现。"""
class MinStack:
    def __init__(self):
        self._items = []

    def push(self, val: int) -> None:
        # 每层保存前缀最小值，弹出后自动恢复上一层状态。
        current_min = min(val, self._items[-1][1]) if self._items else val
        self._items.append((val, current_min))

    def pop(self) -> None:
        self._items.pop()

    def top(self) -> int:
        return self._items[-1][0]

    def getMin(self) -> int:
        return self._items[-1][1]
