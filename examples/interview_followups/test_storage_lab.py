import itertools
import pathlib
import tempfile
import unittest

from storage_lab import Store, Inbox, SimulatedCrash, UnknownOutcome, OffsetPrefix, FencedValue, VersionFloorCache


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.store = Store()
        self.addCleanup(self.store.close)

    def test_success_has_effect_and_event(self):
        result = self.store.apply("tenant", "one", -3)
        self.assertEqual((result["quantity"], result["version"]), (97, 1))
        self.assertEqual(len(self.store.pending()), 1)

    def test_duplicate_returns_original_result(self):
        result = self.store.apply("t", "one", -3)
        self.store.apply("t", "two", -2)
        self.assertEqual(self.store.apply("t", "one", -3), result)
        self.assertEqual(self.store.quantity("t"), 95)

    def test_conflicting_parameters_rejected(self):
        self.store.apply("t", "one", -3)
        with self.assertRaises(ValueError): self.store.apply("t", "one", -4)
        self.assertEqual(self.store.quantity("t"), 97)

    def test_tenant_scope_is_distinct(self):
        a=self.store.apply("a", "same", -3); b=self.store.apply("b", "same", -4)
        self.assertNotEqual(a["event_id"], b["event_id"])

    def test_identity_encoding_is_unambiguous(self):
        a=self.store.apply("a:b", "c", 1); b=self.store.apply("a", "b:c", 1)
        self.assertNotEqual(a["event_id"], b["event_id"])

    def test_fault_after_effect_rolls_back(self):
        with self.assertRaises(SimulatedCrash): self.store.apply("t", "one", -3, "after_effect")
        self.assertIsNone(self.store.quantity("t")); self.assertEqual(self.store.pending(), [])
        self.assertEqual(self.store.apply("t", "one", -3)["version"], 1)

    def test_fault_after_event_rolls_back(self):
        with self.assertRaises(SimulatedCrash): self.store.apply("t", "one", -3, "after_event")
        self.assertIsNone(self.store.quantity("t")); self.assertEqual(self.store.pending(), [])

    def test_lost_reply_safe_retry(self):
        with self.assertRaises(UnknownOutcome): self.store.apply("t", "one", -3, "after_commit")
        self.assertEqual(self.store.apply("t", "one", -3)["quantity"], 97)
        self.assertEqual(len(self.store.pending()), 1)

    def test_committed_state_reopens(self):
        with tempfile.TemporaryDirectory() as directory:
            filename=str(pathlib.Path(directory)/"lab.sqlite")
            first=Store(filename)
            with self.assertRaises(UnknownOutcome): first.apply("t", "one", -3, "after_commit")
            first.close(); second=Store(filename)
            try: self.assertEqual(second.apply("t", "one", -3)["quantity"],97)
            finally: second.close()

    def test_inventory_cannot_go_negative(self):
        with self.assertRaises(ValueError): self.store.apply("t", "one", -101)
        self.assertIsNone(self.store.quantity("t"))

    def test_input_bounds_and_bool_rejected(self):
        for args in [("", "k", 1),("t", "k", True),("t", "k", 10**10),("t", "x"*257, 1)]:
            with self.subTest(args=args), self.assertRaises(ValueError): self.store.apply(*args)

    def test_outbox_mark_and_duplicate_delivery(self):
        inbox=Inbox(); self.addCleanup(inbox.close)
        event=self.store.apply("t", "one", -3)["event_id"]
        self.assertTrue(inbox.deliver(event,-3))
        self.assertEqual(len(self.store.pending()),1) # publisher crashed before mark
        self.assertFalse(inbox.deliver(event,-3)); self.assertEqual(inbox.value,-3)
        self.store.mark_sent(event); self.assertEqual(self.store.pending(),[])

    def test_inbox_rolls_back_effect_and_receipt(self):
        inbox=Inbox(); self.addCleanup(inbox.close)
        with self.assertRaises(SimulatedCrash): inbox.deliver("event",3,fail=True)
        self.assertEqual(inbox.value,0);self.assertTrue(inbox.deliver("event",3))
        self.assertEqual(inbox.value,3)

    def test_inbox_conflicting_identity(self):
        inbox=Inbox(); self.addCleanup(inbox.close);inbox.deliver("e",3)
        with self.assertRaises(ValueError): inbox.deliver("e",4)
        self.assertEqual(inbox.value,3)


class FrontierTests(unittest.TestCase):
    def test_gap_prevents_unsafe_commit(self):
        frontier=OffsetPrefix(100)
        self.assertEqual(frontier.complete(102),100)
        self.assertEqual(frontier.complete(100),101)
        self.assertEqual(frontier.complete(101),103)

    def test_every_small_completion_permutation(self):
        for order in itertools.permutations(range(5)):
            frontier=OffsetPrefix(); done=set()
            for offset in order:
                done.add(offset); expected=0
                while expected in done: expected+=1
                self.assertEqual(frontier.complete(offset),expected)

    def test_duplicate_and_old_completion(self):
        frontier=OffsetPrefix();self.assertEqual(frontier.complete(0),1)
        self.assertEqual(frontier.complete(0),1);self.assertEqual(frontier.completed,set())

    def test_pending_bound_and_gap_closure(self):
        frontier=OffsetPrefix(max_pending=1);frontier.complete(1)
        with self.assertRaises(OverflowError): frontier.complete(2)
        self.assertEqual(frontier.complete(0),2);self.assertEqual(frontier.complete(2),3)

    def test_invalid_offsets_and_bounds(self):
        for value in [-1,True,"0"]:
            with self.assertRaises(ValueError): OffsetPrefix().complete(value)
        with self.assertRaises(ValueError): OffsetPrefix(max_pending=0)


class FencingTests(unittest.TestCase):
    def test_paused_old_writer_rejected(self):
        sink=FencedValue();sink.write(41,"old");sink.write(42,"new")
        self.assertFalse(sink.write(41,"stale"));self.assertEqual(sink.value,"new")

    def test_same_operation_replay_has_one_effect(self):
        sink=FencedValue();self.assertTrue(sink.write(42,"new"));self.assertTrue(sink.write(42,"new"))
        self.assertEqual(sink.effects,1)

    def test_same_token_different_value_rejected(self):
        sink=FencedValue();sink.write(1,"a")
        with self.assertRaises(ValueError): sink.write(1,"b")

    def test_invalid_token(self):
        with self.assertRaises(ValueError): FencedValue().write(True,"value")


class CacheTests(unittest.TestCase):
    def test_inflight_stale_refill_rejected(self):
        cache=VersionFloorCache();cache.invalidate("doc",2)
        self.assertFalse(cache.put("doc",1,"old"));self.assertNotIn("doc",cache.entries)
        self.assertTrue(cache.put("doc",2,"new"))

    def test_out_of_order_invalidation_does_not_lower_floor(self):
        cache=VersionFloorCache();cache.put("doc",3,"latest");cache.invalidate("doc",2)
        self.assertEqual(cache.entries["doc"],(3,"latest"))

    def test_new_floor_removes_old_entry(self):
        cache=VersionFloorCache();cache.put("doc",1,"old");cache.invalidate("doc",2)
        self.assertNotIn("doc",cache.entries)

    def test_same_version_conflict(self):
        cache=VersionFloorCache();cache.put("doc",1,"a")
        with self.assertRaises(ValueError): cache.put("doc",1,"b")

    def test_floor_not_silently_evicted_when_full(self):
        cache=VersionFloorCache()
        for i in range(128): cache.invalidate(str(i),1)
        with self.assertRaises(OverflowError): cache.put("extra",1,"x")
        self.assertFalse(cache.put("0",0,"stale"))

    def test_invalid_payload_and_version(self):
        cache=VersionFloorCache()
        with self.assertRaises(ValueError): cache.put("key",1,"")
        with self.assertRaises(ValueError): cache.invalidate("key",-1)


if __name__ == "__main__":
    unittest.main()
