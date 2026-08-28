---
name: img-skill
description: Use when a user needs to create, expand, compare, or improve image-generation prompts for posters, ads, products, portraits, spaces, illustrations, or reference-image transformations; do not use when the user asks to directly generate or edit an image.
---

# Image Prompt Designer

## Outcome

Turn an image idea into a clear, reusable prompt while preserving the user's non-negotiable requirements.

## Workflow

1. Extract purpose, subject, preservation requirements, format, mood, colors, text, attachments, and model.
2. Build the detailed prompt with the approved ten-block grammar. Use the grammar reference when its block-level detail is needed.
3. Carry confirmed choices into a compact short prompt; do not silently drop must-keep details.
4. If a model is named, use only syntax that is confirmed for that model. When support is unverified, say so and offer model-neutral wording instead of inventing flags, steps, CFG, seeds, or settings.

## Ambiguity Branch

Assess five decision fields: purpose, subject, format, mood/style, and preservation requirements. Treat the request as ambiguous only when three or more fields are missing (at most two are clear). Otherwise, treat it as concrete and return one complete output package.

For an ambiguous request, immediately return exactly four complete output packages; do not pause for a selection first. Each package must satisfy the output contract. Every pair of directions must differ on at least four of exactly these seven axes: medium, layout, color, typography, texture, mood, and rendering. After delivering all four packages, invite refinement or a combination if useful.

## Preservation and Conflict Rules

List every explicit must-keep element and preserve it in both prompts. For product or reference-image work, check such details as shape, proportions, material, color placement, stitching, sole, and logo when stated.

Expose conflicting requirements before resolving them. Prioritize explicit must-keep requirements, then the purpose, then supporting style choices. Follow a user-stated priority; otherwise use that order and say what was chosen.

For a no-text request, explicitly prohibit arbitrary text, numbers, logos, watermarks, signatures, and labels. If accurate readable text, pseudo-text, barcodes, or numbering is requested, flag the generation risk and offer a text-free layout or post-production alternative.

## Output Contract

For every concrete result, including each ambiguous direction, return:

- A mandatory direction name and a one-sentence visual thesis.
- A detailed prompt and a short prompt.
- An optional negative prompt only when the model supports it or it is useful.
- Exactly three editable variables, with safe replacement choices.
- Applied reasoning: the selected direction, preserved elements, and any resolved conflict or model-support caveat.

## References

- Use [prompt-grammar.md](references/prompt-grammar.md) for grammar and block-order requests.
- Use [templates.md](references/templates.md) for type-specific requests.
- Use [quality-check.md](references/quality-check.md) for final review.

## Boundaries

Do not directly generate or edit images. Do not scrape X. Do not invent unsupported model syntax or claim that guidance is the account owner's official algorithm.
