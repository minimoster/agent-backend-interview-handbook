"""Original in-memory teaching model. No provider, payment or persistence."""
from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Callable


@dataclass(frozen=True)
class Quote:
    merchant: str
    item: str
    specification: str
    quantity: int
    total_cents: int
    currency: str
    destination: str
    revision: str

    def validate(self) -> None:
        if type(self.quantity) is not int or self.quantity <= 0:
            raise ValueError("positive integer quantity required")
        if type(self.total_cents) is not int or self.total_cents < 0:
            raise ValueError("non-negative integer total required")
        for k, v in vars(self).items():
            if k not in {"quantity", "total_cents"} and (
                not isinstance(v, str) or not v.strip()
            ):
                raise ValueError(f"missing quote field: {k}")

    def fingerprint(self) -> str:
        self.validate()
        body = json.dumps(vars(self), sort_keys=True, ensure_ascii=False)
        return sha256(body.encode()).hexdigest()


@dataclass(frozen=True)
class Approval:
    # Only a trusted application confirmation boundary may create approvals.
    principal: str
    quote_fingerprint: str
    action: str = "create_order"


@dataclass
class OrderTask:
    principal: str
    operation_id: str
    quote: Quote | None = None
    state: str = "draft"
    approved_fingerprint: str | None = None
    order_id: str | None = None
    observations: list[dict] = field(default_factory=list)

    def preview(self, quote: Quote) -> None:
        if self.state not in {"draft", "preview", "approved"}:
            raise RuntimeError("cannot replace quote after execution or cancellation")
        quote.validate()
        self.quote = quote
        self.approved_fingerprint = None
        self.state = "preview"

    def approve(self, approval: Approval) -> None:
        if self.state != "preview" or self.quote is None:
            raise RuntimeError("preview required")
        if approval.principal != self.principal or approval.action != "create_order":
            raise PermissionError("approval scope mismatch")
        if approval.quote_fingerprint != self.quote.fingerprint():
            raise PermissionError("approval does not match current preview")
        self.approved_fingerprint = approval.quote_fingerprint
        self.state = "approved"

    def cancel(self) -> None:
        if self.state in {"submitting", "unknown", "succeeded"}:
            raise RuntimeError("query provider; local cancellation cannot undo an order")
        self.approved_fingerprint = None
        self.state = "cancelled"

    def submit(self, create_order: Callable[[str, Quote], str]) -> str:
        if self.state == "succeeded":
            assert self.order_id is not None
            return self.order_id
        if self.state != "approved" or self.quote is None:
            raise RuntimeError("matching approval required; unknown outcomes need reconciliation")
        if self.approved_fingerprint != self.quote.fingerprint():
            raise PermissionError("quote changed after approval")
        self.state = "submitting"
        try:
            order_id = create_order(self.operation_id, self.quote)
        except Exception:
            # Conservatively unknown: an exception does not prove no side effect.
            self.state = "unknown"
            self.observations.append({"operation_id": self.operation_id, "state": "unknown"})
            raise
        if not isinstance(order_id, str) or not order_id:
            self.state = "unknown"
            raise ValueError("provider result lacks verifiable order identity")
        self.order_id = order_id
        self.state = "succeeded"
        self.observations.append({"operation_id": self.operation_id, "state": "succeeded"})
        return order_id

    def reconcile_created(self, operation_id: str, verified_order_id: str) -> None:
        """Call only with an independently verified provider lookup result."""
        if self.state != "unknown" or operation_id != self.operation_id:
            raise RuntimeError("reconciliation identity/state mismatch")
        if not isinstance(verified_order_id, str) or not verified_order_id:
            raise ValueError("verified provider identity required")
        self.order_id = verified_order_id
        self.state = "succeeded"


def run_bounded(actions: list[str], max_steps: int) -> tuple[str, int]:
    """Toy control-loop model: budget is checked before consuming an action."""
    if type(max_steps) is not int or max_steps < 0:
        raise ValueError("non-negative step budget required")
    seen = set()
    for step, observation_signature in enumerate(actions):
        if step >= max_steps:
            return "budget_exhausted", step
        if observation_signature in seen:
            return "no_progress", step + 1
        seen.add(observation_signature)
    return "input_exhausted", len(actions)
