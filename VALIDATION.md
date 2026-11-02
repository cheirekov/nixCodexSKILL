# Validation — 2026-10-23

Verified on Ubuntu x86_64 with Nix 2.31.4. The toolbox Nixpkgs revision is
`02c087f3fe673c9e317f206a627cb6b910336dbe`.

- Skill metadata passes the Codex skill validator.
- Inspector tests cover missing Nix, malformed/external-symlink locks, omitted
  credential-bearing URL fields, and unchanged input content.
- Installer tests cover unrelated TOML settings/comments, empty configuration,
  repeat installation, conflicting entries, and disabled server handling.
- statix/deadnix run successfully on a separate infrastructure-project export.
  Seeded issues produce JSON diagnostics without changing the input file.
- nixfmt check passes on the toolbox flake.
- A temporary locked `jq` environment runs successfully.
- `nix path-info` and `nix why-depends` expose a realized fixture's runtime closure
  and the dependency path to glibc.
- All toolbox apps evaluate for x86_64-linux and aarch64-linux.
- MCP-NixOS 3.0.1 starts over STDIO, completes MCP initialization, advertises
  `nix` and `nix_versions`, and answers a real package-info query for `jq`.
- Local installation uses a linked skill and a persistent Nix output link.
  The MCP configuration preserves unrelated existing settings.

ARM runtime, a NixOS host, automatic skill selection, and behavioral comparisons
across GPT/Qwen/GLM/DeepSeek have not been tested. These checks establish tool
availability and technical contracts, not a measured improvement in model
quality or cost. MCP channel results still need verification against project pins.

Specialized operations of nix-locate, nix-diff, nom, nix-init, nix-update, and
nix-fast-build have not been exercised; their app evaluation is the current
coverage. No remote provisioning, cache publication, activation, or reboot was
part of these checks. Full local infrastructure logs are excluded from this
public repository.

## Quality and environment additions — 2026-11-02

Short smoke checks on Ubuntu x86_64 with Nix 2.31.4; no additional model agents
or infrastructure projects were used. The existing Nixpkgs pin is unchanged.
New library pins: treefmt-nix `0d6d739a833ba9a9c93034862e4a7b061a062a1c`
and git-hooks.nix `1ba1dbfe28738c9a71c266be6efa5b89e75491a9`, both following
the toolbox's Nixpkgs input.

- Native `checks.x86_64-linux.formatting` (treefmt-nix/nixfmt) and
  `checks.x86_64-linux.git-hooks` (git-hooks.nix/deadnix) both build successfully.
  The command to repeat them is in README. Neither installs local Git hooks.
- A disposable toolbox copy containing a badly formatted Nix expression with
  an unused binding makes both checks exit nonzero, leaving the input unchanged.
- treefmt 2.6.0 `--fail-on-change` exits nonzero **and rewrites** the disposable
  input. The recipe therefore uses build checks/scratch for unchanged checkouts.
- nurl 0.4.1 parses a public repository/immutable commit and fetches its source
  hash with `--json`. `--parse --json` is rejected; `--parse` alone returns JSON
  without hashing. No generated expression is inserted into a project.
- With direnv 2.38.2/nix-direnv 3.2.0, an isolated, explicitly allowed temporary
  `.envrc` loads a working devShell. After an intentional flake evaluation
  failure, the old shell's marker remains and `NIX_DIRENV_DID_FALLBACK=1` is set.
  The documented guard then exits 1. No user shell configuration was changed.
- All 28 app outputs and four check derivations evaluate for x86_64-linux and
  aarch64-linux. Four existing Python unit tests and skill validation pass.

The smoke shell uses an empty `mkShellNoCC`; no system image or application is
built. Initial helper acquisition may download binary substitutes. ARM runtime,
NixOS-host behavior, manual direnv reload, uv2nix, crane and namaka remain
unverified. The optional integrations are references for future project tasks.
