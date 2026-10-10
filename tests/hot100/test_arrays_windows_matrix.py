"""21题：确定性边界 + 固定种子随机对拍；只依赖标准库。"""
import importlib
import itertools
import math
from pathlib import Path
import random
import unittest
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[2]
MODULES = {int(p.name[1:5]): 'examples.hot100.' + p.stem
           for p in (ROOT / 'examples/hot100').glob('p*.py')}


def solver(pid):
    return importlib.import_module(MODULES[pid]).Solution()


def canonical_groups(groups):
    return sorted(sorted(group) for group in groups)


class ArraysWindowsMatrixTests(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(20261009)

    def test_p0001(self):
        solve = solver(1).twoSum
        for nums, target in [([5, 5], 10), ([0, 0], 0), ([-3, 4, 6], 1), ([8, 1, 6, 4], 10)]:
            i, j = solve(nums, target)
            self.assertNotEqual(i, j)
            self.assertEqual(nums[i] + nums[j], target)
        for _ in range(300):
            nums = self.rng.choices(range(-5, 6), k=self.rng.randrange(2, 10))
            target = self.rng.randrange(-10, 11)
            pairs = [(i, j) for i in range(len(nums)) for j in range(i + 1, len(nums)) if nums[i] + nums[j] == target]
            result = solve(nums, target)
            if pairs:
                self.assertIn(tuple(sorted(result)), pairs)
            else:
                self.assertEqual(result, [])

    def test_p0049(self):
        solve = solver(49).groupAnagrams
        for words in [['', ''], ['ab', 'cab', 'ba', 'abc'], ['a', 'aa'], []] + [
            [''.join(self.rng.choices('abcd', k=self.rng.randrange(7))) for _ in range(8)] for _ in range(200)
        ]:
            expected = defaultdict(list)
            for word in words:
                expected[''.join(sorted(word))].append(word)
            self.assertEqual(canonical_groups(solve(words)), canonical_groups(expected.values()))

    def test_p0128(self):
        solve = solver(128).longestConsecutive
        for nums in [[], [1, 1], [-2, -1, 0], [12, 9, 3, 10, 11, 9]] + [
            self.rng.choices(range(-10, 11), k=self.rng.randrange(20)) for _ in range(300)
        ]:
            values = sorted(set(nums))
            best = run = 0
            for i, value in enumerate(values):
                run = run + 1 if i and value == values[i - 1] + 1 else 1
                best = max(best, run)
            self.assertEqual(solve(nums), best)

    def test_p0283(self):
        solve = solver(283).moveZeroes
        for nums in [[0], [1], [0, 0], [0, 4, 0, 2], []] + [
            self.rng.choices(range(-2, 3), k=self.rng.randrange(20)) for _ in range(300)
        ]:
            expected = [x for x in nums if x] + [0] * nums.count(0)
            identity = id(nums)
            self.assertIsNone(solve(nums))
            self.assertEqual(id(nums), identity)
            self.assertEqual(nums, expected)

    def test_p0011(self):
        solve = solver(11).maxArea
        for nums in [[0, 0], [2, 2], [2, 7, 3, 5]] + [
            self.rng.choices(range(8), k=self.rng.randrange(2, 14)) for _ in range(300)
        ]:
            expected = max((j - i) * min(nums[i], nums[j]) for i in range(len(nums)) for j in range(i + 1, len(nums)))
            self.assertEqual(solve(nums), expected)

    def test_p0015(self):
        solve = solver(15).threeSum
        for nums in [[0, 0, 0, 0], [1, 2, 3], [-3, 1, 2, 2, 0, -1]] + [
            self.rng.choices(range(-5, 6), k=self.rng.randrange(3, 12)) for _ in range(300)
        ]:
            before = nums[:]
            expected = {tuple(sorted(t)) for t in itertools.combinations(nums, 3) if sum(t) == 0}
            result = solve(nums)
            self.assertEqual({tuple(t) for t in result}, expected)
            self.assertEqual(len(result), len(expected))
            self.assertEqual(nums, before)

    def test_p0042(self):
        solve = solver(42).trap
        for nums in [[], [3], [1, 2, 3], [3, 2, 1], [3, 0, 1, 0, 2]] + [
            self.rng.choices(range(8), k=self.rng.randrange(20)) for _ in range(400)
        ]:
            expected = sum(min(max(nums[:i + 1]), max(nums[i:])) - x for i, x in enumerate(nums))
            self.assertEqual(solve(nums), expected)

    def test_p0003(self):
        solve = solver(3).lengthOfLongestSubstring
        for s in ['', 'abba', 'aaaa', 'dvdf', '你好你a'] + [
            ''.join(self.rng.choices('abc d', k=self.rng.randrange(15))) for _ in range(300)
        ]:
            expected = max([0] + [j - i for i in range(len(s)) for j in range(i + 1, len(s) + 1)
                                    if len(set(s[i:j])) == j - i])
            self.assertEqual(solve(s), expected)

        self.assertEqual(solve("abc " * 25000), 4)

    def test_p0438(self):
        solve = solver(438).findAnagrams
        for s, p in [('babaac', 'aab'), ('aa', 'aaaa'), ('aaaa', 'aa')] + [
            (''.join(self.rng.choices('abc', k=self.rng.randrange(1, 15))),
             ''.join(self.rng.choices('abc', k=self.rng.randrange(1, 6)))) for _ in range(300)
        ]:
            expected = [i for i in range(len(s) - len(p) + 1) if sorted(s[i:i + len(p)]) == sorted(p)]
            self.assertEqual(solve(s, p), expected)

    def test_p0560(self):
        solve = solver(560).subarraySum
        for nums, k in [([0, 0], 0), ([2, -1, 2], 3), ([-2, 1, 1], 0)] + [
            (self.rng.choices(range(-3, 4), k=self.rng.randrange(1, 14)), self.rng.randrange(-5, 6)) for _ in range(400)
        ]:
            expected = sum(sum(nums[i:j]) == k for i in range(len(nums)) for j in range(i + 1, len(nums) + 1))
            self.assertEqual(solve(nums, k), expected)

    def test_p0239(self):
        solve = solver(239).maxSlidingWindow
        for nums in [[5], [2, 2, 2], [1, 2, 3], [3, 2, 1], [4, 1, 3, 2]] + [
            self.rng.choices(range(-5, 6), k=self.rng.randrange(1, 18)) for _ in range(250)
        ]:
            for k in range(1, len(nums) + 1):
                self.assertEqual(solve(nums, k), [max(nums[i:i + k]) for i in range(len(nums) - k + 1)])

        self.assertEqual(solve(list(range(100000)), 50000), list(range(49999, 100000)))

    def test_p0076(self):
        solve = solver(76).minWindow
        for s, t in [('caxbaad', 'aab'), ('a', 'aa'), ('aa', 'aa'), ('xyz', 'a')] + [
            (''.join(self.rng.choices('abc', k=self.rng.randrange(1, 10))),
             ''.join(self.rng.choices('abc', k=self.rng.randrange(1, 5)))) for _ in range(300)
        ]:
            need = Counter(t)
            candidates = [s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1)
                          if not (need - Counter(s[i:j]))]
            expected_length = min(map(len, candidates), default=0)
            result = solve(s, t)
            self.assertEqual(len(result), expected_length)
            if expected_length:
                self.assertIn(result, candidates)
        self.assertEqual(solve('abc', ''), '')

    def test_p0053(self):
        solve = solver(53).maxSubArray
        for nums in [[-5], [-3, -1, -2], [-4, 3, -1, 5, -6]] + [
            self.rng.choices(range(-6, 7), k=self.rng.randrange(1, 15)) for _ in range(300)
        ]:
            expected = max(sum(nums[i:j]) for i in range(len(nums)) for j in range(i + 1, len(nums) + 1))
            self.assertEqual(solve(nums), expected)
        with self.assertRaises(ValueError):
            solve([])

    def test_p0056(self):
        solve = solver(56).merge
        def reference(intervals):
            work = [x[:] for x in intervals]
            while True:
                pair = next(((i, j) for i in range(len(work)) for j in range(i + 1, len(work))
                             if max(work[i][0], work[j][0]) <= min(work[i][1], work[j][1])), None)
                if pair is None:
                    return sorted(work)
                i, j = pair
                union = [min(work[i][0], work[j][0]), max(work[i][1], work[j][1])]
                work.pop(j)
                work.pop(i)
                work.append(union)
        for data in [[[5, 7], [1, 3], [3, 6], [9, 9]], [[1, 7], [2, 3]], []] + [
            [sorted(self.rng.choices(range(10), k=2)) for _ in range(self.rng.randrange(9))] for _ in range(250)
        ]:
            before = [x[:] for x in data]
            self.assertEqual(solve(data), reference(data))
            self.assertEqual(data, before)

    def test_p0189(self):
        solve = solver(189).rotate
        for nums in [[3], [1, 4, 7, 9, 2], []] + [
            self.rng.choices(range(8), k=self.rng.randrange(1, 15)) for _ in range(200)
        ]:
            for k in [0, 1, len(nums), len(nums) * 3 + 1]:
                data = nums[:]
                shift = k % len(nums) if nums else 0
                expected = nums[-shift:] + nums[:-shift] if shift else nums[:]
                self.assertIsNone(solve(data, k))
                self.assertEqual(data, expected)

    def test_p0238(self):
        solve = solver(238).productExceptSelf
        for nums in [[3, 2, 4], [0, 2], [0, 0, 2], [-2, 3]] + [
            self.rng.choices(range(-3, 4), k=self.rng.randrange(2, 10)) for _ in range(300)
        ]:
            expected = [math.prod(nums[:i] + nums[i + 1:]) for i in range(len(nums))]
            self.assertEqual(solve(nums), expected)

    def test_p0041(self):
        solve = solver(41).firstMissingPositive
        for nums in [[1, 1], [-3, -2], [1, 2, 3], [4, 1, -2, 2], [10**8]] + [
            self.rng.choices(range(-5, 16), k=self.rng.randrange(1, 20)) for _ in range(500)
        ]:
            expected = 1
            values = set(nums)
            while expected in values:
                expected += 1
            self.assertEqual(solve(nums[:]), expected)

        self.assertEqual(solve(list(range(100000, 0, -1))), 100001)

    def test_p0073(self):
        solve = solver(73).setZeroes
        for data in [[[0]], [[0, 1]], [[1], [0]], [[1, 2, 3], [4, 0, 6], [7, 8, 9]]] + [
            [[self.rng.randrange(4) for _ in range(cols)] for _ in range(rows)]
            for rows in range(1, 6) for cols in range(1, 6) for _ in range(10)
        ]:
            zero_rows = {i for i, row in enumerate(data) if 0 in row}
            zero_cols = {j for row in data for j, x in enumerate(row) if x == 0}
            expected = [[0 if i in zero_rows or j in zero_cols else x for j, x in enumerate(row)]
                        for i, row in enumerate(data)]
            self.assertIsNone(solve(data))
            self.assertEqual(data, expected)

    def test_p0054(self):
        solve = solver(54).spiralOrder
        def reference(a):
            rows, cols = len(a), len(a[0])
            seen, answer = set(), []
            row = col = direction = 0
            moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            for _ in range(rows * cols):
                answer.append(a[row][col])
                seen.add((row, col))
                dr, dc = moves[direction]
                nr, nc = row + dr, col + dc
                if not (0 <= nr < rows and 0 <= nc < cols) or (nr, nc) in seen:
                    direction = (direction + 1) % 4
                    dr, dc = moves[direction]
                row, col = row + dr, col + dc
            return answer
        for rows in range(1, 6):
            for cols in range(1, 6):
                data = [[i * cols + j for j in range(cols)] for i in range(rows)]
                self.assertEqual(solve(data), reference(data))
        self.assertEqual(solve([]), [])

    def test_p0048(self):
        solve = solver(48).rotate
        for n in range(1, 9):
            for _ in range(20):
                before = [self.rng.choices(range(10), k=n) for _ in range(n)]
                data = [row[:] for row in before]
                expected = [[before[n - 1 - col][row] for col in range(n)] for row in range(n)]
                self.assertIsNone(solve(data))
                self.assertEqual(data, expected)
                for _ in range(3):
                    solve(data)
                self.assertEqual(data, before)

    def test_p0240(self):
        solve = solver(240).searchMatrix
        for _ in range(300):
            rows, cols = self.rng.randrange(1, 8), self.rng.randrange(1, 8)
            a = [[0] * cols for _ in range(rows)]
            for i in range(rows):
                for j in range(cols):
                    a[i][j] = max(a[i - 1][j] if i else -8, a[i][j - 1] if j else -8) + self.rng.randrange(4)
            for target in [-10, 30, self.rng.randrange(-8, 25), a[0][0], a[-1][-1]]:
                self.assertEqual(solve(a, target), any(target in row for row in a))


if __name__ == '__main__':
    unittest.main()
