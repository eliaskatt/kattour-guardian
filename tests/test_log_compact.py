"""Tests for deterministic diagnostic-log filtering."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/kattour-guardian/scripts/log_compact.py'


def run_log(log, *args):
    return subprocess.run([sys.executable, str(SCRIPT), '-', *args],
                          input=log, capture_output=True, text=True, check=False)


class LogTests(unittest.TestCase):
    def test_prioritizes_failure_and_skips_noise(self):
        log = '\n'.join(['build success'] * 300 + ['TypeError: something broke', 'at checkout'])
        result = run_log(log, '--max-chars', '700')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('TypeError', result.stdout)
        self.assertNotIn('L20:', result.stdout)
        self.assertLessEqual(len(result.stdout), 700)

    def test_redacts_credentials(self):
        result = run_log('WARNING: token=secretreallylong\nERROR: login failed\n')
        self.assertEqual(result.returncode, 0)
        self.assertNotIn('secretreallylong', result.stdout)
        self.assertIn('REDACTED', result.stdout)

    def test_falls_back_to_tail_when_no_errors(self):
        result = run_log('first\nsecond\nthird\n', '--tail-lines', '1')
        self.assertEqual(result.returncode, 0)
        self.assertIn('third', result.stdout)
        self.assertNotIn('L1:', result.stdout)


if __name__ == '__main__':
    unittest.main()
