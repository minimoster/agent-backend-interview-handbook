"""二分、栈、堆14题：边界用例和可复现随机对拍。"""
import bisect
from collections import Counter
import importlib
from pathlib import Path
import random
import statistics
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODULES = {int(p.name[1:5]): 'examples.hot100.' + p.stem for p in (ROOT / 'examples/hot100').glob('p*.py')}

def module(pid):
    return importlib.import_module(MODULES[pid])

class SearchStackHeapTests(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(78123)

    def test_p0035(self):
        solve = module(35).Solution().searchInsert
        for nums in [[1], [2, 5, 9, 12], []] + [sorted(self.rng.sample(range(-30, 31), self.rng.randrange(1, 25))) for _ in range(200)]:
            for target in range(-35, 36):
                self.assertEqual(solve(nums, target), bisect.bisect_left(nums, target))

    def test_p0074(self):
        solve = module(74).Solution().searchMatrix
        for rows in range(1, 6):
            for cols in range(1, 6):
                values = sorted(self.rng.sample(range(-100, 100), rows * cols))
                matrix = [values[i:i + cols] for i in range(0, len(values), cols)]
                for target in values + [-101, 101, 0]:
                    self.assertEqual(solve(matrix, target), target in values)
        self.assertFalse(solve([], 3))

    def test_p0034(self):
        solve = module(34).Solution().searchRange
        for nums in [[], [5], [2, 2, 2], [1, 4, 4, 4, 8]] + [sorted(self.rng.choices(range(-5, 6), k=self.rng.randrange(20))) for _ in range(200)]:
            for target in range(-7, 8):
                indices = [i for i, x in enumerate(nums) if x == target]
                expected = [indices[0], indices[-1]] if indices else [-1, -1]
                self.assertEqual(solve(nums, target), expected)

    def test_p0033(self):
        solve = module(33).Solution().search
        for _ in range(200):
            values = sorted(self.rng.sample(range(-20, 21), self.rng.randrange(1, 20)))
            for cut in range(len(values)):
                rotated = values[cut:] + values[:cut]
                for target in values + [-21, 21]:
                    expected = rotated.index(target) if target in rotated else -1
                    self.assertEqual(solve(rotated, target), expected)

    def test_p0153(self):
        solve = module(153).Solution().findMin
        for _ in range(200):
            values = sorted(self.rng.sample(range(-30, 31), self.rng.randrange(1, 25)))
            for cut in range(len(values)):
                rotated = values[cut:] + values[:cut]
                self.assertEqual(solve(rotated), min(values))
        with self.assertRaises(ValueError):
            solve([])

    def test_p0004(self):
        solve = module(4).Solution().findMedianSortedArrays
        for a, b in [([], [4]), ([4], []), ([2, 8], [1, 5, 9]), ([-2, -2], [-2, 3])] + [
            (sorted(self.rng.choices(range(-10, 11), k=self.rng.randrange(15))),
             sorted(self.rng.choices(range(-10, 11), k=self.rng.randrange(1, 15)))) for _ in range(400)
        ]:
            self.assertEqual(solve(a, b), statistics.median(a + b))
        with self.assertRaises(ValueError):
            solve([], [])

    def test_p0020(self):
        solve = module(20).Solution().isValid
        for text in ['', '(', ')', '{[()]}', '{[}]', '()[]{}'] + [
            ''.join(self.rng.choices('()[]{}', k=self.rng.randrange(20))) for _ in range(600)
        ]:
            reduced = text
            while True:
                after = reduced.replace('()', '').replace('[]', '').replace('{}', '')
                if after == reduced:
                    break
                reduced = after
            self.assertEqual(solve(text), not reduced)

    def test_p0155(self):
        cls = module(155).MinStack
        stack, ref = cls(), []
        for value in [4, 1, 1, 3, -2, -2]:
            stack.push(value)
            ref.append(value)
            self.assertEqual(stack.top(), ref[-1])
            self.assertEqual(stack.getMin(), min(ref))
        for _ in range(1200):
            if ref and self.rng.randrange(3) == 0:
                self.assertIsNone(stack.pop())
                ref.pop()
            else:
                value = self.rng.randrange(-20, 21)
                self.assertIsNone(stack.push(value))
                ref.append(value)
            if ref:
                self.assertEqual(stack.top(), ref[-1])
                self.assertEqual(stack.getMin(), min(ref))
        while ref:
            stack.pop()
            ref.pop()
        stack.push(9)
        self.assertEqual(stack.getMin(), 9)

    def test_p0394(self):
        solve = module(394).Solution().decodeString
        def reference(text):
            position = 0
            def parse():
                nonlocal position
                output = ''
                while position < len(text) and text[position] != ']':
                    if text[position].isdigit():
                        start = position
                        while text[position].isdigit():
                            position += 1
                        count = int(text[start:position])
                        position += 1  # [
                        block = parse()
                        position += 1  # ]
                        output += block * count
                    else:
                        output += text[position]
                        position += 1
                return output
            return parse()
        def generate(depth=0):
            parts = []
            for _ in range(self.rng.randrange(1, 4)):
                if depth < 2 and self.rng.randrange(3) == 0:
                    parts.append(f'{self.rng.randrange(1, 5)}[{generate(depth + 1)}]')
                else:
                    parts.append(self.rng.choice('abc'))
            return ''.join(parts)
        for text in ['2[a3[b]]', '12[z]', 'xy2[a]q', '1[x]'] + [generate() for _ in range(300)]:
            self.assertEqual(solve(text), reference(text))
        # 题设外深嵌套压力检查，验证迭代解析没有递归栈风险。
        self.assertEqual(solve('1[' * 1500 + 'x' + ']' * 1500), 'x')

    def test_p0739(self):
        solve = module(739).Solution().dailyTemperatures
        for nums in [[70], [70, 70], [70, 71, 72], [72, 71, 70], [68, 70, 69, 73]] + [
            self.rng.choices(range(30, 101), k=self.rng.randrange(1, 25)) for _ in range(400)
        ]:
            expected = [next((j - i for j in range(i + 1, len(nums)) if nums[j] > value), 0) for i, value in enumerate(nums)]
            self.assertEqual(solve(nums), expected)

    def test_p0084(self):
        solve = module(84).Solution().largestRectangleArea
        for nums in [[0], [4], [2, 2, 2], [1, 2, 3], [3, 2, 1], [2, 4, 3]] + [
            self.rng.choices(range(8), k=self.rng.randrange(1, 16)) for _ in range(400)
        ]:
            expected = max(min(nums[i:j]) * (j - i) for i in range(len(nums)) for j in range(i + 1, len(nums) + 1))
            self.assertEqual(solve(nums), expected)

        self.assertEqual(solve([1] * 100000), 100000)

    def test_p0215(self):
        solve = module(215).Solution()
        random.seed(90210)  # 主解的随机枢轴也固定，方便复现
        for nums in [[4], [3, 3, 3], [7, 2, 7, 4, 9], [-5, -2, -5]] + [
            self.rng.choices(range(-10, 11), k=self.rng.randrange(1, 30)) for _ in range(350)
        ]:
            before = nums[:]
            for k in range(1, len(nums) + 1):
                expected = sorted(nums)[-k]
                self.assertEqual(solve.findKthLargest(nums, k), expected)
                self.assertEqual(solve.findKthLargestHeap(nums, k), expected)
            self.assertEqual(nums, before)

        self.assertEqual(solve.findKthLargest([7] * 100000, 50000), 7)

    def test_p0347(self):
        solve = module(347).Solution().topKFrequent
        self.assertEqual(set(solve([4, 6, 4, 8, 6, 4], 2)), {4, 6})
        for _ in range(400):
            nums = self.rng.choices(range(-8, 9), k=self.rng.randrange(1, 50))
            counts = Counter(nums)
            k = self.rng.randrange(1, len(counts) + 1)
            result = solve(nums, k)
            self.assertEqual(len(result), k)
            self.assertEqual(len(set(result)), k)
            self.assertTrue(set(result) <= set(nums))
            for selected in result:
                for unselected in counts.keys() - set(result):
                    self.assertGreaterEqual(counts[selected], counts[unselected])

    def test_p0295(self):
        cls = module(295).MedianFinder
        for values in [[6, 2, 9], [-5, -5, 0, -1]] + [self.rng.choices(range(-100, 101), k=40) for _ in range(80)]:
            finder, prefix = cls(), []
            for value in values:
                self.assertIsNone(finder.addNum(value))
                prefix.append(value)
                self.assertEqual(finder.findMedian(), statistics.median(prefix))
                self.assertIn(len(finder.lower) - len(finder.upper), (0, 1))
                if finder.upper:
                    self.assertLessEqual(-finder.lower[0], finder.upper[0])
        with self.assertRaises(ValueError):
            cls().findMedian()

if __name__ == '__main__':
    unittest.main()
