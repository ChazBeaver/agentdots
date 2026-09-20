# Workflow: find recipe

Goal: the right recipe or short list, without opening files one by one.

## 1. Translate the ask into filters

| User says | Query |
|:--|:--|
| something with chicken and rice | `--ingredient chicken --ingredient rice` |
| use up spinach or kale | `--any-ingredient spinach --any-ingredient kale` |
| quick, weeknight, fast | `--tag weeknight` or `--max-time 30` |
| vegetarian, gluten-free, ... | `--tag <diet>` |
| haven't had in a while | `--not-made-since <date>` |
| something new | `--include-drafts --category drafts` |

Run `python3 scripts/query.py <filters>`. Ingredient matching is substring on
normalised names, so `chicken` matches `boneless chicken thigh`. Widen
synonyms yourself (`scallion` and `green onion`, `cilantro` and `coriander`)
by running a second query with `--any-ingredient`.

If Python is unavailable: `grep -ril "<term>" ~/kitchen/recipes/` and read
`recipes/INDEX.md` for tags and times.

## 2. Present

Up to five results as `title, total time, tags, path`. If zero, say what was
searched and offer the nearest matches or the add-recipe workflow.

## 3. Open on request

Only open the full recipe file when the user picks one or asks for details.
