"""Adversarial finite-contract tests, not provider/A2A interoperability tests."""
import unittest
from dataclasses import replace

from agent_protocol_lab import (
    Artifact, ContractError, Limits, PreparedCall, TaskEvent, TaskMonitor,
    TaskSnapshot, ToolAssembler, ToolEvent, from_a2a_state, strict_object,
    validate_lookup,
)


class TaskTests(unittest.TestCase):
    def monitor(self, **kwargs):
        return TaskMonitor(TaskSnapshot("task-1", "ctx-1", 0, "submitted"),
                           deadline=10, **kwargs)

    def status(self, revision, state, **kwargs):
        return TaskEvent("task-1", "ctx-1", revision, "status", state=state, **kwargs)

    def artifact(self, revision, text, **kwargs):
        return TaskEvent("task-1", "ctx-1", revision, "artifact", artifact_id="report", text=text, **kwargs)

    def test_v1_state_conversion_and_unspecified_rejection(self):
        self.assertEqual(from_a2a_state("TASK_STATE_INPUT_REQUIRED"), "input-required")
        for value in ("TASK_STATE_UNSPECIFIED", "input-required", "TASK_STATE_CANCELLED", None):
            with self.subTest(value=value), self.assertRaises(ContractError):
                from_a2a_state(value)

    def test_interruption_is_not_terminal_and_can_continue(self):
        m = self.monitor()
        for revision, state in enumerate(["working", "input-required", "working", "auth-required", "working", "completed"], 1):
            m.apply(self.status(revision, state), now=1)
            if state.endswith("required"):
                m.continuation("task-1", "ctx-1")
        with self.assertRaises(ContractError):
            m.continuation("task-1", "ctx-1")

    def test_terminal_task_never_restarts(self):
        for terminal in ("completed", "failed", "canceled", "rejected"):
            with self.subTest(terminal=terminal):
                m = self.monitor()
                m.apply(self.status(1, terminal), now=1)
                with self.assertRaises(ContractError):
                    m.apply(self.status(2, "working"), now=1)
                self.assertEqual(m.snapshot.state, terminal)
                self.assertFalse(m.synchronized)

    def test_cancel_request_can_lose_to_completion(self):
        m = self.monitor()
        m.request_cancel()
        self.assertEqual(m.snapshot.state, "submitted")
        m.apply(self.status(1, "completed"), now=1)
        self.assertEqual(m.snapshot.state, "completed")
        with self.assertRaises(ContractError):
            m.request_cancel()

    def test_cancel_acknowledgment_is_distinct(self):
        m = self.monitor()
        m.request_cancel()
        m.apply(self.status(1, "canceled"), now=1)
        self.assertEqual(m.snapshot.state, "canceled")

    def test_artifact_append_replace_and_last_chunk_not_task_done(self):
        m = self.monitor()
        m.apply(self.artifact(1, "draft"), now=1)
        m.apply(self.artifact(2, "v2"), now=1)
        m.apply(self.artifact(3, "!", append=True, last_chunk=True), now=1)
        self.assertEqual(m.snapshot.artifacts, (Artifact("report", "v2!", True),))
        self.assertEqual(m.snapshot.state, "submitted")
        with self.assertRaises(ContractError):
            m.apply(self.artifact(4, "late", append=True), now=1)

    def test_append_without_base_rejected(self):
        m = self.monitor()
        with self.assertRaises(ContractError):
            m.apply(self.artifact(1, "tail", append=True), now=1)
        self.assertEqual(m.snapshot.revision, 0)

    def test_exact_duplicate_does_not_append_twice(self):
        m = self.monitor()
        base = self.artifact(1, "a")
        tail = self.artifact(2, "b", append=True)
        self.assertTrue(m.apply(base, now=1))
        self.assertTrue(m.apply(tail, now=1))
        self.assertFalse(m.apply(tail, now=1))
        self.assertEqual(m.snapshot.artifacts[0].text, "ab")

    def test_conflicting_duplicate_poison_sync_without_mutation(self):
        m = self.monitor()
        m.apply(self.status(1, "working"), now=1)
        with self.assertRaises(ContractError):
            m.apply(self.status(1, "completed"), now=1)
        self.assertEqual(m.snapshot.state, "working")
        self.assertFalse(m.synchronized)

    def test_gap_requires_snapshot_and_uses_current_full_artifact(self):
        m = self.monitor()
        m.apply(self.artifact(1, "a"), now=1)
        with self.assertRaises(ContractError):
            m.apply(self.artifact(3, "c", append=True), now=1)
        m.install_snapshot(TaskSnapshot("task-1", "ctx-1", 3, "working", (Artifact("report", "abc"),)), now=2)
        m.apply(self.artifact(4, "d", append=True), now=2)
        self.assertEqual(m.snapshot.artifacts[0].text, "abcd")

    def test_disconnect_preserves_remote_last_known_state(self):
        m = self.monitor()
        m.apply(self.status(1, "working"), now=1)
        m.disconnect()
        self.assertEqual(m.snapshot.state, "working")
        with self.assertRaises(ContractError):
            m.apply(self.status(2, "completed"), now=1)
        m.install_snapshot(TaskSnapshot("task-1", "ctx-1", 2, "completed"), now=2)
        self.assertEqual(m.snapshot.state, "completed")

    def test_same_revision_authoritative_snapshot_can_reconnect(self):
        m = self.monitor()
        m.apply(self.status(1, "working"), now=1)
        saved = m.snapshot
        m.disconnect()
        m.install_snapshot(saved, now=2)
        self.assertTrue(m.synchronized)
        self.assertEqual(m.snapshot, saved)
        m.apply(self.status(2, "completed"), now=2)
        self.assertEqual(m.snapshot.state, "completed")

    def test_authoritative_snapshot_rebuilds_nonterminal_artifact_projection(self):
        m = self.monitor()
        m.apply(self.artifact(1, "old", last_chunk=True), now=1)
        m.disconnect()
        m.install_snapshot(TaskSnapshot("task-1", "ctx-1", 2, "working",
                                       (Artifact("report", "new", False),)), now=2)
        m.apply(self.artifact(3, "!", append=True, last_chunk=True), now=2)
        self.assertEqual(m.snapshot.artifacts, (Artifact("report", "new!", True),))
        m.apply(self.status(4, "completed"), now=2)
        with self.assertRaises(ContractError):
            m.install_snapshot(TaskSnapshot("task-1", "ctx-1", 5, "completed",
                                           (Artifact("report", "changed", True),)), now=2)
        self.assertEqual(m.snapshot.artifacts[0].text, "new!")

    def test_snapshot_cannot_go_back_or_conflict(self):
        for bad in [TaskSnapshot("task-1", "ctx-1", 0, "working"),
                    TaskSnapshot("task-1", "ctx-1", 1, "submitted"),
                    TaskSnapshot("other", "ctx-1", 2, "working")]:
            with self.subTest(bad=bad):
                m = self.monitor()
                m.apply(self.status(1, "working"), now=1)
                with self.assertRaises(ContractError):
                    m.install_snapshot(bad, now=1)

    def test_cross_context_and_post_terminal_artifact_rejected(self):
        m = self.monitor()
        with self.assertRaises(ContractError):
            m.apply(replace(self.status(1, "working"), context_id="other"), now=1)
        m = self.monitor()
        m.apply(self.status(1, "completed"), now=1)
        with self.assertRaises(ContractError):
            m.apply(self.artifact(2, "late"), now=1)

    def test_artifact_count_and_utf8_total_bounds(self):
        m = self.monitor(limits=Limits(max_artifact_bytes=4, max_total_artifact_bytes=4, max_artifacts=1))
        m.apply(self.artifact(1, "😀"), now=1)
        with self.assertRaises(ContractError):
            m.apply(self.artifact(2, "a", append=True), now=1)
        self.assertEqual(m.snapshot.artifacts[0].text, "😀")
        m = self.monitor(limits=Limits(max_artifacts=1))
        m.apply(self.artifact(1, "a"), now=1)
        with self.assertRaises(ContractError):
            m.apply(replace(self.artifact(2, "b"), artifact_id="second"), now=1)

    def test_snapshot_duplicate_artifact_ids_and_bad_flags_rejected(self):
        with self.assertRaises(ContractError):
            TaskMonitor(TaskSnapshot("t", "c", 0, "working", (Artifact("a", "1"), Artifact("a", "2"))), deadline=10)
        m = self.monitor()
        with self.assertRaises(ContractError):
            m.apply(replace(self.artifact(1, "x"), append=1), now=1)

    def test_task_deadline_and_duplicate_work_are_bounded(self):
        m = self.monitor()
        with self.assertRaises(ContractError):
            m.apply(self.status(1, "working"), now=10)
        m = self.monitor(limits=Limits(max_events=3)) # initial snapshot costs 1
        e = self.status(1, "working")
        m.apply(e, now=1)
        self.assertFalse(m.apply(e, now=1))
        with self.assertRaises(ContractError):
            m.apply(e, now=1)


class ToolTests(unittest.TestCase):
    def assembler(self, **kwargs):
        return ToolAssembler("request-1", deadline=10, **kwargs)

    def e(self, sequence, kind, key="a", **kwargs):
        return ToolEvent("request-1", sequence, kind, call_key=key, **kwargs)

    def feed_one(self, a, raw, *, finish=True):
        a.apply(self.e(0, "start", call_id="call-a", name="lookup_doc"), now=1)
        a.apply(self.e(1, "delta", payload=raw), now=1)
        a.apply(self.e(2, "stop"), now=1)
        if finish:
            a.apply(self.e(3, "finish", key="", status="completed"), now=1)

    def test_every_two_part_json_split_and_escaped_braces(self):
        raw = '{"document_id":"文档😀{\\\"x}\\u4e2d", "limit":2}'
        for point in range(len(raw) + 1):
            with self.subTest(point=point):
                a = self.assembler()
                a.apply(self.e(0, "start", call_id="call-a", name="lookup_doc"), now=1)
                a.apply(self.e(1, "delta", payload=raw[:point]), now=1)
                with self.assertRaises(ContractError):
                    a.calls()
                a.apply(self.e(2, "delta", payload=raw[point:]), now=1)
                a.apply(self.e(3, "stop", payload=raw), now=1)
                a.apply(self.e(4, "finish", key="", status="completed"), now=1)
                self.assertEqual(a.calls()[0].arguments["limit"], 2)

    def test_interleaved_calls_keep_identity_and_out_of_order_stop(self):
        a = self.assembler()
        events = [self.e(0, "start", call_id="call-a", name="lookup_doc"),
                  self.e(1, "start", key="b", call_id="call-b", name="lookup_doc"),
                  self.e(2, "delta", payload='{"document_id":"A",'),
                  self.e(3, "delta", key="b", payload='{"document_id":"B","limit":1}'),
                  self.e(4, "stop", key="b"),
                  self.e(5, "delta", payload='"limit":2}'),
                  self.e(6, "stop"),
                  self.e(7, "finish", key="", status="completed")]
        for event in events:
            a.apply(event, now=1)
        self.assertEqual([(c.call_id, c.arguments["document_id"]) for c in a.calls()], [("call-a", "A"), ("call-b", "B")])

    def test_partial_json_can_be_buffered_but_not_finalized(self):
        a = self.assembler()
        a.apply(self.e(0, "start", call_id="call-a", name="lookup_doc"), now=1)
        a.apply(self.e(1, "delta", payload='{"document_id":'), now=1)
        with self.assertRaises(ContractError):
            a.apply(self.e(2, "stop"), now=1)
        self.assertEqual(a.phase, "failed")
        with self.assertRaises(ContractError):
            a.calls()

    def test_syntactically_complete_delta_is_still_not_committed(self):
        a = self.assembler()
        self.feed_one(a, '{"document_id":"A","limit":1}', finish=False)
        with self.assertRaises(ContractError):
            a.calls()
        a.apply(self.e(3, "finish", key="", status="completed"), now=1)
        self.assertEqual(len(a.calls()), 1)

    def test_identical_event_duplicate_and_repeated_text_are_different(self):
        a = self.assembler()
        a.apply(self.e(0, "start", call_id="call-a", name="lookup_doc"), now=1)
        e = self.e(1, "delta", payload='{"text":"')
        a.apply(e, now=1)
        self.assertFalse(a.apply(e, now=1))
        a.apply(self.e(2, "delta", payload="ha"), now=1)
        a.apply(self.e(3, "delta", payload="ha"), now=1)
        a.apply(self.e(4, "delta", payload='"}'), now=1)
        a.apply(self.e(5, "stop"), now=1)
        final = self.e(6, "finish", key="", status="completed")
        a.apply(final, now=1)
        self.assertFalse(a.apply(final, now=1))
        self.assertEqual(a.calls()[0].arguments["text"], "haha")

    def test_duplicate_conflict_and_gap_fail_closed(self):
        for event in [self.e(0, "start", call_id="different", name="lookup_doc"),
                      self.e(2, "delta", payload="{}")]:
            with self.subTest(event=event):
                a = self.assembler()
                a.apply(self.e(0, "start", call_id="call-a", name="lookup_doc"), now=1)
                with self.assertRaises(ContractError):
                    a.apply(event, now=1)
                self.assertEqual(a.phase, "failed")
                self.assertEqual(a._calls, {})

    def test_wrong_request_unknown_key_and_conflicting_ids(self):
        for event in [replace(self.e(1, "delta", payload="{}"), request_id="other"),
                      self.e(1, "delta", key="unknown", payload="{}"),
                      self.e(1, "start", key="b", call_id="call-a", name="lookup_doc"),
                      self.e(1, "delta", call_id="injected", payload="{}")]:
            with self.subTest(event=event):
                a = self.assembler()
                a.apply(self.e(0, "start", call_id="call-a", name="lookup_doc"), now=1)
                with self.assertRaises(ContractError):
                    a.apply(event, now=1)

    def test_final_arguments_snapshot_is_not_another_delta(self):
        raw = '{"document_id":"A","limit":1}'
        a = self.assembler()
        a.apply(self.e(0, "start", call_id="call-a", name="lookup_doc"), now=1)
        a.apply(self.e(1, "delta", payload=raw), now=1)
        with self.assertRaises(ContractError):
            a.apply(self.e(2, "stop", payload=raw + " "), now=1)
        # Equality is a deliberately strict LOCAL string-snapshot policy.

    def test_delta_after_stop_rejected(self):
        a = self.assembler()
        self.feed_one(a, "{}", finish=False)
        with self.assertRaises(ContractError):
            a.apply(self.e(3, "delta", payload="late"), now=1)

    def test_failure_incomplete_cancel_and_disconnect_release_nothing(self):
        for status in ("failed", "incomplete", "canceled", "disconnected"):
            with self.subTest(status=status):
                a = self.assembler()
                self.feed_one(a, "{}", finish=False)
                if status == "disconnected":
                    a.abort()
                else:
                    a.apply(self.e(3, "finish", key="", status=status), now=1)
                self.assertEqual(a._calls, {})
                with self.assertRaises(ContractError):
                    a.calls()

    def test_complete_request_with_unstopped_call_rejected(self):
        a = self.assembler()
        a.apply(self.e(0, "start", call_id="call-a", name="lookup_doc"), now=1)
        with self.assertRaises(ContractError):
            a.apply(self.e(1, "finish", key="", status="completed"), now=1)

    def test_zero_calls_is_not_task_success_and_late_close_preserves_calls(self):
        a = self.assembler()
        a.apply(self.e(0, "finish", key="", status="completed"), now=1)
        self.assertEqual(a.calls(), ())
        a = self.assembler()
        self.feed_one(a, "{}")
        a.abort("disconnected")
        self.assertEqual(len(a.calls()), 1)
        with self.assertRaises(ContractError):
            a.apply(self.e(4, "delta", payload="late"), now=1)
        self.assertEqual(len(a.calls()), 1)

    def test_call_count_per_call_and_aggregate_byte_limits(self):
        a = self.assembler(limits=Limits(max_calls=1))
        a.apply(self.e(0, "start", call_id="call-a", name="lookup_doc"), now=1)
        with self.assertRaises(ContractError):
            a.apply(self.e(1, "start", key="b", call_id="call-b", name="lookup_doc"), now=1)
        for limits in [Limits(max_argument_bytes=3), Limits(max_total_argument_bytes=3)]:
            with self.subTest(limits=limits):
                a = self.assembler(limits=limits)
                a.apply(self.e(0, "start", call_id="call-a", name="lookup_doc"), now=1)
                with self.assertRaises(ContractError):
                    a.apply(self.e(1, "delta", payload="😀"), now=1)

    def test_event_size_event_count_id_and_deadline_limits(self):
        for limits, event, now in [(Limits(max_event_bytes=10), self.e(0, "start", call_id="call-a", name="lookup_doc"), 1),
                                   (Limits(max_id_bytes=9), self.e(0, "start", call_id="call-a", name="very-long-tool-name"), 1),
                                   (Limits(), self.e(0, "start", call_id="call-a", name="lookup_doc"), 10)]:
            with self.subTest(limits=limits, now=now):
                a = self.assembler(limits=limits)
                with self.assertRaises(ContractError):
                    a.apply(event, now=now)
        a = self.assembler(limits=Limits(max_events=2))
        event = self.e(0, "start", call_id="call-a", name="lookup_doc")
        a.apply(event, now=1)
        self.assertFalse(a.apply(event, now=1))
        with self.assertRaises(ContractError):
            a.apply(event, now=1)

    def test_calls_are_defensive_copies(self):
        a = self.assembler()
        self.feed_one(a, '{"nested":{"x":1}}')
        a.calls()[0].arguments["nested"]["x"] = 9
        self.assertEqual(a.calls()[0].arguments["nested"]["x"], 1)

    def test_unknown_local_event_rejected(self):
        a = self.assembler()
        with self.assertRaises(ContractError):
            a.apply(self.e(0, "mystery"), now=1)


class JsonAndAuthorizationTests(unittest.TestCase):
    def test_strict_json_rejects_duplicate_keys_constants_and_wrong_root(self):
        for raw in ('{"x":1,"x":2}', '{"nested":{"x":1,"x":2}}', '{"x":NaN}', '{"x":Infinity}', '{"x":1e999}', '[]', 'null', '{}{}', '{"x":"\\ud800"}'):
            with self.subTest(raw=raw), self.assertRaises(ContractError):
                strict_object(raw, Limits())

    def test_json_depth_nodes_number_digits_and_unicode_bytes_bounded(self):
        cases = [( '{"x":[[[0]]]}', Limits(max_json_depth=3)),
                 ('{"x":[1,2,3]}', Limits(max_json_nodes=4)),
                 ('{"x":' + '1' * 257 + '}', Limits()),
                 ('{"x":"😀"}', Limits(max_argument_bytes=11))]
        for raw, limits in cases:
            with self.subTest(raw=raw), self.assertRaises(ContractError):
                strict_object(raw, limits)
        self.assertEqual(strict_object('{"x":"[[[["}', Limits(max_json_depth=1)), {"x": "[[[["})

    def test_schema_and_authorization_are_separate(self):
        good = PreparedCall("a", "call-a", "lookup_doc", {"document_id": "A", "limit": 2})
        self.assertEqual(validate_lookup(good, frozenset({"A"})), good.arguments)
        for call in [replace(good, name="invented_tool"),
                     replace(good, arguments={"document_id":"A", "limit":True}),
                     replace(good, arguments={"document_id":"A", "limit":6}),
                     replace(good, arguments={"document_id":"A", "limit":1, "tenant_id":"admin"}),
                     replace(good, arguments={"document_id":"B", "limit":1}),
                     replace(good, arguments={"document_id":None, "limit":1})]:
            with self.subTest(call=call), self.assertRaises(ContractError):
                validate_lookup(call, frozenset({"A"}))

    def test_invalid_limits_time_and_sequence_types_rejected(self):
        for limits in ({"max_events":0}, {"max_calls":True}):
            with self.assertRaises(ContractError):
                Limits(**limits)
        with self.assertRaises(ContractError):
            ToolAssembler("r", deadline=float("nan"))
        a = ToolAssembler("r", deadline=10)
        with self.assertRaises(ContractError):
            a.apply(ToolEvent("r", True, "finish", status="completed"), now=1)
        a = ToolAssembler("r", deadline=10)
        with self.assertRaises(ContractError):
            a.apply(ToolEvent("r", 2**64, "finish", status="completed"), now=1)


if __name__ == "__main__":
    unittest.main()
