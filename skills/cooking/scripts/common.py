"""Shared parsing for the cooking skill scripts. Stdlib only.

Reads the vocabularies (units, size words, tags, categories) from
../references/conventions.md so that file stays the single source of truth,
and parses recipe files: frontmatter, ingredient lines, durations.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CONVENTIONS = SKILL_DIR / "references" / "conventions.md"
DEFAULT_RECIPES = Path(os.path.expanduser("~/kitchen/recipes"))

REQUIRED_KEYS = ["title", "tags", "servings", "prep", "cook", "source"]
OPTIONAL_KEYS = ["rating", "last_made"]
GENERATED = {"INDEX.md", "index.json"}

QTY_RE = re.compile(
    r"^(?P<qty>\d+(?:\.\d+)?(?:\s+\d+/\d+)?|\d+/\d+)"
    r"(?:\s*(?:-|to)\s*(?P<qty_hi>\d+(?:\.\d+)?(?:\s+\d+/\d+)?|\d+/\d+))?"
    r"\s+(?P<rest>.+)$"
)
UNICODE_FRACTIONS = "½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞"
DURATION_RE = re.compile(r"^(?:(\d+)h)?(?:(\d+)m)?$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ---------- vocabularies ----------

@dataclass
class Vocab:
    units: dict[str, str] = field(default_factory=dict)   # alias -> canonical
    size_words: set[str] = field(default_factory=set)
    tags: dict[str, str] = field(default_factory=dict)    # tag -> facet
    categories: list[str] = field(default_factory=list)


def load_vocab(path: Path = CONVENTIONS) -> Vocab:
    vocab = Vocab()
    section = None
    facet = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("## "):
            section = line[3:].strip().lower()
            facet = None
            continue
        if line.startswith("### "):
            facet = line[4:].strip().lower()
            continue
        if not line.startswith("- "):
            continue
        value = line[2:].strip()
        if section == "units":
            m = re.match(r"^([^(]+?)(?:\s*\((.*)\))?$", value)
            canonical = m.group(1).strip().lower()
            vocab.units[canonical] = canonical
            for alias in (m.group(2) or "").split(","):
                alias = alias.strip().lower()
                if alias:
                    vocab.units[alias] = canonical
        elif section == "size words":
            vocab.size_words.add(value.lower())
        elif section == "tags" and facet:
            vocab.tags[value.lower()] = facet
        elif section == "categories":
            vocab.categories.append(value.lower())
    return vocab


# ---------- recipe files ----------

def iter_recipe_files(root: Path):
    for path in sorted(root.rglob("*.md")):
        if path.name in GENERATED or path.name.startswith("."):
            continue
        if path.parent == root:
            continue  # only files inside a category folder count
        yield path


def category_of(path: Path, root: Path) -> str:
    return path.relative_to(root).parts[0]


def slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def split_frontmatter(text: str):
    """Return (frontmatter_lines, body, error)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text, "missing frontmatter opening '---'"
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], "\n".join(lines[i + 1:]), None
    return None, text, "missing frontmatter closing '---'"


def _strip_comment(value: str) -> str:
    # drop an inline "# comment" that is preceded by whitespace
    return re.split(r"\s+#", value, maxsplit=1)[0].strip()


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def parse_frontmatter(lines):
    """Minimal YAML: `key: scalar` and `key: [a, b]`. Returns (dict, errors)."""
    data: dict = {}
    errors: list[str] = []
    for raw in lines:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if ":" not in raw:
            errors.append(f"unparseable frontmatter line: {raw!r}")
            continue
        key, _, value = raw.partition(":")
        key = key.strip()
        value = _strip_comment(value)
        if value.startswith("[") and value.endswith("]"):
            items = [_unquote(v.strip()) for v in value[1:-1].split(",")]
            data[key] = [v for v in items if v]
        else:
            data[key] = _unquote(value)
    return data, errors


def parse_duration(value) -> int | None:
    """'1h30m' -> 90, '20m' -> 20, '0m' -> 0. None if invalid."""
    if value is None:
        return None
    s = str(value).strip().lower()
    if not s:
        return None
    m = DURATION_RE.match(s)
    if not m or (m.group(1) is None and m.group(2) is None):
        return None
    return int(m.group(1) or 0) * 60 + int(m.group(2) or 0)


def fmt_duration(minutes: int | None) -> str:
    if minutes is None:
        return ""
    h, m = divmod(minutes, 60)
    if h and m:
        return f"{h}h{m}m"
    if h:
        return f"{h}h"
    return f"{m}m"


# ---------- ingredients ----------

@dataclass
class Ingredient:
    raw: str
    qty: str | None
    unit: str | None
    item: str
    note: str | None
    component: str | None
    normalized: str


def singularize(word: str) -> str:
    if len(word) <= 3 or word.endswith(("ss", "us", "is")):
        return word
    if word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith(("oes", "ches", "shes", "xes")):
        return word[:-2]
    if word.endswith("s"):
        return word[:-1]
    return word


def normalize_item(item: str, vocab: Vocab) -> str:
    words = [w for w in re.split(r"\s+", item.lower().strip()) if w]
    words = [w for w in words if w not in vocab.size_words]
    if not words:
        return ""
    words[-1] = singularize(words[-1])
    return " ".join(words)


def parse_ingredient_line(line: str, vocab: Vocab, component: str | None = None):
    """Parse one '- ...' bullet. Returns (Ingredient | None, error | None)."""
    text = line.strip()
    if not text.startswith("- "):
        return None, "ingredient line must start with '- '"
    text = text[2:].strip()
    if not text:
        return None, "empty ingredient line"
    if any(ch in text for ch in UNICODE_FRACTIONS):
        return None, "use decimals or ASCII fractions, not unicode fraction characters"

    note = None
    if ", " in text:
        text, note = text.split(", ", 1)
        note = note.strip()
    elif text.endswith(","):
        return None, "dangling comma"

    qty = unit = None
    m = QTY_RE.match(text)
    if m:
        qty = m.group("qty")
        if m.group("qty_hi"):
            qty = f"{qty}-{m.group('qty_hi')}"
        rest = m.group("rest").strip()
        tokens = rest.split()
        two = " ".join(tokens[:2]).lower()
        one = tokens[0].lower() if tokens else ""
        if len(tokens) > 2 and two in vocab.units:
            unit = vocab.units[two]
            rest = " ".join(tokens[2:])
        elif len(tokens) > 1 and one in vocab.units:
            unit = vocab.units[one]
            rest = " ".join(tokens[1:])
        item = rest.strip()
    else:
        if note is None:
            return None, "no quantity and no note (quantity-less lines need ', to taste' style notes)"
        item = text.strip()
    if not item:
        return None, "missing item name"
    return Ingredient(
        raw=line.strip(),
        qty=qty,
        unit=unit,
        item=item,
        note=note,
        component=component,
        normalized=normalize_item(item, vocab),
    ), None


def extract_ingredient_lines(body: str):
    """Yield (line, component, lineno) for bullets under '## Ingredients'."""
    in_section = False
    component = None
    for i, raw in enumerate(body.splitlines(), start=1):
        line = raw.rstrip()
        if line.startswith("## "):
            in_section = line[3:].strip().lower() == "ingredients"
            component = None
            continue
        if not in_section:
            continue
        if line.startswith("### "):
            component = line[4:].strip()
            continue
        if line.strip().startswith("- "):
            yield line, component, i


# ---------- whole recipe ----------

@dataclass
class Recipe:
    path: Path
    root: Path
    meta: dict
    body: str
    ingredients: list[Ingredient]
    errors: list[str]
    warnings: list[str]

    @property
    def rel(self) -> str:
        return str(self.path.relative_to(self.root))

    @property
    def category(self) -> str:
        return category_of(self.path, self.root)

    def total_min(self):
        p, c = parse_duration(self.meta.get("prep")), parse_duration(self.meta.get("cook"))
        if p is None or c is None:
            return None
        return p + c


def load_recipe(path: Path, root: Path, vocab: Vocab) -> Recipe:
    errors: list[str] = []
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8")
    fm_lines, body, err = split_frontmatter(text)
    meta: dict = {}
    if err:
        errors.append(err)
    else:
        meta, fm_errors = parse_frontmatter(fm_lines)
        errors.extend(fm_errors)

    ingredients: list[Ingredient] = []
    seen_section = "## ingredients" in body.lower()
    if not seen_section:
        errors.append("missing '## Ingredients' section")
    for line, component, lineno in extract_ingredient_lines(body):
        ing, e = parse_ingredient_line(line, vocab, component)
        if e:
            errors.append(f"line {lineno}: {e}: {line.strip()!r}")
        else:
            ingredients.append(ing)
    if seen_section and not ingredients and not errors:
        errors.append("'## Ingredients' has no bullet lines")
    return Recipe(path, root, meta, body, ingredients, errors, warnings)


def validate(recipe: Recipe, vocab: Vocab) -> None:
    """Append schema problems to recipe.errors / recipe.warnings."""
    m = recipe.meta
    e, w = recipe.errors, recipe.warnings

    for key in REQUIRED_KEYS:
        if key not in m or m[key] in ("", [], None):
            e.append(f"missing required key: {key}")
    for key in m:
        if key not in REQUIRED_KEYS and key not in OPTIONAL_KEYS:
            w.append(f"unknown frontmatter key (schema is intentionally small): {key}")

    tags = m.get("tags")
    if isinstance(tags, str):
        e.append("tags must be an inline list like [a, b]")
    elif isinstance(tags, list):
        for t in tags:
            if t.lower() not in vocab.tags:
                e.append(f"tag not in vocabulary: {t}")

    if "servings" in m and not str(m["servings"]).isdigit():
        e.append(f"servings must be an integer: {m['servings']!r}")
    for key in ("prep", "cook"):
        if key in m and parse_duration(m[key]) is None:
            e.append(f"{key} must look like 20m, 1h, or 1h30m: {m[key]!r}")
    if "rating" in m and (not str(m["rating"]).isdigit() or not 1 <= int(m["rating"]) <= 5):
        e.append(f"rating must be 1-5: {m['rating']!r}")
    if "last_made" in m and not DATE_RE.match(str(m["last_made"])):
        e.append(f"last_made must be YYYY-MM-DD: {m['last_made']!r}")

    if recipe.category not in vocab.categories:
        e.append(f"folder '{recipe.category}' is not a known category")
    title = m.get("title")
    if isinstance(title, str) and title:
        expected = slugify(title) + ".md"
        if recipe.path.name != expected:
            w.append(f"filename {recipe.path.name} does not match title slug {expected}")
    if "## method" not in recipe.body.lower():
        e.append("missing '## Method' section")

    if isinstance(tags, list) and "weeknight" in [t.lower() for t in tags]:
        total = recipe.total_min()
        if total is not None and total > 45:
            w.append(f"tagged weeknight but total time is {total}m (> 45m)")


def load_all(root: Path, vocab: Vocab) -> list[Recipe]:
    recipes = []
    for path in iter_recipe_files(root):
        r = load_recipe(path, root, vocab)
        validate(r, vocab)
        recipes.append(r)
    return recipes
