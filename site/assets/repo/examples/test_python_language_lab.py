import copy
import inspect
import unittest
from unittest.mock import patch
from python_language_lab import (Account, Counter, Created, Factory, Renderer,
    TextRenderer, append_name, first_even, make_counter, odd_only, render_any,
    retry_timeout, square_stream, timer)

class LanguageTests(unittest.TestCase):
    def test_containers_and_hashability(self):
        self.assertEqual(list({"a": 1, "b": 2}), ["a", "b"])
        self.assertEqual({1, 1, 2}, {1, 2})
        self.assertEqual({("a", 1): "ok"}[("a", 1)], "ok")
        with self.assertRaises(TypeError):
            hash(([],))

    def test_mutation_and_rebinding(self):
        outer = [1]
        alias = outer
        outer.append(2)
        self.assertEqual(alias, [1, 2])
        outer = [3]
        self.assertEqual(alias, [1, 2])

    def test_loop_control(self):
        self.assertEqual(first_even([1, 3, 4, 6]), 4)
        self.assertIsNone(first_even([1, 3]))
        self.assertEqual(odd_only([1, 2, 3, 4]), [1, 3])

    def test_generator_is_lazy(self):
        seen = []
        def source():
            seen.append("started")
            yield 3
            seen.append("resumed")
            yield 4
        stream = square_stream(source())
        self.assertEqual(seen, [])
        self.assertEqual(next(stream), 9)
        self.assertEqual(seen, ["started"])
        self.assertEqual(list(stream), [16])
        self.assertEqual(seen, ["started", "resumed"])
        self.assertEqual(list(stream), [])

    def test_generator_return(self):
        def stream():
            yield 1
            return 7
        it = stream()
        self.assertEqual(next(it), 1)
        with self.assertRaises(StopIteration) as caught:
            next(it)
        self.assertEqual(caught.exception.value, 7)

    def test_copy(self):
        original = [[1]]
        shallow = copy.copy(original)
        deep = copy.deepcopy(original)
        shallow[0].append(2)
        self.assertEqual(original, [[1, 2]])
        self.assertEqual(deep, [[1]])
        self.assertIsNot(shallow, original)

    def test_range_not_iterator(self):
        seq = range(1, 5)
        self.assertEqual(list(seq), [1, 2, 3, 4])
        self.assertEqual(list(seq), [1, 2, 3, 4])
        with self.assertRaises(TypeError):
            next(seq)

    def test_equality_identity(self):
        left, right = [1], [1]
        self.assertEqual(left, right)
        self.assertIsNot(left, right)
        self.assertIs(left, left)

    def test_lambda(self):
        self.assertEqual(sorted(["bbb", "a", "cc"], key=lambda x: len(x)),
                         ["a", "cc", "bbb"])
        self.assertEqual((lambda x: x if x >= 0 else -x)(-2), 2)

    def test_string_splitting(self):
        self.assertEqual(" a  b ".split(), ["a", "b"])
        self.assertEqual("a  b".split(" "), ["a", "", "b"])
        self.assertEqual("x=y=z".partition("="), ("x", "=", "y=z"))
        self.assertEqual("a:b:c".rsplit(":", 1), ["a:b", "c"])
        self.assertEqual("a\r\nb\nc".splitlines(), ["a", "b", "c"])

    def test_docstring_position(self):
        def f():
            """A real docstring."""
            return "x"
        self.assertEqual(inspect.getdoc(f), "A real docstring.")

    def test_default_not_shared(self):
        self.assertEqual(append_name("a"), ["a"])
        self.assertEqual(append_name("b"), ["b"])
        existing = []
        self.assertIs(append_name("c", existing), existing)

    def test_decorator_preserves_metadata(self):
        records = []
        @timer(lambda *row: records.append(row))
        def add(a, b):
            """Add two values."""
            return a + b
        with patch("python_language_lab.time.perf_counter", side_effect=[1., 1.25]):
            self.assertEqual(add(2, 3), 5)
        self.assertEqual(records, [("add", 0.25)])
        self.assertEqual(add.__name__, "add")
        self.assertEqual(add.__doc__, "Add two values.")

    def test_retry_only_selected_error(self):
        calls, sleeps = [], []
        @retry_timeout(max_attempts=2, sleep=sleeps.append)
        def flaky():
            calls.append(1)
            if len(calls) == 1:
                raise TimeoutError("temporary")
            return 9
        self.assertEqual(flaky(), 9)
        self.assertEqual(sleeps, [0.1])
        @retry_timeout(max_attempts=3, sleep=sleeps.append)
        def permanent():
            raise ValueError("bad input")
        with self.assertRaises(ValueError):
            permanent()
        self.assertEqual(sleeps, [0.1])

    def test_retry_exhaustion_keeps_error(self):
        error = TimeoutError("still down")
        @retry_timeout(max_attempts=2, sleep=lambda _: None)
        def unavailable():
            raise error
        with self.assertRaises(TimeoutError) as caught:
            unavailable()
        self.assertIs(caught.exception, error)

    def test_nonlocal_and_retained_state(self):
        counter = make_counter()
        self.assertEqual([counter(), counter()], [1, 2])
        values = []
        def append_without_rebinding():
            values.append(3)
        append_without_rebinding()
        self.assertEqual(values, [3])

    def test_compile_reports_syntax_error(self):
        with self.assertRaises(SyntaxError):
            compile("if:", "<lab>", "exec")

    def test_new_then_init(self):
        events = []
        Created(events)
        self.assertEqual(events, ["new", "init"])
        self.assertEqual(Factory(), {"different_type": True})

    def test_self_state_is_per_instance(self):
        a, b = Counter("a"), Counter("b")
        self.assertEqual(a.increment(), 1)
        self.assertEqual(a.read(), 1)
        self.assertEqual(b.read(), 0)
        self.assertEqual(a.name, "a")
        self.assertEqual(Counter.category, "teaching")

    def test_name_mangling_not_security(self):
        account = Account()
        account.deposit(10)
        self.assertEqual(account.balance, 10)
        self.assertEqual(account._Account__balance, 10)
        with self.assertRaises(ValueError):
            account.deposit(-1)

    def test_abc_and_duck_typing(self):
        with self.assertRaises(TypeError):
            Renderer()
        class Unrelated:
            def render(self):
                return "duck"
        self.assertEqual(render_any(TextRenderer()), "text")
        self.assertEqual(render_any(Unrelated()), "duck")

    def test_mro(self):
        class Root:
            def label(self): return "root"
        class Left(Root):
            def label(self): return "left>" + super().label()
        class Right(Root):
            def label(self): return "right>" + super().label()
        class Child(Left, Right): pass
        self.assertEqual(Child().label(), "left>right>root")

class NumpyTests(unittest.TestCase):
    def test_vector_view_and_advanced_copy(self):
        import numpy as np
        a = np.array([1, 2, 3, 4])
        self.assertEqual((a * 2).tolist(), [2, 4, 6, 8])
        view = a[::2]
        self.assertFalse(view.flags.c_contiguous)
        view[0] = 9
        self.assertEqual(a[0], 9)
        advanced = a[[0, 2]]
        advanced[0] = 0
        self.assertEqual(a[0], 9)

if __name__ == "__main__":
    unittest.main()
