"""Finite, synthetic Agent protocol contracts; no network or provider SDK.

The ordering/revision envelope and fail-closed policies are ORIGINAL TEACHING
CONTRACTS. They are not additional mandatory A2A/OpenAI/Claude wire fields.
Pass a trusted monotonic ``now`` on every update. Upstream framing/authentication
and limits on bytes BEFORE allocation are deliberately outside this module.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from dataclasses import asdict, dataclass, field


class ContractError(ValueError):
    """Invalid, incomplete, conflicting, expired, or over-budget observation."""


TERMINAL = frozenset({"completed", "failed", "canceled", "rejected"})
INTERRUPTED = frozenset({"input-required", "auth-required"})
STATES = TERMINAL | INTERRUPTED | {"submitted", "working"}
A2A_STATE_NAMES = {
    "TASK_STATE_" + state.upper().replace("-", "_"): state for state in STATES
}


def from_a2a_state(value: str) -> str:
    """Explicit v1.0 enum conversion; UNSPECIFIED is not an executable state."""
    try:
        return A2A_STATE_NAMES[value]
    except (KeyError, TypeError) as exc:
        raise ContractError("unknown or unspecified A2A state") from exc


@dataclass(frozen=True)
class Limits:
    max_events: int = 256             # Counts duplicates as received work, too.
    max_event_bytes: int = 16_384
    max_id_bytes: int = 128
    max_artifacts: int = 8
    max_artifact_bytes: int = 16_384
    max_total_artifact_bytes: int = 32_768
    max_calls: int = 8
    max_argument_bytes: int = 16_384
    max_total_argument_bytes: int = 32_768
    max_json_depth: int = 16
    max_json_nodes: int = 512

    def __post_init__(self) -> None:
        if any(type(v) is not int or v <= 0 for v in asdict(self).values()):
            raise ContractError("limits must be positive integers")


def _text(value: str, maximum: int, *, empty: bool = False) -> int:
    if type(value) is not str or (not empty and not value):
        raise ContractError("expected a nonempty string" if not empty else "expected a string")
    try:
        size = len(value.encode("utf-8"))
    except UnicodeEncodeError as exc:
        raise ContractError("invalid Unicode scalar") from exc
    if size > maximum:
        raise ContractError("string byte budget exceeded")
    return size


def _integer(value: int, minimum: int = 0) -> None:
    if type(value) is not int or not minimum <= value <= 2**63 - 1:
        raise ContractError("expected a bounded nonnegative integer")


def _time(value: float) -> None:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ContractError("expected finite monotonic time")


def _digest(event: object, limit: int) -> str:
    raw = json.dumps(asdict(event), ensure_ascii=False, sort_keys=True,
                     separators=(",", ":"), allow_nan=False).encode("utf-8")
    if len(raw) > limit:
        raise ContractError("event byte budget exceeded")
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class Artifact:
    artifact_id: str
    text: str
    complete: bool = False


@dataclass(frozen=True)
class TaskSnapshot:
    task_id: str
    context_id: str
    revision: int
    state: str
    artifacts: tuple[Artifact, ...] = ()


@dataclass(frozen=True)
class TaskEvent:
    task_id: str
    context_id: str
    revision: int
    kind: str                        # status or artifact, local normalized kinds
    state: str = ""
    artifact_id: str = ""
    text: str = ""
    append: bool = False
    last_chunk: bool = False


class TaskMonitor:
    """A single-task projection, with local revisions and authoritative snapshots.

    A protocol or deadline error invalidates synchronization, not the remote
    task's business state. Install a new authenticated snapshot to recover.
    This is not a server-side state machine, durable store, or CAS transaction.
    """
    def __init__(self, snapshot: TaskSnapshot, *, deadline: float,
                 now: float = 0, limits: Limits | None = None):
        self.limits = limits or Limits()
        _time(deadline)
        self.deadline = deadline
        self.received = 0
        self._seen: dict[int, str] = {}
        self._snapshot: TaskSnapshot | None = None
        self.synchronized = False
        self.cancel_requested = False
        self.install_snapshot(snapshot, now=now)

    @property
    def snapshot(self) -> TaskSnapshot:
        assert self._snapshot is not None
        return self._snapshot          # frozen records, immutable tuple and strings

    def _tick(self, now: float) -> None:
        _time(now)
        self.received += 1
        if now >= self.deadline or self.received > self.limits.max_events:
            raise ContractError("deadline or received-event budget exhausted")

    def _validate_snapshot(self, s: TaskSnapshot) -> None:
        if type(s) is not TaskSnapshot or type(s.artifacts) is not tuple:
            raise ContractError("expected an immutable snapshot")
        _text(s.task_id, self.limits.max_id_bytes)
        _text(s.context_id, self.limits.max_id_bytes)
        _integer(s.revision)
        if type(s.state) is not str or s.state not in STATES:
            raise ContractError("unknown state")
        if len(s.artifacts) > self.limits.max_artifacts:
            raise ContractError("artifact count exceeded")
        ids = set()
        total = 0
        for a in s.artifacts:
            if type(a) is not Artifact or type(a.complete) is not bool:
                raise ContractError("invalid artifact")
            _text(a.artifact_id, self.limits.max_id_bytes)
            total += _text(a.text, self.limits.max_artifact_bytes, empty=True)
            if a.artifact_id in ids:
                raise ContractError("duplicate artifact ID in snapshot")
            ids.add(a.artifact_id)
        if total > self.limits.max_total_artifact_bytes:
            raise ContractError("total artifact bytes exceeded")

    def install_snapshot(self, snapshot: TaskSnapshot, *, now: float) -> None:
        try:
            self._tick(now)
            self._validate_snapshot(snapshot)
            old = self._snapshot
            if old is not None:
                if (snapshot.task_id, snapshot.context_id) != (old.task_id, old.context_id):
                    raise ContractError("snapshot belongs to another task/context")
                if snapshot.revision < old.revision:
                    raise ContractError("stale snapshot")
                if snapshot.revision == old.revision and snapshot != old:
                    raise ContractError("same-revision snapshot conflict")
                if old.state in TERMINAL and (snapshot.state != old.state or
                                              snapshot.artifacts != old.artifacts):
                    raise ContractError("terminal task cannot be resurrected/refined")
            self._snapshot = snapshot
            self._seen.clear()
            self.synchronized = True
        except ContractError:
            self.synchronized = False
            raise

    def disconnect(self) -> None:
        self.synchronized = False     # disconnection is NOT a task terminal state

    def request_cancel(self) -> None:
        if self.snapshot.state in TERMINAL:
            raise ContractError("terminal task cannot be canceled by this client")
        self.cancel_requested = True  # a request is NOT an acknowledgment

    def continuation(self, task_id: str, context_id: str) -> None:
        if not self.synchronized or (task_id, context_id) != (
                self.snapshot.task_id, self.snapshot.context_id):
            raise ContractError("continuation requires synchronized matching identity")
        if self.snapshot.state in TERMINAL:
            raise ContractError("create a new task for terminal-task refinement")

    def apply(self, e: TaskEvent, *, now: float) -> bool:
        """Return False only for an identical retained duplicate; otherwise True."""
        try:
            self._tick(now)
            if not self.synchronized or type(e) is not TaskEvent:
                raise ContractError("snapshot resynchronization required")
            old = self.snapshot
            _integer(e.revision)
            for value in (e.task_id, e.context_id):
                _text(value, self.limits.max_id_bytes)
            for value in (e.kind, e.state, e.artifact_id):
                _text(value, self.limits.max_id_bytes, empty=True)
            _text(e.text, self.limits.max_artifact_bytes, empty=True)
            if type(e.append) is not bool or type(e.last_chunk) is not bool:
                raise ContractError("artifact flags must be booleans")
            if (e.task_id, e.context_id) != (old.task_id, old.context_id):
                raise ContractError("cross-task/context event")
            fingerprint = _digest(e, self.limits.max_event_bytes)
            if e.revision in self._seen:
                if self._seen[e.revision] != fingerprint:
                    raise ContractError("same-revision event conflict")
                return False
            if e.revision != old.revision + 1:
                raise ContractError("gap or unrecognized old event; request snapshot")
            artifacts = {a.artifact_id: a for a in old.artifacts}
            state = old.state
            if e.kind == "status":
                if e.state not in STATES or e.artifact_id or e.text or e.append or e.last_chunk:
                    raise ContractError("invalid status event")
                if state in TERMINAL and e.state != state:
                    raise ContractError("terminal state cannot change")
                state = e.state
            elif e.kind == "artifact":
                if e.state or not e.artifact_id or state in TERMINAL:
                    raise ContractError("invalid or post-terminal artifact")
                previous = artifacts.get(e.artifact_id)
                if previous is not None and previous.complete:
                    raise ContractError("completed artifact cannot be modified in this lab")
                if e.append and previous is None:
                    raise ContractError("append has no artifact base")
                text = (previous.text if e.append and previous else "") + e.text
                artifacts[e.artifact_id] = Artifact(e.artifact_id, text, e.last_chunk)
            else:
                raise ContractError("unknown normalized task event")
            candidate = TaskSnapshot(old.task_id, old.context_id, e.revision,
                                     state, tuple(artifacts.values()))
            self._validate_snapshot(candidate)   # validate before mutation
            self._snapshot = candidate
            self._seen[e.revision] = fingerprint
            return True
        except ContractError:
            self.synchronized = False
            raise


@dataclass(frozen=True)
class ToolEvent:
    request_id: str
    sequence: int
    kind: str                        # start/delta/stop/finish, local envelope
    call_key: str = ""
    call_id: str = ""
    name: str = ""
    payload: str = ""
    status: str = ""


@dataclass
class _Call:
    call_id: str
    name: str
    fragments: list[str] = field(default_factory=list)
    byte_count: int = 0
    stopped: bool = False
    arguments: dict | None = None


@dataclass(frozen=True)
class PreparedCall:
    call_key: str
    call_id: str
    name: str
    arguments: dict


def strict_object(raw: str, limits: Limits) -> dict:
    """Byte/depth checks precede parsing; duplicate keys/nonfinite numbers fail.

    Node count is checked after stdlib parsing; the byte cap bounds that earlier
    allocation. This is a bounded JSON subset, not a full JSON Schema validator.
    """
    _text(raw, limits.max_argument_bytes)
    depth = 0
    in_string = escaped = False
    for c in raw:
        if in_string:
            if escaped:
                escaped = False
            elif c == "\\":
                escaped = True
            elif c == '"':
                in_string = False
        elif c == '"':
            in_string = True
        elif c in "[{":
            depth += 1
            if depth > limits.max_json_depth:
                raise ContractError("JSON nesting budget exceeded")
        elif c in "]}":
            depth -= 1
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise ContractError("duplicate JSON key")
            result[key] = value
        return result
    def bad_constant(value):
        raise ContractError("non-standard JSON constant")
    def integer(value):
        if len(value.lstrip("-")) > 256:
            raise ContractError("integer digit budget exceeded")
        return int(value)
    try:
        parsed = json.loads(raw, object_pairs_hook=pairs,
                            parse_constant=bad_constant, parse_int=integer)
    except (ValueError, RecursionError) as exc:
        raise ContractError("invalid complete JSON object") from exc
    if type(parsed) is not dict:
        raise ContractError("tool input must be an object")
    pending = [parsed]
    nodes = 0
    while pending:
        value = pending.pop()
        nodes += 1
        if nodes > limits.max_json_nodes:
            raise ContractError("JSON node budget exceeded")
        if type(value) is float and not math.isfinite(value):
            raise ContractError("nonfinite JSON number")
        if type(value) is str:
            _text(value, limits.max_argument_bytes, empty=True)
        elif type(value) is dict:
            for key in value:
                _text(key, limits.max_argument_bytes, empty=True)
            pending.extend(value.values())
        elif type(value) is list:
            pending.extend(value)
    return parsed


class ToolAssembler:
    """Fail-closed synthetic normalized assembler; no real tool execution.

    The local policy releases calls only after every call stops AND a successful
    request-level finish. Providers do not universally require that policy.
    """
    def __init__(self, request_id: str, *, deadline: float,
                 limits: Limits | None = None):
        self.limits = limits or Limits()
        _text(request_id, self.limits.max_id_bytes)
        _time(deadline)
        self.request_id = request_id
        self.deadline = deadline
        self.received = 0
        self.phase = "receiving"
        self._last = -1
        self._seen: dict[int, str] = {}
        self._calls: dict[str, _Call] = {}
        self._total_bytes = 0

    def abort(self, reason: str = "disconnected") -> None:
        if reason not in {"disconnected", "canceled", "failed", "incomplete"}:
            raise ContractError("unknown abort reason")
        if self.phase == "completed":
            return                    # a late close cannot revoke a committed result
        self.phase = reason
        self._calls.clear()
        self._seen.clear()
        self._total_bytes = 0

    def apply(self, e: ToolEvent, *, now: float) -> bool:
        try:
            _time(now)
            self.received += 1
            if now >= self.deadline or self.received > self.limits.max_events:
                raise ContractError("deadline or received-event budget exhausted")
            if type(e) is not ToolEvent:
                raise ContractError("expected a normalized tool event")
            _integer(e.sequence)
            for value in (e.request_id, e.kind, e.call_key, e.call_id, e.name, e.status):
                _text(value, self.limits.max_id_bytes, empty=True)
            size = _text(e.payload, self.limits.max_argument_bytes, empty=True)
            if e.request_id != self.request_id:
                raise ContractError("cross-request event")
            fingerprint = _digest(e, self.limits.max_event_bytes)
            if e.sequence in self._seen:
                if self._seen[e.sequence] != fingerprint:
                    raise ContractError("same-sequence event conflict")
                return False
            if self.phase != "receiving":
                raise ContractError("request stream is closed")
            if e.sequence != self._last + 1:
                raise ContractError("gap or out-of-order event")
            if e.kind == "finish":
                if e.call_key or e.call_id or e.name or e.payload:
                    raise ContractError("invalid finish envelope")
                if e.status not in {"completed", "failed", "incomplete", "canceled"}:
                    raise ContractError("unknown finish status")
                if e.status != "completed":
                    self.abort(e.status)
                    return True
                if any(not c.stopped for c in self._calls.values()):
                    raise ContractError("successful finish with incomplete call")
                self.phase = "completed"
            elif e.kind == "start":
                if not e.call_key or not e.call_id or not e.name or e.payload or e.status:
                    raise ContractError("invalid start envelope")
                if e.call_key in self._calls or any(c.call_id == e.call_id for c in self._calls.values()):
                    raise ContractError("duplicate/conflicting call identity")
                if len(self._calls) >= self.limits.max_calls:
                    raise ContractError("call count exceeded")
                self._calls[e.call_key] = _Call(e.call_id, e.name)
            elif e.kind in {"delta", "stop"}:
                if not e.call_key or e.call_id or e.name or e.status:
                    raise ContractError("invalid fragment envelope")
                c = self._calls.get(e.call_key)
                if c is None or c.stopped:
                    raise ContractError("unknown or already-stopped call")
                if e.kind == "delta":
                    if c.byte_count + size > self.limits.max_argument_bytes:
                        raise ContractError("per-call argument bytes exceeded")
                    if self._total_bytes + size > self.limits.max_total_argument_bytes:
                        raise ContractError("total argument bytes exceeded")
                    c.fragments.append(e.payload)
                    c.byte_count += size
                    self._total_bytes += size
                else:
                    raw = "".join(c.fragments)
                    if e.payload and e.payload != raw:
                        raise ContractError("final snapshot disagrees with accumulated deltas")
                    arguments = strict_object(raw, self.limits)
                    c.arguments = arguments
                    c.stopped = True
            else:
                raise ContractError("unknown normalized tool event")
            self._last = e.sequence
            self._seen[e.sequence] = fingerprint
            return True
        except ContractError:
            self.abort("failed")
            raise

    def calls(self) -> tuple[PreparedCall, ...]:
        if self.phase != "completed":
            raise ContractError("no committed calls before successful request finish")
        return tuple(PreparedCall(key, c.call_id, c.name, copy.deepcopy(c.arguments))
                     for key, c in self._calls.items())


def validate_lookup(call: PreparedCall, allowed_documents: frozenset[str]) -> dict:
    """One original read-only tool contract; auth scope is trusted caller input.

    Returns a validated preview, never connects to a service or executes a tool.
    This intentionally supports no arbitrary tool, SQL, URL, or full JSON Schema.
    """
    args = call.arguments
    if call.name != "lookup_doc" or type(args) is not dict or set(args) != {"document_id", "limit"}:
        raise ContractError("unknown tool or unexpected fields")
    document = args["document_id"]
    limit = args["limit"]
    if type(document) is not str or not document or type(limit) is not int or not 1 <= limit <= 5:
        raise ContractError("invalid lookup arguments")
    if document not in allowed_documents:
        raise ContractError("document is outside current authorization scope")
    return {"document_id": document, "limit": limit}
