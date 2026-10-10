"""Deterministic examples + randomized/brute-force references; standard library."""
import random
import sys
import unittest
from collections import Counter
from solutions import (Node, reverse_words_in_place, sort_odd_up_even_down,
                       add_decimal_strings, largest_below, largest_below_decimal,
                       remove_all_duplicate_values, are_anagrams)


def make(values):
    head = None
    for value in reversed(values):
        head = Node(value, head)
    return head


def read(head):
    out, seen = [], set()
    while head is not None:
        if id(head) in seen:
            raise AssertionError("cycle detected")
        seen.add(id(head)); out.append(head.value); head = head.next
    return out, seen


class Examples(unittest.TestCase):
    def test_reverse_words(self):
        for before, after in [("", ""), ("one", "one"), ("we build agents", "agents build we"),
                              ("a bb ccc", "ccc bb a")]:
            chars=list(before);original=id(chars);reverse_words_in_place(chars)
            self.assertEqual("".join(chars), after); self.assertEqual(id(chars), original)
        rng=random.Random(1)
        for _ in range(200):
            words=["a"*rng.randrange(1,8) for _ in range(rng.randrange(12))]
            chars=list(" ".join(words));reverse_words_in_place(chars)
            self.assertEqual("".join(chars)," ".join(reversed(words)))

    def test_odd_even_list(self):
        rng=random.Random(2)
        for n in range(50):
            for _ in range(20):
                odd=sorted(rng.randrange(-20,21) for _ in range((n+1)//2))
                even=sorted((rng.randrange(-20,21) for _ in range(n//2)),reverse=True)
                values=[]
                for i in range(n): values.append(odd[i//2] if i%2==0 else even[i//2])
                head=make(values);_,before_ids=read(head)
                actual,after_ids=read(sort_odd_up_even_down(head))
                self.assertEqual(actual,sorted(values));self.assertEqual(before_ids,after_ids)

    def test_big_addition(self):
        self.assertEqual(add_decimal_strings("999", "1"),"1000")
        self.assertEqual(add_decimal_strings("0000", "0"),"0")
        self.assertEqual(add_decimal_strings("0009", "001"),"10")
        rng=random.Random(3)
        for _ in range(1000):
            a=str(rng.randrange(10**100));b=str(rng.randrange(10**80))
            self.assertEqual(add_decimal_strings(a,b),str(int(a)+int(b)))
        for a,b in [("","1"),("1","-2"),("１","2"),("1.0","2")]:
            with self.assertRaises(ValueError):add_decimal_strings(a,b)

    def test_largest_below(self):
        for mask in range(32):
            digits={i for i in range(5) if mask & (1<<i)}
            for n in range(1,300):
                candidates=[x for x in range(1,n) if set(map(int,str(x)))<=digits]
                expected=max(candidates) if candidates else None
                self.assertEqual(largest_below(n,digits),expected,(n,digits))
                self.assertEqual(largest_below_decimal(str(n), digits),
                                 str(expected) if expected is not None else None, (n, digits))
        self.assertEqual(largest_below(678,{1,4,7}),477)
        self.assertEqual(largest_below(1234,{1,2,3,4}),1233)
        self.assertEqual(largest_below(100,{0,1}),11)
        self.assertIsNone(largest_below(1,{0,1}))
        # All 1,024 decimal-digit subsets and N=1..299; grow an independent
        # exhaustive candidate oracle instead of reusing the construction logic.
        for mask in range(1024):
            digits = {i for i in range(10) if mask & (1 << i)}
            expected = None
            for n in range(1, 300):
                candidate = n - 1
                if candidate > 0 and all(int(char) in digits for char in str(candidate)):
                    expected = candidate
                self.assertEqual(largest_below(n, digits), expected, (n, digits))
                self.assertEqual(largest_below_decimal(str(n), digits),
                                 str(expected) if expected is not None else None, (n, digits))

    def test_largest_below_decimal_huge(self):
        before_limit = sys.get_int_max_str_digits() if hasattr(sys, "get_int_max_str_digits") else None
        self.assertEqual(largest_below_decimal("1" + "0" * 5000, {0, 1}), "1" * 5000)
        self.assertEqual(largest_below_decimal("1" * 5000, {1}), "1" * 4999)
        self.assertEqual(largest_below_decimal("7" * 5000 + "6", {1, 4, 7}), "7" * 5000 + "4")
        self.assertEqual(largest_below_decimal("8" + "0" * 5000, {1, 4, 7}), "7" * 5001)
        self.assertEqual(largest_below_decimal("0" * 5000 + "100", {0, 1}), "11")
        self.assertIsNone(largest_below_decimal("9" * 5000, {0}))
        self.assertIsNone(largest_below_decimal("0" * 5000, {0, 1}))
        if before_limit:
            # Build via arithmetic, not decimal parsing; preserve the active security limit.
            with self.assertRaisesRegex(ValueError, "largest_below_decimal"):
                largest_below(10 ** before_limit, {1})
        if before_limit is not None:
            self.assertEqual(sys.get_int_max_str_digits(), before_limit)

    def test_largest_below_validation(self):
        for bound in ("", "-2", "1.0", " 2", "１", 12, None):
            with self.assertRaises(ValueError):
                largest_below_decimal(bound, {1})
        for digits in ({True}, {-1}, {10}, {1.0}, {"1"}):
            with self.assertRaises(ValueError):
                largest_below_decimal("123", digits)
            with self.assertRaises(ValueError):
                largest_below(123, digits)
        for bound in (True, 2.5, "123", None):
            with self.assertRaises(ValueError):
                largest_below(bound, {1})
        self.assertEqual(largest_below_decimal("00100", {0, 1}), "11")
        self.assertIsNone(largest_below_decimal("1", {1}))
        self.assertIsNone(largest_below_decimal("0", {1}))

    def test_remove_duplicates(self):
        rng=random.Random(4)
        for _ in range(1000):
            values=sorted(rng.randrange(-8,9) for _ in range(rng.randrange(40)))
            head=make(values);_,old_ids=read(head)
            actual,new_ids=read(remove_all_duplicate_values(head))
            counts=Counter(values)
            self.assertEqual(actual,[x for x in values if counts[x]==1]);self.assertTrue(new_ids<=old_ids)

    def test_anagrams(self):
        for a,b,answer in [("", "", True),("aab","aba",True),("aab","abb",False),
                           ("Ab","ba",False),("你好好","好你好",True),("é","e\u0301",False)]:
            self.assertEqual(are_anagrams(a,b),answer)
        rng=random.Random(5)
        for _ in range(1000):
            a="".join(rng.choices("abc你",k=rng.randrange(20)))
            b="".join(rng.choices("abc你",k=rng.randrange(20)))
            self.assertEqual(are_anagrams(a,b),Counter(a)==Counter(b))


if __name__ == "__main__":unittest.main(verbosity=2)
