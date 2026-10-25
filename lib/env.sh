#!/usr/bin/env bash
# agentdots/lib/env.sh
# Persistent agentdots environment helpers. Source this file; do not execute it.
# Writes AGENT_DOTS_DIR + alias into the same ~/.dotfiles-env.sh that appdots
# and hyprdots use, so one file carries every *dots repo location.

agentdots_env_file() {
  printf '%s/.dotfiles-env.sh\n' "$HOME"
}

# Read only the literal export produced by ensure_agentdots_env; do not source
# arbitrary shell code when determining ownership of a previous checkout.
installed_agentdots_dir() {
  local env_file line result=""
  env_file="$(agentdots_env_file)"
  [[ -f "$env_file" ]] || return 0
  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" =~ ^export\ AGENT_DOTS_DIR=\"(/[^\"]+)\"$ ]]; then
      result="${BASH_REMATCH[1]}"
    fi
  done < "$env_file"
  [[ "$result" != / ]] || result=""
  printf '%s\n' "$result"
}

ensure_agentdots_env() {
  local repo_dir="$1"
  local env_file
  env_file="$(agentdots_env_file)"
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
