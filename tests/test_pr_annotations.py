import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import pr_annotations


class AnnotationTests(unittest.TestCase):
    def test_emits_redacted_annotation(self):
        data = {'findings': [{'path': 'src/app.py', 'line': 17, 'rule_id': 'KG-SEC-001', 'severity': 'high',
                              'message': 'Very private password=secret1234'}]}
        lines, counts = pr_annotations.render(data)
        self.assertEqual(counts['annotations_emitted'], 1)
        self.assertIn('::error file=src/app.py,line=17', lines[0])
        self.assertNotIn('private', lines[0])
        self.assertNotIn('secret1234', lines[0])

    def test_blocks_injection_and_traversal(self):
        data = {'findings': [{'path': '../token', 'line': 2, 'rule_id': 'KG-SEC-001', 'severity': 'high'},
                             {'path': 'ok.py\n::error::evil', 'line': 3, 'rule_id': 'KG-UX-001', 'severity': 'medium'},
                             {'path': 'ok.py', 'line': True, 'rule_id': 'KG-UX-001', 'severity': 'medium'}]}
        lines, meta = pr_annotations.render(data)
        self.assertEqual(lines, [])
        self.assertEqual(meta['findings_skipped'], 3)

    def test_bound_and_severity(self):
        data = {'findings': [{'path': 'ui.tsx', 'line': x+1, 'rule_id': 'KG-UX-002', 'severity': 'low'} for x in range(10)]}
        lines, meta = pr_annotations.render(data, limit=2)
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[0].startswith('::notice '))
        self.assertEqual(meta['findings_skipped'], 8)


if __name__ == '__main__':
    unittest.main()
