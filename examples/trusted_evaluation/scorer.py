"""Teaching-only accuracy scorer. The evaluator owns the plan, never the adapter.

Labels and sample IDs are nonempty strings. No coercion, inferred coverage or
adapter-supplied gold is allowed. O(n) expected time and O(n) space.
"""
import argparse
import json
from pathlib import Path


def _string(value):
    return type(value) is str and bool(value.strip())


def score(plan, predictions):
    """Score exact coverage against an independently frozen sample_id -> gold.

    The caller must supply a trusted plan. Copy it before consuming predictions;
    reject the entire run on any schema/coverage/parse error, rather than silently
    shrinking the denominator. Only string classification labels are supported.
    """
    if type(plan) is not dict or not plan:
        raise ValueError('plan must be a nonempty object')
    gold = dict(plan)
    if any(not _string(k) or not _string(v) for k, v in gold.items()):
        raise ValueError('plan IDs and labels must be nonempty strings')
    seen = set()
    correct = 0
    for row in predictions:
        if type(row) is not dict or set(row) != {'sample_id', 'prediction'}:
            raise ValueError('prediction requires only sample_id and prediction')
        sample_id, prediction = row['sample_id'], row['prediction']
        if not _string(sample_id) or not _string(prediction):
            raise ValueError('prediction ID and label must be nonempty strings')
        if sample_id not in gold:
            raise ValueError('unknown sample_id: ' + sample_id)
        if sample_id in seen:
            raise ValueError('duplicate sample_id: ' + sample_id)
        seen.add(sample_id)
        correct += prediction == gold[sample_id]
    if seen != gold.keys():
        raise ValueError('missing predictions for frozen plan')
    return {'correct': correct, 'sample_count': len(gold),
            'accuracy': correct / len(gold)}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def parse_json(text):
    """Reject duplicate keys and nonstandard JSON NaN/Infinity constants."""
    def invalid_constant(value):
        raise ValueError('invalid JSON constant: ' + value)
    return json.loads(text, object_pairs_hook=_unique_object,
                      parse_constant=invalid_constant)


def load_predictions(path):
    with Path(path).open(encoding='utf-8') as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                raise ValueError(f'blank prediction line {line_number}')
            yield parse_json(line)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', help='trusted JSON object: sample_id -> gold')
    parser.add_argument('predictions', help='untrusted JSONL: sample_id/prediction only')
    args = parser.parse_args()
    try:
        plan = parse_json(Path(args.plan).read_text(encoding='utf-8'))
        result = score(plan, load_predictions(args.predictions))
    except (ValueError, OSError) as exc:
        parser.exit(2, f'evaluation rejected: {exc}\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
