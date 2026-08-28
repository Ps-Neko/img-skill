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

from validate import main, validate_repository  # noqa: E402


class RepositoryValidationTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
