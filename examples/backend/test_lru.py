"""Differential tests; OrderedDict is used only as an independent oracle."""
from collections import OrderedDict
import random
import unittest
from lru import LRU


class LruTests(unittest.TestCase):
    def test_sample_and_zero_capacity(self):
        cache = LRU(2)
        cache.put("A", 1)
        cache.put("B", 2)
        self.assertEqual(cache.get("A"), 1)
        cache.put("C", 3)
        self.assertIsNone(cache.get("B"))
        cache.put("A", 7)
        self.assertEqual(cache.get("A"), 7)
        self.assertEqual(len(cache.nodes), 2)
        zero = LRU(0)
        zero.put("A", 1)
        self.assertEqual(zero.get("A", "missing"), "missing")

    def test_negative_capacity(self):
        with self.assertRaises(ValueError):
            LRU(-1)

    def test_random_and_pointer_invariants(self):
        operations = 0
        for capacity in range(6):
            for seed in range(10):
                rng = random.Random(seed)
                cache, reference = LRU(capacity), OrderedDict()
                for _ in range(500):
                    key = rng.randrange(9)
                    if rng.randrange(2):
                        value = rng.randrange(100)
                        cache.put(key, value)
                        if capacity:
                            reference[key] = value
                            reference.move_to_end(key, last=False)
                            if len(reference) > capacity:
                                reference.popitem(last=True)
                    else:
                        expected = reference.get(key)
                        if key in reference:
                            reference.move_to_end(key, last=False)
                        self.assertEqual(cache.get(key), expected)
                    actual = []
                    node, previous = cache.head.next, cache.head
                    while node is not cache.tail:
                        self.assertIs(node.prev, previous)
                        actual.append((node.key, node.value))
                        previous, node = node, node.next
                        self.assertLessEqual(len(actual), capacity)
                    self.assertIs(node.prev, previous)
                    self.assertEqual(actual, list(reference.items()))
                    self.assertEqual(set(cache.nodes), set(reference))
                    operations += 1
        self.assertEqual(operations, 30000)


if __name__ == "__main__":
    unittest.main()
