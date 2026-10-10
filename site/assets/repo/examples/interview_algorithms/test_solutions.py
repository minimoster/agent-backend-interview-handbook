"""Deterministic examples + randomized/brute-force references; standard library."""
import random
import unittest
from collections import Counter
from solutions import (Node, reverse_words_in_place, sort_odd_up_even_down,
                       add_decimal_strings, largest_below,
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
        self.assertEqual(largest_below(678,{1,4,7}),477)
        self.assertEqual(largest_below(1234,{1,2,3,4}),1233)
        self.assertEqual(largest_below(100,{0,1}),11)
        self.assertIsNone(largest_below(1,{0,1}))

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
