#!/usr/bin/env bash
# Persistent repository registration. Source this file; do not execute it.

agentdots_env_file() {
  printf '%s/.dotfiles-env.sh\n' "$HOME"
}

# Decode the literal double-quoted path written below, without sourcing code.
installed_agentdots_dir() {
  local env_file="${1:-$(agentdots_env_file)}" line result=""
  [[ -f "$env_file" ]] || return 0
  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" == 'export AGENT_DOTS_DIR="'*'"' ]]; then
      result="${line#export AGENT_DOTS_DIR=\"}"
      result="${result%\"}"
      result="${result//\\\$/\$}"
      result="${result//\\\`/\`}"
      result="${result//\\\"/\"}"
      result="${result//\\\\/\\}"
    fi
  done < "$env_file"
  [[ "$result" == /* && "$result" != / ]] || result=""
  printf '%s\n' "$result"
}

ensure_agentdots_env() {
  local repo_dir="$1"
  # An explicit registry path lets fixtures avoid the real home directory.
  local env_file="${2:-$(agentdots_env_file)}"
  local escaped_repo_dir temporary
  escaped_repo_dir="${repo_dir//\\/\\\\}"
  escaped_repo_dir="${escaped_repo_dir//\"/\\\"}"
  escaped_repo_dir="${escaped_repo_dir//\$/\\\$}"
  escaped_repo_dir="${escaped_repo_dir//\`/\\\`}"
  local expected_export="export AGENT_DOTS_DIR=\"$escaped_repo_dir\""
  local expected_alias='alias agentdots="cd \$AGENT_DOTS_DIR"'

  mkdir -p -- "$(dirname -- "$env_file")/Projects/home" || return 1
  [[ -e "$env_file" ]] || touch -- "$env_file" || return 1
  temporary="$(mktemp "${env_file}.XXXXXX")" || return 1
  # ENVIRON preserves literal backslashes; awk -v would interpret them.
  if ! DOTFILES_REGISTER_EXPORT="$expected_export" \
       DOTFILES_REGISTER_ALIAS="$expected_alias" awk '
    BEGIN {
      desired_export = ENVIRON["DOTFILES_REGISTER_EXPORT"]
      desired_alias = ENVIRON["DOTFILES_REGISTER_ALIAS"]
    }
    $0 ~ /^[[:space:]]*export[[:space:]]+AGENT_DOTS_DIR=/ {
      if (!seen_export++) print desired_export
      next
    }
    $0 ~ /^[[:space:]]*alias[[:space:]]+agentdots=/ {
      if (!seen_alias++) print desired_alias
      next
    }
    { print }
    END {
      if (!seen_export) print desired_export
      if (!seen_alias) print desired_alias
    }
  ' "$env_file" > "$temporary"; then
    rm -f -- "$temporary"
    return 1
  fi
  if ! mv -- "$temporary" "$env_file"; then
    rm -f -- "$temporary"
    return 1
  fi
  export AGENT_DOTS_DIR="$repo_dir"
}
