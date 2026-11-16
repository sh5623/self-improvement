#!/usr/bin/env python3
"""Conservative Codex wiring. Existing convention data is always read-only."""
import argparse
from datetime import date
import json
import os
from pathlib import Path
import posixpath
import re
import stat
import tempfile

START = "<!-- self-improvement:codex:start -->"
END = "<!-- self-improvement:codex:end -->"
PLUGIN = Path(__file__).resolve().parents[1]
# English and Korean labels are equivalent (references/data.md). The format line belongs to the
# project and is preserved verbatim; the other lines of the marked block are rewritten by this tool.
DATA_LINE = r"(?m)^(?:Data|데이터): `([^`]+)`"
ARCHIVE_LINE = r"(?m)^(?:Archive|아카이브): `([^`]+)`"
FORMAT_LINE = r"(?m)^(?:Format|형식):[ \t]*\S.*$"
ARCHIVE_FIELD = re.compile(r"((?:^(?:Format|형식):|·)[ \t]*(?:[Aa]rchive|아카이브):[ \t]*)(.*?)(?=[ \t]+·|[ \t]*$)")
NONE = {"none", "없음"}


def read(path):
    return path.read_bytes().decode("utf-8") if path.is_file() else ""


def inside(root, value):
    path = root / value
    resolved = path.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError("Path leaves the project: " + str(value))
    return path


def relative(root, path):
    return path.relative_to(root).as_posix()


def is_archive(path):
    return any("archive" in p.lower() for p in path.parts)


def prose(text):
    """Ignore fenced examples when inspecting headings and records."""
    lines, fence = [], None
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if match:
            token = match.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            lines.append(line)
    return "\n".join(lines)


def is_data(path):
    text = prose(read(path))
    identity = re.search(r"self-improvement|자가개선|convention|규약|si-plugin:|si-schema:", text, re.I)
    records = re.search(r"(?m)^(?:#{1,6}\s+|[-*]\s+)(?:\*\*)?20\d\d-\d\d-\d\d", text)
    tables = re.search(r"(?im)^##.*(?:§index|§색인)", text)
    return bool(identity and (records or tables))


def section(text, words):
    for line in prose(text).splitlines():
        if re.match(r"^#{1,6} ", line) and any(w in line.lower() for w in words):
            return line.lstrip("# ").strip()
    return "none"


def names_path(written, path):
    """A format-map value names a path verbatim (optionally as inline code); none and 없음 are one value."""
    return written in (path, "`" + path + "`") or (path == "none" and written in NONE)


def retarget_archive(line, old, new):
    """Return (format line, note). The archive field changes only when it names the old path verbatim."""
    field = ARCHIVE_FIELD.search(line)
    if not field:
        return line, ("Format line has no archive field; Archive is now `" + new + "`. "
                      "Add one if readers rely on the format map.")
    written = field.group(2)
    if not names_path(written, old):
        return line, ("Format line's archive field was kept as written (" + written + "); Archive is now `"
                      + new + "`. Edit it by hand if it describes the old destination.")
    if new == "none":
        value = "없음" if "아카이브" in field.group(1) else "none"
    else:
        value = "`" + new + "`" if written.startswith("`") else new
    return line[:field.start(2)] + value + line[field.end(2):], None


def discover(root, anchor_text, explicit):
    if explicit:
        chosen = inside(root, explicit)
        if not chosen.is_file() or is_archive(chosen.relative_to(root)):
            raise ValueError("--data-file must name an existing non-archive data file")
        return chosen
    marked = re.search(re.escape(START) + r"(.*?)" + re.escape(END), anchor_text, re.S)
    if marked:
        found = re.search(DATA_LINE, marked.group(1))
        if not found:
            raise ValueError("Existing Codex section has no Data path; repair the declaration")
        chosen = inside(root, found.group(1))
        if not chosen.is_file():
            raise ValueError("Registered data file is missing: " + found.group(1))
        return chosen
    declarations = [anchor_text]
    declarations += [read(root / f) for f in ["AGENTS.md", "CLAUDE.md", ".claude/CLAUDE.md"]]
    declared = set()
    for text in declarations:
        text = prose(text)
        explicit_names = set(re.findall(
            r"(?:\bData\s*:|\bdata file\s*:?|데이터(?:\s*파일)?\s*:)\s*`([^`\n]+\.md)`", text, re.I))
        for name in re.findall(r"`([^`\n]+\.md)`", text):
            if name not in explicit_names and not re.search(r"changelog|conventions|규약|자가개선", name, re.I):
                continue
            path = inside(root, name)
            if is_archive(path.relative_to(root)):
                continue
            if not path.is_file():
                raise ValueError("Declared convention path is missing: " + name)
            if name not in explicit_names and not is_data(path):
                raise ValueError("Inspect the declared file, then select --data-file: " + name)
            declared.add(path)
    if len(declared) == 1:
        return declared.pop()
    if len(declared) > 1:
        raise ValueError("Conflicting declared systems; select --data-file explicitly")
    candidates, uncertain = set(), set()
    docs = root / "docs"
    if docs.is_dir():
        for path in docs.rglob("*.md"):
            rel = path.relative_to(root)
            if is_archive(rel) or any(p in {".git", "node_modules", ".agents", ".claude", "plugins"} for p in rel.parts):
                continue
            inside(root, rel)
            if is_data(path):
                candidates.add(path)
            elif re.search(r"convention|규약|자가개선", path.stem, re.I):
                # Undated clause lists are valid systems, but require semantic inspection.
                uncertain.add(path)
    default = root / "docs/conventions/CHANGELOG.md"
    if default.is_file() and not is_data(default):
        raise ValueError("Default path exists but is not confirmed convention data; inspect it")
    if len(candidates) > 1:
        names = ", ".join(sorted(relative(root, p) for p in candidates))
        raise ValueError("Multiple convention systems; select --data-file: " + names)
    if uncertain:
        names = ", ".join(sorted(relative(root, p) for p in uncertain))
        raise ValueError("Unclassified convention documents; inspect before initialization: " + names)
    return next(iter(candidates), None)


def atomic_anchor(path, original, updated):
    if read(path) != original:
        raise ValueError("Instruction file changed during initialization; reread and retry")
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    fd, temporary = tempfile.mkstemp(prefix=".si-codex-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(updated.encode("utf-8"))
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def initialize(root, data_file=None, archive=None, check=False):
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("--project must be an existing directory")
    override = root / "AGENTS.override.md"
    anchor = override if override.exists() or override.is_symlink() else root / "AGENTS.md"
    if anchor.is_symlink():
        raise ValueError("Effective instruction file is a symlink; inspect ownership before wiring")
    if anchor.exists() and not anchor.is_file():
        raise ValueError("Effective instruction path is not a file")
    original = read(anchor)
    if original.count(START) != original.count(END) or original.count(START) > 1:
        raise ValueError("Malformed or duplicate Codex registration markers")
    if START in original and original.index(END) < original.index(START):
        raise ValueError("Codex registration markers are reversed")
    chosen = discover(root, original, data_file)
    created = chosen is None
    data = chosen or inside(root, "docs/conventions/CHANGELOG.md")
    name = relative(root, data)
    if any(c in name for c in "`\n\r"):
        raise ValueError("Data path cannot be represented in a Markdown registration")
    previous = re.search(re.escape(START) + r"(.*?)" + re.escape(END), original, re.S)
    registration = previous.group(1) if previous else ""
    previous_data = re.search(DATA_LINE, registration)
    previous_archive = re.search(ARCHIVE_LINE, registration)
    old_archive = previous_archive.group(1) if previous_archive else "none"
    archive_name = archive if archive is not None else (
        old_archive if previous_archive else
        ("docs/conventions/archive/" if created else "none"))
    if archive_name != "none":
        inside(root, archive_name)
    if any(c in archive_name for c in "`\n\r"):
        raise ValueError("Archive path cannot be represented in a Markdown registration")
    version = json.loads(read(PLUGIN / ".codex-plugin/plugin.json"))["version"]
    data_text = read(data)
    if created:
        data_text = read(PLUGIN / "templates/CHANGELOG.md")
        for key, value in {"VERSION": version, "DATE": date.today().isoformat(),
                           "ANCHOR": anchor.name, "ARCHIVE": archive_name}.items():
            data_text = data_text.replace("{{" + key + "}}", value)
    index = section(data_text, ["§index", "§색인"])
    routing = section(data_text, ["§routing", "§라우팅"])
    log_unit = "### dated blocks" if re.search(r"(?m)^### 20\d\d-\d\d-\d\d", prose(data_text)) else "own format"
    format_line = f"Format: index: {index} · log unit: {log_unit} · routing: {routing} · archive: {archive_name}"
    # The project's format map survives as long as the data file is the same one, whatever the
    # arguments; re-inference is only for a data file that actually changed.
    old_format = re.search(FORMAT_LINE, registration)
    same_data = bool(previous_data) and posixpath.normpath(previous_data.group(1)) == posixpath.normpath(name)
    warnings, previous_format = [], None
    if old_format and same_data:
        format_line = old_format.group(0)
        if archive_name != old_archive:
            format_line, note = retarget_archive(format_line, old_archive, archive_name)
            if note:
                warnings.append(note)
    elif old_format and old_format.group(0) != format_line:
        previous_format = old_format.group(0)
        warnings.append("Data file changed, so the format map was re-inferred from the new file; "
                        "previous_format holds the old map. Carry over what still applies.")
    block = "\n".join([
        START, "## Self-improvement (Codex)",
        "When running in Codex, use $self-improvement:si-improve for recurring, evidenced convention gaps;",
        "use $self-improvement:si-archive for over-budget or named dead/duplicate rules. Keep runtime-only",
        "instructions separate and shared rules in their canonical project documents.",
        f"Data: `{name}`", f"Archive: `{archive_name}`", format_line,
        'Report "self-improvement: N items + where / none" (or the project’s existing marker).',
        "The data file is shared with other runtimes; never initialize a second history.", END,
    ])
    if previous:
        updated = original[:previous.start()] + block + original[previous.end():]
    else:
        updated = original + ("\n" if original.endswith("\n") else "\n\n" if original else "") + block + "\n"
    status = "created" if created else "unchanged" if updated == original else "registered"
    result = dict(status=status, check=check, data_file=name, anchor=anchor.name,
                  archive=archive_name, format=format_line, existing_data_preserved=not created,
                  warnings=warnings)
    if previous_format:
        result["previous_format"] = previous_format
    if check:
        return result
    if created:
        data.parent.mkdir(parents=True, exist_ok=True)
        with data.open("x", encoding="utf-8") as stream:
            stream.write(data_text)
    if updated != original:
        atomic_anchor(anchor, original, updated)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--data-file", help="Existing canonical data file, relative to project")
    parser.add_argument("--archive", help="Confirmed archive path relative to project, or none")
    parser.add_argument("--check", action="store_true", help="Inspect and preview without writing")
    args = parser.parse_args()
    try:
        result = initialize(args.project, args.data_file, args.archive, args.check)
    except (OSError, ValueError) as error:
        parser.exit(1, "self-improvement: " + str(error) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
