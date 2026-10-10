"""Small in-memory teaching contracts, not a durable or distributed service."""
from dataclasses import dataclass
import hashlib
import json
import threading


class ParameterConflict(ValueError):
    """A caller reuses the same operation identity with different parameters."""


def fingerprint(parameters):
    """Canonical JSON object-key order; a real API first validates its schema.

    This demo does not equate different numeric encodings or normalize Unicode,
    dates, units, missing fields and nulls. Those choices need an API contract.
    """
    encoded = json.dumps(parameters, sort_keys=True, separators=(',', ':'),
                         ensure_ascii=False, allow_nan=False).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class Job:
    job_id: str
    request_fingerprint: str
    status: str = 'running'


class InMemoryJobs:
    """Serialize local identity lookup/creation; no database or external action."""
    def __init__(self):
        self._lock = threading.Lock()
        self._jobs = {}
        self._next_id = 0

    def submit(self, tenant, operation, caller_key, parameters):
        if any(type(value) is not str or not value for value in (tenant, operation, caller_key)):
            raise ValueError('identity components must be nonempty strings')
        identity = (tenant, operation, caller_key)
        digest = fingerprint(parameters)
        with self._lock:
            current = self._jobs.get(identity)
            if current is not None:
                if current.request_fingerprint != digest:
                    raise ParameterConflict('same caller identity, different parameters')
                return current
            self._next_id += 1
            current = Job(f'teaching-job-{self._next_id}', digest)
            self._jobs[identity] = current
            return current

    def finish(self, tenant, operation, caller_key):
        identity = (tenant, operation, caller_key)
        with self._lock:
            current = self._jobs[identity]
            complete = Job(current.job_id, current.request_fingerprint, 'succeeded')
            self._jobs[identity] = complete
            return complete


def nested_attempt_bound(inner, outer, *, counts_extra_retries=False):
    """Worst-case attempts before deadlines/stop conditions; not retry logic."""
    minimum = 0 if counts_extra_retries else 1
    if any(type(n) is not int or n < minimum for n in (inner, outer)):
        raise ValueError('invalid attempt/retry counts')
    addition = 1 if counts_extra_retries else 0
    return (inner + addition) * (outer + addition)


def persistence_failure_trace(stage):
    """Deterministic counterexample model, not an OS/fsync or project test.

    RAM changes before persistence. Visible disk changes at rename. An error
    after rename can leave both changed. Power-loss durability is unspecified.
    """
    stages = ('write', 'file_sync', 'rename', 'directory_sync')
    if stage not in stages:
        raise ValueError('unknown injection stage')
    ram = 'new'
    visible_disk = 'new' if stage == 'directory_sync' else 'old'
    return {'returned_error': True, 'ram': ram, 'visible_disk': visible_disk,
            'restart_without_power_loss': visible_disk, 'power_loss_durability': 'unknown'}
