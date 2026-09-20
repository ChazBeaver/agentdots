#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
# agentdots/doctor/symlinks.sh
# Verify every symlink sync.sh would create exists and points correctly.
# Read-only. Reports:
#   - DRIFT (error) : link missing, wrong target, replaced by a real dir, or
#                     a link into this repo that no longer resolves
#   - FOREIGN (info): links in a target dir that point outside this repo
#                     (e.g. omarchy's bundled skills). Never drift.

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]:-${(%):-%N}}")" &>/dev/null && pwd)"
REPO_DIR="$(cd -- "$SCRIPT_DIR/.." &>/dev/null && pwd)"
SKILLS_DIR="$REPO_DIR/skills"

# shellcheck source=../lib/log.sh
source "$REPO_DIR/lib/log.sh"
# shellcheck source=../lib/targets.sh
source "$REPO_DIR/lib/targets.sh"
# shellcheck source=../lib/link.sh
source "$REPO_DIR/lib/link.sh"

DRIFT=0

check_link() {
  local source="$1"   # path inside the repo
  local target="$2"   # path in a tool's skills dir

  if [ ! -L "$target" ]; then
    if [ -e "$target" ]; then
      log_err "Not a symlink (real dir): $target"
    else
      log_err "Missing: $target (should link to $source)"
    fi
    DRIFT=1
    return
  fi

  local actual
  actual="$(readlink "$target")"
  if [ "$actual" != "$source" ]; then
    log_err "Wrong target: $target → $actual (expected $source)"
    DRIFT=1
    return
  fi

  if [ ! -e "$target" ]; then
    log_err "Dangling symlink: $target → $source (repo source missing)"
    DRIFT=1
    return
  fi

  log_ok "$target"
}

echo
log_info "Symlink drift check"
echo

skill_count=0
while IFS= read -r skill; do
  [ -n "$skill" ] || continue
  name="$(basename "$skill")"
  log_step "Skill: $name"
  while IFS= read -r target; do
    [ -n "$target" ] || continue
    check_link "$skill" "$target/$name"
  done < <(skill_targets)
  skill_count=$((skill_count + 1))
done < <(list_skills "$SKILLS_DIR")

[ "$skill_count" -gt 0 ] || log_info "No skills in $SKILLS_DIR to check."

echo
log_step "Stale and foreign links in target dirs"
while IFS= read -r target; do
  [ -d "$target" ] || { log_info "Target dir missing (not created yet): $target"; continue; }
  while IFS= read -r link; do
    [ -n "$link" ] || continue
    dest="$(readlink "$link" 2>/dev/null || true)"
    case "$dest" in
      "$REPO_DIR"/*)
        if [ ! -e "$link" ]; then
          log_err "Stale link into repo: $link → $dest"
          DRIFT=1
        fi
        ;;
      *)
        log_info "Foreign: $link → $dest"
        ;;
    esac
  done < <(find "$target" -mindepth 1 -maxdepth 1 -type l | sort)
done < <(skill_targets)

echo
if [ "$DRIFT" -eq 0 ]; then
  log_ok "No symlink drift detected."
  exit 0
else
  log_warn "Symlink drift detected. Run ./sync.sh to fix."
  exit 1
fi
