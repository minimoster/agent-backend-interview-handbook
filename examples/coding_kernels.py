"""New original reference kernels, not supplied answers or production systems."""
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import json
import math
import shlex
from threading import Lock
from uuid import uuid4

class InventoryError(ValueError):
    pass

class InventoryOrders:
    """One-process reserve-on-order model. Amounts are fictional integer cents."""
    transitions = {"pending": {"making", "cancelled"}, "making": {"ready"},
                   "ready": {"picked_up"}, "picked_up": set(), "cancelled": set()}
    def __init__(self, stock, recipes, prices):
        self.stock = dict(stock)
        self.recipes = {name: dict(recipe) for name, recipe in recipes.items()}
        self.prices = dict(prices)
        if any(type(q) is not int or q < 0 for q in self.stock.values()):
            raise InventoryError("invalid stock")
        if set(self.recipes) != set(self.prices):
            raise InventoryError("menu and prices differ")
        for name, recipe in self.recipes.items():
            if not recipe or any(k not in self.stock or type(v) is not int or v <= 0
                                 for k, v in recipe.items()):
                raise InventoryError("invalid recipe")
            if type(self.prices[name]) is not int or self.prices[name] < 0:
                raise InventoryError("invalid price")
        self.orders, self.keys = {}, {}
        self.lock = Lock()

    def _needed(self, cart):
        if not cart or any(name not in self.recipes or type(q) is not int or q <= 0
                           for name, q in cart.items()):
            raise InventoryError("invalid cart")
        needed = Counter()
        for name, quantity in cart.items():
            for ingredient, amount in self.recipes[name].items():
                needed[ingredient] += quantity * amount
        return dict(needed)

    def quote(self, cart):
        self._needed(cart)
        total = sum(self.prices[name] * q for name, q in cart.items())
        # Original fixture: only this pair discounts 50 cents per pair.
        if {"sandwich", "tea"} <= self.prices.keys():
            pairs = min(cart.get("sandwich", 0), cart.get("tea", 0))
            discount = min(50, self.prices["sandwich"] + self.prices["tea"])
            total -= pairs * discount
        return total

    def place(self, customer, key, cart):
        if not isinstance(customer, str) or not customer or not isinstance(key, str) or not key:
            raise InventoryError("customer and key required")
        cart = dict(cart)
        needed = self._needed(cart)
        fingerprint = tuple(sorted(cart.items()))
        with self.lock:
            scoped = (customer, key)
            if scoped in self.keys:
                old_fingerprint, order_id = self.keys[scoped]
                if old_fingerprint != fingerprint:
                    raise InventoryError("idempotency conflict")
                return order_id
            if any(self.stock[item] < q for item, q in needed.items()):
                raise InventoryError("insufficient stock")
            for item, q in needed.items():
                self.stock[item] -= q
            order_id = str(uuid4())
            self.orders[order_id] = {"customer": customer, "status": "pending",
                                     "reserved": needed, "total_cents": self.quote(cart)}
            self.keys[scoped] = (fingerprint, order_id)
            return order_id

    def transition(self, customer, order_id, target):
        with self.lock:
            row = self.orders.get(order_id)
            if row is None or row["customer"] != customer:
                raise InventoryError("order not found")
            if target == row["status"]:
                return target
            if target not in self.transitions[row["status"]]:
                raise InventoryError("invalid transition")
            if target == "cancelled":
                for item, q in row["reserved"].items():
                    self.stock[item] += q
            row["status"] = target
            return target

    def snapshot_stock(self):
        with self.lock:
            return dict(self.stock)


def analyze_jsonl(lines):
    """Original log contract; output omits original messages and rejected inputs."""
    accepted, bad_lines = [], []
    for number, text in enumerate(lines, 1):
        try:
            row = json.loads(text)
            if not isinstance(row, dict):
                raise ValueError("object required")
            timestamp = datetime.fromisoformat(row["ts"].replace("Z", "+00:00"))
            if timestamp.tzinfo is None or timestamp.utcoffset() is None:
                raise ValueError("timezone required")
            status, latency = row["status"], row["latency_ms"]
            if type(status) is not int or not 100 <= status <= 599:
                raise ValueError("invalid status")
            if type(latency) not in (int, float) or not math.isfinite(latency) or latency < 0:
                raise ValueError("invalid latency")
            accepted.append((status, latency))
        except (KeyError, ValueError, TypeError, AttributeError, OverflowError):
            bad_lines.append(number)
    latencies = sorted(x[1] for x in accepted)
    count = len(accepted)
    return {"valid": count, "invalid_lines": bad_lines,
            "server_errors": sum(status >= 500 for status, _ in accepted),
            "p95_ms": latencies[math.ceil(.95 * count) - 1] if count else None}

@dataclass(frozen=True)
class ToyTariff:
    """Fictional tariff for a coding exercise; no city or provider claim."""
    base_fare: Decimal = Decimal("10")
    included_km: Decimal = Decimal("2")
    per_extra_km: Decimal = Decimal("3")
    per_bag: Decimal = Decimal("1.5")
    per_wait_minute: Decimal = Decimal("0.5")
    night_multiplier: Decimal = Decimal("1.2")


def taxi_quote(*, distance_km, bags, wait_minutes, night, tariff=ToyTariff()):
    if type(bags) is not int or bags < 0 or type(night) is not bool:
        raise ValueError("invalid bags or night")
    # Deliberately require Decimal or decimal text. Binary float is not the contract.
    if not isinstance(distance_km, (Decimal, str)) or not isinstance(wait_minutes, (Decimal, str)):
        raise ValueError("decimal text or Decimal required")
    try:
        distance, waiting = Decimal(distance_km), Decimal(wait_minutes)
    except InvalidOperation as exc:
        raise ValueError("invalid decimal input") from exc
    if not distance.is_finite() or not waiting.is_finite() or distance < 0 or waiting < 0:
        raise ValueError("invalid distance or waiting")
    fare = tariff.base_fare + max(Decimal("0"), distance - tariff.included_km) * tariff.per_extra_km
    if night:
        fare *= tariff.night_multiplier
    luggage = bags * tariff.per_bag
    wait = waiting * tariff.per_wait_minute
    rounded = lambda amount: amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    # Original rule: round each component once, then sum displayed components.
    amounts = [rounded(fare), rounded(luggage), rounded(wait)]
    return {"currency": "TEST", "fare": str(amounts[0]), "luggage": str(amounts[1]),
            "waiting": str(amounts[2]), "total": str(sum(amounts))}


def parse_safe_command(text):
    """Parse a tiny original command grammar. Never execute a shell or command."""
    if not isinstance(text, str) or len(text) > 4096 or any(c in text for c in "\n\r\x00"):
        raise ValueError("invalid command text")
    lexer = shlex.shlex(text, posix=True, punctuation_chars="|&;<>`")
    lexer.whitespace_split = True
    lexer.commenters = ""
    tokens = list(lexer)
    if not tokens or tokens[0] not in {"ls", "grep", "cat"}:
        raise ValueError("unsupported command")
    if any(any(c in token for c in "|&;<>`$") for token in tokens):
        raise ValueError("operators or substitutions forbidden")
    return {"command": tokens[0], "args": tokens[1:]}
