import concurrent.futures
from fractions import Fraction
from pathlib import Path
import struct
import tempfile
import threading
import unittest

from interview_lab import (
    rrf, VersionedDocuments, VersionConflict, IdempotentInventory,
    IdempotencyConflict, InsufficientStock, InjectedFailure, LostReply,
    FrameDecoder, FrameError, encode_frame,
)


class RRFTests(unittest.TestCase):
    def test_exact_fusion(self):
        fused = dict(rrf([["A", "B"], ["B", "C"]], k=0))
        self.assertEqual(fused, {"A": Fraction(1), "B": Fraction(3, 2), "C": Fraction(1, 2)})

    def test_duplicate_policy(self):
        self.assertEqual(rrf([["A", "A", "B"]]), rrf([["A", "B"]]))

    def test_deterministic_tie(self):
        self.assertEqual([item[0] for item in rrf([["B"], ["A"]])], ["A", "B"])

    def test_empty_lists(self):
        self.assertEqual(rrf([[], []]), [])

    def test_invalid_k(self):
        for k in (-1, True, 1.5, None):
            with self.subTest(k=k), self.assertRaises(ValueError):
                rrf([["A"]], k=k)

    def test_invalid_id(self):
        for doc_id in ("", None, 5):
            with self.subTest(doc_id=doc_id), self.assertRaises(ValueError):
                rrf([[doc_id]])


class DocumentTests(unittest.TestCase):
    def setUp(self):
        self.docs = VersionedDocuments()
        self.docs.create("tenant-A", "doc", "old")

    def test_version_advances(self):
        snapshot = self.docs.update("tenant-A", "doc", 1, "new")
        self.assertEqual((snapshot.version, snapshot.content), (2, "new"))

    def test_old_snapshot_cannot_overwrite(self):
        old = self.docs.read("tenant-A", "doc")
        self.docs.update("tenant-A", "doc", old.version, "newer")
        with self.assertRaises(VersionConflict):
            self.docs.update("tenant-A", "doc", old.version, "stale")
        self.assertEqual(self.docs.read("tenant-A", "doc").content, "newer")

    def test_storage_partition_not_auth(self):
        self.docs.create("tenant-B", "doc", "B")
        self.docs.update("tenant-B", "doc", 1, "B2")
        self.assertEqual(self.docs.read("tenant-A", "doc").content, "old")

    def test_version_type_validation(self):
        for version in (True, 1.0, 0, -1, "1", None):
            with self.subTest(version=version), self.assertRaises(ValueError):
                self.docs.update("tenant-A", "doc", version, "wrong")
        self.assertEqual(self.docs.read("tenant-A", "doc").version, 1)

    def test_only_one_concurrent_writer_wins(self):
        barrier = threading.Barrier(2)
        def writer(content):
            barrier.wait(timeout=5)
            try:
                self.docs.update("tenant-A", "doc", 1, content)
                return "success"
            except VersionConflict:
                return "conflict"
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(writer, ("one", "two")))
        self.assertCountEqual(outcomes, ["success", "conflict"])
        self.assertEqual(self.docs.read("tenant-A", "doc").version, 2)


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.inventory = IdempotentInventory()
        self.inventory.seed("A", "book", 10)

    def tearDown(self):
        self.inventory.close()

    def test_same_key_replays_same_result(self):
        first = self.inventory.purchase("A", "request-1", "book", 2)
        second = self.inventory.purchase("A", "request-1", "book", 2)
        self.assertEqual(first, second)
        self.assertEqual(self.inventory.remaining("A", "book"), 8)
        self.assertEqual(self.inventory.order_count("A"), 1)

    def test_same_key_different_parameters_conflict(self):
        self.inventory.purchase("A", "request-1", "book", 2)
        with self.assertRaises(IdempotencyConflict):
            self.inventory.purchase("A", "request-1", "book", 3)
        self.assertEqual(self.inventory.remaining("A", "book"), 8)

    def test_different_keys_are_distinct_intentions(self):
        self.inventory.purchase("A", "request-1", "book", 2)
        self.inventory.purchase("A", "request-2", "book", 2)
        self.assertEqual(self.inventory.remaining("A", "book"), 6)
        self.assertEqual(self.inventory.order_count("A"), 2)

    def test_failure_rolls_back_business_and_dedup(self):
        with self.assertRaises(InjectedFailure):
            self.inventory.purchase("A", "request-1", "book", 2, fault="after_business_before_commit")
        self.assertEqual(self.inventory.remaining("A", "book"), 10)
        self.assertEqual(self.inventory.order_count("A"), 0)
        self.inventory.purchase("A", "request-1", "book", 2)
        self.assertEqual(self.inventory.remaining("A", "book"), 8)

    def test_lost_reply_is_not_failed_effect(self):
        with self.assertRaises(LostReply):
            self.inventory.purchase("A", "request-1", "book", 2, fault="after_commit_lost_reply")
        result = self.inventory.purchase("A", "request-1", "book", 2)
        self.assertEqual(result["status"], "done")
        self.assertEqual(self.inventory.remaining("A", "book"), 8)
        self.assertEqual(self.inventory.order_count("A"), 1)

    def test_no_oversell(self):
        with self.assertRaises(InsufficientStock):
            self.inventory.purchase("A", "request-1", "book", 11)
        self.assertEqual(self.inventory.remaining("A", "book"), 10)
        self.assertEqual(self.inventory.order_count("A"), 0)

    def test_rejected_request_does_not_bind_key_in_this_model(self):
        with self.assertRaises(InsufficientStock):
            self.inventory.purchase("A", "request-1", "book", 11)
        self.inventory.purchase("A", "request-1", "book", 2)
        self.assertEqual(self.inventory.remaining("A", "book"), 8)

    def test_rolled_back_request_does_not_bind_key_in_this_model(self):
        with self.assertRaises(InjectedFailure):
            self.inventory.purchase("A", "request-1", "book", 2, fault="after_business_before_commit")
        self.inventory.purchase("A", "request-1", "book", 3)
        self.assertEqual(self.inventory.remaining("A", "book"), 7)

    def test_tenant_key_partition(self):
        self.inventory.seed("B", "book", 10)
        self.inventory.purchase("A", "same-key", "book", 2)
        self.inventory.purchase("B", "same-key", "book", 3)
        self.assertEqual(self.inventory.remaining("A", "book"), 8)
        self.assertEqual(self.inventory.remaining("B", "book"), 7)

    def test_invalid_quantity(self):
        for units in (0, -1, True, 1.5):
            with self.subTest(units=units), self.assertRaises(ValueError):
                self.inventory.purchase("A", "request-1", "book", units)

    def test_persistence_across_connection_reopen(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "lab.sqlite")
            first = IdempotentInventory(path)
            first.seed("A", "book", 10)
            first.purchase("A", "key", "book", 2)
            first.close()
            reopened = IdempotentInventory(path)
            try:
                reopened.purchase("A", "key", "book", 2)
                self.assertEqual(reopened.remaining("A", "book"), 8)
                self.assertEqual(reopened.order_count("A"), 1)
            finally:
                reopened.close()

    def test_concurrent_connections_same_key(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "lab.sqlite")
            initial = IdempotentInventory(path)
            initial.seed("A", "book", 10)
            initial.close()
            barrier = threading.Barrier(2)
            def purchase(_):
                connection = IdempotentInventory(path)
                try:
                    barrier.wait(timeout=5)
                    return connection.purchase("A", "key", "book", 2)
                finally:
                    connection.close()
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                outcomes = list(pool.map(purchase, range(2)))
            self.assertEqual(outcomes[0], outcomes[1])
            check = IdempotentInventory(path)
            try:
                self.assertEqual(check.remaining("A", "book"), 8)
                self.assertEqual(check.order_count("A"), 1)
            finally:
                check.close()

    def test_concurrent_distinct_keys_cannot_oversell(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "lab.sqlite")
            initial = IdempotentInventory(path)
            initial.seed("A", "book", 1)
            initial.close()
            barrier = threading.Barrier(2)
            def purchase(key):
                connection = IdempotentInventory(path)
                try:
                    barrier.wait(timeout=5)
                    try:
                        connection.purchase("A", key, "book", 1)
                        return "success"
                    except InsufficientStock:
                        return "insufficient"
                finally:
                    connection.close()
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                outcomes = list(pool.map(purchase, ("key-one", "key-two")))
            self.assertCountEqual(outcomes, ["success", "insufficient"])
            check = IdempotentInventory(path)
            try:
                self.assertEqual(check.remaining("A", "book"), 0)
                self.assertEqual(check.order_count("A"), 1)
            finally:
                check.close()


class FrameTests(unittest.TestCase):
    def test_split_header_and_payload(self):
        encoded = encode_frame(b"abc")
        decoder = FrameDecoder()
        self.assertEqual(decoder.feed(encoded[:2]), [])
        self.assertEqual(decoder.feed(encoded[2:5]), [])
        self.assertEqual(decoder.feed(encoded[5:]), [b"abc"])
        decoder.eof()

    def test_multiple_frames(self):
        decoder = FrameDecoder()
        self.assertEqual(decoder.feed(encode_frame(b"one") + encode_frame(b"two")), [b"one", b"two"])

    def test_utf8_split_is_kept_as_bytes(self):
        payload = "面试".encode("utf-8")
        encoded = encode_frame(payload)
        decoder = FrameDecoder()
        self.assertEqual(decoder.feed(encoded[:5]), [])
        frames = decoder.feed(encoded[5:])
        self.assertEqual(frames[0].decode("utf-8"), "面试")

    def test_empty_message_is_explicit_frame(self):
        decoder = FrameDecoder()
        self.assertEqual(decoder.feed(encode_frame(b"")), [b""])
        self.assertEqual(decoder.feed(b""), [])
        decoder.eof()

    def test_large_declaration_poisoned(self):
        decoder = FrameDecoder(max_frame=10)
        with self.assertRaises(FrameError):
            decoder.feed(struct.pack("!I", 11))
        with self.assertRaises(FrameError):
            decoder.feed(encode_frame(b"ok"))

    def test_eof_truncation(self):
        decoder = FrameDecoder()
        decoder.feed(encode_frame(b"hello")[:-1])
        with self.assertRaises(FrameError):
            decoder.eof()

    def test_chunk_bound(self):
        decoder = FrameDecoder(max_chunk=4)
        with self.assertRaises(FrameError):
            decoder.feed(b"x" * 5)

    def test_all_split_positions(self):
        stream = encode_frame(b"a") + encode_frame("字".encode("utf-8")) + encode_frame(b"")
        for split in range(len(stream) + 1):
            with self.subTest(split=split):
                decoder = FrameDecoder()
                frames = decoder.feed(stream[:split]) + decoder.feed(stream[split:])
                self.assertEqual(frames, [b"a", "字".encode("utf-8"), b""])
                decoder.eof()

    def test_valid_prefix_before_bad_header_independent_of_split(self):
        stream = encode_frame(b"valid") + struct.pack("!I", 100)
        for split in range(len(stream) + 1):
            with self.subTest(split=split):
                decoder = FrameDecoder(max_frame=10)
                frames = []
                raised = False
                for chunk in (stream[:split], stream[split:]):
                    try:
                        frames.extend(decoder.feed(chunk))
                    except FrameError as error:
                        frames.extend(error.completed_frames)
                        raised = True
                        break
                self.assertTrue(raised)
                self.assertEqual(frames, [b"valid"])
                self.assertTrue(decoder.failed)


if __name__ == "__main__":
    unittest.main()
