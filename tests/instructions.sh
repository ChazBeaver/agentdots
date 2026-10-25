#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

REPO_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
fixture_dir="$(mktemp -d)"
trap 'rm -rf -- "$fixture_dir"' EXIT
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }

source "$REPO_DIR/lib/log.sh"
source "$REPO_DIR/lib/targets.sh"
source "$REPO_DIR/lib/link.sh"

# Route only the client target lists into a fixture. HOME and the production
# source-selection/install/diagnostic code retain their normal behavior.
export INSTRUCTION_TEST_TARGET_ROOT="$fixture_dir/clients"
instruction_targets() {
  printf '%s\n' "$INSTRUCTION_TEST_TARGET_ROOT/.claude/CLAUDE.md" \
    "$INSTRUCTION_TEST_TARGET_ROOT/.codex/AGENTS.md" \
    "$INSTRUCTION_TEST_TARGET_ROOT/.config/opencode/AGENTS.md"
}
skill_targets() { printf '%s\n' "$INSTRUCTION_TEST_TARGET_ROOT/skills"; }

checkout="$fixture_dir/checkout"
mkdir -p "$checkout/instructions" "$checkout/doctor"
cp -R "$REPO_DIR/lib" "$checkout/lib"
cp "$REPO_DIR/doctor/symlinks.sh" "$checkout/doctor/symlinks.sh"
cp "$REPO_DIR/AGENTS.md" "$checkout/AGENTS.md"
cp -P "$REPO_DIR/CLAUDE.md" "$checkout/CLAUDE.md"
cp "$REPO_DIR/instructions/global.md" "$checkout/instructions/global.md"
printf '\nREPOSITORY_ONLY_FIXTURE\n' >> "$checkout/AGENTS.md"
declare -f instruction_targets skill_targets >> "$checkout/lib/targets.sh"

assert_installed() {
  local target
  while IFS= read -r target; do
    [[ -L "$target" && "$(readlink "$target")" == "$checkout/instructions/global.md" ]] || fail "wrong global source: $target"
    cmp -s "$target" "$REPO_DIR/instructions/global.md" || fail "global policy changed or local instructions leaked"
  done < <(instruction_targets)
}

# Model an existing machine: every global client still points to root AGENTS.
while IFS= read -r target; do
  mkdir -p "$(dirname -- "$target")"
  ln -s "$checkout/AGENTS.md" "$target"
done < <(instruction_targets)
if bash "$checkout/doctor/symlinks.sh" >/dev/null 2>&1; then
  fail "doctor accepted repository instructions as global policy"
fi

install_instructions "$checkout" >/dev/null || fail "instruction migration failed"
assert_installed
bash "$checkout/doctor/symlinks.sh" >/dev/null || fail "doctor rejected migrated global links"

# A correct second installation should retain the existing symlink objects.
before_links="$(while IFS= read -r target; do ls -di "$target"; done < <(instruction_targets))"
install_instructions "$checkout" >/dev/null || fail "repeated installation failed"
after_links="$(while IFS= read -r target; do ls -di "$target"; done < <(instruction_targets))"
[[ "$before_links" == "$after_links" ]] || fail "repeated installation replaced correct links"
assert_installed

# Moving the checkout must repair global destinations while keeping the
# repository's relative CLAUDE.md link valid.
mv "$checkout" "$fixture_dir/moved-checkout"
checkout="$fixture_dir/moved-checkout"
if bash "$checkout/doctor/symlinks.sh" >/dev/null 2>&1; then
  fail "doctor missed moved-checkout drift"
fi
install_instructions "$checkout" >/dev/null || fail "relocation repair failed"
assert_installed
[[ "$(readlink "$checkout/CLAUDE.md")" == AGENTS.md && -f "$checkout/CLAUDE.md" ]] || fail "local CLAUDE link broke after relocation"
bash "$checkout/doctor/symlinks.sh" >/dev/null || fail "doctor rejected relocated global links"

# A missing shared policy must fail rather than expose the repository rules.
mv "$checkout/instructions/global.md" "$fixture_dir/saved-global.md"
if install_instructions "$checkout" >/dev/null 2>&1; then
  fail "installer accepted a missing global source"
fi
while IFS= read -r target; do
  [[ "$(readlink "$target")" == "$checkout/instructions/global.md" ]] || fail "missing source caused a local-instruction fallback"
done < <(instruction_targets)
if bash "$checkout/doctor/symlinks.sh" >/dev/null 2>&1; then
  fail "doctor missed a missing global source"
fi
mv "$fixture_dir/saved-global.md" "$checkout/instructions/global.md"
assert_installed

unlink "$checkout/CLAUDE.md"
ln -s instructions/global.md "$checkout/CLAUDE.md"
if bash "$checkout/doctor/symlinks.sh" >/dev/null 2>&1; then
  fail "doctor accepted a global-policy link in place of repository instructions"
fi

printf 'PASS: global instruction migration, isolation, idempotence, relocation, and missing-source detection\n'
