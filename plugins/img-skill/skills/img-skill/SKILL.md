---
name: img-skill
description: Use when a user needs to create, expand, compare, assess, or improve image-generation prompts for posters, ads, products, portraits, spaces, illustrations, or reference-image transformations, including target-matching revisions; do not use when the user asks to directly generate or edit an image.
---

# Image Prompt Designer

## Outcome

Turn an image idea into a clear, reusable prompt while preserving the user's non-negotiable requirements.

## Evidence Scope

Keep account evidence separate from this project's operating rules.

- **Strong account evidence:** poster/editorial design. The coded corpus contained 28/54 prompt units, but repeated variants reduce this to about 16/42 prompt families.
- **Medium account evidence:** product advertising (4/54), presentation/PPT (3/54), and cinematic or sequential-story work (4/54). Treat their type-specific guidance as provisional.
- **Low account evidence / project extension:** portrait or fashion, architecture or space, and specialized 3D grammar. Label outputs that rely on these type-specific extensions.
- **Narrow reference-photo evidence:** preservation-first ordering was concentrated in 13 late variants belonging to one transformation family. Do not present a broad `47/54` preservation count as evidence of reference-image fidelity or as an account-wide rule.

The ten-block grammar, conflict priority, attachment roles, scoring rubric, and automatic checks are analyst-designed project generalizations. They are not the account owner's official method and do not establish image-generation performance or success rates.

## Workflow

Respond in the user's identifiable input language. If the language cannot be determined, use Korean.

1. Extract purpose, subject, user-stated preservation requirements, format, mood, colors, text, attachments, and model. Assign each actual attachment one role: content source, style/layout target, generated result, or region/mask. Without an attachment, do not infer image-derived identity, pose, geometry, or other preservation requirements.
2. Build the detailed prompt with the approved ten-block grammar. Use the grammar reference when its block-level detail is needed. For any attachment-based transformation or result comparison, also use the reference-image fidelity protocol.
3. Carry confirmed choices into a compact short prompt; do not silently drop must-keep details.
4. If a model is named, use only syntax that is confirmed for that model. When support is unverified, say so and offer model-neutral wording instead of inventing flags, steps, CFG, seeds, or settings.

## Ambiguity Branch

Assess five decision fields: purpose, subject, format, mood/style, and preservation requirements. Treat the request as ambiguous only when three or more fields are missing (at most two are clear). Otherwise, treat it as concrete and return one complete output package.

For an ambiguous request, immediately return exactly four complete output packages; do not pause for a selection first. Each package must satisfy the output contract. Every pair of directions must differ on at least four of exactly these seven axes: medium, layout, color, typography, texture, mood, and rendering. After delivering all four packages, invite refinement or a combination if useful.

## Preservation and Conflict Rules

List every explicit must-keep element and preserve it in both prompts. For product or reference-image work, check such details as shape, proportions, material, color placement, stitching, sole, and logo only when the user states them or they are grounded in an accessible attachment. Do not create a preservation contract from an absent reference.

Expose conflicting requirements before resolving them. Prioritize explicit must-keep requirements, then the purpose, then supporting style choices. Follow a user-stated priority; otherwise use that order and say what was chosen.

For a no-text request, explicitly prohibit arbitrary text, numbers, logos, watermarks, signatures, and labels. If accurate readable text, pseudo-text, barcodes, or numbering is requested, flag the generation risk and offer a text-free layout or post-production alternative.

## Reference-Image Fidelity Branch

When an actual image attachment is used as input, read [reference-image-fidelity.md](references/reference-image-fidelity.md).

- State which image controls subject identity and which image, if any, controls observable style or layout. A style target must not replace the content source's identity.
- Split visible details into **preserve**, **transform**, and **ignore**. Unless the user explicitly requires them, ignore incidental QR codes, barcodes, interface chrome, watermarks, unrelated signage, and stray microtext instead of restyling them as decoration.
- Put region ratios, subject and layer counts, title anchors, line and label counts, and required negative space in one geometry contract; do not repeat competing numbers elsewhere.
- Treat continuous geometry as exact only when user-supplied or measured from accessible metadata or pixels. Label visual estimates as approximate. An exact discrete count may also be directly counted or deliberately chosen, but identify it as observed or designed rather than pretending it was measured from the source.
- If a generated result and a target are supplied, report observed differences before returning the normal revision package. Correct only demonstrated failures and retain successful features.
- Calculate a visual-fidelity score only when at least two distinct images are available for direct comparison, normally a generated result plus a reference or target. With fewer than two images, return `N/A` for visual similarity and do not convert prompt inspection into a similarity score.

## Output Contract

For every concrete result, including each ambiguous direction, return:

- A mandatory direction name and a one-sentence visual thesis.
- A detailed prompt and a short prompt.
- An optional negative prompt only when the model supports it or it is useful.
- Exactly three editable variables, with safe replacement choices.
- Applied reasoning: the selected direction, preserved elements, and any resolved conflict or model-support caveat.

For reference-image work, applied reasoning must also include the attachment-role map and a concise preserve/transform/ignore summary. For result-comparison requests with two comparable images, place the fidelity score or difference table before the revision package. If scoring criteria are inapplicable, mark them `N/A` and renormalize only across applicable criteria.

## References

- Use [prompt-grammar.md](references/prompt-grammar.md) for grammar and block-order requests.
- Use [reference-image-fidelity.md](references/reference-image-fidelity.md) whenever an attachment controls content, style, layout, or revision.
- Use [templates.md](references/templates.md) for type-specific requests.
- Use [quality-check.md](references/quality-check.md) for final review.

## Boundaries

Do not directly generate or edit images. Do not scrape X. Do not invent unsupported model syntax or claim that guidance is the account owner's official algorithm. Do not report visual similarity from a prompt alone or a single image, and do not describe rubric scores as model performance, expected quality, or success rate.
