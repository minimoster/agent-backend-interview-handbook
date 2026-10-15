import copy
import unittest
from types import SimpleNamespace

from interview_build_forest import build_forest, zigzag_level_order


class BuildForestTests(unittest.TestCase):
    def test_zigzag_levels(self):
        def node(val, left=None, right=None):
            return SimpleNamespace(val=val, left=left, right=right)
        self.assertEqual(zigzag_level_order(None), [])
        self.assertEqual(zigzag_level_order(node(1)), [[1]])
        tree = node(3, node(9), node(20, node(15), node(7)))
        self.assertEqual(zigzag_level_order(tree), [[3], [20, 9], [15, 7]])
        chain = node(1, node(2, None, node(3)))
        self.assertEqual(zigzag_level_order(chain), [[1], [2], [3]])
        self.assertEqual(tree.left.val, 9)
        self.assertEqual(tree.right.left.val, 15)

    def test_empty(self):
        self.assertEqual(build_forest([]), [])

    def test_single_root(self):
        self.assertEqual(
            build_forest([{"id": "r", "parent_id": None}]),
            [{"id": "r", "parent_id": None, "children": []}],
        )

    def test_unordered_and_stable_and_no_mutation(self):
        rows = [
            {"id": "b", "parent_id": "r"},
            {"id": "c", "parent_id": "r"},
            {"id": "r", "parent_id": None},
            {"id": "a", "parent_id": "b"},
        ]
        original = copy.deepcopy(rows)
        forest = build_forest(iter(rows))
        self.assertEqual([x["id"] for x in forest], ["r"])
        self.assertEqual([x["id"] for x in forest[0]["children"]], ["b", "c"])
        self.assertEqual(forest[0]["children"][0]["children"][0]["id"], "a")
        self.assertEqual(rows, original)

    def test_multiple_roots(self):
        forest = build_forest([
            {"id": "second", "parent_id": None},
            {"id": "first", "parent_id": None},
        ])
        self.assertEqual([x["id"] for x in forest], ["second", "first"])

    def test_duplicate(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            build_forest([{"id": "a", "parent_id": None}] * 2)

    def test_missing_parent(self):
        with self.assertRaisesRegex(ValueError, "unknown parent"):
            build_forest([{"id": "a", "parent_id": "missing"}])

    def test_self_cycle(self):
        with self.assertRaisesRegex(ValueError, "cycle"):
            build_forest([{"id": "a", "parent_id": "a"}])

    def test_disconnected_cycle(self):
        with self.assertRaisesRegex(ValueError, "cycle"):
            build_forest([
                {"id": "root", "parent_id": None},
                {"id": "a", "parent_id": "b"},
                {"id": "b", "parent_id": "a"},
            ])

    def test_deep_chain(self):
        rows = [{"id": str(i), "parent_id": str(i-1) if i else None} for i in range(5000)]
        node = build_forest(reversed(rows))[0]
        count = 1
        while node["children"]:
            self.assertEqual(len(node["children"]), 1)
            node = node["children"][0]
            count += 1
        self.assertEqual(count, 5000)
        self.assertEqual(node["id"], "4999")

    def test_invalid_ids(self):
        for ident, parent in [("", None), (0, None), (None, None), ("a", ""), ("a", 0)]:
            with self.subTest(ident=ident, parent=parent):
                with self.assertRaises(ValueError):
                    build_forest([{"id": ident, "parent_id": parent}])


if __name__ == "__main__":
    unittest.main()
