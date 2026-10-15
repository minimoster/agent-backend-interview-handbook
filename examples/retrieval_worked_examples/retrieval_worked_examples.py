"""Original teaching kernels: retrieval metrics, streaming top-k and RRF.

Python 3.10+. No external packages, service calls or user data.
"""
from collections.abc import Iterable, Mapping, Sequence
import heapq
import math


def score_query(ranking: Sequence[str], grades: Mapping[str, int], k: int) -> dict:
    """Unique IDs, grades 0..3, positive grades are relevant, fixed-k precision.

    Unjudged returned IDs contribute zero under this explicit evaluation policy.
    Recall/RR/nDCG are None for queries with no judged positive evidence.
    """
    if type(k) is not int or k < 1:
        raise ValueError("k must be a positive integer")
    if len(set(ranking)) != len(ranking):
        raise ValueError("ranking must contain unique evidence IDs")
    if any(type(g) is not int or not 0 <= g <= 3 for g in grades.values()):
        raise ValueError("grades must be integers in 0..3")
    top = ranking[:k]
    relevant_total = sum(g > 0 for g in grades.values())
    gains = [grades.get(doc_id, 0) for doc_id in top]
    hits = sum(g > 0 for g in gains)
    first = next((rank for rank, g in enumerate(gains, 1) if g > 0), None)
    dcg = sum((2 ** g - 1) / math.log2(rank + 1)
              for rank, g in enumerate(gains, 1))
    ideal_grades = sorted(grades.values(), reverse=True)[:k]
    idcg = sum((2 ** g - 1) / math.log2(rank + 1)
               for rank, g in enumerate(ideal_grades, 1))
    return {
        "precision_at_k": hits / k,
        "recall_at_k": hits / relevant_total if relevant_total else None,
        "rr_at_k": (1 / first if first else 0.0) if relevant_total else None,
        "ndcg_at_k": dcg / idcg if idcg else None,
        "hit_at_k": int(hits > 0),
        "unjudged_returned": sum(doc_id not in grades for doc_id in top),
        "returned": len(top),
        "relevant_total": relevant_total,
    }


def top_k(items: Iterable[tuple[str, float]], k: int) -> list[tuple[str, float]]:
    """Score descending, ties earlier arrival first. IDs must already be unique.

    Keeps at most k records. Finite float-compatible scores only.
    k=0 returns immediately without consuming the input iterator.
    """
    if type(k) is not int or k < 0:
        raise ValueError("k must be a nonnegative integer")
    if k == 0:
        return []
    heap: list[tuple[float, int, str]] = []
    for order, (doc_id, raw_score) in enumerate(items):
        score = float(raw_score)
        if not math.isfinite(score):
            raise ValueError("scores must be finite")
        item = (score, -order, doc_id)
        if len(heap) < k:
            heapq.heappush(heap, item)
        elif item > heap[0]:
            heapq.heapreplace(heap, item)
    heap.sort(reverse=True)
    return [(doc_id, score) for score, _neg_order, doc_id in heap]


def rrf_scores(rankings: Iterable[Iterable[str]], c: float = 60.0) -> dict[str, float]:
    """Fuse finite ranked lists. A duplicate within one list counts only once.

    The first physical rank is kept; later entries are not renumbered.
    The dictionary insertion order supplies deterministic tie handling to top_k.
    """
    c = float(c)
    if not math.isfinite(c) or c <= 0:
        raise ValueError("c must be finite and positive")
    scores: dict[str, float] = {}
    for ranking in rankings:
        seen: set[str] = set()
        for rank, doc_id in enumerate(ranking, 1):
            if not isinstance(doc_id, str) or not doc_id:
                raise ValueError("evidence IDs must be nonempty strings")
            if doc_id in seen:
                continue
            seen.add(doc_id)
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (c + rank)
    return scores


def rrf(rankings: Iterable[Iterable[str]], k: int, c: float = 60.0) -> list[tuple[str, float]]:
    return top_k(rrf_scores(rankings, c).items(), k)
