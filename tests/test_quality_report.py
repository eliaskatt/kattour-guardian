"""Quality report should be truthful, bounded and avoid source disclosure."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/kattour-guardian/scripts'))
import quality_report


class QualityReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_empty_project_requires_manual_review(self):
        report = quality_report.review(self.root)
        self.assertEqual(report['summary']['total_findings'], 0)
        self.assertEqual(report['status'], 'manual_verification_required')
        self.assertTrue(report['not_tested'])

    def test_findings_prioritized_and_limited(self):
        (self.root / 'index.html').write_text('<html><head></head><body><img src="x"></body></html>', encoding='utf8')
        (self.root / 'server.py').write_text('x = "nothing"\n' + ('verify' + '=False\n') * 3, encoding='utf8')
        report = quality_report.review(self.root, max_findings=1)
        self.assertTrue(report['summary']['truncated'])
        self.assertEqual(report['findings'][0]['severity'], 'high')
        self.assertEqual(report['status'], 'review_high_priority')
        self.assertNotIn('nothing', quality_report.markdown(report))

    def test_max_limit_validation(self):
        with self.assertRaises(ValueError):
            quality_report.review(self.root, 0)
        with self.assertRaises(ValueError):
            quality_report.review(self.root / 'missing')


if __name__ == '__main__':
    unittest.main()
