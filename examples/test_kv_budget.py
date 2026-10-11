import unittest
from kv_budget import kv_bytes

class KVTests(unittest.TestCase):
    def setUp(self):
        self.args = dict(batch=1, tokens=4096, layers=32, kv_heads=8,
                         head_dim=128, bytes_per_element=2)

    def test_example(self):
        self.assertEqual(kv_bytes(**self.args), 536870912)

    def test_linear_batch(self):
        self.assertEqual(kv_bytes(**(self.args | {"batch": 8})), 4 * 2**30)

    def test_invalid_dimensions(self):
        for name in self.args:
            for invalid in (0, -1, 1.5, True):
                with self.subTest(name=name, value=invalid):
                    with self.assertRaises(ValueError):
                        kv_bytes(**(self.args | {name: invalid}))

if __name__ == "__main__":
    unittest.main()
