# Project checks and development environments

## treefmt and git-hooks.nix

Inspect `treefmt.nix`, `treefmt.toml`, hook definitions and flake outputs first.
These files can execute arbitrary tools. Find inline configurations in
`flake.nix` too; filenames alone do not prove that an integration is present.
Preserve the existing formatters, versions, exclusions and CI workflow.

For an existing treefmt formatter, from the project root:

```bash
nix fmt --no-write-lock-file -- --help
nix fmt --no-write-lock-file -- --fail-on-change
```

Use these flags only after confirming the formatter is treefmt. Treat
`--fail-on-change` as a modifying command: it reports formatting differences
with a failing exit status, and can rewrite files. Use scratch for a review that
must preserve the checkout. For an unchanged checkout, prefer the project's
exact formatting check derivation:

```bash
nix build --no-write-lock-file --no-link .#checks.x86_64-linux.formatting
```

Resolve the real system/name before running: neither `formatting` nor
`pre-commit-check` is universal. With git-hooks.nix, prefer the existing check:

```bash
nix build --no-write-lock-file --no-link .#checks.x86_64-linux.pre-commit-check
```

The check runs hooks in a Nix build. In contrast, `pre-commit run --all-files`
can fetch hook environments, execute arbitrary programs and rewrite files;
`pre-commit install` changes Git configuration/hooks. A devShell can also install
hooks through its `shellHook`. Use the project's configured runner (possibly
`prek`), and inspect these effects before executing it. Do not install hooks as
a side effect of reviewing a project. A generic toolbox `pre-commit` does not
recreate the project's Nix-generated hook configuration or dependency versions.

When creating an integration is in scope, treefmt-nix offers a wrapped formatter
and `config.build.check`; git-hooks.nix offers `lib.SYSTEM.run` and its
`shellHook`/`enabledPackages`. Wire one check into both local and CI execution.
Pin new inputs, follow the project's nixpkgs where compatible, and avoid running
the same formatter twice through both integrations. The toolbox's own flake
contains a minimal working example of each check.

[treefmt-nix](https://github.com/numtide/treefmt-nix),
[git-hooks.nix](https://github.com/cachix/git-hooks.nix).

## Detect an old nix-direnv shell

An existing shell is not proof that the current flake evaluates. nix-direnv can
reuse its previous environment after evaluation fails, or defer changes in
manual reload mode. First inspect `.envrc` and any sourced files; loading it
executes shell code. Do not automatically run `direnv allow` on unfamiliar code.

In the environment actually used for the task, inspect only the fallback flag:

```bash
python3 -c 'import os,json; print(json.dumps({"nix_direnv_fallback": os.environ.get("NIX_DIRENV_DID_FALLBACK") == "1"}))'
```

If the command runner does not inherit the interactive shell, an already reviewed
and allowed environment can be loaded explicitly:

```bash
direnv exec "$PROJECT" bash -c 'if [ "${NIX_DIRENV_DID_FALLBACK:-0}" = 1 ]; then echo "Previous devShell reused" >&2; exit 1; fi'
```

A fallback result means tests in that environment do not validate the new shell.
An absent flag alone does not prove freshness: inspect `direnv status`, the
reviewed `.envrc` for `nix_direnv_manual_reload`, and watches for imported files.
Report only relevant status fields; never dump `direnv export`, `direnv dump`,
`nix print-dev-env` output, or the full environment, which may contain secrets.

For a decisive current-shell check, bypass direnv's cache and use the exact
reviewed project shell directly, with the original test cwd:

```bash
cd "$PROJECT"
nix develop --no-write-lock-file .#SHELL -c TEST_COMMAND
```

Resolve `SHELL` and `TEST_COMMAND` first. This evaluates the current definition
and executes its hooks; apply the execution contract. For an authorized permanent
change, `nix_direnv_disallow_fallback` can make fallback fail visibly. A manual
reload uses `nix-direnv-reload` in an initialized interactive environment;
changing `.envrc` requires renewed direnv approval. Do not modify shell startup
files merely to run a project test.

[nix-direnv fallback and manual reload](https://github.com/nix-community/nix-direnv#advanced-usage).
