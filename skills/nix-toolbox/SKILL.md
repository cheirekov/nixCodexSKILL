---
name: nix-toolbox
description: Use Nix tools to make development tasks reproducible and verifiable on Linux. Use for Nix projects, missing commands or libraries, inconsistent development environments, package/build failures, closure size, and dev-shell or CI parity when Nix can simplify the task. Preserve existing project tooling and pins.
---

# Nix toolbox

Use tools to obtain evidence, then decide the next action. Start with the
smallest useful operation. Nix is useful even when the application is Python,
Go, Rust, JavaScript, or infrastructure code.

## 1. Inspect and choose

Resolve this skill's directory as `TOOLBOX` and the target project as `PROJECT`.
Use absolute paths. Run the metadata inspector when it will save manual discovery:

```bash
python3 "$TOOLBOX/scripts/inspect_project.py" "$PROJECT"
```

It reports JSON: host architecture guess, Nix version, project markers, locked
input revisions, and tracked Git status. It does not evaluate project code or
print Nix configuration, environment variables, state, or secret files.
Read relevant `AGENTS.md`, the project's environment definition, and scripts
before running them. The inspector does not discover outputs or prove safety.

Choose one route:

| Need | First action | Evidence to obtain |
| --- | --- | --- |
| Missing command/library | Existing shell; otherwise `nix-locate` or targeted package search | Actual binary/file and package attribute at the chosen pin |
| Different developer/CI environments | Existing devShell, shell.nix, devenv, or devbox | Same locked dependencies and test command in both contexts |
| Nix code review | `statix check`, `deadnix --fail`, project formatter in check mode | File/line diagnostics; verify each proposed fix |
| Evaluation/build failure | Exact output evaluation, build log, derivation metadata | First actionable failure and its phase |
| Unexpected rebuild/large closure | `nix-diff`, `nix why-depends`, `nix path-info` | Changed derivation input or concrete dependency path |
| New package | `nix-init` in scratch, then target-pin evaluation/build | Reviewed dependencies, hashes, license, runtime test |
| Many independent checks | Existing CI; consider `nix-fast-build` after measuring | Explicit system/outputs, bounded parallelism, timings |

Read [tool recipes](references/tools.md) only for the selected route. Read
[execution contracts](references/execution.md) for builds, CI, remote stores,
NixOS operations, or delegation.

## 2. Run in the correct environment

Prefer the project's pinned environment and configuration, including overlays
and `allowUnfree`. A direct `nixpkgs#tool` invocation does not inherit them.
Review shell hooks: entering a devShell can execute commands and create files.
Keep the test's working directory and Python/module import context explicit.

For a missing helper, this skill includes a separately locked toolbox flake:

```bash
nix run --no-write-lock-file "path:$TOOLBOX#statix" -- check "$PROJECT"
nix run --no-write-lock-file "path:$TOOLBOX#deadnix" -- --fail "$PROJECT"
```

Its pin selects helper versions only. Evaluate the application's packages and
options against the application's pin. Fetch each helper on demand. Check its
`--help` before using flags from newer online documentation. Reuse an installed
compatible helper when fetching one would cost more than it saves.

For a non-Nix project, use a temporary pinned `nix shell` for an isolated missing
tool. The toolbox also exposes its locked package set for ordinary tools:

```bash
nix shell --no-write-lock-file "path:$TOOLBOX#jq" -c jq --version
```

Choose the package and command the task actually needs. Add a persistent
environment only when repeatability merits it and project
edits are in scope. Preserve existing devenv/devbox/flake choices. If Nix is
absent, use existing tools and report the prerequisite; installation is a
separate host change.

## 3. Verify and report

Record the selected tool/version, exact command, working directory, relevant
project pin and system, exit code, and finding. Keep output bounded; inspect the
failure excerpt rather than dumping every log. Machine-readable diagnostics are
preferred when supported by the installed version.

Distinguish evaluation, download/substitution, compilation, runtime tests,
activation, and reboot. Successful evaluation does not prove any later phase.
Verify the affected behavior after edits; treat lint advice as suggestions.
If an attempt fails, inspect that evidence before retrying. After two equivalent
failures, change the hypothesis or report the missing prerequisite.

Work alone by default. Delegate independent investigation only when the host
provides agents and current authorization permits it. Give each agent a bounded
question, input paths/pin, allowed actions, and expected evidence. Use one shared
writer for changes; verify returned claims yourself. The skill cannot grant
agent tools, override permissions, or select a provider on its own.
