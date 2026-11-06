# CLAUDE.md

Instructions for Claude and other AI agents working in this repository.

## What this is

A personal gluten-free cookbook. Recipes are Markdown files in an Obsidian vault (`cookbook/`). An app (`app/`, not started yet) will later read and edit the same files, so the format must stay strictly machine-readable. Gluten safety matters more than anything else in this repo.

## Layout

- `cookbook/recipes/` – one recipe per file, flat, no subfolders. Categories live in frontmatter, never in folders.
- `cookbook/templates/recipe.md` – the canonical recipe template. Follow it exactly.
- `cookbook/images/` – photos, named after the recipe file (`cinnamon-rolls.jpg`), max. ~300 KB.
- `cookbook/indexes/` – Obsidian overview notes (Dataview queries). Don't edit unless asked.
- `cookbook/.obsidian/` – Obsidian settings. Never edit.
- `schema/` – source of truth for the format:
  - `recipe.schema.json` – allowed frontmatter fields and values
  - `categories.yml` – category slugs and display names
  - `units.yml` – allowed units
  - `gluten-flags.yml` – ingredients that contain gluten or need a "gluten-free" label
- `scripts/validate.py` – validates every recipe. Its ingredient parser is the reference implementation for the app.

## Recipe format

- **Filename**: lowercase ASCII kebab-case slug of the title (`cheese-noodles.md`, `apple-streusel-cake.md`). The filename is the recipe's permanent ID; don't rename files without asking.
- **Frontmatter**: only fields from `schema/recipe.schema.json`. Times are integers in minutes. `category` must be a slug from `categories.yml`. Tags are lowercase ASCII, no spaces, hyphens allowed.
- **Body**, in this order:
  1. `# <title>` – must match the `title` field exactly.
  2. `## Ingredients` – a bullet list. Optional `### Subgroup` headings (e.g. `### Dough`, `### Filling`).
  3. `## Instructions` – a numbered list, each step starting with a bold short title: `1. **Knead the dough** – …`
  4. `## Notes` – optional: tips, variations, storage, gluten notes.
- **Ingredient lines**: `- <amount> <unit> <name>[, <note>]`
  - amount: `240`, `1,5`, `0.5`, `½`, `1/2`, or a range `2-3`; omit for "to taste" items
  - unit: only from `units.yml`; omit for countable items (`- 2 eggs`)
  - examples: `- 360 g gluten-free flour blend for bread`, `- 1 egg, size M`, `- Salt, to taste`
  - links to base recipes are allowed: `- 500 g [[bread-flour-blend|Bread flour blend]]`
- Everything in this repo is in **English**: recipe content, code, frontmatter keys, enum values, docs and commit messages.

## Gluten-free rules (non-negotiable)

- Never use ingredients from `contains_gluten` in `gluten-flags.yml` (wheat, spelt, rye, barley, malt, couscous, bulgur, seitan, …).
- Ingredients from `needs_gf_label` (oats, soy sauce, broth, baking powder, pasta, …) must say "gluten-free" in the line: `- 2 tbsp soy sauce, gluten-free (e.g. tamari)`.
- Buckwheat is gluten-free despite its name.
- If you're unsure whether something is safe, say so in `## Notes` and leave `gluten_check: pending`.
- **Only the owner** sets `gluten_check: passed` or `status: tested` / `favorite`. Never change these fields yourself.

## Recipes you create

- Set `source: ai`, `ai_model: <your model id>` (e.g. `claude-opus-5-5`), `status: untested`, `gluten_check: pending`, `created` and `updated` to today.
- Search `cookbook/recipes/` for the same or a very similar dish first. If one exists, ask whether to improve it or add a variant.
- Be realistic about gluten-free baking: yeast doughs need a GF bread flour blend plus a binder (psyllium or xanthan). Mention known quirks (sticky dough, less rise) in the notes.

## When editing existing recipes

- Update `updated` to today.
- Keep the owner's wording in `## Notes`; add, don't rewrite, unless asked.

## Workflow

- Run `python scripts/validate.py` before you finish. Fix all errors; report warnings to the owner.
- Don't commit or push unless asked. Commit message style: `recipe: add cinnamon-rolls`, `recipe: fix baking time in brownies`, `schema: add category drink`, `app: …`.
- Schema changes (new field, category, unit) must update the schema files, the template, the validator and this file together. Ask before making them.
