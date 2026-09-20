# Workflow: build grocery list

Goal: a confirmed `grocery/YYYY-MM-DD.md` grouped in the store's aisle order,
with pantry staples pulled out into a stock-check section.

## 1. Inputs

- The plan: the file the user names, or the latest `plans/YYYY-Www.md`. If
  none exists, offer to run `workflows/plan-meals.md` first.
- `pantry.md`, `stores.md`, `references/grocery-categories.md`.
- Extra items the user mentions (household goods, snacks) are added verbatim
  under their category.

## 2. Collect ingredient lines

For each recipe in the plan, read its `## Ingredients` section and parse each
bullet with the grammar from `references/conventions.md`. Scale quantities
when the plan's servings column differs from the recipe's `servings`.
Skip lines with no quantity (`salt, to taste`) unless the item is not in the
pantry, in which case list it without a quantity.

## 3. Aggregate

- Merge identical items across recipes. Sum quantities only when the unit
  matches; otherwise list both (`1 cup + 2 tbsp`). Do not convert units.
- Keep a note of which recipes each item serves, in parentheses.
- Round up to what is actually sold when obvious (`0.5 onion` -> `1 onion`,
  `1.5 lb thighs` stays).

## 4. Subtract pantry

Any item whose name matches a `pantry.md` entry (case-insensitive, ignoring
plurals and size words) moves to the trailing **Already have** section as a
bare name, so the user can glance at stock.

## 5. Group and order

Assign every remaining item a category from `references/grocery-categories.md`.
Order sections by the chosen store in `stores.md` (default: the first store).
Categories not listed for that store go last, alphabetical.

## 6. Confirm and write

Show the list in chat. After the user confirms, write
`grocery/YYYY-MM-DD.md` using `templates/grocery-list.md`, where the date is
the shopping day from the plan or today if unspecified. Add a link to the
list at the bottom of the plan file's "Grocery list" section.
