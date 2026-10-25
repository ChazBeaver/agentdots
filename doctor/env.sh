#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
# agentdots/doctor/env.sh
# Verify ~/.dotfiles-env.sh carries AGENT_DOTS_DIR pointing at this checkout
# and the agentdots alias. Read-only.

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]:-${(%):-%N}}")" &>/dev/null && pwd)"
REPO_DIR="$(cd -- "$SCRIPT_DIR/.." &>/dev/null && pwd)"

# shellcheck source=../lib/log.sh
source "$REPO_DIR/lib/log.sh"
source "$REPO_DIR/lib/env.sh"
ENV_FILE="$(agentdots_env_file)"

status=0

if [ ! -f "$ENV_FILE" ]; then
  log_err "Missing $ENV_FILE (run ./sync.sh)"
  exit 1
fi

if [[ "$(installed_agentdots_dir)" == "$REPO_DIR" ]]; then
  log_ok "AGENT_DOTS_DIR → $REPO_DIR"
else
  log_err "AGENT_DOTS_DIR missing or points elsewhere in $ENV_FILE"
  status=1
fi

if grep -Fxq 'alias agentdots="cd \$AGENT_DOTS_DIR"' "$ENV_FILE"; then
  log_ok "alias agentdots present"
else
  log_err "alias agentdots missing from $ENV_FILE"
  status=1
fi

exit "$status"
