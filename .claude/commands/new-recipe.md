---
description: Create a new gluten-free recipe in the cookbook
argument-hint: <dish or idea, e.g. "cheese spaetzle" or "something with pumpkin">
---
Create a new gluten-free recipe for: $ARGUMENTS

1. Read CLAUDE.md, cookbook/templates/recipe.md and everything in schema/.
2. Check cookbook/recipes/ for the same or a very similar dish. If one exists, stop and ask whether to improve it or create a variant.
3. Write the recipe to cookbook/recipes/<slug>.md, following the template and the rules in CLAUDE.md exactly (source: ai, status: untested, gluten_check: pending).
4. Run `python scripts/validate.py` and fix every error in the new file.
5. Give a short summary: file name, category, tags, and any gluten points the owner should check when shopping. Don't commit.
