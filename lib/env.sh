#!/usr/bin/env bash
# agentdots/lib/env.sh
# Persistent agentdots environment helpers. Source this file; do not execute it.
# Writes AGENT_DOTS_DIR + alias into the same ~/.dotfiles-env.sh that appdots
# and hyprdots use, so one file carries every *dots repo location.

ensure_agentdots_env() {
  local repo_dir="$1"
  local env_file="$HOME/.dotfiles-env.sh"
  local escaped_repo_dir
  local expected_export="export AGENT_DOTS_DIR=\"$repo_dir\""

  mkdir -p "$(dirname "$env_file")"
  [[ -e "$env_file" ]] || touch "$env_file"

  escaped_repo_dir="${repo_dir//\\/\\\\}"
  escaped_repo_dir="${escaped_repo_dir//|/\\|}"
  escaped_repo_dir="${escaped_repo_dir//&/\\&}"

  if grep -Fqx "$expected_export" "$env_file"; then
    :
  elif grep -q '^export AGENT_DOTS_DIR=' "$env_file"; then
    sed -i "s|^export AGENT_DOTS_DIR=.*|export AGENT_DOTS_DIR=\"$escaped_repo_dir\"|" "$env_file"
  else
    printf 'export AGENT_DOTS_DIR="%s"\n' "$repo_dir" >> "$env_file"
  fi

  if ! grep -q '^alias agentdots=' "$env_file"; then
    printf '%s\n' 'alias agentdots="cd \$AGENT_DOTS_DIR"' >> "$env_file"
  fi

  export AGENT_DOTS_DIR="$repo_dir"
}
