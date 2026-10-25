#!/usr/bin/env bash
# agentdots/lib/link.sh
# Symlink creation logic. Source this; do not execute.
# Depends on: lib/log.sh, lib/targets.sh
#
# Skill validation and ownership preflight happen before client links change.
# Global instruction migration retains its existing backup/replacement behavior.

# link_item SOURCE TARGET
# Create a symlink SOURCE -> TARGET. Replaces wrong symlinks or real files
# in-place. Refuses to touch protected macOS Library roots.
link_item() {
  local source="$1"
  local target="$2"

  # Safety: never replace macOS Library roots themselves
  # (file-level items inside Preferences / Application Support are allowed)
  case "$target" in
    "$HOME/Library" | "$HOME/Library/Preferences" | "$HOME/Library/Application Support")
      log_err "Refusing to modify protected path: $target"
      return 1
      ;;
  esac

  # Already linked correctly? No-op.
  if [ -L "$target" ] && [ "$(readlink "$target" 2>/dev/null || true)" = "$source" ]; then
    log_ok "Already linked: $target"
    return 0
  fi

  # Exists but wrong? Remove and relink.
  if [ -L "$target" ]; then
    rm -f "$target" || return 1
    log_replace "Replacing symlink: $target"
  elif [ -e "$target" ]; then
    rm -rf "$target" || return 1
    log_clean "Removed existing file/dir: $target"
  fi

  mkdir -p "$(dirname "$target")" || return 1
  ln -s "$source" "$target" || return 1
  log_link "$source → $target"
}

# list_skills SKILLS_DIR
# Validate every active directory before returning any paths. Keep drafts
# outside skills/ so an incomplete entry cannot silently disappear from doctor.
list_skills() {
  local skills_dir="$1"
  local lib_dir
  lib_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)" || return 1
  python3 -B "$lib_dir/../scripts/validate-skills.py" "$skills_dir"
}

# Compare lexical destinations without following a missing source or an
# unrelated symlink inside it. Relative links and .. segments are normalized.
link_destination() {
  python3 -B - "$1" <<'PY'
import os, sys
link = sys.argv[1]
try:
    print(os.path.abspath(os.path.join(os.path.dirname(link), os.readlink(link))))
except OSError:
    sys.exit(1)
PY
}

link_points_into_repo() {
  local link="$1" repo_dir="$2" destination
  [[ -n "$repo_dir" && "$repo_dir" == /* && "$repo_dir" != / ]] || return 1
  destination="$(link_destination "$link")" || return 1
  repo_dir="${repo_dir%/}"
  [[ "$destination" == "$repo_dir/"* ]]
}

skill_link_active() {
  local repo_dir="$1" link="$2" source
  source="$repo_dir/skills/$(basename "$link")"
  [[ -d "$source" && ! -L "$source" && -f "$source/SKILL.md" ]] || return 1
  [[ "$(link_destination "$link")" == "$source" ]]
}

check_skill_target() {
  local source="$1" target="$2" repo_dir="$3" previous_repo_dir="${4:-}" parent
  if [[ -L "$target" ]]; then
    [[ "$(readlink "$target")" == "$source" ]] && return 0
    if ! link_points_into_repo "$target" "$repo_dir" &&
       ! link_points_into_repo "$target" "$previous_repo_dir"; then
      log_err "Foreign skill collision: $target -> $(readlink "$target"); choose another name or explicitly move that link aside"
      return 1
    fi
  fi
  parent="$(dirname "$target")"
  while [[ ! -e "$parent" && ! -L "$parent" && "$parent" != / ]]; do
    parent="$(dirname "$parent")"
  done
  [[ -d "$parent" && -w "$parent" && -x "$parent" ]] || {
    log_err "Skill target parent is not a writable directory: $parent"
    return 1
  }
}

preflight_skills() {
  local skills_dir="$1" previous_repo_dir="${2:-}" repo_dir skill_dirs skill target
  repo_dir="$(dirname "$skills_dir")"
  skill_dirs="$(list_skills "$skills_dir")" || return 1
  while IFS= read -r skill; do
    [[ -n "$skill" ]] || continue
    while IFS= read -r target; do
      [[ -n "$target" ]] || continue
      check_skill_target "$skill" "$target/$(basename "$skill")" "$repo_dir" "$previous_repo_dir" || return 1
    done < <(skill_targets)
  done <<< "$skill_dirs"
}

preflight_install() {
  local repo_dir="$1" previous_repo_dir="${2:-}" source
  source="$(instruction_source "$repo_dir")"
  [[ -f "$source" ]] || { log_err "Missing global instructions: $source"; return 1; }
  preflight_skills "$repo_dir/skills" "$previous_repo_dir"
}

# install_skills SKILLS_DIR
# For each skill in SKILLS_DIR, link it into each target from skill_targets.
install_skills() {
  local skills_dir="$1"
  local previous_repo_dir="${2:-}" skill_dirs skill name target count=0
  preflight_skills "$skills_dir" "$previous_repo_dir" || return 1
  skill_dirs="$(list_skills "$skills_dir")" || return 1

  while IFS= read -r skill; do
    [ -n "$skill" ] || continue
    name="$(basename "$skill")"
    log_sync "Skill: $name"
    while IFS= read -r target; do
      [ -n "$target" ] || continue
      check_skill_target "$skill" "$target/$name" "$(dirname "$skills_dir")" "$previous_repo_dir" || return 1
      link_item "$skill" "$target/$name" || return 1
    done < <(skill_targets)
    count=$((count + 1))
  done <<< "$skill_dirs"

  if [ "$count" -eq 0 ]; then
    log_info "No skills found in $skills_dir (nothing to link)."
  fi
}

# prune_stale_links REPO_DIR
# In each target directory, remove symlinks that point INTO this repo but no
# no longer represent an active skill at that target name. A previously
# installed checkout is owned only when the persisted environment names it.
prune_stale_links() {
  local repo_dir="$1" previous_repo_dir="${2:-}"
  local target link dest
  list_skills "$repo_dir/skills" >/dev/null || return 1

  while IFS= read -r target; do
    [ -d "$target" ] || continue
    while IFS= read -r link; do
      [ -n "$link" ] || continue
      if link_points_into_repo "$link" "$repo_dir" ||
         link_points_into_repo "$link" "$previous_repo_dir"; then
        if ! skill_link_active "$repo_dir" "$link"; then
          dest="$(readlink "$link")"
          rm -f "$link" || return 1
          log_clean "Pruned retired skill link: $link → $dest"
        fi
      fi
    done < <(find "$target" -mindepth 1 -maxdepth 1 -type l)
  done < <(skill_targets)
}

# install_instructions REPO_DIR
# Link the shared source from instruction_source to every client target.
# A missing source is an error; repository instructions are never a fallback.
install_instructions() {
  local repo_dir="$1"
  local source target
  source="$(instruction_source "$repo_dir")"

  if [ ! -f "$source" ]; then
    log_err "Missing global instructions: $source; restore this tracked file before syncing"
    return 1
  fi
  log_sync "Instructions: instructions/global.md"
  while IFS= read -r target; do
    [ -n "$target" ] || continue
    link_item "$source" "$target"
  done < <(instruction_targets)
}
