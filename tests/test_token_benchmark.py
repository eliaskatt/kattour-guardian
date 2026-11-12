import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import token_benchmark


def pair(task, first=100, second=60, ok=True):
    return {'task_id': task, 'model': 'test-model', 'quality_before_pass': True,
            'quality_after_pass': ok,
            'before': {'input_tokens': first, 'output_tokens': 0},
            'after': {'input_tokens': second, 'output_tokens': 0}}


class BenchmarkTests(unittest.TestCase):
    def test_three_pairs_and_weighted_savings(self):
        data = token_benchmark.benchmark([pair('one'), pair('two'), pair('three')])
        self.assertEqual(data['status'], 'comparable')
        self.assertEqual(data['weighted_change_percent'], 40.0)
        self.assertEqual(data['median_pair_change_percent'], 40.0)

    def test_failed_quality_is_excluded_and_does_not_claim_success(self):
        data = token_benchmark.benchmark([pair('one'), pair('two', ok=False)], min_pairs=2)
        self.assertEqual(data['status'], 'insufficient_comparable_pairs')
        self.assertEqual(len(data['excluded']), 1)

    def test_duplicate_task_rejected(self):
        with self.assertRaises(ValueError):
            token_benchmark.benchmark([pair('a'), pair('a')])

    def test_invalid_and_boolean_token_counters_rejected(self):
        run = pair('bad')
        run['before']['input_tokens'] = True
        with self.assertRaises(ValueError):
            token_benchmark.benchmark([run], min_pairs=1)

    def test_different_model_rejected(self):
        run = pair('mixed')
        run['after']['model'] = 'another-model'
        with self.assertRaises(ValueError):
            token_benchmark.benchmark([run], min_pairs=1)

    def test_negative_savings_reported(self):
        data = token_benchmark.benchmark([pair('one', second=120)], min_pairs=1)
        self.assertEqual(data['weighted_change_percent'], -20.0)


if __name__ == '__main__':
    unittest.main()
