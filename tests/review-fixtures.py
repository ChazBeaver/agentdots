"""Check fixture behavior and Git shape; these are not model evaluations."""

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("review_fixtures", PROJECT / "evals/plan-review/prepare.py")
FIXTURES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FIXTURES)


class ReviewFixtures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="review-fixture-tests-")
        cls.root = Path(cls.temporary.name)
        # A caller's Git routing must not redirect fixture writes elsewhere.
        with patch.dict(os.environ, {"GIT_DIR": str(cls.root / "foreign.git"),
                                     "GIT_WORK_TREE": str(PROJECT),
                                     "GIT_INDEX_FILE": str(cls.root / "foreign-index")}):
            cls.cases = {scenario: cls.root / case_id
                         for case_id, scenario in FIXTURES.prepare(cls.root).items()}

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def command(self, repo, *args):
        return subprocess.run([sys.executable, "-B", str(repo / "bin/validate.py"), *args],
                              capture_output=True, text=True)

    def test_all_bundled_checks_pass(self):
        # Passing these checks is deliberately insufficient for two cases.
        for repo in self.cases.values():
            with self.subTest(repo=repo):
                result = subprocess.run([sys.executable, "-B", "tests/test_validate.py"],
                                        cwd=repo, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_correct_implementation_and_mixed_state(self):
        repo = self.cases["Correct implementation"]
        for args, expected in [(["1"], (0, "valid\n", "")),
                               (["099"], (0, "valid\n", "")),
                               (["100"], (0, "valid\n", "")),
                               ([], (2, "", "invalid\n")),
                               (["101"], (2, "", "invalid\n")),
                               (["0001"], (2, "", "invalid\n")),
                               (["٢"], (2, "", "invalid\n"))]:
            with self.subTest(args=args):
                result = self.command(repo, *args)
                self.assertEqual((result.returncode, result.stdout, result.stderr), expected)
        status = FIXTURES.git(repo, "status", "--porcelain", "--untracked-files=all").splitlines()
        self.assertEqual(set(status), {"M  bin/validate.py", " M tests/test_validate.py", " M notes/personal.md"})

    def test_green_tests_hide_invalid_input_failure(self):
        repo = self.cases["Green tests, wrong outcome"]
        result = self.command(repo, "101")
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "valid\n", ""))
        self.assertEqual(FIXTURES.git(repo, "diff", "--name-only").splitlines(), ["bin/validate.py"])

    def test_untracked_implementation_has_no_tracked_diff(self):
        repo = self.cases["Untracked failure"]
        self.assertEqual(FIXTURES.git(repo, "diff", "HEAD"), "")
        self.assertEqual(FIXTURES.git(repo, "ls-files", "--others", "--exclude-standard").splitlines(),
                         ["bin/validate.py"])
        self.assertEqual(self.command(repo, "bad").returncode, 0)

    def test_git_is_local_and_answers_stay_outside_cases(self):
        self.assertFalse((self.root / "foreign.git").exists())
        self.assertFalse((self.root / "foreign-index").exists())
        self.assertTrue((self.root / "answer-key.json").is_file())
        for repo in self.cases.values():
            with self.subTest(repo=repo):
                self.assertEqual(FIXTURES.git(repo, "remote"), "")
                self.assertEqual(FIXTURES.git(repo, "rev-list", "--count", "HEAD").strip(), "1")
                self.assertFalse((repo / "answer-key.json").exists())

    def test_existing_output_is_preserved(self):
        before = (self.root / "answer-key.json").read_bytes()
        with self.assertRaises(ValueError):
            FIXTURES.prepare(self.root)
        self.assertEqual((self.root / "answer-key.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
