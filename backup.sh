#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
# agentdots/backup.sh
# Before sync replaces anything, copy REAL (non-symlink) directories that share
# a name with a repo skill into backups/<timestamp>/<tool>/<name>.
# Symlinks are never backed up: they are cheap to recreate and carry no data.
# Safe to run on its own; sync.sh calls it automatically.

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]:-${(%):-%N}}")" &>/dev/null && pwd)"
SKILLS_DIR="$SCRIPT_DIR/skills"
BACKUP_ROOT="$SCRIPT_DIR/backups"

# shellcheck source=lib/log.sh
source "$SCRIPT_DIR/lib/log.sh"
# shellcheck source=lib/targets.sh
source "$SCRIPT_DIR/lib/targets.sh"
# shellcheck source=lib/link.sh
source "$SCRIPT_DIR/lib/link.sh"

stamp="$(date +%Y%m%d-%H%M%S)"
count=0

while IFS= read -r skill; do
  [ -n "$skill" ] || continue
  name="$(basename "$skill")"
  while IFS= read -r target; do
    [ -n "$target" ] || continue
    candidate="$target/$name"
    if [ -e "$candidate" ] && [ ! -L "$candidate" ]; then
      dest="$BACKUP_ROOT/$stamp/$(skill_target_label "$target")/$name"
      mkdir -p "$(dirname "$dest")"
      cp -a "$candidate" "$dest"
      log_backup "Backed up $candidate → $dest"
      count=$((count + 1))
    fi
  done < <(skill_targets)
done < <(list_skills "$SKILLS_DIR")

if [ "$count" -eq 0 ]; then
  log_info "Nothing to back up (no real directories would be replaced)."
else
  log_ok "Backed up $count item(s) to $BACKUP_ROOT/$stamp"
fi
