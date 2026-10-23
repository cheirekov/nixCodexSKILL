#!/usr/bin/env python3
"""Inspect bounded project metadata without evaluating Nix or reading secrets."""

import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess


def command(argv, cwd):
    try:
        result = subprocess.run(
            argv, cwd=cwd, capture_output=True, text=True, timeout=10,
            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
        )
        return {"exit_code": result.returncode, "stdout": result.stdout[:8192].strip()}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"error": type(exc).__name__}


def inspect(root):
    markers = [
        "AGENTS.md", "flake.nix", "flake.lock", "shell.nix", "default.nix",
        "devenv.nix", "devenv.yaml", "devenv.lock", "devbox.json", "devbox.lock",
        ".envrc", "pyproject.toml", "package.json", "Cargo.toml", "go.mod",
        "statix.toml", "treefmt.toml", "treefmt.nix",
    ]
    machine = platform.machine()
    arch = {"amd64": "x86_64", "arm64": "aarch64"}.get(machine, machine)
    data = {
        "schema_version": 1,
        "project": str(root),
        "host": {"os": platform.system(), "architecture": machine},
        "host_nix_system_guess": arch + "-linux" if platform.system() == "Linux" else None,
        "markers": [name for name in markers if (root / name).is_file()],
        "nix": {"available": bool(shutil.which("nix"))},
        "project_evaluated": False,
    }
    if data["nix"]["available"]:
        data["nix"]["version"] = command(["nix", "--version"], root)

    lock = root / "flake.lock"
    if lock.is_file():
        if lock.is_symlink() or lock.stat().st_size > 2_000_000:
            data["lock_error"] = "Symlink or oversized flake.lock: inspect manually."
        else:
            try:
                parsed = json.loads(lock.read_text())
                data["locked_inputs"] = {
                    name: {key: node["locked"][key] for key in ("type", "rev", "narHash")
                           if key in node["locked"]}
                    for name, node in parsed.get("nodes", {}).items() if "locked" in node
                }
            except (OSError, ValueError, TypeError, AttributeError, KeyError) as exc:
                data["lock_error"] = type(exc).__name__

    if shutil.which("git"):
        data["git_tracked_status"] = command(
            ["git", "-c", "core.fsmonitor=false", "status", "--porcelain=v1", "--untracked-files=no"], root
        )
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    root = args.project.expanduser().resolve()
    if not root.is_dir():
        parser.error("project must be an existing directory")
    print(json.dumps(inspect(root), indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
