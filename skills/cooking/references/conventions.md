# Conventions

The contract every recipe follows. `scripts/common.py` parses the bullet lists
in this file, so the **Units**, **Size words**, **Tags**, and **Categories**
sections are machine-read: keep them as plain `- item` bullets and add new
values here *before* using them in a recipe.

## File naming

- One recipe per file: `recipes/<category>/<slug>.md`.
- `<slug>` is the title in kebab-case: lowercase, ASCII, hyphens only.
  `Chicken Tikka Masala` -> `chicken-tikka-masala.md`.
- `<category>` is one of the folders listed under **Categories**. It is the
  recipe's only categorisation outside of tags.
- Meal plans: `plans/YYYY-Www.md` (ISO week, e.g. `2026-W38.md`).
- Grocery lists: `grocery/YYYY-MM-DD.md` (the planned shopping day).

## Frontmatter

Required: `title`, `tags`, `servings`, `prep`, `cook`, `source`.
Optional, written by the after-cooking workflow: `rating` (1-5), `last_made` (YYYY-MM-DD).
No other keys. Cuisine, diet, method, and attributes are tags, not fields.

- `servings`: integer.
- `prep`, `cook`: durations as `20m`, `1h`, `1h30m`. Use `0m`, not blank.
- `source`: URL, book and page, a person, or `household` for your own.
- `tags`: inline list `[a, b, c]`, every value from the **Tags** vocabulary.

## Ingredient line grammar

Under `## Ingredients` (optionally split by `### Sub-component` headers):

```
- <qty> [<unit>] <item>[, <note>]
- <item>, <note>
```

- `qty`: `2`, `0.5`, `1.5`, `1/2`, `1 1/2`, or a range `2-3`. Use decimals or
  ASCII fractions, never `½`.
- `unit`: from **Units** below, or omitted for countable things (`1 onion`,
  `2 eggs`). Size words like `large` are allowed before the item and are
  stripped when indexing.
- `item`: the thing you buy, as you would write it on a list.
- `note`: everything after the first comma. Preparation (`minced`), state
  (`fresh or frozen`), or purpose (`to serve`). The second form, with no
  quantity, is only for `to taste`, `to serve`, `for garnish` style lines.

Good: `- 4 cloves garlic, minced`  `- 1 can crushed tomatoes`  `- salt, to taste`
Bad: `- garlic cloves x4`  `- 1/2 an onion`  `- Salt & pepper`

## Units

One per line: canonical form, then accepted aliases in parentheses. Parsed.

- tsp (teaspoon, teaspoons)
- tbsp (tablespoon, tablespoons)
- cup (cups)
- fl oz
- ml
- l (liter, liters, litre, litres)
- pint (pints)
- quart (quarts)
- g (gram, grams)
- kg
- oz (ounce, ounces)
- lb (lbs, pound, pounds)
- clove (cloves)
- can (cans)
- jar (jars)
- bunch (bunches)
- slice (slices)
- stick (sticks)
- sprig (sprigs)
- head (heads)
- stalk (stalks)
- pinch (pinches)
- dash (dashes)
- package (packages, pkg)
- handful (handfuls)
- piece (pieces)

## Size words

Stripped from item names when indexing so `1 large onion` indexes as `onion`. Parsed.

- large
- medium
- small

## Tags

One controlled vocabulary, grouped by facet for readability. A recipe may use
any number from any facet. Parsed.

### cuisine
- american
- british
- chinese
- french
- greek
- indian
- italian
- japanese
- korean
- mediterranean
- mexican
- middle-eastern
- thai
- vietnamese

### diet
- vegetarian
- vegan
- gluten-free
- dairy-free
- low-carb
- high-protein

### method
- stovetop
- oven
- sheet-pan
- one-pot
- slow-cooker
- instant-pot
- grill
- no-cook
- air-fryer

### attribute
- weeknight
- batch
- freezer
- make-ahead
- leftovers-good
- kid-friendly

Meanings: `weeknight` = total time 45 minutes or under and low effort.
`batch` = worth doubling. `freezer` = freezes and reheats well.
`make-ahead` = better or equal made a day early.
`high-protein` = built around a meat, poultry, fish, or egg protein.
`low-carb` = no pasta, rice, bread, or potato as a component.

## Categories

The folders under `recipes/`. Parsed.

- mains
- sides
- breakfast
- soups-and-stews
- baking
- sauces-and-basics
- drafts

`drafts` holds imported or untested recipes. They are excluded from planning
and from `query.py` by default until promoted by the after-cooking workflow.
