# img-skill acceptance test cases

These cases are scored on observable structural requirements, not on exact
wording, preferred prose, or subjective visual taste. The evaluator records
actual results in the separate Task 5 report; this file contains no model
answers or sample outputs.

## Case 1 — Ambiguous image idea

- User request: `제주도 느낌의 감각적인 이미지`
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

## Manual reference-fixture protocol

Cases 8–11 are manual fixture-contract tests. The executor receives only the listed attachments and the exact `User request`; setup notes and the measurement record are evaluator evidence, not hidden instructions. Before each run, record the direct source URL or asset license, attachment role, filename, pixel dimensions, SHA-256, crop or measurement method, named model, and run date. Any exact continuous geometry that should influence the response must appear in the `User request`; if the test concerns a measured value, append that measurement statement to the request.

The X-derived images used for the original internal observation are not redistributed in this repository. Cases 8–10 provide direct account-post URLs so an evaluator with legitimate access can prepare equivalent crops. If a post or required image cannot be accessed, record `BLOCKED — fixture unavailable`; do not count it as PASS or FAIL. See [the internal observation record](../skills/img-skill/references/reference-fidelity-validation-ko.md) for the original artifact dimensions, hashes, and limitations.

## Case 8 — Reference photo with incidental QR and signage

- Setup: from the account's [2026-08-20 post](https://x.com/xiaoxiaodong01/status/2090140034926350693), prepare the dog-chef upper-photo region as a content-source attachment. Record the crop and verify that nearby people, a small QR placard, and unrelated signage remain visible.
- User request: `4:5 상하 50:50 포스터. 위는 원본 사진, 아래는 같은 장면의 종이공예. 강아지 얼굴·포즈·의상·주변 사람과 시장의 관계를 유지하고 제목은 PETIT CHEF만 사용해 주세요.`
- Mode: manual

| Structural criterion | PASS | FAIL |
| --- | --- | --- |
| The response assigns the attachment the content-source role and provides one complete direction. | [ ] | [ ] |
| It separates preserve, transform, and ignore decisions in applied reasoning. | [ ] | [ ] |
| Both prompts preserve 4:5, the upper-photo/lower-paper structure, and the exact 50:50 boundary. | [ ] | [ ] |
| Both prompts protect the dog's identity, pose, clothing, subject count, and decisive market relationships. | [ ] | [ ] |
| They exclude the incidental QR, signage text, invented logos, and extra copy from the lower design. | [ ] | [ ] |
| They do not add unrequested decorative props as required composition anchors. | [ ] | [ ] |
| The exactly three editable variables cannot replace the fixed title, ratio, or subject identity. | [ ] | [ ] |

## Case 9 — Typography geometry and post-production fallback

- Setup: from the account's [2026-08-20 post](https://x.com/xiaoxiaodong01/status/2090140034926350693), prepare the orchard upper-photo region as a content-source attachment and record the crop.
- User request: `4:5 포스터. 위 사진 45%, 아래 종이공예 55%. 제목 ORCHARD AFTERNOON만 아래 영역 왼쪽 위 6% 여백 안에 넣고, 제목 영역은 전체 높이의 18%를 넘기지 마세요. 제목 외 글자는 금지하고 정확히 읽혀야 합니다.`
- Mode: manual

| Structural criterion | PASS | FAIL |
| --- | --- | --- |
| Both prompts carry the 45:55 split, 6% edge margin, 18% maximum title area, and one allowed phrase without replacing them with defaults. | [ ] | [ ] |
| The title content and title geometry are stated separately and consistently. | [ ] | [ ] |
| The composition keeps observable asymmetric negative space instead of enlarging the title or filling every area. | [ ] | [ ] |
| It warns about exact generated-text risk without deleting the requested title. | [ ] | [ ] |
| It offers a text-free reserved-area plus post-production alternative. | [ ] | [ ] |
| It forbids extra metadata, dates, coordinates, QR codes, barcodes, and random labels. | [ ] | [ ] |
| It still returns the ordinary one-direction output package with exactly three editable variables. | [ ] | [ ] |

## Case 10 — Exact structural-layer count without hidden-fact invention

- Setup: from the account's [2026-08-22 post](https://x.com/xiaoxiaodong01/status/2091032515318521971), prepare the vintage-car upper-photo region as a content-source attachment and record the crop. Supply no internal engineering reference.
- User request: `2:3 세로 포스터. 위 42%는 사진, 아래 58%는 실제 정비도처럼 정확한 차량 분해도. 차체 외피·실내 윤곽·섀시의 정확히 3단만 보여주세요. 글자는 없습니다.`
- Mode: manual

| Structural criterion | PASS | FAIL |
| --- | --- | --- |
| Both prompts fix exactly three major layers in the named order and prohibit a fourth frame, platform, or component layer. | [ ] | [ ] |
| They preserve the vehicle silhouette, proportions, viewpoint, orientation, and visible color placement. | [ ] | [ ] |
| The response exposes the conflict between an exterior-only reference and factual maintenance-diagram accuracy. | [ ] | [ ] |
| Without verified internals, it proposes a visibly grounded conceptual three-layer study instead of claiming engineering accuracy. | [ ] | [ ] |
| It invents no model, brand, hidden component, or factual internal label. | [ ] | [ ] |
| It preserves the no-text requirement and the ordinary output package. | [ ] | [ ] |

## Case 11 — Generated-result comparison and narrow revision

- Setup: prepare any legally reusable three-image fixture and record it under the manual protocol. The content source and style/layout target must support the contract in the user request. The generated result must visibly use a measured 40:60 split, enlarge the target title, repeat an incidental QR, and show four structural layers, while its subject identity, palette, and material treatment remain successful.
- User request: `첫 번째 이미지는 content source, 두 번째는 style/layout target, 세 번째는 generated result입니다. 필수 계약은 상하 정확히 50:50, 제목 최대 2줄과 목표의 제목 위치, 구조는 정확히 3단입니다. source의 피사체 정체성은 반드시 유지하고, 현재 결과에서 잘된 팔레트와 재질도 유지하세요. 목표와 결과를 비교해 실패한 부분만 고치는 프롬프트를 만들어 주세요.`
- Mode: manual

| Structural criterion | PASS | FAIL |
| --- | --- | --- |
| The response labels all three image roles and does not merge their authority. | [ ] | [ ] |
| It reports visible successes separately from failures before the revision package. | [ ] | [ ] |
| Any fidelity score uses only applicable preserve/transform criteria, marks other items N/A, and includes item-level evidence without a performance guarantee. | [ ] | [ ] |
| Failure of any explicit must-keep item or explicit prohibition is reported as a separate FAIL gate rather than hidden by an average. | [ ] | [ ] |
| It uses the user-specified or measured 50:50 contract and does not invent a different exact percentage from visual estimation. | [ ] | [ ] |
| The revision corrects the split, target-observed title geometry, QR transfer, and exact layer count; unmeasured continuous title geometry remains approximate. | [ ] | [ ] |
| It preserves the already successful identity, palette, and material blocks rather than rewriting them. | [ ] | [ ] |
| It returns the detailed and short revision prompts, exactly three safe variables, and applied reasoning. | [ ] | [ ] |

## Reference-fidelity regression gate

Run Cases 1–7 and both language probes unchanged whenever the reference-image branch changes.

| Regression criterion | PASS | FAIL |
| --- | --- | --- |
| A specific non-reference request still returns one direction and an ambiguous request still returns exactly four. | [ ] | [ ] |
| Every ordinary package still contains a direction name, visual thesis, detailed and short prompts, exactly three editable variables, and applied reasoning. | [ ] | [ ] |
| The no-text, unsupported-model, and direct-generation boundaries remain unchanged. | [ ] | [ ] |
| The new branch does not invent preservation requirements when no attachment exists. | [ ] | [ ] |
| Numeric layout fields and post-production warnings appear conditionally rather than in every prompt. | [ ] | [ ] |

## Cross-case — Output language contract

These probes apply across all applicable cases and test language selection
only. They add no model-answer fixture.

| Probe | User request | Structural criterion | PASS | FAIL |
| --- | --- | --- | --- | --- |
| Clearly English | `Create a square poster prompt for a quiet moonlit jazz café, with no text.` | The response's authored content is in English, apart from proper nouns or exact user-supplied text. | [x] | [ ] |
| Language indeterminate | `🌊 ✨ 4:5` | Because no input language can be identified, the response's authored content is in Korean rather than a model-default language. | [x] | [ ] |

A negative prompt is optional unless the request or named model supports and
needs one.
