# Workflow: after cooking

Goal: keep `last_made`, `rating`, and notes truthful so planning improves.

## Triggers

"We made X last night", "that was a 4", "next time use less sugar",
"promote X from drafts", "add X to the rotation".

## Steps

1. Locate the recipe with `scripts/query.py --title "<words>"` or grep.
2. Update frontmatter:
   - `last_made`: the date cooked (default today), `YYYY-MM-DD`.
   - `rating`: 1 to 5 if given. Replace, do not average.
3. Tweaks go under `## Notes` as a dated bullet: `- 2026-09-10: halve the sugar.`
   If the user wants the recipe itself changed, show the diff and get a yes
   before editing ingredients or method.
4. Promotion: if the file is in `recipes/drafts/`, ask which category it
   belongs in and `git mv` it there. Update any link in `plans/rotation.md`.
5. Rotation: on request, add or remove the link in `plans/rotation.md` under
   the right heading.
6. Run `scripts/lint_recipes.py` then `scripts/build_index.py`.

Report the file changed and the new frontmatter values in one line.
