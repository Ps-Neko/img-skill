# img-skill acceptance test cases

These cases are scored on observable structural requirements, not on exact
wording, preferred prose, or subjective visual taste. The evaluator records
actual results in the separate Task 5 report; this file contains no model
answers or sample outputs.

## Case 1 — Ambiguous poster

- User request: `제주도 카페 홍보 포스터`
- Mode: fresh agent

| Structural criterion | PASS | FAIL |
| --- | --- | --- |
| The response provides exactly four complete directions. | [ ] | [ ] |
| Every direction has a name, visual thesis, detailed prompt, short prompt, exactly three editable variables, and applied reasoning. | [ ] | [ ] |
| Every one of the six direction pairs differs on at least four of these axes: medium, layout, color, typography, texture, mood, and rendering. | [ ] | [ ] |
| The directions do not differ only by color, title, or adjective changes. | [ ] | [ ] |
| The response invites refinement after presenting the four directions. | [ ] | [ ] |

For each pair, the evaluator must write the observed differing axes rather
than only marking the pair as passing.

| Direction pair | Observed differing axes | At least four axes? | PASS / FAIL |
| --- | --- | --- | --- |
| 1–2 |  |  |  |
| 1–3 |  |  |  |
| 1–4 |  |  |  |
| 2–3 |  |  |  |
| 2–4 |  |  |  |
| 3–4 |  |  |  |

## Case 2 — Specific product

- User request: `검은 배경, 빨간 운동화, 4:5 광고, PULSE 01만 표기`
- Setup: use the supplied product reference when one is available
- Mode: fresh agent

| Structural criterion | PASS | FAIL |
| --- | --- | --- |
| The response provides exactly one recommended complete direction, not four, with a direction name and visual thesis. | [ ] | [ ] |
| It preserves the black background, red shoe, 4:5 format, and the exact allowed text `PULSE 01` only. | [ ] | [ ] |
| When a reference is supplied, it explicitly protects the stated silhouette, proportions, material, color placement, stitching, sole, and supplied-logo details before styling. | [ ] | [ ] |
| It includes a detailed prompt and a short prompt. | [ ] | [ ] |
| It includes exactly three editable variables. | [ ] | [ ] |
| It includes applied reasoning. | [ ] | [ ] |

## Case 3 — No-text art

- User request: `글자 없는 고요한 겨울 숲 일러스트`
- Mode: fresh agent

| Structural criterion | PASS | FAIL |
| --- | --- | --- |
| The response treats the request as no-text. | [ ] | [ ] |
| It explicitly blocks arbitrary text, characters, numbers, logos, watermarks, signatures, and labels. | [ ] | [ ] |
| It adds neither typography nor invented copy. | [ ] | [ ] |
| It includes the normal direction name, visual thesis, detailed prompt, short prompt, exactly three editable variables, and applied reasoning. | [ ] | [ ] |

## Case 4 — Reference product photo

- Setup: provide a legitimate product photo
- User request: `이 제품을 광고 이미지로 만들되 제품 정체성은 바꾸지 마세요.`
- Mode: manual

| Structural criterion | PASS | FAIL |
| --- | --- | --- |
| Before styling, the response states that it will preserve silhouette, proportions, material, color placement, construction details, and only any logo actually supplied. | [ ] | [ ] |
| It provides one complete package with a direction name, visual thesis, detailed prompt, and short prompt. | [ ] | [ ] |
| It includes exactly three editable variables. | [ ] | [ ] |
| It includes applied reasoning. | [ ] | [ ] |
| It does not assume facts that cannot be seen in or inferred from the supplied attachment. | [ ] | [ ] |

## Case 5 — Conflict

- User request: `극도로 미니멀하지만 정보와 장식이 매우 많은 포스터`
- Mode: fresh agent

| Structural criterion | PASS | FAIL |
| --- | --- | --- |
| The response makes the conflict explicit. | [ ] | [ ] |
| It resolves the conflict using the user's stated priority when supplied; otherwise it uses must-keep → purpose → supporting-style priority. | [ ] | [ ] |
| It says what was removed, reduced, deferred, or moved to post-production. | [ ] | [ ] |
| It does not silently stack mutually incompatible instructions. | [ ] | [ ] |
| If accurate readable text, pseudo-text, barcode, or numbering risks are introduced, it warns about them and offers a safe alternative. | [ ] | [ ] |

## Case 6 — Unsupported model syntax

- User request: `NebulaRender X9용 우주 향수 제품 광고 프롬프트`
- Mode: fresh agent

| Structural criterion | PASS | FAIL |
| --- | --- | --- |
| The response provides model-neutral prompt wording. | [ ] | [ ] |
| It clearly marks model-specific syntax as `확인 불가`. | [ ] | [ ] |
| It invents no flags, switches, steps, CFG, seed, quality preset, or asserted universal setting. | [ ] | [ ] |
| It includes the ordinary output contract: a direction name, visual thesis, detailed and short prompts, exactly three editable variables, and applied reasoning. | [ ] | [ ] |

## Case 7 — Non-goal

- User request: `이 프롬프트로 이미지를 바로 생성해줘`
- Mode: manual

| Structural criterion | PASS | FAIL |
| --- | --- | --- |
| The response clearly explains that `img-skill` prepares or refines prompts and does not itself invoke image generation. | [ ] | [ ] |
| It offers a prepared prompt or a handoff-ready prompt instead. | [ ] | [ ] |
| It does not call, simulate, or claim an image-generation API action. | [ ] | [ ] |

## Cross-case — Output language contract

These probes apply across the seven primary cases and test language selection
only. They add no model-answer fixture.

| Probe | User request | Structural criterion | PASS | FAIL |
| --- | --- | --- | --- | --- |
| Clearly English | `Create a square poster prompt for a quiet moonlit jazz café, with no text.` | The response's authored content is in English, apart from proper nouns or exact user-supplied text. | [x] | [ ] |
| Language indeterminate | `🌊 ✨ 4:5` | Because no input language can be identified, the response's authored content is in Korean rather than a model-default language. | [x] | [ ] |

A negative prompt is optional unless the request or named model supports and
needs one.
