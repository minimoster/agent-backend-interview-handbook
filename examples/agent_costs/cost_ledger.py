"""Offline token-cost arithmetic, not a billing client or concurrent budget gate.

One snapshot and currency per summarize() call. Adapt provider usage first:
input_tokens INCLUDES cached_input_tokens; output_tokens is the billable output
bucket after checking the provider's reasoning-token semantics. No API calls.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Optional

MILLION = Decimal(1_000_000)
ZERO = Decimal(0)


def money(value: Decimal) -> Decimal:
    if not isinstance(value, Decimal) or not value.is_finite() or value < 0:
        raise ValueError("money must be a finite nonnegative Decimal")
    return value


@dataclass(frozen=True)
class RateCard:
    snapshot: str
    currency: str
    uncached_input: Decimal
    cached_input: Decimal
    output: Decimal

    def __post_init__(self):
        if not self.snapshot.strip() or not self.currency.strip():
            raise ValueError("snapshot and currency are required")
        for rate in (self.uncached_input, self.cached_input, self.output):
            money(rate)


@dataclass(frozen=True)
class Usage:
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int

    def __post_init__(self):
        for count in (self.input_tokens, self.cached_input_tokens, self.output_tokens):
            if type(count) is not int or count < 0:
                raise ValueError("token counts must be nonnegative integers")
        if self.cached_input_tokens > self.input_tokens:
            raise ValueError("cached input is a subset of total input")


def estimate(usage: Usage, rates: RateCard) -> Decimal:
    return (
        (usage.input_tokens - usage.cached_input_tokens) * rates.uncached_input
        + usage.cached_input_tokens * rates.cached_input
        + usage.output_tokens * rates.output
    ) / MILLION


@dataclass(frozen=True)
class Attempt:
    request_id: str
    outcome: str  # succeeded / failed / unknown; task success is a separate metric
    usage: Optional[Usage] = None
    reserve: Optional[Decimal] = None

    def __post_init__(self):
        if not self.request_id.strip():
            raise ValueError("request identity is required")
        if self.outcome == "unknown":
            if self.usage is not None or self.reserve is None:
                raise ValueError("unknown outcome needs a reserve, not fabricated usage")
            money(self.reserve)
        elif self.outcome in ("succeeded", "failed"):
            if not isinstance(self.usage, Usage) or self.reserve is not None:
                raise ValueError("known usage required; do not also count a reservation")
        else:
            raise ValueError("unsupported outcome")


def summarize(attempts: Iterable[Attempt], rates: RateCard) -> dict:
    seen = set()
    known = reserved = ZERO
    input_tokens = cached_tokens = output_tokens = unknown = 0
    for attempt in attempts:
        if attempt.request_id in seen:
            raise ValueError("duplicate request identity; reconcile the ledger first")
        seen.add(attempt.request_id)
        if attempt.outcome == "unknown":
            reserved += attempt.reserve
            unknown += 1
        else:
            usage = attempt.usage
            known += estimate(usage, rates)
            input_tokens += usage.input_tokens
            cached_tokens += usage.cached_input_tokens
            output_tokens += usage.output_tokens
    return {
        "snapshot": rates.snapshot,
        "currency": rates.currency,
        "requests": len(seen),
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_tokens,
        "output_tokens": output_tokens,
        "known_estimate": known,
        "unknown_requests": unknown,
        "unknown_reserve": reserved,
        "accounted_exposure": known + reserved,
    }
