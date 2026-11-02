# Tool recipes

Set `PROJECT` to the absolute target directory and `TOOLBOX` to the installed
skill's absolute directory. Resolve actual outputs before replacing placeholders.
Keep the project's formatter and versions when they are already defined.

## Find a missing tool or library

1. Check the existing project environment and lock. Search an exact input with
   `nix search --json INPUT_REF QUERY`; inspect a named candidate instead of
   evaluating the entire package set when possible.
2. For a known filename, use the toolbox's `nix-locate` app:

   ```bash
   nix run --no-write-lock-file "path:$TOOLBOX#nix-locate" -- --help
   ```

   `nix-locate` requires a file database. Use a compatible existing database or
   [nix-index-database](https://github.com/nix-community/nix-index-database).
   Its index revision may differ from the project's input. Verify the candidate
   attribute and file against the project pin before adding a dependency.
   Do not repeatedly generate a full index to solve one missing command.
3. Use `nix shell INPUT_REF#ATTRIBUTE -c COMMAND ...` for a temporary tool.
   `INPUT_REF` must be a resolved immutable reference or an appropriate existing
   project output. A project's overlays and unfree policy need its package set.
   For a non-Nix project without a package pin, this toolbox exposes its own
   locked package set: `nix shell --no-write-lock-file "path:$TOOLBOX#shellcheck"
   -c shellcheck SCRIPT_PATH`. The command may write files if the chosen tool
   does; a temporary environment does not sandbox application side effects.

[nix-index upstream](https://github.com/nix-community/nix-index).

## Find a historical version

Use this route when an exact older tool or a version comparison is needed.
Start with the project's pin and existing package attributes. MCP-NixOS
`nix_versions`, when available, can resolve version history without adding an
input. For indexed date/version queries or temporary historical tools, consider
[nixpkgs-multiverse](https://github.com/fzakaria/nixpkgs-multiverse).

Resolve `MULTIVERSE_REF` to `github:fzakaria/nixpkgs-multiverse/FULL_COMMIT`,
then inspect that revision's CLI help. From scratch, for example:

```bash
nix run --no-write-lock-file "$MULTIVERSE_REF#mvs" -- query versions ripgrep --json
```

Queries read the bundled index; acquiring the CLI/index can still download or
build dependencies. Coverage is the indexed revisions, not every Git commit or
every upstream release. Record the multiverse commit, selected nixpkgs revision,
attribute, version and target system before using a result.

The `fast.*` selectors substitute indexed store outputs without evaluating the
historical nixpkgs tree. They are system-specific and fail for missing entries;
do not infer an automatic source-build fallback. Check current cache availability
and closure transfer first. A normal evaluation selector may fetch a large old
nixpkgs tree and require source builds. Choose that explicitly within the task's
cost scope. A fast revision selector may use a canonical build of the same
version from a different revision; use normal evaluation when exact original
patches/build inputs matter.

Prefer historical packages as isolated CLI tools. Matching version strings do
not establish ABI compatibility for libraries or Python extensions from different
revisions. Preserve project overlays/unfree settings and review compatibility
before persisting a dependency. `mvs lock` and module pinning change project or
host configuration; do not run them merely to investigate a version.

[CLI and index semantics](https://github.com/fzakaria/nixpkgs-multiverse/blob/main/docs/cli.md),
[fast-path systems and revision semantics](https://github.com/fzakaria/nixpkgs-multiverse/blob/main/docs/store-paths.md).
This optional route is documentation-reviewed; runtime use remains to be verified
on a project that needs a historical version.

## Review Nix code

```bash
nix run --no-write-lock-file "path:$TOOLBOX#statix" -- check "$PROJECT"
nix run --no-write-lock-file "path:$TOOLBOX#deadnix" -- --fail "$PROJECT"
```

Both report findings without applying fixes. `deadnix --edit` and `statix fix`
modify files. Review unused arguments in `callPackage` functions carefully:
their names can be part of the dependency-injection interface. A lint finding
alone does not justify changing an intentional public argument.

Use the project's formatter in check mode. With this toolbox's formatter:

```bash
nix run --no-write-lock-file "path:$TOOLBOX#nixfmt" -- --check "$PROJECT/flake.nix"
```

Parser/lint success is separate from Nix evaluation and behavioral tests.
The pinned `statix` comes from the
[Molybdenum fork](https://github.com/molybdenumsoftware/statix), as selected by
Nixpkgs. The [older upstream](https://github.com/oppiliappan/statix) documents
this change. [deadnix](https://github.com/astro/deadnix),
[nixfmt](https://github.com/NixOS/nixfmt).

## Evaluate and debug a build

Run from the reviewed project directory. Use the exact output and system:

```bash
nix eval --no-write-lock-file --raw .#checks.x86_64-linux.fixture.system
nix build --no-write-lock-file --no-link --print-out-paths .#checks.x86_64-linux.fixture
```

`fixture` is an example from our evaluation project, not a universal check name.
Use `nix derivation show OUTPUT` and `nix log DRV_PATH` for the failing derivation.
Toolbox app `nom` can render builds; ordinary `nix build -L` is often sufficient.
Builds may download or execute project code and configured hooks; apply the
execution contract before running. Do not build an entire NixOS system to
answer a package-attribute question.

For an already realized output, query closure size and a suspected dependency:

```bash
nix path-info --recursive --size --closure-size /nix/store/ACTUAL-OUTPUT
nix why-depends /nix/store/ACTUAL-OUTPUT /nix/store/ACTUAL-DEPENDENCY
```

`nix why-depends --derivation` investigates build-time dependency paths.
To explain a rebuild, compare two existing derivations:

```bash
nix run --no-write-lock-file "path:$TOOLBOX#nix-diff" -- /nix/store/OLD.drv /nix/store/NEW.drv
```

[Nix why-depends](https://nix.dev/manual/nix/2.31/command-ref/new-cli/nix3-why-depends.html),
[nix-diff](https://github.com/Gabriella439/nix-diff),
[nix-output-monitor](https://github.com/maralorn/nix-output-monitor).

## Package or update software

For just a source fetcher/hash, prefer `nurl` over scaffolding a whole package:

```bash
nix run --no-write-lock-file "path:$TOOLBOX#nurl" -- --help
nix run --no-write-lock-file "path:$TOOLBOX#nurl" -- --json REPOSITORY_URL COMMIT
```

Use an immutable upstream commit. `--parse URL COMMIT` returns parsed JSON but
does not fetch/verify a source hash; the pinned version rejects combining
`--parse` with `--json`. A real hash fetch uses network and
may populate the Nix store. Capture stdout to scratch, review fetcher arguments
(including submodules), then evaluate against the project's pin. Do not insert
the output blindly or treat a content hash as a provenance/signature check.
Avoid command-line credentials and private URLs in logs.
[nurl](https://github.com/nix-community/nurl).

Read the pinned helpers' `--help` first. `nix-init` can infer dependencies and
prefetch hashes from an upstream URL; run it in scratch with an explicit output.
Disable implicit commit/overwrite through its supported flags or a dedicated
scratch configuration. Review generated hashes, build inputs, license, and
runtime dependencies before using the result in a project.

`nix-update` is useful for an existing package expression when updating software
is the actual task. It writes package metadata and can perform builds depending
on flags. Keep generated edits reviewable. For Nixpkgs PR validation consider
[nixpkgs-review](https://github.com/Mic92/nixpkgs-review) separately; it is not
required for ordinary application repositories.

[nix-init](https://github.com/nix-community/nix-init),
[nix-update](https://github.com/Mic92/nix-update).

## Scale evaluation and CI

Try [nix-fast-build](https://github.com/Mic92/nix-fast-build) when evaluation of
many outputs is measured as a bottleneck. Toolbox app: `nix-fast-build`.
Inspect its installed `--help` before choosing an exact flake attribute/system,
evaluation worker count, build concurrency, and link/output behavior.
Do not assume current upstream flags exist at this toolbox's pin.

Preserve reusable workflows, remote-builder routing, cleanup, timeout, and
cache policies already in the project. More parallelism is not automatically
cheaper. Native ARM building, cross compilation, and emulation are distinct.

## Optional agent data source

[MCP-NixOS](https://github.com/utensils/mcp-nixos) exposes package/option search,
function/documentation lookup, and local flake/store inspection. It is a useful
optional companion if already configured in the agent host. Request narrow
queries, the relevant channel, and bounded results. Check important answers
against the actual project revision; channel search alone cannot prove pin
compatibility. Do not invent its tool schema: use the advertised server tools.

The core skill works through shell commands without MCP. Configuring a new
server is a separate host setup task; pin its version/revision. Do not silently
edit Codex configuration or start a server for an unrelated project task.

Discovery source: [best-of-nix](https://github.com/tolkonepiu/best-of-nix).
Rankings guide discovery; select tools by the task and verify installed versions.
