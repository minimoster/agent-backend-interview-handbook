#!/usr/bin/env python3
"""Refresh only question lengths and count-bearing index section headings.

chars counts Unicode code points, without newline or whitespace normalization,
from the numbered question heading through the start of the next question anchor
or next heading of the same/higher level (exclusive), or EOF. The current
question's explicit anchor is excluded; lower-level follow-up headings belong
to the question. Counts are never replaced in arbitrary prose or code.
"""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
QUESTION = re.compile(r'(?m)^(#{2,3})\s+([A-Z]+\d+)\s+.*$')
HEADING = re.compile(r'(?m)^(#{1,3})\s+.*$')
ANCHOR = re.compile(r'(?m)^<a\s+id=["\']([^"\']+)["\']>\s*</a>\s*$')


def lengths(records):
    by_path = {}
    result = {}
    for record in records:
        by_path.setdefault(record['path'], []).append(record)
    for path, entries in by_path.items():
        text = (ROOT / path).read_text(encoding='utf-8')
        headings = list(HEADING.finditer(text))
        numbered = {m[2]: m for m in QUESTION.finditer(text)}
        current_anchors = {r['anchor'] for r in entries}
        anchors = [m for m in ANCHOR.finditer(text) if m[1] in current_anchors]
        for record in entries:
            q = numbered[record['id']]
            boundaries = [m.start() for m in headings if m.start() > q.start() and len(m[1]) <= len(q[1])]
            boundaries += [m.start() for m in anchors if m.start() > q.start()]
            end = min(boundaries, default=len(text))
            result[record['id']] = len(text[q.start():end])
    return result


def counted_index(text):
    sections = re.split(r'(?m)(^## .+\n)', text)
    for i in range(1, len(sections), 2):
        match = re.fullmatch(r'(## .*? · )\d+(题\n)', sections[i])
        if match:
            count = len(re.findall(r'(?m)^- \[', sections[i + 1]))
            if not count:
                raise ValueError('Count-bearing section has no questions')
            sections[i] = f'{match[1]}{count}{match[2]}'
    return ''.join(sections)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    manifest = ROOT / 'coverage/all-question-manifest.json'
    records = json.loads(manifest.read_text(encoding='utf-8'))
    measured = lengths(records)
    for record in records:
        record['chars'] = measured[record['id']]
    index = ROOT / 'QUESTION_INDEX.md'
    updates = {manifest: json.dumps(records, ensure_ascii=False, indent=2) + '\n',
               index: counted_index(index.read_text(encoding='utf-8'))}
    stale = [str(path.relative_to(ROOT)) for path, text in updates.items() if path.read_text(encoding='utf-8') != text]
    if args.check:
        if stale:
            raise SystemExit('Metadata is stale: ' + ', '.join(stale))
    else:
        for path, text in updates.items():
            path.write_text(text, encoding='utf-8')
    print(f'{len(records)} question lengths and index section counts agree; Unicode code-point scope is documented.')


if __name__ == '__main__':
    main()
