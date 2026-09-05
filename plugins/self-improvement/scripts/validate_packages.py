#!/usr/bin/env python3
"""Validate both runtime payloads. Requires PyYAML in the validation environment only."""
import argparse
import json
from pathlib import Path
import re
import yaml


def validate(repo):
    repo = Path(repo).resolve()
    claude = repo if (repo / ".claude-plugin/plugin.json").is_file() else repo / "self-improvement"
    codex = repo / "plugins/self-improvement"
    metadata = [json.loads((root / kind / "plugin.json").read_text())
                for root, kind in [(claude, ".claude-plugin"), (codex, ".codex-plugin")]]
    assert metadata[0]["version"] == metadata[1]["version"], "Edition runtime versions differ"
    files = list((claude / "skills").glob("*/SKILL.md")) + list((claude / "agents").glob("*.md"))
    files += list((codex / "skills").glob("*/SKILL.md"))
    assert len(files) == 7, "Expected six skills and one Claude agent"
    for path in files:
        match = re.match(r"\A---\n(.*?)\n---\n", path.read_text(), re.S)
        assert match, "Missing frontmatter: " + str(path)
        front = yaml.safe_load(match.group(1))
        for field in ["name", "description"]:
            assert isinstance(front.get(field), str) and front[field].strip(), str(path) + ": " + field
    for root, catalog_path, key in [(repo, ".claude-plugin/marketplace.json", "source"),
                                     (repo, ".agents/plugins/marketplace.json", "source")]:
        catalog = json.loads((root / catalog_path).read_text())
        entry = next(p for p in catalog["plugins"] if p["name"] == "self-improvement")
        source = entry[key]
        source = source["path"] if isinstance(source, dict) else source
        assert (root / source).is_dir(), "Missing marketplace source"
    for root in [claude, codex]:
        hooks = json.loads((root / "hooks/hooks.json").read_text())
        assert "SessionStart" in hooks["hooks"]
    print("Both manifests, catalogs, hooks and seven YAML frontmatter blocks passed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    validate(parser.parse_args().repo)
