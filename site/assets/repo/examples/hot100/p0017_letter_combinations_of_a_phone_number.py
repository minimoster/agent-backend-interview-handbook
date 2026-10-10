"""17 · 电话号码的字母组合：原创教学实现。"""
class Solution:
    def letterCombinations(self, digits):
        if not digits:
            return []
        mapping = {"2":"abc", "3":"def", "4":"ghi", "5":"jkl",
                   "6":"mno", "7":"pqrs", "8":"tuv", "9":"wxyz"}
        answer, path = [], []
        def search(index):
            if index == len(digits):
                answer.append("".join(path))
                return
            # 一层只对应一个按键，各位置的选择彼此独立。
            for char in mapping[digits[index]]:
                path.append(char)
                search(index + 1)
                path.pop()
        search(0)
        return answer
