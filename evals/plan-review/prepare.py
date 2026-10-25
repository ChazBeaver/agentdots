#!/usr/bin/env python3
"""Prepare disposable working-change review cases; never invoke an agent."""

import argparse
import hashlib
import json
import os
import random
import subprocess
import tempfile
from pathlib import Path


INSTRUCTIONS = """# Validator repository instructions

This repository owns a small Python command. Use only the standard library.
Run isolated checks with `python3 -B tests/test_validate.py`.
During review, leave source files and Git state unchanged.
"""

BRIEF = """# Task brief: validate a small integer

## Outcome and original request

Implement `bin/validate.py`. It accepts exactly one argument containing one
to three ASCII decimal digits whose numeric value is between 1 and 100.
Leading zeros within that length are allowed. All other invocations are invalid.

## Scope and authorization

Review the current working changes, including staged, unstaged, and relevant
untracked files. The implementation and its tests are in scope. Existing user
work under `notes/` is unrelated and excluded. Review is read-only; no source
changes, staging, commits, installation, network, or live activation is requested.
`BUILDER.md` contains the builder's claims, which need independent verification.

## Acceptance criteria

- C1: A valid invocation exits 0 and writes exactly `valid` followed by a newline
  to stdout, with no stderr output.
- C2: Every invalid invocation exits 2 and writes exactly `invalid` followed by
  a newline to stderr, with no stdout output. This includes missing or extra
  arguments, out-of-range values, signs, non-ASCII digits, and excessive length.

## Verification and completion evidence

Run `python3 -B tests/test_validate.py` and inspect its coverage. Probe missing
cases directly with `python3 -B bin/validate.py <argument>` as needed. Check
repository standards separately from acceptance criteria. Both C1 and C2 are
NOT VERIFIED until supported by observed evidence. No live environment is needed.
"""

STUB = """import sys

print("not implemented", file=sys.stderr)
sys.exit(2)
"""

CORRECT = """import re
import sys


def main():
    args = sys.argv[1:]
    if (len(args) == 1 and re.fullmatch(r"[0-9]{1,3}", args[0])
            and 1 <= int(args[0]) <= 100):
        print("valid")
        return 0
    print("invalid", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
"""

INCORRECT = """print("valid")
"""

POSITIVE_TESTS = """import subprocess
import sys
import unittest
from pathlib import Path


COMMAND = Path(__file__).resolve().parents[1] / "bin" / "validate.py"


class ValidationTests(unittest.TestCase):
    def test_valid_values(self):
        for value in ["1", "042", "100"]:
            with self.subTest(value=value):
                result = subprocess.run([sys.executable, "-B", str(COMMAND), value],
                                        capture_output=True, text=True)
                self.assertEqual((result.returncode, result.stdout, result.stderr),
                                 (0, "valid\\n", ""))
"""

NEGATIVE_TESTS = """
    def test_invalid_invocations(self):
        for args in [[], ["0"], ["101"], ["-1"], ["1.0"], ["abc"],
                     ["0001"], [""], ["٢"], ["1", "2"]]:
            with self.subTest(args=args):
                result = subprocess.run([sys.executable, "-B", str(COMMAND), *args],
                                        capture_output=True, text=True)
                self.assertEqual((result.returncode, result.stdout, result.stderr),
                                 (2, "", "invalid\\n"))
"""

TEST_MAIN = """

if __name__ == "__main__":
    unittest.main()
"""

SCENARIOS = ["Correct implementation", "Green tests, wrong outcome", "Untracked failure"]


def git(repo, *args):
    # Do not inherit a caller's Git directory, index, hooks, signing, or config.
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0")
    return subprocess.run(
        ["git", "-c", f"core.hooksPath={os.devnull}", "-c", "commit.gpgsign=false",
         "-c", "user.name=Review fixture", "-c", "user.email=fixture@example.invalid",
         "-C", str(repo), *args],
        env=env, check=True, capture_output=True, text=True,
    ).stdout


def write(repo, name, text):
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def prepare(root):
    """Populate an empty, caller-owned scratch directory and return its case map."""
    root = Path(root)
    if root.is_symlink() or not root.is_dir() or any(root.iterdir()):
        raise ValueError("fixture output must be an empty, real directory")
    order = SCENARIOS.copy()
    random.SystemRandom().shuffle(order)
    cases = {}
    for number, scenario in enumerate(order, 1):
        case_id = f"case-{number:02d}"
        repo = root / case_id
        repo.mkdir()
        git(repo, "init", "-q", "--initial-branch=fixture")
        write(repo, "AGENTS.md", INSTRUCTIONS)
        write(repo, "TASK.md", BRIEF)
        write(repo, "BUILDER.md", "All tests passed. C1 and C2 are complete.\n")
        write(repo, "notes/personal.md", "Existing user notes, excluded from this task.\n")
        write(repo, "tests/test_validate.py", POSITIVE_TESTS + TEST_MAIN)
        if scenario != "Untracked failure":
            write(repo, "bin/validate.py", STUB)
        git(repo, "add", ".")
        git(repo, "commit", "-qm", "Fixture baseline")
        write(repo, "bin/validate.py", CORRECT if scenario == "Correct implementation" else INCORRECT)
        if scenario == "Correct implementation":
            git(repo, "add", "bin/validate.py")
            write(repo, "tests/test_validate.py", POSITIVE_TESTS + NEGATIVE_TESTS + TEST_MAIN)
            write(repo, "notes/personal.md", "Existing user notes, excluded from this task.\nUnrelated user edit.\n")
        cases[case_id] = scenario

    project = Path(__file__).resolve().parents[2]
    manifest = {
        "cases": cases,
        "review_skill_sha256": hashlib.sha256(
            (project / "skills/review-changes/SKILL.md").read_bytes()).hexdigest(),
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (root / "answer-key.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return cases


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    root = Path(tempfile.mkdtemp(prefix="agentdots-review-"))
    cases = prepare(root)
    print(f"Prepared temporary cases in {root}")
    for case_id in sorted(cases):
        print(f"  {root / case_id}")
    print("Give each reviewer only its case directory and the review-changes skill.")
    print("Compare with answer-key.json and scenarios.md after saving the reviews.")


if __name__ == "__main__":
    main()
