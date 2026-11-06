---
description: Review recipes for hidden gluten sources
argument-hint: [recipe slug, or empty for all recipes with gluten_check pending]
---
Review for gluten safety: $ARGUMENTS
(If empty, review every recipe in cookbook/recipes/ with `gluten_check: pending`.)

1. Run `python scripts/validate.py` and note all gluten errors and warnings.
2. Then go beyond the script: read each ingredient line and look for hidden gluten the word lists miss (spice blends, sauces, sweets, processed meat, cross-contamination risks like non-certified oats).
3. For each recipe, list: safe / needs a labeled product (which one, what to look for) / problem (with a gluten-free replacement).
4. Don't change `gluten_check` or `status`. Only edit recipe files if the owner asks you to apply the fixes.
