#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
# agentdots/sync.sh
# Declarative symlink sync for agent skills. Idempotent, safe to run repeatedly.
# Every skills/<name>/ (with a SKILL.md) is linked into every directory listed
# in lib/targets.sh. Stale links that point into this repo are pruned.
#
# New machine:  git clone <repo> ~/Projects/home/agentdots && cd there && ./sync.sh
# After pull:   ./sync.sh

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]:-${(%):-%N}}")" &>/dev/null && pwd)"
SKILLS_DIR="$SCRIPT_DIR/skills"

# shellcheck source=lib/log.sh
source "$SCRIPT_DIR/lib/log.sh"
# shellcheck source=lib/detect.sh
source "$SCRIPT_DIR/lib/detect.sh"
# shellcheck source=lib/targets.sh
source "$SCRIPT_DIR/lib/targets.sh"
# shellcheck source=lib/link.sh
source "$SCRIPT_DIR/lib/link.sh"
# shellcheck source=lib/env.sh
source "$SCRIPT_DIR/lib/env.sh"

OS="$(detect_os)"
previous_repo_dir="$(installed_agentdots_dir)"
preflight_install "$SCRIPT_DIR" "$previous_repo_dir"

cat <<'EOB'

   ___   _____ _____ _   _ _____ ______ _____ _____ _____
  / _ \ |  __ \  ___| \ | |_   _||  _  \  _  |_   _/  ___|
 / /_\ \| |  \/ |__ |  \| | | |  | | | | | | | | | \ `--.
 |  _  || | __|  __|| . ` | | |  | | | | | | | | |  `--. \
 | | | || |_\ \ |___| |\  | | |  | |/ /\ \_/ / | | /\__/ /
 \_| |_/ \____|____/\_| \_/ \_/  |___/  \___/  \_/ \____/

                    Syncing Agentdots

EOB

log_info "OS: $OS"
echo

# ---- Targets ----
log_step "Targets:"
while IFS= read -r t; do
  [ -n "$t" ] || continue
  printf '   %-10s %s\n' "$(skill_target_label "$t")" "$t"
done < <(skill_targets)
echo

# ---- Backup anything real that would be replaced ----
log_step "Backing up real directories that sync would replace..."
"$SCRIPT_DIR/backup.sh"
echo

# ---- Symlink sync ----
log_step "Linking skills..."
install_skills "$SKILLS_DIR" "$previous_repo_dir"
echo

# ---- Global instructions ----
log_step "Linking global instructions..."
install_instructions "$SCRIPT_DIR"
echo

# ---- Prune ----
log_step "Pruning stale links that point into this repo..."
prune_stale_links "$SCRIPT_DIR" "$previous_repo_dir"
echo

# Persist the new location only after successful convergence, so a retry can
# still identify links owned by a checkout that was moved.
ensure_agentdots_env "$SCRIPT_DIR"
log_info "AGENT_DOTS_DIR: $AGENT_DOTS_DIR"

log_ok "Sync complete."
log_info "Open a new terminal session to use the 'agentdots' alias."
