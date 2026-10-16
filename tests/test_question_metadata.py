import importlib.util
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('question_metadata', ROOT / 'tools/refresh_question_metadata.py')
metadata = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metadata)


class QuestionMetadataTests(unittest.TestCase):
    def test_lengths_match_documented_unicode_scope(self):
        records = json.loads((ROOT / 'coverage/all-question-manifest.json').read_text())
        measured = metadata.lengths(records)
        self.assertEqual({r['id']: r['chars'] for r in records}, measured)
        r12 = next(r for r in records if r['id'] == 'R12')
        text = (ROOT / r12['path']).read_text()
        heading = re.search(r'(?m)^#{2,3} R12 .+$', text)
        self.assertEqual(r12['chars'], len(text[heading.start():]))
        self.assertGreater(r12['chars'], 200)

    def test_index_section_counts_are_derived(self):
        text = (ROOT / 'QUESTION_INDEX.md').read_text()
        self.assertEqual(text, metadata.counted_index(text))
        self.assertIn('## Agent补充 · 23题', text)

    def test_count_repair_cannot_replace_other_numbers(self):
        sample = '409 Conflict\n4096 sequence values\n## Section · 63题\n- [A](a.md)\n- [B](b.md)\n\n## Other\n'
        output = metadata.counted_index(sample)
        self.assertIn('## Section · 2题', output)
        self.assertIn('409 Conflict\n4096 sequence values', output)

    def test_index_manifest_and_document_ownership_match(self):
        manifest = json.loads((ROOT / 'coverage/all-question-manifest.json').read_text())
        index = json.loads((ROOT / 'content-index.json').read_text())
        ids = {r['id'] for r in manifest}
        items = [r for r in index['items'] if r['kind'] == 'interview_question']
        self.assertEqual(len(ids), len(manifest))
        self.assertEqual(ids, {r['id'] for r in items})
        self.assertEqual(len(items), index['counts']['interview_questions'])
        owners = json.loads((ROOT / 'coverage/document-index.json').read_text())
        owned = [q for r in owners for q in r['question_ids']]
        self.assertEqual(len(owned), len(set(owned)))
        self.assertEqual(set(owned), ids)
        self.assertEqual(index['counts']['total_items'], len(index['items']))
        self.assertEqual(sum(r['kind'] == 'algorithm_problem' for r in index['items']), 100)
        self.assertEqual(index['counts']['hot100_problems'], 100)

    def test_critical_numeric_contracts_survive(self):
        network = (ROOT / 'docs/40-backend/01-network-and-streaming.md').read_text()
        snowflake = (ROOT / 'docs/40-backend/34-distributed-systems-details.md').read_text()
        self.assertRegex(network, r'409[^\n]*冲突')
        self.assertRegex(snowflake, r'4096')
        self.assertNotIn('3616', snowflake)

    def test_all_agent_followups_have_answers_and_acceptance(self):
        files = ['docs/10-agent/01-agent-loop-tools-and-state.md',
                 'docs/10-agent/02-rag-retrieval-and-reranking.md',
                 'docs/10-agent/03-memory-and-context.md',
                 'docs/10-agent/04-streaming-and-reliable-execution.md',
                 'docs/50-projects/public-repository-case-studies.md']
        answered = set()
        for file in files:
            text = (ROOT / file).read_text()
            matches = list(re.finditer(r'(?m)^### (A\d{2}) .+$', text))
            for i, match in enumerate(matches):
                end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
                block = text[match.start():end]
                self.assertIn('#### 参考答案', block, match[1])
                self.assertIn('**验收点：**', block, match[1])
                answered.add(match[1])
        self.assertEqual(answered, {f'A{i:02d}' for i in [*range(1, 31), *range(39, 48)]})


if __name__ == '__main__':
    unittest.main(verbosity=2)
