#!/usr/bin/env python3
"""Validate every recipe under a recipes directory. Exit 1 on any error.

usage: lint_recipes.py [RECIPES_DIR]   (default ~/kitchen/recipes)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEFAULT_RECIPES, load_all, load_vocab  # noqa: E402


def main(argv):
    root = Path(argv[1]).expanduser() if len(argv) > 1 else DEFAULT_RECIPES
    if not root.is_dir():
        print(f"error: recipes directory not found: {root}", file=sys.stderr)
        return 2
    vocab = load_vocab()
    recipes = load_all(root, vocab)
    n_err = n_warn = 0
    for r in recipes:
        for msg in r.errors:
            print(f"ERROR {r.rel}: {msg}")
            n_err += 1
        for msg in r.warnings:
            print(f"warn  {r.rel}: {msg}")
            n_warn += 1
    print(f"{len(recipes)} recipe(s), {n_err} error(s), {n_warn} warning(s)")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
