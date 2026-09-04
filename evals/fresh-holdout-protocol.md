# Fresh holdout validation protocol v2

This protocol is independent of the ten cases used while tuning the prompt
algorithm. A holdout item must never reuse their prompt, post, attachment, or
prompt family. Select and lock all holdout items before looking at their source
prompts or scoring generated results.

The machine-readable record is
[`fresh-holdout-manifest.json`](fresh-holdout-manifest.json), and its portable
contract is
[`fresh-holdout-manifest.schema.json`](fresh-holdout-manifest.schema.json).
`scripts/validate.py` enforces the important cross-field rules without an
external JSON Schema package.

## State transitions

- `DRAFT`: selection or metadata is incomplete. `overall_result` is `NOT_RUN`.
- `READY`: every source and attachment is fixed, its SHA-256 is recorded, the
  evaluator plan is fixed, the legacy-overlap review is recorded, and selection
  is locked. It is still `NOT_RUN`.
- `BLOCKED`: a fixture, model, evaluator, or permission is unavailable. Record
  the concrete reason; this is neither PASS nor FAIL.
- `COMPLETE`: all three conditions have at least four recorded image runs and
  every score and gate decision has evidence. Only this state may report PASS
  or FAIL.

## Required evidence for each fresh case

Record a new holdout ID, the direct original URL and date, prompt-family label,
attachment SHA-256, exact model, and either four or more seeds or an explicit
four-or-more repetition count when the model exposes no seed. Record every
evaluator ID and whether that evaluator is blind to the condition identity.
The manifest's `shared_generation_settings` records the identical aspect ratio,
resolution, guidance or quality preset, reference strength, and other available
settings. Do not vary these between conditions.

The same model, attachment, aspect ratio, generation settings, and number of
runs apply to these three conditions:

1. `baseline`: a minimal neutral prompt derived only from the image topic.
2. `skill`: the prompt produced by img-skill from that same input.
3. `source`: the account-post prompt, revealed only after holdout selection is
   locked.

Record the exact prompt or its SHA-256 for each condition. Before READY, define
case-level `must_keep_criteria` IDs. Every evaluator must assess every one of
those IDs for every run; missing, duplicate, or extra criteria invalidate the
record.

The original tuning data does not currently provide complete prompt, post,
family, and attachment fingerprints. Therefore disjointness cannot be proven
automatically from this repository alone. This limitation remains
`NOT_REVIEWED` in the draft manifest. Before READY, a human must compare all
available source records, record their identity and review time, and choose
`REVIEWED_WITH_SOURCE_GAPS` or `FULLY_VERIFIED`. This review is a gate, not proof
that unavailable fingerprints were checked.

Do not silently replace an inaccessible source or missing image. Mark the case
or study `BLOCKED` and preserve the reason.

## Scoring and hard gate

For every generated image, record its artifact URI and SHA-256. Each declared
evaluator records two independent 0–100 scores:

- `structural_score`: prompt-block coverage, ordering, and instruction clarity.
- `image_similarity_score`: visible layout, subject, palette, material,
  typography, and other applicable visual similarity criteria.

Never average these into one score. Each evaluator checks every preregistered
must-keep and prohibition separately with item-level visual evidence. If any such check
fails, `must_keep_gate_pass` is false and the case cannot be PASS regardless of
either numeric score. A blank result, planned run, prompt-only review, or schema
validation is not experimental success.

## Preregistered acceptance rule

These thresholds are project validation rules, not facts observed from the X
account and not claims about the account author's performance. A case may be
PASS only when all of the following are true:

- at least two evaluators are blind to condition identity;
- both blind evaluators submit scores and complete criterion coverage for every
  run, and all runs in all three conditions pass every must-keep check;
- the skill condition's all-run mean exceeds the baseline all-run mean by at
  least 5 points for structural score and at least 5 points for image-similarity
  score; and
- the skill condition's all-run mean is no more than 5 points below the source
  all-run mean for each of those two scores.

Calculate each mean over every recorded run in its condition, including weak or
failed outputs. Do not average the structural and image-similarity dimensions
together. Preregister these values in `protocol.acceptance_criteria`; changing
them after viewing results creates a new study version rather than amending the
completed study.

## Completing a study

Keep source prompts concealed from blind evaluators and randomize condition
labels where practical. Enter every run, including poor or failed generations.
The manifest becomes `COMPLETE` only after the validator accepts all evidence.
Repository validation passing means only that the record is internally
consistent; it does not turn a `DRAFT`, `READY`, or `BLOCKED` study into PASS.
