# Recipe format

Canonical shape of a recipe file. `templates/recipe.md` is the blank version;
`references/conventions.md` defines every allowed value.

```markdown
---
title: Chicken Tikka Masala
tags: [indian, gluten-free, stovetop, weeknight, batch, freezer]
servings: 4
prep: 20m
cook: 30m
source: https://example.com/tikka
rating: 5
last_made: 2026-09-01
---

## Ingredients

### Marinade
- 1.5 lb boneless chicken thighs, cut into 1-inch pieces
- 1 cup plain yogurt
- 1 tbsp garam masala

### Sauce
- 2 tbsp vegetable oil
- 1 onion, finely diced
- 4 cloves garlic, minced
- 1 can crushed tomatoes
- cilantro, to serve

## Method
1. Marinate the chicken at least 20 minutes.
2. Brown the chicken in batches; set aside.
3. Soften onion, add garlic and spices, then tomatoes; simmer 10 minutes.
4. Return chicken, finish with cream, adjust salt.

## Notes
- Freezes well for 3 months.
```

## Sections

| Section | Required | Rules |
|:--|:--|:--|
| frontmatter | yes | Exactly the keys in conventions.md. `rating` and `last_made` are absent until first cooked. |
| `## Ingredients` | yes | Bullet lines only, following the ingredient line grammar. `### Sub-component` headers allowed. No prose. |
| `## Method` | yes | Numbered steps. One action per step. Temperatures and times inline. |
| `## Notes` | no | Substitutions, scaling, serving suggestions, what to change next time. Tweaks from the after-cooking workflow land here, dated. |

## Why this shape

- Frontmatter is small so it stays filled in. Anything you would set once and
  never revisit was removed on purpose.
- Ingredients live only in the body. `build_index.py` derives the searchable
  ingredient list from the bullet lines, so nothing is duplicated and the
  grocery workflow reads the same lines.
- Category is the folder. Everything else that describes the dish is a tag.

## Writing a new recipe from a source

1. Title in Title Case. Slug from the title.
2. Pick the category folder. Unknown or untested goes to `drafts/`.
3. Tags: at least one method tag and, where true, cuisine and diet tags. Add
   `weeknight` only if total time is 45 minutes or under.
4. Rewrite every ingredient line into the grammar. Merge "salt and pepper"
   into two lines. Convert vulgar fractions to decimals.
5. Rewrite the method into short numbered steps in your own words. Keep the
   source URL or citation in `source`.
6. Run `scripts/lint_recipes.py`, then `scripts/build_index.py`.
