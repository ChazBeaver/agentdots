#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

REPO_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
fixture_dir="$(mktemp -d)"
trap 'rm -rf -- "$fixture_dir"' EXIT
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }

mkdir -p "$fixture_dir/lib" "$fixture_dir/tests"
cp "$REPO_DIR/test.sh" "$fixture_dir/test.sh"
cp "$REPO_DIR/lib/log.sh" "$fixture_dir/lib/log.sh"
if bash "$fixture_dir/test.sh" >/dev/null 2>&1; then
  fail "an empty test directory reported success"
fi
cat > "$fixture_dir/tests/01-fails.sh" <<'SUITE'
#!/usr/bin/env bash
printf 'first\n' >> "$TEST_RUNNER_TRACE"
exit 7
SUITE
cat > "$fixture_dir/tests/02-passes.sh" <<'SUITE'
#!/usr/bin/env bash
printf 'second\n' >> "$TEST_RUNNER_TRACE"
SUITE
export TEST_RUNNER_TRACE="$fixture_dir/trace"
if bash "$fixture_dir/test.sh" >/dev/null 2>&1; then
  fail "a failed suite was hidden by a later passing suite"
fi
[[ "$(cat "$TEST_RUNNER_TRACE")" == $'first\nsecond' ]] || fail "runner skipped a suite after a failure"
rm "$fixture_dir/tests/01-fails.sh" "$TEST_RUNNER_TRACE"
bash "$fixture_dir/test.sh" >/dev/null || fail "passing suites reported failure"
[[ "$(cat "$TEST_RUNNER_TRACE")" == second ]] || fail "passing suite did not run"
if bash "$fixture_dir/test.sh" --help >/dev/null 2>&1; then
  fail "runner accepted an unsupported argument"
fi

printf 'PASS: test runner executes every suite and preserves failures\n'
