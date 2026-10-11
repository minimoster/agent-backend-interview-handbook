"""Original, deterministic teaching contracts; no model or external data access.
Tested runtime: CPython 3.12.14. Span coordinates are synthetic canonical units.
"""
from dataclasses import dataclass
from math import log2
from typing import Mapping, Sequence


@dataclass(frozen=True)
class Span:
    document: str
    revision: str
    start: int
    end: int

    def __post_init__(self):
        if not self.document or not self.revision:
            raise ValueError("stable source identity required")
        if type(self.start) is not int or type(self.end) is not int:
            raise ValueError("integer coordinates required")
        if self.start < 0 or self.end <= self.start:
            raise ValueError("nonempty half-open span required")


def union_length(intervals: Sequence[tuple[int, int]]) -> int:
    total = 0
    right = -1
    for start, end in sorted(intervals):
        if type(start) is not int or type(end) is not int or start < 0 or end <= start:
            raise ValueError("invalid interval")
        total += max(0, end - max(start, right))
        right = max(right, end)
    return total


def covered_fraction(gold: Span, chunks: Sequence[Span]) -> float:
    intersections = []
    for chunk in chunks:
        if (gold.document, gold.revision) != (chunk.document, chunk.revision):
            continue
        start, end = max(gold.start, chunk.start), min(gold.end, chunk.end)
        if start < end:
            intersections.append((start, end))
    return union_length(intersections) / (gold.end - gold.start)


def evidence_coverage(gold: Sequence[Span], chunks: Sequence[Span]) -> float | None:
    if not gold:
        return None
    return sum(covered_fraction(span, chunks) == 1.0 for span in gold) / len(gold)


def redundancy(chunks: Sequence[Span]) -> float | None:
    total = sum(s.end - s.start for s in chunks)
    if not total:
        return None
    groups = {}
    for s in chunks:
        groups.setdefault((s.document, s.revision), []).append((s.start, s.end))
    unique = sum(union_length(intervals) for intervals in groups.values())
    return (total - unique) / total


def ranking_metrics(ranking: Sequence[str], grades: Mapping[str, int], k: int) -> dict:
    if type(k) is not int or k <= 0:
        raise ValueError("positive integer k required")
    if len(set(ranking)) != len(ranking):
        raise ValueError("deduplicate stable identities before scoring")
    if any(type(g) is not int or g < 0 for g in grades.values()):
        raise ValueError("nonnegative integer grades required")
    relevant = {identity for identity, grade in grades.items() if grade > 0}
    top = list(ranking[:k])
    hits = sum(identity in relevant for identity in top)
    rr = next((1 / rank for rank, identity in enumerate(top, 1) if identity in relevant), 0.0)
    dcg = sum((2 ** grades.get(identity, 0) - 1) / log2(rank + 1)
              for rank, identity in enumerate(top, 1))
    ideal = sum((2 ** grade - 1) / log2(rank + 1)
                for rank, grade in enumerate(sorted(grades.values(), reverse=True)[:k], 1))
    return {"returned": len(top), "precision_at_k": hits / k,
            "recall_at_k": hits / len(relevant) if relevant else None,
            "hit_at_k": int(hits > 0), "rr_at_k": rr if relevant else None,
            "ndcg_at_k": dcg / ideal if ideal else None}


def mmr(candidates: Sequence[str], relevance: Mapping[str, float],
        pair_similarity: Mapping[tuple[str, str], float], k: int, weight: float) -> list[str]:
    """Greedy illustration with precomputed numbers, not an embedding implementation."""
    if len(set(candidates)) != len(candidates) or type(k) is not int or k <= 0:
        raise ValueError("unique candidates and positive k required")
    if not 0 <= weight <= 1:
        raise ValueError("weight must be in [0, 1]")
    selected = []
    remaining = list(candidates)
    while remaining and len(selected) < k:
        def score(candidate):
            overlap = max((pair_similarity.get((candidate, other),
                           pair_similarity.get((other, candidate), 0.0))
                           for other in selected), default=0.0)
            return weight * relevance[candidate] - (1 - weight) * overlap
        best = max(remaining, key=score)  # input order resolves ties deterministically
        selected.append(best)
        remaining.remove(best)
    return selected


@dataclass(frozen=True)
class Evidence:
    identity: str
    tenant: str
    document: str
    revision: str
    text: str


def select_current(items: Sequence[Evidence], tenant: str,
                   active_revisions: Mapping[tuple[str, str], str]) -> list[Evidence]:
    """Read-side fixture filter only; not a complete authorization system."""
    seen = set()
    result = []
    for item in items:
        if item.tenant != tenant:
            continue
        if active_revisions.get((tenant, item.document)) != item.revision:
            continue
        if item.identity not in seen:
            result.append(item)
            seen.add(item.identity)
    return result


def route_catalog(catalog: Sequence[dict], permitted: set[str], required_tags: set[str],
                  schema_budget: int) -> list[dict]:
    """Deterministic fixture router; schema_units are supplied measurements, not tokens."""
    if type(schema_budget) is not int or schema_budget < 0:
        raise ValueError("nonnegative budget required")
    selected = []
    used = 0
    for item in catalog:
        if item["identity"] not in permitted or not required_tags.issubset(set(item["tags"])):
            continue
        size = item["schema_units"]
        if type(size) is not int or size <= 0:
            raise ValueError("positive measured schema size required")
        if used + size <= schema_budget:
            selected.append(item)
            used += size
    return selected
