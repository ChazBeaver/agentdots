#!/usr/bin/env bash
# agentdots/lib/targets.sh
# The single source of truth for where skills get linked. Source this; do not execute.
#
# Every skills/<name>/ in this repo is symlinked into EACH of these directories.
# Add a line to reach a new tool; remove one to stop targeting it. Directories
# are created on demand by link_item, so listing a tool that is not installed
# yet is harmless.

skill_targets() {
  cat <<TARGETS
$HOME/.claude/skills
$HOME/.codex/skills
$HOME/.agents/skills
$HOME/.config/opencode/skills
TARGETS
}

# skill_target_label DIR -> short human name for log lines
skill_target_label() {
  case "$1" in
    "$HOME/.claude/skills")          echo "claude" ;;
    "$HOME/.codex/skills")           echo "codex" ;;
    "$HOME/.agents/skills")          echo "agents" ;;
    "$HOME/.config/opencode/skills") echo "opencode" ;;
    *)                               basename "$(dirname "$1")" ;;
  esac
}
