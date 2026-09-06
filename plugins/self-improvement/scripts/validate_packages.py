#!/usr/bin/env python3
"""Validate both runtime payloads. Requires PyYAML in the validation environment only."""
import argparse
import json
from pathlib import Path
import re
import yaml

REQUIRED_CLAUDE = ["skills/si-init/SKILL.md", "skills/si-improve/SKILL.md", "skills/si-archive/SKILL.md",
                   "agents/convention-smith.md", "hooks/hooks.json", "hooks/doctrine.md"]
REQUIRED_CODEX = ["skills/si-init/SKILL.md", "skills/si-improve/SKILL.md", "skills/si-archive/SKILL.md",
                  "hooks/hooks.json", "hooks/doctrine.md", "references/data.md", "references/runtime.md",
                  "scripts/init_project.py", "scripts/count_log_blocks.sh", "templates/CHANGELOG.md"]


def validate(repo):
    repo = Path(repo).resolve()
    claude = repo if (repo / ".claude-plugin/plugin.json").is_file() else repo / "self-improvement"
    codex = repo / "plugins/self-improvement"
    metadata = [json.loads((root / kind / "plugin.json").read_text())
                for root, kind in [(claude, ".claude-plugin"), (codex, ".codex-plugin")]]
    assert metadata[0]["version"] == metadata[1]["version"], "Edition runtime versions differ"
    missing = [str(root / name) for root, names in [(claude, REQUIRED_CLAUDE), (codex, REQUIRED_CODEX)]
               for name in names if not (root / name).is_file()]
    assert not missing, "Missing required component(s): " + ", ".join(missing)
    # Every skill and agent that exists is validated, not just the required set, so a new file with
    # broken frontmatter fails here instead of loading silently without metadata.
    files = sorted(set(list((claude / "skills").glob("*/SKILL.md")) + list((claude / "agents").glob("*.md"))
                       + list((codex / "skills").glob("*/SKILL.md"))))
    for path in files:
        match = re.match(r"\A---\n(.*?)\n---\n", path.read_text(), re.S)
        assert match, "Missing frontmatter: " + str(path)
        front = yaml.safe_load(match.group(1))
        assert isinstance(front, dict), "Frontmatter is not a mapping: " + str(path)
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
    doctrine = (claude / "hooks/doctrine.md").read_text()
    assert "references/claude-runtime.md" not in doctrine, \
        "Claude doctrine names a plugin-relative path that a consumer session cannot resolve"
    print(f"Both manifests, catalogs, hooks, required components and {len(files)} YAML frontmatter blocks passed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    validate(parser.parse_args().repo)
