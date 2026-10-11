"""Original finite SQLite/state-machine exercises, not MySQL/Redis/Kafka adapters."""
from __future__ import annotations

import hashlib
import json
import sqlite3


class SimulatedCrash(RuntimeError):
    pass


class UnknownOutcome(RuntimeError):
    """The local commit exists; a caller did not receive its reply."""


def integer(value: int) -> int:
    if type(value) is not int or not 0 <= value <= 10**12:
        raise ValueError("expected a bounded nonnegative integer")
    return value


def text(value: str, limit: int = 8192) -> str:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > limit:
        raise ValueError("expected bounded nonempty text")
    return value


class Store:
    """One local transaction owns command identity, inventory delta and outbox row."""

    def __init__(self, filename: str = ":memory:") -> None:
        self.db = sqlite3.connect(filename, isolation_level=None)
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS stock (
                tenant TEXT PRIMARY KEY,
                quantity INTEGER NOT NULL CHECK(quantity BETWEEN 0 AND 1000000000000),
                version INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS commands (
                tenant TEXT NOT NULL, key TEXT NOT NULL, payload TEXT NOT NULL,
                result TEXT, PRIMARY KEY(tenant, key));
            CREATE TABLE IF NOT EXISTS outbox (
                id TEXT PRIMARY KEY, tenant TEXT NOT NULL, version INTEGER NOT NULL,
                payload TEXT NOT NULL, sent INTEGER NOT NULL DEFAULT 0);
        """)

    def close(self) -> None:
        self.db.close()

    def apply(self, tenant: str, key: str, delta: int, fail_at: str | None = None) -> dict:
        tenant, key = text(tenant, 64), text(key, 256)
        if type(delta) is not int or abs(delta) > 10**9:
            raise ValueError("invalid finite delta")
        if fail_at not in (None, "after_effect", "after_event", "after_commit"):
            raise ValueError("unknown fault point")
        payload = json.dumps({"delta": delta}, sort_keys=True, separators=(",", ":"))
        self.db.execute("BEGIN IMMEDIATE")
        try:
            previous = self.db.execute("SELECT payload,result FROM commands WHERE tenant=? AND key=?", (tenant, key)).fetchone()
            if previous:
                if previous[0] != payload:
                    raise ValueError("same command identity with different parameters")
                result = json.loads(previous[1])
                self.db.execute("COMMIT")
                return result
            self.db.execute("INSERT OR IGNORE INTO stock VALUES(?,100,0)", (tenant,))
            self.db.execute("INSERT INTO commands(tenant,key,payload) VALUES(?,?,?)", (tenant, key, payload))
            changed = self.db.execute("UPDATE stock SET quantity=quantity+?,version=version+1 WHERE tenant=? AND quantity+? BETWEEN 0 AND 1000000000000", (delta, tenant, delta))
            if changed.rowcount != 1:
                raise ValueError("inventory invariant rejected")
            if fail_at == "after_effect":
                raise SimulatedCrash("before outbox insert")
            quantity, version = self.db.execute("SELECT quantity,version FROM stock WHERE tenant=?", (tenant,)).fetchone()
            identity = json.dumps([tenant, key], ensure_ascii=False, separators=(",", ":"))
            event_id = hashlib.sha256(identity.encode()).hexdigest()
            result = {"quantity": quantity, "version": version, "event_id": event_id}
            self.db.execute("INSERT INTO outbox(id,tenant,version,payload) VALUES(?,?,?,?)", (event_id, tenant, version, payload))
            self.db.execute("UPDATE commands SET result=? WHERE tenant=? AND key=?", (json.dumps(result, sort_keys=True), tenant, key))
            if fail_at == "after_event":
                raise SimulatedCrash("before transaction commit")
            self.db.execute("COMMIT")
        except Exception:
            if self.db.in_transaction:
                self.db.execute("ROLLBACK")
            raise
        if fail_at == "after_commit":
            raise UnknownOutcome("commit succeeded but reply was lost")
        return result

    def quantity(self, tenant: str) -> int | None:
        row = self.db.execute("SELECT quantity FROM stock WHERE tenant=?", (tenant,)).fetchone()
        return None if row is None else row[0]

    def pending(self) -> list[tuple]:
        return self.db.execute("SELECT id,tenant,version,payload FROM outbox WHERE sent=0 ORDER BY tenant,version").fetchall()

    def mark_sent(self, event_id: str) -> None:
        self.db.execute("UPDATE outbox SET sent=1 WHERE id=?", (event_id,))


class Inbox:
    """One local SQLite transaction records delivery identity and a finite effect."""

    def __init__(self) -> None:
        self.db = sqlite3.connect(":memory:", isolation_level=None)
        self.db.executescript("CREATE TABLE inbox(id TEXT PRIMARY KEY,payload TEXT NOT NULL); CREATE TABLE effect(value INTEGER NOT NULL); INSERT INTO effect VALUES(0);")

    def close(self) -> None:
        self.db.close()

    def deliver(self, event_id: str, delta: int, fail: bool = False) -> bool:
        text(event_id, 128)
        if type(delta) is not int or abs(delta) > 10**9:
            raise ValueError("invalid finite delta")
        payload = str(delta)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            previous = self.db.execute("SELECT payload FROM inbox WHERE id=?", (event_id,)).fetchone()
            if previous:
                if previous[0] != payload:
                    raise ValueError("delivery identity conflict")
                self.db.execute("COMMIT")
                return False
            self.db.execute("INSERT INTO inbox VALUES(?,?)", (event_id, payload))
            self.db.execute("UPDATE effect SET value=value+?", (delta,))
            if fail:
                raise SimulatedCrash("effect and receipt roll back together")
            self.db.execute("COMMIT")
            return True
        except Exception:
            if self.db.in_transaction:
                self.db.execute("ROLLBACK")
            raise

    @property
    def value(self) -> int:
        return self.db.execute("SELECT value FROM effect").fetchone()[0]


class OffsetPrefix:
    """Toy dense offset interval only. Real Kafka offset gaps require a delivered-record frontier."""

    def __init__(self, next_offset: int = 0, max_pending: int = 128) -> None:
        self.next = integer(next_offset)
        if type(max_pending) is not int or not 1 <= max_pending <= 4096:
            raise ValueError("invalid pending bound")
        self.bound = max_pending
        self.completed: set[int] = set()

    def complete(self, offset: int) -> int:
        offset = integer(offset)
        if offset < self.next or offset in self.completed:
            return self.next
        if offset != self.next and len(self.completed) >= self.bound:
            raise OverflowError("stop dispatch; the uncommitted frontier is full")
        self.completed.add(offset)
        while self.next in self.completed:
            self.completed.remove(self.next)
            self.next += 1
        return self.next


class FencedValue:
    """In-memory resource fence; an external authority must mint increasing tokens."""

    def __init__(self) -> None:
        self.token = -1
        self.value: str | None = None
        self.effects = 0

    def write(self, token: int, value: str) -> bool:
        token, value = integer(token), text(value)
        if token < self.token:
            return False
        if token == self.token:
            if value != self.value:
                raise ValueError("same token with different operation")
            return True
        self.token, self.value = token, value
        self.effects += 1
        return True


class VersionFloorCache:
    """Bounded in-memory invalidation model; floors are not evicted in this exercise."""

    def __init__(self) -> None:
        self.floor: dict[str, int] = {}
        self.entries: dict[str, tuple[int, str]] = {}

    def _reserve(self, key: str) -> None:
        text(key, 256)
        if key not in self.floor and len(self.floor) >= 128:
            raise OverflowError("floor retention is full; don't silently discard correctness state")

    def invalidate(self, key: str, version: int) -> None:
        self._reserve(key)
        self.floor[key] = max(integer(version), self.floor.get(key, 0))
        entry = self.entries.get(key)
        if entry and entry[0] < self.floor[key]:
            del self.entries[key]

    def put(self, key: str, version: int, value: str) -> bool:
        self._reserve(key)
        version, value = integer(version), text(value)
        if version < self.floor.get(key, 0):
            return False
        old = self.entries.get(key)
        if old and old[0] == version and old[1] != value:
            raise ValueError("same version with inconsistent payload")
        self.floor[key] = max(version, self.floor.get(key, 0))
        self.entries[key] = (version, value)
        return True
