#!/usr/bin/env python3
"""Filter recipes/index.json. Rebuilds the index first if it is missing.

examples:
  query.py --ingredient chicken --ingredient rice        # both required
  query.py --any-ingredient spinach --any-ingredient kale
  query.py --tag weeknight --max-time 45
  query.py --not-made-since 2026-06-01                     # includes never made
  query.py --title tikka
  query.py --category breakfast --json
Drafts are excluded unless --include-drafts or --category drafts.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEFAULT_RECIPES, fmt_duration  # noqa: E402


def load_index(root: Path):
    idx = root / "index.json"
    if not idx.exists():
        subprocess.run([sys.executable, str(Path(__file__).with_name("build_index.py")), str(root)],
                       check=False, stdout=subprocess.DEVNULL)
    if not idx.exists():
        print(f"error: could not build {idx}", file=sys.stderr)
        sys.exit(2)
    return json.loads(idx.read_text(encoding="utf-8"))["recipes"]


def has_ingredient(rec, term):
    term = term.lower()
    return any(term in ing for ing in rec["ingredients"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--recipes", default=str(DEFAULT_RECIPES), help="recipes directory")
    ap.add_argument("--ingredient", action="append", default=[], help="must contain (repeatable, AND)")
    ap.add_argument("--any-ingredient", action="append", default=[], help="must contain at least one (OR)")
    ap.add_argument("--tag", action="append", default=[], help="must have tag (repeatable, AND)")
    ap.add_argument("--category", help="folder name, e.g. mains")
    ap.add_argument("--title", help="substring of title, case-insensitive")
    ap.add_argument("--max-time", type=int, help="total minutes at most")
    ap.add_argument("--not-made-since", metavar="YYYY-MM-DD", help="last_made before this date, or never")
    ap.add_argument("--min-rating", type=int)
    ap.add_argument("--include-drafts", action="store_true")
    ap.add_argument("--json", action="store_true", help="print matching records as JSON")
    a = ap.parse_args()

    root = Path(a.recipes).expanduser()
    recs = load_index(root)
    out = []
    for r in recs:
        if r["category"] == "drafts" and not (a.include_drafts or a.category == "drafts"):
            continue
        if a.category and r["category"] != a.category:
            continue
        if a.title and a.title.lower() not in r["title"].lower():
            continue
        if any(not has_ingredient(r, t) for t in a.ingredient):
            continue
        if a.any_ingredient and not any(has_ingredient(r, t) for t in a.any_ingredient):
            continue
        if any(t.lower() not in r["tags"] for t in a.tag):
            continue
        if a.max_time is not None and (r["total_min"] is None or r["total_min"] > a.max_time):
            continue
        if a.not_made_since and r["last_made"] and r["last_made"] >= a.not_made_since:
            continue
        if a.min_rating is not None and (r["rating"] is None or r["rating"] < a.min_rating):
            continue
        out.append(r)

    out.sort(key=lambda r: (r["last_made"] or "", r["title"].lower()))
    if a.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0
    if not out:
        print("no matches")
        return 1
    for r in out:
        print(f"{r['title']}  |  {fmt_duration(r['total_min']) or '?'}  |  {', '.join(r['tags'])}  |  {r['path']}"
              + (f"  |  last made {r['last_made']}" if r['last_made'] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
