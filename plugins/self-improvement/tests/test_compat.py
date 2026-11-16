"""Regression tests for data preservation, runtime wiring and distributable paths."""
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

PLUGIN = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("si_init", PLUGIN / "scripts/init_project.py")
si = importlib.util.module_from_spec(spec)
spec.loader.exec_module(si)
LEGACY = "# 규약 이력\r\n\r\n- 2026-09-01: 공통 검증 추가\r\n"


class Initialization(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="si project with spaces ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def put(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
        return path

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes()
                for p in self.root.rglob("*") if p.is_file()}

    def test_new_and_idempotent(self):
        first = si.initialize(self.root)
        self.assertEqual(first["status"], "created")
        self.assertFalse((self.root / "CLAUDE.md").exists())
        before = self.snapshot()
        self.assertEqual(si.initialize(self.root)["status"], "unchanged")
        self.assertEqual(before, self.snapshot())
        text = (self.root / first["data_file"]).read_text()
        self.assertNotIn("{{", text)
        self.assertIn("si-codex-template:", text)
        self.assertNotIn("si-plugin:", text)

    def test_preview_makes_no_files(self):
        self.assertEqual(si.initialize(self.root, check=True)["status"], "created")
        self.assertEqual(list(self.root.iterdir()), [])

    def test_existing_claude_history_and_import_are_preserved(self):
        data = self.put("docs/old/CONVENTIONS-CHANGELOG.md", LEGACY)
        claude = self.put("CLAUDE.md", "@AGENTS.md\n자가개선: `docs/old/CONVENTIONS-CHANGELOG.md`\n")
        before = data.read_bytes(), claude.read_bytes()
        result = si.initialize(self.root)
        self.assertEqual(result["data_file"], "docs/old/CONVENTIONS-CHANGELOG.md")
        self.assertEqual(result["archive"], "none")
        self.assertIn("index: none", result["format"])
        self.assertEqual(before, (data.read_bytes(), claude.read_bytes()))
        self.assertFalse((self.root / "docs/conventions/CHANGELOG.md").exists())

    def test_claude_dot_directory_registration(self):
        self.put("docs/CONVENTIONS-CHANGELOG.md", LEGACY)
        self.put(".claude/CLAUDE.md", "자가개선: `docs/CONVENTIONS-CHANGELOG.md`\n")
        self.assertEqual(si.initialize(self.root)["status"], "registered")

    def test_explicit_declaration_accepts_custom_name_and_undated_format(self):
        data = self.put("notes/team.md", "# Clauses\n- Validate external input.\n")
        self.put("CLAUDE.md", "## Self-improvement\nData: `notes/team.md`\n")
        result = si.initialize(self.root)
        self.assertEqual(result["data_file"], "notes/team.md")
        self.assertEqual(data.read_text(), "# Clauses\n- Validate external input.\n")

    def test_missing_custom_declared_name_stops(self):
        self.put("CLAUDE.md", "## Self-improvement\nData: `notes/missing.md`\n")
        with self.assertRaisesRegex(ValueError, "missing"):
            si.initialize(self.root)

    def test_conflicting_declarations_require_choice(self):
        self.put("notes/one.md", LEGACY)
        self.put("notes/two.md", LEGACY)
        self.put("CLAUDE.md", "자가개선\n데이터 파일: `notes/one.md`\n")
        self.put("AGENTS.md", "Self-improvement\nData: `notes/two.md`\n")
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            si.initialize(self.root)

    def test_root_override_takes_precedence(self):
        base = self.put("AGENTS.md", "keep base\n")
        self.put("AGENTS.override.md", "keep override\n")
        self.assertEqual(si.initialize(self.root)["anchor"], "AGENTS.override.md")
        self.assertEqual(base.read_text(), "keep base\n")

    def test_nested_instructions_unchanged(self):
        nested = self.put("src/AGENTS.md", "scoped instructions\n")
        si.initialize(self.root)
        self.assertEqual(nested.read_text(), "scoped instructions\n")

    def test_instruction_bytes_and_mode_preserved(self):
        anchor = self.put("AGENTS.md", "# 사용자 규약\r\n기존 내용\r\n")
        anchor.chmod(0o600)
        original = anchor.read_bytes()
        si.initialize(self.root)
        self.assertTrue(anchor.read_bytes().startswith(original))
        self.assertEqual(anchor.stat().st_mode & 0o777, 0o600)

    def test_live_symlink_anchor_refused(self):
        claude = self.put("CLAUDE.md", "Claude only\n")
        (self.root / "AGENTS.md").symlink_to(claude)
        with self.assertRaisesRegex(ValueError, "symlink"):
            si.initialize(self.root)
        self.assertEqual(claude.read_text(), "Claude only\n")

    def test_dangling_override_refused(self):
        (self.root / "AGENTS.override.md").symlink_to("missing")
        with self.assertRaisesRegex(ValueError, "symlink"):
            si.initialize(self.root)
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_directory_anchor_refused(self):
        (self.root / "AGENTS.md").mkdir()
        with self.assertRaisesRegex(ValueError, "not a file"):
            si.initialize(self.root)
        self.assertFalse((self.root / "docs").exists())

    def test_claude_symlink_to_agents_preserved(self):
        self.put("AGENTS.md", "shared project rules\n")
        (self.root / "CLAUDE.md").symlink_to("AGENTS.md")
        si.initialize(self.root)
        self.assertTrue((self.root / "CLAUDE.md").is_symlink())
        self.assertIn("When running in Codex", (self.root / "AGENTS.md").read_text())

    def test_multiple_candidates_require_choice(self):
        self.put("docs/a.md", LEGACY)
        self.put("docs/b.md", LEGACY)
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "Multiple"):
            si.initialize(self.root)
        self.assertEqual(before, self.snapshot())
        self.assertEqual(si.initialize(self.root, "docs/b.md")["data_file"], "docs/b.md")

    def test_explicit_undated_clause_list_is_valid(self):
        self.put("rules/team.md", "# Team rules\n- Validate external input.\n")
        self.assertEqual(si.initialize(self.root, "rules/team.md")["status"], "registered")

    def test_undated_convention_file_needs_inspection(self):
        self.put("docs/conventions.md", "# 규약\n- 입력 검증\n")
        with self.assertRaisesRegex(ValueError, "Unclassified"):
            si.initialize(self.root)
        self.assertFalse((self.root / "docs/conventions/CHANGELOG.md").exists())

    def test_readme_and_fenced_examples_are_not_records(self):
        self.put("docs/README.md", "# self-improvement\nExample only\n```md\n### 2026-09-01\n## §index\n```\n")
        self.assertEqual(si.initialize(self.root)["status"], "created")

    def test_archived_record_does_not_become_head(self):
        self.put("docs/archive/old.md", LEGACY)
        self.assertEqual(si.initialize(self.root)["status"], "created")

    def test_explicit_archive_cannot_be_head(self):
        self.put("docs/ARCHIVE.md", LEGACY)
        with self.assertRaisesRegex(ValueError, "non-archive"):
            si.initialize(self.root, "docs/ARCHIVE.md")

    def test_missing_registered_target_stops(self):
        self.put("AGENTS.md", si.START + "\nData: `docs/gone.md`\n" + si.END)
        with self.assertRaisesRegex(ValueError, "missing"):
            si.initialize(self.root)

    def test_missing_legacy_target_stops(self):
        self.put("CLAUDE.md", "자가개선: `docs/CONVENTIONS-CHANGELOG.md`\n")
        with self.assertRaisesRegex(ValueError, "missing"):
            si.initialize(self.root)

    def test_default_non_data_file_stops(self):
        self.put("docs/conventions/CHANGELOG.md", "human notes\n")
        with self.assertRaisesRegex(ValueError, "not confirmed"):
            si.initialize(self.root)

    def test_escape_paths_refused(self):
        for kwargs in [{"data_file": "../elsewhere.md"}, {"archive": "../archive"}]:
            with self.subTest(kwargs=kwargs), self.assertRaisesRegex(ValueError, "leaves"):
                si.initialize(self.root, **kwargs)
        self.assertEqual(self.snapshot(), {})

    def test_data_symlink_inside_project_preserved(self):
        data = self.put("records.md", LEGACY)
        (self.root / "linked.md").symlink_to("records.md")
        si.initialize(self.root, "linked.md")
        self.assertEqual(data.read_bytes(), LEGACY.encode())
        self.assertTrue((self.root / "linked.md").is_symlink())

    def test_custom_archive_matches_generated_routing(self):
        result = si.initialize(self.root, archive="history/older records")
        self.assertIn("| Archive | history/older records |", (self.root / result["data_file"]).read_text())
        self.assertEqual(si.initialize(self.root)["archive"], "history/older records")

    def test_none_archive_creates_no_archive(self):
        result = si.initialize(self.root, archive="none")
        self.assertIn("| Archive | none |", (self.root / result["data_file"]).read_text())
        self.assertFalse((self.root / "docs/conventions/archive").exists())

    def test_custom_format_survives_rerun(self):
        si.initialize(self.root)
        anchor = self.root / "AGENTS.md"
        text = re.sub(r"(?m)^Format: .+$", "Format: index: none · log unit: dated bullets · routing: docs/team.md · archive: none", anchor.read_text())
        anchor.write_text(text)
        si.initialize(self.root)
        self.assertEqual(anchor.read_text(), text)

    def registered(self, format_line, archive="old.md"):
        """A registered project whose format line was corrected by hand, as si-init asks."""
        si.initialize(self.root, archive=archive)
        anchor = self.root / "AGENTS.md"
        text = re.sub(r"(?m)^Format: .+$", lambda _: format_line, anchor.read_text())
        anchor.write_text(text)
        return anchor, text

    def test_custom_format_survives_explicit_arguments(self):
        line = "Format: index: none · log unit: dated headings · routing: docs/team-routes.md · archive: old.md"
        anchor, text = self.registered(line)
        data = si.initialize(self.root, check=True)["data_file"]
        for kwargs in [{"archive": "old.md"}, {"data_file": data}, {"data_file": "./" + data, "archive": "old.md"}]:
            with self.subTest(kwargs=kwargs):
                result = si.initialize(self.root, **kwargs)
                self.assertEqual(result["status"], "unchanged")
                self.assertEqual(result["format"], line)
                self.assertEqual(result["warnings"], [])
                self.assertEqual(anchor.read_text(), text)

    def test_archive_change_retargets_a_verbatim_field(self):
        for written, expected in [("old.md", "new.md"), ("`old.md`", "`new.md`")]:
            with self.subTest(written=written):
                line = "Format: index: none · routing: docs/team-routes.md · archive: " + written + " · log unit: dated headings"
                anchor, _ = self.registered(line)
                result = si.initialize(self.root, archive="new.md")
                self.assertEqual(result["format"], line.replace("archive: " + written, "archive: " + expected))
                self.assertEqual(result["warnings"], [])
                self.assertIn("Archive: `new.md`", anchor.read_text())
                before = anchor.read_text()
                self.assertEqual(si.initialize(self.root)["status"], "unchanged")
                self.assertEqual(anchor.read_text(), before)
                anchor.unlink()

    def test_descriptive_archive_field_is_kept_and_reported(self):
        line = ("Format: index: `## 색인` · log unit: `### YYYY-MM-DD — 제목` · routing: `docs/SELF-IMPROVEMENT.md` §2"
                " · archive: 같은 디렉터리의 `*-ARCHIVE.md`. 앱/공통 로그 선택은 §6-0을 따른다.")
        for kwargs in [{"archive": "docs/NEW-ARCHIVE.md"}, {"archive": "none"}]:
            with self.subTest(kwargs=kwargs):
                anchor, _ = self.registered(line)
                result = si.initialize(self.root, check=True, **kwargs)
                self.assertEqual(result["format"], line)
                self.assertEqual(len(result["warnings"]), 1)
                self.assertIn("kept as written", result["warnings"][0])
                anchor.unlink()

    def test_missing_archive_field_is_reported(self):
        line = "Format: index: none · log unit: dated bullets · routing: docs/team.md"
        self.registered(line)
        result = si.initialize(self.root, archive="new.md", check=True)
        self.assertEqual(result["format"], line)
        self.assertIn("no archive field", result["warnings"][0])

    def test_korean_format_line_survives_rerun(self):
        line = "형식: 색인: 없음 · 로그 단위: 날짜 제목 · 라우팅: docs/team-routes.md · 아카이브: old.md"
        anchor, text = self.registered(line)
        result = si.initialize(self.root)
        self.assertEqual(result["status"], "unchanged")
        self.assertEqual(anchor.read_text(), text)
        result = si.initialize(self.root, archive="new.md")
        self.assertEqual(result["format"], line.replace("아카이브: old.md", "아카이브: new.md"))
        self.assertEqual(result["warnings"], [])

    def test_korean_none_archive_field_is_retargeted(self):
        unset = "형식: 색인: 없음 · 라우팅: 없음 · 아카이브: 없음"
        moved = "형식: 색인: 없음 · 라우팅: 없음 · 아카이브: history/old.md"
        for line, archive, target, expected in [(unset, "none", "history/old.md", moved),
                                                (moved, "history/old.md", "none", unset)]:
            with self.subTest(target=target):
                anchor, _ = self.registered(line, archive=archive)
                result = si.initialize(self.root, archive=target, check=True)
                self.assertEqual((result["format"], result["warnings"]), (expected, []))
                anchor.unlink()

    def test_korean_archive_label_keeps_its_value(self):
        anchor, _ = self.registered("Format: index: none · archive: old.md")
        anchor.write_text(anchor.read_text().replace("Archive: `old.md`", "아카이브: `old.md`"))
        result = si.initialize(self.root, check=True)
        self.assertEqual(result["archive"], "old.md")
        self.assertEqual(result["format"], "Format: index: none · archive: old.md")

    def test_changed_data_file_reports_previous_format(self):
        line = "Format: index: none · log unit: dated headings · routing: docs/team-routes.md · archive: old.md"
        self.registered(line)
        self.put("docs/other/LOG.md", LEGACY)
        result = si.initialize(self.root, data_file="docs/other/LOG.md", check=True)
        self.assertEqual(result["previous_format"], line)
        self.assertNotEqual(result["format"], line)
        self.assertIn("re-inferred", result["warnings"][0])

    def test_schema_and_other_runtime_stamp_untouched(self):
        path = self.put("docs/conventions/CHANGELOG.md", "<!-- si-schema: v99 -->\n<!-- si-plugin: v9.0.0 -->\n" + LEGACY)
        before = path.read_bytes()
        si.initialize(self.root)
        self.assertEqual(path.read_bytes(), before)

    def test_malformed_markers_stop(self):
        for text in [si.START, si.END, si.END + si.START, (si.START + si.END) * 2]:
            self.put("AGENTS.md", text)
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, "markers"):
                si.initialize(self.root)

    def test_concurrent_anchor_change_is_detected(self):
        path = self.put("AGENTS.md", "changed by another writer")
        with self.assertRaisesRegex(ValueError, "changed"):
            si.atomic_anchor(path, "old value", "new value")
        self.assertEqual(path.read_text(), "changed by another writer")

    def test_relocated_package_works_from_other_cwd(self):
        relocated = self.root / "installed plugin with spaces"
        shutil.copytree(PLUGIN, relocated, ignore=shutil.ignore_patterns("__pycache__"))
        project = self.root / "separate project"
        project.mkdir()
        result = subprocess.run([os.sys.executable, str(relocated / "scripts/init_project.py"),
                                 "--project", str(project)], cwd=self.root,
                                capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)["status"], "created")


COUNT = PLUGIN / "scripts/count_log_blocks.sh"
CLAUDE = PLUGIN.parents[1] if (PLUGIN.parents[1] / ".claude-plugin/plugin.json").is_file() else PLUGIN.parents[1] / "self-improvement"
HEAD = "# log\n\n## §index\n\n| a | b |\n\n## §log\n\n### 2026-09-05 — real block\n\n- body\n"
EXAMPLE = "### 2026-01-01 — example heading inside a fence"


def run_count(path, *args):
    return subprocess.run(["sh", str(COUNT), str(path), *args], capture_output=True, text=True)


def count(path, *args):
    result = run_count(path, *args)
    if result.returncode != 0:
        raise AssertionError(f"count exited {result.returncode}: {result.stderr.strip()}")
    return int(result.stdout.strip())


def program(text):
    """The awk body every copy must share: from BEGIN through the whole END line, so the
    unmeasured-section exit sits inside the compared span."""
    match = re.search(r"BEGIN \{ inlog.*?\nEND \{[^\n]*\}", text, re.S)
    return match.group(0) if match else None


class LogCount(unittest.TestCase):
    """Fence handling follows CommonMark 0.31.2 §4.5; each case below is one grep over-counts."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="si count with spaces ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def data(self, body):
        path = self.root / "CHANGELOG.md"
        path.write_text(HEAD + body, encoding="utf-8")
        return path

    def grep(self, path):
        return sum(1 for line in path.read_text().splitlines() if line.startswith("### "))

    def test_baseline_counts_real_blocks_only(self):
        path = self.data("\n### 2026-09-04 — second block\n\n- body\n")
        self.assertEqual(count(path), 2)

    def test_indented_fence_is_a_fence(self):
        path = self.data(f"\n  ```md\n{EXAMPLE}\n  ```\n")
        self.assertEqual(count(path), 1)
        self.assertEqual(self.grep(path), 2)

    def test_other_fence_character_inside_is_content(self):
        path = self.data(f"\n```md\n~~~\n{EXAMPLE}\n~~~\n```\n")
        self.assertEqual(count(path), 1)
        self.assertEqual(self.grep(path), 2)

    def test_shorter_inner_fence_is_content(self):
        path = self.data(f"\n````md\n```\n{EXAMPLE}\n```\n````\n")
        self.assertEqual(count(path), 1)
        self.assertEqual(self.grep(path), 2)

    def test_headings_outside_log_section_are_not_blocks(self):
        path = self.data("\n## §migration\n\n### not a work block\n")
        self.assertEqual(count(path), 1)
        self.assertEqual(self.grep(path), 2)

    def test_heading_inside_fence_does_not_switch_section(self):
        path = self.data("\n```md\n## §index\n### still inside the fence\n```\n\n### 2026-09-03 — third block\n")
        self.assertEqual(count(path), 2)

    def test_closing_fence_needs_only_spaces_after_it(self):
        path = self.data(f"\n```md\n``` not a closer\n{EXAMPLE}\n```\n")
        self.assertEqual(count(path), 1)

    def test_four_space_indent_is_not_a_fence(self):
        path = self.data("\n    ```\n### 2026-09-02 — real block after an indented code line\n")
        self.assertEqual(count(path), 2)

    def test_format_map_unit_and_section(self):
        path = self.root / "history.md"
        path.write_text("# History\n\n## Log\n\n- 2026-09-01: a\n- 2026-09-02: b\n\n## Notes\n\n- not a record\n", encoding="utf-8")
        self.assertEqual(count(path, "^- ", "Log"), 2)
        self.assertEqual(count(path, "^- ", ""), 3)

    def test_unmatched_section_is_not_measured(self):
        path = self.root / "history.md"
        for heading in ["## History", "## 로그", "## Notes\n\n```md\n## §log\n```"]:
            path.write_text(f"# Data\n\n{heading}\n\n### 2026-11-01 a\n\n### 2026-11-02 b\n", encoding="utf-8")
            for args in [(), ("^### ", "Histroy")]:
                with self.subTest(heading=heading, args=args):
                    result = run_count(path, *args)
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(result.stdout, "")
                    self.assertIn("not measured", result.stderr)
        self.assertEqual(count(path, "^### ", "^## Notes$"), 2)
        self.assertEqual(count(path, "^### ", ""), 2)

    def test_matched_section_without_records_is_zero(self):
        path = self.root / "empty.md"
        path.write_text("# Data\n\n## §log\n\n```md\n### 2026-01-01 example\n```\n", encoding="utf-8")
        result = run_count(path)
        self.assertEqual((result.returncode, result.stdout.strip()), (0, "0"))

    def test_documented_copies_match_the_script(self):
        canonical = program(COUNT.read_text())
        self.assertIsNotNone(canonical)
        self.assertIn("exit 2", canonical)
        for doc in [PLUGIN / "references/data.md", CLAUDE / "skills/si-improve/SKILL.md",
                    CLAUDE / "skills/si-archive/SKILL.md"]:
            with self.subTest(doc=doc):
                self.assertEqual(program(doc.read_text()), canonical)


class Package(unittest.TestCase):
    def test_catalog_resolves_to_complete_payload(self):
        repo = PLUGIN.parents[1]
        catalog = json.loads((repo / ".agents/plugins/marketplace.json").read_text())
        entry = next(p for p in catalog["plugins"] if p["name"] == "self-improvement")
        self.assertEqual((repo / entry["source"]["path"]).resolve(), PLUGIN)
        metadata = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())
        self.assertEqual(metadata["name"], PLUGIN.name)
        self.assertEqual(sorted(p.parent.name for p in (PLUGIN / "skills").glob("*/SKILL.md")),
                         ["si-archive", "si-improve", "si-init"])

    def test_relative_markdown_references_exist(self):
        for path in list((PLUGIN / "skills").rglob("*.md")) + list((PLUGIN / "references").rglob("*.md")):
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if "://" not in target and not target.startswith("#"):
                    with self.subTest(path=path, target=target):
                        self.assertTrue((path.parent / target.split("#")[0]).is_file())

    def test_hook_uses_native_root_and_handles_spaces(self):
        hook = json.loads((PLUGIN / "hooks/hooks.json").read_text())["hooks"]["SessionStart"][0]["hooks"][0]
        with tempfile.TemporaryDirectory(prefix="si hook with spaces ") as temp:
            payload = Path(temp) / "payload"
            shutil.copytree(PLUGIN / "hooks", payload / "hooks")
            env = dict(os.environ, PLUGIN_ROOT=str(payload))
            env.pop("CLAUDE_PLUGIN_ROOT", None)
            result = subprocess.run(["sh", "-c", hook["command"]], env=env, cwd=temp,
                                    capture_output=True, check=True)
            self.assertEqual(result.stdout, (PLUGIN / "hooks/doctrine.md").read_bytes())


if __name__ == "__main__":
    unittest.main()
