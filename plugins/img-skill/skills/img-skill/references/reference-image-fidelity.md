# Reference-Image Fidelity Protocol

Use this protocol only when an actual attachment controls content, style, layout, a protected region, or a revision decision. Without an attachment, do not infer image-derived preservation requirements. This protocol structures prompts and revisions; it does not establish model performance, success rate, or pixel-identical output.

## Evidence Boundary

- **Account-observed pattern / 계정 관찰 패턴:** 13 late variants belonging to one `@xiaoxiaodong01` reference-photo transformation family repeatedly put output and preservation requirements before the stylized region. The family also used explicit region divisions, identity preservation, material actions, editorial typography, and targeted exclusions. This narrow evidence must not be generalized from a broad `47/54` count of all wording related to `maintain`.
- **Internal one-run observation / 내부 1회 관찰:** three non-blind reference-conditioned trials found strong identity preservation and design-family resemblance, while typography hierarchy, whitespace, incidental QR reuse, and structural-layer counts remained the largest gaps. The source posts, legacy scores, artifact hashes, and limitations are recorded in [reference-fidelity-validation-ko.md](reference-fidelity-validation-ko.md). This is not a controlled benchmark or a performance guarantee.
- **Analyst generalization / 분석자 일반화:** the role map, three-list method, measurable geometry fields, and comparison rubric below convert those observations into reusable decisions. They are not the account owner's official method.

## 1. Assign Image Roles

Label every attachment before writing the prompt.

| Role | Controls | Must not control |
| --- | --- | --- |
| Content source | Subject identity, count, silhouette, pose, proportions, viewpoint, visible relationships | Unrequested style or hidden facts |
| Style/layout target | Observable medium, palette roles, information density, spatial hierarchy, typography relationship | Replacement of the content source's subject identity |
| Generated result | Evidence for visible successes and failures during revision | New requirements not requested by the user |
| Region/mask | The area allowed to change or remain fixed | Content outside that region |

When both a content source and a style/layout target exist, state the precedence explicitly: **content source for identity; target for observable style and layout only**. If a role is genuinely unclear and the wrong choice would materially change the result, state the assumption instead of silently merging the images.

## 2. Build Three Lists

### Preserve

Protect only what the user requires or what defines the referenced subject:

- identity, subject count, silhouette, pose, expression, proportions, viewpoint, orientation, and perspective;
- decisive construction features and visible color placement;
- relative position and narrative relationship among important subjects;
- user-supplied exact text or logo when explicitly requested.

### Transform

Name the authorized change rather than saying only "use this style":

- allowed region or background;
- medium and making actions;
- palette simplification or transfer;
- surface, lighting, or rendering treatment;
- editorial layout and typography relationship.

### Ignore or Remove

Do not transfer incidental artifacts unless the user says they are meaningful:

- QR codes, barcodes, unrelated labels, stray microtext, dates, interface chrome, screenshots, watermarks, signatures, and bystander signage;
- accidental crops, compression artifacts, dust, or unrelated objects;
- a logo that was not supplied or requested.

If an incidental item is structurally important to the scene but its text is not, preserve its object shape while replacing the visible code or writing with a plain, text-free surface.

## 3. Write a Single Geometry Contract

Put every measurable layout constraint in one owner block so the model does not receive competing instructions. Later composition, typography, and material blocks may explain the visual treatment but must not restate or replace these numeric fields.

- output count and aspect ratio;
- region count, orientation, order, and percentages whose total is 100%;
- boundary location, such as `horizontal boundary exactly at the vertical midpoint`;
- subject count and relative placement;
- subject occupancy or safe area when important;
- required negative-space area and which side owns it;
- exact structural-layer or component count;
- title anchor, alignment, maximum line count, approximate width or height, and micro-label count.

Treat discrete counts and continuous geometry differently:

- A discrete count, such as subjects, layers, title lines, or labels, may be exact when the user supplies it, when each item is directly countable in a visible target, or when it is deliberately chosen as a design variable. Record the provenance as **user-supplied**, **observed count**, or **design choice**. Never present a design choice as a measured fact about the source.
- A continuous value, such as aspect ratio, region percentage, margin, boundary coordinate, or occupied area, may be exact only when the user supplies it or it is calculated from accessible file metadata or pixel measurement.

Do not turn one benchmark's `50/50` split or `3 layers` into a universal default. If production precision cannot be trusted to the named model, state that the result is a draft and recommend compositing or typography in post-production.

### Geometry evidence levels

- **Exact continuous value:** use only a user-supplied number or a value calculated from accessible file metadata or pixel measurement.
- **Exact discrete count:** use a user-supplied, directly counted, or explicitly designed integer and state which source produced it.
- **Observed approximation:** when estimating continuous geometry by sight, label it `approximately` and do not convert it into an exact percentage, margin, or boundary.
- **Unknown:** if neither the user nor the image provides a defensible value, omit the number or expose it as an editable variable.

When a target file is accessible, inspect its actual width and height before declaring an aspect ratio. Measure a visible region boundary in pixels when the tool allows it. Never write `exactly 53%` or a similarly precise value from visual estimation alone.

## 4. Control Typography as Geometry

For generated text, assign each field to one owner instead of repeating it:

- the typography content/style block owns exact wording, language, title/subtitle/label hierarchy, and type style;
- the single geometry contract owns maximum line and label counts, anchor, alignment, occupied area or size relation, and protected empty space;
- the restriction block owns forbidden extras, including QR codes, barcodes, invented labels, duplicate titles, dates, logos, and random letters.

When accurate typography is mission-critical, offer one of these options:

- generate a text-free image with a reserved safe area and add type in post-production; or
- generate only short, exact copy and treat the image output as a layout draft that still requires verification.

## 5. Control Structural Transformations

For exploded, deconstructed, layered, cutaway, or paper-layer imagery:

- name the exact layer or component count;
- name each permitted layer when known;
- preserve one stable anchor or base so the object can be mentally reassembled;
- derive geometry from visible or user-confirmed structure only;
- do not invent factual hidden internals from an exterior photograph.

If internal construction is not supplied, use visibly supported shells, abstract structural groupings, or an explicitly conceptual study. Do not label guessed internals as factual engineering.

## 6. Reference-Transformation Order

Use this order for attachment-based transformations:

1. image-role map;
2. the single geometry contract, including output, regions, counts, anchors, and numeric information-density limits;
3. preserve list;
4. authorized transform list and region;
5. ignore/remove list;
6. qualitative composition and information-density treatment, without new numeric geometry;
7. medium and making actions;
8. palette roles;
9. typography content and style, without repeating geometry, or a text-free post-production plan;
10. material, light, surface, finish, targeted restrictions, and verification checkpoints.

## 7. Result Comparison and Revision

When the user supplies at least two distinct images—a generated result plus a reference or target:

1. score only visible evidence using the optional visual rubric in [quality-check.md](quality-check.md);
2. list preserved successes separately from failures;
3. map each failure to one prompt block;
4. revise only those blocks;
5. keep the original must-keep list and successful blocks unchanged;
6. preserve user-supplied or measured geometry; label visually estimated geometry as approximate;
7. do not claim that a prompt revision guarantees the next image.

With fewer than two images, do not calculate or imply a visual-fidelity score. Return `N/A`, explain which comparison image is missing, and provide only evidence-grounded prompt review or attachment-role analysis. For valid comparisons, mark inapplicable criteria `N/A` and renormalize as defined in [quality-check.md](quality-check.md).

The revision prompt should include explicit checks for identity, geometry, typography hierarchy, incidental artifacts, and exact counts. The skill prepares and evaluates prompts; it does not invoke image generation itself.
