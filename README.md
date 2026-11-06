# Celia 🍞🚫

My gluten-free cookbook: my own recipes and AI-generated recipes in Markdown, managed in Obsidian, with a dedicated app coming soon.

## Quick Start

1. Clone the repo and open the `cookbook/` folder in Obsidian as a vault.
2. In Obsidian, enable the **Templates** core plugin and install the **Dataview** community plugin.
3. New recipe: create a file in `cookbook/recipes/` (file name, e.g. `apple-cake.md`) and insert the `recipe` template.
4. Check before committing:

```bash
pip install -r scripts/requirements.txt
python scripts/validate.py
```

## Structure

| Path | Contents |
|---|---|
| `cookbook/recipes/` | One recipe per file, flat structure, categories in front matter |
| `cookbook/indexes/` | Indexes: A–Z, by category, untested, favorites |
| `cookbook/templates/` | Recipe template |
| `cookbook/images/` | Photos, named after the recipe |
| `schema/` | Format definition: fields, categories, units, gluten warning list |
| `scripts/validate.py` | Checks all recipes (also runs in GitHub Actions) |
| `app/` | Later: a dedicated app for viewing and editing |
| `CLAUDE.md` | Instructions for Claude and other agents |

## Recipe Status

- `status`: `untested` → `tested` → `favorite`
- `gluten_check`: `pending` → `passed` (set only after verifying the ingredients yourself)
- `source`: `own`, `ai`, `web`, `book`, `family`
