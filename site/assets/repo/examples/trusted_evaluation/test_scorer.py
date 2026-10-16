import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scorer import parse_json, score


class ScorerTests(unittest.TestCase):
    def setUp(self):
        self.plan = {'s1': 'cat', 's2': 'dog', 's3': 'cat'}
        self.rows = [{'sample_id': k, 'prediction': v} for k, v in self.plan.items()]

    def test_order_does_not_matter_and_all_correct(self):
        self.assertEqual(score(self.plan, reversed(self.rows)),
                         {'correct': 3, 'sample_count': 3, 'accuracy': 1.0})

    def test_wrong_and_unseen_label_use_fixed_denominator(self):
        self.rows[1]['prediction'] = 'unseen-class'
        self.assertEqual(score(self.plan, self.rows),
                         {'correct': 2, 'sample_count': 3, 'accuracy': 2 / 3})

    def test_one_sample_all_wrong(self):
        self.assertEqual(score({'s': 'a'}, [{'sample_id': 's', 'prediction': 'b'}])['accuracy'], 0)

    def test_empty_or_invalid_plan(self):
        for plan in ({}, [], None, {'': 'a'}, {'s': ''}, {1: 'a'}, {'s': True}):
            with self.subTest(plan=plan), self.assertRaises(ValueError):
                score(plan, [])

    def test_empty_or_missing_predictions(self):
        for rows in ([], self.rows[:-1]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                score(self.plan, rows)

    def test_duplicate_even_with_correct_row_count(self):
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            score(self.plan, [self.rows[0], self.rows[0], self.rows[2]])

    def test_unknown_even_with_correct_row_count(self):
        with self.assertRaisesRegex(ValueError, 'unknown'):
            score(self.plan, [*self.rows[:2], {'sample_id': 'other', 'prediction': 'cat'}])

    def test_adapter_cannot_supply_target_or_score(self):
        for field in ('target', 'gold', 'accuracy'):
            row = dict(self.rows[0], **{field: 'cat'})
            with self.subTest(field=field), self.assertRaises(ValueError):
                score(self.plan, [row, *self.rows[1:]])

    def test_schema_and_types(self):
        for row in (None, [], 'cat', {}, {'sample_id': 's1'},
                    {'prediction': 'cat'},
                    *({'sample_id': value, 'prediction': 'cat'}
                      for value in (None, True, 1, 1.0, [], {}, '', ' ')),
                    *({'sample_id': 's1', 'prediction': value}
                      for value in (None, False, 0, 0.0, [], {}, '', '\t'))):
            with self.subTest(row=row), self.assertRaises(ValueError):
                score(self.plan, [row, *self.rows[1:]])

    def test_strict_json(self):
        for text in ('{', '{"s":"a","s":"b"}', '{"s":NaN}', '{"s":Infinity}'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_json(text)

    def test_cli_and_rejected_input_have_no_score(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan, rows = Path(tmp) / 'plan.json', Path(tmp) / 'predictions.jsonl'
            plan.write_text(json.dumps(self.plan), encoding='utf-8')
            rows.write_text('\n'.join(map(json.dumps, self.rows)) + '\n', encoding='utf-8')
            command = [sys.executable, '-B', str(Path(__file__).with_name('scorer.py')), str(plan), str(rows)]
            result = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['accuracy'], 1)
            for bad in ('\n', '{bad}\n', '{"sample_id":"s1","sample_id":"s2","prediction":"cat"}\n'):
                rows.write_text(bad, encoding='utf-8')
                result = subprocess.run(command, text=True, capture_output=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, '')


if __name__ == '__main__':
    unittest.main(verbosity=2)
