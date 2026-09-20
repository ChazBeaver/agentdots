# Workflow: add recipe

Goal: a new file in `recipes/` that passes the linter and appears in the index.

## 1. Capture

Accept any of: pasted text, a URL (fetch it if a fetch tool is available,
otherwise ask the user to paste), a photo transcription, or a dictated
description. Keep the original citation for `source`.

## 2. Normalise

Follow `references/recipe-format.md` step by step:

- Title Case title; kebab slug for the filename.
- Category folder from `references/conventions.md`. Default to `drafts/`
  unless the user says they have cooked it before.
- Tags only from the vocabulary. If a needed tag is missing, propose adding
  it to `conventions.md` and wait for a yes.
- Every ingredient line into `- <qty> [<unit>] <item>[, <note>]`. Split
  combined lines, convert `½` to `0.5`, put prep after the comma.
- Method as short numbered steps. Paraphrase; do not copy long prose.
- `servings`, `prep`, `cook` filled. Estimate and say so if the source lacks them.

## 3. Check for duplicates

`python3 scripts/query.py --title "<key words>"` and a `grep -ril` for the
main ingredient. If a close match exists, show both titles and ask: replace,
keep both, or merge notes into the existing one.

## 4. Confirm and write

Show the full file in chat. On yes, write it, then run:

```
python3 scripts/lint_recipes.py
python3 scripts/build_index.py
```

Fix any linter errors before reporting done. Mention the path and whether it
landed in `drafts/`.
