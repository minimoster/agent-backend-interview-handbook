import concurrent.futures
import unittest
from contracts import (InMemoryJobs, ParameterConflict, fingerprint,
                       nested_attempt_bound, persistence_failure_trace)


class TeachingContracts(unittest.TestCase):
    def test_same_identity_and_canonical_object_keys(self):
        jobs = InMemoryJobs()
        first = jobs.submit('tenant-a', 'compute', 'key-1', {'target': 'table-a', 'version': 3})
        repeat = jobs.submit('tenant-a', 'compute', 'key-1', {'version': 3, 'target': 'table-a'})
        self.assertEqual(first.job_id, repeat.job_id)
        self.assertEqual(repeat.status, 'running')

    def test_same_key_parameter_misuse_is_a_conflict(self):
        jobs = InMemoryJobs()
        jobs.submit('tenant-a', 'compute', 'key-1', {'version': 3})
        with self.assertRaises(ParameterConflict):
            jobs.submit('tenant-a', 'compute', 'key-1', {'version': 4})

    def test_identity_separates_tenants_operations_and_explicit_new_runs(self):
        jobs = InMemoryJobs()
        identities = [('a', 'compute', 'key-1'), ('b', 'compute', 'key-1'),
                      ('a', 'publish', 'key-1'), ('a', 'compute', 'key-2')]
        self.assertEqual(len({jobs.submit(*key, {'version': 3}).job_id for key in identities}), 4)

    def test_concurrent_duplicates_have_one_local_job(self):
        jobs = InMemoryJobs()
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
            results = list(pool.map(lambda _: jobs.submit('a', 'compute', 'key', {'version': 3}), range(100)))
        self.assertEqual(len({job.job_id for job in results}), 1)

    def test_finished_repeat_returns_same_identity_and_new_status(self):
        jobs = InMemoryJobs()
        first = jobs.submit('a', 'compute', 'key', {})
        jobs.finish('a', 'compute', 'key')
        repeat = jobs.submit('a', 'compute', 'key', {})
        self.assertEqual(first.job_id, repeat.job_id)
        self.assertEqual(repeat.status, 'succeeded')

    def test_missing_null_and_nonfinite_have_explicit_demo_contract(self):
        self.assertNotEqual(fingerprint({}), fingerprint({'value': None}))
        with self.assertRaises(ValueError):
            fingerprint({'value': float('nan')})

    def test_counting_attempts_differs_from_counting_additional_retries(self):
        self.assertEqual(nested_attempt_bound(3, 3), 9)
        self.assertEqual(nested_attempt_bound(3, 3, counts_extra_retries=True), 16)
        self.assertEqual(nested_attempt_bound(0, 0, counts_extra_retries=True), 1)
        with self.assertRaises(ValueError):
            nested_attempt_bound(0, 3)

    def test_failure_before_and_after_rename_is_not_rollback(self):
        for stage in ('write', 'file_sync', 'rename', 'directory_sync'):
            trace = persistence_failure_trace(stage)
            self.assertTrue(trace['returned_error'])
            self.assertEqual(trace['ram'], 'new')
            self.assertEqual(trace['visible_disk'], 'new' if stage == 'directory_sync' else 'old')
            self.assertEqual(trace['power_loss_durability'], 'unknown')


if __name__ == '__main__':
    unittest.main(verbosity=2)
