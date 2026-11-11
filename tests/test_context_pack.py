"""Token-aware context packer regression tests. No network dependencies."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKER = ROOT / 'skills/kattour-guardian/scripts/context_pack.py'


def run(*args):
    return subprocess.run([sys.executable, str(PACKER), *map(str, args)],
                          capture_output=True, text=True, check=False)


class ContextPackTests(unittest.TestCase):
    def test_map_mode_does_not_emit_full_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / 'checkout.py').write_text('def calculate_checkout():\n    return "private business detail"\n', encoding='utf-8')
            result = run(p, '--task', 'checkout calculation', '--mode', 'map', '--max-chars', 800)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('calculate_checkout', result.stdout)
            self.assertNotIn('private business detail', result.stdout)
            self.assertLessEqual(len(result.stdout), 800)

    def test_snippets_select_relevant_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / 'billing.py').write_text('def invoice():\n    return 123\n', encoding='utf-8')
            (p / 'checkout.py').write_text('def checkout():\n    return "checkout totals"\n', encoding='utf-8')
            result = run(p, '--task', 'checkout totals', '--mode', 'snippets', '--max-files', 1, '--max-chars', 900)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('checkout.py', result.stdout)
            self.assertNotIn('billing.py', result.stdout)
            self.assertIn('return "checkout totals"', result.stdout)

    def test_redact_common_credentials_in_map_and_snippets(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            secret = 'super-sensitive-password-12345'
            (p / 'auth.py').write_text('def auth(password="' + secret + '"):\n    return True\n', encoding='utf-8')
            for mode in ('map', 'snippets'):
                result = run(p, '--task', 'auth password', '--mode', mode, '--max-chars', 900)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn(secret, result.stdout)
                self.assertIn('REDACTED', result.stdout)

    def test_ignores_dependencies_and_dot_env(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / 'node_modules').mkdir()
            (p / 'node_modules' / 'danger.py').write_text('danger\n')
            (p / '.env.production').write_text('SECRET=sensitive-value\n')
            (p / 'app.py').write_text('def hello(): return 2\n')
            result = run(p, '--task', 'app', '--mode', 'map', '--max-chars', 900)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn('danger.py', result.stdout)
            self.assertNotIn('.env.production', result.stdout)
            self.assertIn('app.py', result.stdout)

    def test_snapshots_send_delta_only_and_reinclude_changed_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            code = p / 'checkout.py'
            code.write_text('def checkout(): return 1\n', encoding='utf-8')
            snapshot = p / '.guardian-cache' / 'state.json'
            args = ('--task', 'checkout', '--mode', 'map', '--max-chars', '900')
            first = run(p, *args, '--snapshot-out', snapshot)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertIn('checkout.py', first.stdout)
            stored = json.loads(snapshot.read_text())
            self.assertIn('checkout.py', stored['hashes'])
            self.assertNotIn('def checkout()', snapshot.read_text())
            second = run(p, *args, '--snapshot-in', snapshot, '--snapshot-out', snapshot)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertNotIn('`checkout.py`', second.stdout)
            code.write_text('def checkout(): return 2\n', encoding='utf-8')
            third = run(p, *args, '--snapshot-in', snapshot, '--snapshot-out', snapshot)
            self.assertEqual(third.returncode, 0, third.stderr)
            self.assertIn('`checkout.py`', third.stdout)

    def test_snapshot_scope_mismatch_fails_loudly(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / 'app.py').write_text('x=1\n')
            snap = p / 'snapshot.json'
            self.assertEqual(run(p, '--task', 'task one', '--snapshot-out', snap).returncode, 0)
            mismatch = run(p, '--task', 'task two', '--snapshot-in', snap)
            self.assertNotEqual(mismatch.returncode, 0)
            self.assertIn('scope', mismatch.stderr.lower())

    def test_changed_only_requires_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / 'app.py').write_text('x=1\n')
            result = run(p, '--task', 'app', '--changed-only')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Git', result.stderr)

    def test_changed_only_handles_staged_and_untracked(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            def git(*args):
                return subprocess.run(['git', '-C', str(p), *args], capture_output=True, check=False)
            self.assertEqual(git('init', '-q').returncode, 0)
            git('config', 'user.email', 'test@example.org')
            git('config', 'user.name', 'Test')
            (p / 'stable.py').write_text('def stable(): return 1\n')
            git('add', 'stable.py')
            self.assertEqual(git('commit', '-m', 'baseline', '-q').returncode, 0)
            (p / 'new_checkout.py').write_text('def checkout(): return 1\n')
            result = run(p, '--task', 'checkout', '--mode', 'map', '--changed-only', '--max-chars', 900)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('new_checkout.py', result.stdout)
            self.assertNotIn('`stable.py`', result.stdout)

    def test_budget_is_hard_cap_even_when_many_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            for i in range(40):
                (p / f'component_{i}.py').write_text('def checkout_component():\n    pass\n' * 20)
            result = run(p, '--task', 'checkout component', '--mode', 'snippets', '--max-chars', 600)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertLessEqual(len(result.stdout), 600)

    def test_metrics_are_labeled_as_estimates(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / 'app.py').write_text('def hello(): return 1\n')
            result = run(p, '--task', 'hello', '--max-chars', 900, '--metrics')
            self.assertEqual(result.returncode, 0, result.stderr)
            metrics = json.loads(result.stderr)
            self.assertIn('approximate_output_tokens', metrics)
            self.assertIn('rough', metrics['warning'])


if __name__ == '__main__':
    unittest.main()
