#!/usr/bin/env python3
"""Deterministic repository validation for img-skill."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import unquote


REQUIRED_FILES = (
    ".agents/plugins/marketplace.json",
    ".github/workflows/validate.yml",
    "LICENSE",
    "README.md",
    "evals/test-cases.md",
    "evals/fresh-holdout-manifest.schema.json",
    "evals/fresh-holdout-manifest.json",
    "evals/fresh-holdout-protocol.md",
    "plugins/img-skill/.codex-plugin/plugin.json",
    "plugins/img-skill/skills/img-skill/SKILL.md",
    "scripts/validate.py",
    "tests/test_validate.py",
    "skills/img-skill/SKILL.md",
    "skills/img-skill/agents/openai.yaml",
    "skills/img-skill/references/prompt-grammar.md",
    "skills/img-skill/references/quality-check.md",
    "skills/img-skill/references/reference-fidelity-validation-ko.md",
    "skills/img-skill/references/reference-image-fidelity.md",
    "skills/img-skill/references/templates.md",
)
MINIMUM_EVAL_CASES = 11
MANUAL_VISUAL_CASES = (8, 9, 10, 11)
HOLDOUT_STATES = {"DRAFT", "READY", "BLOCKED", "COMPLETE"}
HOLDOUT_CONDITIONS = ("baseline", "skill", "source")
HOLDOUT_RESULTS = {"NOT_RUN", "PASS", "FAIL", "BLOCKED"}
HOLDOUT_ACCEPTANCE = {
    "minimum_blind_evaluators": 2,
    "skill_vs_baseline_min_delta": {
        "structural_score": 5,
        "image_similarity_score": 5,
    },
    "skill_vs_source_noninferiority_margin": {
        "structural_score": 5,
        "image_similarity_score": 5,
    },
    "must_keep_all_runs_pass": True,
    "averaging_unit": "all_runs_per_condition",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
LOCAL_PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:[\\/]Users[\\/]", re.IGNORECASE),
    re.compile(r"file:" + r"//", re.IGNORECASE),
    re.compile(r"(?<![A-Za-z0-9])/(?:Users|home)/[^/\s]+/"),
)
LOCAL_URI_MARKER = "file:" + "//"
TODO_MARKER = "[TODO" + ":"
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


@dataclass(frozen=True)
class CheckResult:
    check_id: str
    description: str
    passed: bool
    details: str


def _result(
    check_id: str, description: str, problems: list[str], success: str
) -> CheckResult:
    return CheckResult(
        check_id=check_id,
        description=description,
        passed=not problems,
        details="; ".join(problems) if problems else success,
    )


def _markdown_files(root: Path) -> list[Path]:
    files = [root / "README.md"]
    for directory in ("docs", "evals", "plugins", "skills"):
        path = root / directory
        if path.exists():
            files.extend(sorted(path.rglob("*.md")))
    return [path for path in files if path.is_file()]


def _repository_text_files(root: Path) -> list[Path]:
    files = [root / "README.md", root / "LICENSE", root / ".gitignore"]
    supported_suffixes = {".json", ".md", ".py", ".txt", ".yaml", ".yml"}
    for directory in (
        ".agents",
        ".github",
        "docs",
        "evals",
        "plugins",
        "scripts",
        "skills",
        "tests",
    ):
        path = root / directory
        if not path.exists():
            continue
        files.extend(
            candidate
            for candidate in path.rglob("*")
            if candidate.is_file()
            and candidate.suffix.lower() in supported_suffixes
            and "__pycache__" not in candidate.parts
        )
    return sorted({path.resolve() for path in files if path.is_file()})


def _relative_link_target(raw_target: str) -> str | None:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = target.split(maxsplit=1)[0]
    if not target or target.startswith(("#", "http://", "https://", "mailto:", "//")):
        return None
    return unquote(target.split("#", 1)[0])


def _local_links(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    links: list[str] = []
    for match in MARKDOWN_LINK_RE.finditer(text):
        target = _relative_link_target(match.group(1))
        if target:
            links.append(target)
    return links


def _parse_simple_frontmatter(text: str) -> tuple[dict[str, str], str | None]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, "opening YAML delimiter is missing"
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        return {}, "closing YAML delimiter is missing"

    values: dict[str, str] = {}
    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$", line)
        if not match:
            continue
        values[match.group(1)] = match.group(2).strip('"\'')
    return values, None


def _case_sections(text: str) -> dict[int, str]:
    matches = list(re.finditer(r"^## Case (\d+)\b.*$", text, re.MULTILINE))
    sections: dict[int, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[int(match.group(1))] = text[start:end]
    return sections


def _load_json_object(path: Path, label: str, problems: list[str]) -> dict | None:
    if not path.is_file():
        problems.append(f"{label} is missing")
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        problems.append(f"{label} must contain valid JSON")
        return None
    if not isinstance(payload, dict):
        problems.append(f"{label} must contain a JSON object")
        return None
    return payload


def _file_tree(root: Path) -> dict[str, bytes]:
    if not root.is_dir():
        return {}
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }


def _required_string(value: object, label: str, problems: list[str]) -> bool:
    if not isinstance(value, str) or not value.strip():
        problems.append(f"{label} must be a non-empty string")
        return False
    return True


def _validate_completed_holdout_case(case: dict, label: str, problems: list[str]) -> None:
    """Validate artifact-backed evidence from a real three-condition run."""
    results = case.get("results")
    if not isinstance(results, dict):
        problems.append(f"{label}.results must be an object for COMPLETE")
        return
    result_conditions = results.get("conditions")
    if not isinstance(result_conditions, list):
        problems.append(f"{label}.results.conditions must be an array")
        return
    names = [entry.get("name") for entry in result_conditions if isinstance(entry, dict)]
    if names != list(HOLDOUT_CONDITIONS):
        problems.append(f"{label}.results.conditions must be baseline, skill, source in that order")
        return

    run_plan = case.get("run_plan")
    expected_runs = run_plan.get("repetitions") if isinstance(run_plan, dict) else None
    planned_seeds = run_plan.get("seeds") if isinstance(run_plan, dict) else None
    evaluators = case.get("evaluators")
    evaluator_ids = [
        evaluator.get("evaluator_id")
        for evaluator in evaluators
        if isinstance(evaluators, list)
        and isinstance(evaluator, dict)
        and isinstance(evaluator.get("evaluator_id"), str)
    ] if isinstance(evaluators, list) else []
    blind_evaluator_ids = {
        evaluator.get("evaluator_id")
        for evaluator in evaluators
        if isinstance(evaluators, list)
        and isinstance(evaluator, dict)
        and evaluator.get("blind") is True
    } if isinstance(evaluators, list) else set()
    expected_evaluator_ids = set(evaluator_ids)
    criterion_ids = case.get("must_keep_criteria")
    expected_criterion_ids = {
        criterion_id
        for criterion_id in criterion_ids
        if isinstance(criterion_ids, list) and isinstance(criterion_id, str)
    } if isinstance(criterion_ids, list) else set()
    all_run_ids: list[str] = []
    all_artifact_hashes: list[str] = []
    prompt_fingerprints: list[str] = []
    any_gate_failure = False
    scores: dict[str, dict[str, list[float]]] = {
        condition: {"structural_score": [], "image_similarity_score": []}
        for condition in HOLDOUT_CONDITIONS
    }

    for condition in result_conditions:
        condition_label = f"{label}.results.{condition['name']}"
        prompt = condition.get("prompt")
        prompt_hash = condition.get("prompt_sha256")
        has_prompt = isinstance(prompt, str) and bool(prompt.strip())
        has_prompt_hash = isinstance(prompt_hash, str) and SHA256_RE.fullmatch(prompt_hash) is not None
        if has_prompt == has_prompt_hash:
            problems.append(f"{condition_label} must record exactly one of prompt or prompt_sha256")
        elif has_prompt:
            prompt_fingerprints.append(hashlib.sha256(prompt.strip().encode("utf-8")).hexdigest())
        else:
            prompt_fingerprints.append(prompt_hash)
        runs = condition.get("runs")
        if not isinstance(runs, list) or len(runs) < 4:
            problems.append(f"{condition_label} requires at least 4 recorded runs")
            continue
        if isinstance(expected_runs, int) and len(runs) != expected_runs:
            problems.append(f"{condition_label} has {len(runs)} runs, expected {expected_runs}")
        observed_seeds = [run.get("seed") for run in runs if isinstance(run, dict)]
        non_null_seeds = [seed for seed in observed_seeds if seed is not None]
        if len(non_null_seeds) != len(set(map(str, non_null_seeds))):
            problems.append(f"{condition_label} non-null seed values must be unique")
        if isinstance(planned_seeds, list):
            if planned_seeds and observed_seeds != planned_seeds:
                problems.append(f"{condition_label} seeds must exactly match run_plan.seeds")
            if not planned_seeds and any(seed is not None for seed in observed_seeds):
                problems.append(f"{condition_label} seeds must be null when run_plan.seeds is empty")

        for run_index, run in enumerate(runs, 1):
            run_label = f"{condition_label}.runs[{run_index}]"
            if not isinstance(run, dict):
                problems.append(f"{run_label} must be an object")
                continue
            run_id = run.get("run_id")
            if _required_string(run_id, f"{run_label}.run_id", problems):
                all_run_ids.append(run_id)
            if "seed" not in run:
                problems.append(f"{run_label}.seed must be recorded (null is allowed)")
            artifact_hash = run.get("generated_artifact_sha256")
            if not isinstance(artifact_hash, str) or SHA256_RE.fullmatch(artifact_hash) is None:
                problems.append(f"{run_label}.generated_artifact_sha256 must be a lowercase SHA-256")
            else:
                all_artifact_hashes.append(artifact_hash)
            _required_string(
                run.get("generated_artifact_uri"),
                f"{run_label}.generated_artifact_uri",
                problems,
            )

            evaluator_scores = run.get("evaluator_scores")
            observed_evaluator_ids: list[str] = []
            run_assessment_failure = False
            if not isinstance(evaluator_scores, list) or not evaluator_scores:
                problems.append(f"{run_label}.evaluator_scores must be a non-empty array")
                evaluator_scores = []
            for score_index, evaluation in enumerate(evaluator_scores, 1):
                score_label = f"{run_label}.evaluator_scores[{score_index}]"
                if not isinstance(evaluation, dict):
                    problems.append(f"{score_label} must be an object")
                    continue
                evaluator_id = evaluation.get("evaluator_id")
                if _required_string(evaluator_id, f"{score_label}.evaluator_id", problems):
                    observed_evaluator_ids.append(evaluator_id)
                for score_name in ("structural_score", "image_similarity_score"):
                    score = evaluation.get(score_name)
                    if not isinstance(score, (int, float)) or isinstance(score, bool) or not 0 <= score <= 100:
                        problems.append(f"{score_label}.{score_name} must be a number from 0 to 100")
                    else:
                        scores[condition["name"]][score_name].append(float(score))
                assessments = evaluation.get("must_keep_assessments")
                observed_criterion_ids: list[str] = []
                if not isinstance(assessments, list) or not assessments:
                    problems.append(f"{score_label}.must_keep_assessments must be a non-empty array")
                    assessments = []
                for assessment_index, assessment in enumerate(assessments, 1):
                    assessment_label = f"{score_label}.must_keep_assessments[{assessment_index}]"
                    if not isinstance(assessment, dict):
                        problems.append(f"{assessment_label} must be an object")
                        continue
                    criterion_id = assessment.get("criterion_id")
                    if _required_string(criterion_id, f"{assessment_label}.criterion_id", problems):
                        observed_criterion_ids.append(criterion_id)
                    _required_string(assessment.get("evidence"), f"{assessment_label}.evidence", problems)
                    if not isinstance(assessment.get("passed"), bool):
                        problems.append(f"{assessment_label}.passed must be boolean")
                    elif not assessment["passed"]:
                        any_gate_failure = True
                        run_assessment_failure = True
                if len(observed_criterion_ids) != len(set(observed_criterion_ids)):
                    problems.append(f"{score_label}.criterion_id values must be unique")
                if set(observed_criterion_ids) != expected_criterion_ids:
                    problems.append(f"{score_label} must cover every preregistered must-keep criterion exactly")
            if len(observed_evaluator_ids) != len(set(observed_evaluator_ids)):
                problems.append(f"{run_label}.evaluator_id values must be unique")
            if set(observed_evaluator_ids) != expected_evaluator_ids:
                problems.append(f"{run_label} must contain scores from every declared evaluator only")
            if not blind_evaluator_ids.issubset(set(observed_evaluator_ids)):
                problems.append(f"{run_label} is missing a blind evaluator score")

            gate_pass = run.get("must_keep_gate_pass")
            if not isinstance(gate_pass, bool):
                problems.append(f"{run_label}.must_keep_gate_pass must be boolean")
            if run_assessment_failure and gate_pass is not False:
                problems.append(f"{run_label} cannot pass the must-keep gate after a failed assessment")
            any_gate_failure = any_gate_failure or gate_pass is False

    if len(all_run_ids) != len(set(all_run_ids)):
        problems.append(f"{label}.run_id values must be unique across all conditions")
    if len(all_artifact_hashes) != len(set(all_artifact_hashes)):
        problems.append(f"{label}.generated_artifact_sha256 values must be unique across all runs")
    if len(prompt_fingerprints) == len(HOLDOUT_CONDITIONS) and len(set(prompt_fingerprints)) != len(HOLDOUT_CONDITIONS):
        problems.append(f"{label} condition prompts must have distinct fingerprints")
    overall = case.get("overall_result")
    if overall not in {"PASS", "FAIL"}:
        problems.append(f"{label}.overall_result must be PASS or FAIL for COMPLETE")
    if any_gate_failure and overall == "PASS":
        problems.append(f"{label}.overall_result cannot be PASS when a must-keep gate failed")
    if overall == "PASS" and all(
        scores[condition][score_name]
        for condition in HOLDOUT_CONDITIONS
        for score_name in ("structural_score", "image_similarity_score")
    ):
        means = {
            condition: {
                score_name: sum(values) / len(values)
                for score_name, values in condition_scores.items()
            }
            for condition, condition_scores in scores.items()
        }
        for score_name in ("structural_score", "image_similarity_score"):
            baseline_delta = means["skill"][score_name] - means["baseline"][score_name]
            minimum_delta = HOLDOUT_ACCEPTANCE["skill_vs_baseline_min_delta"][score_name]
            if baseline_delta < minimum_delta:
                problems.append(
                    f"{label} PASS requires skill {score_name} mean to beat baseline by at least {minimum_delta}"
                )
            source_gap = means["source"][score_name] - means["skill"][score_name]
            margin = HOLDOUT_ACCEPTANCE["skill_vs_source_noninferiority_margin"][score_name]
            if source_gap > margin:
                problems.append(
                    f"{label} PASS requires skill {score_name} mean within {margin} of source"
                )
    _required_string(results.get("executed_at"), f"{label}.results.executed_at", problems)
    _required_string(results.get("comparison_summary"), f"{label}.results.comparison_summary", problems)


def validate_fresh_holdout_manifest(payload: object) -> list[str]:
    """Validate the dependency-free v2 fresh-holdout evidence contract."""
    problems: list[str] = []
    if not isinstance(payload, dict):
        return ["fresh holdout manifest must contain a JSON object"]
    if payload.get("schema_version") != "2.0":
        problems.append("schema_version must be 2.0")
    state = payload.get("status")
    if state not in HOLDOUT_STATES:
        problems.append("status must be DRAFT, READY, BLOCKED, or COMPLETE")
    overall_result = payload.get("overall_result")
    if overall_result not in HOLDOUT_RESULTS:
        problems.append("overall_result must be NOT_RUN, PASS, FAIL, or BLOCKED")
    _required_string(payload.get("study_id"), "study_id", problems)
    separation = payload.get("separation_from_tuning")
    tuning_ids: list[str] = []
    if not isinstance(separation, dict):
        problems.append("separation_from_tuning must be an object")
    else:
        tuning_ids_raw = separation.get("legacy_tuning_case_ids")
        if not isinstance(tuning_ids_raw, list) or len(tuning_ids_raw) != 10 or not all(isinstance(item, str) and item for item in tuning_ids_raw):
            problems.append("legacy_tuning_case_ids must list exactly the 10 tuning cases")
        else:
            tuning_ids = tuning_ids_raw
            if len(set(tuning_ids)) != len(tuning_ids):
                problems.append("legacy_tuning_case_ids must be unique")
        if separation.get("holdout_ids_disjoint") is not True:
            problems.append("holdout_ids_disjoint must be true")
        if separation.get("disjoint_dimensions") != [
            "prompt",
            "source_url",
            "prompt_family",
            "attachment_sha256",
        ]:
            problems.append(
                "disjoint_dimensions must cover prompt, source_url, prompt_family, attachment_sha256"
            )
        if not isinstance(separation.get("selection_locked_before_evaluation"), bool):
            problems.append("selection_locked_before_evaluation must be boolean")
        if separation.get("legacy_fingerprint_review_status") not in {
            "NOT_REVIEWED",
            "REVIEWED_WITH_SOURCE_GAPS",
            "FULLY_VERIFIED",
        }:
            problems.append("legacy_fingerprint_review_status is invalid")
        for review_field in ("legacy_fingerprint_reviewed_by", "reviewed_at"):
            review_value = separation.get(review_field)
            if review_value is not None and not isinstance(review_value, str):
                problems.append(f"{review_field} must be a string or null")
    protocol = payload.get("protocol")
    if not isinstance(protocol, dict):
        problems.append("protocol must be an object")
    else:
        if protocol.get("conditions") != list(HOLDOUT_CONDITIONS):
            problems.append("protocol.conditions must equal baseline, skill, source")
        if protocol.get("same_conditions_required") is not True:
            problems.append("protocol.same_conditions_required must be true")
        repetitions = protocol.get("minimum_repetitions_per_condition")
        if not isinstance(repetitions, int) or isinstance(repetitions, bool) or repetitions < 4:
            problems.append("minimum_repetitions_per_condition must be at least 4")
        if protocol.get("must_keep_failure_is_gate") is not True:
            problems.append("must_keep_failure_is_gate must be true")
        if protocol.get("scores_kept_separate") is not True:
            problems.append("scores_kept_separate must be true")
        if protocol.get("acceptance_criteria") != HOLDOUT_ACCEPTANCE:
            problems.append("protocol.acceptance_criteria must match the preregistered v2 rule")
    cases = payload.get("cases")
    if not isinstance(cases, list):
        problems.append("cases must be an array")
        cases = []
    case_ids: list[str] = []
    for index, case in enumerate(cases, 1):
        label = f"cases[{index}]"
        if not isinstance(case, dict):
            problems.append(f"{label} must be an object")
            continue
        holdout_id = case.get("holdout_id")
        if _required_string(holdout_id, f"{label}.holdout_id", problems):
            case_ids.append(holdout_id)
            if holdout_id in tuning_ids:
                problems.append(f"{label}.holdout_id overlaps the legacy tuning set")
        case_state = case.get("status")
        if case_state not in HOLDOUT_STATES:
            problems.append(f"{label}.status must be a valid holdout state")
        for field in ("source_url", "prompt_family", "model"):
            _required_string(case.get(field), f"{label}.{field}", problems)
        source_url = case.get("source_url")
        if isinstance(source_url, str) and not source_url.startswith("https://"):
            problems.append(f"{label}.source_url must be a direct HTTPS URL")
        source_date = case.get("source_date")
        if not isinstance(source_date, str) or ISO_DATE_RE.fullmatch(source_date) is None:
            problems.append(f"{label}.source_date must use YYYY-MM-DD")
        else:
            try:
                dt.date.fromisoformat(source_date)
            except ValueError:
                problems.append(f"{label}.source_date must be a real calendar date")
        attachment_hash = case.get("attachment_sha256")
        if not isinstance(attachment_hash, str) or SHA256_RE.fullmatch(attachment_hash) is None:
            problems.append(f"{label}.attachment_sha256 must be a lowercase SHA-256")
        run_plan = case.get("run_plan")
        if not isinstance(run_plan, dict):
            problems.append(f"{label}.run_plan must be an object")
        else:
            repetitions = run_plan.get("repetitions")
            seeds = run_plan.get("seeds")
            protocol_minimum_value = protocol.get("minimum_repetitions_per_condition") if isinstance(protocol, dict) else None
            protocol_minimum = (
                protocol_minimum_value
                if isinstance(protocol_minimum_value, int)
                and not isinstance(protocol_minimum_value, bool)
                and protocol_minimum_value >= 4
                else 4
            )
            if not isinstance(repetitions, int) or isinstance(repetitions, bool) or repetitions < protocol_minimum:
                problems.append(f"{label}.run_plan.repetitions must meet the protocol minimum")
            if not isinstance(seeds, list):
                problems.append(f"{label}.run_plan.seeds must be an array (empty if unsupported)")
            elif seeds and isinstance(repetitions, int) and len(seeds) != repetitions:
                problems.append(f"{label}.run_plan.seeds must match repetitions when supplied")
            elif seeds and len(seeds) != len(set(map(str, seeds))):
                problems.append(f"{label}.run_plan.seeds must be unique")
        shared_settings = case.get("shared_generation_settings")
        if not isinstance(shared_settings, dict) or not shared_settings:
            problems.append(f"{label}.shared_generation_settings must record identical settings")
        evaluators = case.get("evaluators")
        blind_evaluator_count = 0
        declared_evaluator_ids: list[str] = []
        if not isinstance(evaluators, list) or not evaluators:
            problems.append(f"{label}.evaluators must contain at least one evaluator")
        else:
            for evaluator_index, evaluator in enumerate(evaluators, 1):
                evaluator_label = f"{label}.evaluators[{evaluator_index}]"
                if not isinstance(evaluator, dict):
                    problems.append(f"{evaluator_label} must be an object")
                    continue
                evaluator_id = evaluator.get("evaluator_id")
                if _required_string(evaluator_id, f"{evaluator_label}.evaluator_id", problems):
                    declared_evaluator_ids.append(evaluator_id)
                if not isinstance(evaluator.get("blind"), bool):
                    problems.append(f"{evaluator_label}.blind must be boolean")
                elif evaluator["blind"]:
                    blind_evaluator_count += 1
        if case_state in {"READY", "COMPLETE"} and blind_evaluator_count < 2:
            problems.append(f"{label} requires at least 2 blind evaluators")
        if len(declared_evaluator_ids) != len(set(declared_evaluator_ids)):
            problems.append(f"{label}.evaluator_id values must be unique")
        must_keep_criteria = case.get("must_keep_criteria")
        if not isinstance(must_keep_criteria, list) or not must_keep_criteria or not all(
            isinstance(item, str) and item for item in must_keep_criteria
        ):
            problems.append(f"{label}.must_keep_criteria must contain criterion IDs")
        elif len(must_keep_criteria) != len(set(must_keep_criteria)):
            problems.append(f"{label}.must_keep_criteria IDs must be unique")
        if case.get("conditions") != list(HOLDOUT_CONDITIONS):
            problems.append(f"{label}.conditions must equal baseline, skill, source")
        case_result = case.get("overall_result")
        if case_result not in HOLDOUT_RESULTS:
            problems.append(f"{label}.overall_result is invalid")
        if case_state in {"DRAFT", "READY"} and case_result != "NOT_RUN":
            problems.append(f"{label} cannot report a result before execution")
        if case_state == "BLOCKED":
            if case_result != "BLOCKED":
                problems.append(f"{label}.overall_result must be BLOCKED")
            _required_string(case.get("blocking_reason"), f"{label}.blocking_reason", problems)
        if case_state == "COMPLETE":
            _validate_completed_holdout_case(case, label, problems)
    if len(case_ids) != len(set(case_ids)):
        problems.append("holdout_id values must be unique")
    if state == "DRAFT" and overall_result != "NOT_RUN":
        problems.append("a DRAFT manifest must have overall_result NOT_RUN")
    if state == "READY":
        if not cases:
            problems.append("a READY manifest requires at least one fresh holdout case")
        if any(case.get("status") != "READY" for case in cases if isinstance(case, dict)):
            problems.append("all cases must be READY when the manifest is READY")
        if overall_result != "NOT_RUN":
            problems.append("a READY manifest must have overall_result NOT_RUN")
        if isinstance(separation, dict) and separation.get("selection_locked_before_evaluation") is not True:
            problems.append("READY requires selection_locked_before_evaluation=true")
        if isinstance(separation, dict):
            if separation.get("legacy_fingerprint_review_status") == "NOT_REVIEWED":
                problems.append("READY requires human legacy fingerprint review")
            _required_string(separation.get("legacy_fingerprint_reviewed_by"), "legacy_fingerprint_reviewed_by", problems)
            _required_string(separation.get("reviewed_at"), "reviewed_at", problems)
    if state == "BLOCKED":
        if overall_result != "BLOCKED":
            problems.append("a BLOCKED manifest must have overall_result BLOCKED")
        _required_string(payload.get("blocking_reason"), "blocking_reason", problems)
    if state == "COMPLETE":
        if not cases:
            problems.append("a COMPLETE manifest requires completed holdout cases")
        if any(case.get("status") != "COMPLETE" for case in cases if isinstance(case, dict)):
            problems.append("all cases must be COMPLETE when the manifest is COMPLETE")
        if overall_result not in {"PASS", "FAIL"}:
            problems.append("a COMPLETE manifest must have overall_result PASS or FAIL")
        if overall_result == "PASS" and any(case.get("overall_result") != "PASS" for case in cases if isinstance(case, dict)):
            problems.append("manifest PASS requires every holdout case to PASS")
        if isinstance(separation, dict):
            if separation.get("selection_locked_before_evaluation") is not True:
                problems.append("COMPLETE requires selection_locked_before_evaluation=true")
            if separation.get("legacy_fingerprint_review_status") == "NOT_REVIEWED":
                problems.append("COMPLETE requires human legacy fingerprint review")
            _required_string(separation.get("legacy_fingerprint_reviewed_by"), "legacy_fingerprint_reviewed_by", problems)
            _required_string(separation.get("reviewed_at"), "reviewed_at", problems)
    return problems


def validate_fresh_holdout_schema_contract(schema: object) -> list[str]:
    """Detect drift in critical JSON Schema rules without jsonschema."""
    problems: list[str] = []
    if not isinstance(schema, dict):
        return ["fresh holdout schema must contain a JSON object"]
    required = schema.get("required")
    expected_root_required = {
        "schema_version",
        "study_id",
        "status",
        "overall_result",
        "separation_from_tuning",
        "protocol",
        "cases",
    }
    if not isinstance(required, list) or not expected_root_required.issubset(set(required)):
        problems.append("schema root required fields have drifted")
    all_of = schema.get("allOf")
    state_rules: dict[str, dict] = {}
    if isinstance(all_of, list):
        for rule in all_of:
            if not isinstance(rule, dict):
                continue
            condition = rule.get("if", {}).get("properties", {}).get("status", {})
            state = condition.get("const") if isinstance(condition, dict) else None
            if isinstance(state, str) and isinstance(rule.get("then"), dict):
                state_rules[state] = rule["then"]
    if set(state_rules) != HOLDOUT_STATES:
        problems.append("schema must contain if/then rules for every holdout state")
    else:
        draft_result = state_rules["DRAFT"].get("properties", {}).get("overall_result", {}).get("const")
        if draft_result != "NOT_RUN":
            problems.append("schema DRAFT rule must require NOT_RUN")
        ready_properties = state_rules["READY"].get("properties", {})
        if ready_properties.get("cases", {}).get("minItems") != 1:
            problems.append("schema READY rule must require non-empty cases")
        ready_locked = ready_properties.get("separation_from_tuning", {}).get("properties", {}).get("selection_locked_before_evaluation", {}).get("const")
        if ready_locked is not True:
            problems.append("schema READY rule must require selection lock")
        blocked_required = state_rules["BLOCKED"].get("required", [])
        if "blocking_reason" not in blocked_required:
            problems.append("schema BLOCKED rule must require blocking_reason")
        complete_properties = state_rules["COMPLETE"].get("properties", {})
        if complete_properties.get("cases", {}).get("minItems") != 1:
            problems.append("schema COMPLETE rule must require non-empty cases")
        complete_locked = complete_properties.get("separation_from_tuning", {}).get("properties", {}).get("selection_locked_before_evaluation", {}).get("const")
        if complete_locked is not True:
            problems.append("schema COMPLETE rule must require selection lock")
    protocol_const = schema.get("properties", {}).get("protocol", {}).get("properties", {}).get("acceptance_criteria", {}).get("const")
    if protocol_const != HOLDOUT_ACCEPTANCE:
        problems.append("schema acceptance criteria have drifted")
    definitions = schema.get("$defs")
    if not isinstance(definitions, dict):
        return problems + ["schema $defs are missing"]
    run_required = definitions.get("run", {}).get("required", [])
    for field in (
        "run_id",
        "seed",
        "generated_artifact_sha256",
        "generated_artifact_uri",
        "evaluator_scores",
        "must_keep_gate_pass",
    ):
        if field not in run_required:
            problems.append(f"schema run must require {field}")
    case_required = definitions.get("holdoutCase", {}).get("required", [])
    for field in ("must_keep_criteria", "evaluators", "run_plan"):
        if field not in case_required:
            problems.append(f"schema holdoutCase must require {field}")
    condition = definitions.get("conditionResult", {})
    if not isinstance(condition.get("oneOf"), list) or len(condition["oneOf"]) != 2:
        problems.append("schema conditionResult must require prompt xor prompt_sha256")
    return problems


def validate_repository(root: Path) -> list[CheckResult]:
    root = root.resolve()
    results: list[CheckResult] = []

    missing = [relative for relative in REQUIRED_FILES if not (root / relative).is_file()]
    results.append(
        _result(
            "REQUIRED_FILES",
            "required repository and skill files exist",
            [f"missing {path}" for path in missing],
            f"{len(REQUIRED_FILES)} required files found",
        )
    )

    skill_path = root / "skills/img-skill/SKILL.md"
    frontmatter_problems: list[str] = []
    skill_name = ""
    if skill_path.is_file():
        values, error = _parse_simple_frontmatter(skill_path.read_text(encoding="utf-8"))
        if error:
            frontmatter_problems.append(error)
        skill_name = values.get("name", "")
        description = values.get("description", "")
        if not re.fullmatch(r"[a-z0-9-]{1,63}", skill_name):
            frontmatter_problems.append("name must use 1-63 lowercase letters, digits, or hyphens")
        if skill_name != skill_path.parent.name:
            frontmatter_problems.append("frontmatter name must match the skill folder")
        if not description:
            frontmatter_problems.append("description is required")
        elif len(description) > 1024:
            frontmatter_problems.append("description exceeds 1024 characters")
    else:
        frontmatter_problems.append("SKILL.md cannot be inspected")
    results.append(
        _result(
            "SKILL_FRONTMATTER",
            "SKILL.md frontmatter is valid",
            frontmatter_problems,
            f"name={skill_name}",
        )
    )

    metadata_path = root / "skills/img-skill/agents/openai.yaml"
    metadata_problems: list[str] = []
    if metadata_path.is_file():
        metadata = metadata_path.read_text(encoding="utf-8")
        display_match = re.search(
            r"^\s*display_name:\s*[\"']?([^\"'\r\n]+)", metadata, re.MULTILINE
        )
        default_match = re.search(
            r"^\s*default_prompt:\s*[\"']?([^\r\n]+)", metadata, re.MULTILINE
        )
        display_name = display_match.group(1).strip() if display_match else ""
        default_prompt = default_match.group(1).rstrip("\"'").strip() if default_match else ""
        if display_name != skill_name:
            metadata_problems.append(
                f"display_name '{display_name}' does not match skill name '{skill_name}'"
            )
        if f"${skill_name}" not in default_prompt:
            metadata_problems.append("default_prompt must invoke the current skill name")
    else:
        metadata_problems.append("openai.yaml cannot be inspected")
    results.append(
        _result(
            "UI_METADATA",
            "UI metadata matches the skill",
            metadata_problems,
            "display name and default prompt are consistent",
        )
    )

    plugin_root = root / "plugins/img-skill"
    plugin_manifest_path = plugin_root / ".codex-plugin/plugin.json"
    manifest_problems: list[str] = []
    manifest = _load_json_object(
        plugin_manifest_path, "plugin manifest", manifest_problems
    )
    if manifest is not None:
        if manifest.get("name") != "img-skill":
            manifest_problems.append("plugin name must be img-skill")
        if manifest.get("name") != plugin_root.name:
            manifest_problems.append("plugin name must match the plugin folder")
        version = manifest.get("version")
        if not isinstance(version, str) or SEMVER_RE.fullmatch(version) is None:
            manifest_problems.append("plugin version must use semantic versioning")
        if (
            not isinstance(manifest.get("description"), str)
            or not manifest["description"].strip()
        ):
            manifest_problems.append("plugin description is required")
        author = manifest.get("author")
        if not isinstance(author, dict) or author.get("name") != "Ps-Neko":
            manifest_problems.append("plugin author must be Ps-Neko")
        if manifest.get("skills") != "./skills/":
            manifest_problems.append("plugin skills path must be ./skills/")
        for unsupported in ("apps", "hooks", "mcpServers"):
            if unsupported in manifest:
                manifest_problems.append(
                    f"plugin manifest declares unsupported companion: {unsupported}"
                )

        interface = manifest.get("interface")
        if not isinstance(interface, dict):
            manifest_problems.append("plugin interface metadata is required")
        else:
            expected_interface = {
                "displayName": "Image Prompt Designer",
                "developerName": "Ps-Neko",
                "category": "Creativity",
            }
            for field, expected_value in expected_interface.items():
                if interface.get(field) != expected_value:
                    manifest_problems.append(f"interface.{field} must be {expected_value}")
            for field in ("shortDescription", "longDescription"):
                if (
                    not isinstance(interface.get(field), str)
                    or not interface[field].strip()
                ):
                    manifest_problems.append(f"interface.{field} is required")
            capabilities = interface.get("capabilities")
            if not isinstance(capabilities, list) or not capabilities or not all(
                isinstance(value, str) and value.strip() for value in capabilities
            ):
                manifest_problems.append("interface.capabilities must contain strings")
            prompts = interface.get("defaultPrompt")
            if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
                manifest_problems.append(
                    "interface.defaultPrompt must contain 1-3 prompts"
                )
            elif not all(
                isinstance(prompt, str) and 0 < len(prompt) <= 128 for prompt in prompts
            ):
                manifest_problems.append(
                    "each interface.defaultPrompt entry must be 1-128 characters"
                )
    results.append(
        _result(
            "PLUGIN_MANIFEST",
            "Codex plugin manifest has valid identity and UI metadata",
            manifest_problems,
            f"img-skill {manifest.get('version', 'unknown') if manifest else 'unknown'} is packaged as Image Prompt Designer",
        )
    )

    marketplace_path = root / ".agents/plugins/marketplace.json"
    marketplace_problems: list[str] = []
    marketplace = _load_json_object(
        marketplace_path, "marketplace manifest", marketplace_problems
    )
    if marketplace is not None:
        if marketplace.get("name") != "ps-neko":
            marketplace_problems.append("marketplace name must be ps-neko")
        interface = marketplace.get("interface")
        if not isinstance(interface, dict) or interface.get("displayName") != "Ps Neko":
            marketplace_problems.append("marketplace display name must be Ps Neko")
        plugins = marketplace.get("plugins")
        if not isinstance(plugins, list):
            marketplace_problems.append("marketplace plugins must be an array")
        else:
            entries = [entry for entry in plugins if isinstance(entry, dict)]
            matches = [entry for entry in entries if entry.get("name") == "img-skill"]
            if len(matches) != 1:
                marketplace_problems.append(
                    "marketplace must contain exactly one img-skill entry"
                )
            else:
                entry = matches[0]
                source = entry.get("source")
                if source != {
                    "source": "local",
                    "path": "./plugins/img-skill",
                }:
                    marketplace_problems.append(
                        "img-skill source must be ./plugins/img-skill"
                    )
                elif not (root / "plugins/img-skill").is_dir():
                    marketplace_problems.append("packaged plugin directory is missing")
                if entry.get("policy") != {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                }:
                    marketplace_problems.append("img-skill marketplace policy is invalid")
                if entry.get("category") != "Creativity":
                    marketplace_problems.append("img-skill category must be Creativity")
    results.append(
        _result(
            "PLUGIN_MARKETPLACE",
            "GitHub marketplace entry points to the packaged plugin",
            marketplace_problems,
            "ps-neko exposes ./plugins/img-skill as an available plugin",
        )
    )

    standalone_skill_root = root / "skills/img-skill"
    packaged_skill_root = plugin_root / "skills/img-skill"
    mirror_problems: list[str] = []
    standalone_files = _file_tree(standalone_skill_root)
    packaged_files = _file_tree(packaged_skill_root)
    if not standalone_files:
        mirror_problems.append("standalone skill tree is missing")
    if not packaged_files:
        mirror_problems.append("packaged skill tree is missing")
    for relative in sorted(set(standalone_files) - set(packaged_files)):
        mirror_problems.append(f"packaged skill is missing {relative}")
    for relative in sorted(set(packaged_files) - set(standalone_files)):
        mirror_problems.append(f"packaged skill has unexpected {relative}")
    for relative in sorted(set(standalone_files) & set(packaged_files)):
        if standalone_files[relative] != packaged_files[relative]:
            mirror_problems.append(f"packaged skill differs at {relative}")
    results.append(
        _result(
            "PLUGIN_SKILL_MIRROR",
            "plugin skill matches the standalone-install skill",
            mirror_problems,
            f"{len(standalone_files)} skill files are identical",
        )
    )

    markdown_files = _markdown_files(root)
    link_problems: list[str] = []
    for path in markdown_files:
        for target in _local_links(path):
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                link_problems.append(f"{path.relative_to(root)} -> {target}")
    results.append(
        _result(
            "MARKDOWN_LINKS",
            "relative Markdown links resolve",
            link_problems,
            f"checked {len(markdown_files)} Markdown files",
        )
    )

    skill_root = (root / "skills/img-skill").resolve()
    escaping_links: list[str] = []
    if skill_root.exists():
        for path in sorted(skill_root.rglob("*.md")):
            for target in _local_links(path):
                resolved = (path.parent / target).resolve()
                try:
                    resolved.relative_to(skill_root)
                except ValueError:
                    escaping_links.append(f"{path.relative_to(root)} -> {target}")
    results.append(
        _result(
            "SKILL_SELF_CONTAINED",
            "installed-skill links remain inside the skill folder",
            escaping_links,
            "all installed-skill links are self-contained",
        )
    )

    portability_problems: list[str] = []
    for path in _repository_text_files(root):
        text = path.read_text(encoding="utf-8")
        for pattern in LOCAL_PATH_PATTERNS:
            if pattern.search(text):
                portability_problems.append(
                    f"machine-specific path in {path.relative_to(root)}"
                )
                break
        if TODO_MARKER in text or LOCAL_URI_MARKER in text.lower():
            portability_problems.append(
                f"unfinished or local marker in {path.relative_to(root)}"
            )
    results.append(
        _result(
            "PORTABILITY",
            "repository text contains no local paths or unfinished markers",
            sorted(set(portability_problems)),
            "no machine-specific paths or unfinished markers found",
        )
    )

    structure_problems: list[str] = []
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        fence_count = len(re.findall(r"^\s*```", text, re.MULTILINE))
        if fence_count % 2:
            structure_problems.append(
                f"unbalanced code fence in {path.relative_to(root)}"
            )
    results.append(
        _result(
            "MARKDOWN_STRUCTURE",
            "Markdown code fences are balanced",
            structure_problems,
            "all code fences are balanced",
        )
    )

    eval_path = root / "evals/test-cases.md"
    eval_problems: list[str] = []
    sections: dict[int, str] = {}
    if eval_path.is_file():
        eval_text = eval_path.read_text(encoding="utf-8")
        case_numbers = [
            int(value)
            for value in re.findall(r"^## Case (\d+)\b", eval_text, re.MULTILINE)
        ]
        expected = list(range(1, max(case_numbers) + 1)) if case_numbers else []
        if case_numbers != expected:
            eval_problems.append(f"case numbers must be unique and sequential: {case_numbers}")
        if len(case_numbers) < MINIMUM_EVAL_CASES:
            eval_problems.append(
                f"expected at least {MINIMUM_EVAL_CASES} cases, found {len(case_numbers)}"
            )
        sections = _case_sections(eval_text)
        for case_number, section in sections.items():
            if "- User request:" not in section:
                eval_problems.append(f"Case {case_number} is missing User request")
            if "- Mode:" not in section:
                eval_problems.append(f"Case {case_number} is missing Mode")
            if "| Structural criterion | PASS | FAIL |" not in section:
                eval_problems.append(f"Case {case_number} is missing acceptance criteria")
    else:
        eval_problems.append("evals/test-cases.md cannot be inspected")
    results.append(
        _result(
            "EVAL_CASES",
            "evaluation cases are complete and sequential",
            eval_problems,
            f"{len(sections)} structured cases found",
        )
    )

    manual_problems: list[str] = []
    if eval_path.is_file():
        eval_text = eval_path.read_text(encoding="utf-8")
        if "## Manual reference-fixture protocol" not in eval_text:
            manual_problems.append("manual reference-fixture protocol is missing")
        if "BLOCKED — fixture unavailable" not in eval_text:
            manual_problems.append("unavailable fixtures need an explicit BLOCKED state")
        for case_number in MANUAL_VISUAL_CASES:
            section = sections.get(case_number, "")
            if "- Mode: manual" not in section:
                manual_problems.append(f"Case {case_number} must remain manual")
        for case_number in (8, 9, 10):
            if "https://x.com/xiaoxiaodong01/status/" not in sections.get(case_number, ""):
                manual_problems.append(f"Case {case_number} needs a direct account-post URL")
    results.append(
        _result(
            "MANUAL_VISUAL_BOUNDARY",
            "visual-fidelity cases remain explicit manual gates",
            manual_problems,
            "Cases 8-11 are manual; unavailable fixtures are BLOCKED",
        )
    )

    holdout_manifest_path = root / "evals/fresh-holdout-manifest.json"
    holdout_problems: list[str] = []
    holdout_manifest = _load_json_object(
        holdout_manifest_path, "fresh holdout manifest", holdout_problems
    )
    if holdout_manifest is not None:
        holdout_problems.extend(validate_fresh_holdout_manifest(holdout_manifest))
    schema = _load_json_object(
        root / "evals/fresh-holdout-manifest.schema.json",
        "fresh holdout schema",
        holdout_problems,
    )
    if schema is not None:
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            holdout_problems.append("fresh holdout schema must use JSON Schema 2020-12")
        if schema.get("$id") != "https://github.com/Ps-Neko/img-skill/evals/fresh-holdout-manifest.schema.json":
            holdout_problems.append("fresh holdout schema has an unexpected $id")
        holdout_problems.extend(validate_fresh_holdout_schema_contract(schema))
    results.append(
        _result(
            "FRESH_HOLDOUT_V2",
            "fresh holdout state and evidence contract are valid; unexecuted studies never pass",
            holdout_problems,
            f"manifest status={holdout_manifest.get('status') if holdout_manifest else 'missing'}; no unexecuted PASS",
        )
    )

    reference_root = root / "skills/img-skill/references"
    discovery_problems: list[str] = []
    if reference_root.exists():
        linked_sources: dict[Path, set[Path]] = {}
        for skill_document in sorted((root / "skills/img-skill").rglob("*.md")):
            for target in _local_links(skill_document):
                resolved_target = (skill_document.parent / target).resolve()
                linked_sources.setdefault(resolved_target, set()).add(
                    skill_document.resolve()
                )
        for reference in sorted(reference_root.glob("*.md")):
            reference_path = reference.resolve()
            external_sources = linked_sources.get(reference_path, set()) - {
                reference_path
            }
            if not external_sources:
                discovery_problems.append(f"unlinked reference: {reference.name}")
    results.append(
        _result(
            "REFERENCE_DISCOVERABILITY",
            "supporting references are linked from skill documentation",
            discovery_problems,
            "all supporting references are discoverable",
        )
    )

    workflow_path = root / ".github/workflows/validate.yml"
    workflow_problems: list[str] = []
    if workflow_path.is_file():
        workflow = workflow_path.read_text(encoding="utf-8")
        required_fragments = (
            "pull_request:",
            "push:",
            "workflow_dispatch:",
            "contents: read",
            "actions/checkout@v7",
            "actions/setup-python@v7",
            "python scripts/validate.py",
            "python -m unittest discover -s tests -v",
        )
        for fragment in required_fragments:
            if fragment not in workflow:
                workflow_problems.append(f"workflow is missing: {fragment}")
        if "pull_request_target:" in workflow:
            workflow_problems.append("pull_request_target is not allowed")
    else:
        workflow_problems.append("validate.yml cannot be inspected")
    results.append(
        _result(
            "CI_WORKFLOW",
            "GitHub Actions runs validation with read-only permissions",
            workflow_problems,
            "PR, main-push, and manual triggers are configured",
        )
    )

    readme_path = root / "README.md"
    docs_problems: list[str] = []
    if readme_path.is_file():
        readme = readme_path.read_text(encoding="utf-8")
        for command in (
            "python scripts/validate.py",
            "python -m unittest discover -s tests -v",
        ):
            if command not in readme:
                docs_problems.append(f"README is missing: {command}")
        if "수동 시각 검증" not in readme:
            docs_problems.append("README must explain the manual visual gate")
    results.append(
        _result(
            "AUTOMATION_DOCS",
            "README documents automated and manual validation",
            docs_problems,
            "local commands and the manual visual boundary are documented",
        )
    )

    plugin_docs_problems: list[str] = []
    if readme_path.is_file():
        readme = readme_path.read_text(encoding="utf-8")
        for command in (
            "codex plugin marketplace add Ps-Neko/img-skill --ref main",
            "codex plugin add img-skill@ps-neko",
        ):
            if command not in readme:
                plugin_docs_problems.append(f"README is missing: {command}")
        if "새 채팅" not in readme:
            plugin_docs_problems.append("README must tell users to start a new chat")
    else:
        plugin_docs_problems.append("README.md cannot be inspected")
    results.append(
        _result(
            "PLUGIN_DOCS",
            "README documents GitHub plugin installation",
            plugin_docs_problems,
            "marketplace registration, plugin install, and new-chat pickup are documented",
        )
    )

    return results


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (defaults to the parent of scripts/)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON instead of the text report",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    results = validate_repository(args.root)
    failures = [result for result in results if not result.passed]

    if args.json:
        payload = {
            "automated": [asdict(result) for result in results],
            "summary": {
                "passed": len(results) - len(failures),
                "failed": len(failures),
            },
            "manual_visual_validation": {
                "status": "required",
                "cases": list(MANUAL_VISUAL_CASES),
                "reason": "reference assets and an image-generation result are required",
            },
            "fresh_holdout_validation": {
                "status": "required",
                "manifest": "evals/fresh-holdout-manifest.json",
                "reason": "DRAFT/READY is not PASS; COMPLETE requires recorded three-condition image runs",
            },
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for result in results:
            status = "PASS" if result.passed else "FAIL"
            print(f"[{status}] {result.check_id}: {result.details}")
        print(
            f"\nAutomated checks: {len(results) - len(failures)} passed, "
            f"{len(failures)} failed"
        )
        print(
            "Manual visual validation: required for Cases 8-11; "
            "see evals/test-cases.md"
        )

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
