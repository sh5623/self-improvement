#!/usr/bin/env python3
"""Read a local marketplace through Codex, without installation or a model turn."""
import argparse
import json
from pathlib import Path
import queue
import subprocess
import threading


def inspect(repo):
    repo = Path(repo).resolve()
    process = subprocess.Popen(["codex", "app-server"], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    messages = queue.Queue()

    def pump():
        for line in process.stdout:
            try:
                messages.put(json.loads(line))
            except ValueError:
                pass

    threading.Thread(target=pump, daemon=True).start()
    sequence = 0

    def request(method, params):
        nonlocal sequence
        sequence += 1
        process.stdin.write(json.dumps(dict(id=sequence, method=method, params=params)) + "\n")
        process.stdin.flush()
        while True:
            message = messages.get(timeout=20)
            if message.get("id") == sequence:
                if "error" in message:
                    raise RuntimeError(message["error"])
                return message["result"]

    try:
        request("initialize", {"clientInfo": {"name": "si_compat_check", "version": "1.0.0"},
                               "capabilities": {"experimentalApi": True}})
        process.stdin.write('{"method":"initialized"}\n')
        process.stdin.flush()
        plugin = request("plugin/read", {"marketplacePath": str(repo / ".agents/plugins/marketplace.json"),
                                         "pluginName": "self-improvement"})["plugin"]
        names = sorted(s["name"] for s in plugin["skills"])
        expected = ["self-improvement:" + s for s in ["si-archive", "si-improve", "si-init"]]
        if names != expected:
            raise ValueError("Unexpected runtime skill names: " + repr(names))
        events = [h["eventName"] for h in plugin["hooks"]]
        if events != ["sessionStart"]:
            raise ValueError("Missing or duplicate SessionStart hook: " + repr(events))
        return dict(marketplace=plugin["marketplaceName"], version=plugin["summary"]["localVersion"],
                    skills=names, hooks=events, mode="read-only catalog inspection")
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="Marketplace repository root")
    args = parser.parse_args()
    print(json.dumps(inspect(args.repo), ensure_ascii=False, indent=2))
