#!/usr/bin/env python3
"""Deterministic repository validation for img-skill."""

from __future__ import annotations

import argparse
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
            "img-skill 1.0.0 is packaged as Image Prompt Designer",
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
