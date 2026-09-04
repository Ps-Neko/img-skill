from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate import (  # noqa: E402
    main,
    validate_fresh_holdout_manifest,
    validate_fresh_holdout_schema_contract,
    validate_repository,
)


class RepositoryValidationTests(unittest.TestCase):
    def fresh_manifest(self) -> dict:
        return json.loads(
            (REPO_ROOT / "evals/fresh-holdout-manifest.json").read_text(
                encoding="utf-8"
            )
        )

    def fresh_case(self, status: str = "READY") -> dict:
        return {
            "holdout_id": "fresh-001",
            "status": status,
            "source_url": "https://x.com/xiaoxiaodong01/status/1234567890",
            "source_date": "2026-09-01",
            "prompt_family": "fresh-family-001",
            "attachment_sha256": "a" * 64,
            "model": "recorded-model-name",
            "run_plan": {"repetitions": 4, "seeds": [11, 22, 33, 44]},
            "shared_generation_settings": {
                "aspect_ratio": "4:5",
                "resolution": "same for all conditions",
            },
            "evaluators": [
                {"evaluator_id": "evaluator-1", "blind": True},
                {"evaluator_id": "evaluator-2", "blind": True},
            ],
            "must_keep_criteria": ["subject-identity"],
            "conditions": ["baseline", "skill", "source"],
            "overall_result": "NOT_RUN",
        }

    def review_and_lock(self, manifest: dict) -> None:
        separation = manifest["separation_from_tuning"]
        separation["selection_locked_before_evaluation"] = True
        separation["legacy_fingerprint_review_status"] = "REVIEWED_WITH_SOURCE_GAPS"
        separation["legacy_fingerprint_reviewed_by"] = "reviewer-1"
        separation["reviewed_at"] = "2026-09-04T12:00:00+09:00"

    def completed_results(self, failed_gate: bool = False) -> dict:
        conditions = []
        for condition_name in ("baseline", "skill", "source"):
            score_by_condition = {
                "baseline": (70, 60),
                "skill": (80, 70),
                "source": (84, 74),
            }
            structural_score, similarity_score = score_by_condition[condition_name]
            runs = []
            for run_number, seed in enumerate((11, 22, 33, 44), 1):
                passed = not (failed_gate and condition_name == "skill" and run_number == 1)
                runs.append(
                    {
                        "run_id": f"{condition_name}-{run_number}",
                        "seed": seed,
                        "generated_artifact_sha256": (
                            {"baseline": "a", "skill": "b", "source": "c"}[
                                condition_name
                            ]
                            + str(run_number)
                        )
                        * 32,
                        "generated_artifact_uri": f"artifacts/{condition_name}-{run_number}.png",
                        "evaluator_scores": [
                            {
                                "evaluator_id": evaluator_id,
                                "structural_score": structural_score,
                                "image_similarity_score": similarity_score,
                                "must_keep_assessments": [
                                    {
                                        "criterion_id": "subject-identity",
                                        "passed": passed,
                                        "evidence": "recorded visual observation",
                                    }
                                ],
                            }
                            for evaluator_id in ("evaluator-1", "evaluator-2")
                        ],
                        "must_keep_gate_pass": passed,
                    }
                )
            conditions.append(
                {"name": condition_name, "prompt": f"{condition_name} prompt", "runs": runs}
            )
        return {
            "executed_at": "2026-09-04T12:00:00+09:00",
            "conditions": conditions,
            "comparison_summary": "Three conditions were compared under identical settings.",
        }

    def copy_repository(self) -> Path:
        temporary_root = Path(self.addCleanupDirectory())
        copied_root = temporary_root / "repo"
        shutil.copytree(
            REPO_ROOT,
            copied_root,
            ignore=shutil.ignore_patterns(
                ".git",
                ".validation-deps",
                ".validation-tmp",
                "__pycache__",
                "*.pyc",
            ),
        )
        return copied_root

    def addCleanupDirectory(self) -> str:
        scratch_root = REPO_ROOT / ".validation-tmp"
        scratch_root.mkdir(exist_ok=True)
        temporary = scratch_root / f"img-skill-test-{uuid.uuid4().hex}"
        temporary.mkdir()
        self.addCleanup(shutil.rmtree, temporary, True)
        return str(temporary)

    def assertCheckFails(self, root: Path, check_id: str) -> None:
        results = {result.check_id: result for result in validate_repository(root)}
        self.assertIn(check_id, results)
        self.assertFalse(results[check_id].passed, results[check_id].details)

    def test_current_repository_passes_all_automated_checks(self) -> None:
        failures = [
            result
            for result in validate_repository(REPO_ROOT)
            if not result.passed
        ]
        self.assertEqual([], failures)

    def test_missing_required_skill_file_is_rejected(self) -> None:
        root = self.copy_repository()
        (root / "skills/img-skill/references/quality-check.md").unlink()

        self.assertCheckFails(root, "REQUIRED_FILES")

    def test_broken_relative_markdown_link_is_rejected(self) -> None:
        root = self.copy_repository()
        readme = root / "README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8") + "\n[broken](missing-file.md)\n",
            encoding="utf-8",
        )

        self.assertCheckFails(root, "MARKDOWN_LINKS")

    def test_local_machine_path_is_rejected(self) -> None:
        root = self.copy_repository()
        readme = root / "README.md"
        local_path = "C:" + "\\Users\\Example\\private.txt"
        readme.write_text(
            readme.read_text(encoding="utf-8")
            + f"\nDo not publish {local_path}\n",
            encoding="utf-8",
        )

        self.assertCheckFails(root, "PORTABILITY")

    def test_local_machine_path_in_workflow_is_rejected(self) -> None:
        root = self.copy_repository()
        workflow = root / ".github/workflows/validate.yml"
        local_path = "C:" + "\\Users\\Example\\private-script.py"
        workflow.write_text(
            workflow.read_text(encoding="utf-8")
            + f"\n# accidental local path: {local_path}\n",
            encoding="utf-8",
        )

        self.assertCheckFails(root, "PORTABILITY")

    def test_skill_reference_cannot_escape_installed_skill_folder(self) -> None:
        root = self.copy_repository()
        reference = root / "skills/img-skill/references/templates.md"
        reference.write_text(
            reference.read_text(encoding="utf-8")
            + "\n[outside](../../../README.md)\n",
            encoding="utf-8",
        )

        self.assertCheckFails(root, "SKILL_SELF_CONTAINED")

    def test_reference_linked_only_to_itself_is_not_discoverable(self) -> None:
        root = self.copy_repository()
        orphan = root / "skills/img-skill/references/orphan.md"
        orphan.write_text("# Orphan\n\n[self](orphan.md)\n", encoding="utf-8")

        self.assertCheckFails(root, "REFERENCE_DISCOVERABILITY")

    def test_ui_display_name_must_match_skill_name(self) -> None:
        root = self.copy_repository()
        metadata = root / "skills/img-skill/agents/openai.yaml"
        metadata.write_text(
            metadata.read_text(encoding="utf-8").replace(
                'display_name: "img-skill"', 'display_name: "different-name"'
            ),
            encoding="utf-8",
        )

        self.assertCheckFails(root, "UI_METADATA")

    def test_invalid_skill_frontmatter_is_rejected(self) -> None:
        root = self.copy_repository()
        skill = root / "skills/img-skill/SKILL.md"
        skill.write_text(
            skill.read_text(encoding="utf-8").replace(
                "name: img-skill", "name: Image Prompt Designer", 1
            ),
            encoding="utf-8",
        )

        self.assertCheckFails(root, "SKILL_FRONTMATTER")

    def test_evaluation_case_numbers_must_be_unique_and_sequential(self) -> None:
        root = self.copy_repository()
        cases = root / "evals/test-cases.md"
        cases.write_text(
            cases.read_text(encoding="utf-8").replace(
                "## Case 11 —", "## Case 13 —", 1
            ),
            encoding="utf-8",
        )

        self.assertCheckFails(root, "EVAL_CASES")

    def test_reference_fidelity_cases_remain_manual(self) -> None:
        root = self.copy_repository()
        cases = root / "evals/test-cases.md"
        text = cases.read_text(encoding="utf-8")
        case_8_start = text.index("## Case 8")
        case_9_start = text.index("## Case 9")
        case_8 = text[case_8_start:case_9_start].replace(
            "- Mode: manual", "- Mode: fresh agent", 1
        )
        cases.write_text(
            text[:case_8_start] + case_8 + text[case_9_start:],
            encoding="utf-8",
        )

        self.assertCheckFails(root, "MANUAL_VISUAL_BOUNDARY")

    def test_unbalanced_markdown_fence_is_rejected(self) -> None:
        root = self.copy_repository()
        reference = root / "skills/img-skill/references/prompt-grammar.md"
        reference.write_text(
            reference.read_text(encoding="utf-8") + "\n```text\n",
            encoding="utf-8",
        )

        self.assertCheckFails(root, "MARKDOWN_STRUCTURE")

    def test_workflow_requires_read_only_contents_permission(self) -> None:
        root = self.copy_repository()
        workflow = root / ".github/workflows/validate.yml"
        workflow.write_text(
            workflow.read_text(encoding="utf-8").replace(
                "contents: read", "contents: write", 1
            ),
            encoding="utf-8",
        )

        self.assertCheckFails(root, "CI_WORKFLOW")

    def test_readme_must_document_local_validation_commands(self) -> None:
        root = self.copy_repository()
        readme = root / "README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8").replace(
                "python scripts/validate.py", "run the validator", 1
            ),
            encoding="utf-8",
        )

        self.assertCheckFails(root, "AUTOMATION_DOCS")

    def test_json_report_exposes_automatic_and_manual_status(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = main(["--root", str(REPO_ROOT), "--json"])

        report = json.loads(output.getvalue())
        self.assertEqual(0, exit_code)
        self.assertEqual(0, report["summary"]["failed"])
        self.assertEqual("required", report["manual_visual_validation"]["status"])
        self.assertEqual([8, 9, 10, 11], report["manual_visual_validation"]["cases"])
        self.assertEqual("required", report["fresh_holdout_validation"]["status"])

    def test_fresh_holdout_draft_is_valid_but_not_passed(self) -> None:
        manifest = self.fresh_manifest()

        self.assertEqual([], validate_fresh_holdout_manifest(manifest))
        self.assertEqual("DRAFT", manifest["status"])
        self.assertEqual("NOT_RUN", manifest["overall_result"])

    def test_fresh_holdout_cannot_self_pass_without_runs(self) -> None:
        manifest = self.fresh_manifest()
        manifest["status"] = "COMPLETE"
        manifest["overall_result"] = "PASS"

        problems = validate_fresh_holdout_manifest(manifest)

        self.assertTrue(any("requires completed holdout cases" in item for item in problems))

    def test_fresh_holdout_ready_requires_locked_new_case(self) -> None:
        manifest = self.fresh_manifest()
        manifest["status"] = "READY"
        manifest["cases"] = [self.fresh_case()]

        problems = validate_fresh_holdout_manifest(manifest)

        self.assertTrue(any("selection_locked_before_evaluation" in item for item in problems))
        self.review_and_lock(manifest)
        self.assertEqual([], validate_fresh_holdout_manifest(manifest))

    def test_fresh_holdout_rejects_tuning_case_overlap(self) -> None:
        manifest = self.fresh_manifest()
        case = self.fresh_case()
        case["holdout_id"] = "legacy-tuning-01"
        manifest["cases"] = [case]

        problems = validate_fresh_holdout_manifest(manifest)

        self.assertTrue(any("overlaps the legacy tuning set" in item for item in problems))

    def test_completed_holdout_requires_three_conditions_and_four_runs(self) -> None:
        manifest = self.fresh_manifest()
        manifest["status"] = "COMPLETE"
        manifest["overall_result"] = "PASS"
        case = self.fresh_case(status="COMPLETE")
        case["overall_result"] = "PASS"
        case["results"] = self.completed_results()
        case["results"]["conditions"][0]["runs"].pop()
        manifest["cases"] = [case]

        problems = validate_fresh_holdout_manifest(manifest)

        self.assertTrue(any("requires at least 4 recorded runs" in item for item in problems))

    def test_must_keep_failure_is_a_hard_gate(self) -> None:
        manifest = self.fresh_manifest()
        manifest["status"] = "COMPLETE"
        manifest["overall_result"] = "PASS"
        case = self.fresh_case(status="COMPLETE")
        case["overall_result"] = "PASS"
        case["results"] = self.completed_results(failed_gate=True)
        manifest["cases"] = [case]

        problems = validate_fresh_holdout_manifest(manifest)

        self.assertTrue(any("cannot be PASS when a must-keep gate failed" in item for item in problems))

    def test_ready_and_complete_require_two_blind_evaluators(self) -> None:
        manifest = self.fresh_manifest()
        manifest["status"] = "READY"
        self.review_and_lock(manifest)
        case = self.fresh_case()
        case["evaluators"][1]["blind"] = False
        manifest["cases"] = [case]

        problems = validate_fresh_holdout_manifest(manifest)

        self.assertTrue(any("requires at least 2 blind evaluators" in item for item in problems))

    def test_pass_requires_five_point_gain_over_baseline_on_both_scores(self) -> None:
        manifest = self.fresh_manifest()
        manifest["status"] = "COMPLETE"
        manifest["overall_result"] = "PASS"
        self.review_and_lock(manifest)
        case = self.fresh_case(status="COMPLETE")
        case["overall_result"] = "PASS"
        case["results"] = self.completed_results()
        for run in case["results"]["conditions"][1]["runs"]:
            for evaluation in run["evaluator_scores"]:
                evaluation["structural_score"] = 74
                evaluation["image_similarity_score"] = 64
        manifest["cases"] = [case]

        problems = validate_fresh_holdout_manifest(manifest)

        self.assertTrue(any("structural_score mean to beat baseline" in item for item in problems))
        self.assertTrue(any("image_similarity_score mean to beat baseline" in item for item in problems))

    def test_pass_requires_noninferiority_to_source_on_both_scores(self) -> None:
        manifest = self.fresh_manifest()
        manifest["status"] = "COMPLETE"
        manifest["overall_result"] = "PASS"
        self.review_and_lock(manifest)
        case = self.fresh_case(status="COMPLETE")
        case["overall_result"] = "PASS"
        case["results"] = self.completed_results()
        for run in case["results"]["conditions"][2]["runs"]:
            for evaluation in run["evaluator_scores"]:
                evaluation["structural_score"] = 90
                evaluation["image_similarity_score"] = 80
        manifest["cases"] = [case]

        problems = validate_fresh_holdout_manifest(manifest)

        self.assertTrue(any("structural_score mean within 5 of source" in item for item in problems))
        self.assertTrue(any("image_similarity_score mean within 5 of source" in item for item in problems))

    def test_acceptance_criteria_are_preregistered(self) -> None:
        manifest = self.fresh_manifest()
        manifest["protocol"]["acceptance_criteria"][
            "skill_vs_baseline_min_delta"
        ]["structural_score"] = 0

        problems = validate_fresh_holdout_manifest(manifest)

        self.assertTrue(any("preregistered v2 rule" in item for item in problems))

    def test_completed_holdout_accepts_separate_scores_with_full_evidence(self) -> None:
        manifest = self.fresh_manifest()
        manifest["status"] = "COMPLETE"
        manifest["overall_result"] = "PASS"
        self.review_and_lock(manifest)
        case = self.fresh_case(status="COMPLETE")
        case["overall_result"] = "PASS"
        case["results"] = self.completed_results()
        manifest["cases"] = [case]

        self.assertEqual([], validate_fresh_holdout_manifest(manifest))

    def completed_manifest(self) -> tuple[dict, dict]:
        manifest = self.fresh_manifest()
        manifest["status"] = "COMPLETE"
        manifest["overall_result"] = "PASS"
        self.review_and_lock(manifest)
        case = self.fresh_case(status="COMPLETE")
        case["overall_result"] = "PASS"
        case["results"] = self.completed_results()
        manifest["cases"] = [case]
        return manifest, case

    def test_complete_requires_selection_lock(self) -> None:
        manifest, _ = self.completed_manifest()
        manifest["separation_from_tuning"]["selection_locked_before_evaluation"] = False

        problems = validate_fresh_holdout_manifest(manifest)

        self.assertTrue(any("COMPLETE requires selection_locked" in item for item in problems))

    def test_case_repetitions_must_meet_protocol_minimum(self) -> None:
        manifest = self.fresh_manifest()
        manifest["protocol"]["minimum_repetitions_per_condition"] = 5
        manifest["cases"] = [self.fresh_case(status="DRAFT")]

        problems = validate_fresh_holdout_manifest(manifest)

        self.assertTrue(any("must meet the protocol minimum" in item for item in problems))

    def test_completed_evidence_requires_unique_ids_seeds_and_artifacts(self) -> None:
        for mutation, expected in (
            (lambda case: case["results"]["conditions"][1]["runs"][0].update(run_id="baseline-1"), "run_id values must be unique"),
            (lambda case: case["results"]["conditions"][0]["runs"][1].update(seed=11), "non-null seed values must be unique"),
            (lambda case: case["results"]["conditions"][2]["runs"][0].update(generated_artifact_sha256="a1" * 32), "generated_artifact_sha256 values must be unique"),
        ):
            manifest, case = self.completed_manifest()
            mutation(case)
            problems = validate_fresh_holdout_manifest(manifest)
            self.assertTrue(any(expected in item for item in problems), problems)

    def test_result_seeds_must_match_preregistered_plan(self) -> None:
        manifest, case = self.completed_manifest()
        case["results"]["conditions"][0]["runs"][0]["seed"] = 99

        problems = validate_fresh_holdout_manifest(manifest)

        self.assertTrue(any("seeds must exactly match run_plan.seeds" in item for item in problems))

    def test_declared_evaluator_ids_must_be_unique(self) -> None:
        manifest = self.fresh_manifest()
        case = self.fresh_case()
        case["evaluators"][1]["evaluator_id"] = "evaluator-1"
        manifest["cases"] = [case]

        problems = validate_fresh_holdout_manifest(manifest)

        self.assertTrue(any("evaluator_id values must be unique" in item for item in problems))

    def test_every_run_requires_artifact_and_every_evaluator_score(self) -> None:
        manifest, case = self.completed_manifest()
        run = case["results"]["conditions"][0]["runs"][0]
        run.pop("generated_artifact_uri")
        run["evaluator_scores"].pop()

        problems = validate_fresh_holdout_manifest(manifest)

        self.assertTrue(any("generated_artifact_uri" in item for item in problems))
        self.assertTrue(any("scores from every declared evaluator" in item for item in problems))

    def test_every_evaluator_must_cover_preregistered_must_keep_ids(self) -> None:
        manifest, case = self.completed_manifest()
        evaluation = case["results"]["conditions"][0]["runs"][0]["evaluator_scores"][0]
        evaluation["must_keep_assessments"][0]["criterion_id"] = "unplanned-extra"

        problems = validate_fresh_holdout_manifest(manifest)

        self.assertTrue(any("cover every preregistered" in item for item in problems))

    def test_condition_prompts_must_exist_and_be_distinct(self) -> None:
        manifest, case = self.completed_manifest()
        case["results"]["conditions"][1]["prompt"] = "baseline prompt"

        problems = validate_fresh_holdout_manifest(manifest)

        self.assertTrue(any("condition prompts must have distinct" in item for item in problems))
        case["results"]["conditions"][1].pop("prompt")
        problems = validate_fresh_holdout_manifest(manifest)
        self.assertTrue(any("exactly one of prompt or prompt_sha256" in item for item in problems))

    def test_malformed_holdout_input_reports_errors_without_crashing(self) -> None:
        manifest, case = self.completed_manifest()
        case["must_keep_criteria"] = ["valid", {}]
        case["results"]["conditions"][0]["runs"][0]["evaluator_scores"][0][
            "must_keep_assessments"
        ] = 5
        manifest["protocol"]["minimum_repetitions_per_condition"] = "four"

        problems = validate_fresh_holdout_manifest(manifest)

        self.assertGreater(len(problems), 0)

    def test_schema_contract_rejects_state_rule_and_evidence_drift(self) -> None:
        schema = json.loads(
            (REPO_ROOT / "evals/fresh-holdout-manifest.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual([], validate_fresh_holdout_schema_contract(schema))
        schema["allOf"] = []
        schema["$defs"]["run"]["required"].remove("generated_artifact_sha256")

        problems = validate_fresh_holdout_schema_contract(schema)

        self.assertTrue(any("if/then rules" in item for item in problems))
        self.assertTrue(any("generated_artifact_sha256" in item for item in problems))

    def test_plugin_manifest_is_required_and_validated(self) -> None:
        results = {result.check_id: result for result in validate_repository(REPO_ROOT)}

        self.assertIn("PLUGIN_MANIFEST", results)
        self.assertTrue(
            results["PLUGIN_MANIFEST"].passed,
            results["PLUGIN_MANIFEST"].details,
        )

        root = self.copy_repository()
        manifest = root / "plugins/img-skill/.codex-plugin/plugin.json"
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        payload["name"] = "different-plugin"
        manifest.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        self.assertCheckFails(root, "PLUGIN_MANIFEST")

    def test_marketplace_entry_points_to_packaged_plugin(self) -> None:
        results = {result.check_id: result for result in validate_repository(REPO_ROOT)}

        self.assertIn("PLUGIN_MARKETPLACE", results)
        self.assertTrue(
            results["PLUGIN_MARKETPLACE"].passed,
            results["PLUGIN_MARKETPLACE"].details,
        )

        root = self.copy_repository()
        marketplace = root / ".agents/plugins/marketplace.json"
        payload = json.loads(marketplace.read_text(encoding="utf-8"))
        payload["plugins"][0]["source"]["path"] = "./plugins/missing"
        marketplace.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        self.assertCheckFails(root, "PLUGIN_MARKETPLACE")

    def test_packaged_skill_must_match_standalone_skill(self) -> None:
        results = {result.check_id: result for result in validate_repository(REPO_ROOT)}

        self.assertIn("PLUGIN_SKILL_MIRROR", results)
        self.assertTrue(
            results["PLUGIN_SKILL_MIRROR"].passed,
            results["PLUGIN_SKILL_MIRROR"].details,
        )

        root = self.copy_repository()
        packaged_skill = root / "plugins/img-skill/skills/img-skill/SKILL.md"
        packaged_skill.write_text(
            packaged_skill.read_text(encoding="utf-8") + "\nmirror drift\n",
            encoding="utf-8",
        )

        self.assertCheckFails(root, "PLUGIN_SKILL_MIRROR")

    def test_readme_documents_github_plugin_installation(self) -> None:
        results = {result.check_id: result for result in validate_repository(REPO_ROOT)}

        self.assertIn("PLUGIN_DOCS", results)
        self.assertTrue(results["PLUGIN_DOCS"].passed, results["PLUGIN_DOCS"].details)

        root = self.copy_repository()
        readme = root / "README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8").replace(
                "codex plugin add img-skill@ps-neko",
                "install the plugin",
            ),
            encoding="utf-8",
        )

        self.assertCheckFails(root, "PLUGIN_DOCS")


if __name__ == "__main__":
    unittest.main()
