"""Provider token counters and privacy invariants."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/kattour-guardian/scripts'))
import provider_usage


class ProviderUsageTests(unittest.TestCase):
    def test_openai_responses(self):
        row = provider_usage.normalize({'object': 'response', 'usage': {
            'input_tokens': 110, 'output_tokens': 20, 'total_tokens': 130,
            'input_tokens_details': {'cached_tokens': 50}}})
        self.assertEqual((row['provider'], row['cached_input_tokens']), ('openai', 50))

    def test_openai_chat(self):
        row = provider_usage.normalize({'usage': {'prompt_tokens': 80, 'completion_tokens': 20, 'total_tokens': 100}})
        self.assertEqual(row['total_tokens'], 100)

    def test_anthropic_with_cache(self):
        row = provider_usage.normalize({'type': 'message', 'usage': {
            'input_tokens': 40, 'output_tokens': 10,
            'cache_read_input_tokens': 80, 'cache_creation_input_tokens': 30}})
        self.assertEqual(row['input_tokens'], 150)
        self.assertEqual(row['total_tokens'], 160)

    def test_anthropic_with_explicit_provider(self):
        row = provider_usage.normalize({'usage': {'input_tokens': 42, 'output_tokens': 8}}, 'anthropic')
        self.assertEqual(row['total_tokens'], 50)

    def test_gemini(self):
        row = provider_usage.normalize({'usageMetadata': {
            'promptTokenCount': 110, 'candidatesTokenCount': 20,
            'totalTokenCount': 140, 'cachedContentTokenCount': 50}})
        self.assertEqual(row['total_tokens'], 140)

    def test_ambiguous_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            provider_usage.normalize({'usage': {'input_tokens': 30, 'output_tokens': 10}})

    def test_bad_types_and_malformed_counts(self):
        for bad in (True, -5, '500'):
            with self.assertRaises(ValueError):
                provider_usage.normalize({'usage': {'prompt_tokens': bad, 'completion_tokens': 2}})
        with self.assertRaises(ValueError):
            provider_usage.normalize({'usage': {'prompt_tokens': 20, 'completion_tokens': 10,
                                                'total_tokens': 29}})
        with self.assertRaises(ValueError):
            provider_usage.normalize({'usageMetadata': {'promptTokenCount': 10,
                                                        'candidatesTokenCount': 3,
                                                        'cachedContentTokenCount': 11}})

    def test_private_payload_not_returned(self):
        text = 'sensitive prompt text should never be echoed'
        result = provider_usage.aggregate([{'object': 'response', 'input': text,
                                            'usage': {'input_tokens': 4, 'output_tokens': 1}}])
        self.assertNotIn(text, json.dumps(result))
        self.assertEqual(result['records'], 1)

    def test_before_after_comparison(self):
        base = provider_usage.aggregate([{'usage': {'prompt_tokens': 200, 'completion_tokens': 100}}])
        after = provider_usage.aggregate([{'usage': {'prompt_tokens': 100, 'completion_tokens': 50}}])
        result = provider_usage.compare(base, after)
        self.assertEqual(result['difference_tokens'], 150)
        self.assertEqual(result['reduction_percent'], 50)
        self.assertIn('not costs', result['warning'])

    def test_local_jsonl_and_symlink_refusal(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'usage.jsonl'
            p.write_text('\n'.join(json.dumps({'usage': {'prompt_tokens': x, 'completion_tokens': 1}})
                                   for x in (10, 15)), encoding='utf8')
            self.assertEqual(provider_usage.aggregate(provider_usage.load(p, True))['total_tokens'], 27)
            link = Path(folder) / 'link.jsonl'
            link.symlink_to(p)
            with self.assertRaises(ValueError):
                provider_usage.load(link, True)

    def test_no_records_rejected(self):
        with self.assertRaises(ValueError):
            provider_usage.aggregate([])


if __name__ == '__main__':
    unittest.main()
