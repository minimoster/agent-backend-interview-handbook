"""Original, local-only teaching exercises. No network or external side effects.

They demonstrate contracts, not a production retrieval, billing, document or MQ service.
"""

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import sqlite3
import struct
from threading import Lock


def rrf(rankings, k=60):
    """Fuse unique string IDs; duplicate IDs in one list consume no extra rank.

    k is a nonnegative integer, ranks start at 1, ties sort by ID. Fractions keep
    teaching examples exact; this does not provide relevance or permission checks.
    """
    if isinstance(k, bool) or not isinstance(k, int) or k < 0:
        raise ValueError("k must be a nonnegative integer")
    scores = {}
    for ranking in rankings:
        unique = []
        seen = set()
        for doc_id in ranking:
            if not isinstance(doc_id, str) or not doc_id:
                raise ValueError("IDs must be nonempty strings")
            if doc_id not in seen:
                seen.add(doc_id)
                unique.append(doc_id)
        for rank, doc_id in enumerate(unique, 1):
            scores[doc_id] = scores.get(doc_id, Fraction()) + Fraction(1, k + rank)
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))


class VersionConflict(Exception):
    pass


@dataclass(frozen=True)
class Snapshot:
    version: int
    content: str


class VersionedDocuments:
    """Atomic compare-and-write only inside this one Python process.

    Tenant keys partition storage but are not authentication or authorization.
    A real service needs server-side identity checks and database CAS/transactions.
    """

    def __init__(self):
        self._lock = Lock()
        self._docs = {}

    def create(self, tenant, doc_id, content):
        with self._lock:
            key = (tenant, doc_id)
            if key in self._docs:
                raise ValueError("already exists")
            self._docs[key] = Snapshot(1, content)
            return self._docs[key]

    def read(self, tenant, doc_id):
        with self._lock:
            return self._docs[(tenant, doc_id)]

    def update(self, tenant, doc_id, expected_version, content):
        if isinstance(expected_version, bool) or not isinstance(expected_version, int) or expected_version < 1:
            raise ValueError("expected_version must be a positive integer")
        with self._lock:
            key = (tenant, doc_id)
            current = self._docs[key]
            if current.version != expected_version:
                raise VersionConflict(f"expected {expected_version}, current {current.version}")
            updated = Snapshot(current.version + 1, content)
            self._docs[key] = updated
            return updated


class IdempotencyConflict(Exception):
    pass


class InsufficientStock(Exception):
    pass


class InjectedFailure(Exception):
    pass


class LostReply(Exception):
    """The client has no successful reply, but the local DB already committed."""


class IdempotentInventory:
    """SQLite-only simulation: business effect + dedup result in one transaction.

    Stable (tenant, request_key) and canonical parameter fingerprint are separate.
    No HTTP, external payment, Redis or broker is part of this atomic boundary.
    Only successfully committed requests bind a key. Rejected/rolled-back calls
    leave no request record: a later call may reuse that key with different params.
    This explicit teaching policy is NOT first-attempt reservation or failure caching.
    Retention, schema migration, auth, metrics and busy-retry policy are omitted.
    Each instance/connection is used by its owning thread.
    """

    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path, timeout=5, isolation_level=None)
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS stock (
                tenant TEXT NOT NULL, sku TEXT NOT NULL, units INTEGER NOT NULL CHECK(units>=0),
                PRIMARY KEY(tenant,sku)
            );
            CREATE TABLE IF NOT EXISTS requests (
                tenant TEXT NOT NULL, request_key TEXT NOT NULL,
                fingerprint TEXT NOT NULL, result TEXT NOT NULL,
                PRIMARY KEY(tenant,request_key)
            );
            CREATE TABLE IF NOT EXISTS orders (
                tenant TEXT NOT NULL, request_key TEXT NOT NULL,
                sku TEXT NOT NULL, units INTEGER NOT NULL CHECK(units>0),
                PRIMARY KEY(tenant,request_key)
            );
        """)

    def close(self):
        self.db.close()

    def seed(self, tenant, sku, units):
        if isinstance(units, bool) or not isinstance(units, int) or units < 0:
            raise ValueError("stock must be a nonnegative integer")
        self.db.execute("INSERT INTO stock VALUES (?,?,?)", (tenant, sku, units))

    def purchase(self, tenant, request_key, sku, units, fault=None):
        if not all(isinstance(v, str) and v for v in (tenant, request_key, sku)):
            raise ValueError("tenant, request_key and sku must be nonempty strings")
        if isinstance(units, bool) or not isinstance(units, int) or units <= 0:
            raise ValueError("units must be a positive integer")
        if fault not in (None, "after_business_before_commit", "after_commit_lost_reply"):
            raise ValueError("unknown fault point")
        encoded = json.dumps({"sku": sku, "units": units}, sort_keys=True, separators=(",", ":"))
        fingerprint = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
        self.db.execute("BEGIN IMMEDIATE")
        try:
            previous = self.db.execute(
                "SELECT fingerprint,result FROM requests WHERE tenant=? AND request_key=?",
                (tenant, request_key),
            ).fetchone()
            if previous:
                if previous[0] != fingerprint:
                    raise IdempotencyConflict("same request key with different parameters")
                result = json.loads(previous[1])
            else:
                changed = self.db.execute(
                    "UPDATE stock SET units=units-? WHERE tenant=? AND sku=? AND units>=?",
                    (units, tenant, sku, units),
                ).rowcount
                if changed != 1:
                    raise InsufficientStock("unknown sku or insufficient stock")
                self.db.execute("INSERT INTO orders VALUES (?,?,?,?)", (tenant, request_key, sku, units))
                result = {"request_key": request_key, "sku": sku, "units": units, "status": "done"}
                if fault == "after_business_before_commit":
                    raise InjectedFailure("rollback all local business changes")
                self.db.execute(
                    "INSERT INTO requests VALUES (?,?,?,?)",
                    (tenant, request_key, fingerprint, json.dumps(result, sort_keys=True)),
                )
            self.db.execute("COMMIT")
        except BaseException:
            if self.db.in_transaction:
                self.db.execute("ROLLBACK")
            raise
        if fault == "after_commit_lost_reply":
            raise LostReply("committed, reply lost; query/retry with the SAME key")
        return result

    def remaining(self, tenant, sku):
        row = self.db.execute("SELECT units FROM stock WHERE tenant=? AND sku=?", (tenant, sku)).fetchone()
        return None if row is None else row[0]

    def order_count(self, tenant):
        return self.db.execute("SELECT count(*) FROM orders WHERE tenant=?", (tenant,)).fetchone()[0]


class FrameError(Exception):
    def __init__(self, message, completed_frames=()):
        super().__init__(message)
        self.completed_frames = tuple(completed_frames)


class FrameDecoder:
    """Four-byte unsigned network-endian length + arbitrary payload bytes.

    Input chunks and retained incomplete data are bounded. On protocol error this
    decoder is poisoned; the error carries frames completed earlier in that feed,
    so callers can account for the valid prefix independently of read boundaries.
    Create a new decoder only for a new connection. A real
    server must separately impose read deadlines, connection and total work limits.
    """

    def __init__(self, max_frame=1024, max_chunk=4096):
        if not isinstance(max_frame, int) or isinstance(max_frame, bool) or max_frame < 0:
            raise ValueError("invalid max_frame")
        if not isinstance(max_chunk, int) or isinstance(max_chunk, bool) or max_chunk <= 0:
            raise ValueError("invalid max_chunk")
        self.max_frame = max_frame
        self.max_chunk = max_chunk
        self.buffer = bytearray()
        self.failed = False

    def _error(self, message, completed_frames=()):
        self.failed = True
        self.buffer.clear()
        raise FrameError(message, completed_frames)

    def feed(self, chunk):
        if self.failed:
            raise FrameError("decoder is poisoned")
        if not isinstance(chunk, bytes):
            raise TypeError("chunk must be bytes")
        if len(chunk) > self.max_chunk:
            self._error("input chunk exceeds caller contract")
        self.buffer.extend(chunk)
        frames = []
        while len(self.buffer) >= 4:
            length = struct.unpack("!I", self.buffer[:4])[0]
            if length > self.max_frame:
                self._error("declared frame too large", frames)
            if len(self.buffer) < 4 + length:
                break
            frames.append(bytes(self.buffer[4:4 + length]))
            del self.buffer[:4 + length]
        return frames

    def eof(self):
        if self.failed:
            raise FrameError("decoder is poisoned")
        if self.buffer:
            self._error("truncated frame at EOF")


def encode_frame(payload):
    if not isinstance(payload, bytes):
        raise TypeError("payload must be bytes")
    return struct.pack("!I", len(payload)) + payload
