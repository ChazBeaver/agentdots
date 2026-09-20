# Workflow: plan meals

Goal: a confirmed `plans/YYYY-Www.md` the user is happy with, ready for the
grocery workflow.

## 1. Gather context (read, do not ask yet)

- `preferences.md`: people, default servings, restrictions, dislikes, time cap,
  batch-cook day, nights that need fast meals.
- `pantry.md`: what is always available (affects which recipes are "cheap" to make).
- `plans/rotation.md`: the go-to set. Pull from here first.
- The most recent two files in `plans/`: avoid repeating last week's mains.
- `recipes/index.json` via `scripts/query.py` (drafts excluded by default).
  Useful queries: `--tag weeknight --max-time 45`, `--not-made-since <8 weeks ago>`.

## 2. Ask only what the files cannot tell you

One short message: which days need covering, how many people each night,
anything to use up (fridge leftovers, produce), and any nights out. Skip any
question already answered by `preferences.md`.

## 3. Draft

- Fill the table from `templates/meal-plan.md`. Dinners only unless asked.
- Fast or leftover nights get a `weeknight` recipe or an explicit leftovers row.
- Batch-cook day gets a `batch` recipe sized to cover at least one later night.
- Reuse perishable ingredients across two recipes in the same week (half a
  bunch of cilantro should not be the only reason to buy cilantro).
- Prefer recipes with `last_made` furthest in the past, then rotation, then
  the rest. Never a draft.
- Fill "Prep ahead" with anything that saves weeknight time (marinades, rice,
  chopped aromatics) and "Leftovers" with what covers which lunch.

Show the draft as a table in chat with one line of reasoning per pick.

## 4. Revise, then write

Iterate until the user says yes. Then write `plans/YYYY-Www.md` (ISO week of
the first planned day), link it from nothing else, and offer to build the
grocery list next. Do not build it unprompted.
