#!/usr/bin/env python3
"""Validate all recipes in cookbook/recipes/.

Errors (exit code 1): broken frontmatter, unknown category or unit, missing
sections, title mismatch, ingredients that always contain gluten.
Warnings: ingredients that are only safe as labeled gluten-free products.

parse_recipe() and parse_ingredient() double as the reference parser for the app.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
RECIPES_DIR = ROOT / "cookbook" / "recipes"
IMAGES_DIR = ROOT / "cookbook" / "images"
SCHEMA_DIR = ROOT / "schema"


def load_yaml(name: str):
    return yaml.safe_load((SCHEMA_DIR / name).read_text(encoding="utf-8"))


SCHEMA = json.loads((SCHEMA_DIR / "recipe.schema.json").read_text(encoding="utf-8"))
CATEGORIES: dict = load_yaml("categories.yml")
UNITS: set[str] = set(load_yaml("units.yml"))
GLUTEN = load_yaml("gluten-flags.yml")

FILENAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*\.md$")
NUM = r"(?:\d+(?:\.\d+)?|\d+/\d+|[½¼¾⅓⅔])"
AMOUNT_RE = re.compile(rf"^{NUM}(?:-{NUM})?$")
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
REQUIRED_SECTIONS = ["Ingredients", "Instructions"]


@dataclass
class Ingredient:
    raw: str
    amount: str | None
    unit: str | None
    name: str
    note: str | None
    group: str | None
    links: list[str] = field(default_factory=list)


def parse_ingredient(text: str, group: str | None = None) -> Ingredient:
    """Parse '240 ml warm milk, approx. 37 °C' into its parts."""
    links = [m.group(1) for m in WIKILINK_RE.finditer(text)]
    plain = WIKILINK_RE.sub(lambda m: m.group(2) or m.group(1), text).strip()
    amount = unit = None
    tokens = plain.split(" ", 1)
    if len(tokens) == 2 and AMOUNT_RE.match(tokens[0]):
        amount, plain = tokens[0], tokens[1]
        tokens = plain.split(" ", 1)
        if len(tokens) == 2 and tokens[0] in UNITS:
            unit, plain = tokens[0], tokens[1]
    name, _, note = plain.partition(",")
    return Ingredient(text, amount, unit, name.strip(), note.strip() or None, group, links)


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        raise ValueError("file must start with '---' frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError("frontmatter is not closed with '---'")
    meta = yaml.safe_load(text[4:end]) or {}
    # YAML turns 2026-11-05 into a date object; the schema expects strings.
    meta = json.loads(json.dumps(meta, default=str))
    return meta, text[end + 4 :]


def parse_recipe(path: Path) -> dict:
    meta, body = split_frontmatter(path.read_text(encoding="utf-8"))
    h1, sections, current, group = None, {}, None, None
    ingredients: list[Ingredient] = []
    for line in body.splitlines():
        if line.startswith("# "):
            h1 = line[2:].strip()
        elif line.startswith("## "):
            current, group = line[3:].strip(), None
            sections[current] = []
        elif current:
            sections[current].append(line)
            if current == "Ingredients":
                if line.startswith("### "):
                    group = line[4:].strip()
                elif line.startswith("- ") and line[2:].strip():
                    ingredients.append(parse_ingredient(line[2:].strip(), group))
    return {"slug": path.stem, "meta": meta, "h1": h1, "sections": sections, "ingredients": ingredients}


def gluten_findings(ing: Ingredient) -> tuple[list[str], list[str]]:
    text = ing.raw
    lowered = text.lower()
    if "gluten-free" in lowered or "gluten free" in lowered:
        return [], []
    cleaned = text
    for safe in GLUTEN["safe_exceptions"]:
        cleaned = re.sub(safe, "", cleaned, flags=re.IGNORECASE)
    errors = [w for w in GLUTEN["contains_gluten"] if w.lower() in cleaned.lower()]
    warnings = [
        w for w in GLUTEN["needs_gf_label"]
        if re.search(rf"(?<!\w){re.escape(w)}(?!\w)", cleaned, flags=re.IGNORECASE)
    ]
    return errors, warnings


def validate(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not FILENAME_RE.match(path.name):
        errors.append("filename must be lowercase ASCII kebab-case, e.g. 'cheese-noodles.md'")
    try:
        recipe = parse_recipe(path)
    except (ValueError, yaml.YAMLError) as exc:
        return [f"cannot parse: {exc}"], []

    meta = recipe["meta"]
    for err in Draft202012Validator(SCHEMA).iter_errors(meta):
        where = ".".join(str(p) for p in err.absolute_path) or "frontmatter"
        errors.append(f"{where}: {err.message}")
    if meta.get("category") and meta["category"] not in CATEGORIES:
        errors.append(f"unknown category '{meta['category']}' (see schema/categories.yml)")
    if meta.get("image") and not (IMAGES_DIR / meta["image"]).exists():
        errors.append(f"image not found: cookbook/images/{meta['image']}")
    if recipe["h1"] != meta.get("title"):
        errors.append(f"'# {recipe['h1']}' must match title '{meta.get('title')}'")
    for section in REQUIRED_SECTIONS:
        if section not in recipe["sections"]:
            errors.append(f"missing section '## {section}'")
    if not recipe["ingredients"]:
        errors.append("no ingredients found under '## Ingredients'")

    for ing in recipe["ingredients"]:
        first = ing.raw.split(" ", 1)[0]
        if first[:1].isdigit() and ing.amount is None:
            errors.append(f"cannot read amount in '- {ing.raw}'")
        if ing.amount and ing.unit is None:
            maybe_unit = ing.name.split(" ", 1)[0]
            if maybe_unit.lower() in {u.lower() for u in UNITS}:
                errors.append(f"unit with wrong spelling in '- {ing.raw}' (see schema/units.yml)")
        hard, soft = gluten_findings(ing)
        for word in hard:
            errors.append(f"GLUTEN: '{word}' in '- {ing.raw}'")
        for word in soft:
            warnings.append(f"'{word}' must be labeled gluten-free: '- {ing.raw}'")
        for link in ing.links:
            if not (RECIPES_DIR / f"{link}.md").exists():
                errors.append(f"link target not found: [[{link}]]")
    return errors, warnings


def main() -> int:
    files = sorted(RECIPES_DIR.glob("*.md"))
    total_errors = total_warnings = 0
    for path in files:
        errors, warnings = validate(path)
        total_errors += len(errors)
        total_warnings += len(warnings)
        if errors or warnings:
            print(f"\n{path.relative_to(ROOT)}")
            for e in errors:
                print(f"  ✗ {e}")
            for w in warnings:
                print(f"  ! {w}")
    print(f"\n{len(files)} recipes checked: {total_errors} errors, {total_warnings} warnings")
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main())
