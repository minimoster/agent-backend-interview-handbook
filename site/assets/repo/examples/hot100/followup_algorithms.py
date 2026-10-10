"""Original follow-ups for LC53 and LC295; main Hot100 interfaces stay separate.

Median examples use the official integer domain -100000..100000. Empty queries
and invalid inputs raise ValueError. No class silently clamps or drops a rank.
"""
from bisect import insort


def maximum_subarray_summary(nums: list[int]) -> tuple[int, int, int, int]:
    """Return (total, best nonempty prefix, suffix, subarray), without mutation.

    Balanced index intervals avoid slices. O(n) arithmetic operations and
    O(log n) stack space, assuming bounded-cost integer arithmetic.
    """
    if not nums:
        raise ValueError("nums must be nonempty")

    def visit(start: int, stop: int) -> tuple[int, int, int, int]:
        if stop - start == 1:
            value = nums[start]
            return value, value, value, value
        middle = (start + stop) // 2
        lt, lp, ls, lb = visit(start, middle)
        rt, rp, rs, rb = visit(middle, stop)
        # A crossing subarray is a nonempty left suffix plus right prefix.
        return (lt + rt, max(lp, lt + rp), max(rs, rt + ls),
                max(lb, rb, ls + rp))

    return visit(0, len(nums))


def max_subarray_divide_conquer(nums: list[int]) -> int:
    """The fourth summary field is the maximum nonempty subarray sum."""
    return maximum_subarray_summary(nums)[3]


def _validate_num(num: int) -> None:
    if type(num) is not int or not -100000 <= num <= 100000:
        raise ValueError("num must be an integer in -100000..100000")


def _middle_ranks(size: int) -> tuple[int, int]:
    if size == 0:
        raise ValueError("no values added")
    # One-based ranks; identical for an odd-size data set.
    return (size + 1) // 2, (size + 2) // 2


def _select_band(frequencies: list[int], rank: int) -> int:
    if rank < 1:
        raise ValueError("median rank outside [0, 100]; retain exact outliers")
    for value, count in enumerate(frequencies):
        rank -= count
        if rank <= 0:
            return value
    raise ValueError("median rank outside [0, 100]; retain exact outliers")


class BoundedMedianFinder:
    """All inputs in [0,100]; add O(1), query O(101), 101 frequency counters."""
    def __init__(self):
        self.frequencies = [0] * 101
        self.size = 0

    def addNum(self, num: int) -> None:
        _validate_num(num)
        if not 0 <= num <= 100:
            raise ValueError("num must be in 0..100")
        self.frequencies[num] += 1
        self.size += 1

    def findMedian(self) -> float:
        first, second = _middle_ranks(self.size)
        return (_select_band(self.frequencies, first)
                + _select_band(self.frequencies, second)) / 2


class BandCountMedianFinder:
    """Store band frequencies and outlier counts, not individual outlier values.

    Exact only when both central ranks lie in the band. At least 99% in-band
    at every query suffices. Otherwise an outside central rank raises ValueError.
    Add O(1), query O(101), fixed counter count under the usual word model.
    """
    def __init__(self):
        self.frequencies = [0] * 101
        self.below = self.above = self.size = 0

    def addNum(self, num: int) -> None:
        _validate_num(num)
        if num < 0:
            self.below += 1
        elif num > 100:
            self.above += 1
        else:
            self.frequencies[num] += 1
        self.size += 1

    def findMedian(self) -> float:
        first, second = _middle_ranks(self.size)
        # Below-band values precede every frequency-table entry.
        return (_select_band(self.frequencies, first - self.below)
                + _select_band(self.frequencies, second - self.below)) / 2


class ExactPrefixMedianFinder:
    """Exact on every prefix, including outlier-heavy prefixes of a 99% stream.

    Sorted outlier lists preserve rank information. In-band add O(1), outlier
    add O(k+1) for shifting k existing outliers, query O(101), space O(101+k).
    This simple reference favors checkability over logarithmic outlier insertion.
    """
    def __init__(self):
        self.frequencies = [0] * 101
        self.lower_outliers = []
        self.upper_outliers = []
        self.size = 0

    def addNum(self, num: int) -> None:
        _validate_num(num)
        if num < 0:
            insort(self.lower_outliers, num)
        elif num > 100:
            insort(self.upper_outliers, num)
        else:
            self.frequencies[num] += 1
        self.size += 1

    def _select(self, rank: int) -> int:
        if rank <= len(self.lower_outliers):
            return self.lower_outliers[rank - 1]
        band_size = self.size - len(self.lower_outliers) - len(self.upper_outliers)
        rank -= len(self.lower_outliers)
        if rank <= band_size:
            return _select_band(self.frequencies, rank)
        return self.upper_outliers[rank - band_size - 1]

    def findMedian(self) -> float:
        first, second = _middle_ranks(self.size)
        return (self._select(first) + self._select(second)) / 2
