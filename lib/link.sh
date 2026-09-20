#!/usr/bin/env bash
# agentdots/lib/link.sh
# Symlink creation logic. Source this; do not execute.
# Depends on: lib/log.sh, lib/targets.sh
#
# link_item is copied verbatim from appdots so the two repos behave identically.
# install_skills / prune_stale_links are the agentdots-specific fan-out: one
# skill directory is linked into EVERY target directory listed in lib/targets.sh.

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
    rm -f "$target"
    log_replace "Replacing symlink: $target"
  elif [ -e "$target" ]; then
    rm -rf "$target"
    log_clean "Removed existing file/dir: $target"
  fi

  mkdir -p "$(dirname "$target")"
  ln -s "$source" "$target"
  log_link "$source → $target"
}

# list_skills SKILLS_DIR
# Print every immediate subdirectory of SKILLS_DIR that contains a SKILL.md,
# one absolute path per line, sorted. Directories without SKILL.md are
# reported and skipped so a half-written skill never gets linked.
list_skills() {
  local skills_dir="$1"
  [ -d "$skills_dir" ] || return 0

  local dir
  while IFS= read -r dir; do
    if [ -f "$dir/SKILL.md" ]; then
      echo "$dir"
    else
      log_warn "Skipping $(basename "$dir"): no SKILL.md" >&2
    fi
  done < <(find "$skills_dir" -mindepth 1 -maxdepth 1 -type d | sort)
}

# install_skills SKILLS_DIR
# For each skill in SKILLS_DIR, link it into each target from skill_targets.
install_skills() {
  local skills_dir="$1"
  local skill name target count=0

  while IFS= read -r skill; do
    [ -n "$skill" ] || continue
    name="$(basename "$skill")"
    log_sync "Skill: $name"
    while IFS= read -r target; do
      [ -n "$target" ] || continue
      link_item "$skill" "$target/$name"
    done < <(skill_targets)
    count=$((count + 1))
  done < <(list_skills "$skills_dir")

  if [ "$count" -eq 0 ]; then
    log_info "No skills found in $skills_dir (nothing to link)."
  fi
}

# prune_stale_links REPO_DIR
# In each target directory, remove symlinks that point INTO this repo but no
# longer resolve (skill renamed or deleted). Symlinks that point elsewhere
# (e.g. omarchy's /usr/share/... skills) are never touched.
prune_stale_links() {
  local repo_dir="$1"
  local target link dest

  while IFS= read -r target; do
    [ -d "$target" ] || continue
    while IFS= read -r link; do
      [ -n "$link" ] || continue
      dest="$(readlink "$link" 2>/dev/null || true)"
      case "$dest" in
        "$repo_dir"/*)
          if [ ! -e "$link" ]; then
            rm -f "$link"
            log_clean "Pruned stale link: $link → $dest"
          fi
          ;;
      esac
    done < <(find "$target" -mindepth 1 -maxdepth 1 -type l)
  done < <(skill_targets)
}
