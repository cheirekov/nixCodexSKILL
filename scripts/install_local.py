#!/usr/bin/env python3
"""Install the linked skill and pinned MCP server; preserve unrelated settings."""

import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib


def add_server(original, command):
    """Return original TOML plus our server, refusing a conflicting entry."""
    before = tomllib.loads(original.decode())
    existing = before.get("mcp_servers", {}).get("mcp-nixos")
    if existing is not None:
        if existing.get("command") != command or existing.get("args", []):
            raise ValueError("Existing mcp-nixos configuration differs; review it before replacing it.")
        if existing.get("enabled") is False:
            raise ValueError("Existing mcp-nixos is disabled; enable it explicitly before installing.")
        return original
    table = "\n\n[mcp_servers.mcp-nixos]\ncommand = " + json.dumps(command) + "\n"
    updated = original.rstrip() + table.encode()
    after = tomllib.loads(updated.decode())
    after["mcp_servers"].pop("mcp-nixos")
    if not before.get("mcp_servers") and "mcp_servers" not in before:
        after.pop("mcp_servers")
    if after != before:
        raise ValueError("Unrelated configuration would change.")
    return updated


def main():
    repo = Path(__file__).resolve().parents[1]
    home = Path.home()
    codex_home = Path(os.environ.get("CODEX_HOME", str(home / ".codex"))).expanduser()
    config = codex_home / "config.toml"
    if config.is_symlink():
        raise ValueError("config.toml is managed through a symlink; add the server at its source.")
    source = repo / "skills" / "nix-toolbox"
    destination = home / ".agents" / "skills" / "nix-toolbox"
    if destination.exists() or destination.is_symlink():
        if not destination.is_symlink() or destination.resolve() != source:
            raise ValueError("Skill destination already exists and points elsewhere.")
    original = config.read_bytes() if config.exists() else b""
    runtime = home / ".local" / "share" / "nix-toolbox" / "mcp-nixos"
    if runtime.exists() and not runtime.is_symlink():
        raise ValueError("MCP output destination already exists and is not a symlink.")
    command = str(runtime / "bin" / "mcp-nixos")
    updated = add_server(original, command)
    nix = shutil.which("nix")
    if not nix:
        raise ValueError("A working Nix installation with flakes/nix-command is required.")
    runtime.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        nix, "build", "--option", "builders", "", "--no-write-lock-file",
        "--out-link", str(runtime), "path:" + str(source) + "#mcp-nixos",
    ], check=True)
    if not Path(command).is_file():
        raise ValueError("MCP executable was not produced.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.is_symlink():
        destination.symlink_to(source, target_is_directory=True)
    if updated != original:
        codex_home.mkdir(parents=True, exist_ok=True)
        if (config.read_bytes() if config.exists() else b"") != original:
            raise ValueError("Codex configuration changed during installation; retry after reviewing it.")
        if config.exists():
            backups = codex_home / "backups"
            backups.mkdir(mode=0o700, exist_ok=True)
            stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            backup = backups / ("config.before-nix-toolbox-" + stamp + ".toml")
            descriptor = os.open(backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(original)
        descriptor, name = tempfile.mkstemp(prefix=".config-nix-toolbox-", dir=codex_home)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(updated)
            os.replace(name, config)
        finally:
            if os.path.exists(name):
                os.unlink(name)
    print(json.dumps({"skill": str(destination), "mcp_command": command,
                      "config": str(config), "unrelated_settings_preserved": True}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error)) from error
