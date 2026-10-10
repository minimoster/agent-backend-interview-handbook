"""贪心、DP与技巧24题：边界、原地契约和固定随机种子的独立对拍。"""
from collections import Counter, deque
from itertools import permutations
from math import comb, isqrt, prod
import importlib
from pathlib import Path
import random
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODULES = {
    int(path.name[1:5]): 'examples.hot100.' + path.stem
    for path in (ROOT / 'examples/hot100').glob('p*.py')
}


def solution(pid):
    return importlib.import_module(MODULES[pid]).Solution()


def jump_bfs(nums):
    """显式枚举跳跃边，与主解的区间贪心相互独立。"""
    queue = deque([(0, 0)])
    seen = {0}
    while queue:
        position, steps = queue.popleft()
        if position == len(nums) - 1:
            return steps
        for target in range(position + 1, min(len(nums), position + nums[position] + 1)):
            if target not in seen:
                seen.add(target)
                queue.append((target, steps + 1))
    return None


def minimum_summands(values, target):
    """从0出发的显式图BFS，每条边表示加一个正数。"""
    queue = deque([(0, 0)])
    seen = {0}
    while queue:
        current, steps = queue.popleft()
        if current == target:
            return steps
        for value in values:
            nxt = current + value
            if nxt <= target and nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, steps + 1))
    return -1


def subsequences(text):
    return {
        ''.join(char for index, char in enumerate(text) if mask & (1 << index))
        for mask in range(1 << len(text))
    }


def edit_bfs(source, target):
    """小字符串上直接枚举编辑操作，不使用编辑距离的表格转移。"""
    alphabet = set(source + target) or {'a'}
    max_length = max(len(source), len(target))
    queue = deque([(source, 0)])
    seen = {source}
    while queue:
        text, steps = queue.popleft()
        if text == target:
            return steps
        candidates = {text[:i] + text[i + 1:] for i in range(len(text))}
        candidates.update(
            text[:i] + char + text[i + 1:]
            for i in range(len(text)) for char in alphabet
        )
        if len(text) < max_length:
            candidates.update(
                text[:i] + char + text[i:]
                for i in range(len(text) + 1) for char in alphabet
            )
        for candidate in candidates - seen:
            seen.add(candidate)
            queue.append((candidate, steps + 1))
    raise AssertionError('完整的小规模编辑图应能抵达目标')


class GreedyDPTricksTests(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(24681357)

    def test_p0121(self):
        solve = solution(121).maxProfit
        cases = [[0], [9, 7, 3], [2, 2, 2], [8, 3, 6, 2, 7]]
        cases += [self.rng.choices(range(15), k=self.rng.randrange(1, 10)) for _ in range(160)]
        for nums in cases:
            expected = max([0] + [nums[j] - nums[i] for i in range(len(nums)) for j in range(i + 1, len(nums))])
            before = nums[:]
            self.assertEqual(solve(nums), expected, nums)
            self.assertEqual(nums, before)

    def test_p0055(self):
        solve = solution(55).canJump
        cases = [[0], [0, 1], [2, 0, 0], [1, 0, 2], [2, 0, 2, 0, 1]]
        cases += [self.rng.choices(range(5), k=self.rng.randrange(1, 13)) for _ in range(300)]
        for nums in cases:
            self.assertEqual(solve(nums), jump_bfs(nums) is not None, nums)
        self.assertTrue(solve([1] * 10000))

    def test_p0045(self):
        solve = solution(45).jump
        self.assertEqual(solve([0]), 0)
        self.assertEqual(solve([2, 2, 1, 1, 0]), 3)
        self.assertEqual(solve([9, 0, 0, 0]), 1)
        for _ in range(300):
            nums = self.rng.choices(range(6), k=self.rng.randrange(1, 15))
            expected = jump_bfs(nums)
            if expected is not None:  # 本题官方保证可达，不测试未定义扩展行为。
                self.assertEqual(solve(nums), expected, nums)
        self.assertEqual(solve([1] * 10000), 9999)

    def test_p0763(self):
        solve = solution(763).partitionLabels
        self.assertEqual(solve('abacddce'), [3, 4, 1])
        self.assertEqual(solve('z'), [1])
        self.assertEqual(solve('aaaa'), [4])
        for _ in range(120):
            text = ''.join(self.rng.choices('abcd', k=self.rng.randrange(1, 9)))
            best_count = 0
            for mask in range(1 << (len(text) - 1)):
                cuts = [0] + [i + 1 for i in range(len(text) - 1) if mask & (1 << i)] + [len(text)]
                seen = set()
                valid = True
                for left, right in zip(cuts, cuts[1:]):
                    chars = set(text[left:right])
                    if chars & seen:
                        valid = False
                        break
                    seen.update(chars)
                if valid:
                    best_count = max(best_count, len(cuts) - 1)
            result = solve(text)
            self.assertEqual(sum(result), len(text))
            self.assertTrue(all(length > 0 for length in result))
            self.assertEqual(len(result), best_count, text)
            seen = set()
            start = 0
            for length in result:
                chars = set(text[start:start + length])
                self.assertFalse(chars & seen)
                seen.update(chars)
                start += length

    def test_p0070(self):
        solve = solution(70).climbStairs
        # 按“两级步”的个数分组，用组合数独立计数。
        for n in range(1, 46):
            expected = sum(comb(n - doubles, doubles) for doubles in range(n // 2 + 1))
            self.assertEqual(solve(n), expected, n)

    def test_p0118(self):
        solve = solution(118).generate
        for count in range(1, 31):
            triangle = solve(count)
            expected = [[comb(row, column) for column in range(row + 1)] for row in range(count)]
            self.assertEqual(triangle, expected)
            self.assertEqual(len({id(row) for row in triangle}), count)
        result = solve(4)
        result[-1][0] = 99
        self.assertEqual(result[0], [1])

    def test_p0198(self):
        solve = solution(198).rob
        cases = [[0], [7], [2, 2], [4, 1, 2, 7, 3], [2, 1, 1, 2]]
        cases += [self.rng.choices(range(10), k=self.rng.randrange(1, 10)) for _ in range(130)]
        for nums in cases:
            expected = max(
                sum(value for index, value in enumerate(nums) if mask & (1 << index))
                for mask in range(1 << len(nums)) if not (mask & (mask << 1))
            )
            self.assertEqual(solve(nums), expected, nums)

    def test_p0279(self):
        solve = solution(279).numSquares
        for n in range(1, 121):
            squares = [root * root for root in range(1, isqrt(n) + 1)]
            self.assertEqual(solve(n), minimum_summands(squares, n), n)
        self.assertEqual(solve(10000), 1)
        self.assertEqual(solve(9999), 4)

    def test_p0322(self):
        solve = solution(322).coinChange
        cases = [([2], 0), ([2], 3), ([1, 3, 4], 6), ([2**31 - 1], 1), ([7], 14)]
        cases += [(self.rng.sample(range(1, 12), self.rng.randrange(1, 6)), self.rng.randrange(36)) for _ in range(150)]
        for coins, amount in cases:
            self.assertEqual(solve(coins, amount), minimum_summands(coins, amount), (coins, amount))

    def test_p0139(self):
        solve = solution(139).wordBreak
        self.assertTrue(solve('redbluered', ['red', 'blue']))
        self.assertTrue(solve('abcd', ['abc', 'ab', 'cd']))
        self.assertFalse(solve('ab', ['a']))
        self.assertTrue(solve('a', ['a']))
        self.assertFalse(solve('a' * 299 + 'b', ['a' * i for i in range(1, 21)]))
        words_pool = ['a', 'b', 'aa', 'ab', 'ba', 'bb', 'aaa', 'aab']
        for _ in range(150):
            text = ''.join(self.rng.choices('ab', k=self.rng.randrange(1, 9)))
            words = self.rng.sample(words_pool, self.rng.randrange(1, len(words_pool) + 1))
            def brute(remaining):
                if not remaining:
                    return True
                return any(remaining.startswith(word) and brute(remaining[len(word):]) for word in words)
            self.assertEqual(solve(text, words), brute(text), (text, words))

    def test_p0300(self):
        solve = solution(300).lengthOfLIS
        cases = [[1], [2, 2, 2], [5, 4, 3], [6, 2, 5, 3, 7, 4], [-3, -2, -1]]
        cases += [self.rng.choices(range(-4, 5), k=self.rng.randrange(1, 10)) for _ in range(130)]
        for nums in cases:
            expected = 0
            for mask in range(1 << len(nums)):
                seq = [value for i, value in enumerate(nums) if mask & (1 << i)]
                if all(a < b for a, b in zip(seq, seq[1:])):
                    expected = max(expected, len(seq))
            self.assertEqual(solve(nums), expected, nums)
        self.assertEqual(solve(list(range(2500))), 2500)

    def test_p0152(self):
        solve = solution(152).maxProduct
        cases = [[-3], [0], [-2, -3], [-2, 3, -4, 0, -1], [-1, -2, -3], [0, -1, 0]]
        cases += [self.rng.choices(range(-3, 4), k=self.rng.randrange(1, 10)) for _ in range(200)]
        for nums in cases:
            expected = max(prod(nums[left:right]) for left in range(len(nums)) for right in range(left + 1, len(nums) + 1))
            self.assertEqual(solve(nums), expected, nums)

    def test_p0416(self):
        solve = solution(416).canPartition
        cases = [[1], [1, 1], [1, 2, 5], [2, 3, 7, 8], [2, 2, 3, 5], [1, 2]]
        cases += [self.rng.choices(range(1, 10), k=self.rng.randrange(1, 10)) for _ in range(150)]
        for nums in cases:
            total = sum(nums)
            expected = total % 2 == 0 and any(
                2 * sum(value for i, value in enumerate(nums) if mask & (1 << i)) == total
                for mask in range(1 << len(nums))
            )
            self.assertEqual(solve(nums), expected, nums)
        self.assertTrue(solve([100] * 200))

    def test_p0032(self):
        solve = solution(32).longestValidParentheses
        cases = ['', '(', ')', '()(())', '())(())', '((((((', '))))))', '()()()']
        cases += [''.join(self.rng.choices('()', k=self.rng.randrange(15))) for _ in range(250)]
        for text in cases:
            expected = 0
            for left in range(len(text)):
                balance = 0
                for right in range(left, len(text)):
                    balance += 1 if text[right] == '(' else -1
                    if balance < 0:
                        break
                    if balance == 0:
                        expected = max(expected, right - left + 1)
            self.assertEqual(solve(text), expected, text)
        self.assertEqual(solve('()' * 15000), 30000)

    def test_p0062(self):
        solve = solution(62).uniquePaths
        for rows in range(1, 10):
            for columns in range(1, 10):
                self.assertEqual(solve(rows, columns), comb(rows + columns - 2, rows - 1))
        self.assertEqual(solve(1, 100), 1)
        self.assertEqual(solve(100, 1), 1)

    def test_p0064(self):
        solve = solution(64).minPathSum
        cases = [[[0]], [[7]], [[2, 1, 4], [3, 2, 1]], [[2, 3, 4]], [[2], [3], [4]]]
        for _ in range(100):
            rows, columns = self.rng.randrange(1, 5), self.rng.randrange(1, 5)
            cases.append([self.rng.choices(range(8), k=columns) for _ in range(rows)])
        for grid in cases:
            before = [row[:] for row in grid]
            def path_costs(row, column, cost):
                cost += grid[row][column]
                if row == len(grid) - 1 and column == len(grid[0]) - 1:
                    return [cost]
                result = []
                if row + 1 < len(grid):
                    result += path_costs(row + 1, column, cost)
                if column + 1 < len(grid[0]):
                    result += path_costs(row, column + 1, cost)
                return result
            self.assertEqual(solve(grid), min(path_costs(0, 0, 0)))
            self.assertIsInstance(solve(grid), int)
            self.assertEqual(grid, before)

    def test_p0005(self):
        solve = solution(5).longestPalindrome
        cases = ['a', 'aa', 'ab', 'xaabac', 'abacdc', 'aaaaa', 'aAa']
        cases += [''.join(self.rng.choices('abc', k=self.rng.randrange(1, 13))) for _ in range(200)]
        for text in cases:
            expected_length = max(
                right - left for left in range(len(text)) for right in range(left + 1, len(text) + 1)
                if text[left:right] == text[left:right][::-1]
            )
            result = solve(text)
            self.assertEqual(len(result), expected_length, text)
            self.assertEqual(result, result[::-1])
            self.assertIn(result, text)
        self.assertEqual(solve('a' * 1000), 'a' * 1000)

    def test_p1143(self):
        solve = solution(1143).longestCommonSubsequence
        cases = [('a', 'a'), ('a', 'b'), ('axby', 'aby'), ('aaaa', 'aa'), ('ab', 'ba')]
        cases += [
            (''.join(self.rng.choices('abc', k=self.rng.randrange(1, 8))),
             ''.join(self.rng.choices('abc', k=self.rng.randrange(1, 8)))) for _ in range(130)
        ]
        for first, second in cases:
            expected = max(map(len, subsequences(first) & subsequences(second)))
            self.assertEqual(solve(first, second), expected, (first, second))
            self.assertEqual(solve(second, first), expected)
        # 扩展行为：官方输入非空，通用实现同时支持空串。
        self.assertEqual(solve('', 'abc'), 0)

    def test_p0072(self):
        solve = solution(72).minDistance
        cases = [('', ''), ('abc', ''), ('', 'abc'), ('ab', 'ba'), ('aaa', 'bbb'), ('a', 'a')]
        cases += [
            (''.join(self.rng.choices('ab', k=self.rng.randrange(4))),
             ''.join(self.rng.choices('ab', k=self.rng.randrange(4)))) for _ in range(80)
        ]
        for first, second in cases:
            expected = edit_bfs(first, second)
            self.assertEqual(solve(first, second), expected, (first, second))
            self.assertEqual(solve(second, first), expected)
        self.assertEqual(solve('cat', 'cut'), 1)
        self.assertEqual(solve('a' * 500, ''), 500)

    def test_p0136(self):
        solve = solution(136).singleNumber
        for unique in [0, -3, 7]:
            self.assertEqual(solve([unique]), unique)
        for _ in range(160):
            values = self.rng.sample(range(-100, 101), self.rng.randrange(1, 20))
            unique = values.pop()
            nums = [unique] + values * 2
            self.rng.shuffle(nums)
            expected = next(value for value, count in Counter(nums).items() if count == 1)
            self.assertEqual(solve(nums), expected)

    def test_p0169(self):
        solve = solution(169).majorityElement
        self.assertEqual(solve([0]), 0)
        self.assertEqual(solve([5, 2, 5, 3, 5, 5, 2]), 5)
        for _ in range(200):
            size = self.rng.randrange(1, 40)
            majority = self.rng.randrange(-5, 6)
            count = self.rng.randrange(size // 2 + 1, size + 1)
            others = [value for value in range(-5, 6) if value != majority]
            nums = [majority] * count + self.rng.choices(others, k=size - count)
            self.rng.shuffle(nums)
            expected = Counter(nums).most_common(1)[0][0]
            self.assertEqual(solve(nums), expected)

    def test_p0075(self):
        solve = solution(75).sortColors
        cases = [[0], [1], [2], [2, 0, 1], [1, 2, 0, 1, 0], [2] * 8, [0] * 8]
        cases += [self.rng.choices(range(3), k=self.rng.randrange(1, 100)) for _ in range(200)]
        for nums in cases:
            expected = sorted(nums)
            alias = nums
            self.assertIsNone(solve(nums))
            self.assertIs(nums, alias)
            self.assertEqual(alias, expected)

    def test_p0031(self):
        solve = solution(31).nextPermutation
        cases = [[1], [2, 2], [3, 2, 1], [1, 1, 2], [1, 4, 3, 3, 2]]
        cases += [self.rng.choices(range(4), k=self.rng.randrange(1, 7)) for _ in range(120)]
        for nums in cases:
            ordered = sorted(set(permutations(nums)))
            position = ordered.index(tuple(nums))
            expected = list(ordered[(position + 1) % len(ordered)])
            alias = nums
            self.assertIsNone(solve(nums))
            self.assertIs(nums, alias)
            self.assertEqual(alias, expected)

    def test_p0287(self):
        solve = solution(287).findDuplicate
        cases = [[1, 1], [2, 2, 2], [2, 4, 1, 3, 1], [3, 3, 3, 3, 3]]
        for _ in range(200):
            n = self.rng.randrange(1, 80)
            duplicate = self.rng.randrange(1, n + 1)
            repeats = self.rng.randrange(2, n + 2)
            others = [value for value in range(1, n + 1) if value != duplicate]
            nums = [duplicate] * repeats + self.rng.sample(others, n + 1 - repeats)
            self.rng.shuffle(nums)
            cases.append(nums)
        for nums in cases:
            expected = next(value for value, count in Counter(nums).items() if count > 1)
            before = nums[:]
            self.assertEqual(solve(nums), expected, nums)
            self.assertEqual(nums, before)
        nums = list(range(1, 100001)) + [1]
        before = nums[:]
        self.assertEqual(solve(nums), 1)
        self.assertEqual(nums, before)


if __name__ == '__main__':
    unittest.main()
